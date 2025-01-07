import json
from fastapi import HTTPException
from fastapi.responses import JSONResponse
import requests
from wrapperfunction.core import config
import wrapperfunction.search.integration.aisearch_connector as aisearchconnector
from wrapperfunction.search.model.search_criterial import searchCriteria

def search(bot_name: str,rs: searchCriteria):
    try:
        # Get the search terms from the request form
        search_text = rs.query
        # If a facet is selected, use it in a filter
        filter_expression = None
        if rs.facet:
            filter_expression = "metadata_author eq '{0}'".format(rs.facet)
        sort_expression = "search.score()"
        chatbot_settings = config.load_chatbot_settings(bot_name)
        # submit the query and get the results
        results = aisearchconnector.search_query(
            chatbot_settings.index_name,
            search_text,
            filter_expression,
            sort_expression,
            rs.page_size,
            rs.page_number,
        )
        # render the results
        return results

    except Exception as error:
        return json.dumps({"error": True, "message": str(error)})



def delete_indexes(index_name: str, key: str, value):
    try:
        aisearchconnector.delete_indexed_data(index_name, key, value)
        return JSONResponse(
            content={"message": f"index '{index_name} deleted successfully."},
            status_code=200,
        )
    except:
        raise HTTPException(status_code=404, detail="Blob not found")

def reset_index(index_name: str):
    try:
        aisearchconnector.reset_indexed_data(index_name)
        return JSONResponse(content={"message": f"index '{index_name} deleted successfully."}, status_code=200)
    except:
        raise HTTPException(status_code=404, detail="index not found")

def run_indexer(index_name: str):
    try:
        aisearchconnector.run_indexer(index_name)
        return JSONResponse(content={"message": f"index '{index_name} reloaded successfully."}, status_code=200)
    except:
        raise HTTPException(status_code=404, detail="index not found")

def index_info(index_name: str):
    try:
        return aisearchconnector.get_index_info(index_name)
    except:
        raise HTTPException(status_code=404, detail="index not found")

def indexes_name():
    try:
        return aisearchconnector.get_indexes_name()
    except:
        raise HTTPException(status_code=404, detail="index not found")
    
def update_index(index_name: str, data):
    try:
        return aisearchconnector.update_index(index_name,data)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{str(e)}")

