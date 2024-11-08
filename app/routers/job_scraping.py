from typing import List
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.job_scraping_service import get_jobs_in_json

router = APIRouter()

class JobRequest(BaseModel):
    site_name: List[str] = ["indeed"]
    search_term: str = "Ingeniero de software"
    google_search_term: str = "ingeniero de software cerca de Lima"
    location: str = "Lima, Peru"
    is_remote: bool = False
    job_type: str = "fulltime"
    results_wanted: int = 10
    country_indeed: str = "Peru"
    offset: int = 0
    hours_old: int = 72
    enforce_annual_salary: bool = False

@router.get("/jobs")
async def get_jobs(job_query: JobRequest):
    jobs_data = get_jobs_in_json(
        site_name=job_query.site_name,
        search_term=job_query.search_term,
        google_search_term=job_query.google_search_term,
        location=job_query.location,
        is_remote=job_query.is_remote,
        job_type=job_query.job_type,
        results_wanted=job_query.results_wanted,
        country_indeed=job_query.country_indeed,
        offset=job_query.offset,
        hours_old=job_query.hours_old,
        enforce_annual_salary=job_query.enforce_annual_salary
    )
    return jobs_data