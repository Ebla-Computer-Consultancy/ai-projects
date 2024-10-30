import wrapperfunction.avatar.integration.avatar_connector as avatarconnector
from fastapi import Request

def start_stream(size: str,stream_id: str):
    return avatarconnector.start_stream(size,stream_id)


async def send_candidate(stream_id: str, request: Request):
    data = await request.json()
    candidate_ = data.get("candidate")
    jsonData = {"candidate": candidate_}
    return avatarconnector.send_candidate(stream_id, jsonData)


async def send_answer(stream_id: str, request: Request):
    data = await request.json()
    answer = data.get("answer")
    jsonData = {"answer": answer}
    return avatarconnector.send_answer(stream_id, jsonData)


async def render_text(stream_id: str, request: Request):
    data = await request.json()
    text = data.get("text")
    return avatarconnector.render_text(stream_id, text)

async def render_text_async(stream_id: str, text: str, is_ar: bool):
    return avatarconnector.render_text_async(stream_id, text, is_ar)

def stop_render(stream_id: str):
    return avatarconnector.stop_render(stream_id)

def close_stream(stream_id: str):
    return avatarconnector.close_stream(stream_id)
