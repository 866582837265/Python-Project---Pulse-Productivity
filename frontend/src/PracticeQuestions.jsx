import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';

export default function PracticeQuestions() {
  const { topicId } = useParams();
  const navigate = useNavigate();
  const [questions, setQuestions] = useState([]);
  const [topic, setTopic] = useState('');
  const [difficulty, setDifficulty] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [answers, setAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);

  useEffect(() => {
    fetchPracticeQuestions();
  }, [topicId]);

  const { state } = useLocation();
  
  const fetchPracticeQuestions = async () => {
    try {
      const passedQuestions = state?.questions || [];
      
      if (passedQuestions.length > 0) {
        setQuestions(passedQuestions.filter(q => q.type === 'mcq'));
        setTopic('Array Basics');
        setDifficulty('Beginner');
      } else {
        setError('No questions available');
      }
    } catch (err) {
      console.error('Load error:', err);
      setError('Failed to load questions');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionId, selectedIndex) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: selectedIndex
    }));
  };

  const submitAnswers = () => {
    setShowResults(true);
  };

  const getScore = () => {
    let correct = 0;
    questions.forEach(q => {
      if (answers[q.id] === q.answer) correct++;
    });
    return { correct, total: questions.length };
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty?.toLowerCase()) {
      case 'beginner': return 'bg-green-500';
      case 'intermediate': return 'bg-orange-500';
      case 'expert': return 'bg-red-500';
      default: return 'bg-blue-500';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p>Loading practice questions...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center bg-white p-8 rounded-lg shadow-sm max-w-md">
          <h2 className="text-xl font-bold text-red-600 mb-4">Unable to load content</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <div className="space-y-2">
            <button 
              onClick={fetchPracticeQuestions}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 mr-2"
            >
              Try Again
            </button>
            <button 
              onClick={() => navigate('/roadmap')}
              className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
            >
              Back to Roadmap
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (showResults) {
    const { correct, total } = getScore();
    const percentage = Math.round((correct / total) * 100);
    
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-sm max-w-md text-center">
          <h2 className="text-2xl font-bold mb-4">Practice Complete!</h2>
          <div className="text-4xl mb-4">{percentage >= 70 ? '🎉' : '📚'}</div>
          <p className="text-xl mb-4">Score: {correct}/{total} ({percentage}%)</p>
          <p className="text-gray-600 mb-6">
            {percentage >= 70 ? 'Great job! Keep practicing!' : 'Keep studying and try again!'}
          </p>
          <button 
            onClick={() => navigate('/roadmap')}
            className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600"
          >
            Back to Roadmap
          </button>
        </div>
      </div>
    );
  }

  // Handle empty questions case
  if (!questions || questions.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center bg-white p-8 rounded-lg shadow-sm max-w-md">
          <h2 className="text-xl font-bold mb-4">No content yet</h2>
          <p className="text-gray-600 mb-4">Generating practice problems for {topic}...</p>
          <div className="animate-pulse bg-gray-200 h-4 rounded mb-4"></div>
          <button 
            onClick={() => navigate('/roadmap')}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Back to Roadmap
          </button>
        </div>
      </div>
    );
  }

  const allAnswered = questions.every(q => answers[q.id] !== undefined);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <button 
            onClick={() => navigate('/roadmap')}
            className="text-blue-500 hover:text-blue-700 mb-4"
          >
            ← Back to Roadmap
          </button>
          <div className="flex items-center gap-4 mb-4">
            <h1 className="text-3xl font-bold">{topic} Practice</h1>
            <span className={`px-3 py-1 rounded-full text-sm font-medium text-white ${getDifficultyColor(difficulty)}`}>
              {difficulty}
            </span>
          </div>
          <p className="text-gray-600">Answer all questions to see your results</p>
        </div>

        {/* Questions */}
        <div className="space-y-6">
          {questions.map((question, index) => (
            <div key={question.id} className="bg-white p-6 rounded-lg shadow-sm border">
              <h3 className="text-lg font-semibold mb-4">
                {index + 1}. {question.question}
              </h3>
              
              <div className="space-y-2">
                {question.options.map((option, optionIndex) => (
                  <label 
                    key={optionIndex} 
                    className={`
                      flex items-center p-3 rounded border cursor-pointer transition-colors
                      ${answers[question.id] === optionIndex ? 'bg-blue-50 border-blue-300' : 'hover:bg-gray-50'}
                      ${showResults && optionIndex === question.answer ? 'bg-green-50 border-green-300' : ''}
                      ${showResults && answers[question.id] === optionIndex && optionIndex !== question.answer ? 'bg-red-50 border-red-300' : ''}
                    `}
                  >
                    <input
                      type="radio"
                      name={`q-${index}`}
                      value={optionIndex}
                      checked={answers[question.id] === optionIndex}
                      onChange={() => handleAnswerChange(question.id, optionIndex)}
                      className="mr-3"
                      disabled={showResults}
                    />
                    <span>{option}</span>
                  </label>
                ))}
              </div>
              
              {showResults && question.explanation && (
                <div className="mt-4 p-3 bg-blue-50 rounded border-l-4 border-blue-400">
                  <p className="text-sm text-blue-800">
                    <strong>Explanation:</strong> {question.explanation}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Submit Button */}
        {!showResults && (
          <div className="mt-8 text-center">
            <button
              onClick={submitAnswers}
              disabled={!allAnswered}
              className={`px-8 py-3 rounded-lg font-semibold ${
                allAnswered
                  ? 'bg-blue-500 text-white hover:bg-blue-600'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
            >
              Submit Answers
            </button>
            
            {!allAnswered && (
              <p className="text-gray-500 mt-2">Please answer all questions to submit</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}