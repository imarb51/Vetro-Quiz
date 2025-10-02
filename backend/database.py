import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional


def init_database():
    """Initialize the SQLite database with sample quiz questions and user management tables."""
    db_path = Path(__file__).parent / "quiz.db"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create questions table (existing - preserved)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_text TEXT NOT NULL,
            options TEXT NOT NULL,
            correct_option INTEGER NOT NULL
        )
    ''')

    # Create users table for authentication
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            google_id TEXT UNIQUE,
            hashed_password TEXT,
            is_active BOOLEAN DEFAULT 1,
            is_admin BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create quiz_attempts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            percentage REAL NOT NULL,
            time_taken INTEGER,
            answers TEXT,
            completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Create user_sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            access_token TEXT NOT NULL,
            refresh_token TEXT,
            expires_at DATETIME NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Create admin_settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_key TEXT UNIQUE NOT NULL,
            setting_value TEXT NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Clear existing data for demo purposes
    cursor.execute('DELETE FROM questions')

    # Insert sample quiz questions
    sample_questions = [
        {
            "question_text": "What is the capital of France?",
            "options": ["London", "Berlin", "Paris", "Madrid"],
            "correct_option": 2
        },
        {
            "question_text": "Which planet is known as the Red Planet?",
            "options": ["Venus", "Mars", "Jupiter", "Saturn"],
            "correct_option": 1
        },
        {
            "question_text": "What is 2 + 2?",
            "options": ["3", "4", "5", "6"],
            "correct_option": 1
        },
        {
            "question_text": "Who painted the Mona Lisa?",
            "options": ["Vincent van Gogh", "Pablo Picasso", "Leonardo da Vinci", "Michelangelo"],
            "correct_option": 2
        },
        {
            "question_text": "What is the largest ocean on Earth?",
            "options": ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean", "Pacific Ocean"],
            "correct_option": 3
        },
        {
            "question_text": "Which programming language is known for its use in web development?",
            "options": ["C++", "JavaScript", "Assembly", "COBOL"],
            "correct_option": 1
        },
        {
            "question_text": "What year did World War II end?",
            "options": ["1943", "1944", "1945", "1946"],
            "correct_option": 2
        },
        {
            "question_text": "Which element has the chemical symbol 'O'?",
            "options": ["Gold", "Oxygen", "Silver", "Iron"],
            "correct_option": 1
        }
    ]

    for q in sample_questions:
        cursor.execute(
            'INSERT INTO questions (question_text, options, correct_option) VALUES (?, ?, ?)',
            (q["question_text"], json.dumps(q["options"]), q["correct_option"])
        )

    # Create default admin user if not exists
    admin_email = "imranance99@gmail.com"
    cursor.execute("SELECT id FROM users WHERE email = ?", (admin_email,))
    if not cursor.fetchone():
        admin_id = str(uuid.uuid4())
        try:
            from auth_utils import get_password_hash
            # Use a simpler password for admin (under 72 bytes)
            admin_password = "admin123"
            hashed_password = get_password_hash(admin_password)
            cursor.execute('''
                INSERT INTO users (id, email, name, hashed_password, is_admin, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (admin_id, admin_email, "Admin User", hashed_password, 1, 1))
            print(f"Created default admin user: {admin_email} with password: {admin_password}")
        except (ImportError, Exception) as e:
            print(f"Warning: Could not hash password ({e}), creating admin without password")
            cursor.execute('''
                INSERT INTO users (id, email, name, is_admin, is_active)
                VALUES (?, ?, ?, ?, ?)
            ''', (admin_id, admin_email, "Admin User", 1, 1))
        print(f"Created default admin user: {admin_email}")

    # Insert default admin settings
    default_settings = [
        ("quiz_time_limit", "300"),  # 5 minutes
        ("max_questions_per_quiz", "10"),
        ("allow_anonymous_quiz", "true"),
        ("gemini_api_enabled", "false")
    ]

    for key, value in default_settings:
        cursor.execute('''
            INSERT OR REPLACE INTO admin_settings (setting_key, setting_value)
            VALUES (?, ?)
        ''', (key, value))

    conn.commit()
    conn.close()
    print("✅ Database initialized with sample questions and user management tables!")


def get_db_connection():
    """Get database connection with row factory."""
    db_path = Path(__file__).parent / "quiz.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def create_user(email: str, name: str, hashed_password: Optional[str] = None,
                google_id: Optional[str] = None, phone: Optional[str] = None,
                address: Optional[str] = None) -> str:
    """Create a new user and return user ID."""
    user_id = str(uuid.uuid4())
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO users (id, email, name, hashed_password, google_id, phone, address)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, email, name, hashed_password, google_id, phone, address))

    conn.commit()
    conn.close()
    return user_id


def get_user_by_email(email: str):
    """Get user by email."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ? AND is_active = 1", (email,))
    user = cursor.fetchone()
    conn.close()
    # Convert sqlite3.Row to dictionary for compatibility with login endpoint
    if user:
        return dict(user)
    return None


def get_user_by_id(user_id: str):
    """Get user by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ? AND is_active = 1", (user_id,))
    user = cursor.fetchone()
    conn.close()
    # Convert sqlite3.Row to dictionary for compatibility
    if user:
        return dict(user)
    return None


def get_user_by_google_id(google_id: str):
    """Get user by Google ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE google_id = ? AND is_active = 1", (google_id,))
    user = cursor.fetchone()
    conn.close()
    return user


def update_user_google_id(user_id: str, google_id: str):
    """Update user's Google ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET google_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (google_id, user_id)
    )
    conn.commit()
    conn.close()


def create_or_get_google_user(google_info: dict) -> str:
    """Create a new user from Google info or return existing user ID."""
    user = get_user_by_google_id(google_info['google_id'])
    if user:
        return user['id']

    user = get_user_by_email(google_info['email'])
    if user:
        update_user_google_id(user['id'], google_info['google_id'])
        return user['id']

    return create_user(
        email=google_info['email'],
        name=google_info['name'],
        google_id=google_info['google_id']
    )


def save_quiz_attempt(user_id: str, score: int, total_questions: int,
                      percentage: float, answers: dict, time_taken: Optional[int] = None):
    """Save quiz attempt to database."""
    attempt_id = str(uuid.uuid4())
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO quiz_attempts (id, user_id, score, total_questions, percentage, answers, time_taken)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (attempt_id, user_id, score, total_questions, percentage, json.dumps(answers), time_taken))

    conn.commit()
    conn.close()
    return attempt_id


if __name__ == "__main__":
    init_database()
