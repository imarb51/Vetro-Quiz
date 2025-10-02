import React, { useState } from 'react';
import { GoogleLogin } from '@react-oauth/google';
import { authAPI } from '../api';

const Login = ({ onLogin, onSwitchToRegister, onSwitchToAdminLogin, setError }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

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
      onLogin(response.user);
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Login failed. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSuccess = async (credentialResponse) => {
    setLoading(true);
    setError('');

    try {
      const response = await authAPI.googleLogin(credentialResponse.credential);
      onLogin(response.user);
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Google login failed. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleError = () => {
    setError('Google login was cancelled or failed. Please try again.');
  };

  return (
    <div className="modern-auth-container">
      <div className="auth-background">
        <div className="auth-gradient"></div>
      </div>
      
      <div className="auth-content">
        <div className="auth-card">
          {/* Header */}
          <div className="auth-header">
            <div className="logo-section">
              <div className="logo">🧠</div>
              <h1>QuizMaster</h1>
            </div>
            <h2>Welcome Back!</h2>
            <p>Sign in to continue your learning journey</p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="modern-form">
            <div className="input-group">
              <div className="input-wrapper">
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="modern-input"
                  placeholder=" "
                  required
                />
                <label htmlFor="email" className="floating-label">
                  📧 Email Address
                </label>
              </div>
            </div>

            <div className="input-group">
              <div className="input-wrapper">
                <input
                  type={showPassword ? "text" : "password"}
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="modern-input"
                  placeholder=" "
                  required
                />
                <label htmlFor="password" className="floating-label">
                  🔒 Password
                </label>
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? '🙈' : '👁️'}
                </button>
              </div>
            </div>

            <button
              type="submit"
              className="modern-btn primary-btn"
              disabled={loading}
            >
              <span className="btn-content">
                {loading ? (
                  <>
                    <div className="spinner"></div>
                    Signing In...
                  </>
                ) : (
                  <>
                    🚀 Sign In
                  </>
                )}
              </span>
            </button>
          </form>

          {/* Divider */}
          <div className="modern-divider">
            <span>or continue with</span>
          </div>

          {/* Google Auth */}
          <div className="google-auth-section">
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={handleGoogleError}
              theme="outline"
              size="large"
              text="signin_with"
              shape="rectangular"
              width="100%"
            />
          </div>

          {/* Action Buttons */}
          <div className="auth-actions">
            <div className="action-group">
              <span>Don't have an account?</span>
              <button
                type="button"
                className="link-btn"
                onClick={onSwitchToRegister}
              >
                Create Account
              </button>
            </div>
            
            
          </div>

          
        </div>
      </div>
    </div>
  );
};

export default Login;