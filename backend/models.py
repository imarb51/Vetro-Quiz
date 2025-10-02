from pydantic import BaseModel, EmailStr
from typing import List, Dict, Optional
from datetime import datetime

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

# Admin models
class AdminLogin(BaseModel):
    username: str
    password: str

class AdminUser(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: bool
    created_at: str
    total_attempts: int
    average_score: float

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class QuestionCreate(BaseModel):
    question_text: str
    options: List[str]
    correct_option: int

class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    options: Optional[List[str]] = None
    correct_option: Optional[int] = None