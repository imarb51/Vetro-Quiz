import React from 'react';

const StartScreen = ({ onStartQuiz, questionsCount, user, onBackToDashboard }) => {
  return (
    <div className="quiz-card start-screen fade-in">
      {user && onBackToDashboard && (
        <div className="user-header">
          <div className="user-info">
            <span>Welcome, {user.name}! {user.is_admin && '👑'}</span>
          </div>
          <button onClick={onBackToDashboard} className="btn-secondary">
            ← Back to Dashboard
          </button>
        </div>
      )}
      
      <h1>🧠 Online Quiz Challenge</h1>
      <p>Test your knowledge with our interactive quiz and challenge yourself!</p>
      
      <div className="quiz-stats">
        <div className="stat-item">
          <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📊</div>
          <div><strong>Questions:</strong> {questionsCount || 8}</div>
        </div>
        <div className="stat-item">
          <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>⏱️</div>
          <div><strong>Time Limit:</strong> 5 minutes</div>
        </div>
        <div className="stat-item">
          <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🎯</div>
          <div><strong>Goal:</strong> Best score possible</div>
        </div>
      </div>
      
      <p style={{ 
        fontSize: 'clamp(0.9rem, 2vw, 1.1rem)', 
        color: 'var(--gray-500)',
        marginBottom: 'var(--space-xl)'
      }}>
        Navigate through questions using Next/Previous buttons. You can change your answers before submitting. 
        The timer will automatically submit your quiz when it reaches zero.
      </p>
      
      <button 
        className="btn" 
        onClick={onStartQuiz}
        aria-label="Start the quiz challenge"
      >
        🚀 Start Quiz
      </button>
    </div>
  );
};

export default StartScreen;