import os
import tempfile

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import (
    IngestResponse, QuizRequest, Quiz,
    SubmitAnswers, ScoreResult, QuestionResult,
    SummarizeRequest, QuizSummary,
)
from ingestion.parser  import parse_file
from ingestion.chunker import chunk_text
from ingestion.store   import store_chunks
from retrieval.search  import search_chunks
from generation.quiz   import generate_quiz, generate_summary

app = FastAPI(title="Quiz Generator", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins  = ["*"],
    allow_methods  = ["*"],
    allow_headers  = ["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile = File(...)):
    name = file.filename
    if not name.endswith((".pdf", ".pptx")):
        raise HTTPException(400, "Only PDF and PPTX supported")

    suffix = ".pdf" if name.endswith(".pdf") else ".pptx"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        raw_text, page_map = parse_file(tmp_path, name)
        
        if not raw_text or len(raw_text.strip()) < 50:
            raise HTTPException(400, "Document has insufficient text content. It might be scanned or image-based.")
        
        chunks = chunk_text(raw_text)
        
        if not chunks:
            raise HTTPException(400, "Failed to create chunks from document")
        
        result = store_chunks(chunks, name, page_map)
        
        if result["chunk_count"] == 0:
            raise HTTPException(400, "No content could be stored from document")
        
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Internal error processing document: {str(e)}")
    finally:
        os.unlink(tmp_path)

    return IngestResponse(
        doc_id      = result["doc_id"],
        filename    = name,
        chunk_count = result["chunk_count"],
    )


@app.post("/quiz", response_model=Quiz)
def quiz(req: QuizRequest):
    chunks = search_chunks(req.topic, req.doc_id)
    if not chunks:
        raise HTTPException(404, "No content found for this document")
    
    # Get filename from first chunk
    filename = chunks[0].get("filename", "") if chunks else ""
    quiz_result = generate_quiz(chunks, req.doc_id, req.topic, req.n)
    
    # Add filename to quiz
    quiz_dict = quiz_result.model_dump()
    quiz_dict["filename"] = filename
    
    return Quiz.model_validate(quiz_dict)


@app.post("/score", response_model=ScoreResult)
def score(payload: SubmitAnswers):
    correct   = 0
    breakdown = []

    for i, q in enumerate(payload.quiz.questions):
        user_ans   = payload.answers.get(str(i), "")
        is_correct = user_ans == q.correct_answer
        if is_correct:
            correct += 1
        breakdown.append(QuestionResult(
            question       = q.question,
            your_answer    = user_ans,
            correct_answer = q.correct_answer,
            was_correct    = is_correct,
            explanation    = q.explanation,
            source_text    = q.source_text,
            page_number    = q.page_number,
        ))

    total = len(payload.quiz.questions)
    return ScoreResult(
        total         = total,
        correct       = correct,
        score_percent = round(correct / total * 100, 1),
        breakdown     = breakdown,
    )



@app.post("/summarize", response_model=QuizSummary)
def summarize(req: SummarizeRequest):
    """Generate detailed performance summary with study recommendations."""
    chunks = search_chunks(req.quiz.topic, req.doc_id, top_k=10)
    if not chunks:
        raise HTTPException(404, "No content found for this document")
    return generate_summary(chunks, req.quiz, req.result)
