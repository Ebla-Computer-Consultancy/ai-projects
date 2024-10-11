import os
from azure.data.tables import TableServiceClient
from dotenv import load_dotenv
from fastapi import HTTPException
from datetime import datetime
from uuid import uuid4

TABLE_NAME ="data"

connection_string='DefaultEndpointsProtocol=https;AccountName=chathistorys;AccountKey=LMPqi1aOpre7aCYPk0ZLSCVhmOQg5TCKPc1kqLhl74vnoPsoeJhnmV9FC2LlQFKPyhq7twqGDTTqACDbkOot7Q==;TableEndpoint=https://chathistorys.table.cosmos.azure.com:443/;'

Table_service_Client = TableServiceClient.from_connection_string(conn_str=connection_string)
Table_Client=Table_service_Client.get_table_client(table_name=TABLE_NAME)
def start_new_chat(user_id,content='User Starts New Chat',Role='User'):
    entity = {
        "PartitionKey": user_id,
        "RowKey": str(uuid4()),
        "content": content,
        "Role": Role,
        "Timestamp": datetime.now().isoformat(),
        "conversation_id": str(uuid4()),
    }
    Table_Client.create_entity(entity)
    return entity

def add_to_chat_history(user_id, content, conversatsion_id,Role): 
    try:  
        res=Table_Client.create_entity({'PartitionKey':user_id,'RowKey':str(uuid4()),'conversation_id':conversatsion_id, 'content':content, 'timestamp':datetime.now().isoformat(),'Role':Role})
        return res
    except Exception as e:
        return HTTPException(400,e)
def get_all_chat_history(user_id):
    try:
        res=Table_Client.query_entities(f"PartitionKey eq '{user_id}'")
        return list(res)
    except Exception as e:
        return HTTPException(400,e)    
 
    
# def get_chat_history(user_id,conversation_id):
#     try:
#         res=Table_Client.query_entities(f"PartitionKey eq '{user_id}' and conversation_id eq '{conversation_id}'")
#         return list(res)
#     except Exception as e:
#         return HTTPException(400,e)


