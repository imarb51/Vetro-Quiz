from pydantic import BaseModel
from typing import List, Dict, Optional

class Question(BaseModel):
    id: int
    question_text: str
    options: List[str]

class QuestionWithAnswer(BaseModel):
    id: int
    question_text: str
    options: List[str]
    correct_option: int
    user_answer: Optional[int] = None
    is_correct: Optional[bool] = None

class UserAnswers(BaseModel):
    answers: Dict[int, int]  # question_id -> selected_option_index

class QuizResult(BaseModel):
    score: int
    total_questions: int
    percentage: float
    results: List[QuestionWithAnswer]