from azure.data.tables import TableServiceClient
from azure.core.exceptions import HttpResponseError
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from wrapperfunction.core import config
import uuid

class CosmosDBConnector:
    def __init__(self):
        """Initializing CosmosDB connection and Text Analytics client."""
        self.connection_string = config.CONNECTION_STRING
        self.table_service_client = TableServiceClient.from_connection_string(conn_str=self.connection_string)
        self.table_client = self.table_service_client.get_table_client(config.CONTAINER_NAME)
        
        # Here is the text analytics client initialization for sentiment analysis
        self.text_analytics_client = TextAnalyticsClient(
            endpoint=config.TEXT_ANALYTICS_ENDPOINT,
            credential=AzureKeyCredential(config.TEXT_ANALYTICS_KEY)
        )

    def get_chat_history_by_user_id(self, user_id: str):
        """
        Here we retrieve chat history for a specific user by their user_id (PartitionKey in Cosmos DB Table data).
        :param user_id: The ID of the user whose chat history is being queried.
        :return: A list of chat history entries or raises an exception in case of errors.
        """
        query_filter = f"PartitionKey eq '{user_id}'"
        try:
            chat_history = list(self.table_client.query_entities(filter=query_filter))
            return chat_history
        except HttpResponseError as cosmos_error:
            raise cosmos_error

    def analyze_sentiment(self, message: str):
        """
        Here we perform sentiment analysis on a given message using Azure Text Analytics API.
        :param message: The message for which sentiment needs to be analyzed.
        :return: Sentiment analysis result (positive, neutral, or negative).
        """
        try:
            response = self.text_analytics_client.analyze_sentiment(documents=[message])[0]
            return response.sentiment  # Returns 'positive', 'neutral', or 'negative'
        except Exception as error:
            raise Exception(f"Error analyzing sentiment: {str(error)}")

    def save_chat_history(self, chat_payload, results, feedback):
        """
        In this part we save chat history in Cosmos DB with additional columns for sentiment analysis and feedback.
        :param chat_payload: The data related to the chat, including user_id and stream_id.
        :param results: The chat results, including the message response.
        :param feedback: Feedback from the user or system for the chat.
        :return: None.
        """
        try:
            # Checking if stream_id is available or generate a unique identifier if None
            row_key = str(chat_payload.stream_id) if chat_payload.stream_id else f"conversation-{chat_payload.user_id}-{uuid.uuid4()}"

            # Performing sentiment analysis on the response message
            sentiment = self.analyze_sentiment(results['message']['content'])

            # Preparing the data for Cosmos DB
            chat_data = {
                "PartitionKey": chat_payload.user_id,  # user_id as PartitionKey
                "RowKey": row_key,  # stream_id or unique conversation key as RowKey
                "user_id": chat_payload.user_id,
                "stream_id": chat_payload.stream_id,  # None if no stream is opened
                "messages": chat_payload.messages,  # Chat history (messages)
                "response": results['message']['content'],  # Response message content
                "sentiment": sentiment,  # Sentiment analysis result
                "feedback": feedback  # User/system feedback
            }

            # Updating the entity in Cosmos DB
            self.table_client.upsert_entity(chat_data)
        
        except HttpResponseError as cosmos_error:
            raise HttpResponseError(f"Cosmos DB Table API error: {str(cosmos_error)}")

        except Exception as error:
            raise Exception(f"Error saving chat history: {str(error)}")
