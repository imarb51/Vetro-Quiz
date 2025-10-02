# Vetro Quiz Application 🎯# Online Quiz Application



A full-stack quiz application with user authentication, admin panel, and real-time scoring. Built with FastAPI and React.A full-stack quiz application built with React frontend and FastAPI backend.



![Quiz Application](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)## Features

![Tests](https://img.shields.io/badge/Tests-17%20Passing-success)

![Python](https://img.shields.io/badge/Python-3.11-blue)### Core Features ✅

![React](https://img.shields.io/badge/React-18-blue)- **Backend**: FastAPI with SQLite database storing quiz questions

- **Database**: Pre-loaded with 8 sample questions across various topics

## 📋 Features- **API Endpoints**:

  - `GET /api/questions` - Fetch quiz questions (without correct answers)

### Core Features  - `POST /api/submit` - Submit answers and get scored results

- ✅ **Interactive Quiz**: Multiple-choice questions with real-time navigation- **Frontend**: React with modern UI/UX

- ✅ **Timer**: 5-minute countdown with auto-submit- **Quiz Flow**: Start → Questions → Results

- ✅ **Scoring System**: Instant results with detailed breakdown- **Navigation**: Next/Previous buttons between questions

- ✅ **User Authentication**: Email/Password and Google OAuth- **State Management**: Tracks user answers throughout the quiz

- ✅ **Admin Panel**: Complete CRUD operations for users and questions- **Score Calculation**: Real-time scoring with percentage and detailed results

- ✅ **PDF Import**: Bulk upload questions via PDF

- ✅ **Responsive Design**: Works on desktop, tablet, and mobile### Bonus Features ✨

- **Timer**: 5-minute countdown timer with visual warnings

### Tech Stack- **Detailed Results**: Shows correct/incorrect answers for each question

- **Backend**: FastAPI, SQLite, Python 3.11- **Progress Bar**: Visual progress indicator

- **Frontend**: React 18, React Router v6- **Responsive Design**: Works on desktop and mobile

- **Authentication**: JWT, Google OAuth 2.0- **Test Coverage**: Comprehensive backend tests for scoring logic

- **Testing**: Pytest (17 test cases)

## Project Structure

---

```

## 🚀 Quick Startvetro/

├── backend/

### Prerequisites│   ├── main.py              # FastAPI application

- Python 3.11 or higher│   ├── models.py            # Pydantic models

- Node.js 16 or higher│   ├── database.py          # Database initialization

- npm or yarn│   ├── test_main.py         # Test suite

│   ├── requirements.txt     # Python dependencies

### Installation│   └── quiz.db             # SQLite database (created on first run)

├── frontend/

#### 1. Clone the Repository│   ├── src/

```bash│   │   ├── App.js          # Main React component

git clone https://github.com/imarb51/Vetro-Quiz.git│   │   ├── StartScreen.js  # Quiz start screen

cd vetro│   │   ├── QuizQuestion.js # Question display component

```│   │   ├── ResultsScreen.js # Results display

│   │   ├── api.js          # API communication

#### 2. Backend Setup│   │   ├── index.js        # React entry point

│   │   └── index.css       # Styles

```bash│   ├── public/

# Navigate to backend folder│   │   └── index.html      # HTML template

cd backend│   └── package.json        # Node.js dependencies

└── README.md               # This file

# Create virtual environment```

python -m venv myenv

## Setup Instructions

# Activate virtual environment

# On Windows:### Prerequisites

myenv\Scripts\activate- Python 3.8+

# On macOS/Linux:- Node.js 16+

source myenv/bin/activate- npm or yarn



# Install dependencies### Backend Setup

pip install -r requirements.txt

1. Navigate to the backend directory:

# Initialize database```bash

python database.pycd backend

```

# Run the backend server

python main.py2. Create a virtual environment:

``````bash

python -m venv venv

Backend will run on `http://localhost:8000````



#### 3. Frontend Setup3. Activate the virtual environment:

```bash

Open a new terminal:# Windows

venv\Scripts\activate

```bash

# Navigate to frontend folder# macOS/Linux

cd frontendsource venv/bin/activate

```

# Install dependencies

npm install4. Install dependencies:

```bash

# Start the development serverpip install -r requirements.txt

npm start```

```

5. Initialize the database with sample questions:

Frontend will run on `http://localhost:3000````bash

python database.py

---```



## 📖 Usage6. Start the FastAPI server:

```bash

### For Userspython main.py

```

1. **Register/Login**

   - Visit `http://localhost:3000`The backend will be available at `http://localhost:8000`

   - Create an account or login with email/password

   - Or use Google OAuth for quick login### Frontend Setup



2. **Take a Quiz**1. Navigate to the frontend directory:

   - Click "Start Quiz" from your dashboard```bash

   - Answer questions using Previous/Next buttonscd frontend

   - Submit when complete or let the timer auto-submit```



3. **View Results**2. Install dependencies:

   - See your score and percentage```bash

   - Review which questions you got right/wrongnpm install

   - Retake the quiz or return to dashboard```



### For Admins3. Start the React development server:

```bash

1. **Admin Login**npm start

   - Navigate to `http://localhost:3000/admin````

   - Default credentials:

     - **Username**: `admin`The frontend will be available at `http://localhost:3000`

     - **Password**: `admin123`

   - ⚠️ **Change these in production!**## Running Tests



2. **Manage Users**### Backend Tests

   - View all registered users```bash

   - Edit user information (name, email, phone, address)cd backend

   - Delete users if neededpytest test_main.py -v

   - View user quiz history and statistics```



3. **Manage Questions**The test suite covers:

   - Add questions manually- API endpoint functionality

   - Edit existing questions- Scoring logic accuracy

   - Delete questions- Edge cases (empty answers, partial answers)

   - Upload multiple questions via PDF- Response structure validation



4. **PDF Upload Format**## API Documentation

   ```

   Q1. What is 2 + 2?### GET /api/questions

   A) 3Returns all quiz questions without correct answers.

   B) 4

   C) 5**Response:**

   D) 6```json

   Answer: B[

  {

   Q2. What is the capital of France?    "id": 1,

   A) London    "question_text": "What is the capital of France?",

   B) Berlin    "options": ["London", "Berlin", "Paris", "Madrid"]

   C) Paris  }

   D) Madrid]

   Answer: C```

   ```

