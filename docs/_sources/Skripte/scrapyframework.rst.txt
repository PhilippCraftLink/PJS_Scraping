Scraping with Scrapy
==============================================

What is Scrapy?
---------------

Scrapy is a powerful and flexible web scraping framework for Python. It simplifies the process of building and running web spiders to crawl websites and extract structured data. Scrapy manages many complexities of web scraping, such as handling HTTP requests, following pagination links, and dealing with cookies or different content types. It’s widely used for tasks like data extraction, automated testing, and information gathering.

For more details, check out the `official Scrapy documentation <https://docs.scrapy.org/en/latest/>`_.

Key Files in the Project
------------------------

- **`settings.py`**

  This file holds the configuration settings for the Scrapy project. It defines:

  - The bot name (``BOT_NAME = "stepstonesearch"``).
  - Spider module locations (``SPIDER_MODULES``).
  - A custom user agent mimicking Firefox (``USER_AGENT``) to make requests appear legitimate.
  - Scraping behavior, such as disabling cookies (``COOKIES_ENABLED = False``) and setting a 3-second download delay (``DOWNLOAD_DELAY = 3``) to avoid overwhelming the server.
  - Whether to obey robots.txt rules (``ROBOTSTXT_OBEY = False``).

  These settings ensure the scraper runs responsibly and efficiently.

- **`items.py`**

  This file defines data models for scraped items. Scrapy uses items as containers to structure extracted data. In this project, the ``StepstonesearchItem`` class is defined with a single placeholder field (``name``). This suggests the project doesn’t heavily rely on Scrapy’s item system, handling data processing directly in the spiders instead.

- **`pipelines.py`**

  This file is for defining item pipelines, which process scraped items (e.g., cleaning, validating, or storing data). The project includes a ``StepstonesearchPipeline`` class, but it only returns items without modification. This indicates no additional processing occurs in the pipeline, with data handling managed elsewhere.

- **`Links.py`**

  This file contains the ``LinksSpider`` spider, which scrapes job listing links from Stepstone search result pages. It:

  - Starts with a search URL for a job title, such as "pwc-consultant".
  - Extracts job details like title, company, location, and URL.
  - Follows pagination up to a set limit, such as 5 pages or 35 jobs.
  - Saves results to ``links_output.json``.

  This spider is the first step in collecting job links for further scraping.

- **`sitespider.py`**

  This file defines the ``sitespiderSpider`` spider, which scrapes detailed job information from individual job pages. It:

  - Reads links from ``links_output.json``.
  - Extracts details like job title, company, location, salary, description paragraphs, and lists such as benefits.
  - Saves data to a JSON file named with the job title and timestamp, for example, ``pwc-consultant_2023-10-15_14-30-00.json``.

  This spider builds on the ``LinksSpider`` output to gather comprehensive job data.

- **`stepstone_scraper.py`**

  This file contains functions to run the Scrapy spiders and save the scraped data to a MongoDB database. It manages the execution of the spiders, waits for output files, and handles data storage. The main functions are explained in the individual modules