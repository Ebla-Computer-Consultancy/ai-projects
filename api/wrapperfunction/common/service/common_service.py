import os
import tempfile
import wrapperfunction.integration as integration
from fastapi import UploadFile, HTTPException

async def transcribe(file: UploadFile):
    splittedFileName = file.filename.lower().split(".")
    fileExtension = splittedFileName[len(splittedFileName) - 1]

    if fileExtension != "wav":
        raise HTTPException(
            400, f"file type { fileExtension } not allowed \n use wav audio files"
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio_file:
        content = await file.read()
        tmp_audio_file.write(content)
        tmp_filename = tmp_audio_file.name
    transcription_result =  integration.speechconnector.transcribe_audio_file(tmp_filename)
    await file.close() 
    os.unlink(tmp_filename)

    return transcription_result