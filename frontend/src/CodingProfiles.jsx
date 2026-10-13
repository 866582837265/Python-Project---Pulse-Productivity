import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './CodingProfiles.css';

export default function CodingProfiles() {
  const [platforms, setPlatforms] = useState({
    leetcode: '',
    hackerrank: ''
  });
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Load existing profile links on component mount
  useEffect(() => {
    loadExistingProfiles();
  }, []);

  const loadExistingProfiles = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5000/api/user/profile', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data.profile_links) {
        setPlatforms({
          leetcode: response.data.profile_links.leetcode || '',
          hackerrank: response.data.profile_links.hackerrank || ''
        });
        
        // If we have existing progress, show it
        if (response.data.platform_progress) {
          setStats(response.data.platform_progress);
        }
      }
    } catch (error) {
      console.error('Failed to load existing profiles:', error);
    }
  };

  const handleInputChange = (platform, value) => {
    setPlatforms(prev => ({
      ...prev,
      [platform]: value
    }));
    setError('');
    setSuccess('');
  };

  const savePlatformUsernames = async () => {
    try {
      setSaving(true);
      setError('');
      setSuccess('');
      
      const token = localStorage.getItem('token');
      
      // Save profile links using the correct endpoint
      const response = await axios.post('http://localhost:5000/api/profile/update_links', platforms, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data.success) {
        setSuccess('Profile links saved successfully!');
        
        // Update stats with immediate sync results
        if (response.data.platform_progress) {
          setStats(response.data.platform_progress);
        } else {
          // Fetch stats separately if not included in response
          await fetchPlatformStats();
        }
      } else {
        setError(response.data.error || 'Failed to save profile links');
      }
    } catch (error) {
      console.error('Failed to save platform usernames:', error);
      setError(error.response?.data?.error || 'Failed to save profile links');
    } finally {
      setSaving(false);
    }
  };

  const fetchPlatformStats = async () => {
    if (!platforms.leetcode && !platforms.hackerrank) {
      setError('Please enter at least one platform username');
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      const token = localStorage.getItem('token');
      
      // Use the profile progress endpoint for fetching stats
      const response = await axios.get('http://localhost:5000/api/profile/progress', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data.success) {
        setStats(response.data.platform_progress || {});
        if (Object.keys(response.data.platform_progress || {}).length === 0) {
          setError('No progress data found. Please check your usernames and try again.');
        } else {
          setSuccess('Progress data fetched successfully!');
        }
      } else {
        setError(response.data.error || 'Failed to fetch progress data');
      }
    } catch (error) {
      console.error('Failed to fetch platform stats:', error);
      setError(error.response?.data?.error || 'Failed to fetch progress data. Please check your usernames and try again.');
    } finally {
      setLoading(false);
    }
  };

  const syncProgress = async () => {
    try {
      setLoading(true);
      setError('');
      
      const token = localStorage.getItem('token');
      
      const response = await axios.post('http://localhost:5000/api/profile/sync-progress', {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data.success) {
        setStats(response.data.platform_progress || {});
        setSuccess('Progress synced successfully!');
      } else {
        setError(response.data.error || 'Failed to sync progress');
      }
    } catch (error) {
      console.error('Failed to sync progress:', error);
      setError(error.response?.data?.error || 'Failed to sync progress');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="coding-profiles">
      <div className="profiles-header">
        <h2>Coding Platform Integration</h2>
        <p>Connect your coding profiles to track your progress across platforms</p>
      </div>

      {/* Error and Success Messages */}
      {error && (
        <div className="message error-message">
          <span className="message-icon">❌</span>
          {error}
        </div>
      )}
      
      {success && (
        <div className="message success-message">
          <span className="message-icon">✅</span>
          {success}
        </div>
      )}

      <div className="platform-forms">
        <div className="platform-form">
          <label>
            <span className="platform-icon">🟠</span>
            LeetCode Username
          </label>
          <input
            type="text"
            value={platforms.leetcode}
            onChange={(e) => handleInputChange('leetcode', e.target.value)}
            placeholder="Enter your LeetCode username"
            disabled={saving || loading}
          />
        </div>

        <div className="platform-form">
          <label>
            <span className="platform-icon">🟢</span>
            HackerRank Username
          </label>
          <input
            type="text"
            value={platforms.hackerrank}
            onChange={(e) => handleInputChange('hackerrank', e.target.value)}
            placeholder="Enter your HackerRank username"
            disabled={saving || loading}
          />
        </div>

        <div className="button-group">
          <button 
            className="save-button"
            onClick={savePlatformUsernames}
            disabled={saving || loading || (!platforms.leetcode && !platforms.hackerrank)}
          >
            {saving ? 'Saving...' : 'Save Profile Links'}
          </button>

          <button 
            className="fetch-button"
            onClick={fetchPlatformStats}
            disabled={saving || loading || (!platforms.leetcode && !platforms.hackerrank)}
          >
            {loading ? 'Fetching...' : 'Fetch Progress'}
          </button>

          {Object.keys(stats).length > 0 && (
            <button 
              className="sync-button"
              onClick={syncProgress}
              disabled={saving || loading}
            >
              {loading ? 'Syncing...' : 'Sync Progress'}
            </button>
          )}
        </div>
      </div>

      {loading && (
        <div className="loading-stats">
          <div className="loading-spinner"></div>
          <p>Fetching your coding stats...</p>
        </div>
      )}

      {Object.keys(stats).length > 0 && !loading && (
        <div className="platform-stats">
          <h3>Your Coding Stats</h3>
          
          {stats.leetcode && (
            <div className="stat-card leetcode">
              <div className="stat-header">
                <span className="platform-icon">🟠</span>
                <h4>LeetCode</h4>
              </div>
              <div className="stat-content">
                <div className="stat-item">
                  <span className="stat-label">Problems Solved:</span>
                  <span className="stat-value">{stats.leetcode.solved || 0}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Easy:</span>
                  <span className="stat-value">{stats.leetcode.easy || 0}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Medium:</span>
                  <span className="stat-value">{stats.leetcode.medium || 0}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Hard:</span>
                  <span className="stat-value">{stats.leetcode.hard || 0}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Ranking:</span>
                  <span className="stat-value">{stats.leetcode.ranking || 'N/A'}</span>
                </div>
                {stats.leetcode.weekly_solved !== undefined && (
                  <div className="stat-item">
                    <span className="stat-label">Weekly Solved:</span>
                    <span className="stat-value">{stats.leetcode.weekly_solved}</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {stats.hackerrank && (
            <div className="stat-card hackerrank">
              <div className="stat-header">
                <span className="platform-icon">🟢</span>
                <h4>HackerRank</h4>
              </div>
              <div className="stat-content">
                <div className="stat-item">
                  <span className="stat-label">Stars:</span>
                  <span className="stat-value">{stats.hackerrank.stars || 0}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Problems Solved:</span>
                  <span className="stat-value">{stats.hackerrank.problems_solved || 0}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Badges:</span>
                  <span className="stat-value">{stats.hackerrank.badges || 0}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Certificates:</span>
                  <span className="stat-value">{stats.hackerrank.certificates || 0}</span>
                </div>
              </div>
            </div>
          )}

          {stats.leetcode?.last_updated && (
            <div className="last-updated">
              <small>Last updated: {new Date(stats.leetcode.last_updated).toLocaleString()}</small>
            </div>
          )}
        </div>
      )}

      {Object.keys(stats).length === 0 && !loading && !error && (platforms.leetcode || platforms.hackerrank) && (
        <div className="no-stats">
          <p>No progress data available. Click "Fetch Progress" to load your stats.</p>
        </div>
      )}
    </div>
  );
}