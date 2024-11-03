import boto3
from app.dependencies import get_settings


def synthesize_speech(content: str, language_code: str = "es-MX", voice_id: str = "Mia") -> bytes:
    settings = get_settings()
    client = boto3.client(
        'polly',
        aws_access_key_id=settings.AWS_AK,
        aws_secret_access_key=settings.AWS_SAK,
        region_name='us-east-1'
    )
    result = client.synthesize_speech(
        Text=content,
        LanguageCode=language_code,
        OutputFormat='mp3',
        VoiceId=voice_id)
    audio = result['AudioStream'].read()
    
    # Save audio to a file for debugging purposes
    with open("tmp/audio.mp3", "wb") as file:
        file.write(audio)

    return audio