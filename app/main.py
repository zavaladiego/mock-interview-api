import uvicorn
from fastapi import FastAPI
from app.routers import text_to_speech


app = FastAPI()

app.include_router(text_to_speech.router, prefix="/api/v1", tags=["Text-to-Speech"])

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)