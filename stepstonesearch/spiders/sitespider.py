import scrapy
import json
from datetime import datetime
import re

"""
This module defines a Scrapy spider for scraping detailed job information from Stepstone job pages.
The spider reads job links from a JSON file, extracts relevant data from each job page, and saves the results to another JSON file.
"""

class sitespiderSpider(scrapy.Spider):
    """
    A Scrapy spider to scrape detailed job information from Stepstone.

    This spider reads job links from a provided JSON file, visits each job page, extracts job details such as job title,
    company name, location, salary, job description paragraphs, and lists (e.g., benefits), and saves the data in the variable job_data.

    :ivar name: The name of the spider.
    :ivar allowed_domains: Domains allowed for the spider to crawl.
    :ivar input_file: Path to the JSON file containing job links.
    :ivar output_file: Path to the output JSON file where scraped data will be saved.
    :ivar items: List of job items loaded from the input JSON file.
    :ivar job_details: List to store scraped job details.
    :ivar job_title: The job title used for naming the output file.
    """
    name = "sitespider"
    allowed_domains = ["stepstone.de"]

    def __init__(self, input_file="links_output.json", job_title="default_job", *args, **kwargs):
        """
        Initialize the spider with the input JSON file and job title.

        :param input_file: Path to the JSON file containing job links (default is "links_output.json").
        :param job_title: The job title used to name the output file (default is "default_job").
        """
        super(sitespiderSpider, self).__init__(*args, **kwargs)
        self.input_file = input_file
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.output_file = f"{job_title}_{timestamp}.json"
        self.items = self.load_items()
        self.job_details = []
        self.job_title = job_title

    def load_items(self):
        """
        Load job items from the input JSON file.

        :return: List of job items or an empty list if loading fails.
        """
        try:
            with open(self.input_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            self.logger.error(f"Error loading items: {e}")
            return []

    def start_requests(self):
        """
        Generate Scrapy requests for each job link in the input items.

        Each request includes the job item metadata and is sent to the `parse` method for processing.
        """
        for item in self.items:
            url = "https://www.stepstone.de" + item.get("link", "")
            yield scrapy.Request(url=url, callback=self.parse, meta={'item': item})

    def extract_job_id(self, url):
        """
        Extract the job ID from the job page URL.

        The job ID is extracted using a regular expression that looks for a sequence of digits before "-inline.html".

        :param url: The URL of the job page.
        :return: The extracted job ID or None if not found.
        """
        match = re.search(r'-(\d+)-inline\.html', url)
        if match:
            return match.group(1)
        return None

    def parse(self, response):
        """
        Parse the job page and extract relevant job details.

        This method extracts paragraphs, lists (e.g., benefits), and other job details from the page.
        It cleans the text and organizes the data into a dictionary, which is then appended to the job_details list.

        :param response: The Scrapy response object containing the job page HTML.
        """
        item = kohta.meta.get('item', {})

        def clean_text(text):
            """Clean the text by stripping whitespace and removing text with unwanted characters."""
            return text.strip() if not ("{" in text or ":" in text or "}" in text) else ""

        job_id = self.extract_job_id(response.url)

        paragraphs = response.xpath('//p[not(ancestor::*[contains(@class, "job-ad-display-1wh962r")])]//text()').getall()
        paragraphs_cleaned = [clean_text(p) for p in paragraphs if clean_text(p)]

        lists_data = {}
        lists = response.xpath('//ul[not(ancestor::*[contains(@class, "job-ad-display-1wh962r")])]')

        for ul in lists:
            parent_class = ul.xpath('./ancestor::*[contains(@class, "")][1]/@class').get()
            if parent_class:
                class_name = parent_class.split()[0]
                if class_name == "job-ad-display-kyg8or" and ul.xpath('./ancestor::*[@id="SeoRelatedLinks"]'):
                    continue
                if class_name == "job-ad-display-1cat3iu":
                    class_name = "content/benefits"
                if class_name == "job-ad-display-kyg8or":
                    class_name = "company"
                if class_name == "job-ad-display-1yd5hr5":
                    class_name = "companySize"
            else:
                class_name = "CompanyInfo"

            items = ul.xpath('.//li//text()').getall()
            items_cleaned = [clean_text(item) for item in items if clean_text(item)]

            if class_name not in lists_data:
                lists_data[class_name] = []
            lists_data[class_name].append(items_cleaned)

        company_data = {}
        companyURL = response.xpath(
            '//div[@id="JobAdContent"]//a[contains(@class, "job-ad-display-1ifgnl6")]/@href'
        ).get()
        if companyURL:
            company_data["companyLogoResultPageUrl"] = companyURL

        job_data = {
            "Job Title": self.job_title,
            "specific job title": item.get('title', '').strip(),
            'companyName': item.get('companyName', '').strip(),
            'location': item.get('location', '').strip(),
            'datePosted': item.get('datePosted', '').strip(),
            'salary': item.get('salary', '').strip(),
            "url": response.url,
            "jobId": job_id,
            "paragraphs": paragraphs_cleaned,
            "lists": lists_data,
        }

        self.job_details.append(job_data)

    def closed(self, reason):
        """
        Save the collected job details to a JSON file when the spider is closed.

        :param reason: The reason for the spider being closed.
        """
        try:
            with open(self.output_file, "w", encoding="utf-8") as file:
                json.dump(self.job_details, file, ensure_ascii=False, indent=4)
            self.logger.info(f"Job details saved to '{self.output_file}'.")
        except Exception as e:
            self.logger.error(f"Error saving job details: {e}")