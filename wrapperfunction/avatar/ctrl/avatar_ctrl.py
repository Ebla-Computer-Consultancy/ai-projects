from fastapi import APIRouter,Request
import wrapperfunction.avatar.service.avatar_service as avatar_service

router = APIRouter()

@router.post("/start-stream")
def start_stream(size: str = 'half-size',stream_id: str = None):
    return avatar_service.start_stream(size,stream_id)


@router.post("/send-candidate/{stream_id}")
async def send_candidate(stream_id: str, request: Request):
    return await avatar_service.send_candidate(stream_id, request)


@router.put("/send-answer/{stream_id}")
async def send_answer(stream_id: str, request: Request):
    return await avatar_service.send_answer(stream_id, request)


@router.post("/render-text/{stream_id}")
async def render_text(stream_id: str, request: Request):
    return await avatar_service.render_text(stream_id, request)

@router.delete("/stop-render/{stream_id}")
def stop_render(stream_id: str):
    return avatar_service.stop_render(stream_id)

@router.delete("/close-stream/{stream_id}")
def close_stream(stream_id: str):
    return avatar_service.close_stream(stream_id)

@router.post("/update-video")
def update_video(text: str):
    return avatar_service.update_video(text)

@router.get("/retrieve-video")
def retrieve_video():
    return avatar_service.retrieve_video()

"""
@router.post("/render-video/{video_id}")
def render_video(video_id: str):
    return avatar_service.render_video(video_id)

@router.get("/list-videos")
def list_videos(page: int=1, limit:int=50, with_deleted:bool= False):
    return avatar_service.list_videos(page, limit, with_deleted)

@router.delete("/delete-video/{video_id}")
def delete_video(video_id: str):
    return avatar_service.delete_video(video_id)
"""