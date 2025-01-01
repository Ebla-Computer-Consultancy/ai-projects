import json
import wrapperfunction.core.config as config
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexerClient
from wrapperfunction.search.model.indexer_model import IndexInfo

def get_search_client(search_index: str):
    # Create a search client
    azure_credential = AzureKeyCredential(config.SEARCH_KEY)
    return SearchClient(
        config.SEARCH_ENDPOINT, search_index, azure_credential
    )
def get_search_indexer_client():
    # Create a search client
    return SearchIndexerClient(endpoint=config.SEARCH_ENDPOINT, credential=AzureKeyCredential(config.SEARCH_KEY))  

def search_query(
    search_index,
    search_text,
    filter_by=None,
    sort_order=None,
    page_size=1000000,
    page_number=1,
):
    try:
        search_client = get_search_client(search_index)
        jsonResult = []
        results = search_client.search(
            search_text=search_text,
            vector_queries=[
                {
                    "kind": "text",
                    "text":search_text,
                    "fields": "text_vector",
                    # "k": 10,
                }
            ],
            query_type="semantic",
            semantic_configuration_name=search_index+"-semantic-configuration",
            include_total_count=True,
            # highlight_fields="chunk",
            top=page_size,
            skip=(page_number - 1) * page_size,
        )
        for result in results:
            jsonResult.append(json.loads(json.dumps(dict(result))))
        return {
            "total_count": results.get_count(),
            "count": len(jsonResult),
            "page_number": page_number,
            "rs": jsonResult,
        }

    except Exception as error:
        return json.dumps({"error": True, "message": str(error)})


def delete_indexed_data(index_name:str, key:str, value=None):
    # Create a search client
    client = get_search_client(index_name)
    # Search for all documents and retrieve their keys
    if value  is not None:
        filter_query = f"{key} eq '{value}'"
        results = client.search(search_text="*",filter=filter_query, select=["chunk_id"])
    else:
        results = client.search(search_text="*", select=["chunk_id"])
    document_keys = [doc["chunk_id"] for doc in results]
    # Delete documents by their values
    for value_ in document_keys:
        client.delete_documents(documents=[{"chunk_id": value_}])

def reset_indexed_data(index_name:str):
    # Create a search client
    client = get_search_client(index_name)
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
    search_indexer_client = get_search_indexer_client()
    # Get indexer details
    indexers = search_indexer_client.get_indexers()
    indexer_details = next((indexer for indexer in indexers if indexer.target_index_name == index_name), None)
    indexer_name= indexer_details.name
    reset_indexed_data(index_name)
    search_indexer_client.reset_indexer(indexer_name)
    search_indexer_client.run_indexer(indexer_name)

def get_index_info(index_name:str):
    # Create a search index client
    search_indexer_client = get_search_indexer_client()  
    
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