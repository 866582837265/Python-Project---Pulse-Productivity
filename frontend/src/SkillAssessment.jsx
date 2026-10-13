import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "./api";
import "./SkillAssessment.css";

export default function SkillAssessment({ onComplete }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState({ preferred_language: "Java" });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const assessmentSteps = [
    {
      id: "background",
      title: "Tell us about your background",
      questions: [
        {
          key: "coding_experience_years",
          question: "How many years of coding experience do you have?",
          type: "select",
          options: [
            { value: 0.2, label: "Less than 6 months" },
            { value: 0.5, label: "6 months - 1 year" },
            { value: 1.5, label: "1-2 years" },
            { value: 3, label: "2-4 years" },
            { value: 5, label: "4-6 years" },
            { value: 7, label: "6+ years" }
          ]
        },
        {
          key: "education_level",
          question: "What's your highest education level?",
          type: "select",
          options: [
            { value: "High School", label: "High School" },
            { value: "Bachelor", label: "Bachelor's Degree" },
            { value: "Master", label: "Master's Degree" },
            { value: "PhD", label: "PhD" }
          ]
        },
        {
          key: "background",
          question: "What's your educational background?",
          type: "select",
          options: [
            { value: "CS", label: "Computer Science" },
            { value: "Non-CS", label: "Non-Computer Science" }
          ]
        },

      ]
    },
    {
      id: "coding_quiz",
      title: "Quick Coding Assessment",
      questions: [
        {
          key: "quiz_q1",
          question: "What is the time complexity of binary search?",
          type: "radio",
          options: [
            { value: 0, label: "O(n)" },
            { value: 1, label: "O(log n)" },
            { value: 2, label: "O(n²)" },
            { value: 3, label: "O(1)" }
          ]
        },
        {
          key: "quiz_q2",
          question: "Which data structure uses LIFO (Last In, First Out)?",
          type: "radio",
          options: [
            { value: 0, label: "Queue" },
            { value: 1, label: "Stack" },
            { value: 2, label: "Array" },
            { value: 3, label: "Linked List" }
          ]
        },
        {
          key: "quiz_q3",
          question: "What's the best approach to find duplicates in an array?",
          type: "radio",
          options: [
            { value: 0, label: "Nested loops" },
            { value: 1, label: "Hash Set" },
            { value: 2, label: "Sorting first" },
            { value: 3, label: "Linear search" }
          ]
        },
        {
          key: "quiz_q4",
          question: "Which algorithm is used for shortest path in graphs?",
          type: "radio",
          options: [
            { value: 0, label: "Dijkstra's Algorithm" },
            { value: 1, label: "Bubble Sort" },
            { value: 2, label: "Linear Search" },
            { value: 3, label: "Quick Sort" }
          ]
        },
        {
          key: "quiz_q5",
          question: "What is dynamic programming primarily used for?",
          type: "radio",
          options: [
            { value: 0, label: "Sorting data" },
            { value: 1, label: "Optimization problems" },
            { value: 2, label: "Searching data" },
            { value: 3, label: "Memory management" }
          ]
        }
      ]
    },
    {
      id: "habits",
      title: "Your Learning Habits",
      questions: [
        {
          key: "problems_solved_daily",
          question: "How many coding problems do you solve per day on average?",
          type: "select",
          options: [
            { value: 1, label: "1-2 problems" },
            { value: 3, label: "3-5 problems" },
            { value: 7, label: "6-10 problems" },
            { value: 12, label: "10+ problems" }
          ]
        },
        {
          key: "time_per_problem_minutes",
          question: "How much time do you typically spend on a coding problem?",
          type: "select",
          options: [
            { value: 5, label: "Less than 5 minutes" },
            { value: 10, label: "5-15 minutes" },
            { value: 20, label: "15-30 minutes" },
            { value: 45, label: "30+ minutes" }
          ]
        }
      ]
    }
  ];

  const handleAnswerChange = (key, value) => {
    console.log(`[ASSESSMENT] Answer changed: ${key} = ${value}`);
    setAnswers(prev => {
      const updated = {
        ...prev,
        [key]: value
      };
      console.log(`[ASSESSMENT] Updated answers:`, updated);
      return updated;
    });
  };

  const handleNext = () => {
    if (currentStep < assessmentSteps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleSubmit();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const calculateQuizScore = () => {
    const quizAnswers = Object.keys(answers)
      .filter(key => key.startsWith('quiz_q'))
      .map(key => answers[key]);
    
    const totalScore = quizAnswers.reduce((sum, score) => sum + score, 0);
    const maxScore = 20; // 5 questions × 4 points max
    return Math.round((totalScore / maxScore) * 100);
  };

  const handleSubmit = async () => {
    setLoading(true);
    
    try {
      // Get JWT token
      const token = localStorage.getItem('token');
      if (!token) {
        console.log('[ASSESSMENT] No token found, redirecting to login');
        alert('Please login first');
        navigate('/login');
        return;
      }

      console.log('[ASSESSMENT] Starting assessment submission...');

      // Map quiz answers to correct format - now using 0-based indexing
      const quizAnswers = [
        { question_id: 1, selected_answer: answers.quiz_q1 !== undefined ? answers.quiz_q1 : 0, time_taken: 30 },
        { question_id: 2, selected_answer: answers.quiz_q2 !== undefined ? answers.quiz_q2 : 0, time_taken: 25 },
        { question_id: 3, selected_answer: answers.quiz_q3 !== undefined ? answers.quiz_q3 : 0, time_taken: 35 },
        { question_id: 4, selected_answer: answers.quiz_q4 !== undefined ? answers.quiz_q4 : 0, time_taken: 40 },
        { question_id: 5, selected_answer: answers.quiz_q5 !== undefined ? answers.quiz_q5 : 0, time_taken: 30 }
      ];

      const assessmentData = {
        domain: "programming",
        answers: quizAnswers
      };

      console.log('[ASSESSMENT] Submitting assessment data:', assessmentData);

      // Send to quiz submission API using enhanced API client
      const result = await api.submitQuiz(assessmentData);
      console.log('[ASSESSMENT] Assessment result:', result);

      if (result.success) {
        console.log(`[ASSESSMENT] Assessment completed for user ${result.user_email} - Level: ${result.predicted_level}`);
        
        // Verify this result is for the current user
        const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
        if (result.user_email && currentUser.email && result.user_email !== currentUser.email) {
          console.error('[ASSESSMENT] User mismatch detected! Result for different user.');
          alert('Session error detected. Please login again.');
          localStorage.clear();
          navigate('/');
          return;
        }
        
        // Clear any old assessment data first
        localStorage.removeItem('skillAssessment');
        
        // Store NEW results for current user with verification
        localStorage.setItem('skillAssessment', JSON.stringify({
          ...result,
          completedAt: new Date().toISOString(),
          userEmail: result.user_email  // Store for verification
        }));

        // Show success message
        alert(`🎉 Assessment Complete!\n\nYour skill level: ${result.predicted_level?.toUpperCase() || 'UNKNOWN'}\nScore: ${result.score}/${result.total_questions} (${result.percentage}%)\n\nYour personalized roadmap has been generated!`);

        // Call completion callback
        if (onComplete) {
          onComplete(result);
        } else {
          navigate('/dashboard');
        }
      } else {
        console.error('[ASSESSMENT] Assessment failed:', result.error);
        if (result.error && result.error.includes('Assessment already taken')) {
          alert('You have already completed the assessment. Redirecting to your dashboard.');
          navigate('/dashboard');
        } else {
          alert(result.error || 'Assessment failed. Please try again.');
        }
      }
    } catch (error) {
      console.error('[ASSESSMENT] Assessment error:', error);
      
      // Enhanced error handling
      if (error.message.includes('Authentication failed')) {
        alert('Your session has expired. Please login again.');
        navigate('/login');
      } else if (error.message.includes('Network error')) {
        alert('Network error. Please check your connection and try again.');
      } else {
        alert(error.message || 'Assessment failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const currentStepData = assessmentSteps[currentStep];
  const isLastStep = currentStep === assessmentSteps.length - 1;
  const canProceed = currentStepData.questions.every(q => answers[q.key] !== undefined || q.key === 'preferred_language');

  return (
    <div className="skill-assessment-container">
      <div className="assessment-card">
        {/* Progress Bar */}
        <div className="progress-section">
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ width: `${((currentStep + 1) / assessmentSteps.length) * 100}%` }}
            />
          </div>
          <div className="progress-text">
            Step {currentStep + 1} of {assessmentSteps.length}
          </div>
        </div>

        {/* Step Content */}
        <div className="step-content">
          <h2 className="step-title">{currentStepData.title}</h2>
          
          <div className="questions-container">
            {currentStepData.questions.map((question, index) => (
              <div key={question.key} className="question-group">
                <label className="question-label">
                  {question.question}
                </label>
                
                {question.type === "select" && (
                  <select
                    value={answers[question.key] || ""}
                    onChange={(e) => handleAnswerChange(question.key, 
                      question.key.includes('_years') || question.key.includes('_daily') || question.key.includes('_minutes') 
                        ? parseFloat(e.target.value) 
                        : e.target.value
                    )}
                    className="question-select"
                  >
                    <option value="">Select an option...</option>
                    {question.options.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                )}

                {question.type === "radio" && (
                  <div className="radio-group">
                    {question.options.map((option) => (
                      <label key={option.value} className="radio-option">
                        <input
                          type="radio"
                          name={question.key}
                          value={option.value}
                          checked={answers[question.key] === option.value}
                          onChange={(e) => handleAnswerChange(question.key, parseInt(e.target.value))}
                        />
                        <span className="radio-label">{option.label}</span>
                      </label>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Navigation */}
        <div className="navigation-section">
          <button
            onClick={handlePrevious}
            disabled={currentStep === 0}
            className="nav-button secondary"
          >
            Previous
          </button>
          
          <button
            onClick={handleNext}
            disabled={!canProceed || loading}
            className="nav-button primary"
          >
            {loading ? (
              <span className="loading-content">
                <div className="spinner"></div>
                {isLastStep ? 'Analyzing...' : 'Processing...'}
              </span>
            ) : (
              isLastStep ? 'Complete Assessment' : 'Next'
            )}
          </button>
        </div>
      </div>
    </div>
  );
}