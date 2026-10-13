import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams, useLocation } from 'react-router-dom';

export default function EnhancedPractice() {
  const { topicId } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const practiceType = searchParams.get('type') || 'coding';
  
  const [topic, setTopic] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(practiceType);
  
  // Coding state
  const [selectedProblem, setSelectedProblem] = useState(0);
  const [code, setCode] = useState('');
  const [codeOutput, setCodeOutput] = useState('');
  const [runningCode, setRunningCode] = useState(false);
  
  // MCQ state
  const [mcqAnswers, setMcqAnswers] = useState({});
  const [mcqResults, setMcqResults] = useState(null);
  const [showMcqResults, setShowMcqResults] = useState(false);

  useEffect(() => {
    fetchTopicContent();
  }, [topicId]);

  useEffect(() => {
    if (topic?.coding_questions?.[selectedProblem]?.starter_code) {
      setCode(topic.coding_questions[selectedProblem].starter_code);
    } else {
      setCode(`public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, Java!");
        // Your solution here
    }
}`);
    }
  }, [selectedProblem, topic]);

  const { state } = useLocation();
  
  const fetchTopicContent = async () => {
    try {
      const passedQuestions = state?.questions || [];
      
      if (passedQuestions.length > 0) {
        const topicData = {
          title: 'Array Basics',
          coding_questions: passedQuestions.filter(q => q.type === 'coding').map(q => ({
            id: q.id,
            title: q.question,
            description: `Example: ${q.example_input} → ${q.example_output}`,
            sample_input: q.example_input,
            sample_output: q.example_output,
            difficulty: 'Beginner',
            starter_code: `public class Solution {
    public void solve() {
        // ${q.question}
        // Example: ${q.example_input} → ${q.example_output}
        System.out.println("Your solution here");
    }
}`
          })),
          mcq_questions: passedQuestions.filter(q => q.type === 'mcq')
        };
        
        setTopic(topicData);
      } else {
        setError('No questions available');
      }
    } catch (err) {
      setError('Failed to load questions');
    } finally {
      setLoading(false);
    }
  };

  const runCode = async () => {
    if (!code.trim()) return;
    
    setRunningCode(true);
    setCodeOutput('Running code...');
    
    // Simulate code execution
    setTimeout(() => {
      setCodeOutput('Code executed successfully!\nOutput: Hello, Java!');
      setRunningCode(false);
    }, 1500);
  };

  const submitMcq = async () => {
    const correct = Object.keys(mcqAnswers).length;
    const total = topic.mcq_questions?.length || 0;
    const percentage = Math.round((correct / total) * 100);
    
    setMcqResults({
      score: correct,
      total: total,
      percentage: percentage
    });
    setShowMcqResults(true);
  };

  const handleMcqAnswer = (questionId, optionIndex) => {
    setMcqAnswers(prev => ({
      ...prev,
      [questionId]: optionIndex
    }));
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <nav className="dashboard-nav">
          <div className="nav-content">
            <div className="nav-brand">
              <h1 className="brand-wordmark">Pulse</h1>
            </div>
            <button className="nav-back-btn" onClick={() => navigate(`/roadmap/topic/${topicId}`)}>
              <span className="back-icon">←</span>
              <span>Back to Topic</span>
            </button>
          </div>
        </nav>
        
        <main className="dashboard-main">
          <div className="loading-state">
            <h2>Loading practice content...</h2>
            <p>Preparing your questions ✨</p>
          </div>
        </main>
      </div>
    );
  }

  if (error || !topic) {
    return (
      <div className="dashboard-container">
        <nav className="dashboard-nav">
          <div className="nav-content">
            <div className="nav-brand">
              <h1 className="brand-wordmark">Pulse</h1>
            </div>
            <button className="nav-back-btn" onClick={() => navigate(`/roadmap/topic/${topicId}`)}>
              <span className="back-icon">←</span>
              <span>Back to Topic</span>
            </button>
          </div>
        </nav>
        
        <main className="dashboard-main">
          <div className="error-state">
            <div className="error-icon">⚠️</div>
            <h2>Unable to load practice content</h2>
            <p>{error}</p>
            <button className="btn-primary" onClick={() => navigate('/roadmap')}>
              Back to Roadmap
            </button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* Navigation Bar */}
      <nav className="dashboard-nav">
        <div className="nav-content">
          {/* Left: Brand */}
          <div className="nav-brand">
            <h1 className="brand-wordmark">Pulse</h1>
          </div>

          {/* Center: Navigation Links */}
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

          {/* Right: Back Button */}
          <div className="nav-profile">
            <button className="nav-back-btn" onClick={() => navigate(`/roadmap/topic/${topicId}`)}>
              ← Back to Topic
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="dashboard-main">
        {/* Welcome Section */}
        <section className="welcome-section">
          <div className="welcome-header">
            <h1 className="dashboard-welcome-text">{topic.title} Practice 💻</h1>
            <p>Master {topic.title} with hands-on coding and quiz questions</p>
          </div>
        </section>

        {/* Coding Section */}
        {activeTab === 'coding' && (
          <section className="progress-section">
            <div className="progress-content">
              {/* Problem List Card */}
              <div className="platforms-card glass-card">
                <h3 className="card-title">Problems</h3>
                <div className="platforms-grid">
                  {topic.coding_questions?.map((problem, index) => (
                    <button
                      key={problem.id}
                      onClick={() => setSelectedProblem(index)}
                      className={`platform-link ${selectedProblem === index ? 'active' : ''}`}
                      style={{ 
                        '--platform-color': selectedProblem === index ? '#38bdf8' : '#6b7280',
                        background: selectedProblem === index ? 'rgba(56, 189, 248, 0.1)' : 'transparent'
                      }}
                    >
                      <span className="platform-icon">{index + 1}</span>
                      <span className="platform-name">{problem.title}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Problem Details Card */}
              {topic.coding_questions?.[selectedProblem] && (
                <div className="streaks-card glass-card">
                  <h3 className="card-title">Problem Details</h3>
                  <div className="motivational-quote">
                    <div className="quote-icon">📝</div>
                    <div className="quote-text">{topic.coding_questions[selectedProblem].title}</div>
                  </div>
                  <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>
                    {topic.coding_questions[selectedProblem].description}
                  </p>
                  
                  <div className="streaks-grid">
                    <div className="streak-item">
                      <div className="streak-icon">📥</div>
                      <div className="streak-info">
                        <div className="streak-label">Sample Input</div>
                        <div className="streak-number" style={{ fontSize: '0.9rem', fontFamily: 'monospace' }}>
                          {topic.coding_questions[selectedProblem].sample_input}
                        </div>
                      </div>
                    </div>
                    
                    <div className="streak-item">
                      <div className="streak-icon">📤</div>
                      <div className="streak-info">
                        <div className="streak-label">Expected Output</div>
                        <div className="streak-number" style={{ fontSize: '0.9rem', fontFamily: 'monospace' }}>
                          {topic.coding_questions[selectedProblem].sample_output}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Code Editor Card */}
              <div className="quick-actions-card glass-card">
                <h3 className="card-title">Code Editor</h3>
                <textarea
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  style={{
                    width: '100%',
                    minHeight: '300px',
                    background: 'rgba(0, 0, 0, 0.4)',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: '12px',
                    padding: '1rem',
                    color: '#fff',
                    fontFamily: 'Monaco, Consolas, monospace',
                    fontSize: '0.9rem',
                    resize: 'vertical',
                    marginBottom: '1rem'
                  }}
                  placeholder="Write your Java solution here..."
                />
                
                <div className="actions-grid">
                  <button 
                    className="action-btn pomodoro" 
                    onClick={runCode}
                    disabled={runningCode}
                  >
                    <span className="action-icon">{runningCode ? '⏳' : '▶️'}</span>
                    <span className="action-text">{runningCode ? 'Running...' : 'Run Code'}</span>
                  </button>
                </div>
                
                {codeOutput && (
                  <div style={{
                    marginTop: '1rem',
                    background: 'rgba(0, 0, 0, 0.4)',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: '12px',
                    padding: '1rem'
                  }}>
                    <h4 style={{ fontSize: '0.9rem', fontWeight: '600', marginBottom: '0.5rem', color: '#fff' }}>
                      Output:
                    </h4>
                    <pre style={{
                      color: codeOutput.includes('Error') ? '#f87171' : '#4ade80',
                      fontSize: '0.85rem',
                      whiteSpace: 'pre-wrap',
                      margin: 0
                    }}>
                      {codeOutput}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          </section>
        )}

        {/* MCQ Section */}
        {activeTab === 'mcq' && (
          <section className="progress-section">
            <div className="progress-content">
              {!showMcqResults ? (
                <>
                  {topic.mcq_questions?.map((question, index) => (
                    <div key={question.id} className="streaks-card glass-card">
                      <h3 className="card-title">
                        Question {index + 1}
                      </h3>
                      <div className="motivational-quote">
                        <div className="quote-icon">❓</div>
                        <div className="quote-text">{question.question}</div>
                      </div>
                      
                      <div className="streaks-grid">
                        {question.options?.map((option, optionIndex) => (
                          <button
                            key={optionIndex}
                            onClick={() => handleMcqAnswer(question.id, optionIndex)}
                            className="streak-item"
                            style={{
                              cursor: 'pointer',
                              background: mcqAnswers[question.id] === optionIndex ? 'rgba(56, 189, 248, 0.2)' : 'transparent',
                              border: mcqAnswers[question.id] === optionIndex ? '1px solid rgba(56, 189, 248, 0.5)' : '1px solid transparent',
                              borderRadius: '8px',
                              padding: '0.75rem'
                            }}
                          >
                            <div className="streak-icon">{String.fromCharCode(65 + optionIndex)}</div>
                            <div className="streak-info">
                              <div className="streak-label">{option}</div>
                            </div>
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
                  
                  <div className="quick-actions-card glass-card">
                    <div className="actions-grid">
                      <button
                        onClick={submitMcq}
                        disabled={Object.keys(mcqAnswers).length !== topic.mcq_questions?.length}
                        className="action-btn practice"
                        style={{
                          opacity: Object.keys(mcqAnswers).length === topic.mcq_questions?.length ? 1 : 0.5
                        }}
                      >
                        <span className="action-icon">✨</span>
                        <span className="action-text">Submit Quiz</span>
                      </button>
                    </div>
                  </div>
                </>
              ) : (
                <div className="streaks-card glass-card" style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>
                    {mcqResults.percentage >= 70 ? '🎉' : '📚'}
                  </div>
                  <h2 className="card-title" style={{ fontSize: '2rem', marginBottom: '1rem' }}>
                    Quiz Complete!
                  </h2>
                  <div className="streaks-grid">
                    <div className="streak-item">
                      <div className="streak-icon">📊</div>
                      <div className="streak-info">
                        <div className="streak-number">{mcqResults.score}/{mcqResults.total}</div>
                        <div className="streak-label">Score</div>
                      </div>
                    </div>
                    <div className="streak-item">
                      <div className="streak-icon">📈</div>
                      <div className="streak-info">
                        <div className="streak-number">{mcqResults.percentage}%</div>
                        <div className="streak-label">Percentage</div>
                      </div>
                    </div>
                  </div>
                  <div className="motivational-quote">
                    <div className="quote-icon">💬</div>
                    <div className="quote-text">
                      {mcqResults.percentage >= 70 ? 
                        'Excellent work! You\'ve mastered this topic! 🌟' : 
                        'Good effort! Review the concepts and try again. 💪'
                      }
                    </div>
                  </div>
                  <div className="actions-grid">
                    <button className="action-btn progress" onClick={() => navigate('/roadmap')}>
                      <span className="action-icon">🏠</span>
                      <span className="action-text">Back to Roadmap</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}