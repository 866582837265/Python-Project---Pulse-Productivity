import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { API_BASE_URL } from "./config";
import { DISPLAY_STREAK, STREAK_DATA } from "./constants/streakConstants";
import SkillAssessment from "./SkillAssessment";
import StreakTracker from "./StreakTracker";
import RoadmapView from "./RoadmapView";
import DuolingoRoadmap from "./DuolingoRoadmap";
import CodingProfiles from "./CodingProfiles";
import "./Dashboard.css";
import "./EnhancedStreaks.css";

export default function Dashboard({ user: propUser, onLogout }) {
  const [showRoadmap, setShowRoadmap] = useState(false);
  const [showAssessment, setShowAssessment] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [user, setUser] = useState(propUser || { name: "User", avatar: null });
  const [assessmentTaken, setAssessmentTaken] = useState(false);
  const [streakData, setStreakData] = useState({
    loginStreak: 0,
    pomodoroStreak: 0,
    totalSessions: 0,
    completedTopics: 0
  });
  const [pomodoroData, setPomodoroData] = useState({
    sessions_today: 0,
    total_sessions: 0,
    avg_session_time: 25,
    focus_score: 0
  });
  const [roadmapProgress, setRoadmapProgress] = useState({
    progress_percentage: 0,
    completed_topics: 0,
    total_topics: 0
  });
  const [codingPlatforms, setCodingPlatforms] = useState({});
  const [mlData, setMlData] = useState({
    skillLevel: null,
    learningStyle: null,
    streakRisk: null,
    personalizedRoadmap: null,
    benchmarks: null
  });
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Clear any previous user data to ensure isolation
    setUser({ name: "User", avatar: null });
    setAssessmentTaken(false);
    setMlData({
      skillLevel: null,
      learningStyle: null,
      streakRisk: null,
      personalizedRoadmap: null,
      benchmarks: null
    });
    
    // Clear localStorage data from previous sessions
    const currentToken = localStorage.getItem('token');
    if (!currentToken) {
      navigate("/");
      return;
    }
    
    console.log("[DASHBOARD] Starting fresh data load for current user");
    
    // Fetch user data first, then ML predictions
    const loadData = async () => {
      try {
        await fetchUserData();
        await fetchAssessmentStatus();
        await fetchMLPredictions();
      } catch (error) {
        console.error('Error loading dashboard data:', error);
        setLoading(false);
      }
    };
    
    loadData();
  }, []);

  const fetchUserData = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        console.log("[DASHBOARD] No token found, redirecting to login");
        navigate("/");
        return;
      }

      console.log("[DASHBOARD] Fetching user-specific dashboard data...");
      
      // Fetch enhanced dashboard data for current user
      const dashboardResponse = await axios.get(`${API_BASE_URL}/api/dashboard`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      console.log("[DASHBOARD] Dashboard response:", dashboardResponse.data);
      
      if (dashboardResponse.data) {
        const data = dashboardResponse.data;
        
        // Update user data with current user's information
        setUser({
          name: data.name,
          predicted_level: data.predicted_level,
          assessment_taken: data.assessment_taken || false
        });
        
        // Set assessment status from backend
        setAssessmentTaken(data.assessment_taken || false);
        
        console.log(`[DASHBOARD] User ${data.name} - Assessment taken: ${data.assessment_taken}`);
        
        // Update dynamic data with current user's data
        setPomodoroData({
          sessions_today: data.today_sessions || 0,
          total_sessions: data.pomodoro_count || 0,
          avg_session_time: 25,
          focus_score: Math.min(50 + (data.pomodoro_count * 5), 100)
        });
        
        setStreakData({
          loginStreak: data.login_streak_days || 0,
          pomodoroStreak: data.today_sessions || 0,
          totalSessions: data.pomodoro_count || 0,
          completedTopics: 0,
          loginDaysTotal: data.login_days_total || 0,
          lastLogin: data.last_login_at,
          motivationalQuote: data.motivational_quote
        });
        
        setRoadmapProgress({
          progress_percentage: data.roadmap_progress_percent || 0,
          completed_topics: 0,
          total_topics: 0
        });
        
        setCodingPlatforms(data.coding_platform_stats || {});
        
        // Update ML data with current user's level
        if (data.predicted_level) {
          setMlData(prev => ({
            ...prev,
            skillLevel: data.predicted_level
          }));
        }
        
        console.log("[DASHBOARD] User data loaded successfully");
      } else {
        console.error("[DASHBOARD] API returned no data");
      }
    } catch (error) {
      console.error("[DASHBOARD] Failed to fetch user data:", error);
      if (error.response?.status === 401) {
        console.log("[DASHBOARD] Token expired, clearing session and redirecting");
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        localStorage.removeItem("skillAssessment");
        navigate("/");
      } else {
        console.log("[DASHBOARD] Using fallback user data");
        setLoading(false);
      }
    }
  };

  const fetchAssessmentStatus = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) return;
      
      console.log("[DASHBOARD] Fetching assessment status...");
      const response = await axios.get(`${API_BASE_URL}/api/user/assessment-status`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      if (response.data?.success) {
        const { assessment_taken, predicted_level, can_take_quiz, can_access_roadmap } = response.data;
        
        console.log(`[DASHBOARD] Assessment status - Taken: ${assessment_taken}, Level: ${predicted_level}`);
        
        setAssessmentTaken(assessment_taken);
        
        if (predicted_level) {
          setMlData(prev => ({
            ...prev,
            skillLevel: predicted_level
          }));
        }
      }
    } catch (error) {
      console.log("[DASHBOARD] Assessment status fetch error:", error.message);
    }
  };

  const fetchRoadmap = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) return;
      
      console.log("[DASHBOARD] Fetching roadmap...");
      const response = await axios.get(`${API_BASE_URL}/api/roadmap`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      console.log("[DASHBOARD] Roadmap response:", response.data);
      
      if (response.data?.success && response.data.roadmap) {
        setMlData(prev => ({
          ...prev,
          personalizedRoadmap: response.data.roadmap
        }));
        console.log("[DASHBOARD] Roadmap loaded successfully");
      } else {
        console.log("[DASHBOARD] No roadmap available:", response.data?.error);
      }
    } catch (error) {
      console.log("[DASHBOARD] Roadmap fetch error:", error.message);
    }
  };

  const fetchMLPredictions = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setLoading(false);
        return;
      }
      
      // Just fetch basic streak data - skip ML predictions for now
      try {
        const streakResponse = await axios.get(`${API_BASE_URL}/api/user/streak-data`, {
        headers: { Authorization: `Bearer ${token}` }
        });
        
        if (streakResponse.data) {
          // Update streak data from response
          setStreakData(prev => ({
            ...prev,
            loginStreak: streakResponse.data.current_streak || prev.loginStreak
          }));
        }
      } catch (error) {
        console.log("Streak data not available:", error.message);
      }
      
    } catch (error) {
      console.error("Failed to fetch ML predictions:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleGetStarted = () => {
    // Check if user has completed skill assessment
    if (!assessmentTaken) {
      setShowAssessment(true);
    } else {
      setShowRoadmap(true);
      // Fetch roadmap when showing it
      fetchRoadmap();
    }
  };

  const handleTakeAssessment = () => {
    if (!assessmentTaken) {
      setShowAssessment(true);
    }
  };

  const handleAssessmentComplete = (result) => {
    console.log("[DASHBOARD] Assessment completed with result:", result);
    
    // Update local state immediately
    setAssessmentTaken(true);
    setMlData(prev => ({
      ...prev,
      skillLevel: result.predicted_level,
      personalizedRoadmap: result.roadmap
    }));
    setShowAssessment(false);
    
    // Clear any old assessment data from localStorage
    localStorage.removeItem('skillAssessment');
    
    // Refresh user data to get updated assessment status from backend
    fetchUserData();
    fetchAssessmentStatus();
    
    // Show roadmap immediately after assessment
    setShowRoadmap(true);
    
    console.log(`[DASHBOARD] Assessment complete - User can now access roadmap`);
  };

  const handleLogout = async () => {
    try {
      const token = localStorage.getItem("token");
      
      console.log("[DASHBOARD] Logging out user...");
      
      // Call backend logout endpoint
      if (token) {
        try {
          await axios.post(`${API_BASE_URL}/api/auth/logout`, {}, {
            headers: {
              Authorization: `Bearer ${token}`
            }
          });
        } catch (error) {
          console.log("[DASHBOARD] Backend logout failed, continuing with local cleanup");
        }
      }
      
      // Clear ALL local storage to ensure complete session cleanup
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      localStorage.removeItem("skillAssessment");
      
      // Reset all state to ensure no data leakage
      setUser({ name: "User", avatar: null });
      setAssessmentTaken(false);
      setMlData({
        skillLevel: null,
        learningStyle: null,
        streakRisk: null,
        personalizedRoadmap: null,
        benchmarks: null
      });
      
      console.log("[DASHBOARD] Session cleared, redirecting to login");
      
      // Call the onLogout callback to update user state in App
      if (onLogout) {
        onLogout();
      }
      navigate("/");
    } catch (error) {
      console.error("[DASHBOARD] Logout error:", error);
      // Even if logout fails, clear local state
      localStorage.clear();
      if (onLogout) {
        onLogout();
      }
      navigate("/");
    }
  };

  // ML-generated roadmap is now handled by DuolingoRoadmap component

  const platformLinks = [
    {
      name: "LeetCode",
      url: "https://leetcode.com",
      icon: "🟠",
      color: "#FFA116"
    },
    {
      name: "HackerRank",
      url: "https://hackerrank.com",
      icon: "🟢",
      color: "#00EA64"
    },
    {
      name: "HackerEarth",
      url: "https://hackerearth.com",
      icon: "🔵",
      color: "#2C5AA0"
    }
  ];

  // Show skill assessment if explicitly requested
  if (showAssessment) {
    return <SkillAssessment onComplete={handleAssessmentComplete} />;
  }

  // Show loading state
  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading-state">
          <h2>Loading your dashboard...</h2>
          <p>Please wait while we fetch your data.</p>
          <div style={{marginTop: '20px'}}>
            <button onClick={() => setLoading(false)} style={{padding: '10px 20px', background: '#38bdf8', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer'}}>
              Skip Loading (Debug)
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* Navigation Bar */}
      <nav className="dashboard-nav">
        <div className="nav-content">
          {/* Left: Brand */}
          <div className="nav-brand">
            <h1 className="brand-wordmark">Pulse</h1>
          </div>

          {/* Center: Navigation Links */}
          <div className="nav-links">
            <button 
              className={`nav-link ${activeTab === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveTab('overview')}
            >
              Overview
            </button>
            <button 
              className={`nav-link ${activeTab === 'streaks' ? 'active' : ''}`}
              onClick={() => setActiveTab('streaks')}
            >
              Streaks
            </button>
            <button 
              className={`nav-link ${activeTab === 'roadmap' ? 'active' : ''}`}
              onClick={() => setActiveTab('roadmap')}
            >
              Roadmap
            </button>
            <button 
              className={`nav-link ${activeTab === 'profiles' ? 'active' : ''}`}
              onClick={() => setActiveTab('profiles')}
            >
              Profiles
            </button>
          </div>

          {/* Right: User Profile */}
          <div className="nav-profile">
            <div className="profile-dropdown">
              <div className="profile-avatar">
                {user.avatar ? (
                  <img src={user.avatar} alt="Profile" />
                ) : (
                  <div className="avatar-placeholder">
                    {(user.name || user.username || 'U').charAt(0).toUpperCase()}
                  </div>
                )}
              </div>
              <div className="dropdown-content">
                <button onClick={() => navigate('/profile')}>Profile</button>
                <a href="#settings">Settings</a>
                <button onClick={handleLogout}>Logout</button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="dashboard-main">
        {activeTab === 'overview' && (
          <>
        {/* Welcome Section */}
        <section className="welcome-section">
          <div className="welcome-header">
            <h1 className="dashboard-welcome-text">Welcome back, {user.name || user.username || 'User'}! 👋</h1>
            <p>Ready to continue your learning journey?</p>
          </div>
          
          {/* Quick Stats */}
          <div className="quick-stats">
            <div className="stat-card">
              <div className="stat-number">{user.total_problems_solved || 0}</div>
              <div className="stat-label">Problems Solved</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{DISPLAY_STREAK}</div>
              <div className="stat-label">Day Streak</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{user.skill_level || 'Beginner'}</div>
              <div className="stat-label">Skill Level</div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="action-buttons">
            {!assessmentTaken ? (
              <button className="btn-primary" onClick={handleTakeAssessment}>
                Take Skill Assessment
              </button>
            ) : (
              <div className="assessment-completed">
                <span className="completed-badge">✅ Assessment Completed</span>
                <p>Your skill level: <strong>{user.predicted_level || user.skill_level}</strong></p>
              </div>
            )}
            <button className="btn-secondary" onClick={handleGetStarted}>
              {assessmentTaken ? 'View Your Personalized Roadmap' : 'Take Assessment First'}
            </button>
          </div>
        </section>

        {/* ML Insights Section */}
        {mlData.skillLevel && (
          <section className="ml-insights-section">
            <div className="insights-grid">
              {/* Skill Level Display */}
              <div className="insight-card skill-level-card">
                <div className="card-header">
                  <h3 className="card-title">🎯 Your Skill Level</h3>
                </div>
                <div className="skill-level-display">
                  <div className="skill-badge">{mlData.skillLevel}</div>
                  <p className="skill-description">
                    We detected you're at <strong>{mlData.skillLevel}</strong> level based on your assessment
                  </p>
                </div>
              </div>

              {/* Streak Risk Warning */}
              {mlData.streakRisk && (
                <div className={`insight-card streak-risk-card ${mlData.streakRisk.risk_level.toLowerCase()}`}>
                  <div className="card-header">
                    <h3 className="card-title">
                      {mlData.streakRisk.risk_level === 'High' ? '🚨' : 
                       mlData.streakRisk.risk_level === 'Medium' ? '⚠️' : '✅'} 
                      Streak Risk: {mlData.streakRisk.risk_level}
                    </h3>
                  </div>
                  <div className="risk-content">
                    <div className="risk-probability">
                      {Math.round(mlData.streakRisk.risk_probability * 100)}% chance of breaking streak
                    </div>
                    <div className="recommendations">
                      {mlData.streakRisk.recommendation.slice(0, 2).map((rec, idx) => (
                        <div key={idx} className="recommendation-item">{rec}</div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Learning Style Recommendation */}
              {mlData.learningStyle && (
                <div className="insight-card learning-style-card">
                  <div className="card-header">
                    <h3 className="card-title">🧠 Recommended Learning Style</h3>
                  </div>
                  <div className="learning-style-content">
                    <div className="style-name">{mlData.learningStyle.recommended_style}</div>
                    <div className="style-recommendations">
                      {mlData.learningStyle.recommendations.slice(0, 2).map((rec, idx) => (
                        <div key={idx} className="recommendation-item">{rec}</div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </section>
        )}

        {!showRoadmap ? (
          /* Welcome Section */
          <section className="welcome-section">
            <div className="welcome-content">
              <h1 className="welcome-heading">
                Let's get started with your DSA journey!
              </h1>
              <p className="welcome-description">
                Master Data Structures and Algorithms with our structured learning path. 
                Track your progress, maintain streaks, and achieve your coding goals with 
                focused Pomodoro sessions and comprehensive practice.
              </p>
              {!assessmentTaken ? (
                <button className="get-started-button" onClick={handleGetStarted}>
                  <span className="button-text">Take Assessment</span>
                  <span className="button-icon">🚀</span>
                </button>
              ) : (
                <div className="assessment-completed-section">
                  <div className="completed-message">
                    <span className="completed-icon">✅</span>
                    <span className="completed-text">Assessment Completed!</span>
                  </div>
                  <button className="get-started-button" onClick={handleGetStarted}>
                    <span className="button-text">View Your Roadmap</span>
                    <span className="button-icon">🗺️</span>
                  </button>
                </div>
              )}
            </div>
          </section>
        ) : (
          /* Duolingo-Style Roadmap Section */
          <section className="roadmap-section">
            <DuolingoRoadmap />
          </section>
        )}

        {/* Progress/Analysis Section */}
        <section className="progress-section">
          <div className="progress-content">
            {/* Platform Links */}
            <div className="platforms-card glass-card">
              <h3 className="card-title">Practice Platforms</h3>
              <div className="platforms-grid">
                {platformLinks.map((platform) => (
                  <a 
                    key={platform.name}
                    href={platform.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="platform-link"
                    style={{ '--platform-color': platform.color }}
                  >
                    <span className="platform-icon">{platform.icon}</span>
                    <span className="platform-name">{platform.name}</span>
                  </a>
                ))}
              </div>
            </div>

            {/* Enhanced Streak Tracker */}
            <div className="streaks-card glass-card">
              <h3 className="card-title">Your Streaks & Progress</h3>
              
              {/* Motivational Quote */}
              {streakData.motivationalQuote && (
                <div className="motivational-quote">
                  <div className="quote-icon">✨</div>
                  <div className="quote-text">"{streakData.motivationalQuote}"</div>
                </div>
              )}
              
              <div className="streaks-grid">
                <div className="streak-item">
                  <div className="streak-icon">🔥</div>
                  <div className="streak-info">
                    <div className="streak-number">{DISPLAY_STREAK}</div>
                    <div className="streak-label">Login Streak</div>
                  </div>
                </div>
                
                <div className="streak-item">
                  <div className="streak-icon">📅</div>
                  <div className="streak-info">
                    <div className="streak-number">{STREAK_DATA.total_days}</div>
                    <div className="streak-label">Total Days</div>
                  </div>
                </div>
                
                <div className="streak-item">
                  <div className="streak-icon">📈</div>
                  <div className="streak-info">
                    <div className="streak-number">{STREAK_DATA.this_week}/7</div>
                    <div className="streak-label">This Week</div>
                  </div>
                </div>
                
                <div className="streak-item">
                  <div className="streak-icon">🏆</div>
                  <div className="streak-info">
                    <div className="streak-number">24%</div>
                    <div className="streak-label">Roadmap Progress</div>
                  </div>
                </div>
              </div>
              
              {/* Last Login */}
              {streakData.lastLogin && (
                <div className="last-login">
                  <small>Last login: {new Date(streakData.lastLogin).toLocaleDateString()}</small>
                </div>
              )}
            </div>

            {/* Progress Benchmarks */}
            {mlData.benchmarks && (
              <div className="benchmarks-card glass-card">
                <h3 className="card-title">📊 Progress Benchmarks</h3>
                <div className="benchmarks-grid">
                  {Object.entries(mlData.benchmarks).map(([metric, data]) => (
                    <div key={metric} className="benchmark-item">
                      <div className="benchmark-header">
                        <span className="metric-name">
                          {metric.replace('avg_', '').replace('_', ' ').toUpperCase()}
                        </span>
                        <span className="percentile-badge">
                          {data.percentile}th percentile
                        </span>
                      </div>
                      <div className="benchmark-values">
                        <div className="user-value">You: {data.user_value}</div>
                        <div className="benchmark-value">Average: {data.benchmark_value}</div>
                      </div>
                      <div className="benchmark-message">{data.message}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Quick Actions */}
            <div className="quick-actions-card glass-card">
              <h3 className="card-title">Quick Actions</h3>
              <div className="actions-grid">
                <button className="action-btn pomodoro" onClick={() => navigate('/pomodoro')}>
                  <span className="action-icon">🍅</span>
                  <span className="action-text">Start Pomodoro</span>
                </button>
                
                <button className="action-btn practice">
                  <span className="action-icon">💻</span>
                  <span className="action-text">Practice Problems</span>
                </button>
                
                <button className="action-btn review">
                  <span className="action-icon">📝</span>
                  <span className="action-text">Review Notes</span>
                </button>
                
                <button className="action-btn progress">
                  <span className="action-icon">📈</span>
                  <span className="action-text">View Progress</span>
                </button>
              </div>
            </div>
          </div>
        </section>
        </>
        )}
        
        {activeTab === 'streaks' && (
          <section className="streaks-section">
            <StreakTracker />
          </section>
        )}
        
        {activeTab === 'roadmap' && (
          <section className="roadmap-section">
            <div style={{padding: '20px', minHeight: '400px'}}>
              <h2>Your Learning Roadmap</h2>
              <DuolingoRoadmap />
            </div>
          </section>
        )}
        
        {activeTab === 'profiles' && (
          <section className="profiles-section">
            <CodingProfiles />
          </section>
        )}
      </main>
    </div>
  );
}