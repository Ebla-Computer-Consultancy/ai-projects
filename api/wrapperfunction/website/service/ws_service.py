import json
from typing import List
from wrapperfunction.core import config
import wrapperfunction.integration as integration
from wrapperfunction.website.model.search_criterial import searchCriteria
from wrapperfunction.website.model.chat_message import ChatMessage
from fastapi import status, HTTPException

def search(rs: searchCriteria):
    try:
        # Get the search terms from the request form
        search_text = rs.query
        # If a facet is selected, use it in a filter
        filter_expression = None
        if rs.facet:
            filter_expression = "metadata_author eq '{0}'".format(rs.facet)
        sort_expression = "search.score()"

        # submit the query and get the results
        results = integration.aisearchconnector.search_query(config.SEARCH_INDEX, search_text, filter_expression, sort_expression,rs.page_size,rs.page_number)
        # render the results
        return results

    except Exception as error:
        return json.dumps({"error": True, "message": str(error)})
    


def chat(messageHistory: List[ChatMessage]):
    try:
        chat_history_arr = messageHistory
        if bool(len([x for x in chat_history_arr if x.role == "system"])):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "system messages is not allowed"
            )
        system_message="You are an intelligent assistant specifically designed to help users with research and answer questions related to the General Authority for Real Estate Regulation. Your goal is to provide accurate and reliable information about the regulations, laws, and procedures pertaining to the Authority, as well as any other inquiries related to the real estate sector in the country.You will detect the input language and responds in the same language. You must add Arabic diacritics to your output answer if the prompt is in Arabic"
        chat_history = [{
             "role": "system",
             "content":system_message
            }]
        for item in chat_history_arr:
            chat_history.append(item.model_dump())
        # Get response from OpenAI ChatGPT
        results = integration.openaiconnector.chat_completion(config.SEARCH_INDEX,chat_history,system_message)
        return results  
    except Exception as error:
        return json.dumps({"error": True, "message": str(error)})
