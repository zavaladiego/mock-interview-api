from fastapi import APIRouter, HTTPException

from app.services.student_scraping_service import scrape_alumno_by_code, scrape_alumno_by_email

router = APIRouter()

@router.post("/student/{codigo}")
async def get_student_by_code(codigo: str):
    try:
        student_data = scrape_alumno_by_code(codigo)
        return student_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/student/email/{email}")
async def validate_student_by_email(email: str):
    try:
        student_data = scrape_alumno_by_email(email)
        return student_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))