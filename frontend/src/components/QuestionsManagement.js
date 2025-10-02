import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { adminAPI, authAPI } from '../api';
import './AdminDashboard.css';
import './QuestionsManagement.css';

function QuestionsManagement() {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [pdfFile, setPdfFile] = useState(null);
  const [questionForm, setQuestionForm] = useState({
    question_text: '',
    options: ['', '', '', ''],
    correct_option: 0
  });
  const navigate = useNavigate();

  useEffect(() => {
    fetchQuestions();
  }, []);

  const fetchQuestions = async () => {
    try {
      const data = await adminAPI.getAllQuestions();
      setQuestions(data.questions || []);
    } catch (error) {
      showMessage('error', 'Failed to fetch questions');
    } finally {
      setLoading(false);
    }
  };

  const handleAddQuestion = () => {
    setQuestionForm({
      question_text: '',
      options: ['', '', '', ''],
      correct_option: 0
    });
    setShowAddModal(true);
  };

  const handleEditQuestion = (question) => {
    setSelectedQuestion(question);
    setQuestionForm({
      question_text: question.question_text,
      options: question.options,
      correct_option: question.correct_option
    });
    setShowEditModal(true);
  };

  const handleDeleteQuestion = (question) => {
    setSelectedQuestion(question);
    setShowDeleteModal(true);
  };

  const confirmAddQuestion = async () => {
    try {
      // Validate form
      if (!questionForm.question_text.trim()) {
        showMessage('error', 'Question text is required');
        return;
      }
      
      const validOptions = questionForm.options.filter(opt => opt.trim() !== '');
      if (validOptions.length < 2) {
        showMessage('error', 'At least 2 options are required');
        return;
      }

      await adminAPI.createQuestion(questionForm);
      showMessage('success', 'Question added successfully');
      setShowAddModal(false);
      fetchQuestions();
    } catch (error) {
      showMessage('error', error.response?.data?.detail || 'Failed to add question');
    }
  };

  const confirmEditQuestion = async () => {
    try {
      await adminAPI.updateQuestion(selectedQuestion.id, questionForm);
      showMessage('success', 'Question updated successfully');
      setShowEditModal(false);
      fetchQuestions();
    } catch (error) {
      showMessage('error', 'Failed to update question');
    }
  };

  const confirmDeleteQuestion = async () => {
    try {
      await adminAPI.deleteQuestion(selectedQuestion.id);
      showMessage('success', 'Question deleted successfully');
      setShowDeleteModal(false);
      fetchQuestions();
    } catch (error) {
      showMessage('error', 'Failed to delete question');
    }
  };

  const handlePdfUpload = async () => {
    if (!pdfFile) {
      showMessage('error', 'Please select a PDF file');
      return;
    }

    try {
      setLoading(true);
      const response = await adminAPI.uploadPDF(pdfFile);
      showMessage('success', `Successfully imported ${response.count} questions`);
      setShowUploadModal(false);
      setPdfFile(null);
      fetchQuestions();
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to upload PDF';
      showMessage('error', typeof errorMsg === 'string' ? errorMsg : 'Failed to upload PDF');
    } finally {
      setLoading(false);
    }
  };

  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: '', text: '' }), 3000);
  };

  const handleLogout = async () => {
    await authAPI.logout();
    navigate('/admin');
  };

  const handleNavigation = (section) => {
    if (section === 'dashboard') {
      navigate('/admin/dashboard');
    } else if (section === 'users') {
      navigate('/admin/users');
    }
  };

  const updateOption = (index, value) => {
    const newOptions = [...questionForm.options];
    newOptions[index] = value;
    setQuestionForm({ ...questionForm, options: newOptions });
  };

  if (loading) {
    return (
      <div className="admin-loading">
        <div className="spinner-large"></div>
        <p>Loading questions...</p>
      </div>
    );
  }

  return (
    <div className="admin-layout">
      {/* Sidebar */}
      <aside className={`admin-sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <h2>📊 Admin Panel</h2>
          <button 
            className="sidebar-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? '✕' : '☰'}
          </button>
        </div>

        <nav className="sidebar-nav">
          <button
            className="nav-item"
            onClick={() => handleNavigation('dashboard')}
          >
            <span className="nav-icon">📈</span>
            {sidebarOpen && <span>Dashboard</span>}
          </button>

          <button
            className="nav-item"
            onClick={() => handleNavigation('users')}
          >
            <span className="nav-icon">👥</span>
            {sidebarOpen && <span>Users</span>}
          </button>

          <button
            className="nav-item active"
          >
            <span className="nav-icon">❓</span>
            {sidebarOpen && <span>Questions</span>}
          </button>

          <div className="nav-divider"></div>

          <button
            className="nav-item logout"
            onClick={handleLogout}
          >
            <span className="nav-icon">🚪</span>
            {sidebarOpen && <span>Logout</span>}
          </button>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="admin-main">
        <div className="admin-header">
          <h1>Questions Management</h1>
          <button 
            className="mobile-menu-btn"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            ☰
          </button>
        </div>

        {message.text && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}

        <div className="questions-actions">
          <button className="btn-primary" onClick={handleAddQuestion}>
            ➕ Add Question
          </button>
          <button className="btn-secondary" onClick={() => setShowUploadModal(true)}>
            📄 Upload PDF
          </button>
        </div>

        <div className="questions-container">
          <div className="table-container">
            <table className="questions-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Question</th>
                  <th>Options</th>
                  <th>Correct Answer</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {questions.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="no-data">
                      No questions found. Add questions using the buttons above.
                    </td>
                  </tr>
                ) : (
                  questions.map((question) => (
                    <tr key={question.id}>
                      <td>{question.id}</td>
                      <td className="question-text">{question.question_text}</td>
                      <td>
                        <ul className="options-list">
                          {question.options.map((opt, idx) => (
                            <li key={idx} className={idx === question.correct_option ? 'correct-option' : ''}>
                              {idx + 1}. {opt}
                            </li>
                          ))}
                        </ul>
                      </td>
                      <td>
                        <span className="answer-badge">
                          Option {question.correct_option + 1}
                        </span>
                      </td>
                      <td>
                        <div className="action-buttons-group">
                          <button
                            className="btn-edit"
                            onClick={() => handleEditQuestion(question)}
                          >
                            ✏️
                          </button>
                          <button
                            className="btn-delete"
                            onClick={() => handleDeleteQuestion(question)}
                          >
                            🗑️
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Add Question Modal */}
        {showAddModal && (
          <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h3>Add New Question</h3>
                <button className="modal-close" onClick={() => setShowAddModal(false)}>✕</button>
              </div>
              <div className="modal-body">
                <div className="form-group">
                  <label>Question Text:</label>
                  <textarea
                    value={questionForm.question_text}
                    onChange={(e) => setQuestionForm({ ...questionForm, question_text: e.target.value })}
                    rows="3"
                    placeholder="Enter question text"
                  />
                </div>
                <div className="form-group">
                  <label>Options:</label>
                  {questionForm.options.map((option, idx) => (
                    <input
                      key={idx}
                      type="text"
                      value={option}
                      onChange={(e) => updateOption(idx, e.target.value)}
                      placeholder={`Option ${idx + 1}`}
                      className="option-input"
                    />
                  ))}
                </div>
                <div className="form-group">
                  <label>Correct Answer:</label>
                  <select
                    value={questionForm.correct_option}
                    onChange={(e) => setQuestionForm({ ...questionForm, correct_option: parseInt(e.target.value) })}
                  >
                    {questionForm.options.map((opt, idx) => (
                      <option key={idx} value={idx}>Option {idx + 1}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="modal-footer">
                <button className="btn-cancel" onClick={() => setShowAddModal(false)}>Cancel</button>
                <button className="btn-confirm" onClick={confirmAddQuestion}>Add Question</button>
              </div>
            </div>
          </div>
        )}

        {/* Edit Question Modal */}
        {showEditModal && (
          <div className="modal-overlay" onClick={() => setShowEditModal(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h3>Edit Question</h3>
                <button className="modal-close" onClick={() => setShowEditModal(false)}>✕</button>
              </div>
              <div className="modal-body">
                <div className="form-group">
                  <label>Question Text:</label>
                  <textarea
                    value={questionForm.question_text}
                    onChange={(e) => setQuestionForm({ ...questionForm, question_text: e.target.value })}
                    rows="3"
                  />
                </div>
                <div className="form-group">
                  <label>Options:</label>
                  {questionForm.options.map((option, idx) => (
                    <input
                      key={idx}
                      type="text"
                      value={option}
                      onChange={(e) => updateOption(idx, e.target.value)}
                      placeholder={`Option ${idx + 1}`}
                      className="option-input"
                    />
                  ))}
                </div>
                <div className="form-group">
                  <label>Correct Answer:</label>
                  <select
                    value={questionForm.correct_option}
                    onChange={(e) => setQuestionForm({ ...questionForm, correct_option: parseInt(e.target.value) })}
                  >
                    {questionForm.options.map((opt, idx) => (
                      <option key={idx} value={idx}>Option {idx + 1}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="modal-footer">
                <button className="btn-cancel" onClick={() => setShowEditModal(false)}>Cancel</button>
                <button className="btn-confirm" onClick={confirmEditQuestion}>Update Question</button>
              </div>
            </div>
          </div>
        )}

        {/* Delete Confirmation Modal */}
        {showDeleteModal && (
          <div className="modal-overlay" onClick={() => setShowDeleteModal(false)}>
            <div className="modal-content small" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h3>Confirm Delete</h3>
                <button className="modal-close" onClick={() => setShowDeleteModal(false)}>✕</button>
              </div>
              <div className="modal-body">
                <p>Are you sure you want to delete this question?</p>
                <p className="warning-text">This action cannot be undone.</p>
              </div>
              <div className="modal-footer">
                <button className="btn-cancel" onClick={() => setShowDeleteModal(false)}>Cancel</button>
                <button className="btn-delete-confirm" onClick={confirmDeleteQuestion}>Delete</button>
              </div>
            </div>
          </div>
        )}

        {/* PDF Upload Modal */}
        {showUploadModal && (
          <div className="modal-overlay" onClick={() => setShowUploadModal(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h3>Upload Questions from PDF</h3>
                <button className="modal-close" onClick={() => setShowUploadModal(false)}>✕</button>
              </div>
              <div className="modal-body">
                <div className="upload-info">
                  <p><strong>PDF Format:</strong></p>
                  <pre className="format-example">
Q1. What is the capital of France?
A) London
B) Berlin
C) Paris
D) Madrid
Answer: C

Q2. Which planet is known as the Red Planet?
A) Venus
B) Mars
C) Jupiter
D) Saturn
Answer: B
                  </pre>
                </div>
                <div className="form-group">
                  <label>Select PDF File:</label>
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={(e) => setPdfFile(e.target.files[0])}
                    className="file-input"
                  />
                  {pdfFile && <p className="file-name">Selected: {pdfFile.name}</p>}
                </div>
              </div>
              <div className="modal-footer">
                <button className="btn-cancel" onClick={() => setShowUploadModal(false)}>Cancel</button>
                <button className="btn-confirm" onClick={handlePdfUpload} disabled={!pdfFile}>
                  Upload & Import
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default QuestionsManagement;
