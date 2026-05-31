import json
from models import Quiz
from generation.llm import chat

PROMPT = """\
You are a quiz generator. Use ONLY the context below.
Generate exactly {n} multiple choice questions.

Context:
{context}

Return ONLY a JSON object with this structure:
{{
  "doc_id": "{doc_id}",
  "topic":  "{topic}",
  "questions": [
    {{
      "question":       "...",
      "choices": [
        {{"label": "A", "text": "..."}},
        {{"label": "B", "text": "..."}},
        {{"label": "C", "text": "..."}},
        {{"label": "D", "text": "..."}}
      ],
      "correct_answer": "A",
      "explanation":    "Why this answer is correct in one sentence.",
      "source_text":    "The exact sentence from the context this is based on."
    }}
  ]
}}
"""


def generate_quiz(
    chunks: list[str],
    doc_id: str,
    topic:  str,
    n:      int = 5,
) -> Quiz:
    context = "\n\n---\n\n".join(chunks)
    prompt  = PROMPT.format(
        context = context,
        doc_id  = doc_id,
        topic   = topic,
        n       = n,
    )
    raw  = chat(prompt)
    data = json.loads(raw)
    return Quiz.model_validate(data)
