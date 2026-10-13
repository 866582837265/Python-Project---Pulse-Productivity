import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './StreakTracker.css';
import { DISPLAY_STREAK, STREAK_DATA } from './constants/streakConstants';

const StreakTracker = () => {
  const [streakData, setStreakData] = useState({
    current_streak: 0,
    longest_streak: 0,
    total_active_days: 0,
    last_activity: null,
    last_activity_type: 'login',
    streak_risk: 'Low',
    recent_activity: {
      days_active_last_week: 0,
      days_active_last_month: 0
    }
  });
  const [streakHistory, setStreakHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    fetchStreakData();
    fetchStreakHistory();
  }, []);

  const fetchStreakData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5000/api/streaks', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data.success) {
        setStreakData(response.data.data);
      }
    } catch (error) {
      console.error('Failed to fetch streak data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStreakHistory = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5000/api/streaks/history', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data.success) {
        setStreakHistory(response.data.history);
      }
    } catch (error) {
      console.error('Failed to fetch streak history:', error);
    }
  };

  const updateStreak = async (activityType = 'practice') => {
    try {
      setUpdating(true);
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:5000/api/streaks/update', 
        { activity_type: activityType },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.success) {
        // Update local state immediately for better UX
        if (response.data.streak_updated) {
          setStreakData(prev => ({
            ...prev,
            current_streak: response.data.current_streak,
            longest_streak: response.data.longest_streak,
            total_active_days: response.data.total_active_days || prev.total_active_days,
            last_activity_type: activityType
          }));
          
          showStreakNotification(response.data.current_streak, response.data.message);
        }
        
        // Refresh data from server
        await fetchStreakData();
        await fetchStreakHistory();
        setLastUpdate(new Date());
      }
    } catch (error) {
      console.error('Failed to update streak:', error);
      showErrorNotification('Failed to update streak. Please try again.');
    } finally {
      setUpdating(false);
    }
  };

  const showStreakNotification = (streak, message = null) => {
    const notification = document.createElement('div');
    notification.className = 'streak-notification success';
    notification.innerHTML = message || `🔥 ${streak} day streak!`;
    document.body.appendChild(notification);
    
    setTimeout(() => {
      if (document.body.contains(notification)) {
        document.body.removeChild(notification);
      }
    }, 4000);
  };
  
  const showErrorNotification = (message) => {
    const notification = document.createElement('div');
    notification.className = 'streak-notification error';
    notification.innerHTML = `❌ ${message}`;
    document.body.appendChild(notification);
    
    setTimeout(() => {
      if (document.body.contains(notification)) {
        document.body.removeChild(notification);
      }
    }, 4000);
  };

  const getStreakEmoji = (streak) => {
    if (streak >= 30) return '🏆';
    if (streak >= 14) return '🔥';
    if (streak >= 7) return '⚡';
    if (streak >= 3) return '💪';
    return '🌱';
  };

  const getStreakMessage = (streak, risk = 'Low') => {
    if (streak === 0) {
      return risk === 'High' ? "Your streak was broken. Start fresh today!" : "Start your streak today!";
    }
    if (streak === 1) return "Great start! Keep it going!";
    if (streak < 7) return "Building momentum!";
    if (streak < 14) return "You're on fire! 🔥";
    if (streak < 30) return "Incredible consistency! 💪";
    return "Streak master! 🏆";
  };
  
  const getStreakRiskMessage = (risk, lastActivity) => {
    if (risk === 'High') return "⚠️ Streak at risk! Stay active to maintain it.";
    if (risk === 'Medium') return "⏰ Don't forget to practice today!";
    return "✅ You're doing great! Keep up the momentum.";
  };
  
  const getActivityTypeIcon = (activityType) => {
    switch (activityType) {
      case 'login': return '🚪';
      case 'practice': return '💻';
      case 'quiz': return '📝';
      default: return '⭐';
    }
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  if (loading) {
    return (
      <div className="streak-loading">
        <div className="loading-spinner"></div>
        <p>Loading your streak...</p>
      </div>
    );
  }

  return (
    <div className="streak-tracker">
      {/* Header */}
      <div className="streak-header">
        <h2>🔥 Learning Streak</h2>
        <p className="streak-subtitle">{getStreakMessage(streakData.current_streak, streakData.streak_risk)}</p>
        {streakData.streak_risk && (
          <p className={`streak-risk ${streakData.streak_risk.toLowerCase()}`}>
            {getStreakRiskMessage(streakData.streak_risk, streakData.last_activity)}
          </p>
        )}
      </div>

      {/* Main Streak Display */}
      <div className="streak-main">
        <div className="streak-circle">
          <div className="streak-emoji">{getStreakEmoji(streakData.current_streak)}</div>
          <div className="streak-number">{DISPLAY_STREAK}</div>
          <div className="streak-label">Day{streakData.current_streak !== 1 ? 's' : ''}</div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="streak-stats">
        <div className="stat-card">
          <div className="stat-number">{DISPLAY_STREAK}</div>
          <div className="stat-label">Current Streak</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{STREAK_DATA.best_streak}</div>
          <div className="stat-label">Best Streak</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{STREAK_DATA.total_days}</div>
          <div className="stat-label">Total Days</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{STREAK_DATA.this_week}</div>
          <div className="stat-label">This Week</div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="streak-actions">
        <button 
          className="update-streak-btn primary"
          onClick={() => updateStreak('practice')}
          disabled={updating}
        >
          {updating ? 'Updating...' : '💻 Mark Practice Complete'}
        </button>
        <button 
          className="update-streak-btn secondary"
          onClick={() => updateStreak('login')}
          disabled={updating}
        >
          {updating ? 'Updating...' : '🚪 Daily Check-in'}
        </button>
      </div>

      {/* Visual History */}
      <div className="streak-history">
        <h3>Last 30 Days</h3>
        <div className="history-grid">
          {streakHistory.map((day, index) => (
            <div
              key={index}
              className={`history-day ${day.has_activity ? 'active' : 'inactive'} ${day.streak > 7 ? 'high-streak' : ''}`}
              title={`${formatDate(day.date)} - ${day.has_activity ? `${day.activity_type} (${day.streak} days)` : 'No activity'}`}
            >
              <div className="day-indicator">
                {day.has_activity ? (day.streak > 7 ? '🏆' : '🔥') : '⚪'}
              </div>
              <div className="day-date">{formatDate(day.date).split(' ')[1]}</div>
            </div>
          ))}
        </div>
        <div className="history-legend">
          <div className="legend-item">
            <span className="legend-icon">🔥</span>
            <span>Active Day</span>
          </div>
          <div className="legend-item">
            <span className="legend-icon">⚪</span>
            <span>Missed Day</span>
          </div>
        </div>
      </div>

      {/* Activity Summary */}
      <div className="activity-summary">
        {streakData.last_activity && (
          <div className="last-activity">
            <p>
              {getActivityTypeIcon(streakData.last_activity_type)} Last activity: {streakData.last_activity_type} on{' '}
              {new Date(streakData.last_activity).toLocaleDateString()}
            </p>
          </div>
        )}
        
        {lastUpdate && (
          <div className="last-update">
            <p>Last updated: {lastUpdate.toLocaleTimeString()}</p>
          </div>
        )}
        
        <div className="weekly-summary">
          <h4>Weekly Summary</h4>
          <div className="summary-stats">
            <span>📅 {streakData.recent_activity?.days_active_last_week || 0}/7 days active</span>
            <span>📊 {streakData.recent_activity?.days_active_last_month || 0}/30 days this month</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StreakTracker;