import React, { useEffect, useMemo, useState, useCallback, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";

export default function QuestionsPage(props) {
  const location = useLocation();
  const navigate = useNavigate();

  const allQuestions = useMemo(() => {
    if (props && Array.isArray(props.questions) && props.questions.length) return props.questions;
    if (location && location.state && Array.isArray(location.state.questions)) return location.state.questions;
    return [];
  }, [props, location]);

  const codingQuestions = useMemo(() => allQuestions.filter(q => q.type === "coding"), [allQuestions]);
  const mcqQuestions = useMemo(() => allQuestions.filter(q => q.type === "mcq"), [allQuestions]);

  const [activeTab, setActiveTab] = useState('coding');

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
              💻 Coding
            </button>
            <button 
              className={`nav-link ${activeTab === 'mcq' ? 'active' : ''}`}
              onClick={() => setActiveTab('mcq')}
            >
              🧠 MCQ
            </button>
          </div>

          {/* Right: Back Button */}
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
            <h1 className="dashboard-welcome-text">Practice Questions 🚀</h1>
            <p>One question at a time. Use the arrows or ← / → keys to navigate.</p>
          </div>
        </section>

        {/* Questions Section */}
        {activeTab === 'coding' && <CodingCarousel questions={codingQuestions} />}
        {activeTab === 'mcq' && <McqCarousel questions={mcqQuestions} />}
      </main>
    </div>
  );
}

