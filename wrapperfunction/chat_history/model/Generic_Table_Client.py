from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from azure.data.tables import  TableServiceClient,UpdateMode
class GenericTableClient:
    def __init__(self, table_name: str,table_service_client:TableServiceClient):
        table_service_client.create_table_if_not_exists(table_name=table_name)
        self.table_client = table_service_client.get_table_client(table_name=table_name)
        

    async def add_entity(self, entity: Dict[str, Any]) -> None:
        try:
            self.table_client.create_entity(entity)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def get_entities(self, filter_expression: Optional[str] = None, select: Optional[str] = None) -> list:
        try:
            if filter_expression:
                entities = self.table_client.query_entities(query_filter=filter_expression,select=select)
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

    
    def delete_entity(self,entity: Dict[str, Any]) -> None:
        try:
            self.table_client.delete_entity(entity=entity)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    def batch_update_entities(self, entities: list) -> None:
        try:
            self.table_client.submit_transaction(entities)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    def batch_update_entities(self, entities: List[Dict[str, Any]]) -> None:
        if not entities:
            raise HTTPException(status_code=400, detail="No entities provided for batch update.")

        batch_operations = []
        try:
            for entity in entities:
                batch_operations.append(("update", entity, {"mode": UpdateMode.MERGE}))

            self.table_client.submit_transaction(batch_operations)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Batch update failed: {str(e)}")

