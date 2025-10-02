"""
Backend Test Cases for Vetro Quiz Application
Tests for scoring logic, question fetching, and authentication
"""

import pytest
import json
from fastapi.testclient import TestClient
from main import app
from database import init_database, get_db_connection
import os

# Test client
client = TestClient(app)

# Test database path
TEST_DB = "test_quiz.db"


@pytest.fixture(scope="function")
def setup_test_db():
    """Setup test database before each test and cleanup after."""
    # Backup production DB if it exists
    if os.path.exists("quiz_app.db"):
        os.rename("quiz_app.db", "quiz_app.db.backup")
    
    # Create test database
    init_database()
    
    # Clear any sample questions that were added
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM questions")
    conn.commit()
    
    # Add test questions
    test_questions = [
        {
            "question_text": "What is 2 + 2?",
            "options": json.dumps(["3", "4", "5", "6"]),
            "correct_option": 1
        },
        {
            "question_text": "What is the capital of France?",
            "options": json.dumps(["London", "Berlin", "Paris", "Madrid"]),
            "correct_option": 2
        },
        {
            "question_text": "What color is the sky?",
            "options": json.dumps(["Red", "Blue", "Green", "Yellow"]),
            "correct_option": 1
        }
    ]
    
    for q in test_questions:
        cursor.execute(
            "INSERT INTO questions (question_text, options, correct_option) VALUES (?, ?, ?)",
            (q["question_text"], q["options"], q["correct_option"])
        )
    
    conn.commit()
    conn.close()
    
    yield
    
    # Cleanup: Remove test DB and restore production DB
    if os.path.exists("quiz_app.db"):
        os.remove("quiz_app.db")
    
    if os.path.exists("quiz_app.db.backup"):
        os.rename("quiz_app.db.backup", "quiz_app.db")


# ============= TEST QUESTIONS ENDPOINT =============

def test_get_questions_success(setup_test_db):
    """Test fetching questions without correct answers."""
    response = client.get("/api/questions")
    
    assert response.status_code == 200
    questions = response.json()
    
    # Should return 3 test questions
    assert len(questions) == 3
    
    # Check structure of first question
    first_question = questions[0]
    assert "id" in first_question
    assert "question_text" in first_question
    assert "options" in first_question
    
    # Should NOT contain correct_option (security check)
    assert "correct_option" not in first_question
    
    # Verify question content
    assert first_question["question_text"] == "What is 2 + 2?"
    assert len(first_question["options"]) == 4


def test_get_questions_returns_all_questions(setup_test_db):
    """Test that all questions are returned."""
    response = client.get("/api/questions")
    questions = response.json()
    
    expected_texts = [
        "What is 2 + 2?",
        "What is the capital of France?",
        "What color is the sky?"
    ]
    
    actual_texts = [q["question_text"] for q in questions]
    assert actual_texts == expected_texts


# ============= TEST SCORING LOGIC =============

def test_submit_quiz_all_correct(setup_test_db):
    """Test scoring when all answers are correct."""
    # First get the questions to see their IDs
    questions_response = client.get("/api/questions")
    questions = questions_response.json()
    
    # Build answers based on actual question IDs
    answers = {}
    for q in questions:
        qid = q["id"]
        if "2 + 2" in q["question_text"]:
            answers[qid] = 1  # Answer is "4" at index 1
        elif "France" in q["question_text"]:
            answers[qid] = 2  # Answer is "Paris" at index 2
        elif "sky" in q["question_text"]:
            answers[qid] = 1  # Answer is "Blue" at index 1
    
    response = client.post("/api/submit", json={"answers": answers})
    
    assert response.status_code == 200
    result = response.json()
    
    # Check score calculation
    assert result["score"] == 3
    assert result["total_questions"] == 3
    assert result["percentage"] == 100.0
    
    # Check detailed results
    assert len(result["results"]) == 3
    assert all(r["is_correct"] for r in result["results"])


def test_submit_quiz_all_incorrect(setup_test_db):
    """Test scoring when all answers are incorrect."""
    # All wrong answers
    answers = {
        1: 0,  # Wrong answer
        2: 0,  # Wrong answer
        3: 0   # Wrong answer
    }
    
    response = client.post("/api/submit", json={"answers": answers})
    
    assert response.status_code == 200
    result = response.json()
    
    # Check score calculation
    assert result["score"] == 0
    assert result["total_questions"] == 3
    assert result["percentage"] == 0.0
    
    # Check that all marked as incorrect
    assert all(not r["is_correct"] for r in result["results"])


