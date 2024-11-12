from typing import Optional, Dict, Any
from fastapi import HTTPException
from azure.data.tables import  TableServiceClient,UpdateMode
class GenericTableClient:
    def __init__(self, table_name: str,table_service_client:TableServiceClient):
        self.table_client = table_service_client.get_table_client(table_name=table_name)

    async def add_entity(self, entity: Dict[str, Any]) -> None:
        try:
            self.table_client.create_entity(entity)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def get_entities(self, filter_expression: Optional[str] = None) -> list:
        try:
            if filter_expression:
                entities = self.table_client.query_entities(filter_expression)
            else:
                entities = self.table_client.list_entities()
            return list(entities)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def update_entity(self, entity: Dict[str, Any]) -> None:
        try:
            self.table_client.update_entity(entity, mode=UpdateMode.MERGE)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))