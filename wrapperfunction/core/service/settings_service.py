import uuid
import azure.cosmos.cosmos_client as cosmos_client
from fastapi import HTTPException
from wrapperfunction.core import config

def get_settings_db_client():
    client = cosmos_client.CosmosClient(config.SETTINGS_ACCOUNT_HOST, {'masterKey': config.SETTINGS_ACCOUNT_KEY}, user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
    db = client.get_database_client(config.SETTINGS_COSMOS_DATABASE)
    return db.get_container_client(config.SETTINGS_COSMOS_CONTAINER)

def create_item(data: dict):
    try:
        container = get_settings_db_client()
        data["id"] = str(uuid.uuid4())
        data["settingsPK"] = str(uuid.uuid4()) 
        response = container.create_item(body=data)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error While Creating Item: {str(e)}")

def read_item(entity_name: str):
    try:
        container = get_settings_db_client()
        items =  list(container.query_items(query=f"SELECT * FROM c WHERE c.entity_name = '{entity_name}'",enable_cross_partition_query=True))
        if items[0]:
            return items[0]
        else:
            raise ModuleNotFoundError
    except ModuleNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Error while reading Item: '{entity_name}' Item Not Found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while reading Item: {str(e)}")
        
def read_items():
    try:
        container = get_settings_db_client()
        item_list = list(container.read_all_items())
        return item_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while reading Items: {str(e)}")

def update_item(entity_name: str, filed: str, value):
    try:
        container = get_settings_db_client()
        item = read_item(entity_name= entity_name)
        item[f'{filed}'] = value
        response = list(container.replace_item(item=item, body=item))
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while Updating Item: {str(e)}")

def delete_item(entity_name: str):
    try:
        container = get_settings_db_client()
        item = read_item(entity_name)
        response = container.delete_item(item=item,partition_key=item["settingsPK"])
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while Deleting Item: {str(e)}")