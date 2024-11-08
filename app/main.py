import uvicorn
from fastapi import FastAPI
from app.routers import speech_to_text, text_to_speech, chat_gpt, job_scraping

app = FastAPI()

app.include_router(text_to_speech.router, prefix="/api/v1", tags=["Text-to-Speech"])
app.include_router(speech_to_text.router, prefix="/api/v1", tags=["Speech-to-Text"])
app.include_router(chat_gpt.router, prefix="/api/v1", tags=["OpenAI Service"])
app.include_router(job_scraping.router, prefix="/api/v1", tags=["Job Scraping"])

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)  