def test_submit_quiz_partial_correct(setup_test_db):
    """Test scoring with mix of correct and incorrect answers."""
    # Get questions first
    questions_response = client.get("/api/questions")
    questions = questions_response.json()
    
    # 2 correct, 1 incorrect
    answers = {}
    for q in questions:
        qid = q["id"]
        if "2 + 2" in q["question_text"]:
            answers[qid] = 1  # Correct
        elif "France" in q["question_text"]:
            answers[qid] = 2  # Correct
        elif "sky" in q["question_text"]:
            answers[qid] = 0  # Incorrect
    
    response = client.post("/api/submit", json={"answers": answers})
    
    assert response.status_code == 200
    result = response.json()
    
    # Check score calculation
    assert result["score"] == 2
    assert result["total_questions"] == 3
    assert result["percentage"] == 66.67
    
    # Verify correct answers marked correctly
    results_by_text = {r["question_text"]: r for r in result["results"]}
    assert results_by_text["What is 2 + 2?"]["is_correct"] is True
    assert results_by_text["What is the capital of France?"]["is_correct"] is True
    assert results_by_text["What color is the sky?"]["is_correct"] is False


def test_submit_quiz_missing_answers(setup_test_db):
    """Test scoring when some answers are missing."""
    # Get questions first
    questions_response = client.get("/api/questions")
    questions = questions_response.json()
    
    # Only answer 2 out of 3 questions
    answers = {}
    for q in questions:
        qid = q["id"]
        if "2 + 2" in q["question_text"]:
            answers[qid] = 1  # Correct
        elif "France" in q["question_text"]:
            answers[qid] = 2  # Correct
        # Question 3 not answered
    
    response = client.post("/api/submit", json={"answers": answers})
    
    assert response.status_code == 200
    result = response.json()
    
    # Missing answers should be marked as incorrect
    assert result["score"] == 2
    assert result["total_questions"] == 3
    assert result["percentage"] == 66.67
    
    # Check unanswered question
    results_by_text = {r["question_text"]: r for r in result["results"]}
    unanswered = results_by_text["What color is the sky?"]
    assert unanswered["user_answer"] is None
    assert unanswered["is_correct"] is False


def test_submit_quiz_empty_answers(setup_test_db):
    """Test scoring with no answers submitted."""
    answers = {}
    
    response = client.post("/api/submit", json={"answers": answers})
    
    assert response.status_code == 200
    result = response.json()
    
    # No correct answers
    assert result["score"] == 0
    assert result["total_questions"] == 3
    assert result["percentage"] == 0.0


def test_submit_quiz_returns_correct_options(setup_test_db):
    """Test that results include correct answer information."""
    answers = {1: 0, 2: 0, 3: 0}  # All wrong
    
    response = client.post("/api/submit", json={"answers": answers})
    result = response.json()
    
    # Verify correct options are included
    assert result["results"][0]["correct_option"] == 1
    assert result["results"][1]["correct_option"] == 2
    assert result["results"][2]["correct_option"] == 1


def test_submit_quiz_returns_user_answers(setup_test_db):
    """Test that results include user's selected answers."""
    # Get questions first
    questions_response = client.get("/api/questions")
    questions = questions_response.json()
    
    answers = {}
    for q in questions:
        qid = q["id"]
        if "2 + 2" in q["question_text"]:
            answers[qid] = 0
        elif "France" in q["question_text"]:
            answers[qid] = 1
        elif "sky" in q["question_text"]:
            answers[qid] = 2
    
    response = client.post("/api/submit", json={"answers": answers})
    result = response.json()
    
    # Verify user answers are returned
    results_by_text = {r["question_text"]: r for r in result["results"]}
    assert results_by_text["What is 2 + 2?"]["user_answer"] == 0
    assert results_by_text["What is the capital of France?"]["user_answer"] == 1
    assert results_by_text["What color is the sky?"]["user_answer"] == 2


# ============= TEST EDGE CASES =============

