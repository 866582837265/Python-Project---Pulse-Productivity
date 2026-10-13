import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from './api';
import { useAuth } from './AuthContext';
import Navigation from './Navigation';
import './UserProfile.css';

export default function EnhancedUserProfile() {
  const navigate = useNavigate();
  const { user, updateUser } = useAuth();
  const [profileData, setProfileData] = useState({});
  const [profileLinks, setProfileLinks] = useState({ leetcode: '', hackerrank: '' });
  const [platformProgress, setPlatformProgress] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState(null);
  const [syncStatus, setSyncStatus] = useState('');

  useEffect(() => {
    loadUserProfile();
  }, []);

  const loadUserProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await api.getUserProfile();
      setProfileData(data);
      
      if (data.profile_links) {
        setProfileLinks({
          leetcode: data.profile_links.leetcode || '',
          hackerrank: data.profile_links.hackerrank || ''
        });
      }
      
      if (data.platform_progress) {
        setPlatformProgress(data.platform_progress);
      }
      
    } catch (error) {
      console.error('[PROFILE] Load failed:', error);
      setError(`Failed to load profile: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleLinkChange = (platform, value) => {
    setProfileLinks(prev => ({
      ...prev,
      [platform]: value.trim()
    }));
  };

  const saveProfileLinks = async () => {
    try {
      setSaving(true);
      setError(null);
      setSyncStatus('Saving profile links...');
      
      const response = await api.updateProfileLinks(profileLinks);
      
      if (response.platform_progress) {
        setPlatformProgress(response.platform_progress);
        setSyncStatus('Profile links saved and progress synced!');
      } else {
        setSyncStatus('Profile links saved. Syncing progress...');
        await syncProgress();
      }
      
      setTimeout(() => setSyncStatus(''), 3000);
      
    } catch (error) {
      console.error('[PROFILE] Save failed:', error);
      setError(`Failed to save: ${error.message}`);
      setSyncStatus('');
    } finally {
      setSaving(false);
    }
  };

  const syncProgress = async () => {
    try {
      setSyncing(true);
      setError(null);
      setSyncStatus('Fetching latest progress from platforms...');
      
      const response = await api.syncProgress();
      
      if (response.platform_progress) {
        setPlatformProgress(response.platform_progress);
        setSyncStatus('Progress synced successfully!');
        
        // Show detailed sync results
        const leetcodeData = response.platform_progress.leetcode;
        const hackerrankData = response.platform_progress.hackerrank;
        
        let syncDetails = [];
        if (leetcodeData) {
          syncDetails.push(`LeetCode: ${leetcodeData.solved} problems`);
        }
        if (hackerrankData) {
          syncDetails.push(`HackerRank: ${hackerrankData.stars} stars`);
        }
        
        if (syncDetails.length > 0) {
          setSyncStatus(`Synced: ${syncDetails.join(', ')}`);
        }
      } else {
        setSyncStatus('Sync completed but no data returned');
      }
      
      setTimeout(() => setSyncStatus(''), 5000);
      
    } catch (error) {
      console.error('[PROFILE] Sync failed:', error);
      setError(`Sync failed: ${error.message}`);
      setSyncStatus('');
    } finally {
      setSyncing(false);
    }
  };

  const calculateOverallScore = () => {
    let totalScore = 0;
    let platforms = 0;

    if (platformProgress.leetcode?.solved) {
      totalScore += Math.min(platformProgress.leetcode.solved * 0.5, 50);
      platforms++;
    }
    if (platformProgress.hackerrank?.stars) {
      totalScore += platformProgress.hackerrank.stars * 10;
      platforms++;
    }

    return platforms > 0 ? Math.round(totalScore / platforms) : 0;
  };

  const handleLogout = () => {
    const { logout } = useAuth();
    logout();
    navigate('/');
  };

  if (loading) {
    return (
      <>
        <Navigation user={user} onLogout={handleLogout} />
        <div className="profile-container">
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <p>Loading your profile...</p>
          </div>
        </div>
      </>
    );
  }

  const overallScore = calculateOverallScore();

  return (
    <>
      <Navigation user={user} onLogout={handleLogout} />
      <div className="profile-container">
        
        {/* Error Display */}
        {error && (
          <div className="error-banner">
            <span className="error-icon">⚠️</span>
            <span className="error-text">{error}</span>
            <button onClick={() => setError(null)} className="error-close">×</button>
          </div>
        )}
        
        {/* Sync Status */}
        {syncStatus && (
          <div className="sync-status-banner">
            <span className="sync-icon">🔄</span>
            <span className="sync-text">{syncStatus}</span>
          </div>
        )}

        {/* Profile Header */}
        <div className="profile-header">
          <div className="header-content">
            <div className="profile-avatar-large">
              <div className="avatar-placeholder-large">
                {(user?.username || profileData?.username || 'User').charAt(0).toUpperCase()}
              </div>
            </div>
            <div className="profile-info">
              <h1 className="profile-name">{user?.username || profileData?.username || 'User'}</h1>
              <p className="profile-email">{user?.email || profileData?.email}</p>
              <div className="profile-badges">
                <span className="skill-badge">{user?.skill_level || profileData?.skill_level || 'Beginner'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Platform Integration Section */}
        <div className="platform-integration-section">
          <div className="platform-card glass-card">
            <div className="card-header">
              <h2 className="card-title">🔗 Platform Integration</h2>
              <div className="sync-controls">
                <button 
                  className="btn-sync"
                  onClick={syncProgress}
                  disabled={syncing || saving}
                >
                  {syncing ? '🔄 Syncing...' : '🔄 Sync Now'}
                </button>
              </div>
            </div>

            {/* Platform Account Setup */}
            <div className="platform-setup">
              <div className="platform-input-group">
                <label className="platform-label">
                  <span className="platform-icon">🟠</span>
                  LeetCode Username
                </label>
                <div className="input-with-status">
                  <input
                    type="text"
                    className="platform-input"
                    value={profileLinks.leetcode}
                    onChange={(e) => handleLinkChange('leetcode', e.target.value)}
                    placeholder="Enter your LeetCode username"
                    disabled={saving}
                  />
                  {platformProgress.leetcode && (
                    <span className="connection-status connected">✅</span>
                  )}
                </div>
              </div>

              <div className="platform-input-group">
                <label className="platform-label">
                  <span className="platform-icon">🟢</span>
                  HackerRank Username
                </label>
                <div className="input-with-status">
                  <input
                    type="text"
                    className="platform-input"
                    value={profileLinks.hackerrank}
                    onChange={(e) => handleLinkChange('hackerrank', e.target.value)}
                    placeholder="Enter your HackerRank username"
                    disabled={saving}
                  />
                  {platformProgress.hackerrank && (
                    <span className="connection-status connected">✅</span>
                  )}
                </div>
              </div>

              <button 
                className="btn-save-links"
                onClick={saveProfileLinks}
                disabled={saving || syncing || (!profileLinks.leetcode && !profileLinks.hackerrank)}
              >
                {saving ? 'Saving & Syncing...' : 'Save & Sync Progress'}
              </button>
            </div>

            {/* Progress Display */}
            {Object.keys(platformProgress).length > 0 && (
              <div className="progress-display">
                <h3 className="progress-title">📊 Your Progress</h3>
                
                <div className="progress-grid">
                  {platformProgress.leetcode && (
                    <div className="progress-card leetcode-card">
                      <div className="progress-header">
                        <span className="platform-icon">🟠</span>
                        <h4>LeetCode</h4>
                        {platformProgress.leetcode.demo_data && (
                          <span className="demo-badge">Demo</span>
                        )}
                      </div>
                      <div className="progress-stats">
                        <div className="main-stat">
                          <span className="stat-number">{platformProgress.leetcode.solved || 0}</span>
                          <span className="stat-label">Problems Solved</span>
                        </div>
                        <div className="sub-stats">
                          <div className="sub-stat easy">
                            <span>Easy: {platformProgress.leetcode.easy || 0}</span>
                          </div>
                          <div className="sub-stat medium">
                            <span>Medium: {platformProgress.leetcode.medium || 0}</span>
                          </div>
                          <div className="sub-stat hard">
                            <span>Hard: {platformProgress.leetcode.hard || 0}</span>
                          </div>
                        </div>
                        {platformProgress.leetcode.ranking && (
                          <div className="ranking-stat">
                            <span>Ranking: #{platformProgress.leetcode.ranking.toLocaleString()}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {platformProgress.hackerrank && (
                    <div className="progress-card hackerrank-card">
                      <div className="progress-header">
                        <span className="platform-icon">🟢</span>
                        <h4>HackerRank</h4>
                        {platformProgress.hackerrank.demo_data && (
                          <span className="demo-badge">Demo</span>
                        )}
                      </div>
                      <div className="progress-stats">
                        <div className="main-stat">
                          <span className="stat-number">{platformProgress.hackerrank.stars || 0}</span>
                          <span className="stat-label">Stars</span>
                        </div>
                        <div className="sub-stats">
                          <div className="sub-stat">
                            <span>Certificates: {platformProgress.hackerrank.certificates || 0}</span>
                          </div>
                          <div className="sub-stat">
                            <span>Badges: {platformProgress.hackerrank.badges || 0}</span>
                          </div>
                          <div className="sub-stat">
                            <span>Problems: {platformProgress.hackerrank.problems_solved || 0}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Overall Score */}
                <div className="overall-score-display">
                  <div className="score-circle" style={{'--score': `${overallScore}%`}}>
                    <div className="score-inner">
                      <span className="score-value">{overallScore}</span>
                      <span className="score-label">Overall Score</span>
                    </div>
                  </div>
                  <div className="score-insights">
                    <p>
                      {overallScore >= 80 ? "🔥 Excellent progress!" :
                       overallScore >= 60 ? "👍 Good progress!" :
                       overallScore >= 40 ? "📈 Making progress!" :
                       "🚀 Just getting started!"}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* No Progress Message */}
            {Object.keys(platformProgress).length === 0 && (profileLinks.leetcode || profileLinks.hackerrank) && (
              <div className="no-progress-message">
                <p>🔄 Enter your platform usernames and click "Save & Sync Progress" to see your coding statistics.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}