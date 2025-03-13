import wrapperfunction.avatar.integration.avatar_connector as avatar_connector
from fastapi import Request

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


async def render_text(stream_id: str, request: Request):
    data = await request.json()
    text = data.get("text")
    return avatar_connector.render_text(stream_id, text)

async def render_text_async(stream_id: str, text: str, is_ar: bool):
    return avatar_connector.render_text_async(stream_id, text, is_ar)

def stop_render(stream_id: str):
    return avatar_connector.stop_render(stream_id)

def close_stream(stream_id: str):
    return avatar_connector.close_stream(stream_id)

def update_video(text: str):
    return avatar_connector.update_video(text)

def retrieve_video():
    return avatar_connector.retrieve_video()
"""
def render_video(video_id: str):
    return avatar_connector.render_video(video_id)

def delete_video(video_id: str):
    return avatar_connector.delete_video(video_id)

def list_videos(page: int, limit:int, with_deleted:bool):
    return avatar_connector.list_videos(page, limit, with_deleted)
"""