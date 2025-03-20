import asyncio
import wrapperfunction.avatar.integration.avatar_connector as avatar_connector
from fastapi import HTTPException, Request

from wrapperfunction.core import config

def start_stream(size: str,stream_id: str):
    return avatar_connector.start_stream(size,stream_id)


async def send_candidate(stream_id: str, request: Request):
    data = await request.json()
    candidate_ = data.get("candidate")
    jsonData = {"candidate": candidate_}
    return avatar_connector.send_candidate(stream_id, jsonData)


async def send_answer(stream_id: str, request: Request):
    data = await request.json()
    answer = data.get("answer")
    jsonData = {"answer": answer}
    return avatar_connector.send_answer(stream_id, jsonData)

def render_text_async(stream_id: str, text: str, is_ar: bool):
    try:
        return asyncio.create_task(avatar_connector.render_text_async(stream_id, text, is_ar))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
async def greeting(stream_id: str, bot_name: str, is_ar: bool):
    text = (
        config.load_chatbot_settings(bot_name).greeting_message["ar"]
        if is_ar
        else config.load_chatbot_settings(bot_name).greeting_message["en"]
    )
    return asyncio.create_task(avatar_connector.render_text_async(stream_id, text, is_ar))
def stop_render(stream_id: str):
    return avatar_connector.stop_render(stream_id)

def close_stream(stream_id: str):
    return avatar_connector.close_stream(stream_id)

def update_video(text: str):
    return avatar_connector.update_video(text)

def retrieve_video():
    return avatar_connector.retrieve_video()
