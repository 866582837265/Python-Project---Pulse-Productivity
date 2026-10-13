import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './RoadmapView.css';

const RoadmapView = () => {
  const [roadmap, setRoadmap] = useState([]);
  const [skillLevel, setSkillLevel] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRoadmap();
  }, []);

  const fetchRoadmap = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5000/api/roadmap', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data.success) {
        setRoadmap(response.data.roadmap);
        setSkillLevel(response.data.skill_level);
      }
    } catch (error) {
      console.error('Failed to fetch roadmap:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateProgress = async (topicId, progress, completed = false) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post('http://localhost:5000/api/roadmap/progress', {
        topic_id: topicId,
        progress,
        completed
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Update local state
      setRoadmap(prev => prev.map(topic => 
        topic.id === topicId 
          ? { ...topic, progress, completed }
          : topic
      ));
    } catch (error) {
      console.error('Failed to update progress:', error);
    }
  };

  if (loading) {
    return <div className="roadmap-loading">Loading your personalized roadmap...</div>;
  }

  return (
    <div className="roadmap-view">
      <div className="roadmap-header">
        <h2>🗺️ Your Learning Roadmap</h2>
        <div className="skill-badge">{skillLevel} Level</div>
      </div>
      
      <div className="roadmap-grid">
        {roadmap.map((topic, index) => (
          <div key={topic.id} className={`roadmap-card ${topic.completed ? 'completed' : ''}`}>
            <div className="card-header">
              <div className="card-number">{index + 1}</div>
              <div className="badges">
                <span className={`difficulty-badge ${topic.difficulty?.toLowerCase()}`}>
                  {topic.difficulty}
                </span>
                {topic.priority && (
                  <span className={`priority-badge ${topic.priority}`}>
                    {topic.priority === 'high' ? '🔥' : topic.priority === 'medium' ? '⚡' : '📚'}
                  </span>
                )}
              </div>
            </div>
            
            <h3 className="card-title">{topic.title}</h3>
            <p className="card-description">{topic.description}</p>
            
            <div className="topics-list">
              {topic.topics?.map((subtopic, idx) => (
                <span key={idx} className="topic-tag">{subtopic}</span>
              ))}
            </div>
            
            {topic.estimated_time && (
              <div className="estimated-time">⏱️ {topic.estimated_time}</div>
            )}
            
            <div className="progress-section">
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${topic.progress || 0}%` }}
                ></div>
              </div>
              <div className="progress-text">{topic.progress || 0}% Complete</div>
            </div>
            
            <div className="card-actions">
              {topic.completed ? (
                <span className="completed-badge">✅ Completed</span>
              ) : (
                <div className="action-buttons">
                  <button 
                    className="start-btn"
                    onClick={() => updateProgress(topic.id, 25)}
                  >
                    Start Learning
                  </button>
                  <button 
                    className="complete-btn"
                    onClick={() => updateProgress(topic.id, 100, true)}
                  >
                    Mark Complete
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RoadmapView;