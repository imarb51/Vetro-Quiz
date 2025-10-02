from pydantic import BaseModel, validator, EmailStr
from fastapi import HTTPException, status
from typing import Optional
from security_middleware import security

class SecureUserCreate(BaseModel):
    """Secure user creation with validation."""
    email: EmailStr
    name: str
    password: Optional[str] = None
    google_id: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError('Name is required')
        if len(v) > 100:
            raise ValueError('Name too long')
        return security.sanitize_string(v, 100)
    
    @validator('password')
    def validate_password(cls, v):
        if v is not None:
            if not security.validate_password(v):
                raise ValueError('Password must be at least 6 characters long')
            if len(v) > 72:  # bcrypt limit
                raise ValueError('Password too long (max 72 characters)')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if v is not None:
            if len(v) > 20:
                raise ValueError('Phone number too long')
            return security.sanitize_string(v, 20)
        return v
    
    @validator('address')
    def validate_address(cls, v):
        if v is not None:
            if len(v) > 500:
                raise ValueError('Address too long')
            return security.sanitize_string(v, 500)
        return v

class SecureUserLogin(BaseModel):
    """Secure login with validation."""
    email: EmailStr
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError('Password is required')
        if len(v) > 72:  # bcrypt limit
            raise ValueError('Password too long')
        return v

class SecureQuestionCreate(BaseModel):
    """Secure question creation for admin."""
    question_text: str
    options: list
    correct_option: int
    
    @validator('question_text')
    def validate_question(cls, v):
        if not v or len(v.strip()) < 5:
            raise ValueError('Question must be at least 5 characters')
        if len(v) > 1000:
            raise ValueError('Question too long')
        return security.sanitize_string(v, 1000)
    
    @validator('options')
    def validate_options(cls, v):
        if not v or len(v) < 2:
            raise ValueError('At least 2 options required')
        if len(v) > 6:
            raise ValueError('Maximum 6 options allowed')
        
        sanitized_options = []
        for option in v:
            if not isinstance(option, str):
                raise ValueError('Options must be strings')
            if len(option) > 200:
                raise ValueError('Option too long')
            sanitized_options.append(security.sanitize_string(option, 200))
        
        return sanitized_options
    
    @validator('correct_option')
    def validate_correct_option(cls, v, values):
        if 'options' in values and values['options']:
            if v < 0 or v >= len(values['options']):
                raise ValueError('Invalid correct option index')
        return v

def validate_user_input(data: dict, model_class) -> dict:
    """Validate user input using Pydantic models."""
    try:
        validated_data = model_class(**data)
        return validated_data.dict()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(e)}"
        )

# Admin Dashboard Models
class AdminStats(BaseModel):
    total_users: int
    total_questions: int
    total_attempts: int
    average_score: float

class User(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool = False
    is_active: bool = True