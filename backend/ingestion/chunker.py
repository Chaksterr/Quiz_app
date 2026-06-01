from chonkie import SemanticChunker


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 40) -> list[dict]:
    """Chunk text and preserve metadata."""
    chunker = SemanticChunker(
        max_chunk_size = chunk_size,
        similarity_threshold = 0.5,
    )
    chunks = chunker.chunk(text)
    
    # Return chunks with their start positions for page mapping
    result = []
    for c in chunks:
        if c.text.strip():
            result.append({
                "text": c.text,
                "start_index": c.start_index if hasattr(c, 'start_index') else 0,
            })
    
    return result
