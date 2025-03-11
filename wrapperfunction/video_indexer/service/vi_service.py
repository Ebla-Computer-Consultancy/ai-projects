from fastapi.datastructures import UploadFile
from wrapperfunction.chat_history.bp.chat_history_blue_print import StatusCode
from wrapperfunction.chatbot.integration import openai_connector
from wrapperfunction.core import config
from wrapperfunction.core.model.service_return import ServiceReturn
from wrapperfunction.video_indexer.integration import vi_connector


async def get_all_videos():
    res_data = await vi_connector.get_all_videos()
    videos = []
    for v in res_data["results"]:
                video_id = v["id"]
                video_name = v["name"]
                thumbnail_url = vi_connector.get_video_thumbnail(video_id)
                videos.append({"name": video_name, "id": video_id, "thumbnail_url": thumbnail_url})

    return {"status": "SUCCESS","message": "Videos retrieved successfully","data": {"videos": videos}}

async def get_video_index(video_id: str,bot_name: str,language:str):
    res_data = await vi_connector.get_video_index(video_id,language)
    
    if res_data.get("state") == "Processed":
        await add_thumbnail_urls(res_data,video_id)
        transcript = " ".join(entry["text"] for entry in res_data.get("videos", [{}])[0].get("insights", {}).get("transcript", []))
        if not transcript.strip():
            summary = "No transcript available."
        else:
            summary_content = transcript
            summary = summarize_with_openai(summary_content, bot_name, language)                    
        video_stream_url = await vi_connector.get_stream_url(video_id,"video/mp4")
        audio_stream_url = await vi_connector.get_stream_url(video_id,"audio/mp4")
        video_download_url=await vi_connector.get_video_download_url(video_id)
        video_caption=await vi_connector.get_video_caption_url(video_id)
        return ServiceReturn(status=StatusCode.SUCCESS,message=f"Indexing completed successfully for video ID: {video_id}",data={"res_data": res_data,"summary": summary,"video_stream_url": video_stream_url,"audio_stream_url":audio_stream_url,"video_download_url":video_download_url,"video_caption":video_caption}).to_dict()

    elif res_data.get("state") == "Failed":
        return ServiceReturn(status=StatusCode.BAD_REQUEST,message=f"Indexing failed for video ID: {video_id}",data=res_data).to_dict()
    else:
        return ServiceReturn(status=StatusCode.PENDING,message=f"Indexing in progress for video ID: {video_id}",data=res_data).to_dict()

async def reindex_video(v_id: str):
    return await vi_connector.reindex_video(v_id)

async def upload_video(video_file: UploadFile,language: str):
    return await vi_connector.upload_video(video_file,language)

def get_supported_languages():
    return vi_connector.get_supported_languages()
   
async def add_thumbnail_urls(res_data, video_id):
    access_token = vi_connector.get_access_token()["data"]
    base_url = f"https://api.videoindexer.ai/{config.ACCOUNT_REGION}/Accounts/{config.VIDEO_INDEXER_ACCOUNT_ID}/Videos/{video_id}/Thumbnails/"
    
    thumbnail_id = res_data.get("summarizedInsights", {}).get("thumbnailId")
    if thumbnail_id:
        res_data["summarizedInsights"]["thumbnail_url"] = f"{base_url}{thumbnail_id}?accessToken={access_token}"

    for face in res_data.get("summarizedInsights", {}).get("faces", []):
        if face_thumbnail_id := face.get("thumbnailId"):
            face["thumbnail_url"] = f"{base_url}{face_thumbnail_id}?accessToken={access_token}"

    for video in res_data.get("videos", []):
        video_thumbnail_id = video.get("thumbnailId")
        if video_thumbnail_id:
            video["thumbnail_url"] = f"{base_url}{video_thumbnail_id}?accessToken={access_token}"

        for insight in video.get("insights", {}).get("faces", []):
            insight_thumbnail_id = insight.get("thumbnailId")
            if insight_thumbnail_id:
                insight["thumbnail_url"] = f"{base_url}{insight_thumbnail_id}?accessToken={access_token}"

        for label in video.get("insights", {}).get("labels", []):
            label_thumbnail_id = label.get("thumbnailId")
            if label_thumbnail_id:
                label["thumbnail_url"] = f"{base_url}{label_thumbnail_id}?accessToken={access_token}"

        for scene in video.get("insights", {}).get("scenes", []):
            scene_thumbnail_id = scene.get("thumbnailId")
            if scene_thumbnail_id:
                scene["thumbnail_url"] = f"{base_url}{scene_thumbnail_id}?accessToken={access_token}"

        for shot in video.get("insights", {}).get("shots", []):
            shot_thumbnail_id = shot.get("thumbnailId")
            if shot_thumbnail_id:
                shot["thumbnail_url"] = f"{base_url}{shot_thumbnail_id}?accessToken={access_token}"

            for key_frame in shot.get("keyFrames", []):
                key_frame_thumbnail_id = key_frame.get("instances", [{}])[0].get("thumbnailId")
                if key_frame_thumbnail_id:
                    key_frame["thumbnail_url"] = f"{base_url}{key_frame_thumbnail_id}?accessToken={access_token}"

def summarize_with_openai(content: str, bot_name: str, language: str):
    try:
        response = openai_connector.chat_completion(
            chatbot_setting=config.load_chatbot_settings(bot_name),
            chat_history=[{"role": "system", "content": f"Summarize the following content in {language}: {content},If summarization is not possible, respond with 'No transcript available.'"}]
        )
        
        return response["message"]["content"].strip()
    except Exception as e:
        return f"Error summarizing content: {str(e)}"