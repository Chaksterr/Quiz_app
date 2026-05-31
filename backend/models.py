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


class Quiz(BaseModel):
    doc_id:    str
    topic:     str
    questions: List[QuizQuestion]


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


class ScoreResult(BaseModel):
    total:         int
    correct:       int
    score_percent: float
    breakdown:     List[QuestionResult]
