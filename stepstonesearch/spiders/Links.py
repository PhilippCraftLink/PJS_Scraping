import scrapy
import json

"""
This module defines a Scrapy spider for scraping job listing links from Stepstone search result pages.
The spider collects job links up to a specified number of pages or jobs and saves them to a JSON file.
"""

class LinksSpider(scrapy.Spider):
    """
    A Scrapy spider to scrape job listing links from Stepstone.

    This spider starts from the search results page for a given job title, extracts job listing data (e.g., title, company, location, link),
    and follows pagination up to a specified maximum number of pages or jobs. The results are saved to a JSON file.

    :ivar name: The name of the spider.
    :ivar allowed_domains: Domains allowed for the spider to crawl.
    :ivar custom_settings: Custom settings for the spider, including the output feed configuration.
    :ivar base_url: The base URL template for Stepstone job search pages.
    :ivar start_urls: The initial URL(s) to start scraping from.
    :ivar jobs_collected: A counter for the number of jobs collected so far.
    """
    name = "Links"
    allowed_domains = ["stepstone.de"]

    custom_settings = {
        "FEEDS": {
            "links_output.json": {"format": "json", "encoding": "utf8", "indent": 4},
        }
    }

    def __init__(self, job_title="pwc-consultant", max_pages=5, max_jobs=35, *args, **kwargs):
        """
        Initialize the spider with the job title and limits for pages and jobs.

        :param job_title: The job title to search for (default is "pwc-consultant").
        :param max_pages: The maximum number of pages to scrape (default is 2).
        :param max_jobs: The maximum number of jobs to collect (default is 2).
        """
        super(LinksSpider, self).__init__(*args, **kwargs)
        self.job_title = job_title
        self.base_url = "https://www.stepstone.de/jobs/{job_title}?page={page}"
        self.start_urls = [self.base_url.format(job_title=self.job_title, page=1)]
        self.max_pages = max_pages
        self.max_jobs = max_jobs
        self.jobs_collected = 0

    def extract_items(self, data):
        """
        Extract the 'items' array from the JSON-like data in the page source.

        This method uses a stack-based approach to find the balanced brackets of the 'items' array in the page's script data.

        :param data: The raw HTML content of the page.
        :return: The extracted 'items' array as a string, or None if not found.
        """
        stack = []
        start_idx = data.find('"items":[') + 8
        if start_idx == -1:
            return None

        for i in range(start_idx, len(data)):
            if data[i] == '[':
                stack.append('[')
            elif data[i] == ']':
                stack.pop()
                if not stack:
                    return data[start_idx:i + 1]

        return None

    def parse(self, response):
        """
        Parse the search results page and extract job listing data.

        This method extracts job items from the page, yields them as dictionaries, and follows pagination links
        until the maximum number of pages or jobs is reached.

        :param response: The Scrapy response object containing the search results page HTML.
        """
        if self.jobs_collected >= self.max_jobs:
            return

        html_content = response.text
        self.logger.info(f"Response size: {len(html_content)} characters.")

        items_list_str = self.extract_items(html_content)
        if items_list_str:
            try:
                items_list = json.loads(items_list_str)
                self.logger.info(f"Extracted {len(items_list)} items.")

                for item in items_list:
                    if self.jobs_collected >= self.max_jobs:
                        break

                    yield {
                        'title': item.get('title', '').strip(),
                        'companyName': item.get('companyName', '').strip(),
                        'location': item.get('location', '').strip(),
                        'link': item.get('url', ''),
                        'Kurztext': item.get('textSnippet', ''),
                        'salary': item.get('salary', ''),
                        'datePosted': item.get('datePosted', ''),
                    }
                    self.jobs_collected += 1

            except json.JSONDecodeError as e:
                self.logger.error(f"Error decoding JSON: {e}")

        current_page = int(response.url.split("page=")[-1]) if "page=" in response.url else 1
        if current_page < self.max_pages and self.jobs_collected < self.max_jobs:
            next_page_url = self.base_url.format(job_title=self.job_title, page=current_page + 1)
            self.logger.info(f"Navigating to next page: {next_page_url}")
            yield scrapy.Request(next_page_url, callback=self.parse)