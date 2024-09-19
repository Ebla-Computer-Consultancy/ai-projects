import asyncio
import json
import re
from wrapperfunction.website.model.chat_payload import ChatPayload
from wrapperfunction.website.model.chat_message import ChatMessage
from wrapperfunction.website.model.chat_message import Roles
from wrapperfunction.core import config
import wrapperfunction.integration as integration
from wrapperfunction.website.model.search_criterial import searchCriteria
from fastapi import status, HTTPException
from azure.data.tables import TableServiceClient
from azure.core.exceptions import HttpResponseError

connection_string = config.CONNECTION_STRING
table_service_client = TableServiceClient.from_connection_string(conn_str=connection_string)
table_client = table_service_client.get_table_client(config.CONTAINER_NAME)
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
        is_ar = is_arabic(chat_history_arr[-1].content)
        if chat_payload.stream_id:
            if is_ar:
                system_message=f"IMPORTANT: I want you to answer the questions in Arabic with diacritics (tashkeel) in every response., like this:'السَّلَامُ عَلَيْكُمْ'. Represent numbers in alphabet only not numeric. Always respond with very short answers. {config.SYSTEM_MESSAGE}"
                chat_history= [{
                "role": Roles.User.value,
                "content":"من انت؟"
                },
                {
                "role": Roles.Assistant.value,
                "content":"أنا مساعد ذكي مصمم خصيصًا للمساعدة"
                },{
                "role": Roles.User.value,
                "content":"أضف تشكيل اللغة العربية إلى الإجابة دائما."
                },{
                "role": Roles.Assistant.value,
                "content":"أنا مُساعِد ذكي مُصَمَّم خِصِّيصًا للمُساعَدةِ"
                }
                ]
            else:
                system_message=f"{config.SYSTEM_MESSAGE}, I want you to detect the input language and responds in the same language. Always respond with very short answers."
        else:
            system_message=f"{config.SYSTEM_MESSAGE}, I want you to detect the input language and responds in the same language."
        
        chat_history.insert(0, {
             "role":Roles.System.value,
             "content":system_message
            })
        for item in chat_history_arr:
            chat_history.append(item.model_dump())
        
        # Get response from OpenAI ChatGPT
        results = integration.openaiconnector.chat_completion_mydata(config.SEARCH_INDEX,chat_history,system_message)
        if chat_payload.stream_id is not None:
            is_ar=is_arabic(results['message']['content'][:30])
            #await integration.avatarconnector.render_text_async(chat_payload.stream_id,results['message']['content'])
        #Here we save chat history to Cosmos DB
        chat_data = {
            "PartitionKey": chat_payload.user_id,  # user_id as PartitionKey
            "RowKey": str(chat_payload.stream_id),  # stream_id as RowKey 
            "user_id": chat_payload.user_id,
            "stream_id": chat_payload.stream_id,
            "messages": chat_history,
            "response": results['message']['content']
        }
        table_client.upsert_entity(chat_data) # here we store chat history in Cosmos DB 
        return results  
    except HttpResponseError as cosmos_error:
        return {"error": True, "message": f"Cosmos DB Table API error: {str(cosmos_error)}"}
    except Exception as error:
        return {"error": True, "message": str(error)}
    
def is_arabic(text):
    arabic_range = (0x0600, 0x06FF)  # Arabic script range
    return any(arabic_range[0] <= ord(char) <= arabic_range[1] for char in text)
def clean_text(text):
    # Remove any pattern like [doc*], where * represents numbers
    # Remove non-readable characters (anything not a letter, number, punctuation, or whitespace)
    # text = re.sub(r'[^\w\s,.!?\'\"-]', '', text)
    text = re.sub(r'\[doc\d+\]', '', text)
    return text
