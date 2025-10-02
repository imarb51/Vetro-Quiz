import React, { useState, useEffect } from 'react';
import { adminAPI } from '../api';

const AdminDashboard = ({ user, onLogout, onStartQuiz }) => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // New question form state
  const [newQuestion, setNewQuestion] = useState({
    question_text: '',
    options: ['', '', '', ''],
    correct_option: 0
  });

  useEffect(() => {
    if (activeTab === 'dashboard') {
      fetchStats();
    } else if (activeTab === 'questions') {
      fetchQuestions();
    }
  }, [activeTab]);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const statsData = await adminAPI.getStats();
      setStats(statsData);
    } catch (err) {
      setError('Failed to load admin statistics');
    } finally {
      setLoading(false);
    }
  };

  const fetchQuestions = async () => {
    try {
      setLoading(true);
      const questionsData = await adminAPI.getAllQuestions();
      setQuestions(questionsData.questions || []);
    } catch (err) {
      setError('Failed to load questions');
    } finally {
      setLoading(false);
    }
  };

  const handleQuestionChange = (field, value, index = null) => {
    if (field === 'options' && index !== null) {
      const updatedOptions = [...newQuestion.options];
      updatedOptions[index] = value;
      setNewQuestion({ ...newQuestion, options: updatedOptions });
    } else {
      setNewQuestion({ ...newQuestion, [field]: value });
    }
  };

  const addOption = () => {
    if (newQuestion.options.length < 6) {
      setNewQuestion({
        ...newQuestion,
        options: [...newQuestion.options, '']
      });
    }
  };

  const removeOption = (index) => {
    if (newQuestion.options.length > 2) {
      const updatedOptions = newQuestion.options.filter((_, i) => i !== index);
      setNewQuestion({
        ...newQuestion,
        options: updatedOptions,
        correct_option: newQuestion.correct_option >= updatedOptions.length 
          ? updatedOptions.length - 1 
          : newQuestion.correct_option
      });
    }
  };

  const handleCreateQuestion = async (e) => {
    e.preventDefault();
    
    // Validate form
    if (!newQuestion.question_text.trim()) {
      setError('Question text is required');
      return;
    }

    const validOptions = newQuestion.options.filter(opt => opt.trim());
    if (validOptions.length < 2) {
      setError('At least 2 options are required');
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      const questionData = {
        question_text: newQuestion.question_text.trim(),
        options: validOptions,
        correct_option: newQuestion.correct_option
      };

      await adminAPI.createQuestion(questionData);
      
      // Reset form
      setNewQuestion({
        question_text: '',
        options: ['', '', '', ''],
        correct_option: 0
      });

      // Refresh questions list
      fetchQuestions();
    } catch (err) {
      setError('Failed to create question');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteQuestion = async (questionId) => {
    if (window.confirm('Are you sure you want to delete this question?')) {
      try {
        await adminAPI.deleteQuestion(questionId);
        fetchQuestions(); // Refresh list
      } catch (err) {
        setError('Failed to delete question');
      }
    }
  };

  return (
    <div className="admin-container">
      {/* Admin Header */}
      <div className="admin-header">
        <div className="admin-nav">
          <h1 className="admin-title">🎛️ Admin Portal</h1>
          <div className="admin-user-info">
            <span>Welcome, {user.name}</span>
            <button onClick={onLogout} className="btn btn-secondary btn-sm">
              Logout
            </button>
          </div>
        </div>

        <div className="admin-tabs">
          <button 
            className={`tab-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            📊 Dashboard
          </button>
          <button 
            className={`tab-btn ${activeTab === 'questions' ? 'active' : ''}`}
            onClick={() => setActiveTab('questions')}
          >
            📝 Questions
          </button>
          <button 
            className={`tab-btn ${activeTab === 'ai-generate' ? 'active' : ''}`}
            onClick={() => setActiveTab('ai-generate')}
          >
            🤖 AI Generate (Coming Soon)
          </button>
        </div>
      </div>

      {/* Admin Content */}
      <div className="admin-content">
        {error && (
          <div className="error-message" role="alert">
            {error}
          </div>
        )}

        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div className="dashboard-content">
            <h2>📈 System Statistics</h2>
            {loading ? (
              <div className="loading">Loading statistics...</div>
            ) : stats ? (
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-icon">👥</div>
                  <div className="stat-info">
                    <h3>{stats.total_users}</h3>
                    <p>Total Users</p>
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon">❓</div>
                  <div className="stat-info">
                    <h3>{stats.total_questions}</h3>
                    <p>Total Questions</p>
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon">📋</div>
                  <div className="stat-info">
                    <h3>{stats.total_attempts}</h3>
                    <p>Quiz Attempts</p>
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon">🎯</div>
                  <div className="stat-info">
                    <h3>{stats.average_score}%</h3>
                    <p>Average Score</p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="no-data">No statistics available</div>
            )}
          </div>
        )}

        {/* Questions Tab */}
        {activeTab === 'questions' && (
          <div className="questions-content">
            <div className="questions-section">
              <h2>➕ Create New Question</h2>
              <form onSubmit={handleCreateQuestion} className="question-form">
                <div className="form-group">
                  <label htmlFor="question_text">Question Text</label>
                  <textarea
                    id="question_text"
                    value={newQuestion.question_text}
                    onChange={(e) => handleQuestionChange('question_text', e.target.value)}
                    placeholder="Enter your question..."
                    rows="3"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Options</label>
                  {newQuestion.options.map((option, index) => (
                    <div key={index} className="option-row">
                      <input
                        type="text"
                        value={option}
                        onChange={(e) => handleQuestionChange('options', e.target.value, index)}
                        placeholder={`Option ${index + 1}`}
                      />
                      <input
                        type="radio"
                        name="correct_option"
                        checked={newQuestion.correct_option === index}
                        onChange={() => handleQuestionChange('correct_option', index)}
                        title="Mark as correct answer"
                      />
                      {newQuestion.options.length > 2 && (
                        <button
                          type="button"
                          onClick={() => removeOption(index)}
                          className="btn-remove-option"
                        >
                          ✕
                        </button>
                      )}
                    </div>
                  ))}
                  {newQuestion.options.length < 6 && (
                    <button
                      type="button"
                      onClick={addOption}
                      className="btn btn-secondary btn-sm"
                    >
                      + Add Option
                    </button>
                  )}
                </div>

                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Creating...' : 'Create Question'}
                </button>
              </form>
            </div>

            <div className="questions-list-section">
              <h2>📋 Existing Questions ({questions.length})</h2>
              {loading ? (
                <div className="loading">Loading questions...</div>
              ) : questions.length > 0 ? (
                <div className="questions-list">
                  {questions.map((question) => (
                    <div key={question.id} className="question-item">
                      <div className="question-content">
                        <h4>{question.question_text}</h4>
                        <div className="question-options">
                          {question.options.map((option, index) => (
                            <div 
                              key={index} 
                              className={`option ${index === question.correct_option ? 'correct' : ''}`}
                            >
                              {index === question.correct_option ? '✓' : '○'} {option}
                            </div>
                          ))}
                        </div>
                      </div>
                      <button
                        onClick={() => handleDeleteQuestion(question.id)}
                        className="btn btn-danger btn-sm"
                      >
                        Delete
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="no-data">No questions available</div>
              )}
            </div>
          </div>
        )}

        {/* AI Generate Tab */}
        {activeTab === 'ai-generate' && (
          <div className="ai-generate-content">
            <h2>🤖 AI-Powered Question Generation</h2>
            <div className="coming-soon">
              <p>🚧 This feature is coming soon!</p>
              <p>Generate questions automatically using Google Gemini AI based on topics and difficulty levels.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;