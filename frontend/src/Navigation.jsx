import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from './AuthContext';
import ThemeToggle from './ThemeToggle';
import './Navigation.css';

export default function Navigation({ onLogout }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '🏠' },
    { path: '/roadmap', label: 'Roadmap', icon: '🗺️' },
    { path: '/profile', label: 'Profile', icon: '👤' },
    { path: '/pomodoro', label: 'Pomodoro', icon: '🍅' }
  ];

  const handleLogout = () => {
    logout();
    if (onLogout) {
      onLogout();
    }
    navigate('/');
  };

  // Get dynamic username
  const getDynamicUsername = () => {
    return user?.username || user?.name || 'User';
  };

  return (
    <nav className="navigation-bar">
      <div className="nav-container">
        {/* Brand */}
        <div className="nav-brand" onClick={() => navigate('/dashboard')}>
          <h1>Pulse</h1>
        </div>

        {/* Navigation Links */}
        <div className="nav-links">
          {navItems.map((item) => (
            <button
              key={item.path}
              className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
              onClick={() => navigate(item.path)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </button>
          ))}
        </div>

        {/* Theme Toggle */}
        <ThemeToggle />

        {/* User Profile */}
        <div className="nav-profile">
          <div className="profile-dropdown">
            <div className="profile-trigger">
              <div className="profile-avatar">
                {user?.avatar ? (
                  <img src={user.avatar} alt="Profile" />
                ) : (
                  <div className="avatar-placeholder">
                    {getDynamicUsername().charAt(0).toUpperCase()}
                  </div>
                )}
              </div>
              <span className="profile-name">{getDynamicUsername()}</span>
            </div>
            <div className="dropdown-menu">
              <button onClick={() => navigate('/profile')}>
                <span className="menu-icon">👤</span>
                Profile
              </button>
              <button onClick={() => navigate('/settings')}>
                <span className="menu-icon">⚙️</span>
                Settings
              </button>
              <hr className="menu-divider" />
              <button onClick={handleLogout} className="logout-btn">
                <span className="menu-icon">🚪</span>
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}