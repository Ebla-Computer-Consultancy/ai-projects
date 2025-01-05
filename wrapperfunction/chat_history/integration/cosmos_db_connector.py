from typing import Optional, Dict, Any
from wrapperfunction.core import config
from azure.data.tables import TableServiceClient
from wrapperfunction.chat_history.model.Generic_Table_Client import GenericTableClient


table_service_client = TableServiceClient.from_connection_string(conn_str=config.COSMOS_CONNECTION_STRING)

def get_table_client(conn_str):
    return TableServiceClient.from_connection_string(conn_str=conn_str)

async def add_entity(table_name: str, entity: Dict[str, Any], conn_str: str = None):
    if conn_str is None:
        generic_table_client = GenericTableClient(table_name,table_service_client)
    else:
        generic_table_client = GenericTableClient(table_name,get_table_client(conn_str))
    await generic_table_client.add_entity(entity)

def get_entities(table_name: str, filter_expression: Optional[str] = None, conn_str: str= None):
    if conn_str is None:
        generic_table_client = GenericTableClient(table_name,table_service_client)
    else:
        generic_table_client = GenericTableClient(table_name,get_table_client(conn_str))
    return generic_table_client.get_entities(filter_expression)

def update_entity(table_name: str, entity: Dict[str, Any], conn_str: str = None):
    if conn_str is None:
        generic_table_client = GenericTableClient(table_name,table_service_client)
    else:
        generic_table_client = GenericTableClient(table_name,get_table_client(conn_str))
    return generic_table_client.update_entity(entity)

def delete_entity(table_name: str, partition_key: str, row_key: str):
    generic_table_client = GenericTableClient(table_name,table_service_client)
    return generic_table_client.delete_entity(partition_key=partition_key,row_key=row_key)
  