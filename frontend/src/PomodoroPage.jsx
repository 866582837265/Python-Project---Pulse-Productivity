import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './PomodoroPage.css';

export default function PomodoroPage() {
  const [timeLeft, setTimeLeft] = useState(25 * 60);
  const [isActive, setIsActive] = useState(false);
  const [sessionType, setSessionType] = useState('focus');
  const [isCompleted, setIsCompleted] = useState(false);
  const [stats, setStats] = useState({ total_sessions: 0, today_sessions: 0 });
  
  const intervalRef = useRef(null);
  const navigate = useNavigate();

  const sessionTypes = {
    focus: { duration: 25, label: 'Focus', color: '#ef4444' },
    shortBreak: { duration: 5, label: 'Short Break', color: '#10b981' },
    longBreak: { duration: 15, label: 'Long Break', color: '#3b82f6' }
  };

  useEffect(() => {
    fetchStats();
    setTimeLeft(sessionTypes[sessionType].duration * 60);
  }, [sessionType]);

  useEffect(() => {
    if (isActive && timeLeft > 0) {
      intervalRef.current = setInterval(() => {
        setTimeLeft(time => time - 1);
      }, 1000);
    } else if (timeLeft === 0 && isActive) {
      handleTimerComplete();
    } else {
      clearInterval(intervalRef.current);
    }

    return () => clearInterval(intervalRef.current);
  }, [isActive, timeLeft]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e) => {
      if (e.code === 'Space') {
        e.preventDefault();
        toggleTimer();
      } else if (e.code === 'KeyR') {
        e.preventDefault();
        resetTimer();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [isActive]);

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5000/api/pomodoro/summary', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data) {
        setStats(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch Pomodoro stats:', error);
    }
  };

  const toggleTimer = () => {
    setIsActive(!isActive);
  };

  const resetTimer = () => {
    setIsActive(false);
    setTimeLeft(sessionTypes[sessionType].duration * 60);
    setIsCompleted(false);
  };

  const handleTimerComplete = async () => {
    setIsActive(false);
    setIsCompleted(true);
    
    // Only save focus sessions
    if (sessionType === 'focus') {
      try {
        const token = localStorage.getItem('token');
        await axios.post('http://localhost:5000/api/pomodoro/complete', {
          durationMinutes: sessionTypes[sessionType].duration
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        fetchStats(); // Refresh stats
        showConfetti();
      } catch (error) {
        console.error('Failed to save Pomodoro session:', error);
      }
    }
  };

  const showConfetti = () => {
    // Simple confetti effect
    const confetti = document.createElement('div');
    confetti.innerHTML = '🎉';
    confetti.style.position = 'fixed';
    confetti.style.top = '50%';
    confetti.style.left = '50%';
    confetti.style.fontSize = '4rem';
    confetti.style.zIndex = '9999';
    confetti.style.animation = 'confetti 2s ease-out forwards';
    document.body.appendChild(confetti);
    
    setTimeout(() => {
      document.body.removeChild(confetti);
    }, 2000);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getProgressPercentage = () => {
    const totalSeconds = sessionTypes[sessionType].duration * 60;
    return ((totalSeconds - timeLeft) / totalSeconds) * 100;
  };

  const currentSession = sessionTypes[sessionType];

  return (
    <div className="pomodoro-page" style={{ '--session-color': currentSession.color }}>
      <div className="pomodoro-header">
        <button className="back-btn" onClick={() => navigate('/dashboard')}>
          ← Dashboard
        </button>
        <div className="stats">
          <div className="stat">
            <span className="stat-number">{stats.today_sessions}</span>
            <span className="stat-label">Today</span>
          </div>
          <div className="stat">
            <span className="stat-number">{stats.total_sessions}</span>
            <span className="stat-label">Total</span>
          </div>
        </div>
      </div>

      <div className="session-selector">
        {Object.entries(sessionTypes).map(([key, session]) => (
          <button
            key={key}
            className={`session-btn ${sessionType === key ? 'active' : ''}`}
            onClick={() => setSessionType(key)}
            disabled={isActive}
            style={{ '--btn-color': session.color }}
          >
            {session.label}
          </button>
        ))}
      </div>

      <div className="timer-container">
        <div className="timer-circle">
          <svg className="progress-ring" width="300" height="300">
            <circle
              className="progress-ring-bg"
              stroke="rgba(255,255,255,0.1)"
              strokeWidth="8"
              fill="transparent"
              r="140"
              cx="150"
              cy="150"
            />
            <circle
              className="progress-ring-fill"
              stroke="var(--session-color)"
              strokeWidth="8"
              fill="transparent"
              r="140"
              cx="150"
              cy="150"
              strokeDasharray={`${2 * Math.PI * 140}`}
              strokeDashoffset={`${2 * Math.PI * 140 * (1 - getProgressPercentage() / 100)}`}
              transform="rotate(-90 150 150)"
            />
          </svg>
          <div className="timer-content">
            <div className="time-display">{formatTime(timeLeft)}</div>
            <div className="session-label">{currentSession.label}</div>
          </div>
        </div>
      </div>

      <div className="controls">
        <button
          className="control-btn primary"
          onClick={toggleTimer}
          disabled={isCompleted}
        >
          {isActive ? 'Pause' : 'Start'}
        </button>
        <button className="control-btn secondary" onClick={resetTimer}>
          Reset
        </button>
      </div>

      {isCompleted && (
        <div className="completion-modal">
          <div className="completion-content">
            <div className="completion-icon">
              {sessionType === 'focus' ? '🎉' : '✨'}
            </div>
            <h2>
              {sessionType === 'focus' 
                ? '+1 Focus Session!' 
                : `${currentSession.label} Complete!`}
            </h2>
            <p>
              {sessionType === 'focus'
                ? 'Great job staying focused! Take a short break.'
                : 'Time to get back to work!'}
            </p>
            <button className="completion-btn" onClick={resetTimer}>
              Start New Session
            </button>
          </div>
        </div>
      )}

      <div className="shortcuts">
        <div className="shortcut">
          <kbd>Space</kbd> Start/Pause
        </div>
        <div className="shortcut">
          <kbd>R</kbd> Reset
        </div>
      </div>
    </div>
  );
}