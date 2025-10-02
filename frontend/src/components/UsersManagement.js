import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { adminAPI, authAPI } from '../api';
import './AdminDashboard.css';
import './UsersManagement.css';

function UsersManagement() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [selectedUser, setSelectedUser] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [userDetails, setUserDetails] = useState(null);
  const [editForm, setEditForm] = useState({ 
    email: '', 
    name: '', 
    phone: '', 
    address: '' 
  });
  const [message, setMessage] = useState({ type: '', text: '' });
  const navigate = useNavigate();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const data = await adminAPI.getAllUsers();
      setUsers(data.users);
    } catch (error) {
      showMessage('error', 'Failed to fetch users');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (user) => {
    setSelectedUser(user);
    setEditForm({ 
      email: user.email, 
      name: user.full_name || '', 
      phone: user.phone || '', 
      address: user.address || '' 
    });
    setShowEditModal(true);
  };

  const handleDelete = (user) => {
    setSelectedUser(user);
    setShowDeleteModal(true);
  };

  const handleViewDetails = async (user) => {
    try {
      const data = await adminAPI.getUserDetails(user.id);
      setUserDetails(data);
      setShowDetailsModal(true);
    } catch (error) {
      showMessage('error', 'Failed to fetch user details');
    }
  };

  const confirmEdit = async () => {
    try {
      const updates = {};
      if (editForm.email && editForm.email !== selectedUser.email) {
        updates.email = editForm.email;
      }
      if (editForm.name && editForm.name !== selectedUser.full_name) {
        updates.name = editForm.name;
      }
      if (editForm.phone !== (selectedUser.phone || '')) {
        updates.phone = editForm.phone;
      }
      if (editForm.address !== (selectedUser.address || '')) {
        updates.address = editForm.address;
      }

      if (Object.keys(updates).length === 0) {
        showMessage('warning', 'No changes to update');
        return;
      }

      await adminAPI.updateUser(selectedUser.id, updates);
      showMessage('success', 'User updated successfully');
      setShowEditModal(false);
      fetchUsers();
    } catch (error) {
      showMessage('error', error.response?.data?.detail || 'Failed to update user');
    }
  };

  const confirmDelete = async () => {
    try {
      await adminAPI.deleteUser(selectedUser.id);
      showMessage('success', 'User deleted successfully');
      setShowDeleteModal(false);
      fetchUsers();
    } catch (error) {
      showMessage('error', 'Failed to delete user');
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

  if (loading) {
    return (
      <div className="admin-loading">
        <div className="spinner-large"></div>
        <p>Loading users...</p>
      </div>
    );
  }

  return (
    <div className="admin-layout">
      {/* Sidebar */}
      <aside className={`admin-sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <h2>📊 Admin Panel</h2>
          <button className="sidebar-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>
            {sidebarOpen ? '✕' : '☰'}
          </button>
        </div>

        <nav className="sidebar-nav">
          <button className="nav-item" onClick={() => navigate('/admin/dashboard')}>
            <span className="nav-icon">📈</span>
            {sidebarOpen && <span>Dashboard</span>}
          </button>

          <button className="nav-item active">
            <span className="nav-icon">👥</span>
            {sidebarOpen && <span>Users</span>}
          </button>

          <button className="nav-item" onClick={() => navigate('/admin/questions')}>
            <span className="nav-icon">❓</span>
            {sidebarOpen && <span>Questions</span>}
          </button>

          <div className="nav-divider"></div>

          <button className="nav-item logout" onClick={handleLogout}>
            <span className="nav-icon">🚪</span>
            {sidebarOpen && <span>Logout</span>}
          </button>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="admin-main">
        <div className="admin-header">
          <h1>User Management</h1>
          <button className="mobile-menu-btn" onClick={() => setSidebarOpen(!sidebarOpen)}>
            ☰
          </button>
        </div>

        {message.text && (
          <div className={`alert alert-${message.type}`}>
            {message.text}
          </div>
        )}

        <div className="users-container">
          <div className="users-header">
            <h2>All Users ({users.length})</h2>
          </div>

          <div className="table-container">
            <table className="users-table">
              <thead>
                <tr>
                  
                  <th>Email</th>
                  <th>Name</th>
                  <th>Registered</th>
                  <th>Attempts</th>
                  <th>Avg Score</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id}>
                    
                    <td>{user.email}</td>
                    <td>{user.full_name}</td>
                    <td>{new Date(user.created_at).toLocaleDateString()}</td>
                    <td>{user.total_attempts}</td>
                    <td>
                      <span className={`score-badge ${user.average_score >= 70 ? 'good' : user.average_score >= 50 ? 'medium' : 'low'}`}>
                        {user.average_score}%
                      </span>
                    </td>
                    <td>
                      <div className="action-buttons-group">
                       
                        <button className="btn-edit" onClick={() => handleEdit(user)} title="Edit User">
                          ✏️
                        </button>
                        <button className="btn-delete" onClick={() => handleDelete(user)} title="Delete User">
                          🗑️
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Edit Modal */}
        {showEditModal && (
          <div className="modal-overlay" onClick={() => setShowEditModal(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h3>Edit User Information</h3>
                <button className="modal-close" onClick={() => setShowEditModal(false)}>✕</button>
              </div>
              <div className="modal-body">
                <div className="form-group">
                  <label>Email</label>
                  <input
                    type="email"
                    className="modern-input"
                    value={editForm.email}
                    onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Full Name</label>
                  <input
                    type="text"
                    className="modern-input"
                    value={editForm.name}
                    onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                    placeholder="Enter full name"
                  />
                </div>
                <div className="form-group">
                  <label>Phone Number</label>
                  <input
                    type="tel"
                    className="modern-input"
                    value={editForm.phone}
                    onChange={(e) => setEditForm({ ...editForm, phone: e.target.value })}
                    placeholder="Enter phone number"
                  />
                </div>
                <div className="form-group">
                  <label>Address</label>
                  <textarea
                    className="modern-input"
                    value={editForm.address}
                    onChange={(e) => setEditForm({ ...editForm, address: e.target.value })}
                    placeholder="Enter address"
                    rows="3"
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button className="btn-cancel" onClick={() => setShowEditModal(false)}>Cancel</button>
                <button className="btn-save" onClick={confirmEdit}>Save Changes</button>
              </div>
            </div>
          </div>
        )}

        {/* Delete Confirmation Modal */}
        {showDeleteModal && (
          <div className="modal-overlay" onClick={() => setShowDeleteModal(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h3>Confirm Delete</h3>
                <button className="modal-close" onClick={() => setShowDeleteModal(false)}>✕</button>
              </div>
              <div className="modal-body">
                <p>Are you sure you want to delete user <strong>{selectedUser?.email}</strong>?</p>
                <p className="warning-text">This action cannot be undone and will also delete all quiz attempts.</p>
              </div>
              <div className="modal-footer">
                <button className="btn-cancel" onClick={() => setShowDeleteModal(false)}>Cancel</button>
                <button className="btn-delete" onClick={confirmDelete}>Delete User</button>
              </div>
            </div>
          </div>
        )}

        {/* User Details Modal */}
        {showDetailsModal && userDetails && (
          <div className="modal-overlay" onClick={() => setShowDetailsModal(false)}>
            <div className="modal-content large" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h3>User Details</h3>
                <button className="modal-close" onClick={() => setShowDetailsModal(false)}>✕</button>
              </div>
              <div className="modal-body">
                <div className="user-info">
                  <h4>Profile Information</h4>
                  <p><strong>Email:</strong> {userDetails.user.email}</p>
                  <p><strong>Name:</strong> {userDetails.user.full_name}</p>
                  <p><strong>Registered:</strong> {new Date(userDetails.user.created_at).toLocaleString()}</p>
                  <p><strong>Status:</strong> {userDetails.user.is_active ? '✅ Active' : '❌ Inactive'}</p>
                </div>

                <div className="quiz-history">
                  <h4>Quiz History ({userDetails.quiz_history.length} attempts)</h4>
                  {userDetails.quiz_history.length > 0 ? (
                    <div className="history-table">
                      <table>
                        <thead>
                          <tr>
                            <th>Date</th>
                            <th>Score</th>
                            <th>Percentage</th>
                          </tr>
                        </thead>
                        <tbody>
                          {userDetails.quiz_history.map((attempt) => (
                            <tr key={attempt.id}>
                              <td>{new Date(attempt.completed_at).toLocaleString()}</td>
                              <td>{attempt.score}/{attempt.total_questions}</td>
                              <td>
                                <span className={`score-badge ${attempt.percentage >= 70 ? 'good' : attempt.percentage >= 50 ? 'medium' : 'low'}`}>
                                  {attempt.percentage}%
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <p className="no-data">No quiz attempts yet</p>
                  )}
                </div>
              </div>
              <div className="modal-footer">
                <button className="btn-cancel" onClick={() => setShowDetailsModal(false)}>Close</button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default UsersManagement;
