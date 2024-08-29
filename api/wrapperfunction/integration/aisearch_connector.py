import json
from wrapperfunction import integration
import wrapperfunction.core.config as config
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient


def search_query(
    search_index,
    search_text,
    filter_by=None,
    sort_order=None,
    page_size=1000000,
    page_number=1,
):
    try:
        # Create a search client
        azure_credential = AzureKeyCredential(config.SEARCH_KEY)
        search_client = SearchClient(
            config.SEARCH_ENDPOINT, search_index, azure_credential
        )

        jsonResult = []
        results = search_client.search(
            search_text=search_text,
            vector_queries=[
                {
                    "kind": "vector",
                    "vector": integration.openaiconnector.generate_embeddings(
                        search_text
                    ),
                    "fields": "text_vector",
                    # "k": 10,
                }
            ],
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
