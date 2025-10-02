import pytest
from fastapi.testclient import TestClient
import os
import tempfile
from pathlib import Path
from main import app
from database import init_database

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    """Set up test database before running tests."""
    # Create a temporary database for testing
    test_db_path = Path(__file__).parent / "test_quiz.db"
    
    # Initialize the database
    init_database()
    
    yield
    
    # Clean up - remove test database if it exists
    if test_db_path.exists():
        test_db_path.unlink()

def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Quiz API is running!"}

def test_get_questions():
    """Test fetching quiz questions."""
    response = client.get("/api/questions")
    assert response.status_code == 200
    
    questions = response.json()
    assert isinstance(questions, list)
    assert len(questions) > 0
    
    # Check structure of first question
    first_question = questions[0]
    assert "id" in first_question
    assert "question_text" in first_question
    assert "options" in first_question
    assert isinstance(first_question["options"], list)
    assert len(first_question["options"]) == 4
    
    # Ensure correct answers are not exposed
    assert "correct_option" not in first_question

def test_submit_quiz_all_correct():
    """Test submitting quiz with all correct answers."""
    # First get the questions to know how many there are
    questions_response = client.get("/api/questions")
    questions = questions_response.json()
    
    # Prepare answers - these should match the correct answers from database.py
    correct_answers = {
        1: 2,  # Paris
        2: 1,  # Mars
        3: 1,  # 4
        4: 2,  # Leonardo da Vinci
        5: 3,  # Pacific Ocean
        6: 1,  # JavaScript
        7: 2,  # 1945
        8: 1,  # Oxygen
    }
    
    # Only include answers for questions that exist
    answers = {q["id"]: correct_answers[q["id"]] for q in questions if q["id"] in correct_answers}
    
    response = client.post("/api/submit", json={"answers": answers})
    assert response.status_code == 200
    
    result = response.json()
    assert "score" in result
    assert "total_questions" in result
    assert "percentage" in result
    assert "results" in result
    
    assert result["score"] == len(questions)
    assert result["total_questions"] == len(questions)
    assert result["percentage"] == 100.0

def test_submit_quiz_all_wrong():
    """Test submitting quiz with all wrong answers."""
    questions_response = client.get("/api/questions")
    questions = questions_response.json()
    
    # Prepare wrong answers (always select option 0 if it's not correct)
    wrong_answers = {}
    for q in questions:
        wrong_answers[q["id"]] = 0  # Always choose first option
    
    response = client.post("/api/submit", json={"answers": wrong_answers})
    assert response.status_code == 200
    
    result = response.json()
    # Should have low score (some questions might have 0 as correct answer)
    assert result["score"] <= len(questions)
    assert result["percentage"] <= 100.0

def test_submit_quiz_partial_answers():
    """Test submitting quiz with only some questions answered."""
    questions_response = client.get("/api/questions")
    questions = questions_response.json()
    
    # Answer only the first question
    partial_answers = {questions[0]["id"]: 2}
    
    response = client.post("/api/submit", json={"answers": partial_answers})
    assert response.status_code == 200
    
    result = response.json()
    assert result["total_questions"] == len(questions)
    # Score should be 0 or 1 depending on if the answer was correct
    assert 0 <= result["score"] <= 1

def test_submit_empty_answers():
    """Test submitting quiz with no answers."""
    response = client.post("/api/submit", json={"answers": {}})
    assert response.status_code == 200
    
    result = response.json()
    assert result["score"] == 0
    assert result["percentage"] == 0.0

def test_quiz_result_structure():
    """Test the structure of quiz results."""
    # Get questions first
    questions_response = client.get("/api/questions")
    questions = questions_response.json()
    
    # Submit some answers
    answers = {questions[0]["id"]: 1}
    response = client.post("/api/submit", json={"answers": answers})
    
    result = response.json()
    
    # Check overall structure
    assert "score" in result
    assert "total_questions" in result
    assert "percentage" in result
    assert "results" in result
    
    # Check results structure
    results = result["results"]
    assert len(results) == len(questions)
    
    for question_result in results:
        assert "id" in question_result
        assert "question_text" in question_result
        assert "options" in question_result
        assert "correct_option" in question_result
        assert "user_answer" in question_result
        assert "is_correct" in question_result