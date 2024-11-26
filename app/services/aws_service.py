import uuid
import boto3
import requests

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
    
    return audio

def upload_to_s3(file_path: str, bucket_name: str) -> str:
    """Uploads an audio file to S3 and returns the S3 URI."""
    settings = get_settings()
    s3 = boto3.client('s3',
                      aws_access_key_id=settings.AWS_AK,
        aws_secret_access_key=settings.AWS_SAK,)
    unique_filename = f"{uuid.uuid4()}.mp3"
    s3.upload_file(file_path, bucket_name, unique_filename)
    return f"s3://{bucket_name}/{unique_filename}"

def transcribe_speech(s3_uri: str, job_name: str, language_code: str = "es-US") -> dict:
    """Starts a transcription job and returns the job details."""
    settings = get_settings()
    client = boto3.client('transcribe', 
                          aws_access_key_id=settings.AWS_AK,
        aws_secret_access_key=settings.AWS_SAK,
        region_name='us-east-1')
    response = client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': s3_uri},
        MediaFormat='mp3',
        LanguageCode=language_code
    )
    return response

def get_transcription_result(job_name: str) -> str:
    """Checks the transcription job status and retrieves the transcript if complete."""
    settings = get_settings()
    client = boto3.client('transcribe', region_name='us-east-1',
                          aws_access_key_id=settings.AWS_AK,
        aws_secret_access_key=settings.AWS_SAK)
    response = client.get_transcription_job(TranscriptionJobName=job_name)
    
    if response['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
        transcript_uri = response['TranscriptionJob']['Transcript']['TranscriptFileUri']
        
        # Retrieve and return the transcription text from the URI
        transcript_response = requests.get(transcript_uri)
        transcript_json = transcript_response.json()
        transcripts = transcript_json.get("results", {}).get("transcripts", [])
        if transcripts:
            return transcripts[0].get("transcript", "")
        else:
            return ""
        
    elif response['TranscriptionJob']['TranscriptionJobStatus'] == 'FAILED':
        raise Exception("Transcription job failed.")
    else:
        return None  # still in progress
