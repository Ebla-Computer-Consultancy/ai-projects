from fastapi import APIRouter
import wrapperfunction.speech.service.speech_service  as speechservice

router = APIRouter()


# @router.post("/transcribe")
# async def transcribe(file: bytes = File(...), filename: str = Form(...)):
#     return await speechservice.transcribe(file,filename)


@router.get("/token")
def get_speech_token():
    return speechservice.get_speech_token()
