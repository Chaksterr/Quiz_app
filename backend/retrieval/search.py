from qdrant_client.models import Filter, FieldCondition, MatchValue
from clients import azure_client, qdrant_client
from config  import settings


def search_chunks(topic: str, doc_id: str, top_k: int = 6) -> list[dict]:
    """Search chunks and return with page numbers and filename."""
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

    return [
        {
            "text": r.payload["text"],
            "page_num": r.payload.get("page_num", 0),
            "doc_type": r.payload.get("doc_type", "PDF"),
            "filename": r.payload.get("filename", ""),
        }
        for r in results
    ]
