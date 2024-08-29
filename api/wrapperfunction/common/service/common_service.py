from io import BytesIO
import os
import tempfile
import wrapperfunction.integration as integration
from fastapi import UploadFile, HTTPException
from pydub import AudioSegment
from pydub.silence import split_on_silence

async def transcribe(file: UploadFile):
    splittedFileName = file.filename.lower().split(".")
    fileExtension = splittedFileName[len(splittedFileName) - 1]

    if fileExtension != "wav":
        raise HTTPException(
            400, f"file type { fileExtension } not allowed \n use wav audio files"
        )
    processed_audio_bytes = await fast_file(file)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio_file:
        tmp_audio_file.write(processed_audio_bytes)
        tmp_filename = tmp_audio_file.name
    transcription_result =  integration.speechconnector.transcribe_audio_file(tmp_filename)
    await file.close() 
    os.unlink(tmp_filename)

    return transcription_result

async def fast_file(file: UploadFile ):
    contents = await file.read()
    audio = AudioSegment.from_file(BytesIO(contents), format="wav")

    # Remove silence
    chunks = split_on_silence(audio, silence_thresh=-40)  # Adjust silence_thresh as needed

    # Combine chunks into a single audio segment if exists
    if len(chunks)>1 :
        trimmed_audio = AudioSegment.empty()
        for chunk in chunks:
            trimmed_audio += chunk

        # Save the processed audio to a BytesIO object
        processed_audio_stream = BytesIO()
        trimmed_audio.export(processed_audio_stream, format="wav")
        processed_audio_stream.seek(0)

        # Return the processed audio as a streaming response
        return processed_audio_stream.getvalue()
    else: return contents