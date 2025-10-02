# Vetro Quiz: Full-Stack Quiz Application

A feature-rich, full-stack quiz application built with a React frontend and a FastAPI backend. This project includes user authentication, Google OAuth, a full-featured admin panel, PDF-based question uploads, and comprehensive backend testing.

---

## ✨ Features

### Core User Features
- **User Registration & Login**: Secure local authentication with password hashing.
- **Google OAuth 2.0**: One-click login/registration using Google.
- **User Dashboard**: Personalized dashboard for authenticated users.
- **Quiz History**: Users can view their past quiz attempts and scores.
- **Timed Quizzes**: A 5-minute countdown timer with auto-submission.
- **Interactive Quiz Interface**:
    - Navigate with "Next" and "Previous" buttons.
    - Progress bar to track completion.
    - Answers are preserved when navigating.
- **Detailed Results**: Instant feedback with score, percentage, and a review of correct/incorrect answers.
- **Responsive Design**: Fully functional on both desktop and mobile devices.

### Admin Panel Features
- **Admin-Only Access**: Separate login for administrators.
- **User Management (CRUD)**:
    - View all registered users.
    - Edit user details (name, email, phone, address).
    - Delete users.
    - View quiz history for any user.
- **Question Management (CRUD)**:
    - Add, edit, and delete quiz questions.
    - View all questions with correct answers.
- **PDF Question Upload**: Bulk-add questions by uploading a formatted PDF file.

---

## 📁 Project Structure

```
vetro/
├── backend/
│   ├── main.py                    # FastAPI application core
│   ├── database.py                # Database connection and initialization
│   ├── models.py                  # Pydantic models for API data
│   ├── test_api.py                # Backend test suite (17 tests)
│   ├── auth_dependencies.py       # Authentication middleware and dependencies
│   ├── auth_models.py             # Pydantic models for authentication
│   ├── auth_utils.py              # Password hashing and token utilities
│   ├── google_auth.py             # Google OAuth 2.0 integration
│   ├── input_validation.py        # Server-side input validation logic
│   ├── security_middleware.py     # Extra security headers middleware
│   ├── requirements.txt           # Python dependencies
│   └── quiz_app.db                # SQLite database (auto-generated)
│
├── frontend/
│   ├── src/
│   │   ├── App.js                 # Main application router
│   │   ├── api.js                 # Centralized API client (Axios)
│   │   ├── StartScreen.js         # Initial landing page
│   │   ├── QuizQuestion.js        # Component for displaying a single question
│   │   ├── ResultsScreen.js       # Component for displaying quiz results
│   │   └── components/
│   │       ├── Login.js           # User login component
│   │       ├── Register.js        # User registration component
│   │       ├── UserDashboard.js   # Dashboard for regular users
│   │       ├── AdminLogin.js      # Login page for admins
│   │       └── AdminDashboard.js  # Main dashboard for admin tasks
│   ├── package.json
│   └── public/
│
└── README.md                      # This file
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- **Node.js 16+**
- **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/imarb51/Vetro-Quiz.git
cd Vetro-Quiz
```

### 2. Backend Setup
```bash
# Navigate to the backend folder
cd backend

# Create a Python virtual environment
python -m venv myenv

# Activate the virtual environment
# On Windows:
myenv\Scripts\activate
# On macOS/Linux:
# source myenv/bin/activate

# Install the required Python packages
pip install -r requirements.txt

# Run the backend server
# The server will start on http://localhost:8000
uvicorn main:app --reload
```

### 3. Frontend Setup
*Open a new terminal for this step.*
```bash
# Navigate to the frontend folder
cd frontend

# Install the required Node.js packages
npm install

# Start the React development server
# The application will open on http://localhost:3000
npm start
```

---

## 📖 Usage

### As a User
1.  **Register/Login**: Visit `http://localhost:3000`, create an account, or log in with Google.
2.  **Start Quiz**: From your dashboard, click "Start Quiz".
3.  **Answer Questions**: Navigate through questions. Your progress is saved.
4.  **View Results**: After submitting, review your score and see a detailed breakdown of your answers.

### As an Admin
1.  **Login**: Navigate to `http://localhost:3000/admin`.
2.  **Credentials**: Use the default credentials (change them in production!):
    - **Username**: `admin`
    - **Password**: `admin123`
3.  **Manage**: Use the dashboard to manage users and questions.
4.  **Upload Questions**: Use the "Upload PDF" feature to add questions in bulk. The format must be:
    ```
    Q1. What is 2 + 2?
    A) 3
    B) 4
    C) 5
    Answer: B

    Q2. What is the capital of France?
    A) London
    B) Paris
    C) Berlin
    Answer: B
    ```

---

## 🧪 Running Tests

The backend includes a comprehensive test suite with **17 tests** covering API logic, scoring, and edge cases.

```bash
# Navigate to the backend directory
cd backend

# Make sure your virtual environment is activated
myenv\Scripts\activate

# Run the tests with verbose output
pytest -v
```

---

## 📡 API Endpoints

A summary of the available API endpoints.

### Public Endpoints
- `POST /api/auth/register`: Register a new user.
- `POST /api/auth/login`: Log in a user and get JWT tokens.
- `POST /api/auth/google`: Authenticate or register a user via Google.
- `GET /api/questions`: Fetch quiz questions (for unauthenticated users).
- `POST /api/submit`: Submit quiz answers (for unauthenticated users).

### Protected Endpoints (Requires User Authentication)
- `GET  /api/user/profile`: Get the current user's profile.
- `POST /api/submit-authenticated`: Submit quiz answers and save the attempt to the user's history.
- `GET  /api/user/quiz-history`: Get the logged-in user's quiz history.

### Admin Endpoints (Requires Admin Authentication)
- `GET    /api/admin/users`: Get a list of all users.
- `PUT    /api/admin/users/{user_id}`: Update a user's details.
- `DELETE /api/admin/users/{user_id}`: Delete a user.
- `GET    /api/admin/questions`: Get all questions, including correct answers.
- `POST   /api/admin/questions`: Create a new question.
- `PUT    /api/admin/questions/{question_id}`: Update an existing question.
- `DELETE /api/admin/questions/{question_id}`: Delete a question.
- `POST   /api/admin/questions/upload-pdf`: Upload questions from a PDF file.

---

## 🔐 Security Notes

⚠️ **Important**: Before deploying to production:

1.  **Change Default Admin Credentials**: Modify the `ADMIN_USERNAME` and `ADMIN_PASSWORD` in a `.env` file in the `backend` directory.
2.  **Set Strong Secret Keys**: Create a `.env` file in the `backend` directory and set `SECRET_KEY`, `ALGORITHM`, and token expiry times.
3.  **Configure Frontend Environment**: Create a `.env` file in the `frontend` directory to store `REACT_APP_GOOGLE_CLIENT_ID`.
4.  **Enable HTTPS**: Always use HTTPS in production.
5.  **Database**: For a production environment, consider migrating from SQLite to a more robust database like PostgreSQL.

---

## 🤝 Contributing

Contributions are welcome! Please fork the repository and open a pull request with your changes.

## 📝 License

This project is licensed under the MIT License.

## 👨‍💻 Author

- **GitHub**: [@imarb51](https://github.com/imarb51)
- **Repository**: [Vetro-Quiz](https://github.com/imarb51/Vetro-Quiz)