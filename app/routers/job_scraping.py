from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.job_scraping_service import get_jobs_in_json
from app.shared.enums.job_site_type import JobSiteType
from app.shared.enums.job_type import JobType

router = APIRouter()

class JobRequest(BaseModel):
    location: Optional[str] = None
    google_search_term: Optional[str] = None
    hours_old: Optional[int] = None
    job_type: Optional[str] = None
    is_remote: Optional[bool] = False
    site_name: Optional[str] = JobSiteType.indeed
    search_term: Optional[str] = "Ingeniero de software"
    results_wanted: Optional[int] = 10
    country_indeed: Optional[str] = "Peru"
    offset: Optional[int] = 0
    enforce_annual_salary: Optional[bool] = False

@router.post("/jobs")
async def get_jobs(job_query: JobRequest):
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
