import json
from models import Quiz, QuizSummary, ScoreResult
from generation.llm import chat

PROMPT = """\
You are a quiz generator. Use ONLY the context below.
Generate exactly {n} multiple choice questions.

Context:
{context}

IMPORTANT: Do NOT include page numbers in the questions themselves.
Page numbers will be added automatically later.

Return ONLY a JSON object with this structure:
{{
  "doc_id": "{doc_id}",
  "topic":  "{topic}",
  "questions": [
    {{
      "question":       "What is the main concept?",
      "choices": [
        {{"label": "A", "text": "First option"}},
        {{"label": "B", "text": "Second option"}},
        {{"label": "C", "text": "Third option"}},
        {{"label": "D", "text": "Fourth option"}}
      ],
      "correct_answer": "A",
      "explanation":    "Why this answer is correct in one sentence.",
      "source_text":    "The exact sentence from the context this is based on.",
      "page_number":    1
    }}
  ]
}}

Note: The page_number field is for reference only and will be used in the answer explanations.
"""


def generate_quiz(
    chunks: list[dict],
    doc_id: str,
    topic:  str,
    n:      int = 5,
) -> Quiz:
    # Build context WITHOUT page numbers in the main text
    # Page numbers are tracked separately
    context_parts = []
    for chunk in chunks:
        # Don't include page reference in the context text
        # This prevents AI from mentioning pages in questions
        context_parts.append(chunk['text'])
    
    context = "\n\n---\n\n".join(context_parts)
    prompt  = PROMPT.format(
        context = context,
        doc_id  = doc_id,
        topic   = topic,
        n       = n,
    )
    raw  = chat(prompt)
    data = json.loads(raw)
    return Quiz.model_validate(data)



SUMMARIZE_PROMPT = """\
You are an educational AI assistant analyzing a student's quiz performance.

Quiz Topic: {topic}
Score: {correct}/{total} ({percent}%)

Questions and Performance:
{breakdown}

Document Context:
{context}

Analyze the student's performance and provide:
1. Overall performance assessment
2. Strengths (concepts they mastered)
3. Weaknesses (concepts needing improvement)
4. Key concepts with page references and mastery level
5. Personalized recommendations
6. A study plan for improvement

Return ONLY a JSON object with this structure:
{{
  "overall_performance": "Detailed assessment of their performance...",
  "strengths": ["Concept 1 they understood well", "Concept 2..."],
  "weaknesses": ["Concept 1 they struggled with", "Concept 2..."],
  "key_concepts": [
    {{
      "concept": "Concept name",
      "pages": [1, 3, 5],
      "mastery": "excellent|good|needs_work"
    }}
  ],
  "recommendations": ["Specific action 1", "Specific action 2"],
  "study_plan": "Detailed study plan with priorities..."
}}
"""


def generate_summary(
    chunks: list[dict],
    quiz: Quiz,
    result: ScoreResult,
) -> QuizSummary:
    """Generate detailed performance summary with page references."""
    
    # Build breakdown text
    breakdown_text = []
    for i, item in enumerate(result.breakdown):
        status = "✓ CORRECT" if item.was_correct else "✗ INCORRECT"
        page_ref = f"Page {item.page_number}" if item.page_number > 0 else "Document"
        breakdown_text.append(
            f"Q{i+1}: {item.question}\n"
            f"  Status: {status}\n"
            f"  Student answer: {item.your_answer}\n"
            f"  Correct answer: {item.correct_answer}\n"
            f"  Source ({page_ref}): {item.source_text[:200]}..."
        )
    
    # Build context with page numbers
    context_parts = []
    for chunk in chunks:
        page_ref = f"[Page {chunk['page_num']}]" if chunk['doc_type'] == 'PDF' else f"[Slide {chunk['page_num']}]"
        context_parts.append(f"{page_ref}\n{chunk['text']}")
    
    context = "\n\n---\n\n".join(context_parts)
    prompt = SUMMARIZE_PROMPT.format(
        topic     = quiz.topic,
        correct   = result.correct,
        total     = result.total,
        percent   = result.score_percent,
        breakdown = "\n\n".join(breakdown_text),
        context   = context[:8000],  # Limit context size
    )
    
    raw  = chat(prompt)
    data = json.loads(raw)
    return QuizSummary.model_validate(data)