def test_submit_quiz_invalid_question_id(setup_test_db):
    """Test handling of invalid question IDs."""
    # Include answer for non-existent question
    answers = {
        1: 1,
        999: 2  # Non-existent question ID
    }
    
    response = client.post("/api/submit", json={"answers": answers})
    
    # Should still process valid answers
    assert response.status_code == 200
    result = response.json()
    assert result["score"] >= 0


def test_submit_quiz_invalid_answer_index(setup_test_db):
    """Test handling of out-of-range answer indices."""
    # Answer index that's out of bounds
    answers = {
        1: 10,  # Invalid index
        2: 2,   # Valid
        3: 1    # Valid
    }
    
    response = client.post("/api/submit", json={"answers": answers})
    
    # Should handle gracefully
    assert response.status_code == 200
    result = response.json()
    
    # Invalid index should be marked incorrect
    assert result["results"][0]["is_correct"] is False


def test_get_questions_empty_database():
    """Test fetching questions when database is empty."""
    # This will run without setup_test_db fixture
    # Create empty DB
    if os.path.exists("quiz_app.db"):
        os.rename("quiz_app.db", "quiz_app.db.backup2")
    
    init_database()
    
    response = client.get("/api/questions")
    
    # Should return empty list, not error
    assert response.status_code == 200
    assert response.json() == []
    
    # Cleanup
    if os.path.exists("quiz_app.db"):
        os.remove("quiz_app.db")
    if os.path.exists("quiz_app.db.backup2"):
        os.rename("quiz_app.db.backup2", "quiz_app.db")


# ============= TEST PERCENTAGE CALCULATION =============

def test_percentage_calculation_accuracy(setup_test_db):
    """Test that percentage is calculated with correct precision."""
    # Get questions first
    questions_response = client.get("/api/questions")
    questions = questions_response.json()
    
    # 1 correct out of 3
    answers = {}
    for q in questions:
        qid = q["id"]
        if "2 + 2" in q["question_text"]:
            answers[qid] = 1  # Correct
        else:
            answers[qid] = 0  # Wrong
    
    response = client.post("/api/submit", json={"answers": answers})
    result = response.json()
    
    expected_percentage = round(1/3 * 100, 2)
    assert result["percentage"] == expected_percentage


def test_percentage_rounding(setup_test_db):
    """Test that percentage is properly rounded to 2 decimal places."""
    # Get questions first
    questions_response = client.get("/api/questions")
    questions = questions_response.json()
    
    # 2 out of 3
    answers = {}
    for q in questions:
        qid = q["id"]
        if "2 + 2" in q["question_text"]:
            answers[qid] = 1  # Correct
        elif "France" in q["question_text"]:
            answers[qid] = 2  # Correct
        else:
            answers[qid] = 0  # Wrong
    
    response = client.post("/api/submit", json={"answers": answers})
    result = response.json()
    
    # Should be 66.67, not 66.66666...
    assert result["percentage"] == 66.67
    assert isinstance(result["percentage"], float)


# ============= TEST DATA INTEGRITY =============

def test_questions_have_required_fields(setup_test_db):
    """Test that all questions have required fields."""
    response = client.get("/api/questions")
    questions = response.json()
    
    for question in questions:
        assert "id" in question
        assert "question_text" in question
        assert "options" in question
        assert isinstance(question["options"], list)
        assert len(question["options"]) > 0


def test_results_maintain_question_order(setup_test_db):
    """Test that results are returned in correct question order."""
    answers = {1: 1, 2: 2, 3: 1}
    
    response = client.post("/api/submit", json={"answers": answers})
    result = response.json()
    
    # Results should be in order
    assert result["results"][0]["question_text"] == "What is 2 + 2?"
    assert result["results"][1]["question_text"] == "What is the capital of France?"
    assert result["results"][2]["question_text"] == "What color is the sky?"


# ============= PERFORMANCE TESTS =============

def test_submit_quiz_response_time(setup_test_db):
    """Test that quiz submission responds quickly."""
    import time
    
    answers = {1: 1, 2: 2, 3: 1}
    
    start_time = time.time()
    response = client.post("/api/submit", json={"answers": answers})
    end_time = time.time()
    
    # Should respond in less than 1 second
    response_time = end_time - start_time
    assert response_time < 1.0
    assert response.status_code == 200


# ============= RUN TESTS =============

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
