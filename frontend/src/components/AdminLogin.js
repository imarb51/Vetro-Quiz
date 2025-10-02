import React, { useState } from 'react';
import { authAPI } from '../api';

const AdminLogin = ({ onLogin, onSwitchToUserLogin, setError }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError(''); // Clear error when user types
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await authAPI.login(formData);
      
      // Check if user is admin
      if (!response.user.is_admin) {
        setError('Access denied. Admin privileges required.');
        return;
      }
      
      onLogin(response.user);
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Admin login failed. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="quiz-card admin-login-card">
        <div className="quiz-header">
          <h1 className="quiz-title">👑 Admin Portal</h1>
          <p className="quiz-description">
            Administrative access required. Please enter your admin credentials.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="admin-email" className="form-label">
              Admin Email Address
            </label>
            <input
              type="email"
              id="admin-email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="form-input"
              placeholder="Enter admin email"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="admin-password" className="form-label">
              Admin Password
            </label>
            <input
              type="password"
              id="admin-password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="form-input"
              placeholder="Enter admin password"
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary admin-btn"
            disabled={loading}
          >
            {loading ? 'Authenticating...' : '🔐 Admin Sign In'}
          </button>
        </form>

        <div className="auth-switch">
          <p>Not an admin?</p>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onSwitchToUserLogin}
          >
            👤 User Login
          </button>
        </div>

        <div className="admin-demo">
          <div className="demo-info">
            <h4>🧪 Demo Admin Account</h4>
            <p><strong>Email:</strong> admin@quiz.com</p>
            <p><strong>Password:</strong> admin123</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminLogin;