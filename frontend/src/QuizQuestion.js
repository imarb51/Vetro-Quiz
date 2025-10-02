import React from 'react';

const QuizQuestion = ({ 
  question, 
  currentQuestionIndex, 
  totalQuestions, 
  selectedAnswer, 
  onAnswerSelect, 
  onNext, 
  onPrevious, 
  onSubmit,
  isLastQuestion,
  timeLeft
}) => {
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getTimerClass = () => {
    if (timeLeft <= 60) return 'timer warning';
    return 'timer';
  };

  const getTimerAriaLabel = () => {
    const time = formatTime(timeLeft);
    if (timeLeft <= 60) {
      return `Warning: Only ${time} remaining`;
    }
    return `Time remaining: ${time}`;
  };

  const progressPercentage = ((currentQuestionIndex + 1) / totalQuestions * 100).toFixed(1);

  return (
    <div className="quiz-card question-container slide-up">
      <div className="question-header">
        <div className="question-counter" role="status" aria-live="polite">
          Question {currentQuestionIndex + 1} of {totalQuestions}
        </div>
        <div 
          className={getTimerClass()}
          role="timer"
          aria-live="assertive"
          aria-label={getTimerAriaLabel()}
        >
          {formatTime(timeLeft)}
        </div>
      </div>

      <div className="progress-bar" role="progressbar" aria-valuenow={progressPercentage} aria-valuemin="0" aria-valuemax="100">
        <div 
          className="progress-fill"
          style={{ width: `${progressPercentage}%` }}
          aria-label={`Quiz progress: ${progressPercentage}% complete`}
        />
      </div>

      <h2 className="question-text" id={`question-${currentQuestionIndex}`}>
        {question.question_text}
      </h2>

      <fieldset className="options-list" aria-labelledby={`question-${currentQuestionIndex}`}>
        <legend className="sr-only">Choose your answer</legend>
        {question.options.map((option, index) => {
          const letter = String.fromCharCode(65 + index);
          return (
            <div key={index} className="option-item">
              <button
                className={`option-button ${selectedAnswer === index ? 'selected' : ''}`}
                onClick={() => onAnswerSelect(index)}
                data-letter={letter}
                aria-pressed={selectedAnswer === index}
                aria-describedby={`option-${index}-description`}
              >
                <span id={`option-${index}-description`}>
                  {option}
                </span>
              </button>
            </div>
          );
        })}
      </fieldset>

      <nav className="navigation-buttons" aria-label="Quiz navigation">
        <button 
          className="btn" 
          onClick={onPrevious} 
          disabled={currentQuestionIndex === 0}
          aria-label="Go to previous question"
        >
          ← Previous
        </button>
        
        <div>
          {isLastQuestion ? (
            <button 
              className="btn btn-success" 
              onClick={onSubmit}
              aria-label="Submit quiz and view results"
            >
              🏁 Submit Quiz
            </button>
          ) : (
            <button 
              className="btn" 
              onClick={onNext}
              aria-label="Go to next question"
            >
              Next →
            </button>
          )}
        </div>
      </nav>
    </div>
  );
};

export default QuizQuestion;