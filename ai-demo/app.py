import os
import openai
from openai import AzureOpenAI
from flask import Flask, request, render_template, redirect, url_for,jsonify,json
from dotenv import load_dotenv

# Import search namespaces
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorQuery

app = Flask(__name__)


# Azure Search constants
load_dotenv()
search_endpoint = os.getenv('SEARCH_SERVICE_ENDPOINT')
search_key = os.getenv('SEARCH_SERVICE_QUERY_KEY')
search_index = os.getenv('SEARCH_INDEX_NAME')
openai_api_type=os.getenv('OPENAI_API_TYPE')
openai_endpoint=os.getenv('OPENAI_ENDPOINT')
openai_api_version=os.getenv('OPENAI_API_VERSION')
openai_api_key=os.getenv('OPENAI_API_KEY')
openai_chat_model=os.getenv('OPENAI_CHAT_MODEL')
openai_emb_model=os.getenv('OPENAI_EMB_MODEL')
# Wrapper function for request to search index
def search_query(search_text, filter_by=None, sort_order=None):
    try:

        # Create a search client
        azure_credential = AzureKeyCredential(search_key)
        search_client = SearchClient(search_endpoint, search_index, azure_credential)
        

        # Submit search query
        """ results =  search_client.search(search_text,
                                        search_mode="all",
                                        include_total_count=True,
                                        filter=filter_by,
                                        order_by=sort_order,
                                        facets=['metadata_author'],
                                        highlight_fields='merged_content-3,imageCaption-3',
                                        select = "url,metadata_storage_name,metadata_author,metadata_storage_size,metadata_storage_last_modified,language,sentiment,merged_content,keyphrases,locations,imageTags,imageCaption")
         """
       

        results = search_client.search(
            search_text=search_text,
            vector_queries=[{
      "kind": "vector",
      "vector": generate_embeddings(search_text,openai_emb_model),
      "fields": "text_vector",
    #   "fields": "contentVector",
      "k": 10
    }],
            query_type="semantic",
            semantic_configuration_name=search_index+"-semantic-configuration",
            include_total_count=True,
        )
        return results
        
    except Exception as ex:
        raise ex
    
@app.route("/")
def home():
    return render_template("index.html")

# Seach Home page route
@app.route("/search")
def searchhome():
    return render_template("default.html")

# Search results route
@app.route("/search-action", methods=['GET'])
def search():
    try:

        # Get the search terms from the request form
        search_text = request.args["search"]

        # If a facet is selected, use it in a filter
        filter_expression = None
        if 'facet' in request.args:
            filter_expression = "metadata_author eq '{0}'".format(request.args["facet"])

        # If a sort field is specified, modify the search expression accordingly
        sort_expression = 'search.score()'
        sort_field = 'relevance' #default sort is search.score(), which is relevance
        if 'sort' in request.args:
            sort_field = request.args["sort"]
            if sort_field == 'file_name':
                sort_expression = 'metadata_storage_name asc'
            elif sort_field == 'size':
                sort_expression = 'metadata_storage_size desc'
            elif sort_field == 'date':
                sort_expression = 'metadata_storage_last_modified desc'
            elif sort_field == 'sentiment':
                sort_expression = 'sentiment desc'

        # submit the query and get the results
        results = search_query(search_text, filter_expression, sort_expression)

        # render the results
        return render_template("search.html", search_results=results, search_terms=search_text)

    except Exception as error:
        return render_template("error.html", error_message=error)

openai.api_type = openai_api_type

client = AzureOpenAI(
  azure_endpoint =openai_endpoint,
  api_key = openai_api_key,
  api_version = openai_api_version
)



@app.route('/chat')
def chathome():
    return render_template('chat.html')

@app.route('/chat-action', methods=['POST'])
def chat():
    try:
        chat_history_arr=request.json['messageHistory']
        chat_history = []
        for item in chat_history_arr:
            chat_history.append(json.loads(item))
        # Get response from OpenAI ChatGPT
        completion = client.chat.completions.create(
            model=openai_chat_model,
            messages= chat_history, 
            max_tokens=800,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            stream=False,
            extra_body={
            "data_sources": [{
                "type": "azure_search",
                "parameters": {
                    "endpoint": search_endpoint,
                    "index_name": search_index,
                    "semantic_configuration": search_index+"-semantic-configuration",
                    "query_type": "vector_semantic_hybrid",
                    "fields_mapping": {
                    "content_fields_separator": "\n",
                    "content_fields": [
                        "chunk"
                    ],
                    "filepath_field": "title",
                    "title_field": "chunk_id",
                    "url_field": "metadata_storage_path",
                    "vector_fields": [
                        "text_vector"
                    ]
                    },
                    "in_scope": True,
                    "role_information": "You are an AI assistant that helps people find information using the defined datasource. always reply in the same question language. and give long and desciptive answers",
                    "filter": None,
                    "strictness": 3,
                    "top_n_documents": 5,
                    "authentication": {
                    "type": "api_key",
                    "key": search_key
                    },
                    "embedding_dependency": {
                    "type": "deployment_name",
                    "deployment_name": "TestEmbElbar"
                    }
                }
                }]
            }
        )
        
        return completion.choices[0].json()
    except Exception as error:
        print(error)
        return json.dumps({'error':True,'message':str(error)})

def generate_embeddings(text, model): # model = "deployment_name"
    return client.embeddings.create(input = [text], model=model).data[0].embedding

if __name__ == "__main__":
  app.run(debug=True)