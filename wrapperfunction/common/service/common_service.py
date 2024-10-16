from io import BytesIO
import os
import tempfile
import wrapperfunction.integration as integration
from fastapi import Request, UploadFile, HTTPException
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
    transcription_result = integration.speechconnector.transcribe_audio_file(
        tmp_filename
    )
    await file.close()
    os.unlink(tmp_filename)

    return transcription_result


async def fast_file(file: UploadFile):
    contents = await file.read()
    audio = AudioSegment.from_file(BytesIO(contents), format="wav")

    # Remove silence
    chunks = split_on_silence(
        audio, silence_thresh=-40
    )  # Adjust silence_thresh as needed

    # Combine chunks into a single audio segment if exists
    if len(chunks) > 1:
        trimmed_audio = AudioSegment.empty()
        for chunk in chunks:
            trimmed_audio += chunk

        # Save the processed audio to a BytesIO object
        processed_audio_stream = BytesIO()
        trimmed_audio.export(processed_audio_stream, format="wav")
        processed_audio_stream.seek(0)

        # Return the processed audio as a streaming response
        return processed_audio_stream.getvalue()
    else:
        return contents


def get_speech_token():
    return integration.speechconnector.get_speech_token()


def start_stream(size: str,stream_id: str):
    return integration.avatarconnector.start_stream(size,stream_id)


async def send_candidate(stream_id: str, request: Request):
    data = await request.json()
    candidate_ = data.get("candidate")
    jsonData = {"candidate": candidate_}
    return integration.avatarconnector.send_candidate(stream_id, jsonData)


async def send_answer(stream_id: str, request: Request):
    data = await request.json()
    answer = data.get("answer")
    jsonData = {"answer": answer}
    return integration.avatarconnector.send_answer(stream_id, jsonData)


async def render_text(stream_id: str, request: Request):
    data = await request.json()
    text = data.get("text")
    return integration.avatarconnector.render_text(stream_id, text)

def stop_render(stream_id: str):
    return integration.avatarconnector.stop_render(stream_id)

def close_stream(stream_id: str):
    return integration.avatarconnector.close_stream(stream_id)

def add_user(email: str, password: str):
    return integration.chatconnector.create_user(email, password)
def start_chat(user_id: str):
    return integration.chatconnector.start_new_chat(user_id)

def get_all_chat_history(user_id: str):
    return integration.chatconnector.get_all_chat_history(user_id)

def add_to_chat_history(user_id: str, content: str, conversation_id: str, Role: str):
    return integration.chatconnector.add_to_chat_history(user_id, content, conversation_id, Role)


def get_chat_history(user_id: str, conversation_id: str):
    return integration.chatconnector.get_chat_history(user_id, conversation_id)


