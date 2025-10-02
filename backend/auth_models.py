from pydantic import BaseModel, EmailStr
from typing import List, Dict, Optional
from datetime import datetime

# Existing Quiz Models (preserved)
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

# New Authentication Models
class UserBase(BaseModel):
    email: EmailStr
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None

class UserCreate(UserBase):
    password: Optional[str] = None
    google_id: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class GoogleAuthRequest(BaseModel):
    token: str

class User(UserBase):
    id: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: User

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None

# Enhanced Quiz Models with User Integration
class QuizAttempt(BaseModel):
    id: str
    user_id: Optional[str]
    score: int
    total_questions: int
    percentage: float
    time_taken: Optional[int]
    completed_at: datetime

class QuizResultWithUser(QuizResult):
    attempt_id: Optional[str] = None
    user_id: Optional[str] = None
    time_taken: Optional[int] = None

# Admin Models
class AdminQuestionCreate(BaseModel):
    question_text: str
    options: List[str]
    correct_option: int

class AdminQuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    options: Optional[List[str]] = None
    correct_option: Optional[int] = None

class AdminStats(BaseModel):
    total_users: int
    total_questions: int
    total_attempts: int
    average_score: float

class GeminiQuestionRequest(BaseModel):
    topic: str
    difficulty: str = "medium"  # easy, medium, hard
    count: int = 5