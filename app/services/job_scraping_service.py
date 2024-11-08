# app/services/job_scraping_service.py
import json
from jobspy import scrape_jobs

def get_jobs_in_json(
    site_name=["indeed"],
    search_term="Ingeniero de software",
    google_search_term="ingeniero de software cerca de Lima",
    location="Lima, Peru",
    is_remote=False,
    job_type="fulltime",
    results_wanted=10,
    country_indeed="Peru",
    offset=0,
    hours_old=72,
    enforce_annual_salary=False
):
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
    
    filtered_df = df[desired_columns]
    jobs_json_str = filtered_df.to_json(orient='records')
    jobs_json = json.loads(jobs_json_str)
    
    return jobs_json
