import urllib.parse
import re
import json
from bs4 import BeautifulSoup
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError

"""
This module contains functions to scrape job listings from Indeed for the given list of job titles.
It uses SeleniumBase for browser automation and BeautifulSoup for HTML parsing.

Indeed uses captcha tests to make scraping more difficult. SeleniumBase is therefore well suited,
as it solves captcha tests automatically. 

note: to guarantee that the captcha test is bypassed, seleniumbase should be executed locally and not within a docker container, as the virtual environment can lead to complications with the browser.

The scraped data is stored in a MongoDB database.
"""

TEXT_IDS = ["jobLocationText"]
LIST_ID = "benefits"
DESCRIPTION_ID = "jobDescriptionText"

def scrape_indeed_for_title(job_title, sb, db):
    """
    Scrape job listings from Indeed for the given job title.

    This function automates a browser to search Indeed for a specified job title, collects job links across multiple pages,
    and extracts detailed job information such as location, benefits, and description. The data is then stored in a MongoDB collection.

    :param job_title: The job title to search for (e.g., "Software Engineer").
    :param sb: An instance of SeleniumBase for browser automation.
    :param db: A MongoDB database instance to store the scraped data.
    """
    collection_name = job_title.replace(" ", "_").lower()
    collection = db["indeed_" + collection_name]
    collection.create_index([("jobID", ASCENDING)], unique=True)

    encoded_job_title = urllib.parse.quote(job_title)
    url = f"https://de.indeed.com/jobs?q={encoded_job_title}"
    print(f"\n🔍 Suche nach: {job_title}")
    print(url)

    sb.activate_cdp_mode(url)
    sb.open(url)
    sb.sleep(15)

    raw_html = sb.get_page_source()
    print(raw_html)

    job_links = []
    max_pages = 5
    for page in range(max_pages):
        print(f"Scraping Seite {page + 1} für {job_title}")
        raw_html = sb.get_page_source()
        soup = BeautifulSoup(raw_html, "html.parser")
        for link in soup.select("a[data-mobtk]"):
            job_url = "https://de.indeed.com" + link["href"]
            if job_url not in job_links:
                job_links.append(job_url)

        if page < max_pages - 1:
            try:
                next_button = sb.find_element('a[aria-label="Nächste Seite"]')
                sb.click(next_button)
                sb.sleep(5)
            except:
                print("Keine weiteren Seiten verfügbar")
                break

    print(f"🔎 {len(job_links)} Jobangebote gefunden für {job_title}")
    print(job_links)
    job_links = job_links[:2]
    if len(job_links) == 0:
        print("Keine Jobangebote gefunden. Programm wird beendet.")
        #sys.exit()

    for idx, job_url in enumerate(job_links, start=1):
        try:
            sb.open(job_url)
            sb.sleep(5)
            raw_html = sb.get_page_source()
            soup = BeautifulSoup(raw_html, "html.parser")

            job_data = {
                "Job Title": job_title,
                "URL": job_url,
            }

            for text_id in TEXT_IDS:
                element = soup.find(id=text_id)
                job_data[text_id] = element.get_text(separator=" ", strip=True) if element else "Nicht gefunden"

            benefits_div = soup.find(id=LIST_ID)
            if benefits_div:
                job_data[LIST_ID] = [li.get_text(strip=True) for li in benefits_div.find_all("li")] or "Keine Vorteile angegeben"
            else:
                job_data[LIST_ID] = "Nicht gefunden"

            description_div = soup.find(id=DESCRIPTION_ID)
            if description_div:
                elements = description_div.find_all(["p", "li"])
                paragraphs = [elem.get_text(strip=True) for elem in elements if elem.get_text(strip=True)]
                job_data["paragraphs"] = paragraphs
            else:
                job_data["paragraphs"] = "Nicht gefunden"

            scripts = soup.find_all("script")
            pattern = r"window\._initialData\s*=\s*(\{.*?\});"
            for script in scripts:
                script_text = script.string
                if script_text:
                    cleaned_script = " ".join(script_text.split())
                    match = re.search(pattern, cleaned_script)
                    if match:
                        json_str = match.group(1)
                        try:
                            initial_data = json.loads(json_str)
                        except json.JSONDecodeError:
                            print("Fehler beim Parsen des JSON-Strings")
                            continue

                        host_query_result = initial_data.get("hostQueryExecutionResult")
                        if not host_query_result:
                            print("hostQueryExecutionResult nicht gefunden")
                            continue

                        job_dataElement = host_query_result.get("data", {}).get("jobData")
                        if not job_dataElement:
                            print("jobData nicht gefunden")
                            continue

                        results = job_dataElement.get("results")
                        if not results or len(results) == 0:
                            print("Keine Ergebnisse im results-Array")
                            continue

                        first_result = results[0]
                        jobElement = first_result.get("job")
                        if not jobElement:
                            print("job-Objekt nicht gefunden")
                            continue

                        key = jobElement.get("key")
                        CompanyName = jobElement.get("sourceEmployerName")
                        if key:
                            job_data["jobID"] = key
                        else:
                            print("Key existiert nicht im job-Objekt")

                        if CompanyName:
                            job_data["Company Name"] = CompanyName
                        else:
                            print("kein Company Name gefunden")

            try:
                collection.insert_one(job_data)
                print(f"✅ {job_title} - Job {idx} erfolgreich gespeichert")
            except DuplicateKeyError:
                print(f"⏩ Übersprungen: {job_url} existiert bereits")

        except Exception as e:
            print(f"⚠️ Fehler bei Job {job_url}: {str(e)}")
            continue