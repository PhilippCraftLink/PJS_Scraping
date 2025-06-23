import time
from seleniumbase import SB
from indeed_scraper import scrape_indeed_for_title
from stepstone_scraper import run_spiders
import pymongo
import os
from dotenv import load_dotenv


"""
This module contains a script for scraping job listings from Indeed and Stepstone
using SeleniumBase and storing the data in a MongoDB database.

The script retrieves a list of job titles from a MongoDB collection and then scrapes
job listings for each title from Indeed and Stepstone, storing the results in another
MongoDB database.

Dependencies:
- seleniumbase
- pymongo
- python-dotenv

Configuration:
- The MongoDB URI must be set in the environment variable `MONGO_URI` or in a `.env` file.

Usage:
- Run the script directly: `python run_scrapers_parallel.py`
"""

# Lade Variablen aus der .env-Datei
load_dotenv()

# Lese die URI aus der Umgebungsvariable
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("Keine MONGO_URI in den Umgebungsvariablen gefunden")

def fetch_job_titles_from_mongodb(client):
    """
     Fetches the list of job titles from the MongoDB database.

     This function connects to the "Jobliste" database and retrieves the
     "job_titles" field from the document with _id "current_job_titles"
     in the "job_titles" collection.

     If no document is found or the field is missing, an empty list is returned.

     Parameters
     ----------
     client : pymongo.MongoClient
         The MongoDB client instance.

     Returns
     -------
     list[str]
         A list of job titles.
     """

    db = client["Jobliste"]
    collection = db["job_titles"]
    doc = collection.find_one({"_id": "current_job_titles"})
    return doc["job_titles"] if doc and "job_titles" in doc else []


def main():
    """
      Main function to orchestrate the job scraping process.

      This function performs the following steps:
      1. Connects to the MongoDB database using the URI from the environment.
      2. Fetches the list of job titles from the database.
      3. For each job title, scrapes job listings from Indeed and Stepstone.
      4. Stores the scraped data in the "stepstone_data" database.
      5. Closes the MongoDB connection.

      The scraping is done using SeleniumBase in headless mode to avoid
      detection and to run efficiently on servers.

      Notes
      -----
      - The script uses a 2-second delay between scraping each job title to
        avoid overwhelming the websites.
      - Ensure that the MongoDB URI is correctly set in the environment.
      - The script requires SeleniumBase and the necessary webdrivers.
      """

    client = pymongo.MongoClient(MONGO_URI)
    job_titles = fetch_job_titles_from_mongodb(client)
    #job_titles = ["Lehrer"]
    db = client["stepstone_data"]

    # für lokale Durchführung
    #with SB(uc=True, test=True, locale_code="de") as sb:

    chrome_args = ["--headless", "--no-sandbox", "--disable-dev-shm-usage"]
    with SB(uc=True, test=True, locale_code="de", disable_csp=True, chromium_arg=chrome_args) as sb:
        for job_title in job_titles:
            print(f"🚀 Starte Scraping für: {job_title}")
            # Scrape Indeed
            scrape_indeed_for_title(job_title, sb, db)
            # Scrape Stepstone
            run_spiders(job_title, db)
            print(f"✅ Fertig: {job_title}\n")
            time.sleep(2)  # Kurze Pause zwischen den Jobtiteln

    client.close()

if __name__ == "__main__":
    main()