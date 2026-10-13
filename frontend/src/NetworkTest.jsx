import React, { useState, useEffect } from 'react';
import { api } from './api';

export default function NetworkTest() {
  const [testResults, setTestResults] = useState({});
  const [testing, setTesting] = useState(false);

  const runTests = async () => {
    setTesting(true);
    const results = {};

    // Test 1: Health Check
    try {
      const healthy = await api.healthCheck();
      results.healthCheck = { success: healthy, error: null };
    } catch (error) {
      results.healthCheck = { success: false, error: error.message };
    }

    // Test 2: Basic API endpoint
    try {
      const response = await fetch('http://127.0.0.1:5000/api/test');
      const data = await response.json();
      results.basicEndpoint = { success: response.ok, data, error: null };
    } catch (error) {
      results.basicEndpoint = { success: false, error: error.message };
    }

    // Test 3: CORS preflight
    try {
      const response = await fetch('http://127.0.0.1:5000/api/quiz/submit', {
        method: 'OPTIONS',
        headers: {
          'Origin': 'http://localhost:3000',
          'Access-Control-Request-Method': 'POST',
          'Access-Control-Request-Headers': 'Content-Type,Authorization'
        }
      });
      results.corsTest = { success: response.ok, status: response.status, error: null };
    } catch (error) {
      results.corsTest = { success: false, error: error.message };
    }

    // Test 4: Protected endpoint (should return 401)
    try {
      await api.getDashboard();
      results.authTest = { success: false, error: 'Should have returned 401' };
    } catch (error) {
      results.authTest = { 
        success: error.message.includes('Authentication failed'), 
        error: error.message 
      };
    }

    setTestResults(results);
    setTesting(false);
  };

  useEffect(() => {
    runTests();
  }, []);

  const TestResult = ({ name, result }) => (
    <div style={{ 
      padding: '10px', 
      margin: '5px 0', 
      border: '1px solid #ccc', 
      borderRadius: '5px',
      backgroundColor: result.success ? '#d4edda' : '#f8d7da'
    }}>
      <strong>{name}:</strong> {result.success ? '✅ PASS' : '❌ FAIL'}
      {result.error && <div style={{ fontSize: '12px', color: '#666' }}>Error: {result.error}</div>}
      {result.data && <div style={{ fontSize: '12px', color: '#666' }}>Data: {JSON.stringify(result.data)}</div>}
      {result.status && <div style={{ fontSize: '12px', color: '#666' }}>Status: {result.status}</div>}
    </div>
  );

  return (
    <div style={{ padding: '20px', maxWidth: '600px', margin: '0 auto' }}>
      <h2>🔍 Network Connectivity Test</h2>
      <p>Testing connection between React frontend (port 3000) and Flask backend (port 5000)</p>
      
      <button 
        onClick={runTests} 
        disabled={testing}
        style={{ 
          padding: '10px 20px', 
          marginBottom: '20px',
          backgroundColor: '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '5px',
          cursor: testing ? 'not-allowed' : 'pointer'
        }}
      >
        {testing ? '🔄 Testing...' : '🔄 Run Tests'}
      </button>

      <div>
        {Object.keys(testResults).length === 0 && !testing && (
          <p>Click "Run Tests" to check connectivity</p>
        )}
        
        {testing && <p>🔄 Running connectivity tests...</p>}
        
        {Object.entries(testResults).map(([name, result]) => (
          <TestResult key={name} name={name} result={result} />
        ))}
      </div>

      {Object.keys(testResults).length > 0 && (
        <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '5px' }}>
          <h3>📋 Summary</h3>
          <p><strong>Backend URL:</strong> http://127.0.0.1:5000</p>
          <p><strong>Frontend URL:</strong> http://localhost:3000</p>
          <p><strong>Tests Passed:</strong> {Object.values(testResults).filter(r => r.success).length}/{Object.keys(testResults).length}</p>
          
          {Object.values(testResults).every(r => r.success) ? (
            <div style={{ color: 'green', fontWeight: 'bold' }}>
              ✅ All tests passed! Network connectivity is working properly.
            </div>
          ) : (
            <div style={{ color: 'red', fontWeight: 'bold' }}>
              ❌ Some tests failed. Check the console for details and ensure both servers are running.
            </div>
          )}
        </div>
      )}
    </div>
  );
}