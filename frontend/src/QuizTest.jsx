import React, { useState } from 'react';

export default function QuizTest() {
  const [answers, setAnswers] = useState({});

  const testQuestions = [
    {
      key: "test_q1",
      question: "Test Question 1: What is 2+2?",
      type: "radio",
      options: [
        { value: 0, label: "3" },
        { value: 1, label: "4" },
        { value: 2, label: "5" },
        { value: 3, label: "6" }
      ]
    },
    {
      key: "test_q2", 
      question: "Test Question 2: What color is the sky?",
      type: "radio",
      options: [
        { value: 0, label: "Red" },
        { value: 1, label: "Blue" },
        { value: 2, label: "Green" },
        { value: 3, label: "Yellow" }
      ]
    }
  ];

  const handleAnswerChange = (key, value) => {
    console.log(`Answer changed: ${key} = ${value}`);
    setAnswers(prev => ({
      ...prev,
      [key]: value
    }));
  };

  return (
    <div style={{ padding: '20px', maxWidth: '600px', margin: '0 auto' }}>
      <h2>Quiz Option Selection Test</h2>
      <p>This component tests if radio button selections work correctly.</p>
      
      {testQuestions.map((question, qIndex) => (
        <div key={question.key} style={{ marginBottom: '30px', border: '1px solid #ccc', padding: '15px' }}>
          <h3>{question.question}</h3>
          <div>
            {question.options.map((option, oIndex) => (
              <label key={option.value} style={{ display: 'block', margin: '10px 0', cursor: 'pointer' }}>
                <input
                  type="radio"
                  name={question.key}
                  value={option.value}
                  checked={answers[question.key] === option.value}
                  onChange={(e) => handleAnswerChange(question.key, parseInt(e.target.value))}
                  style={{ marginRight: '10px' }}
                />
                <span>Option {option.value}: {option.label}</span>
              </label>
            ))}
          </div>
          <div style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
            Selected: {answers[question.key] !== undefined ? `Option ${answers[question.key]}` : 'None'}
          </div>
        </div>
      ))}
      
      <div style={{ marginTop: '30px', padding: '15px', backgroundColor: '#f5f5f5' }}>
        <h4>Current Answers State:</h4>
        <pre>{JSON.stringify(answers, null, 2)}</pre>
      </div>
    </div>
  );
}