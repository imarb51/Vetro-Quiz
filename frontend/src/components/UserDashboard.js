import React, { useState, useEffect } from 'react';
import { quizAPI } from '../api';
import '../Dashboard.css';

const UserDashboard = ({ user, onLogout, onStartQuiz }) => {
  const [quizHistory, setQuizHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchQuizHistory();
  }, []);

  const fetchQuizHistory = async () => {
    try {
      setLoading(true);
      const historyData = await quizAPI.getUserQuizHistory();
      setQuizHistory(historyData.attempts || []);
    } catch (err) {
      setError('Failed to load quiz history');
      setQuizHistory([]);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = () => {
    if (quizHistory.length === 0) {
      return {
        totalAttempts: 0,
        averageScore: 0,
        bestScore: 0,
        lastAttempt: null
      };
    }

    const scores = quizHistory.map(attempt => attempt.percentage);
    const averageScore = scores.reduce((sum, score) => sum + score, 0) / scores.length;
    const bestScore = Math.max(...scores);
    const lastAttempt = quizHistory[0]; // Assuming sorted by date desc

    return {
      totalAttempts: quizHistory.length,
      averageScore: Math.round(averageScore),
      bestScore: Math.round(bestScore),
      lastAttempt
    };
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getScoreColor = (percentage) => {
    if (percentage >= 80) return '#84CC16'; // lime-500
    if (percentage >= 60) return '#F59E0B'; // amber-500
    return '#EF4444'; // red-500
  };

  const getPerformanceLevel = (percentage) => {
    if (percentage >= 90) return { text: 'Outstanding!', emoji: '🌟', color: '#10b981' };
    if (percentage >= 80) return { text: 'Excellent!', emoji: '⭐', color: '#84CC16' };
    if (percentage >= 70) return { text: 'Very Good!', emoji: '👍', color: '#3b82f6' };
    if (percentage >= 60) return { text: 'Good!', emoji: '👌', color: '#F59E0B' };
    return { text: 'Keep Practicing!', emoji: '💪', color: '#EF4444' };
  };

  const stats = calculateStats();

  return (
    <div className="dashboard-wrapper">
      <div className="dashboard-container">
        {/* Header Section */}
        <header className="dashboard-header-modern">
          <div className="header-content">
            <div className="user-info-section">
              <div className="user-avatar">
                {user.name.charAt(0).toUpperCase()}
              </div>
              <div className="user-greeting">
                <h1>Welcome back, <span className="user-name">{user.name}</span>!</h1>
                <p>Ready to test your knowledge? 🎯</p>
              </div>
            </div>
            <div className="header-actions">
              <button onClick={onStartQuiz} className="btn-start-quiz">
                <span>🚀</span> Take Quiz
              </button>
              <button onClick={onLogout} className="btn-logout">
                Logout
              </button>
            </div>
          </div>
        </header>

        {error && (
          <div className="alert-error">
            <span>⚠️</span> {error}
          </div>
        )}

        {/* Main Content Grid */}
        <div className="dashboard-grid">
          {/* Stats Cards */}
          <section className="stats-overview">
            <h2 className="section-title">
              <span className="title-icon">📊</span>
              Your Performance
            </h2>
            <div className="stats-cards">
              <div className="stat-card">
                <div className="stat-card-icon">🎲</div>
                <div className="stat-card-content">
                  <div className="stat-value">{stats.totalAttempts}</div>
                  <div className="stat-label">Quizzes Taken</div>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-card-icon">📈</div>
                <div className="stat-card-content">
                  <div className="stat-value">{stats.averageScore}%</div>
                  <div className="stat-label">Average Score</div>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-card-icon">🏆</div>
                <div className="stat-card-content">
                  <div className="stat-value">{stats.bestScore}%</div>
                  <div className="stat-label">Best Score</div>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-card-icon">
                  {stats.totalAttempts > 0 ? '🎯' : '🎪'}
                </div>
                <div className="stat-card-content">
                  <div className="stat-value">{stats.totalAttempts > 5 ? 'Pro' : 'Beginner'}</div>
                  <div className="stat-label">
                    {stats.totalAttempts > 0 ? 'Active Player' : 'New Player'}
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Recent Activity */}
          {stats.lastAttempt && (
            <section className="recent-activity-section">
              <h2 className="section-title">
                <span className="title-icon">🕐</span>
                Last Quiz Result
              </h2>
              <div className="recent-quiz-card">
                <div className="quiz-score-circle" style={{ 
                  background: `conic-gradient(${getScoreColor(stats.lastAttempt.percentage)} ${stats.lastAttempt.percentage}%, #e5e7eb ${stats.lastAttempt.percentage}%)`
                }}>
                  <div className="score-inner">
                    <span className="score-percentage">{stats.lastAttempt.percentage}%</span>
                  </div>
                </div>
                <div className="quiz-details">
                  <div className="detail-row">
                    <span className="detail-label">Score</span>
                    <span className="detail-value">
                      {stats.lastAttempt.score}/{stats.lastAttempt.total_questions} correct
                    </span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Date</span>
                    <span className="detail-value">{formatDate(stats.lastAttempt.attempt_date)}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Performance</span>
                    <span className="detail-value performance-badge" style={{ 
                      color: getPerformanceLevel(stats.lastAttempt.percentage).color 
                    }}>
                      {getPerformanceLevel(stats.lastAttempt.percentage).emoji} {getPerformanceLevel(stats.lastAttempt.percentage).text}
                    </span>
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* Quiz History */}
          <section className="history-section">
            <h2 className="section-title">
              <span className="title-icon">📚</span>
              Quiz History
            </h2>
            {loading ? (
              <div className="loading-spinner">
                <div className="spinner"></div>
                <p>Loading quiz history...</p>
              </div>
            ) : quizHistory.length > 0 ? (
              <div className="history-timeline">
                {quizHistory.slice(0, 10).map((attempt, index) => (
                  <div key={attempt.id || index} className="timeline-item">
                    <div className="timeline-marker" style={{ 
                      backgroundColor: getScoreColor(attempt.percentage) 
                    }}></div>
                    <div className="timeline-content">
                      <div className="timeline-header">
                        <span className="timeline-date">{formatDate(attempt.attempt_date)}</span>
                        <span className="timeline-score" style={{ 
                          backgroundColor: getScoreColor(attempt.percentage),
                          color: 'white'
                        }}>
                          {attempt.percentage}%
                        </span>
                      </div>
                      <div className="timeline-details">
                        {attempt.score}/{attempt.total_questions} questions correct
                      </div>
                    </div>
                  </div>
                ))}
                {quizHistory.length > 10 && (
                  <div className="timeline-more">
                    <p>+ {quizHistory.length - 10} more attempts</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-icon">🎪</div>
                <h3>No Quiz History Yet!</h3>
                <p>Take your first quiz to start tracking your progress.</p>
                <button onClick={onStartQuiz} className="btn-primary-large">
                  <span>🚀</span> Start First Quiz
                </button>
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
};

export default UserDashboard;