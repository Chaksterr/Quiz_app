from openai import AzureOpenAI
from qdrant_client import QdrantClient
from config import settings

azure_client = AzureOpenAI(
    azure_endpoint = settings.azure_openai_endpoint,
    api_key        = settings.azure_openai_api_key,
    api_version    = settings.azure_openai_api_version,
)

qdrant_client = QdrantClient(
    host = settings.qdrant_host,
    port = settings.qdrant_port,
)
