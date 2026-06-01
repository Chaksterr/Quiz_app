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


def store_chunks(chunks: list[dict], filename: str, page_map: dict = None) -> dict:
    """Store chunks with page number metadata."""
    if not chunks:
        return {"doc_id": "", "chunk_count": 0}

    # Extract text from chunk dicts
    chunk_texts = [c["text"] if isinstance(c, dict) else c for c in chunks]
    
    vectors = []
    for i in range(0, len(chunk_texts), 100):
        batch = chunk_texts[i:i + 100]
        vectors.extend(embed_texts(batch))

    _ensure_collection(vector_size=len(vectors[0]))

    doc_id = str(uuid.uuid4())
    
    # Determine page number for each chunk
    is_pdf = filename.lower().endswith(".pdf")
    doc_type = "PDF" if is_pdf else "PPTX"
    
    points = []
    for i in range(len(chunk_texts)):
        # Estimate page/slide number based on chunk position
        page_num = (i // 2) + 1 if page_map is None else page_map.get(i, i + 1)
        
        points.append(PointStruct(
            id      = str(uuid.uuid4()),
            vector  = vectors[i],
            payload = {
                "text":      chunk_texts[i],
                "doc_id":    doc_id,
                "filename":  filename,
                "page_num":  page_num,
                "doc_type":  doc_type,
            },
        ))

    for i in range(0, len(points), 100):
        qdrant_client.upsert(
            collection_name = settings.collection_name,
            points          = points[i:i + 100],
        )

    return {"doc_id": doc_id, "chunk_count": len(points)}
