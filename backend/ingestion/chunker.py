from chonkie import SemanticChunker


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 40) -> list[str]:
    chunker = SemanticChunker(
        max_chunk_size = chunk_size,
        similarity_threshold = 0.5,
    )
    chunks = chunker.chunk(text)
    return [c.text for c in chunks if c.text.strip()]
