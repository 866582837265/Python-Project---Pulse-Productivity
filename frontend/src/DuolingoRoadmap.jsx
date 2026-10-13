import React, { useState, useEffect } from "react";
import axios from "axios";
import { API_BASE_URL } from "./config";
import RoadmapUI from "./RoadmapUI";
import "./DuolingoRoadmap.css";

export default function DuolingoRoadmap() {
  const [roadmap, setRoadmap] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Add error boundary
  useEffect(() => {
    const handleError = (error) => {
      console.error('[ROADMAP] Component error:', error);
      setError('Component failed to load');
      setLoading(false);
    };
    
    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, []);

  useEffect(() => {
    fetchRoadmap();
  }, []);

  const fetchRoadmap = async (retryCount = 0) => {
    const maxRetries = 3;
    
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("Authentication required");
        setLoading(false);
        return;
      }

      console.log(`[FRONTEND] Fetching roadmap (attempt ${retryCount + 1})...`);
      const response = await axios.get(`${API_BASE_URL}/api/roadmap`, {
        headers: { Authorization: `Bearer ${token}` },
        timeout: 10000
      });

      console.log("[FRONTEND] Roadmap API response:", response.data);

      if (response.data.success && response.data.roadmap) {
        const roadmapNodes = response.data.roadmap;
        const roadmapData = {
          level: response.data.level,
          topics: roadmapNodes,
          total_topics: roadmapNodes.length
        };
        
        setRoadmap(roadmapData);
        console.log("[FRONTEND] Roadmap loaded successfully with", roadmapNodes.length, "topics");
      } else if (response.data.code === "LEVEL_NOT_SET" || response.data.error?.includes("assessment")) {
        setError("LEVEL_NOT_SET");
      } else {
        const errorMsg = response.data.error || "No roadmap data available. Please try refreshing.";
        console.error("[FRONTEND] Roadmap API error:", errorMsg);
        setError(errorMsg);
      }
    } catch (error) {
      console.error(`[FRONTEND] Failed to fetch roadmap (attempt ${retryCount + 1}):`, error);
      
      if (error.response) {
        const status = error.response.status;
        const errorData = error.response.data;
        
        // Retry on 5xx server errors
        if (status >= 500 && retryCount < maxRetries) {
          console.log(`[FRONTEND] Retrying in ${(retryCount + 1) * 1000}ms...`);
          setTimeout(() => fetchRoadmap(retryCount + 1), (retryCount + 1) * 1000);
          return;
        }
        
        if (status === 401) {
          setError("Please log in again");
        } else if (status === 404 && errorData?.code === "LEVEL_NOT_SET") {
          setError("LEVEL_NOT_SET");
        } else {
          setError(errorData?.error || `Server error (${status}). Please try again.`);
        }
      } else if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        if (retryCount < maxRetries) {
          console.log(`[FRONTEND] Timeout, retrying in ${(retryCount + 1) * 1000}ms...`);
          setTimeout(() => fetchRoadmap(retryCount + 1), (retryCount + 1) * 1000);
          return;
        }
        setError("Request timeout. Please check your connection.");
      } else if (error.request) {
        setError("Network error. Please check your connection and try again.");
      } else {
        setError("An unexpected error occurred. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const completeTopic = async (topicId) => {
    try {
      const token = localStorage.getItem("token");
      console.log("[FRONTEND] Completing topic:", topicId);
      
      const response = await axios.post(
        `${API_BASE_URL}/api/roadmap/complete-topic`,
        { topic_id: topicId },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data.success) {
        console.log("[FRONTEND] Topic completed successfully");
        // Refresh roadmap to show updated progress
        setLoading(true);
        await fetchRoadmap();
      } else {
        console.error("[FRONTEND] Failed to complete topic:", response.data.error);
      }
    } catch (error) {
      console.error("[FRONTEND] Failed to complete topic:", error);
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty.toLowerCase()) {
      case "beginner": return "#22c55e"; // Green
      case "intermediate": return "#f59e0b"; // Yellow
      case "expert": return "#ef4444"; // Red
      default: return "#6b7280"; // Gray
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "completed": return "✅";
      case "unlocked": return "🔓";
      case "locked": return "🔒";
      default: return "⭕";
    }
  };

  if (loading) {
    return (
      <div className="duolingo-roadmap" style={{minHeight: '400px', padding: '20px'}}>
        <div className="loading-state">
          <h2>Loading your roadmap...</h2>
          <p>Please wait while we fetch your learning path...</p>
          <div className="loading-skeleton">
            {[1,2,3,4].map(i => (
              <div key={i} className="skeleton-item" style={{
                height: '80px', background: 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)',
                backgroundSize: '200% 100%', animation: 'loading 1.5s infinite',
                borderRadius: '8px', marginBottom: '16px'
              }} />
            ))}
          </div>
          <style>{`
            @keyframes loading {
              0% { background-position: 200% 0; }
              100% { background-position: -200% 0; }
            }
          `}</style>
        </div>
      </div>
    );
  }

  if (error) {
    if (error === "LEVEL_NOT_SET") {
      return (
        <div className="duolingo-roadmap">
          <div className="assessment-required">
            <h2>🎯 Assessment Required</h2>
            <p>Please complete the skill assessment first to generate your personalized roadmap.</p>
            <button onClick={() => window.location.href = '/dashboard'} className="assessment-cta">
              Take Assessment
            </button>
          </div>
        </div>
      );
    }
    
    return (
      <div className="duolingo-roadmap">
        <div className="error-state">
          <h2>❌ Error: {error}</h2>
          <p>Failed to load your roadmap. Please try again.</p>
          <button onClick={() => fetchRoadmap(0)} className="retry-btn">
            Retry Loading Roadmap
          </button>
        </div>
      </div>
    );
  }

  if (!roadmap || !roadmap.topics || roadmap.topics.length === 0) {
    // Show default roadmap instead of empty state
    const defaultRoadmap = {
      level: 'Beginner',
      total_topics: 4,
      estimated_total_hours: 40,
      estimated_weeks: 4,
      topics: [
        {
          id: 1,
          title: 'Arrays & Basic Operations',
          difficulty: 'Beginner',
          description: 'Master array fundamentals and basic operations',
          status: 'unlocked',
          estimated_hours: 10,
          key_problems: ['Two Sum', 'Best Time to Buy Stock', 'Contains Duplicate'],
          resources: ['https://leetcode.com/tag/array/', 'https://www.geeksforgeeks.org/array-data-structure/']
        },
        {
          id: 2,
          title: 'Strings & Pattern Matching',
          difficulty: 'Beginner',
          description: 'String manipulation and pattern matching',
          status: 'locked',
          estimated_hours: 10,
          key_problems: ['Valid Palindrome', 'Reverse String', 'First Unique Character'],
          resources: ['https://leetcode.com/tag/string/', 'https://www.geeksforgeeks.org/string-data-structure/']
        },
        {
          id: 3,
          title: 'Basic Recursion',
          difficulty: 'Beginner',
          description: 'Understanding recursive thinking',
          status: 'locked',
          estimated_hours: 10,
          key_problems: ['Fibonacci', 'Factorial', 'Power of Two'],
          resources: ['https://leetcode.com/tag/recursion/', 'https://www.geeksforgeeks.org/recursion/']
        },
        {
          id: 4,
          title: 'Searching & Sorting',
          difficulty: 'Beginner',
          description: 'Linear search, binary search, and basic sorting',
          status: 'locked',
          estimated_hours: 10,
          key_problems: ['Binary Search', 'Merge Sorted Array', 'Sort Colors'],
          resources: ['https://www.geeksforgeeks.org/searching-algorithms/', 'https://www.geeksforgeeks.org/sorting-algorithms/']
        }
      ]
    };
    
    return (
      <div className="duolingo-roadmap" style={{minHeight: '400px'}}>
        <div className="roadmap-header">
          <h1>Your DSA Learning Path</h1>
          <div className="roadmap-stats">
            <div className="stat">
              <span className="stat-label">Level:</span>
              <span className="stat-value">Default Beginner</span>
            </div>
            <div className="stat">
              <span className="stat-label">Topics:</span>
              <span className="stat-value">4</span>
            </div>
            <div className="stat">
              <span className="stat-label">Est. Time:</span>
              <span className="stat-value">40h</span>
            </div>
          </div>
          <p style={{textAlign: 'center', color: '#6b7280', marginTop: '10px'}}>
            This is a default roadmap. Take the skill assessment for a personalized path!
          </p>
          <div style={{textAlign: 'center', marginTop: '10px'}}>
            <button onClick={fetchRoadmap} className="retry-btn" style={{marginRight: '10px'}}>
              Load My Roadmap
            </button>
            <button onClick={() => window.location.href = '/dashboard'} className="assessment-btn">
              Take Assessment
            </button>
          </div>
        </div>
        
        {/* Show default roadmap */}
        <div className="roadmap-path">
          {defaultRoadmap.topics.map((topic, index) => (
            <div key={topic.id} className="topic-container">
              {index > 0 && <div className="connection-line" />}
              <div className={`topic-node ${topic.status}`} style={{ borderColor: getDifficultyColor(topic.difficulty) }}>
                <div className="node-icon">{getStatusIcon(topic.status)}</div>
                <div className="node-content">
                  <h3 className="node-title">{topic.title}</h3>
                  <p className="node-description">{topic.description}</p>
                  <div className="node-meta">
                    <span className="difficulty-badge" style={{ backgroundColor: getDifficultyColor(topic.difficulty) }}>
                      {topic.difficulty}
                    </span>
                    <span className="time-estimate">~{topic.estimated_hours}h</span>
                  </div>
                  <div className="problems-list">
                    <h4>Key Problems:</h4>
                    <ul>
                      {topic.key_problems.map((problem, idx) => (
                        <li key={idx}>{problem}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="resources-list">
                    <h4>Resources:</h4>
                    <div className="resource-links">
                      {topic.resources.map((resource, idx) => (
                        <a key={idx} href={resource} target="_blank" rel="noopener noreferrer" className="resource-link">
                          Study Material {idx + 1}
                        </a>
                      ))}
                    </div>
                  </div>
                  <div className="node-actions">
                    {topic.status === 'unlocked' ? (
                      <div className="complete-btn" style={{background: '#22c55e', color: 'white', padding: '8px 16px', borderRadius: '8px'}}>
                        Start Learning
                      </div>
                    ) : (
                      <div className="locked-badge">Complete previous topics to unlock</div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Use new RoadmapUI component
  return <RoadmapUI />;
}