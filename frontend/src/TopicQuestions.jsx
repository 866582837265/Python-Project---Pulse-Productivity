import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import arrayBasics from './data/arrayBasics.json';
import './TopicQuestions.css';

export default function TopicQuestions() {
  const { topicId } = useParams();
  const navigate = useNavigate();
  const [topic, setTopic] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('coding');
  const [isBookmarked, setIsBookmarked] = useState(false);

  useEffect(() => {
    fetchTopicDetails();
  }, [topicId]);

  const fetchTopicDetails = async () => {
    try {
      // Use static data instead of API call
      const topicData = {
        id: topicId,
        title: arrayBasics.topic,
        description: `Master ${arrayBasics.topic} with comprehensive practice`,
        difficulty: "Beginner",
        status: "available",
        coding_questions: arrayBasics.coding_questions.map(q => ({
          id: q.id,
          title: q.question,
          question: `Example: ${q.example_input} → ${q.example_output}`,
          starterCode: `// ${q.question}\n// Example: ${q.example_input} → ${q.example_output}\nconsole.log('Your solution here');`
        })),
        mcq_questions: arrayBasics.mcqs
      };
      
      setTopic(topicData);
    } catch (err) {
      console.error('Topic details load error:', err);
      setError(`Failed to load topic: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const startPractice = (subtopicId, type = 'coding') => {
    navigate(`/practice/${subtopicId || topicId}?type=${type}`);
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty?.toLowerCase()) {
      case 'beginner':
      case 'easy': 
        return { bg: 'rgba(34, 197, 94, 0.2)', text: '#4ade80', border: 'rgba(34, 197, 94, 0.3)' };
      case 'intermediate':
      case 'medium': 
        return { bg: 'rgba(251, 191, 36, 0.2)', text: '#fbbf24', border: 'rgba(251, 191, 36, 0.3)' };
      case 'expert':
      case 'hard': 
        return { bg: 'rgba(239, 68, 68, 0.2)', text: '#f87171', border: 'rgba(239, 68, 68, 0.3)' };
      default: 
        return { bg: 'rgba(56, 189, 248, 0.2)', text: '#38bdf8', border: 'rgba(56, 189, 248, 0.3)' };
    }
  };

  const getMotivationalQuote = () => {
    const quotes = [
      "Master the fundamentals, excel in complexity! 🚀",
      "Every algorithm starts with understanding the basics ✨",
      "Level up your DSA journey, one topic at a time! 💪",
      "Practice makes perfect - let's code! 🔥",
      "Transform your thinking, transform your code 🧠",
      "Keep pushing your DSA journey! 💫",
      "Excellence is a habit, not an act! ⭐",
      "Code with passion, learn with purpose! 🎯"
    ];
    return quotes[Math.floor(Math.random() * quotes.length)];
  };

  const ShimmerLoader = () => (
    <div className="shimmer-container">
      <div className="shimmer-line shimmer-title"></div>
      <div className="shimmer-line shimmer-subtitle"></div>
      <div className="shimmer-line shimmer-text"></div>
      <div className="shimmer-line shimmer-text short"></div>
    </div>
  );

  if (loading) {
    return (
      <div className="dashboard-container">
        <nav className="dashboard-nav">
          <div className="nav-content">
            <div className="nav-brand">
              <h1 className="brand-wordmark">Pulse</h1>
            </div>
            <button className="nav-back-btn" onClick={() => navigate('/roadmap')}>
              <span className="back-icon">←</span>
              <span>Back to Roadmap</span>
            </button>
          </div>
        </nav>
        <main className="dashboard-main">
          <div className="loading-state">
            <h2>Loading Topic Content</h2>
            <p>Preparing your learning materials...</p>
          </div>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <nav className="dashboard-nav">
          <div className="nav-content">
            <div className="nav-brand">
              <h1 className="brand-wordmark">Pulse</h1>
            </div>
            <button className="nav-back-btn" onClick={() => navigate('/roadmap')}>
              <span className="back-icon">←</span>
              <span>Back to Roadmap</span>
            </button>
          </div>
        </nav>
        <main className="dashboard-main">
          <div className="error-state">
            <div className="error-icon">⚠️</div>
            <h2>Unable to Load Topic</h2>
            <p>{error}</p>
            <div className="error-actions">
              <button className="btn-primary" onClick={fetchTopicDetails}>
                Try Again
              </button>
              <button className="btn-secondary" onClick={() => navigate('/roadmap')}>
                Back to Roadmap
              </button>
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (!topic) {
    return (
      <div className="dashboard-container">
        <nav className="dashboard-nav">
          <div className="nav-content">
            <div className="nav-brand">
              <h1 className="brand-wordmark">Pulse</h1>
            </div>
            <button className="nav-back-btn" onClick={() => navigate('/roadmap')}>
              <span className="back-icon">←</span>
              <span>Back to Roadmap</span>
            </button>
          </div>
        </nav>
        <main className="dashboard-main">
          <div className="error-state">
            <div className="error-icon">🔍</div>
            <h2>Topic Not Found</h2>
            <button className="btn-primary" onClick={() => navigate('/roadmap')}>
              Back to Roadmap
            </button>
          </div>
        </main>
      </div>
    );
  }

  const difficultyStyle = getDifficultyColor(topic.difficulty);

  return (
    <div className="dashboard-container">
      {/* Navigation */}
      <nav className="dashboard-nav">
        <div className="nav-content">
          <div className="nav-brand">
            <h1 className="brand-wordmark">Pulse</h1>
          </div>
          <div className="nav-links">
            <button 
              className={`nav-link ${activeTab === 'coding' ? 'active' : ''}`}
              onClick={() => setActiveTab('coding')}
            >
              💻 Coding ({topic.coding_questions?.length || 0})
            </button>
            <button 
              className={`nav-link ${activeTab === 'mcq' ? 'active' : ''}`}
              onClick={() => setActiveTab('mcq')}
            >
              🧠 MCQ ({topic.mcq_questions?.length || 0})
            </button>
          </div>
          <div className="nav-profile">
            <button className="nav-back-btn" onClick={() => navigate('/roadmap')}>
              ← Back to Roadmap
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="dashboard-main">
        {/* Welcome Section */}
        <section className="welcome-section">
          <div className="welcome-header">
            <h1 className="dashboard-welcome-text">{topic.title} 📚</h1>
            <p>{topic.description}</p>
          </div>
          
          <div className="quick-stats">
            <div className="stat-card">
              <div className="stat-number">{topic.coding_questions?.length || 0}</div>
              <div className="stat-label">Coding Problems</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{topic.mcq_questions?.length || 0}</div>
              <div className="stat-label">MCQ Questions</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{topic.difficulty}</div>
              <div className="stat-label">Difficulty</div>
            </div>
          </div>
        </section>

        {/* Questions Section - Full Width */}
        <section style={{ width: '100%', maxWidth: '100%', padding: '0' }}>
          {activeTab === 'coding' && (
            <div className="coding-tab fade-in" style={{ width: '100%', maxWidth: '100%' }}>
              <div style={{ width: '100%', maxWidth: '100%', display: 'block' }}>
                <h3 className="card-title" style={{ marginBottom: '1.5rem', fontSize: '1.5rem' }}>Coding Practice Problems</h3>
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))', 
                  gap: '2rem', 
                  width: '100%',
                  maxWidth: '100%'
                }}>
                  {topic.coding_questions && topic.coding_questions.length > 0 ? (
                    topic.coding_questions.map((problem, index) => (
                      <div key={problem.id} className="streaks-card glass-card" style={{ width: '100%', maxWidth: '100%' }}>
                        <div className="motivational-quote">
                          <div className="quote-icon">{index + 1}</div>
                          <div className="quote-text" style={{ fontSize: '1.1rem', fontWeight: '600' }}>
                            {problem.title.split('\n')[0]}
                          </div>
                        </div>
                        <div style={{ color: 'var(--text-muted)', marginTop: '1rem', fontSize: '0.95rem', lineHeight: '1.5' }}>
                          {problem.question}
                        </div>
                        <div className="actions-grid" style={{ marginTop: '1.5rem' }}>
                          <button 
                            className="action-btn practice"
                            onClick={() => navigate('/questions', { state: { questions: [...topic.coding_questions.map(q => ({...q, type: 'coding'})), ...topic.mcq_questions.map(q => ({...q, type: 'mcq'}))] } })}
                          >
                            <span className="action-icon">🚀</span>
                            <span className="action-text">Start Coding</span>
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="streaks-card glass-card">
                      <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                        No coding problems available.
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'mcq' && (
            <div className="mcq-tab fade-in" style={{ width: '100%', maxWidth: '100%' }}>
              <div style={{ width: '100%', maxWidth: '100%', display: 'block' }}>
                <h3 className="card-title" style={{ marginBottom: '1.5rem', fontSize: '1.5rem' }}>Multiple Choice Questions</h3>
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))', 
                  gap: '2rem', 
                  width: '100%',
                  maxWidth: '100%'
                }}>
                  {topic.mcq_questions && topic.mcq_questions.length > 0 ? (
                    topic.mcq_questions.map((question, index) => (
                      <div key={question.id} className="streaks-card glass-card" style={{ width: '100%', maxWidth: '100%' }}>
                        <div className="motivational-quote">
                          <div className="quote-icon">Q{index + 1}</div>
                          <div className="quote-text" style={{ fontSize: '1rem' }}>
                            {question.question?.substring(0, 100)}...
                          </div>
                        </div>
                        <div className="streaks-grid" style={{ marginTop: '1rem' }}>
                          <div className="streak-item" style={{ background: 'rgba(255, 255, 255, 0.05)', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
                            <div className="streak-icon">📝</div>
                            <div className="streak-info">
                              <div className="streak-number">{question.options?.length || 4}</div>
                              <div className="streak-label">Options</div>
                            </div>
                          </div>
                        </div>
                        <div className="actions-grid" style={{ marginTop: '1.5rem' }}>
                          <button 
                            className="action-btn review"
                            onClick={() => navigate('/questions', { state: { questions: [...topic.coding_questions.map(q => ({...q, type: 'coding'})), ...topic.mcq_questions.map(q => ({...q, type: 'mcq'}))] } })}
                          >
                            <span className="action-icon">🧠</span>
                            <span className="action-text">Take Quiz</span>
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="streaks-card glass-card">
                      <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                        No MCQ questions available.
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}