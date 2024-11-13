import json
import wrapperfunction.core.config as config
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

def delete_indexed_data(index_name:str, key:str, value=None):
    # Create a search client
    AI_SEARCH_KEY= config.SEARCH_KEY # 
    AI_SEARCH_ENDPOINT = config.SEARCH_ENDPOINT #
    client = SearchClient(endpoint=AI_SEARCH_ENDPOINT, index_name=index_name, credential=AzureKeyCredential(AI_SEARCH_KEY)) 
    # Search for all documents and retrieve their keys
    if value  is not None:
        filter_query = f"{key} eq '{value}'"
        print(filter_query)
        results = client.search(search_text="*",filter=filter_query, select=["chunk_id"])
    else:
        results = client.search(search_text="*", select=["chunk_id"])
    document_keys = [doc["chunk_id"] for doc in results]
    # Delete documents by their values
    for value_ in document_keys:
        client.delete_documents(documents=[{"chunk_id": value_}])