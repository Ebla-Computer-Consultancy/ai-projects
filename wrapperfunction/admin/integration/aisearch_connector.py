import json
import wrapperfunction.core.config as config
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from wrapperfunction.admin.model.indexer_model import IndexInfo

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


def reset_indexed_data(index_name:str):
    # Create a search client
    AI_SEARCH_KEY= config.SEARCH_KEY
    AI_SEARCH_ENDPOINT = config.SEARCH_ENDPOINT
    client = SearchClient(endpoint=AI_SEARCH_ENDPOINT, index_name=index_name, credential=AzureKeyCredential(AI_SEARCH_KEY)) 
    # Search for all documents and retrieve their keys
    # Retrieve all documents' keys
    results = client.search(search_text="*", select=["chunk_id"])
    document_keys = [doc["chunk_id"] for doc in results]    
    # Create a batch delete request
    batch = [{"@search.action": "delete", "chunk_id": key} for key in document_keys]
    
    # Delete all documents in the index
    client.upload_documents(documents=batch)

def run_indexer(index_name:str):
    # Create a search client
    AI_SEARCH_KEY= config.SEARCH_KEY
    AI_SEARCH_ENDPOINT = config.SEARCH_ENDPOINT
    search_indexer_client = SearchIndexerClient(endpoint=AI_SEARCH_ENDPOINT,credential=AzureKeyCredential(AI_SEARCH_KEY))
    # Get indexer details
    indexers = search_indexer_client.get_indexers()
    indexer_details = next((indexer for indexer in indexers if indexer.target_index_name == index_name), None)
    indexer_name= indexer_details.name
    reset_indexed_data(index_name)
    print(f"reset {index_name} done")
    search_indexer_client.reset_indexer(indexer_name)
    print(f"reset {indexer_name} done")
    search_indexer_client.run_indexer(indexer_name)
    print(f"runing {indexer_name} done")


def get_index_info(index_name:str):
    # Create a search index client
    AI_SEARCH_KEY= config.SEARCH_KEY
    AI_SEARCH_ENDPOINT = config.SEARCH_ENDPOINT
    search_indexer_client = SearchIndexerClient(endpoint=AI_SEARCH_ENDPOINT, credential=AzureKeyCredential(AI_SEARCH_KEY))  
    
    # Get indexer details
    indexers = search_indexer_client.get_indexers()
    indexer_details = next((indexer for indexer in indexers if indexer.target_index_name == index_name), None)
    
    # Get data source details
    data_source = search_indexer_client.get_data_source_connection(indexer_details.data_source_name)
    data_source_name = data_source.name
    data_source_type = data_source.type
    data_storage_name = data_source.container.name
    
    # Get skillset name
    skillset_name = indexer_details.skillset_name if indexer_details else None
    return IndexInfo(
            # index_details=index_details.as_dict(),
            index_name=index_name,
            indexer_name=indexer_details.name,
            data_source_name=data_source_name,
            data_storage_type=data_source_type,
            data_storage_name =data_storage_name,
            skillset_name=skillset_name
        )