from fastapi.datastructures import UploadFile
from wrapperfunction.video_indexer.integration import vi_connector


async def get_all_videos():
    return await vi_connector.get_all_videos()

async def get_video_index(video_id: str,bot_name: str,language:str):
    return await vi_connector.get_video_index(video_id,bot_name,language)

async def reindex_video(v_id: str):
    return await vi_connector.reindex_video(v_id)

async def upload_video(video_file: UploadFile,language: str):
    return await vi_connector.upload_video(video_file,language)

def get_supported_languages():
    return vi_connector.get_supported_languages()
   


