from wrapperfunction.core import config
from azure.data.tables import TableServiceClient
from fastapi import HTTPException
from wrapperfunction.common.model.conversation_entity import ConversationEntity
from wrapperfunction.common.model.message_entity import MessageEntity
from wrapperfunction.common.model.role import Role 



Table_service_Client = TableServiceClient.from_connection_string(conn_str=config.CONNECTION_STRING)
MESSAGE_Table_Client=Table_service_Client.get_table_client(table_name=config.MESSAGE_TABLE_NAME)
USER_Table_Client=Table_service_Client.get_table_client(table_name=config.USER_TABLE_NAME)
CONVERSATION_Table_Client=Table_service_Client.get_table_client(table_name=config.CONVERSATION_TABLE_NAME)




def start_new_chat(user_id,conversation_id,content,Role):
    try:    
        conv_entity=ConversationEntity(user_id,conversation_id).to_dict()
        CONVERSATION_Table_Client.create_entity(conv_entity)
        message_entity=MessageEntity(user_id, content, conversation_id, Role).to_dict() 
        res=MESSAGE_Table_Client.create_entity(message_entity)
        return res
    except Exception as e:
        return HTTPException(400,e)

    

def add_to_chat_history(user_id:str, content:str, conversatsion_id:str,Role:Role): 
    try: 
        message_entity=MessageEntity(user_id, content, conversatsion_id, Role).to_dict() 
        res=MESSAGE_Table_Client.create_entity(message_entity)
        return res
    except Exception as e:
        return HTTPException(400,e)
def get_all_chat_history(user_id):
    try:
        res=CONVERSATION_Table_Client.query_entities(f"PartitionKey eq '{user_id}'")
        return list(res)
    except Exception as e:
        return HTTPException(400,e)    
 
    
def get_chat_history(conversation_id):
    try:
        res=CONVERSATION_Table_Client.query_entities(f" conversation_id eq '{conversation_id}'")
        return list(res)
    except Exception as e:
        return HTTPException(400,e)


