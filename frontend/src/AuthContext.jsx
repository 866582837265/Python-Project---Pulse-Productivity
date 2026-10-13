import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from './api';
import { useStreak } from './contexts/StreakContext';

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

  // Load user from localStorage on app start
  useEffect(() => {
    const token = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    
    if (token && savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setUser(userData);
        // Refresh user data from server
        refreshUserData();
      } catch (error) {
        console.error('Failed to parse saved user data:', error);
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

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
    try {
      const response = await api.login(credentials);
      const { token, user: userData, streak } = response;
      
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
      
      // Update streak context if available
      if (streak && window.streakContext) {
        window.streakContext.setStreak(streak);
      }
      
      // Refresh with complete profile data
      await refreshUserData();
      
      return response;
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const updateUser = (updates) => {
    const updatedUser = { ...user, ...updates };
    setUser(updatedUser);
    localStorage.setItem('user', JSON.stringify(updatedUser));
  };

  const value = {
    user,
    login,
    logout,
    updateUser,
    refreshUserData,
    loading,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};