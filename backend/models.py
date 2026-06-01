from pydantic import BaseModel
from typing import List


class AnswerChoice(BaseModel):
    label: str
    text:  str


class QuizQuestion(BaseModel):
    question:       str
    choices:        List[AnswerChoice]
    correct_answer: str
    explanation:    str
    source_text:    str
    page_number:    int = 0  # Page or slide number


class Quiz(BaseModel):
    doc_id:    str
    topic:     str
    questions: List[QuizQuestion]
    filename:  str = ""  # Store filename for reference


class IngestResponse(BaseModel):
    doc_id:      str
    filename:    str
    chunk_count: int


class QuizRequest(BaseModel):
    doc_id: str
    topic:  str
    n:      int = 5


class SubmitAnswers(BaseModel):
    quiz:    Quiz
    answers: dict


class QuestionResult(BaseModel):
    question:       str
    your_answer:    str
    correct_answer: str
    was_correct:    bool
    explanation:    str
    source_text:    str
    page_number:    int = 0


class ScoreResult(BaseModel):
    total:         int
    correct:       int
    score_percent: float
    breakdown:     List[QuestionResult]


class SummarizeRequest(BaseModel):
    doc_id: str
    quiz:   Quiz
    result: ScoreResult


class QuizSummary(BaseModel):
    overall_performance: str
    strengths:           List[str]
    weaknesses:          List[str]
    key_concepts:        List[dict]  # {"concept": str, "pages": List[int], "mastery": str}
    recommendations:     List[str]
    study_plan:          str
