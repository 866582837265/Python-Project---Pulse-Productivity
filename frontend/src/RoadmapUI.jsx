import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from './config';
import './RoadmapUI.css';

export default function RoadmapUI() {
  const navigate = useNavigate();
  const [roadmap, setRoadmap] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRoadmap();
  }, []);

  const fetchRoadmap = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/api/roadmap`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const data = await response.json();
      if (data.success) {
        setRoadmap(data.roadmap);
        setError(null);
      } else if (data.code === 'LEVEL_NOT_SET') {
        setError('LEVEL_NOT_SET');
      } else {
        setError(data.error || 'Failed to load roadmap');
      }
    } catch (err) {
      setError('Network error. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  const startTopic = (topicId) => {
    navigate(`/roadmap/topic/${topicId}`);
  };

  if (loading) {
    return <div className="loading">Loading roadmap...</div>;
  }

  if (error === 'LEVEL_NOT_SET') {
    return (
      <div className="error-container">
        <h2>Assessment Required</h2>
        <p>Complete the skill assessment to unlock your personalized roadmap.</p>
        <button onClick={() => navigate('/dashboard')}>Take Assessment</button>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <h2>Error Loading Roadmap</h2>
        <p>{error}</p>
        <button onClick={fetchRoadmap}>Retry</button>
      </div>
    );
  }

  const completed = roadmap.filter(t => t.status === 'completed').length;
  const progressPercent = roadmap.length ? Math.round((completed / roadmap.length) * 100) : 0;

  return (
    <div className="roadmap-container">
      <h1>Learning Roadmap</h1>
      
      <div className="progress-section">
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progressPercent}%` }}></div>
        </div>
        <p>{progressPercent}% Complete ({completed}/{roadmap.length} topics)</p>
      </div>

      <div className="topics-list">
        {roadmap.map((topic) => {
          const isUnlocked = topic.status === 'unlocked';
          const isCompleted = topic.status === 'completed';
          const topicName = topic.title || topic.topic || 'Unknown Topic';
          
          return (
            <div key={topic.id} className={`topic-item ${topic.status}`}>
              <div className="topic-info">
                <h3>{topicName}</h3>
                <span className={`difficulty ${topic.difficulty?.toLowerCase()}`}>
                  {topic.difficulty}
                </span>
              </div>
              
              <div className="topic-actions">
                {isCompleted && <span className="status-icon">✅</span>}
                {isUnlocked && (
                  <button onClick={() => startTopic(topic.id)} className="start-btn">
                    View Topic
                  </button>
                )}
                {isCompleted && (
                  <button onClick={() => startTopic(topic.id)} className="start-btn" style={{backgroundColor: '#28a745'}}>
                    Review
                  </button>
                )}
                {topic.status === 'locked' && <span className="status-icon">🔒</span>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}