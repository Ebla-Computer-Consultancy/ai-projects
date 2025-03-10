class CategorizationSettings:
    def __init__(self, categorize=None, categorize_field=None):
        self.categorize = categorize if categorize is not None else None
        self.categorize_field = categorize_field if categorize_field is not None else None

class CustomSettings:
    def __init__(self, temperature=None, tools=None, max_tokens=None, top_p=None, max_history_length=None,display_in_chat=True):
        self.temperature = temperature if temperature is not None else 0.5
        self.tools = tools if tools is not None else None
        self.max_tokens = max_tokens if max_tokens is not None else 800
        self.top_p = top_p if top_p is not None else 0.95
        self.max_history_length = max_history_length if max_history_length is not None else 9
        self.display_in_chat = display_in_chat


# Class for individual chatbot information
class ChatbotSetting:
    def __init__(
        self, name, index_name, system_message,enable_history,apply_sentiment ,preserve_first_message,examples=[], custom_settings=None,categorization_settings=None
    ):  # Default to None
        self.name = name
        self.index_name = index_name
        # If custom_settings is not provided, use the default CustomSettings

        self.custom_settings = (
            custom_settings if custom_settings is not None else CustomSettings()
        )
        self.system_message = system_message
        self.examples = examples
        self.enable_history = enable_history,
        self.apply_sentiment = apply_sentiment
        self.preserve_first_message = preserve_first_message
        self.categorization_settings = categorization_settings if categorization_settings is not None else CategorizationSettings()





