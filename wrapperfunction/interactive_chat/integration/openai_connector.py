import json
from openai import AzureOpenAI
from wrapperfunction.core import config


client = AzureOpenAI(
    azure_endpoint="https://assisasimopenai.openai.azure.com/",
    api_key="ffe733f851f84c808e0d15bc008c8c34",
    api_version="2024-05-01-preview"
)

def assistant_chat_completion(user_message, chat_history, function_descriptions):
    chat_history.append({"role": "user", "content": user_message})
    
    completion = client.chat.completions.create(
        model="gpt-35-turbo-3",
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
        model="gpt-35-turbo-3",
        messages=chat_history,
        temperature=0.01,
        top_p=0.01,
    )
    # compl_data = json.loads(completion.choices[0].json())
    # compl_data["usage"] = json.loads(completion.usage.json())
    return completion