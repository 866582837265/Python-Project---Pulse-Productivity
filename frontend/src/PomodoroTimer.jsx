import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './PomodoroTimer.css';

export default function PomodoroTimer() {
  const [timeLeft, setTimeLeft] = useState(25 * 60); // 25 minutes in seconds
  const [isActive, setIsActive] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [task, setTask] = useState('Focus Session');
  const [duration, setDuration] = useState(25);
  const [isCompleted, setIsCompleted] = useState(false);
  const [stats, setStats] = useState({ total_sessions: 0, sessions_today: 0 });
  
  const intervalRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchStats();
  }, []);

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

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5000/api/pomodoro/stats', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data.success) {
        setStats(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch Pomodoro stats:', error);
    }
  };

  const startTimer = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:5000/api/pomodoro/start', {
        duration: duration,
        task: task
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        setSessionId(response.data.session_id);
        setTimeLeft(duration * 60);
        setIsActive(true);
        setIsCompleted(false);
        console.log('Pomodoro session started:', response.data.session_id);
      }
    } catch (error) {
      console.error('Failed to start Pomodoro session:', error);
    }
  };

  const pauseTimer = () => {
    setIsActive(false);
  };

  const resumeTimer = () => {
    setIsActive(true);
  };

  const resetTimer = () => {
    setIsActive(false);
    setTimeLeft(duration * 60);
    setSessionId(null);
    setIsCompleted(false);
  };

  const handleTimerComplete = async () => {
    setIsActive(false);
    setIsCompleted(true);
    
    if (sessionId) {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.post('http://localhost:5000/api/pomodoro/complete', {
          session_id: sessionId
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (response.data.success) {
          console.log('Pomodoro session completed successfully');
          fetchStats(); // Refresh stats
        }
      } catch (error) {
        console.error('Failed to complete Pomodoro session:', error);
      }
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getProgressPercentage = () => {
    const totalSeconds = duration * 60;
    return ((totalSeconds - timeLeft) / totalSeconds) * 100;
  };

  return (
    <div className="pomodoro-container">
      <div className="pomodoro-header">
        <button className="back-button" onClick={() => navigate('/dashboard')}>
          ← Back to Dashboard
        </button>
        <h1>Pomodoro Timer</h1>
      </div>

      <div className="pomodoro-stats">
        <div className="stat-item">
          <span className="stat-number">{stats.sessions_today}</span>
          <span className="stat-label">Today</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{stats.total_sessions}</span>
          <span className="stat-label">Total</span>
        </div>
      </div>

      <div className="timer-card">
        <div className="timer-display">
          <div className="progress-ring">
            <svg className="progress-ring-svg" width="200" height="200">
              <circle
                className="progress-ring-circle-bg"
                stroke="#e5e7eb"
                strokeWidth="8"
                fill="transparent"
                r="90"
                cx="100"
                cy="100"
              />
              <circle
                className="progress-ring-circle"
                stroke="#3b82f6"
                strokeWidth="8"
                fill="transparent"
                r="90"
                cx="100"
                cy="100"
                strokeDasharray={`${2 * Math.PI * 90}`}
                strokeDashoffset={`${2 * Math.PI * 90 * (1 - getProgressPercentage() / 100)}`}
                transform="rotate(-90 100 100)"
              />
            </svg>
            <div className="timer-text">
              <div className="time-display">{formatTime(timeLeft)}</div>
              <div className="task-name">{task}</div>
            </div>
          </div>
        </div>

        {!isActive && !sessionId && (
          <div className="timer-setup">
            <div className="input-group">
              <label>Task Name:</label>
              <input
                type="text"
                value={task}
                onChange={(e) => setTask(e.target.value)}
                placeholder="What are you working on?"
              />
            </div>
            <div className="input-group">
              <label>Duration (minutes):</label>
              <select value={duration} onChange={(e) => setDuration(Number(e.target.value))}>
                <option value={15}>15 minutes</option>
                <option value={25}>25 minutes</option>
                <option value={30}>30 minutes</option>
                <option value={45}>45 minutes</option>
                <option value={60}>60 minutes</option>
              </select>
            </div>
          </div>
        )}

        <div className="timer-controls">
          {!sessionId ? (
            <button className="start-button" onClick={startTimer}>
              Start Focus Session
            </button>
          ) : (
            <div className="control-buttons">
              {!isActive ? (
                <button className="resume-button" onClick={resumeTimer}>
                  Resume
                </button>
              ) : (
                <button className="pause-button" onClick={pauseTimer}>
                  Pause
                </button>
              )}
              <button className="reset-button" onClick={resetTimer}>
                Reset
              </button>
            </div>
          )}
        </div>

        {isCompleted && (
          <div className="completion-message">
            <div className="success-icon">🎉</div>
            <h3>Great job! Session completed!</h3>
            <p>You've successfully completed a {duration}-minute focus session.</p>
            <button className="new-session-button" onClick={resetTimer}>
              Start New Session
            </button>
          </div>
        )}
      </div>

      <div className="tips-section">
        <h3>Pomodoro Tips</h3>
        <ul>
          <li>🎯 Focus on one task during each session</li>
          <li>📱 Put away distractions like your phone</li>
          <li>☕ Take a 5-minute break between sessions</li>
          <li>🏆 After 4 sessions, take a longer 15-30 minute break</li>
        </ul>
      </div>
    </div>
  );
}