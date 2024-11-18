from typing import Optional, Dict, Any
from wrapperfunction.core import config
from azure.data.tables import TableServiceClient
from wrapperfunction.chat_history.model.Generic_Table_Client import GenericTableClient


table_service_client = TableServiceClient.from_connection_string(conn_str=config.CONNECTION_STRING)


async def add_entity(table_name: str, entity: Dict[str, Any]):
    generic_table_client = GenericTableClient(table_name,table_service_client)
    await generic_table_client.add_entity(entity)

def get_entities(table_name: str, filter_expression: Optional[str] = None):
    generic_table_client = GenericTableClient(table_name,table_service_client)
    return generic_table_client.get_entities(filter_expression)
def update_entity(table_name: str, entity: Dict[str, Any]):
    generic_table_client = GenericTableClient(table_name,table_service_client)
    return generic_table_client.update_entity(entity)
  