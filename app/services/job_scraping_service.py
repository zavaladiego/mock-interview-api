# app/services/job_scraping_service.py
import json
from jobspy import scrape_jobs

from app.shared.enums.job_site_type import JobSiteType
from app.shared.enums.job_type import JobType

import json
import logging

def get_jobs_in_json(
    location,
    google_search_term,
    hours_old,
    job_type,
    is_remote,
    site_name,
    search_term,
    results_wanted,
    country_indeed,
    offset,
    enforce_annual_salary
):
    try:
        location = _setLocation(location)
        google_search_term = _setGoogleSearchTerm(location, search_term)

        # Perform the scraping with dynamic parameters
        df = scrape_jobs(
            site_name=site_name,
            search_term=search_term,
            google_search_term=google_search_term,
            location=location,
            is_remote=is_remote,
            job_type=job_type,
            results_wanted=results_wanted,
            country_indeed=country_indeed,
            offset=offset,
            hours_old=hours_old,
            enforce_annual_salary=enforce_annual_salary,
        )

        desired_columns = [
            "id", "site", "job_url", "title", "company", "location",
            "date_posted", "job_type", "interval", "min_amount",
            "max_amount", "currency", "is_remote"
        ]

        if df.empty:
            return []

        filtered_df = df[desired_columns]
        jobs_json_str = filtered_df.to_json(orient='records')
        jobs_json = json.loads(jobs_json_str)

        return jobs_json

    except Exception as e:
        logging.error(f"Error in get_jobs_in_json: {e}")
        raise Exception(f"Error in get_jobs_in_json: {e}")
        

def _setLocation(location):
    if location is None:
        return "Lima, Peru"
    return location + ", Peru"

def _setGoogleSearchTerm(location, search_term):
    if location is None:
        return search_term + " cerca de Lima"
    return search_term + " cerca de " + location
