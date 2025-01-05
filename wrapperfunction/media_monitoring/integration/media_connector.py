from fastapi import HTTPException
from wrapperfunction.core import config
from wrapperfunction.search.integration import aisearch_connector


def get_media_info() -> dict:
    try:
        media_settings = config.ENTITY_SETTINGS.get("media_settings",{})
        info = media_settings.get("info",{}) if len(media_settings) > 0 else None
        if info is not None and len(info) > 0: 
            return info
        else:
            raise HTTPException(status_code=500, detail="There is no media setting info provided")
    except Exception as e:
        raise HTTPException(status_code=500, detail="There is no media setting info provided")