/* ----------------------- CodingCarousel ----------------------- */
function CodingCarousel({ questions = [] }) {
  const [index, setIndex] = useState(0);
  const [code, setCode] = useState("");
  const [output, setOutput] = useState("");
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  const iframeRef = useRef(null);

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => setIndex(0), [questions]);

  useEffect(() => {
    const q = questions[index];
    setCode((q && q.starterCode) ? q.starterCode : "// Write JavaScript here\nconsole.log('Hello world');");
    setOutput("");
  }, [index, questions]);

  const prev = () => setIndex(i => Math.max(0, i - 1));
  const next = () => setIndex(i => Math.min(questions.length - 1, i + 1));

  const runCode = useCallback(() => {
    setOutput("Running...");
    const srcDoc = `
      <html><body><script>
      (function(){
        const logs = [];
        const oldLog = console.log;
        console.log = function(...args){
          logs.push(args.map(a => {
            try { return JSON.stringify(a); } catch(e) { return String(a); }
          }).join(' '));
          oldLog.apply(console, args);
        };
        window.onerror = function(message, src, lineno, colno, error) {
          parent.postMessage({ type: 'error', message: String(message) + ' (line:' + lineno + ', col:'+colno+')' }, '*');
        }
        try {
          ${code}
          parent.postMessage({ type: 'result', logs }, '*');
        } catch (err) {
          parent.postMessage({ type: 'error', message: String(err) }, '*');
        }
      })();
      <\/script></body></html>
    `;
    if (iframeRef.current) iframeRef.current.srcdoc = srcDoc;
  }, [code]);

  useEffect(() => {
    const onMessage = (e) => {
      const d = e.data;
      if (!d || typeof d !== "object") return;
      if (d.type === "result") {
        const text = (d.logs && d.logs.length) ? d.logs.join("\n") : "(no output)";
        setOutput(text);
      } else if (d.type === "error") {
        setOutput("Error: " + (d.message || "(unknown)"));
      }
    };
    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  }, []);

  if (!questions.length) {
    return (
      <div className="streaks-card glass-card">
        <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
          No coding questions available.
        </div>
      </div>
    );
  }

  const q = questions[index];

  return (
    <div style={{
      position: 'fixed',
      top: '80px',
      left: 0,
      right: 0,
      bottom: 0,
      width: '100vw',
      height: 'calc(100vh - 80px)',
      background: 'linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 50%, var(--bg-tertiary) 100%)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '2rem',
      overflow: 'hidden'
    }}>
      {/* Main Coding Card */}
      <div className="streaks-card glass-card" style={{
        width: '95%',
        maxWidth: '1400px',
        height: '85%',
        padding: '2rem',
        borderRadius: '1.5rem',
        boxShadow: '0 25px 50px rgba(0, 0, 0, 0.5)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        display: 'flex',
        flexDirection: isMobile ? 'column' : 'row',
        gap: '2rem'
      }}>
        {/* Question Section - Left */}
        <div style={{
          width: isMobile ? '100%' : '40%',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
            <h3 className="card-title" style={{ fontSize: '1.5rem', fontWeight: '700' }}>{q.title ?? `Question ${index + 1}`}</h3>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <button 
                onClick={prev} 
                disabled={index === 0}
                className="action-btn pomodoro"
                style={{ 
                  opacity: index === 0 ? 0.5 : 1,
                  cursor: index === 0 ? 'not-allowed' : 'pointer',
                  padding: '0.75rem 1.5rem',
                  fontSize: '1rem'
                }}
              >
                <span className="action-icon">←</span>
              </button>
              <button 
                onClick={next} 
                disabled={index === questions.length - 1}
                className="action-btn pomodoro"
                style={{ 
                  opacity: index === questions.length - 1 ? 0.5 : 1,
                  cursor: index === questions.length - 1 ? 'not-allowed' : 'pointer',
                  padding: '0.75rem 1.5rem',
                  fontSize: '1rem'
                }}
              >
                <span className="action-icon">→</span>
              </button>
            </div>
          </div>
          
          <div className="motivational-quote" style={{ marginBottom: '1.5rem' }}>
            <div className="quote-icon" style={{ fontSize: '1.5rem' }}>📝</div>
            <div className="quote-text" style={{ lineHeight: '1.8', fontSize: '1.2rem', fontWeight: '400' }}>{q.question}</div>
          </div>

          {q.examples && (
            <div style={{
              background: 'rgba(0, 0, 0, 0.4)',
              border: '2px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '16px',
              padding: '1.5rem',
              marginBottom: '1.5rem'
            }}>
              <h4 style={{ color: 'var(--text-muted)', fontSize: '1rem', marginBottom: '0.75rem', fontWeight: '600' }}>Examples:</h4>
              <pre style={{ color: '#4ade80', fontSize: '0.95rem', whiteSpace: 'pre-wrap', lineHeight: '1.4' }}>{q.examples}</pre>
            </div>
          )}

          <div style={{ 
            color: 'var(--text-muted)', 
            fontSize: '1rem',
            marginTop: 'auto',
            textAlign: 'center',
            fontWeight: '500'
          }}>
            Question {index + 1} of {questions.length}
          </div>
        </div>

        </div>

        {/* Editor Section - Right */}
        <div style={{
          width: isMobile ? '100%' : '60%',
          display: 'flex',
          flexDirection: 'column',
          height: '100%'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
            <h4 style={{ color: 'var(--text-secondary)', fontSize: '1.25rem', margin: 0, fontWeight: '600' }}>Code Editor</h4>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <button className="action-btn practice" onClick={runCode} style={{
                padding: '0.75rem 1.5rem',
                fontSize: '1rem',
                fontWeight: '600'
              }}>
                <span className="action-icon">▶️</span>
                <span className="action-text">Run Code</span>
              </button>
              <button 
                className="action-btn review" 
                onClick={() => { setCode(q.starterCode || ""); setOutput(""); }}
                style={{
                  padding: '0.75rem 1.5rem',
                  fontSize: '1rem',
                  fontWeight: '600'
                }}
              >
                <span className="action-icon">🔄</span>
                <span className="action-text">Reset</span>
              </button>
            </div>
          </div>

          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            style={{
              width: '100%',
              height: '65%',
              background: 'rgba(0, 0, 0, 0.6)',
              border: '2px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '16px',
              padding: '1.5rem',
              color: '#fff',
              fontFamily: 'Monaco, Consolas, "Courier New", monospace',
              fontSize: '1rem',
              lineHeight: '1.5',
              resize: 'none',
              marginBottom: '1.5rem',
              boxShadow: 'inset 0 4px 8px rgba(0, 0, 0, 0.3)'
            }}
            spellCheck={false}
            placeholder="// Write JavaScript here\nconsole.log('Hello world');"
          />

          <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <h4 style={{ color: 'var(--text-muted)', fontSize: '1rem', marginBottom: '0.75rem', fontWeight: '600' }}>Console Output</h4>
            <div style={{
              flex: 1,
              background: 'rgba(0, 0, 0, 0.6)',
              border: '2px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '16px',
              padding: '1.5rem',
              fontFamily: 'Monaco, Consolas, "Courier New", monospace',
              color: output.includes('Error') ? '#f87171' : '#4ade80',
              whiteSpace: 'pre-wrap',
              fontSize: '0.95rem',
              lineHeight: '1.4',
              overflow: 'auto',
              boxShadow: 'inset 0 4px 8px rgba(0, 0, 0, 0.3)'
            }}>
              {output || "(no output)"}
            </div>
          </div>

          <iframe ref={iframeRef} title="sandbox" sandbox="allow-scripts" style={{ display: "none" }} />
        </div>
      </div>
  );
}

/* ----------------------- MCQ Carousel ----------------------- */
function McqCarousel({ questions = [] }) {
  const [index, setIndex] = useState(0);
  const [selected, setSelected] = useState(null);
  const [locked, setLocked] = useState(false);

  useEffect(() => setIndex(0), [questions]);
  useEffect(() => { setSelected(null); setLocked(false); }, [index]);

  const prev = () => setIndex(i => Math.max(0, i - 1));
  const next = () => setIndex(i => Math.min(questions.length - 1, i + 1));

  if (!questions.length) {
    return (
      <div className="streaks-card glass-card">
        <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
          No MCQ questions available.
        </div>
      </div>
    );
  }

  const q = questions[index];
  const correctIndex = (typeof q.answer !== "undefined") ? q.answer : null;

  const onSelect = (i) => {
    if (locked) return;
    setSelected(i);
    setLocked(true);
  };

  return (
    <div style={{
      position: 'fixed',
      top: '80px',
      left: 0,
      right: 0,
      bottom: 0,
      width: '100vw',
      height: 'calc(100vh - 80px)',
      background: 'linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 50%, var(--bg-tertiary) 100%)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '2rem',
      overflow: 'hidden'
    }}>
      {/* Main Card */}
      <div className="streaks-card glass-card" style={{
        width: '90%',
        maxWidth: '1200px',
        height: '80%',
        padding: '2rem',
        borderRadius: '1.5rem',
        boxShadow: '0 25px 50px rgba(0, 0, 0, 0.5)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        display: 'flex',
        flexDirection: 'column'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
          <h3 className="card-title" style={{ fontSize: '1.5rem', fontWeight: '700' }}>{q.title ?? `Question ${index + 1}`}</h3>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <button 
              onClick={prev} 
              disabled={index === 0}
              className="action-btn pomodoro"
              style={{ 
                opacity: index === 0 ? 0.5 : 1,
                cursor: index === 0 ? 'not-allowed' : 'pointer',
                padding: '0.75rem 1.5rem',
                fontSize: '1rem'
              }}
            >
              <span className="action-icon">←</span>
            </button>
            <button 
              onClick={next} 
              disabled={index === questions.length - 1}
              className="action-btn pomodoro"
              style={{ 
                opacity: index === questions.length - 1 ? 0.5 : 1,
                cursor: index === questions.length - 1 ? 'not-allowed' : 'pointer',
                padding: '0.75rem 1.5rem',
                fontSize: '1rem'
              }}
            >
              <span className="action-icon">→</span>
            </button>
          </div>
        </div>
        
        <div className="motivational-quote" style={{ marginBottom: '2rem' }}>
          <div className="quote-icon" style={{ fontSize: '1.5rem' }}>❓</div>
          <div className="quote-text" style={{ lineHeight: '1.8', fontSize: '1.2rem', fontWeight: '400' }}>{q.question}</div>
        </div>

        <div style={{ 
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
          gap: '1.5rem',
          flex: 1,
          marginBottom: '2rem'
        }}>
          {(q.options || []).map((opt, i) => {
            const isSelected = selected === i;
            const isCorrect = correctIndex === i;
            const showCorrect = locked && isCorrect;
            const showWrong = locked && isSelected && !isCorrect;

            return (
              <button
                key={i}
                onClick={() => onSelect(i)}
                disabled={locked}
                className="streak-item"
                style={{
                  cursor: locked ? 'default' : 'pointer',
                  background: showCorrect ? 'rgba(16, 185, 129, 0.2)' : 
                             showWrong ? 'rgba(239, 68, 68, 0.2)' : 
                             'rgba(255, 255, 255, 0.05)',
                  border: showCorrect ? '2px solid rgba(16, 185, 129, 0.5)' : 
                          showWrong ? '2px solid rgba(239, 68, 68, 0.5)' : 
                          '2px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '16px',
                  padding: '1.5rem',
                  transition: 'all 0.2s ease',
                  minHeight: '80px',
                  display: 'flex',
                  alignItems: 'center'
                }}
              >
                <div className="streak-icon" style={{
                  background: showCorrect ? '#10b981' : showWrong ? '#ef4444' : 'rgba(255, 255, 255, 0.1)',
                  color: showCorrect || showWrong ? '#fff' : 'inherit',
                  width: '50px',
                  height: '50px',
                  fontSize: '1.2rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  {String.fromCharCode(65 + i)}
                </div>
                <div className="streak-info" style={{ flex: 1 }}>
                  <div className="streak-label" style={{ textAlign: 'left', fontSize: '1.1rem', lineHeight: '1.5' }}>{opt}</div>
                  {showCorrect && <div style={{ color: '#10b981', fontSize: '1rem', fontWeight: '600', marginTop: '0.5rem' }}>✓ Correct</div>}
                  {showWrong && <div style={{ color: '#ef4444', fontSize: '1rem', fontWeight: '600', marginTop: '0.5rem' }}>✗ Wrong</div>}
                </div>
              </button>
            );
          })}
        </div>

        {locked && q.explanation && (
          <div className="motivational-quote" style={{ marginTop: '2rem', marginBottom: '2rem' }}>
            <div className="quote-icon" style={{ fontSize: '1.5rem' }}>💡</div>
            <div className="quote-text" style={{ fontSize: '1.1rem', lineHeight: '1.6' }}>
              <strong style={{ fontSize: '1.2rem' }}>Explanation:</strong><br/><br/>{q.explanation}
            </div>
          </div>
        )}

        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginTop: 'auto',
          paddingTop: '1rem',
          borderTop: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          <div style={{ 
            color: 'var(--text-muted)', 
            fontSize: '1rem',
            fontWeight: '500'
          }}>
            Question {index + 1} of {questions.length}
          </div>
          <button 
            className="action-btn review" 
            onClick={() => { setSelected(null); setLocked(false); }}
            style={{
              padding: '0.75rem 1.5rem',
              fontSize: '1rem',
              fontWeight: '600'
            }}
          >
            <span className="action-icon">🔄</span>
            <span className="action-text">Try Again</span>
          </button>
        </div>
      </div>
    </div>
  );
}