
class CustomSettings:

    def __init__(self, temperature=None, tools=None, max_tokens=None, top_p=None, max_history_length=None,display_in_chat=True,filter_exp=None,categorize=None,categorize_field=None):

        self.temperature = temperature if temperature is not None else 0.5
        self.tools = tools if tools is not None else None
        self.max_tokens = max_tokens if max_tokens is not None else 800
        self.top_p = top_p if top_p is not None else 0.95
        self.max_history_length = max_history_length if max_history_length is not None else 9
        self.display_in_chat = display_in_chat #to make chatbotname display in chat
        self.categorize = categorize if categorize is not None else None #to apply categorization in query
        self.categorize_field = categorize_field if categorize_field is not None else None 
        self.filter_exp = filter_exp if filter_exp else None #Filter expression to ai search


# Class for individual chatbot information
class ChatbotSetting:
    def __init__(

        self, name, index_name, system_message,enable_history,apply_sentiment, greeting_message,preserve_first_message,examples=[], custom_settings=None

    ):  # Default to None
        self.name = name
        self.index_name = index_name
        # If custom_settings is not provided, use the default CustomSettings

        self.custom_settings = (
            custom_settings if custom_settings is not None else CustomSettings()
        )
        self.system_message = system_message
        self.examples = examples
        self.enable_history = enable_history,#to enable chat history for this chatbot
        self.apply_sentiment = apply_sentiment #Applying sentiment analysis for this chatbot
        self.preserve_first_message = preserve_first_message #to make sure the first message is not removed from chat history to avoid context loss
        self.greeting_message = greeting_message