### POST /api/submit

---Submit quiz answers and receive scored results.



## 🧪 Running Tests**Request:**

```json

```bash{

# Navigate to backend  "answers": {

cd backend    "1": 2,

    "2": 1

# Activate virtual environment  }

myenv\Scripts\activate  # Windows}

source myenv/bin/activate  # macOS/Linux```



# Run all tests**Response:**

python -m pytest test_api.py -v```json

{

# Run specific test  "score": 2,

python -m pytest test_api.py::test_submit_quiz_all_correct -v  "total_questions": 8,

```  "percentage": 25.0,

  "results": [

**Test Coverage**: 17 tests covering:    {

- Question fetching      "id": 1,

- Scoring logic (all correct, partial, missing answers)      "question_text": "What is the capital of France?",

- Percentage calculations      "options": ["London", "Berlin", "Paris", "Madrid"],

- Edge cases (invalid IDs, empty submissions)      "correct_option": 2,

- Performance (response time < 1s)      "user_answer": 2,

      "is_correct": true

---    }

  ]

## 📁 Project Structure}

```

```

vetro/## Usage

├── backend/

│   ├── main.py                    # FastAPI application1. **Start Quiz**: Click "Start Quiz" on the welcome screen

│   ├── database.py                # Database initialization2. **Answer Questions**: Select your answer and navigate with Next/Previous

│   ├── models.py                  # Pydantic models3. **Submit**: Click "Submit Quiz" on the final question

│   ├── test_api.py                # Test suite (17 tests)4. **View Results**: See your score and detailed breakdown

│   ├── pdf_parser.py              # PDF question parser5. **Retake**: Click "Take Quiz Again" to restart

│   ├── auth_dependencies.py       # Auth middleware

│   ├── auth_models.py             # Auth data models## Technical Highlights

│   ├── auth_utils.py              # Auth utilities

│   ├── google_auth.py             # Google OAuth integration### Frontend Architecture

│   ├── input_validation.py        # Input validation- **React Hooks**: useState and useEffect for state management

│   ├── security_middleware.py     # Security layer- **Component Composition**: Modular components for different screens

│   ├── requirements.txt           # Python dependencies- **API Integration**: Axios for HTTP requests

│   └── quiz_app.db               # SQLite database (auto-generated)- **Timer Implementation**: Real-time countdown with auto-submit

│- **Responsive Design**: CSS Grid/Flexbox for mobile compatibility

├── frontend/

│   ├── src/### Backend Architecture

│   │   ├── App.js                 # Main application- **FastAPI**: Modern Python web framework

│   │   ├── api.js                 # API client- **SQLite**: Lightweight database for questions storage

│   │   ├── StartScreen.js         # Quiz start page- **Pydantic**: Type validation and serialization

│   │   ├── QuizQuestion.js        # Question display- **CORS**: Configured for cross-origin requests

│   │   ├── ResultsScreen.js       # Score display- **Error Handling**: Comprehensive error responses

│   │   ├── index.css              # Global styles

│   │   └── components/### Database Schema

│   │       ├── Login.js           # User login```sql

│   │       ├── Register.js        # User registrationquestions (

│   │       ├── UserDashboard.js   # User dashboard  id INTEGER PRIMARY KEY,

│   │       ├── AdminLoginPage.js  # Admin login  question_text TEXT NOT NULL,

│   │       ├── NewAdminDashboard.js  # Admin dashboard  options TEXT NOT NULL,        -- JSON array

│   │       ├── UsersManagement.js    # User management  correct_option INTEGER NOT NULL

│   │       └── QuestionsManagement.js # Question management)

│   ├── package.json```

│   └── package-lock.json

│## Development Notes

└── README.md                      # This file

```- The application uses a proxy configuration to route API calls from React to FastAPI

- CORS is configured to allow requests from the React development server

---- The timer automatically submits the quiz when time expires

- User answers are preserved when navigating between questions

## 📡 API Endpoints- Results show which questions were correct, incorrect, or unanswered



### Public Endpoints## Possible Enhancements

```

GET  /api/questions              Get all quiz questions (without answers)- Multiple quiz categories

POST /api/submit                 Submit quiz answers and get score- User authentication and score history

POST /api/auth/register          Register new user- Question difficulty levels

POST /api/auth/login             User login- Admin panel for managing questions

POST /api/auth/google            Google OAuth login- Real-time multiplayer quizzes

```- Export results to PDF

- Social sharing of results
### Protected Endpoints (Requires Authentication)
```
GET  /api/user/profile           Get user profile
POST /api/submit-authenticated   Submit quiz with user tracking
GET  /api/user/quiz-history      Get user's quiz history
```

### Admin Endpoints (Requires Admin Role)
```
GET    /api/admin/users                    Get all users
GET    /api/admin/users/{user_id}          Get user details
PUT    /api/admin/users/{user_id}          Update user
DELETE /api/admin/users/{user_id}          Delete user
GET    /api/admin/questions                Get all questions (with answers)
POST   /api/admin/questions                Create question
PUT    /api/admin/questions/{question_id}  Update question
DELETE /api/admin/questions/{question_id}  Delete question
POST   /api/admin/questions/upload-pdf     Upload questions via PDF
```

---

## 🔧 Configuration

### Backend Configuration (Optional)

Create a `.env` file in the `backend` folder for custom configuration:

```env
# JWT Secret Keys
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=sqlite:///./quiz_app.db

# Admin Credentials (Change in production!)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

### Frontend Configuration (Optional)

Create a `.env` file in the `frontend` folder:

```env
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id-here
```

---

## 🔐 Security Notes

⚠️ **Important**: Before deploying to production:

1. **Change Default Admin Credentials**
   - Update in `backend/main.py` line ~950
   ```python
   DEFAULT_ADMIN_USERNAME = "your-secure-username"
   DEFAULT_ADMIN_PASSWORD = "your-secure-password"
   ```

2. **Set Strong Secret Keys**
   - Generate secure keys for JWT tokens
   - Use environment variables

3. **Enable HTTPS**
   - Configure SSL certificates
   - Update CORS settings for your domain

4. **Database**
   - For production, consider PostgreSQL or MySQL
   - Enable regular backups

---

## 🐛 Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError`
```bash
# Make sure virtual environment is activated
myenv\Scripts\activate  # Windows
source myenv/bin/activate  # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

**Issue**: Database errors
```bash
# Reinitialize database
python database.py
```

**Issue**: Port 8000 already in use
```bash
# Change port in main.py (last line)
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Frontend Issues

**Issue**: `npm install` fails
```bash
# Clear npm cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**Issue**: CORS errors
- Check that backend is running on `http://localhost:8000`
- Verify `API_BASE_URL` in `frontend/src/api.js`
- Clear browser cache

**Issue**: White screen after `npm start`
```bash
# Check for JavaScript errors in browser console (F12)
# Ensure all dependencies are installed
npm install
```

---

## 📊 Database Schema

### Questions Table
```sql
id               INTEGER PRIMARY KEY
question_text    TEXT NOT NULL
options          TEXT NOT NULL (JSON array)
correct_option   INTEGER NOT NULL
```

### Users Table
```sql
id               TEXT PRIMARY KEY (UUID)
email            TEXT UNIQUE NOT NULL
name             TEXT NOT NULL
phone            TEXT
address          TEXT
hashed_password  TEXT
google_id        TEXT UNIQUE
is_active        BOOLEAN
is_admin         BOOLEAN
created_at       DATETIME
```

### Quiz Attempts Table
```sql
id               TEXT PRIMARY KEY (UUID)
user_id          TEXT (Foreign Key)
score            INTEGER NOT NULL
total_questions  INTEGER NOT NULL
percentage       REAL NOT NULL
answers          TEXT (JSON)
completed_at     DATETIME
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👨‍💻 Author

**imarb51**
- GitHub: [@imarb51](https://github.com/imarb51)
- Repository: [Vetro-Quiz](https://github.com/imarb51/Vetro-Quiz)

---

## 🙏 Acknowledgments

- FastAPI for the amazing backend framework
- React team for the frontend library
- pdfplumber for PDF parsing capabilities
- All contributors and testers

---

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review the [API Endpoints](#-api-endpoints) documentation
3. Open an issue on GitHub with detailed information

---

**Made with ❤️ for learning and education**
