import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { adminAPI, authAPI } from '../api';
import './AdminDashboard.css';

function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeSection, setActiveSection] = useState('overview');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const data = await adminAPI.getStats();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await authAPI.logout();
    navigate('/admin');
  };

  const handleNavigation = (section) => {
    setActiveSection(section);
    if (section === 'users') {
      navigate('/admin/users');
    } else if (section === 'questions') {
      navigate('/admin/questions');
    }
  };

  if (loading) {
    return (
      <div className="admin-loading">
        <div className="spinner-large"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="admin-layout">
      {/* Sidebar */}
      <aside className={`admin-sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <h2>{sidebarOpen ? '📊 Admin Panel' : ''}</h2>
          <button 
            className="sidebar-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? '✕' : '☰'}
          </button>
        </div>

        <nav className="sidebar-nav">
          <button
            className={`nav-item ${activeSection === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveSection('overview')}
          >
            <span className="nav-icon">📈</span>
            {sidebarOpen && <span>Dashboard</span>}
          </button>

          <button
            className={`nav-item ${activeSection === 'users' ? 'active' : ''}`}
            onClick={() => handleNavigation('users')}
          >
            <span className="nav-icon">👥</span>
            {sidebarOpen && <span>Users</span>}
          </button>

          <button
            className={`nav-item ${activeSection === 'questions' ? 'active' : ''}`}
            onClick={() => handleNavigation('questions')}
          >
            <span className="nav-icon">❓</span>
            {sidebarOpen && <span>Questions</span>}
          </button>

          <div className="nav-divider"></div>

          <button
            className="nav-item"
            onClick={() => navigate('/dashboard')}
            
          >
            <span className="nav-icon">🏠</span>
            {sidebarOpen && <span>User Site</span>}
          </button>

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
          <h1>Dashboard Overview</h1>
          <button 
            className="mobile-menu-btn"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            ☰
          </button>
        </div>

        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon" style={{background: '#000000', color: '#ffffff'}}>
              👥
            </div>
            <div className="stat-content">
              <h3>Total Users</h3>
              <p className="stat-number">{stats?.total_users || 0}</p>
              <span className="stat-label">Registered users</span>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{background: '#333333', color: '#ffffff'}}>
              ❓
            </div>
            <div className="stat-content">
              <h3>Total Questions</h3>
              <p className="stat-number">{stats?.total_questions || 0}</p>
              <span className="stat-label">In question bank</span>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{background: '#666666', color: '#ffffff'}}>
              📝
            </div>
            <div className="stat-content">
              <h3>Quiz Attempts</h3>
              <p className="stat-number">{stats?.total_attempts || 0}</p>
              <span className="stat-label">Total submissions</span>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{background: '#999999', color: '#ffffff'}}>
              ⭐
            </div>
            <div className="stat-content">
              <h3>Average Score</h3>
              <p className="stat-number">{stats?.average_score || 0}%</p>
              <span className="stat-label">Overall performance</span>
            </div>
          </div>
        </div>

        <div className="quick-actions">
          <h2>Quick Actions</h2>
          <div className="action-buttons">
            <button 
              className="action-btn"
              onClick={() => handleNavigation('users')}
            >
              <span>👥</span>
              <div>
                <strong>Manage Users</strong>
                <p>View, edit, and delete users</p>
              </div>
            </button>

            <button 
              className="action-btn"
              onClick={() => handleNavigation('questions')}
            >
              <span>❓</span>
              <div>
                <strong>Manage Questions</strong>
                <p>Add, edit, or remove questions</p>
              </div>
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

export default AdminDashboard;
