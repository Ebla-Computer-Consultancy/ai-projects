class CustomSettings:
    def __init__(self, temperature=None):  # Set default temperature to 0.5
        self.temperature = temperature if temperature is not None else 0.5

# Class for individual chatbot information
class ChatbotSetting:
    def __init__(self, name, index_name, custom_settings=None):  # Default to None
        self.name = name
        self.index_name = index_name
        # If custom_settings is not provided, use the default CustomSettings
        self.custom_settings = custom_settings if custom_settings is not None else CustomSettings()
