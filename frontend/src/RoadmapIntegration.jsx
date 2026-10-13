import React, { useState, useEffect } from "react";
import { API_BASE_URL } from "./config";
import DuolingoRoadmap from "./DuolingoRoadmap";

// Example of how to integrate Duolingo roadmap into existing Dashboard
export default function RoadmapIntegration({ user }) {
  const [showRoadmap, setShowRoadmap] = useState(false);
  const [roadmapData, setRoadmapData] = useState(null);

  useEffect(() => {
    // Check if user has completed assessment and has roadmap
    if (user?.assessment_taken) {
      fetchRoadmapPreview();
    }
  }, [user]);

  const fetchRoadmapPreview = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${API_BASE_URL}/api/roadmap`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const data = await response.json();
      if (data.success) {
        setRoadmapData(data.roadmap);
      }
    } catch (error) {
      console.error("Failed to fetch roadmap preview:", error);
    }
  };

  if (!user?.assessment_taken) {
    return (
      <div className="roadmap-integration">
        <div className="assessment-prompt">
          <h3>🎯 Get Your Personalized Learning Path</h3>
          <p>Complete the skill assessment to unlock your Duolingo-style DSA roadmap!</p>
          <button className="assessment-btn">
            Take Assessment
          </button>
        </div>
      </div>
    );
  }

  if (showRoadmap) {
    return <DuolingoRoadmap />;
  }

  return (
    <div className="roadmap-integration">
      <div className="roadmap-preview">
        <h3>🗺️ Your Learning Path</h3>
        
        {roadmapData && (
          <div className="preview-stats">
            <div className="preview-stat">
              <span className="stat-number">{roadmapData.progress.completion_percentage}%</span>
              <span className="stat-label">Complete</span>
            </div>
            <div className="preview-stat">
              <span className="stat-number">{roadmapData.total_topics}</span>
              <span className="stat-label">Topics</span>
            </div>
            <div className="preview-stat">
              <span className="stat-number">{roadmapData.estimated_completion_weeks}</span>
              <span className="stat-label">Weeks</span>
            </div>
          </div>
        )}

        <div className="current-topic">
          <h4>📚 Current Topic</h4>
          <p>{roadmapData?.progress.current_topic || "Loading..."}</p>
        </div>

        <button 
          onClick={() => setShowRoadmap(true)}
          className="view-roadmap-btn"
        >
          View Full Roadmap
        </button>
      </div>
    </div>
  );
}