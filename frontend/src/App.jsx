import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { useState, useEffect } from "react";
import axios from "axios";
import { API_BASE_URL } from "./config";
import { ThemeProvider } from "./ThemeContext";
import { AuthProvider } from "./AuthContext";
import { StreakProvider } from "./contexts/StreakContext";
import ErrorBoundary from "./ErrorBoundary";
import useTheme from "./hooks/useTheme";
import Login from "./Login";
import Register from "./Register";
import Dashboard from "./Dashboard";
import PomodoroTimer from "./PomodoroTimer";
import PomodoroPage from "./PomodoroPage";
import TopicQuestions from "./TopicQuestions";
import PracticeQuestions from "./PracticeQuestions";
import EnhancedPractice from "./EnhancedPractice";
import QuestionsPage from "./QuestionsPage";
import RoadmapUI from "./RoadmapUI";
import UserProfile from "./UserProfile";
import CodingProfiles from "./CodingProfiles";

function AppContent() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Initialize dark theme
  useTheme();

  // Check for existing token on app load
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const token = localStorage.getItem("token");
        const storedUser = localStorage.getItem("user");
        
        if (token && storedUser) {
          // Verify token is still valid by making a request to dashboard
          const response = await axios.get(`${API_BASE_URL}/api/dashboard`, {
            headers: {
              Authorization: `Bearer ${token}`
            }
          });
          
          if (response.data) {
            setUser(JSON.parse(storedUser));
          } else {
            // Token is invalid, clear storage
            localStorage.removeItem("token");
            localStorage.removeItem("user");
          }
        }
      } catch (error) {
        console.log("No valid session found");
        // Clear invalid token
        localStorage.removeItem("token");
        localStorage.removeItem("user");
      } finally {
        setLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  // Handle login success
  const handleLogin = (userData) => {
    setUser(userData);
  };

  // Handle registration success
  const handleRegister = (userData) => {
    console.log("Registration completed for:", userData);
  };

  // Handle logout
  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
  };

  // Show loading spinner while checking auth status
  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)',
        color: '#fff'
      }}>
        <div>Loading...</div>
      </div>
    );
  }

  return (
    <Router>
      <Routes>
        {/* Login Page - Default route */}
        <Route
          path="/"
          element={
            !user ? (
              <Login onLogin={handleLogin} />
            ) : (
              <Navigate to="/dashboard" replace />
            )
          }
        />

        {/* Register Page */}
        <Route
          path="/register"
          element={
            !user ? (
              <Register onRegister={handleRegister} />
            ) : (
              <Navigate to="/dashboard" replace />
            )
          }
        />

        {/* Dashboard Page - Protected route */}
        <Route
          path="/dashboard"
          element={
            user ? (
              <Dashboard user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />

        {/* Pomodoro Timer Page - Protected route */}
        <Route
          path="/pomodoro"
          element={
            user ? (
              <PomodoroPage />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />

        {/* Roadmap Page - Protected route */}
        <Route
          path="/roadmap"
          element={
            user ? (
              <RoadmapUI />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />

        {/* Topic Questions Page - Protected route */}
        <Route
          path="/roadmap/topic/:topicId"
          element={
            user ? (
              <TopicQuestions />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />

        {/* Practice Questions Page - Protected route */}
        <Route
          path="/practice/:topicId"
          element={
            user ? (
              <EnhancedPractice />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />

        {/* User Profile Page - Protected route */}
        <Route
          path="/profile"
          element={
            user ? (
              <UserProfile user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />

        {/* Coding Profiles Page - Protected route */}
        <Route
          path="/coding-profiles"
          element={
            user ? (
              <CodingProfiles />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />

        {/* Questions Page - Protected route */}
        <Route
          path="/questions"
          element={
            user ? (
              <QuestionsPage />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />

        {/* Catch all route - redirect to login */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <AuthProvider>
          <StreakProvider>
            <AppContent />
          </StreakProvider>
        </AuthProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;