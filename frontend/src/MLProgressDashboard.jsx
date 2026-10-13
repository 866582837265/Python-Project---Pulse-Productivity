import React, { useState, useEffect } from 'react';
import { api } from './api';
import './MLProgressDashboard.css';

export default function MLProgressDashboard({ userEmail }) {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadMLAnalysis();
  }, []);

  const loadMLAnalysis = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await api.get('/api/profile/ml-progress-analysis');
      setAnalysis(response.analysis);
    } catch (err) {
      setError(err.message);
      console.error('Failed to load ML analysis:', err);
    } finally {
      setLoading(false);
    }
  };

  const refreshAnalysis = async () => {
    await loadMLAnalysis();
  };

  if (loading) {
    return (
      <div className="ml-dashboard loading">
        <div className="loading-spinner"></div>
        <p>Analyzing your coding progress...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="ml-dashboard error">
        <p>Failed to load analysis: {error}</p>
        <button onClick={refreshAnalysis} className="retry-btn">Retry</button>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="ml-dashboard empty">
        <p>No analysis available. Please ensure your platform accounts are connected.</p>
        <button onClick={refreshAnalysis} className="analyze-btn">Run Analysis</button>
      </div>
    );
  }

  return (
    <div className="ml-dashboard">
      <div className="dashboard-header">
        <h2>🤖 AI Progress Analysis</h2>
        <button onClick={refreshAnalysis} className="refresh-btn" disabled={loading}>
          {loading ? '🔄' : '🔄'} Refresh
        </button>
      </div>

      {/* Overall Score Circle */}
      <div className="overall-score-section">
        <div className="score-circle-container">
          <div 
            className="score-circle" 
            style={{'--score': `${analysis.overall_score}%`}}
          >
            <div className="score-inner">
              <span className="score-value">{analysis.overall_score}</span>
              <span className="score-label">Overall Score</span>
            </div>
          </div>
          <div className="skill-level">
            <span className={`level-badge ${analysis.level.toLowerCase()}`}>
              {analysis.level}
            </span>
          </div>
        </div>
      </div>

      {/* Score Breakdown */}
      <div className="breakdown-section">
        <h3>📊 Score Breakdown</h3>
        <div className="breakdown-grid">
          {Object.entries(analysis.breakdown).map(([category, score]) => (
            <div key={category} className="breakdown-item">
              <div className="breakdown-header">
                <span className="category-name">
                  {category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </span>
                <span className="category-score">{Math.round(score)}</span>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{width: `${(score / getMaxScore(category)) * 100}%`}}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recommendations */}
      {analysis.recommendations && analysis.recommendations.length > 0 && (
        <div className="recommendations-section">
          <h3>💡 Personalized Recommendations</h3>
          <div className="recommendations-list">
            {analysis.recommendations.map((recommendation, index) => (
              <div key={index} className="recommendation-item">
                <span className="recommendation-icon">🎯</span>
                <span className="recommendation-text">{recommendation}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Feature Analysis */}
      <div className="features-section">
        <h3>🔍 Detailed Analysis</h3>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">📚</div>
            <div className="feature-content">
              <h4>Problem Volume</h4>
              <p>{analysis.features.total_problems} problems solved</p>
              <div className="feature-breakdown">
                <span>Easy: {analysis.features.easy_problems}</span>
                <span>Medium: {analysis.features.medium_problems}</span>
                <span>Hard: {analysis.features.hard_problems}</span>
              </div>
            </div>
          </div>

          <div className="feature-card">
            <div className="feature-icon">⚡</div>
            <div className="feature-content">
              <h4>Weekly Activity</h4>
              <p>{analysis.features.weekly_activity} problems this week</p>
              <div className="activity-indicator">
                <div 
                  className="activity-bar" 
                  style={{width: `${Math.min(analysis.features.weekly_activity * 10, 100)}%`}}
                ></div>
              </div>
            </div>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🎯</div>
            <div className="feature-content">
              <h4>Consistency</h4>
              <p>{Math.round(analysis.features.consistency_score * 100)}% consistent</p>
              <div className="consistency-indicator">
                <div 
                  className="consistency-bar" 
                  style={{width: `${analysis.features.consistency_score * 100}%`}}
                ></div>
              </div>
            </div>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🏆</div>
            <div className="feature-content">
              <h4>Platform Ranking</h4>
              <p>LeetCode: #{analysis.features.leetcode_ranking.toLocaleString()}</p>
              <p>HackerRank: {analysis.features.hackerrank_stars} ⭐</p>
            </div>
          </div>
        </div>
      </div>

      {/* Progress Trend */}
      <div className="trend-section">
        <h3>📈 Progress Trend</h3>
        <div className="trend-indicator">
          <div className="trend-arrow">
            {analysis.features.recent_activity_trend > 0.6 ? '📈' : 
             analysis.features.recent_activity_trend > 0.4 ? '➡️' : '📉'}
          </div>
          <div className="trend-text">
            {analysis.features.recent_activity_trend > 0.6 ? 'Improving' : 
             analysis.features.recent_activity_trend > 0.4 ? 'Stable' : 'Declining'}
          </div>
          <div className="trend-score">
            {Math.round(analysis.features.recent_activity_trend * 100)}%
          </div>
        </div>
      </div>
    </div>
  );
}

function getMaxScore(category) {
  const maxScores = {
    'problem_solving': 25,
    'difficulty_mastery': 20,
    'consistency': 15,
    'platform_ranking': 15,
    'recent_activity': 15,
    'platform_diversity': 10
  };
  return maxScores[category] || 25;
}