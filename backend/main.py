from fastapi import FastAPI, HTTPException, Depends, status, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
import os
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
import logging

# Import models
from models import (
    Question, UserAnswers, QuizResult, QuestionWithAnswer,
    AdminLogin, AdminUser, UserUpdate, QuestionCreate, QuestionUpdate
)
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
        
        # Get total users (excluding admins)
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE is_admin = 0")
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

@app.put("/api/admin/questions/{question_id}")
async def update_question(
    question_id: int,
    question_data: QuestionUpdate,
    admin_user: User = Depends(get_current_admin_user)
):
    """Update a question (admin only)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if question exists
        cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
        existing = cursor.fetchone()
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        # Build update query dynamically
        update_fields = []
        update_values = []
        
        if question_data.question_text is not None:
            update_fields.append("question_text = ?")
            update_values.append(question_data.question_text)
        
        if question_data.options is not None:
            update_fields.append("options = ?")
            update_values.append(json.dumps(question_data.options))
        
        if question_data.correct_option is not None:
            update_fields.append("correct_option = ?")
            update_values.append(question_data.correct_option)
        
        if not update_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        update_values.append(question_id)
        query = f"UPDATE questions SET {', '.join(update_fields)} WHERE id = ?"
        
        cursor.execute(query, update_values)
        conn.commit()
        conn.close()
        
        return {"message": "Question updated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update question: {str(e)}"
        )

@app.post("/api/admin/questions/upload-pdf")
async def upload_questions_pdf(
    file: UploadFile = File(...),
    admin_user: User = Depends(get_current_admin_user)
):
    """Upload questions from PDF file (admin only)."""
    try:
        from pdf_parser import parse_quiz_pdf_from_bytes
        
        # Read file content
        file_content = await file.read()
        
        # Parse PDF
        questions = parse_quiz_pdf_from_bytes(file_content)
        
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No questions found in PDF"
            )
        
        # Insert questions into database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        inserted_count = 0
        for q in questions:
            cursor.execute('''
                INSERT INTO questions (question_text, options, correct_option)
                VALUES (?, ?, ?)
            ''', (
                q['question_text'],
                json.dumps(q['options']),
                q['correct_option']
            ))
            inserted_count += 1
        
        conn.commit()
        conn.close()
        
        return {
            "message": f"Successfully uploaded {inserted_count} questions",
            "count": inserted_count
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload PDF: {str(e)}"
        )

# ============= USER MANAGEMENT ROUTES (ADMIN) =============

@app.get("/api/admin/users")
async def get_all_users(admin_user: User = Depends(get_current_admin_user)):
    """Get all users with their quiz statistics (admin only)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get users with their quiz stats
        cursor.execute('''
            SELECT 
                u.id,
                u.email,
                u.name,
                u.phone,
                u.address,
                u.is_active,
                u.created_at,
                COUNT(qa.id) as total_attempts,
                COALESCE(AVG(qa.percentage), 0) as average_score
            FROM users u
            LEFT JOIN quiz_attempts qa ON u.id = qa.user_id
            WHERE u.is_admin = 0
            GROUP BY u.id
            ORDER BY u.created_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        users = []
        for row in rows:
            users.append({
                "id": row["id"],
                "email": row["email"],
                "full_name": row["name"] or "N/A",
                "phone": row["phone"],
                "address": row["address"],
                "is_active": bool(row["is_active"]),
                "created_at": row["created_at"],
                "total_attempts": row["total_attempts"],
                "average_score": round(float(row["average_score"]), 2)
            })
        
        return {"users": users}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users: {str(e)}"
        )

@app.get("/api/admin/users/{user_id}")
async def get_user_details(
    user_id: str,
    admin_user: User = Depends(get_current_admin_user)
):
    """Get detailed information about a specific user (admin only)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user info
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get user's quiz history
        cursor.execute('''
            SELECT id, score, total_questions, percentage, completed_at
            FROM quiz_attempts
            WHERE user_id = ?
            ORDER BY completed_at DESC
        ''', (user_id,))
        
        attempts = []
        for row in cursor.fetchall():
            attempts.append({
                "id": row["id"],
                "score": row["score"],
                "total_questions": row["total_questions"],
                "percentage": round(float(row["percentage"]), 2),
                "completed_at": row["completed_at"]
            })
        
        conn.close()
        
        return {
            "user": {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["name"] or "N/A",
                "phone": user["phone"],
                "address": user["address"],
                "is_active": bool(user["is_active"]),
                "created_at": user["created_at"]
            },
            "quiz_history": attempts
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user details: {str(e)}"
        )

@app.put("/api/admin/users/{user_id}")
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    admin_user: User = Depends(get_current_admin_user)
):
    """Update user details (admin only)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Build update query
        update_fields = []
        update_values = []
        
        if user_data.email is not None:
            # Check if email is already taken
            cursor.execute("SELECT id FROM users WHERE email = ? AND id != ?", (user_data.email, user_id))
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            update_fields.append("email = ?")
            update_values.append(user_data.email)
        
        if user_data.password is not None:
            hashed_password = get_password_hash(user_data.password)
            update_fields.append("hashed_password = ?")
            update_values.append(hashed_password)
        
        if user_data.name is not None:
            update_fields.append("name = ?")
            update_values.append(user_data.name)
        
        if user_data.phone is not None:
            update_fields.append("phone = ?")
            update_values.append(user_data.phone)
        
        if user_data.address is not None:
            update_fields.append("address = ?")
            update_values.append(user_data.address)
        
        if not update_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        update_values.append(user_id)
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
        
        cursor.execute(query, update_values)
        conn.commit()
        conn.close()
        
        return {"message": "User updated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )

@app.delete("/api/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    admin_user: User = Depends(get_current_admin_user)
):
    """Delete a user (admin only)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Delete user's quiz attempts first (foreign key constraint)
        cursor.execute("DELETE FROM quiz_attempts WHERE user_id = ?", (user_id,))
        
        # Delete user
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        conn.commit()
        conn.close()
        
        return {"message": "User deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )

# ============= ADMIN AUTH ROUTE =============

@app.post("/api/admin/login")
async def admin_login(credentials: AdminLogin):
    """Admin login with default credentials."""
    try:
        # Default admin credentials
        DEFAULT_ADMIN_USERNAME = "admin"
        DEFAULT_ADMIN_PASSWORD = "admin123"
        
        if credentials.username != DEFAULT_ADMIN_USERNAME or credentials.password != DEFAULT_ADMIN_PASSWORD:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Check if admin user exists in database
        admin_user = get_user_by_email("admin@quiz.com")
        
        if not admin_user:
            # Create admin user if doesn't exist
            import uuid
            from database import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            
            admin_id = str(uuid.uuid4())
            hashed_password = get_password_hash(DEFAULT_ADMIN_PASSWORD)
            cursor.execute('''
                INSERT INTO users (id, email, hashed_password, name, is_admin, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (admin_id, "admin@quiz.com", hashed_password, "Administrator", 1, 1))
            
            conn.commit()
            conn.close()
            
            admin_user = get_user_by_id(admin_id)
        
        if not admin_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create admin user"
            )
        
        admin_dict = {key: admin_user[key] for key in admin_user.keys()}
        
        # Generate tokens
        tokens = generate_tokens(admin_dict)
        
        return Token(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            user=User(**admin_dict)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Admin login failed: {str(e)}"
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