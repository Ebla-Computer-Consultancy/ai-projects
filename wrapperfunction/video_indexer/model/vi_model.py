from pydantic import BaseModel


class VIRequest(BaseModel):
    video_name: str | None = None
    video_url: str | None = None
    video_id: str | None = None


    
    