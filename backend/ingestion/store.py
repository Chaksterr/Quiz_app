import uuid
from qdrant_client.models import PointStruct, VectorParams, Distance
from clients import azure_client, qdrant_client
from config  import settings


def _ensure_collection(vector_size: int):
    names = [c.name for c in qdrant_client.get_collections().collections]
    if settings.collection_name not in names:
        qdrant_client.create_collection(
            collection_name = settings.collection_name,
            vectors_config  = VectorParams(
                size     = vector_size,
                distance = Distance.COSINE,
            ),
        )


def embed_texts(texts: list[str]) -> list[list[float]]:
    response = azure_client.embeddings.create(
        input = texts,
        model = settings.azure_openai_embed_model,
    )
    return [item.embedding for item in response.data]


def store_chunks(chunks: list[str], filename: str) -> dict:
    if not chunks:
        return {"doc_id": "", "chunk_count": 0}

    vectors = []
    for i in range(0, len(chunks), 100):
        batch = chunks[i:i + 100]
        vectors.extend(embed_texts(batch))

    _ensure_collection(vector_size=len(vectors[0]))

    doc_id = str(uuid.uuid4())
    points = [
        PointStruct(
            id      = str(uuid.uuid4()),
            vector  = vectors[i],
            payload = {
                "text":     chunks[i],
                "doc_id":   doc_id,
                "filename": filename,
            },
        )
        for i in range(len(chunks))
    ]

    for i in range(0, len(points), 100):
        qdrant_client.upsert(
            collection_name = settings.collection_name,
            points          = points[i:i + 100],
        )

    return {"doc_id": doc_id, "chunk_count": len(points)}
