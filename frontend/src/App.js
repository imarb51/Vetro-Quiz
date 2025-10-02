import React, { useState, useEffect, useCallback } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { quizAPI, authAPI } from "./api";

// Screens & components
import StartScreen from "./StartScreen";
import QuizQuestion from "./QuizQuestion";
import ResultsScreen from "./ResultsScreen";
import Login from "./components/Login";
import Register from "./components/Register";
import AdminLogin from "./components/AdminLogin";
import AdminLoginPage from "./components/AdminLoginPage";
import UserDashboard from "./components/UserDashboard";
import AdminDashboard from "./components/AdminDashboard";
import NewAdminDashboard from "./components/NewAdminDashboard";
import UsersManagement from "./components/UsersManagement";
import QuestionsManagement from "./components/QuestionsManagement";

const QUIZ_TIME_LIMIT = 5 * 60; // 5 minutes in seconds
const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID;

// Protected Route Component
function ProtectedRoute({ children, user }) {
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

// Admin Route Component
function AdminRoute({ children, user }) {
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  if (!user.is_admin) {
    return <Navigate to="/dashboard" replace />;
  }
  return children;
}

// Main App Content Component
// Main App Content Component
function AppContent() {
  const navigate = useNavigate();
  
  // Authentication state
  const [user, setUser] = useState(null);

  // Quiz state
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  const [timeLeft, setTimeLeft] = useState(QUIZ_TIME_LIMIT);

  // Submit quiz function (defined early to avoid hoisting issues)
  const handleSubmitQuiz = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const resultsData = await quizAPI.submitQuiz(userAnswers);
      setResults(resultsData);
      navigate('/results');
    } catch (err) {
      setError('Failed to submit quiz. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [userAnswers, navigate]);

  // Check authentication on app load
  useEffect(() => {
    const checkAuth = () => {
      const isAuth = authAPI.isAuthenticated();
      const userData = authAPI.getCurrentUser();
      
      if (isAuth && userData) {
        setUser(userData);
      } else {
        setUser(null);
      }
    };

    checkAuth();
  }, []);

  // Timer effect
  useEffect(() => {
    let timer;
    if (window.location.pathname === '/quiz' && timeLeft > 0) {
      timer = setInterval(() => {
        setTimeLeft(prev => {
          if (prev <= 1) {
            // Time's up - auto submit
            handleSubmitQuiz();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [timeLeft, handleSubmitQuiz]);

  // Authentication handlers
  const handleLogin = (userData) => {
    setUser(userData);
    setError(null);
    // Navigate based on user role
    if (userData.is_admin) {
      navigate('/admin/dashboard');
    } else {
      navigate('/dashboard');
    }
  };

  const handleRegister = (userData) => {
    setUser(userData);
    setError(null);
    navigate('/dashboard');
  };

  const handleLogout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      // Reset quiz state
      setQuestions([]);
      setCurrentQuestionIndex(0);
      setUserAnswers({});
      setResults(null);
      setTimeLeft(QUIZ_TIME_LIMIT);
      navigate('/login');
    }
  };

  const fetchQuestions = async () => {
    try {
      setLoading(true);
      setError(null);
      const questionsData = await quizAPI.getQuestions();
      setQuestions(questionsData);
    } catch (err) {
      setError('Failed to load questions. Please check if the backend server is running.');
    } finally {
      setLoading(false);
    }
  };

  const startQuiz = async () => {
    await fetchQuestions();
    if (questions.length > 0 || !error) {
      setCurrentQuestionIndex(0);
      setUserAnswers({});
      setTimeLeft(QUIZ_TIME_LIMIT);
      navigate('/quiz');
    }
  };

  const selectAnswer = (answerIndex) => {
    const currentQuestion = questions[currentQuestionIndex];
    setUserAnswers(prev => ({
      ...prev,
      [currentQuestion.id]: answerIndex
    }));
  };

  const goToNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    }
  };

  const goToPreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  const retakeQuiz = () => {
    setCurrentQuestionIndex(0);
    setUserAnswers({});
    setResults(null);
    setError(null);
    setTimeLeft(QUIZ_TIME_LIMIT);
    navigate('/start');
  };

  // Loading state
  if (loading) {
    return (
      <div className="quiz-container">
        <div className="quiz-card">
          <div className="loading">
            <span aria-live="polite">Loading your quiz...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="quiz-container">
      <main role="main" aria-label="Online Quiz Application">
        {error && (
          <div className="error" role="alert" aria-live="assertive">
            {error}
          </div>
        )}

        <Routes>
          {/* Admin Routes - Must come BEFORE other routes */}
          <Route 
            path="/admin" 
            element={
              user ? (
                <Navigate to="/admin/dashboard" replace />
              ) : (
                <AdminLoginPage onLogin={handleLogin} />
              )
            } 
          />

          <Route 
            path="/admin/dashboard" 
            element={
              <AdminRoute user={user}>
                <NewAdminDashboard />
              </AdminRoute>
            } 
          />

          <Route 
            path="/admin/users" 
            element={
              <AdminRoute user={user}>
                <UsersManagement />
              </AdminRoute>
            } 
          />

          <Route 
            path="/admin/questions" 
            element={
              <AdminRoute user={user}>
                <QuestionsManagement />
              </AdminRoute>
            } 
          />

          {/* Auth Routes */}
          <Route 
            path="/login" 
            element={
              user ? (
                <Navigate to={user.is_admin ? "/admin/dashboard" : "/dashboard"} replace />
              ) : (
                <Login 
                  onLogin={handleLogin}
                  onSwitchToRegister={() => navigate('/register')}
                  onSwitchToAdminLogin={() => navigate('/admin')}
                  setError={setError}
                />
              )
            } 
          />
          
          <Route 
            path="/register" 
            element={
              user ? (
                <Navigate to="/dashboard" replace />
              ) : (
                <Register 
                  onRegister={handleRegister}
                  onSwitchToLogin={() => navigate('/login')}
                  setError={setError}
                />
              )
            } 
          />

          {/* Protected Routes */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute user={user}>
                <UserDashboard 
                  user={user}
                  onLogout={handleLogout}
                  onStartQuiz={() => navigate('/start')}
                />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/start" 
            element={
              <ProtectedRoute user={user}>
                <StartScreen 
                  onStartQuiz={startQuiz} 
                  questionsCount={questions.length}
                  user={user}
                  onBackToDashboard={() => navigate(user?.is_admin ? '/admin/dashboard' : '/dashboard')}
                />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/quiz" 
            element={
              <ProtectedRoute user={user}>
                {questions.length > 0 ? (
                  <QuizQuestion
                    question={questions[currentQuestionIndex]}
                    currentQuestionIndex={currentQuestionIndex}
                    totalQuestions={questions.length}
                    selectedAnswer={userAnswers[questions[currentQuestionIndex].id]}
                    onAnswerSelect={selectAnswer}
                    onNext={goToNextQuestion}
                    onPrevious={goToPreviousQuestion}
                    onSubmit={handleSubmitQuiz}
                    isLastQuestion={currentQuestionIndex === questions.length - 1}
                    timeLeft={timeLeft}
                  />
                ) : (
                  <Navigate to="/start" replace />
                )}
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/results" 
            element={
              <ProtectedRoute user={user}>
                {results ? (
                  <ResultsScreen 
                    results={results} 
                    onRetakeQuiz={retakeQuiz}
                    onBackToDashboard={() => navigate(user?.is_admin ? '/admin/dashboard' : '/dashboard')}
                  />
                ) : (
                  <Navigate to="/dashboard" replace />
                )}
              </ProtectedRoute>
            } 
          />

          {/* Default Route */}
          <Route 
            path="/" 
            element={
              <Navigate to={user ? (user.is_admin ? "/admin/dashboard" : "/dashboard") : "/login"} replace />
            } 
          />

          {/* Catch all - redirect to home */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

// Main App Component with Router and OAuth Provider
function App() {
  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <Router>
        <AppContent />
      </Router>
    </GoogleOAuthProvider>
  );
}

export default App;