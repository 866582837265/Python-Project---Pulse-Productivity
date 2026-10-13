import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './DuolingoRoadmap.css';

export default function DuolingoRoadmapNew() {
  const [roadmap, setRoadmap] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [userLevel, setUserLevel] = useState('Beginner');
  const navigate = useNavigate();

  useEffect(() => {
    fetchRoadmap();
  }, []);

  const fetchRoadmap = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/');
        return;
      }

      console.log('[ROADMAP] Fetching roadmap...');
      
      const response = await axios.get('http://localhost:5000/api/roadmap', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      console.log('[ROADMAP] Response:', response.data);

      if (response.data.success) {
        setRoadmap(response.data.roadmap || []);
        setUserLevel(response.data.level || 'Beginner');
        setError(null);
        console.log(`✅ Roadmap loaded with ${response.data.roadmap?.length || 0} nodes`);
      } else {
        if (response.data.code === 'LEVEL_NOT_SET') {
          setError('LEVEL_NOT_SET');
        } else {
          setError(response.data.error || 'Failed to load roadmap');
        }
      }
    } catch (err) {
      console.error('[ROADMAP] Error:', err);
      if (err.response?.status === 401) {
        localStorage.removeItem('token');
        navigate('/');
      } else if (err.response?.data?.code === 'LEVEL_NOT_SET') {
        setError('LEVEL_NOT_SET');
      } else {
        setError('Network error. Please check your connection and try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleTopicStart = async (topicId) => {
    try {
      console.log(`[ROADMAP] Starting topic: ${topicId}`);
      
      // Generate questions for this topic
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:5000/api/questions/generate', {
        topicId: topicId
      }, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      if (response.data.success) {
        // Navigate to topic questions page
        navigate(`/roadmap/topic/${topicId}?packId=${response.data.packId}`);
      } else {
        alert('Failed to generate questions for this topic');
      }
    } catch (error) {
      console.error('[ROADMAP] Error starting topic:', error);
      alert('Failed to start topic. Please try again.');
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'Beginner': return 'bg-green-500';
      case 'Intermediate': return 'bg-amber-500';
      case 'Expert': return 'bg-rose-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return '✅';
      case 'unlocked': return '🔓';
      case 'locked': return '🔒';
      default: return '⭕';
    }
  };

  if (loading) {
    return (
      <div className="roadmap-container">
        <div className="loading-skeleton">
          <h2>Loading your personalized roadmap...</h2>
          <div className="skeleton-nodes">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="skeleton-node"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error === 'LEVEL_NOT_SET') {
    return (
      <div className="roadmap-container">
        <div className="error-state">
          <h2>🎯 Take Your Skill Assessment</h2>
          <p>Complete the skill assessment to unlock your personalized learning roadmap.</p>
          <button 
            className="btn-primary"
            onClick={() => navigate('/dashboard')}
          >
            Take Assessment
          </button>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="roadmap-container">
        <div className="error-state">
          <h2>❌ Error Loading Roadmap</h2>
          <p>{error}</p>
          <button 
            className="btn-secondary"
            onClick={fetchRoadmap}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="roadmap-container">
      <div className="roadmap-header">
        <h1>Your Learning Path</h1>
        <div className="level-badge">
          <span className={`badge ${getDifficultyColor(userLevel)}`}>
            {userLevel} Level
          </span>
        </div>
      </div>

      <div className="roadmap-path">
        {roadmap.map((topic, index) => {
          const isUnlocked = topic.status === 'unlocked';
          const isCompleted = topic.status === 'completed';
          const isLocked = topic.status === 'locked';
          
          return (
            <div key={topic.id} className="topic-node-container">
              {/* Connector line */}
              {index > 0 && (
                <div className={`connector ${isCompleted ? 'completed' : ''}`}></div>
              )}
              
              {/* Topic Node */}
              <div className={`topic-node ${topic.status}`}>
                <div className="node-circle">
                  <span className="status-icon">{getStatusIcon(topic.status)}</span>
                  <span className="order-number">{topic.order}</span>
                </div>
                
                <div className="node-content">
                  <h3 className="topic-title">{topic.title}</h3>
                  <p className="topic-description">{topic.description}</p>
                  
                  <div className="topic-meta">
                    <span className={`difficulty-badge ${getDifficultyColor(topic.difficulty)}`}>
                      {topic.difficulty}
                    </span>
                  </div>
                  
                  {/* Action Button */}
                  <div className="topic-actions">
                    {isUnlocked && (
                      <button 
                        className="btn-start"
                        onClick={() => handleTopicStart(topic.id)}
                      >
                        Start
                      </button>
                    )}
                    {isCompleted && (
                      <button className="btn-completed" disabled>
                        Completed
                      </button>
                    )}
                    {isLocked && (
                      <button className="btn-locked" disabled>
                        Locked
                      </button>
                    )}
                  </div>
                  
                  {/* Resources */}
                  {topic.resources && topic.resources.length > 0 && (
                    <div className="topic-resources">
                      <h4>Resources:</h4>
                      <ul>
                        {topic.resources.map((resource, idx) => (
                          <li key={idx}>
                            <a href={resource} target="_blank" rel="noopener noreferrer">
                              📚 Resource {idx + 1}
                            </a>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      {roadmap.length === 0 && (
        <div className="empty-state">
          <h2>No roadmap available</h2>
          <p>Complete the skill assessment to generate your personalized roadmap.</p>
        </div>
      )}
    </div>
  );
}