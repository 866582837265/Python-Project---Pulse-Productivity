# Dynamic Username Implementation Example

## Overview
This example shows how to implement truly dynamic username display that updates automatically when users log in and reflects the actual logged-in user's data.

## Key Components

### 1. AuthContext (Authentication Context)
```jsx
// AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from './api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Auto-refresh user data from server
  const refreshUserData = async () => {
    try {
      const profileData = await api.getUserProfile();
      const updatedUser = {
        id: profileData.id || user?.id,
        email: profileData.email,
        username: profileData.username || profileData.name,
        name: profileData.name || profileData.username,
        avatar: profileData.avatar,
        skill_level: profileData.skill_level,
        assessment_taken: profileData.assessment_taken
      };
      setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));
    } catch (error) {
      console.error('Failed to refresh user data:', error);
    }
  };

  const login = async (credentials) => {
    const response = await api.login(credentials);
    const { token, user: userData } = response;
    
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
    
    // Refresh with complete profile data
    await refreshUserData();
    
    return response;
  };

  const updateUser = (updates) => {
    const updatedUser = { ...user, ...updates };
    setUser(updatedUser);
    localStorage.setItem('user', JSON.stringify(updatedUser));
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, updateUser, refreshUserData }}>
      {children}
    </AuthContext.Provider>
  );
};
```

### 2. Dynamic Username in Profile Component
```jsx
// UserProfile.jsx
import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';

export default function UserProfile() {
  const { user, updateUser, refreshUserData } = useAuth();
  const [profileData, setProfileData] = useState({});

  // Get dynamic username with fallback
  const getDynamicUsername = () => {
    return user?.username || user?.name || profileData?.username || profileData?.name || 'User';
  };

  const loadUserProfile = async () => {
    try {
      const data = await api.getUserProfile();
      setProfileData(data);
      
      // Update auth context with latest user data
      updateUser({
        username: data.username || data.name,
        name: data.name || data.username,
        email: data.email,
        avatar: data.avatar,
        skill_level: data.skill_level,
        assessment_taken: data.assessment_taken
      });
    } catch (error) {
      console.error('Failed to load profile:', error);
    }
  };

  useEffect(() => {
    loadUserProfile();
  }, []);

  return (
    <div className="profile-container">
      {/* Header with Dynamic Username */}
      <div className="profile-header">
        <h1 className="profile-name">{getDynamicUsername()}</h1>
        <p className="profile-email">{user?.email || profileData?.email}</p>
      </div>

      {/* Profile Information */}
      <div className="profile-info">
        <div className="info-item">
          <span className="info-label">Username</span>
          <span className="info-value">{getDynamicUsername()}</span>
        </div>
        <div className="info-item">
          <span className="info-label">Email</span>
          <span className="info-value">{user?.email || profileData?.email}</span>
        </div>
      </div>
    </div>
  );
}
```

### 3. App Component Integration
```jsx
// App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './AuthContext';
import UserProfile from './UserProfile';
import Login from './Login';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/profile" element={<UserProfile />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
```

### 4. Login Component with Context
```jsx
// Login.jsx
import React, { useState } from 'react';
import { useAuth } from './AuthContext';
import { useNavigate } from 'react-router-dom';

export default function Login() {
  const [credentials, setCredentials] = useState({ email: '', password: '' });
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await login(credentials);
      navigate('/profile'); // Username will be automatically updated
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={credentials.email}
        onChange={(e) => setCredentials({...credentials, email: e.target.value})}
        placeholder="Email"
      />
      <input
        type="password"
        value={credentials.password}
        onChange={(e) => setCredentials({...credentials, password: e.target.value})}
        placeholder="Password"
      />
      <button type="submit">Login</button>
    </form>
  );
}
```

## Key Features

### ✅ Truly Dynamic Username
- Fetches from authentication context
- Updates automatically on login
- Reflects current logged-in user
- No hardcoded values

### ✅ Real-time Updates
- Context updates when profile data changes
- Automatic refresh from server
- Consistent across all components
- Persists in localStorage

### ✅ Fallback Strategy
```jsx
const getDynamicUsername = () => {
  return user?.username || user?.name || profileData?.username || profileData?.name || 'User';
};
```

### ✅ Auto-Refresh on Login
```jsx
const login = async (credentials) => {
  const response = await api.login(credentials);
  setUser(response.user);
  
  // Automatically refresh with complete profile data
  await refreshUserData();
  
  return response;
};
```

## Usage Examples

### Display Username in Header
```jsx
<h1 className="profile-name">{getDynamicUsername()}</h1>
```

### Display Username in Navigation
```jsx
<span className="profile-name">{getDynamicUsername()}</span>
```

### Display Username in Avatar Placeholder
```jsx
<div className="avatar-placeholder">
  {getDynamicUsername().charAt(0).toUpperCase()}
</div>
```

## Benefits

1. **No Static Data**: Username always reflects current user
2. **Automatic Updates**: Changes when user logs in/out
3. **Consistent Display**: Same username across all components
4. **Error Handling**: Graceful fallbacks for missing data
5. **Performance**: Cached in context, minimal API calls

## Testing the Implementation

1. **Login Test**: Login with different users, verify username changes
2. **Refresh Test**: Refresh page, verify username persists
3. **Navigation Test**: Navigate between pages, verify consistency
4. **Logout Test**: Logout and login as different user, verify update

This implementation ensures the username is never static and always reflects the actual logged-in user's data!