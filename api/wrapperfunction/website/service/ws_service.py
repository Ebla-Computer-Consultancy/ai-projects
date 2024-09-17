import asyncio
import json
from wrapperfunction.website.model.chat_payload import ChatPayload
from wrapperfunction.core import config
import wrapperfunction.integration as integration
from wrapperfunction.website.model.search_criterial import searchCriteria
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
    


async def chat(chat_payload: ChatPayload):
    try:
        chat_history_arr = chat_payload.messages
        if bool(len([x for x in chat_history_arr if x.role == "system"])):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "system messages is not allowed"
            )
        chat_history = []
        for item in chat_history_arr:
            chat_history.append(item.model_dump())

        if chat_payload.stream_id and is_arabic(chat_history[-1]['content']):
            system_message=f"IMPORTANT: I want you to answer the questions in Arabic with diacritics (tashkeel) in every response., like this:'السَّلَامُ عَلَيْكُمْ'. Represent numbers in alphabet only not numeric. Always give short answers. {config.SYSTEM_MESSAGE}"
        else:
            system_message=f"{config.SYSTEM_MESSAGE}, You will detect the input language and responds in the same language."
        
        chat_history.insert(0, {
             "role": "system",
             "content":system_message
            })
        
        # Get response from OpenAI ChatGPT
        results = integration.openaiconnector.chat_completion_mydata(config.SEARCH_INDEX,chat_history,system_message)
        if chat_payload.stream_id is not None:
            #await integration.avatarconnector.render_text_async(chat_payload.stream_id,results['message']['content'])
            asyncio.create_task(integration.avatarconnector.render_text_async(chat_payload.stream_id,results['message']['content']))
        return results  
    except Exception as error:
        return json.dumps({"error": True, "message": str(error)})
    
def is_arabic(text):
    arabic_range = (0x0600, 0x06FF)  # Arabic script range
    return any(arabic_range[0] <= ord(char) <= arabic_range[1] for char in text)