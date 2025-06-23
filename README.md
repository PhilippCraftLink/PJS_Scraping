# Job Listing Scraper

This project was developed as part of a university seminar in collaboration with **PWC (PricewaterhouseCoopers)**. The codebase is designed to be easily accessible and deployable using **Docker**, ensuring a streamlined setup process for users.

My task was to identify suitable sources for data extraction. To achieve this, I analyzed various job portals to assess whether they provide both qualitative and sufficiently quantitative data. Additionally, I evaluated each portal with regard to bot detection mechanisms and the simplicity of their HTML structure.

Based on this analysis, Stepstone emerged as a particularly scraping-friendly and high-quality data source. By using reverse engineering and scraping frameworks, I was able to access the API endpoint and retrieve structured data. The extracted data then only needed to be saved in proper JSON format to be ready for further processing.

As a second source, I decided in favour of the Indeed portal. The decision criteria here were very similar to Stepstone.
Indeed also offers high quality and a large amount of data. However, Indeed was much more difficult to scrape. On the one hand, the HTML structure is very deeply nested and difficult to analyse. Secondly, Indeed uses Cloud-Flare as an anti-bot mechanism. Using the Scrapy framework is not enough to bypass this captcha test. 
Even a normal Selenium browser is not sufficient. To solve the test, i decided to use Seleniumbase, an extension of Selenium, which 
recognises and automatically solves simple captcha tests.

---

## 📚 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Setup and Installation](#setup-and-installation)
  - [Prerequisites](#prerequisites)
  - [Clone the Repository](#clone-the-repository)
  - [Install Dependencies](#install-dependencies)
  - [Set Up MongoDB](#set-up-mongodb)
  - [Configure Environment Variables](#configure-environment-variables)
  - [Build and Run with Docker](#build-and-run-with-docker)
- [Usage](#usage)

---

## 📌 Project Overview 

This project emerged from a seminar collaboration between university students and PWC, with the goal of scraping job listing data from **Indeed** and **Stepstone**. The extracted data—such as job titles, companies, locations, and descriptions—is stored in a structured format for further analysis.

By leveraging Docker, the project ensures portability and ease of deployment, making it accessible to both academic and professional audiences.

---

## 🚀 Features

- Scrapes job listings from **Indeed** and **Stepstone**
- Extracts key job details (e.g., title, company, location, description)
- Stores data in a **MongoDB** database
- Containerized with **Docker** for simplified setup and execution

---

## 🛠 Technologies Used 

- **Python 3.x** – Core language for scripting and data processing  
- **Seleniumbase** – Automates browser interactions for scraping dynamic content  
- **Scrapy** – Framework for efficient web scraping  
- **MongoDB** – NoSQL database for storing job listing data  
- **Docker** – Containerization tool for consistent deployment

---

## ⚙️ Setup and Installation 

### Prerequisites 

- [Docker](https://www.docker.com/) – Required for containerized deployment  
- [MongoDB](https://www.mongodb.com/) – Can be run locally or via MongoDB Atlas  
- [Git](https://git-scm.com/) – For cloning the repository

### Clone the Repository 

### bash

    git clone https://github.com/PhilippCraftLink/PJS_PWC_WS2024-25-PS.git
    cd $path$

### Install Dependencies 

For local use without Docker:

    pip install -r requirements.txt

### Set Up MongoDB 

Start a local MongoDB instance (mongodb) or use a cloud-hosted solution (e.g., MongoDB Atlas)

Create a database (e.g., job_listings) to store the scraped data

### Configure Environment Variables 

Create a .env file in the project root with the following content:

    MONGO_URI="your-MongoDB-Connection-Link"

### Build and Run with Docker 

Build the Docker image:

    docker build -t image_Name .

Run the container:

    docker run -it --env-file .env image_name

### Usage 

With Docker: Follow the Build and Run with Docker steps

Locally: After setting up dependencies and MongoDB:

    python run_scrapers_parallel.py

#### Output:
The scraper collects job listings from Indeed and Stepstone and stores them in MongoDB under the collections indeed_jobs and stepstone_jobs.
