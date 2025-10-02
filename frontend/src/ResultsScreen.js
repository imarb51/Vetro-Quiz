import React from 'react';

const ResultsScreen = ({ results, onRetakeQuiz, onBackToDashboard }) => {
  const { score, total_questions, percentage, results: questionResults } = results;

  const getResultStatus = (result) => {
    if (result.user_answer === null || result.user_answer === undefined) {
      return 'unanswered';
    }
    return result.is_correct ? 'correct' : 'incorrect';
  };

  const getResultText = (result) => {
    const correctAnswer = result.options[result.correct_option];
    const userAnswer = result.user_answer !== null ? result.options[result.user_answer] : 'Not answered';
    
    if (result.user_answer === null || result.user_answer === undefined) {
      return (
        <>
          <span>❌ Not answered</span>
          <br />
          <span>✅ Correct: {correctAnswer}</span>
        </>
      );
    }
    
    if (result.is_correct) {
      return (
        <>
          <span>✅ Your answer: {userAnswer}</span>
        </>
      );
    } else {
      return (
        <>
          <span>❌ Your answer: {userAnswer}</span>
          <br />
          <span>✅ Correct: {correctAnswer}</span>
        </>
      );
    }
  };

  const getGradeText = () => {
    if (percentage >= 90) return 'Excellent! 🏆';
    if (percentage >= 80) return 'Great job! 🎉';
    if (percentage >= 70) return 'Good work! 👍';
    if (percentage >= 60) return 'Not bad! 👌';
    return 'Keep studying! 📚';
  };

  const getPerformanceEmoji = () => {
    if (percentage >= 90) return '🏆';
    if (percentage >= 80) return '🎉';
    if (percentage >= 70) return '👍';
    if (percentage >= 60) return '👌';
    return '📚';
  };

  const correctCount = questionResults.filter(r => r.is_correct).length;
  const incorrectCount = questionResults.filter(r => !r.is_correct && r.user_answer !== null).length;
  const unansweredCount = questionResults.filter(r => r.user_answer === null).length;

  return (
    <div className="quiz-card results-screen fade-in">
      <h1>🎯 Quiz Results</h1>
      
      <div className="score-display">
        <div className="performance-emoji">{getPerformanceEmoji()}</div>
        <div className="score-number" aria-label={`You scored ${score} out of ${total_questions} questions correct`}>
          {score}/{total_questions}
        </div>
        <div className="score-percentage">
          {percentage}% - {getGradeText()}
        </div>
      </div>

      {/* Performance Summary */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', 
        gap: 'var(--space-md)', 
        marginBottom: 'var(--space-xl)',
        textAlign: 'center'
      }}>
        <div style={{ 
          background: 'rgba(16, 185, 129, 0.1)', 
          padding: 'var(--space-md)', 
          borderRadius: 'var(--radius-lg)',
          border: '2px solid rgba(16, 185, 129, 0.2)'
        }}>
          <div style={{ fontSize: '1.5rem', color: '#10b981' }}>✅</div>
          <div><strong>{correctCount}</strong></div>
          <div style={{ fontSize: '0.9rem', color: 'var(--gray-600)' }}>Correct</div>
        </div>
        <div style={{ 
          background: 'rgba(239, 68, 68, 0.1)', 
          padding: 'var(--space-md)', 
          borderRadius: 'var(--radius-lg)',
          border: '2px solid rgba(239, 68, 68, 0.2)'
        }}>
          <div style={{ fontSize: '1.5rem', color: '#ef4444' }}>❌</div>
          <div><strong>{incorrectCount}</strong></div>
          <div style={{ fontSize: '0.9rem', color: 'var(--gray-600)' }}>Incorrect</div>
        </div>
        <div style={{ 
          background: 'rgba(245, 158, 11, 0.1)', 
          padding: 'var(--space-md)', 
          borderRadius: 'var(--radius-lg)',
          border: '2px solid rgba(245, 158, 11, 0.2)'
        }}>
          <div style={{ fontSize: '1.5rem', color: '#f59e0b' }}>⏭️</div>
          <div><strong>{unansweredCount}</strong></div>
          <div style={{ fontSize: '0.9rem', color: 'var(--gray-600)' }}>Skipped</div>
        </div>
      </div>

      <section className="results-list" aria-label="Detailed question results">
        <h3 style={{ marginBottom: 'var(--space-lg)', color: 'var(--gray-800)' }}>
          📋 Detailed Results
        </h3>
        {questionResults.map((result, index) => (
          <article 
            key={result.id} 
            className={`result-item ${getResultStatus(result)}`}
            role="region"
            aria-label={`Question ${index + 1} result`}
          >
            <div className="result-question">
              <strong>Q{index + 1}:</strong> {result.question_text}
            </div>
            <div className="result-answer">
              {getResultText(result)}
            </div>
          </article>
        ))}
      </section>

      <div style={{ 
        display: 'flex', 
        gap: 'var(--space-md)', 
        flexWrap: 'wrap',
        justifyContent: 'center'
      }}>
        <button 
          className="btn btn-secondary" 
          onClick={onBackToDashboard}
          aria-label="Return to dashboard"
        >
          🏠 Back to Dashboard
        </button>
        <button 
          className="btn" 
          onClick={onRetakeQuiz}
          aria-label="Start a new quiz"
        >
          🔄 Take Quiz Again
        </button>
      </div>
    </div>
  );
};

export default ResultsScreen;