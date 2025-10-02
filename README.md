# Online Quiz Application

A full-stack quiz application built with React frontend and FastAPI backend.

## Features

### Core Features ✅
- **Backend**: FastAPI with SQLite database storing quiz questions
- **Database**: Pre-loaded with 8 sample questions across various topics
- **API Endpoints**:
  - `GET /api/questions` - Fetch quiz questions (without correct answers)
  - `POST /api/submit` - Submit answers and get scored results
- **Frontend**: React with modern UI/UX
- **Quiz Flow**: Start → Questions → Results
- **Navigation**: Next/Previous buttons between questions
- **State Management**: Tracks user answers throughout the quiz
- **Score Calculation**: Real-time scoring with percentage and detailed results

### Bonus Features ✨
- **Timer**: 5-minute countdown timer with visual warnings
- **Detailed Results**: Shows correct/incorrect answers for each question
- **Progress Bar**: Visual progress indicator
- **Responsive Design**: Works on desktop and mobile
- **Test Coverage**: Comprehensive backend tests for scoring logic

## Project Structure

```
vetro/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── database.py          # Database initialization
│   ├── test_main.py         # Test suite
│   ├── requirements.txt     # Python dependencies
│   └── quiz.db             # SQLite database (created on first run)
├── frontend/
│   ├── src/
│   │   ├── App.js          # Main React component
│   │   ├── StartScreen.js  # Quiz start screen
│   │   ├── QuizQuestion.js # Question display component
│   │   ├── ResultsScreen.js # Results display
│   │   ├── api.js          # API communication
│   │   ├── index.js        # React entry point
│   │   └── index.css       # Styles
│   ├── public/
│   │   └── index.html      # HTML template
│   └── package.json        # Node.js dependencies
└── README.md               # This file
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Initialize the database with sample questions:
```bash
python database.py
```

6. Start the FastAPI server:
```bash
python main.py
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the React development server:
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## Running Tests

### Backend Tests
```bash
cd backend
pytest test_main.py -v
```

The test suite covers:
- API endpoint functionality
- Scoring logic accuracy
- Edge cases (empty answers, partial answers)
- Response structure validation

## API Documentation

### GET /api/questions
Returns all quiz questions without correct answers.

**Response:**
```json
[
  {
    "id": 1,
    "question_text": "What is the capital of France?",
    "options": ["London", "Berlin", "Paris", "Madrid"]
  }
]
```

### POST /api/submit
Submit quiz answers and receive scored results.

**Request:**
```json
{
  "answers": {
    "1": 2,
    "2": 1
  }
}
```

**Response:**
```json
{
  "score": 2,
  "total_questions": 8,
  "percentage": 25.0,
  "results": [
    {
      "id": 1,
      "question_text": "What is the capital of France?",
      "options": ["London", "Berlin", "Paris", "Madrid"],
      "correct_option": 2,
      "user_answer": 2,
      "is_correct": true
    }
  ]
}
```

## Usage

1. **Start Quiz**: Click "Start Quiz" on the welcome screen
2. **Answer Questions**: Select your answer and navigate with Next/Previous
3. **Submit**: Click "Submit Quiz" on the final question
4. **View Results**: See your score and detailed breakdown
5. **Retake**: Click "Take Quiz Again" to restart

## Technical Highlights

### Frontend Architecture
- **React Hooks**: useState and useEffect for state management
- **Component Composition**: Modular components for different screens
- **API Integration**: Axios for HTTP requests
- **Timer Implementation**: Real-time countdown with auto-submit
- **Responsive Design**: CSS Grid/Flexbox for mobile compatibility

### Backend Architecture
- **FastAPI**: Modern Python web framework
- **SQLite**: Lightweight database for questions storage
- **Pydantic**: Type validation and serialization
- **CORS**: Configured for cross-origin requests
- **Error Handling**: Comprehensive error responses

### Database Schema
```sql
questions (
  id INTEGER PRIMARY KEY,
  question_text TEXT NOT NULL,
  options TEXT NOT NULL,        -- JSON array
  correct_option INTEGER NOT NULL
)
```

## Development Notes

- The application uses a proxy configuration to route API calls from React to FastAPI
- CORS is configured to allow requests from the React development server
- The timer automatically submits the quiz when time expires
- User answers are preserved when navigating between questions
- Results show which questions were correct, incorrect, or unanswered

## Possible Enhancements

- Multiple quiz categories
- User authentication and score history
- Question difficulty levels
- Admin panel for managing questions
- Real-time multiplayer quizzes
- Export results to PDF
- Social sharing of results