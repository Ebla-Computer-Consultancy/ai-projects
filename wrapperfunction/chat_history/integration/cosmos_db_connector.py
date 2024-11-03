from typing import Optional
from wrapperfunction.core import config
from azure.data.tables import TableServiceClient
from fastapi import HTTPException
from wrapperfunction.chat_history.model.message_entity import MessageEntity
from wrapperfunction.chat_history.model.conversation_entity import ConversationEntity
from wrapperfunction.core.model.entity_setting import CosmosDBTableSetting

Table_service_Client = TableServiceClient.from_connection_string(conn_str=config.CONNECTION_STRING)
conversation_table = config.load_cosmos_table_settings(config.CONVERSATION_TABLE_NAME)
message_table = config.load_cosmos_table_settings(config.MESSAGE_TABLE_NAME)
message_table_client= Table_service_Client.get_table_client(table_name=message_table.name)


    
async def add_to_chat_history(user_mess_entity:MessageEntity,assistant_mess_entity:MessageEntity,conv_entity:Optional[ConversationEntity] = None): 
    try: 
        message_table_client.create_entity(user_mess_entity.to_dict())
        message_table_client.create_entity(assistant_mess_entity.to_dict())
        if conv_entity:
            conversation_table_client= Table_service_Client.get_table_client(table_name=conversation_table.name)
            conversation_table_client.create_entity(conv_entity.to_dict())


    except Exception as e:
        return HTTPException(400,e)
def get_all_conversations(user_id):
    try:
        
        res=Table_service_Client.get_table_client(table_name=conversation_table.name).query_entities(f"user_id eq '{user_id}'")
        return list(res)
    except Exception as e:
        return HTTPException(400,e)    
 
    
def get_chat_history(conversation_id):
    try:
        
        res=Table_service_Client.get_table_client(table_name=message_table.name).query_entities(f" conversation_id eq '{conversation_id}'")
        return list(res)
    except Exception as e:
        return HTTPException(400,e)


