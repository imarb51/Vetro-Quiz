import React, { useState } from 'react';
import { GoogleLogin } from '@react-oauth/google';
import { authAPI } from '../api';

const Register = ({ onRegister, onSwitchToLogin, setError }) => {
  const [formData, setFormData] = useState({
    email: '',
    name: '',
    password: '',
    confirmPassword: '',
    phone: '',
    address: ''
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError(''); // Clear error when user types
  };

  const validateForm = () => {
    if (!formData.email || !formData.name || !formData.password) {
      setError('Please fill in all required fields.');
      return false;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return false;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match.');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError('');

    try {
      const registrationData = {
        email: formData.email,
        name: formData.name,
        password: formData.password,
        phone: formData.phone || null,
        address: formData.address || null
      };

      await authAPI.register(registrationData);
      
      // Auto-login after successful registration
      const loginResponse = await authAPI.login({
        email: formData.email,
        password: formData.password
      });
      
      onRegister(loginResponse.user);
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Registration failed. Please try again.';
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
      onRegister(response.user);
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Google registration failed. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleError = () => {
    setError('Google registration was cancelled or failed. Please try again.');
  };

  return (
    <div className="modern-auth-container">
      <div className="auth-background">
        <div className="auth-gradient"></div>
      </div>
      
      <div className="auth-content">
        <div className="auth-card">
          <div className="auth-header">
            <div className="logo-section">
              <div className="logo">🚀</div>
              <h1>QuizMaster</h1>
            </div>
            <h2>Join Us Today!</h2>
            <p>Create your account and start your learning journey</p>
          </div>

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
                  📧 Email Address *
                </label>
              </div>
            </div>

            <div className="input-group">
              <div className="input-wrapper">
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className="modern-input"
                  placeholder=" "
                  required
                />
                <label htmlFor="name" className="floating-label">
                  👤 Full Name *
                </label>
              </div>
            </div>

            <div className="input-group">
              <div className="input-wrapper">
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="modern-input"
                  placeholder=" "
                  required
                />
                <label htmlFor="password" className="floating-label">
                  🔒 Password *
                </label>
              </div>
            </div>

            <div className="input-group">
              <div className="input-wrapper">
                <input
                  type="password"
                  id="confirmPassword"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  className="modern-input"
                  placeholder=" "
                  required
                />
                <label htmlFor="confirmPassword" className="floating-label">
                  🔐 Confirm Password *
                </label>
              </div>
            </div>

            <div className="input-group">
              <div className="input-wrapper">
                <input
                  type="tel"
                  id="phone"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  className="modern-input"
                  placeholder=" "
                />
                <label htmlFor="phone" className="floating-label">
                  📱 Phone Number
                </label>
              </div>
            </div>

            <div className="input-group">
              <div className="input-wrapper">
                <textarea
                  id="address"
                  name="address"
                  value={formData.address}
                  onChange={handleChange}
                  className="modern-input"
                  placeholder=" "
                  rows="3"
                />
                <label htmlFor="address" className="floating-label">
                  🏠 Address
                </label>
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
                    Creating Account...
                  </>
                ) : (
                  <>
                    🚀 Create Account
                  </>
                )}
              </span>
            </button>
          </form>

          <div className="modern-divider">
            <span>or continue with</span>
          </div>

          <div className="google-auth-section">
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={handleGoogleError}
              theme="outline"
              size="large"
              text="signup_with"
              shape="rectangular"
              width="100%"
            />
          </div>

          <div className="auth-actions">
            <div className="action-group">
              <span>Already have an account?</span>
              <button
                type="button"
                className="link-btn"
                onClick={onSwitchToLogin}
              >
                Sign In
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;