from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
import os
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
import logging

# Import models
from models import Question, UserAnswers, QuizResult, QuestionWithAnswer
from auth_models import (
    User, UserCreate, UserLogin, Token, QuizResultWithUser,
    GoogleAuthRequest, AdminStats
)
from auth_utils import verify_password, get_password_hash, generate_tokens
from auth_dependencies import get_optional_user, get_current_active_user, get_current_admin_user
from database import (
    get_user_by_email, get_user_by_id, create_user, save_quiz_attempt
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Quiz API with Authentication", 
    description="Enhanced API for online quiz application with user management",
    version="2.0.0"
)

# Add Security Middleware
from security_middleware import security_middleware
app.middleware("http")(security_middleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        os.getenv("FRONTEND_URL", "http://localhost:3000")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    """Get database connection."""
    db_path = Path(__file__).parent / "quiz.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
async def root():
    return {"message": "Quiz API is running!"}

@app.get("/api/questions", response_model=List[Question])
async def get_questions():
    """Get all quiz questions without revealing correct answers."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, question_text, options FROM questions ORDER BY id")
        rows = cursor.fetchall()
        conn.close()
        
        questions = []
        for row in rows:
            questions.append(Question(
                id=row["id"],
                question_text=row["question_text"],
                options=json.loads(row["options"])
            ))
        
        return questions
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching questions: {str(e)}")

@app.post("/api/submit", response_model=QuizResult)
async def submit_quiz(user_answers: UserAnswers):
    """Submit quiz answers and get score with detailed results."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all questions with correct answers
        cursor.execute("SELECT id, question_text, options, correct_option FROM questions ORDER BY id")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            raise HTTPException(status_code=404, detail="No questions found")
        
        results = []
        score = 0
        
        for row in rows:
            question_id = row["id"]
            correct_option = row["correct_option"]
            user_answer = user_answers.answers.get(question_id)
            is_correct = user_answer == correct_option if user_answer is not None else False
            
            if is_correct:
                score += 1
            
            results.append(QuestionWithAnswer(
                id=question_id,
                question_text=row["question_text"],
                options=json.loads(row["options"]),
                correct_option=correct_option,
                user_answer=user_answer,
                is_correct=is_correct
            ))
        
        total_questions = len(results)
        percentage = (score / total_questions * 100) if total_questions > 0 else 0
        
        return QuizResult(
            score=score,
            total_questions=total_questions,
            percentage=round(percentage, 2),
            results=results
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing quiz submission: {str(e)}")

# ============= AUTHENTICATION ROUTES =============

@app.post("/api/auth/register", response_model=Token)
async def register_user(user_data: UserCreate):
    """Register a new user with enhanced security validation."""
    try:
        from input_validation import SecureUserCreate, validate_user_input
        
        # Validate input with security checks
        validated_data = validate_user_input(user_data.dict(), SecureUserCreate)
        
        # Check if user already exists
        existing_user = get_user_by_email(validated_data['email'])
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password if provided
        hashed_password = None
        if validated_data.get('password'):
            hashed_password = get_password_hash(validated_data['password'])
        
        # Create user with validated data
        user_id = create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            hashed_password=hashed_password,
            google_id=validated_data.get('google_id'),
            phone=validated_data.get('phone'),
            address=validated_data.get('address')
        )
        
        # Get created user
        user = get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        user_dict = {key: user[key] for key in user.keys()}
        
        # Generate tokens
        tokens = generate_tokens(user_dict)
        
        return Token(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            user=User(**user_dict)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/api/auth/login", response_model=Token)
async def login_user(login_data: UserLogin):
    """Login user with enhanced security validation."""
    try:
        from input_validation import SecureUserLogin, validate_user_input
        
        logging.info(f"Login attempt for email: {login_data.email}")
        
        # Validate input with security checks
        validated_data = validate_user_input(login_data.model_dump(), SecureUserLogin)
        logging.info(f"Input validation passed for: {validated_data['email']}")
        
        # Get user
        user = get_user_by_email(validated_data['email'])
        if not user:
            logging.warning(f"User not found for email: {validated_data['email']}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        logging.info(f"User found: {user['email']}, is_admin: {user.get('is_admin', False)}")
        
        # Verify password
        password_check = verify_password(validated_data['password'], user["hashed_password"])
        logging.info(f"Password verification result: {password_check}")
        
        if not user["hashed_password"] or not password_check:
            logging.warning(f"Password verification failed for: {validated_data['email']}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        user_dict = {key: user[key] for key in user.keys()}
        
        # Generate tokens
        tokens = generate_tokens(user_dict)
        
        return Token(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            user=User(**user_dict)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.get("/api/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current authenticated user information."""
    return current_user

@app.post("/api/auth/google", response_model=Token)
async def google_auth(auth_data: GoogleAuthRequest):
    """Authenticate with Google OAuth."""
    try:
        from google_auth import GoogleAuth
        from database import create_or_get_google_user
        
        # Verify Google token and get user info
        google_info = GoogleAuth.verify_google_token(auth_data.token)
        
        # Create or get existing user
        user_id = create_or_get_google_user(google_info)
        
        # Get complete user data
        user = get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create or retrieve user"
            )
        
        user_dict = {key: user[key] for key in user.keys()}
        
        # Generate tokens
        tokens = generate_tokens(user_dict)
        
        return Token(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            user=User(**user_dict)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google authentication failed: {str(e)}"
        )

@app.post("/api/auth/refresh", response_model=Token)
async def refresh_access_token(refresh_token: str):
    """Refresh access token using refresh token."""
    try:
        from auth_utils import verify_token
        
        # Verify refresh token
        payload = verify_token(refresh_token, "refresh")
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user data
        user = get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        user_dict = {key: user[key] for key in user.keys()}
        
        # Generate new tokens
        tokens = generate_tokens(user_dict)
        
        return Token(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            user=User(**user_dict)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )

@app.post("/api/auth/logout")
async def logout_user(current_user: User = Depends(get_current_active_user)):
    """Logout user (client should remove tokens)."""
    return {"message": "Successfully logged out"}

@app.get("/api/auth/profile", response_model=User)
async def get_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get detailed user profile."""
    return current_user

@app.put("/api/auth/profile", response_model=User)
async def update_user_profile(
    profile_data: dict, 
    current_user: User = Depends(get_current_active_user)
):
    """Update user profile."""
    try:
        from database import get_db_connection
        
        # Validate and sanitize input
        allowed_fields = ['name', 'phone', 'address']
        update_data = {k: v for k, v in profile_data.items() if k in allowed_fields and v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields to update"
            )
        
        # Update database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        set_clause = ", ".join([f"{field} = ?" for field in update_data.keys()])
        values = list(update_data.values()) + [current_user.id]
        
        cursor.execute(f'''
            UPDATE users 
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', values)
        
        conn.commit()
        conn.close()
        
        # Return updated user
        updated_user = get_user_by_id(current_user.id)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve updated user"
            )
        
        updated_user_dict = {key: updated_user[key] for key in updated_user.keys()}
        return User(**updated_user_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile update failed: {str(e)}"
        )

# ============= ADMIN ROUTES =============

@app.get("/api/admin/stats", response_model=AdminStats)
async def get_admin_stats(admin_user: User = Depends(get_current_admin_user)):
    """Get basic admin statistics."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total users
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE is_active = 1")
        total_users = cursor.fetchone()['count']
        
        # Get total questions
        cursor.execute("SELECT COUNT(*) as count FROM questions")
        total_questions = cursor.fetchone()['count']
        
        # Get total quiz attempts
        cursor.execute("SELECT COUNT(*) as count FROM quiz_attempts")
        total_attempts = cursor.fetchone()['count']
        
        # Get average score
        cursor.execute("SELECT AVG(percentage) as avg_score FROM quiz_attempts")
        avg_result = cursor.fetchone()
        average_score = float(avg_result['avg_score']) if avg_result['avg_score'] else 0.0
        
        conn.close()
        
        return AdminStats(
            total_users=total_users,
            total_questions=total_questions,
            total_attempts=total_attempts,
            average_score=round(average_score, 2)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get admin stats: {str(e)}"
        )

@app.get("/api/admin/questions")
async def get_all_questions_admin(admin_user: User = Depends(get_current_admin_user)):
    """Get all questions with correct answers for admin."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM questions ORDER BY id")
        rows = cursor.fetchall()
        conn.close()
        
        questions = []
        for row in rows:
            questions.append({
                "id": row["id"],
                "question_text": row["question_text"],
                "options": json.loads(row["options"]),
                "correct_option": row["correct_option"]
            })
        
        return {"questions": questions}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get questions: {str(e)}"
        )

@app.post("/api/admin/questions")
async def create_question(
    question_data: dict,
    admin_user: User = Depends(get_current_admin_user)
):
    """Create a new question (admin only)."""
    try:
        from input_validation import SecureQuestionCreate, validate_user_input
        
        # Validate input
        validated_data = validate_user_input(question_data, SecureQuestionCreate)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO questions (question_text, options, correct_option)
            VALUES (?, ?, ?)
        ''', (
            validated_data['question_text'],
            json.dumps(validated_data['options']),
            validated_data['correct_option']
        ))
        
        question_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "message": "Question created successfully",
            "question_id": question_id
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create question: {str(e)}"
        )

@app.delete("/api/admin/questions/{question_id}")
async def delete_question(
    question_id: int,
    admin_user: User = Depends(get_current_admin_user)
):
    """Delete a question (admin only)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if question exists
        cursor.execute("SELECT id FROM questions WHERE id = ?", (question_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        # Delete question
        cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
        conn.commit()
        conn.close()
        
        return {"message": "Question deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete question: {str(e)}"
        )

# ============= ENHANCED QUIZ ROUTES WITH AUTH =============

@app.post("/api/submit-authenticated", response_model=QuizResultWithUser)
async def submit_quiz_authenticated(
    user_answers: UserAnswers, 
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Submit quiz answers with optional user authentication for tracking."""
    try:
        logger.info(f"Quiz submission received. User: {current_user.email if current_user else 'Anonymous'}")
        logger.info(f"Answers submitted: {user_answers.answers}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all questions with correct answers
        cursor.execute("SELECT id, question_text, options, correct_option FROM questions ORDER BY id")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            raise HTTPException(status_code=404, detail="No questions found")
        
        results = []
        score = 0
        
        for row in rows:
            question_id = row["id"]
            correct_option = row["correct_option"]
            user_answer = user_answers.answers.get(question_id)
            is_correct = user_answer == correct_option if user_answer is not None else False
            
            if is_correct:
                score += 1
            
            results.append(QuestionWithAnswer(
                id=question_id,
                question_text=row["question_text"],
                options=json.loads(row["options"]),
                correct_option=correct_option,
                user_answer=user_answer,
                is_correct=is_correct
            ))
        
        total_questions = len(results)
        percentage = (score / total_questions * 100) if total_questions > 0 else 0
        
        logger.info(f"Quiz results: {score}/{total_questions} ({percentage}%)")
        
        # Save attempt if user is authenticated
        attempt_id = None
        if current_user:
            logger.info(f"Saving quiz attempt for user {current_user.email}")
            try:
                attempt_id = save_quiz_attempt(
                    user_id=current_user.id,
                    score=score,
                    total_questions=total_questions,
                    percentage=percentage,
                    answers=user_answers.answers
                )
                logger.info(f"Quiz attempt saved with ID: {attempt_id}")
            except Exception as save_error:
                logger.error(f"Error saving quiz attempt: {str(save_error)}")
                raise
        else:
            logger.warning("No user authenticated - quiz attempt not saved")
        
        # Convert results to dict format for proper serialization
        results_dict = [result.model_dump() for result in results]
        
        return QuizResultWithUser(
            score=score,
            total_questions=total_questions,
            percentage=round(percentage, 2),
            results=results_dict,
            attempt_id=attempt_id,
            user_id=current_user.id if current_user else None
        )
    
    except Exception as e:
        logger.error(f"Error processing quiz submission: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing quiz submission: {str(e)}")

@app.get("/api/quiz-history")
async def get_quiz_history(current_user: User = Depends(get_current_active_user)):
    """Get quiz history for the authenticated user."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user's quiz attempts
        cursor.execute("""
            SELECT id, score, total_questions, percentage, completed_at 
            FROM quiz_attempts 
            WHERE user_id = ? 
            ORDER BY completed_at DESC 
            LIMIT 20
        """, (current_user.id,))
        
        rows = cursor.fetchall()
        
        attempts = []
        for row in rows:
            attempts.append({
                "id": row["id"],
                "score": row["score"],
                "total_questions": row["total_questions"],
                "percentage": row["percentage"],
                "attempt_date": row["completed_at"]
            })
        
        conn.close()
        
        logger.info(f"Retrieved {len(attempts)} quiz attempts for user {current_user.email}")
        return {"attempts": attempts}
        
    except Exception as e:
        logger.error(f"Error fetching quiz history for user {current_user.email}: {str(e)}")
        # Return empty attempts list instead of raising an error
        return {"attempts": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)