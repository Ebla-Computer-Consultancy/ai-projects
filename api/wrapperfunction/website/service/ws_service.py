import asyncio
import json
import re
from typing import List
from wrapperfunction.website.model.chat_payload import ChatPayload
from wrapperfunction.core import config
import wrapperfunction.integration as integration
from wrapperfunction.website.model.search_criterial import searchCriteria
from fastapi import status, HTTPException
from num2words import num2words
import mishkal.tashkeel

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
        system_message=f"{config.SYSTEM_MESSAGE} You will detect the input language and responds in the same language. You must add Arabic diacritics to your output answer if the prompt is in Arabic"  #.represent any numbers in the answer by alphabet"
        chat_history = [{
             "role": "system",
             "content":system_message
            }]
        for item in chat_history_arr:
            chat_history.append(item.model_dump())
        # Get response from OpenAI ChatGPT
        results = integration.openaiconnector.chat_completion(config.SEARCH_INDEX,chat_history,system_message)
        if chat_payload.stream_id is not None:
            #await integration.avatarconnector.render_text_async(chat_payload.stream_id,results['message']['content'])
            asyncio.create_task(integration.avatarconnector.render_text_async(chat_payload.stream_id,clean_text(results['message']['content'])))
            print("after calling the render")
        return results  
    except Exception as error:
        return json.dumps({"error": True, "message": str(error)})
    
def clean_text(text):
    vocalizer = mishkal.tashkeel.TashkeelClass()
    # Remove any pattern like [doc*], where * represents numbers
    # Remove non-readable characters (anything not a letter, number, punctuation, or whitespace)
    # text = re.sub(r'[^\w\s,.!?\'\"-]', '', text)
    text = re.sub(r'\[doc\d+\]', '', text)
    def add_tashkeel(text):
        vocalized_text = vocalizer.tashkeel(text)
        return vocalized_text
    
    def number_to_arabic_with_tashkeel(number):
        arabic_word = num2words(int(number), lang='ar')
        arabic_word_with_tashkeel = add_tashkeel(arabic_word)
        return arabic_word_with_tashkeel
    
    def replace_arabic_numbers_with_words(phrase):
        def replace_number(match):
            number = match.group(0)
            return number_to_arabic_with_tashkeel(number)
        arabic_digit_pattern = r'[\u0660-\u0669]+'
        converted_phrase = re.sub(arabic_digit_pattern, replace_number, phrase)
        phrase_with_tashkeel = add_tashkeel(converted_phrase)
        return phrase_with_tashkeel
    return text