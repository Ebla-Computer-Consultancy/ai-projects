from wrapperfunction.core import config
from azure.data.tables import TableServiceClient
from fastapi import HTTPException
from datetime import datetime
from uuid import uuid4
from wrapperfunction.common.utils.helper import ChatEntity , Role
Table_service_Client = TableServiceClient.from_connection_string(conn_str=config.CONNECTION_STRING)
Table_Client=Table_service_Client.get_table_client(table_name=config.TABLE_NAME)


def start_new_chat(user_id):
    entity=ChatEntity(user_id).to_dict()
    Table_Client.create_entity(entity)
    return entity

def add_to_chat_history(user_id:str, content:str, conversatsion_id:str,Role:Role): 
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
 
    
def get_chat_history(user_id,conversation_id):
    try:
        res=Table_Client.query_entities(f"PartitionKey eq '{user_id}' and conversation_id eq '{conversation_id}'")
        return list(res)
    except Exception as e:
        return HTTPException(400,e)


