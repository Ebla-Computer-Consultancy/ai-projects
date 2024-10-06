from fastapi import APIRouter, HTTPException, Request
import wrapperfunction.skills.service.skills_service as skillsservice
from fastapi import HTTPException , UploadFile, File
import aiofiles
import logging
import os 

router = APIRouter()

@router.post("/extract-text/")
async def extract_text(file: UploadFile = File()):
    try:
        logging.info(f"{file.filename}")
        # print(file.filename)
        print(os.path)
        file_path = os.path.join("./export/docs", file.filename)
        
        contents = await file.read()
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(contents)
        # file.close()
        return  await skillsservice.extract_text(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

        
        