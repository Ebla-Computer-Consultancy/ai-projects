import json
from openai import AzureOpenAI
from wrapperfunction.core import config


client = AzureOpenAI(
    azure_endpoint=config.OPENAI_ENDPOINT,
    api_key=config.OPENAI_API_KEY,
    api_version=config.OPENAI_API_VERSION
)

def assistant_chat_completion(user_message, chat_history, function_descriptions):
    chat_history.append({"role": "user", "content": user_message})
    
    completion = client.chat.completions.create(
        model=config.OPENAI_CHAT_MODEL,
        messages=chat_history,
        tools=function_descriptions,
        tool_choice="auto",
        temperature=0.01,
        top_p=0.01,
    )
    # compl_data = json.loads(completion.choices[0].json())
    # compl_data["usage"] = json.loads(completion.usage.json())
    return completion

def chat_completion(user_message, chat_history):
    chat_history.append({"role": "user", "content": user_message})
    
    completion = client.chat.completions.create(
        model=config.OPENAI_CHAT_MODEL,
        messages=chat_history,
        temperature=0.01,
        top_p=0.01,
    )
    # compl_data = json.loads(completion.choices[0].json())
    # compl_data["usage"] = json.loads(completion.usage.json())
    return completion