from qdrant_client.models import Filter, FieldCondition, MatchValue
from clients import azure_client, qdrant_client
from config  import settings


def search_chunks(topic: str, doc_id: str, top_k: int = 6) -> list[str]:
    response = azure_client.embeddings.create(
        input = [topic],
        model = settings.azure_openai_embed_model,
    )
    query_vector = response.data[0].embedding

    results = qdrant_client.search(
        collection_name = settings.collection_name,
        query_vector    = query_vector,
        query_filter    = Filter(
            must=[
                FieldCondition(
                    key   = "doc_id",
                    match = MatchValue(value=doc_id),
                )
            ]
        ),
        limit           = top_k,
        with_payload    = True,
    )

    return [r.payload["text"] for r in results]
