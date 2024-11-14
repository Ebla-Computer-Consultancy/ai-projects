from wrapperfunction.admin.integration.crawl_integration import (
    run_crawler,
    process_and_upload,
    upload_files_to_blob,
    delete_blobs_base_on_metadata,
    delete_base_on_subfolder,
    edit_blob_by_new_jsonfile,
    split_json_file,
    update_json_with_pdf_text,
    scrape_csv,
)
from wrapperfunction.admin.integration.aisearch_connector import delete_indexed_data
from wrapperfunction.core.utls.helper import download_pdfs
from fastapi import HTTPException, UploadFile
from fastapi.responses import JSONResponse
import json
from urllib.parse import unquote


def crawl(link: str):
    filepath, filename = run_crawler(link)

    split_json_file(
        filepath, filepath[:-5] + "-links.json", filepath[:-5] + "-docs.json"
    )
    download_pdfs(filepath[:-5] + "-docs.json", "./export/docs/" + filepath[2:-5])
    update_json_with_pdf_text(
        filepath[:-5] + "-docs.json", "./export/docs/" + filepath[2:-5]
    )
    process_and_upload(filepath[:-5] + "-links.json", "./export/", link)
    process_and_upload(
        "updated_" + filepath[2:-5] + "-docs.json", "./export/docs/", link, True
    )
    return {"message": "Crawling completed successfully"}


def scrape(file: UploadFile, container_name: str):
    results = scrape_csv(file, container_name)
    process_and_upload("./" + container_name + ".json", "./export/", "  ")
    return results


async def delete_blob(metadata_key, metadata_value):
    if not metadata_key or not metadata_value:
        raise HTTPException(status_code=400, detail="Missing required parameters")
    try:
        print(metadata_value)
        metadata_value_ = unquote(metadata_value)
        print(metadata_value_)
        delete_blobs_base_on_metadata(metadata_key, metadata_value)
        return JSONResponse(
            content={
                "message": f"Blob with metadata {metadata_key}={metadata_value} deleted successfully"
            },
            status_code=200,
        )
    except:
        raise HTTPException(status_code=404, detail="Blob not found")


async def delete_subfolder(container_name, subfolder_name):
    if not container_name or not subfolder_name:
        raise HTTPException(status_code=400, detail="Missing required parameters")
    try:
        print(container_name)
        print(subfolder_name)
        delete_base_on_subfolder(subfolder_name, container_name)
        return JSONResponse(
            content={
                "message": f"Subfolder '{subfolder_name}' in the container {container_name} deleted successfully."
            },
            status_code=200,
        )
    except:
        raise HTTPException(status_code=404, detail="Subfolder not found")


def edit_blob(new_content_file, metadata_key, metadata_value):
    try:
        new_content = json.load(new_content_file.file)  #
        new_content_file.file.seek(0)
        print(new_content_file.file.read())
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to read new content file: {str(e)}"
        )
    edit_blob_by_new_jsonfile(metadata_key, metadata_value, new_content)


def delete_indexes(index_name: str, key: str, value):
    try:
        delete_indexed_data(index_name, key, value)
        return JSONResponse(
            content={"message": f"index '{index_name} deleted successfully."},
            status_code=200,
        )
    except:
        raise HTTPException(status_code=404, detail="index not found")
