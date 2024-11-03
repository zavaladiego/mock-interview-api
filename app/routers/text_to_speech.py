import base64
from enum import Enum
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.aws_service import synthesize_speech

router = APIRouter()

class VoiceID(str, Enum):
    mia = "Mia" # Spanish (Mexico)
    brian = "Brian" # English (US)

class TextToSpeechRequest(BaseModel):
    content: str = Field(..., example="Hola, ¿cómo estás?", description="The text to be converted to speech")
    language_code: Optional[str] = Field("es-MX", example="es-MX", description="Available options: es-MX, en-US")

default_voice_ids = {
    "es-MX": VoiceID.mia,
    "en-US": VoiceID.brian
}

@router.post("/tts")
async def get_audio(request: TextToSpeechRequest): 
    audio = synthesize_speech(request.content, request.language_code, default_voice_ids.get(request.language_code, VoiceID.mia))
    encoded_audio = base64.b64encode(audio).decode('utf-8')
    return {
        "message": "Audio conversion complete",
        "data": {
            "text": request.content,
            "output_format": "mp3",
            "audio": encoded_audio
        }
    }