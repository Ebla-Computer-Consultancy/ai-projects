from fastapi import APIRouter,Request
import wrapperfunction.avatar.service.avatar_service as avatarservice

router = APIRouter()

@router.post("/start-stream")
def start_stream(size: str = 'half-size',stream_id: str = None):
    return avatarservice.start_stream(size,stream_id)


@router.post("/send-candidate/{stream_id}")
async def send_candidate(stream_id: str, request: Request):
    return await avatarservice.send_candidate(stream_id, request)


@router.put("/send-answer/{stream_id}")
async def send_answer(stream_id: str, request: Request):
    return await avatarservice.send_answer(stream_id, request)


@router.post("/render-text/{stream_id}")
async def render_text(stream_id: str, request: Request):
    return await avatarservice.render_text(stream_id, request)

@router.delete("/stop-render/{stream_id}")
def stop_render(stream_id: str):
    return avatarservice.stop_render(stream_id)

@router.delete("/close-stream/{stream_id}")
def close_stream(stream_id: str):
    return avatarservice.close_stream(stream_id)
