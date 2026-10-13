import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from './api';
import Navigation from './Navigation';
import './UserProfile.css';

export default function UserProfile({ user: propUser, onLogout }) {
  const navigate = useNavigate();
  const [profileData, setProfileData] = useState({});
  const [profileLinks, setProfileLinks] = useState({
    leetcode: '',
    hackerrank: ''
  });
  const [badges, setBadges] = useState([]);
  const [selectedAvatar, setSelectedAvatar] = useState(null);
  const [showAvatarSelector, setShowAvatarSelector] = useState(false);
  const [platformProgress, setPlatformProgress] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');

  // Use prop user or fallback to localStorage
  const user = propUser || JSON.parse(localStorage.getItem('user') || '{}');

  useEffect(() => {
    if (!user?.email) {
      console.error('[PROFILE] No user data available');
      navigate('/');
      return;
    }
    loadUserProfile();
  }, [user?.email, navigate]);

  const loadUserProfile = async () => {
    try {
      setLoading(true);
      setError('');
      console.log('[PROFILE] Loading user profile data...');
      
      // Load profile data
      const data = await api.getUserProfile();
      console.log('[PROFILE] Profile data loaded:', data);
      
      setProfileData(data);
      
      // Load saved profile links
      if (data.profile_links) {
        const links = {
          leetcode: data.profile_links.leetcode || '',
          hackerrank: data.profile_links.hackerrank || ''
        };
        setProfileLinks(links);
        console.log('[PROFILE] Profile links loaded:', links);
      }
      
      // Set current avatar
      if (data.avatar) {
        setSelectedAvatar(data.avatar);
        console.log('[PROFILE] Avatar loaded:', data.avatar);
      }
      
      // Load progress data if links exist
      if (data.profile_links && (data.profile_links.leetcode || data.profile_links.hackerrank)) {
        try {
          console.log('[PROFILE] Loading progress data...');
          const progressData = await api.getProfileProgress();
          console.log('[PROFILE] Progress data loaded:', progressData);
          setPlatformProgress(progressData.platform_progress || {});
        } catch (progressError) {
          console.error('[PROFILE] Failed to load progress:', progressError);
          setPlatformProgress({});
        }
      }
      
      // Load badges
      try {
        const badgesData = await api.get('/api/profile/badges');
        setBadges(badgesData.badges || []);
        console.log('[PROFILE] Badges loaded:', badgesData.badges?.length || 0);
      } catch (badgesError) {
        console.error('[PROFILE] Failed to load badges:', badgesError);
        setBadges([]);
      }
      
    } catch (error) {
      console.error('[PROFILE] Failed to load profile:', error);
      setError('Failed to load profile data. Please try refreshing the page.');
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
      setError('');
      console.log('[PROFILE] Saving profile links:', profileLinks);
      
      const response = await api.updateProfileLinks(profileLinks);
      console.log('[PROFILE] Save response:', response);
      
      // Update progress immediately from the response
      if (response.platform_progress) {
        setPlatformProgress(response.platform_progress);
        console.log('[PROFILE] Progress updated from save response:', response.platform_progress);
      } else {
        // Fallback: refresh progress separately
        console.log('[PROFILE] No progress in response, refreshing separately...');
        await refreshProgress();
      }
      
      alert('Profile links saved and progress updated successfully!');
    } catch (error) {
      console.error('[PROFILE] Failed to save profile links:', error);
      setError(`Failed to save profile links: ${error.message}`);
    } finally {
      setSaving(false);
    }
  };

  const refreshProgress = async () => {
    try {
      setRefreshing(true);
      setError('');
      console.log('[PROFILE] Refreshing progress data...');
      
      // Use the sync endpoint
      const response = await api.syncProgress();
      console.log('[PROFILE] Sync response:', response);
      
      setPlatformProgress(response.platform_progress || {});
      
      console.log('[PROFILE] Progress data refreshed successfully');
      alert('Progress synced successfully with latest data!');
    } catch (error) {
      console.error('[PROFILE] Failed to refresh progress:', error);
      setError(`Failed to refresh progress: ${error.message}`);
    } finally {
      setRefreshing(false);
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

  const predefinedAvatars = {
    male: [
      '👨💻', '👨🎓', '👨🔬', '👨💼', '🧑💻', '🧑🎓', '🧑🔬', '🧑💼'
    ],
    female: [
      '👩💻', '👩🎓', '👩🔬', '👩💼', '👩🚀', '👩🏫', '👩⚕️', '👩🎨'
    ]
  };

  const handleAvatarChange = async (avatar) => {
    try {
      await api.updateAvatar(avatar);
      setSelectedAvatar(avatar);
      setShowAvatarSelector(false);
      
      // Update localStorage user data
      const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
      const updatedUser = { ...currentUser, avatar };
      localStorage.setItem('user', JSON.stringify(updatedUser));
    } catch (error) {
      console.error('Failed to update avatar:', error);
      setError('Failed to update avatar. Please try again.');
    }
  };

  const handleLogout = () => {
    if (onLogout) {
      onLogout();
    } else {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      navigate('/');
    }
  };

  // Get dynamic username with fallback
  const getDynamicUsername = () => {
    return user?.username || user?.name || profileData?.username || profileData?.name || 'User';
  };

  if (loading) {
    return (
      <div className="profile-container">
        <Navigation user={user} onLogout={handleLogout} />
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading your profile...</p>
        </div>
      </div>
    );
  }

  if (error && !profileData.email) {
    return (
      <div className="profile-container">
        <Navigation user={user} onLogout={handleLogout} />
        <div className="error-state">
          <h2>Profile Error</h2>
          <p>{error}</p>
          <button onClick={loadUserProfile} className="retry-button">
            Retry Loading Profile
          </button>
        </div>
      </div>
    );
  }

  const overallScore = calculateOverallScore();

  return (
    <>
      <Navigation user={user} onLogout={handleLogout} />
      <div className="profile-container">
        {/* Error Message */}
        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            {error}
            <button onClick={() => setError('')} className="close-error">×</button>
          </div>
        )}

        {/* Header Section */}
        <div className="profile-header">
          <div className="header-content">
            <div className="profile-avatar-large" onClick={() => setShowAvatarSelector(true)}>
              {selectedAvatar ? (
                <div className="avatar-emoji">{selectedAvatar}</div>
              ) : user?.avatar ? (
                <img src={user.avatar} alt="Profile" />
              ) : (
                <div className="avatar-placeholder-large">
                  {getDynamicUsername().charAt(0).toUpperCase()}
                </div>
              )}
              <div className="avatar-overlay">
                <span>Change Avatar</span>
              </div>
            </div>
            <div className="profile-info">
              <h1 className="profile-name">{getDynamicUsername()}</h1>
              <p className="profile-email">{user?.email || profileData?.email}</p>
              <div className="profile-badges">
                <span className="skill-badge">{user?.skill_level || profileData?.skill_level || 'Beginner'}</span>
                {(user?.assessment_taken || profileData?.assessment_taken) && (
                  <span className="assessment-badge">✅ Assessed</span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Profile Section */}
        <div className="unified-profile-section">
          <div className="profile-card glass-card">
            <h2 className="card-title">👤 Complete Profile</h2>
            
            {/* User Information */}
            <div className="profile-subsection">
              <h3 className="subsection-title">Personal Information</h3>
              <div className="info-grid">
                <div className="info-item">
                  <span className="info-label">Username</span>
                  <span className="info-value">{getDynamicUsername()}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Email</span>
                  <span className="info-value">{user?.email || profileData?.email}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Member Since</span>
                  <span className="info-value">{profileData?.join_date || 'Recently'}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Skill Level</span>
                  <span className="info-value">{user?.skill_level || profileData?.skill_level || 'Beginner'}</span>
                </div>
              </div>
            </div>

            {/* Coding Platform Accounts */}
            <div className="profile-subsection">
              <div className="subsection-header">
                <h3 className="subsection-title">Coding Platform Accounts</h3>
                <div className="sync-controls">
                  <button 
                    className="btn-refresh"
                    onClick={refreshProgress}
                    disabled={refreshing}
                  >
                    {refreshing ? '🔄' : '🔄'} {refreshing ? 'Syncing...' : 'Sync Now'}
                  </button>
                </div>
              </div>

              {/* Platform Account Display */}
              <div className="platform-accounts">
                <div className="account-display">
                  <div className="account-header">
                    <span className="platform-icon">🟠</span>
                    <h4>LeetCode Account</h4>
                  </div>
                  <div className="account-info">
                    {profileLinks.leetcode ? (
                      <div className="account-connected">
                        <span className="account-username">@{profileLinks.leetcode}</span>
                        <span className="connection-status connected">✅ Connected</span>
                      </div>
                    ) : (
                      <div className="account-setup">
                        <input
                          type="text"
                          className="platform-input"
                          value={profileLinks.leetcode}
                          onChange={(e) => handleLinkChange('leetcode', e.target.value)}
                          placeholder="Enter your LeetCode username"
                        />
                      </div>
                    )}
                  </div>
                </div>

                <div className="account-display">
                  <div className="account-header">
                    <span className="platform-icon">🟢</span>
                    <h4>HackerRank Account</h4>
                  </div>
                  <div className="account-info">
                    {profileLinks.hackerrank ? (
                      <div className="account-connected">
                        <span className="account-username">@{profileLinks.hackerrank}</span>
                        <span className="connection-status connected">✅ Connected</span>
                      </div>
                    ) : (
                      <div className="account-setup">
                        <input
                          type="text"
                          className="platform-input"
                          value={profileLinks.hackerrank}
                          onChange={(e) => handleLinkChange('hackerrank', e.target.value)}
                          placeholder="Enter your HackerRank username"
                        />
                      </div>
                    )}
                  </div>
                </div>

                {(!profileLinks.leetcode || !profileLinks.hackerrank) && (
                  <button 
                    className="btn-save"
                    onClick={saveProfileLinks}
                    disabled={saving}
                  >
                    {saving ? 'Connecting...' : 'Connect Accounts'}
                  </button>
                )}
              </div>

              {/* Platform Stats */}
              {Object.keys(platformProgress).length > 0 ? (
                <div className="platform-stats">
                  <h3 className="stats-title">Your Coding Progress</h3>
                  
                  <div className="stats-grid">
                    {platformProgress.leetcode && (
                      <div className="stat-card leetcode-card">
                        <div className="stat-header">
                          <span className="platform-icon">🟠</span>
                          <h4>LeetCode</h4>
                        </div>
                        <div className="stat-content">
                          <div className="stat-main">
                            <span className="stat-number">{platformProgress.leetcode.solved || 0}</span>
                            <span className="stat-label">Problems Solved</span>
                          </div>
                          <div className="stat-breakdown">
                            <div className="difficulty-stat easy">
                              <span>Easy: {platformProgress.leetcode.easy || 0}</span>
                            </div>
                            <div className="difficulty-stat medium">
                              <span>Medium: {platformProgress.leetcode.medium || 0}</span>
                            </div>
                            <div className="difficulty-stat hard">
                              <span>Hard: {platformProgress.leetcode.hard || 0}</span>
                            </div>
                            {platformProgress.leetcode.weekly_solved !== undefined && (
                              <div className="weekly-stat">
                                <span>🔥 This week: {platformProgress.leetcode.weekly_solved}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    )}

                    {platformProgress.hackerrank && (
                      <div className="stat-card hackerrank-card">
                        <div className="stat-header">
                          <span className="platform-icon">🟢</span>
                          <h4>HackerRank</h4>
                        </div>
                        <div className="stat-content">
                          <div className="stat-main">
                            <span className="stat-number">{platformProgress.hackerrank.stars || 0}</span>
                            <span className="stat-label">Stars</span>
                          </div>
                          <div className="stat-breakdown">
                            <div className="achievement-stat">
                              <span>Certificates: {platformProgress.hackerrank.certificates || 0}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ) : (profileLinks.leetcode || profileLinks.hackerrank) && (
                <div className="no-progress-message">
                  <div className="message-card">
                    <h3>🔍 No Progress Data Found</h3>
                    <p>We couldn't find progress data for your usernames. This might be because:</p>
                    <ul>
                      <li>The username doesn't exist on the platform</li>
                      <li>The profile is private or new</li>
                      <li>API rate limits are active</li>
                    </ul>
                    <div className="suggested-usernames">
                      <h4>💡 Try these working usernames for testing:</h4>
                      <div className="username-suggestions">
                        <div className="suggestion">
                          <strong>LeetCode:</strong> <code>awice</code> (3,148 problems solved)
                        </div>
                        <div className="suggestion">
                          <strong>LeetCode:</strong> <code>leetcode</code> (45 problems solved)
                        </div>
                      </div>
                      <p className="suggestion-note">
                        These are real, active accounts that will show actual progress data.
                      </p>
                    </div>
                    <button 
                      className="btn-refresh"
                      onClick={refreshProgress}
                      disabled={refreshing}
                    >
                      {refreshing ? 'Retrying...' : 'Try Again'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Badges Section */}
        {badges.length > 0 && (
          <div className="badges-section">
            <div className="badges-card glass-card">
              <h2 className="card-title">🏅 Your Achievements</h2>
              <div className="badges-grid">
                {badges.map((badge) => (
                  <div key={badge.id} className="badge-item" style={{'--badge-color': badge.color}}>
                    <div className="badge-icon">{badge.icon}</div>
                    <div className="badge-info">
                      <h4 className="badge-name">{badge.name}</h4>
                      <p className="badge-description">{badge.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Overall Progress Summary */}
        {Object.keys(platformProgress).length > 0 && (
          <div className="progress-summary">
            <div className="summary-card glass-card">
              <h2 className="card-title">🏆 Overall Progress</h2>
              <div className="progress-circle">
                <div className="circle-progress" style={{'--progress': `${overallScore}%`}}>
                  <span className="progress-value">{overallScore}</span>
                  <span className="progress-label">Overall Score</span>
                </div>
              </div>
              <div className="progress-insights">
                <p>
                  {overallScore >= 80 ? "🔥 Excellent progress! You're doing great!" :
                   overallScore >= 60 ? "👍 Good progress! Keep it up!" :
                   overallScore >= 40 ? "📈 Making steady progress!" :
                   "🚀 Just getting started! Keep practicing!"}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Avatar Selector Modal */}
        {showAvatarSelector && (
          <div className="avatar-modal" onClick={() => setShowAvatarSelector(false)}>
            <div className="avatar-selector" onClick={(e) => e.stopPropagation()}>
              <h3>Choose Your Avatar</h3>
              <div className="avatar-categories">
                <div className="avatar-category">
                  <h4>Male Avatars</h4>
                  <div className="avatars-grid">
                    {predefinedAvatars.male.map((avatar, index) => (
                      <div
                        key={`male-${index}`}
                        className={`avatar-option ${selectedAvatar === avatar ? 'selected' : ''}`}
                        onClick={() => handleAvatarChange(avatar)}
                      >
                        {avatar}
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="avatar-category">
                  <h4>Female Avatars</h4>
                  <div className="avatars-grid">
                    {predefinedAvatars.female.map((avatar, index) => (
                      <div
                        key={`female-${index}`}
                        className={`avatar-option ${selectedAvatar === avatar ? 'selected' : ''}`}
                        onClick={() => handleAvatarChange(avatar)}
                      >
                        {avatar}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              <button className="close-modal" onClick={() => setShowAvatarSelector(false)}>
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </>
  );
}