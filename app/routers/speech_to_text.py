import time
import uuid
from fastapi import APIRouter, File, UploadFile

from app.services.aws_service import get_transcription_result, transcribe_speech, upload_to_s3


router = APIRouter()

@router.post("/stt")
async def transcribe_audio(file: UploadFile = File(...)):
    # Save the uploaded audio file locally
    file_path = f"./tmp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Define bucket and unique job name
    bucket_name = "test-unmsm-tesis-dev-mp3-us-west-1"
    job_name = f"transcription-job-{uuid.uuid4()}"

    # Upload to S3 and start transcription
    try:
        s3_uri = upload_to_s3(file_path, bucket_name)
    except Exception as e:
        return {"message": "Error uploading file to S3", "error": str(e)}
    
    transcribe_speech(s3_uri, job_name)

    # Poll for job completion
    transcription_text = None
    while transcription_text is None:
        transcription_text = get_transcription_result(job_name)
        time.sleep(5)  # Wait 5 seconds before checking again

    # Return the transcription text
    return {
        "message": "Transcription complete",
        "data": transcription_text
    }
