from clients import azure_client
from config  import settings


def chat(prompt: str) -> str:
    response = azure_client.chat.completions.create(
        model           = settings.azure_openai_chat_model,
        messages        = [{"role": "user", "content": prompt}],
        response_format = {"type": "json_object"},
    )
    return response.choices[0].message.content
