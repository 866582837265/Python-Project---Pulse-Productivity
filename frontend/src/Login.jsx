import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import { API_BASE_URL } from "./config";
import ThemeToggle from "./ThemeToggle";
import "./Login.css";

export default function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      // Clear any previous user data to ensure isolation
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      localStorage.removeItem("skillAssessment");
      
      console.log(`[LOGIN] Attempting login for: ${email}`);
      
      const response = await axios.post(`${API_BASE_URL}/api/auth/login`, {
        email,
        password
      });

      const data = response.data;

      if (data.success) {
        console.log(`[LOGIN] Login successful for: ${email}`);
        console.log(`[LOGIN] Assessment taken: ${data.user.assessment_taken}`);
        
        setMessage("✅ Login successful!");
        
        // Store new user's data
        localStorage.setItem("token", data.token);
        localStorage.setItem("user", JSON.stringify(data.user));
        
        if (onLogin) {
          onLogin(data.user);
        }
        
        setTimeout(() => {
          navigate("/dashboard");
        }, 1000);
      } else {
        setMessage(`❌ ${data.message || "Login failed"}`);
      }
    } catch (error) {
      console.error(`[LOGIN] Login error for ${email}:`, error);
      const errorMessage = error.response?.data?.message || error.message || "Network/server error";
      setMessage(`❌ ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = () => {
    // Navigate to forgot password page or show modal
    console.log("Forgot password clicked");
  };

  return (
    <div className="login-container">
      <div className="theme-toggle-container" style={{ position: 'absolute', top: '20px', right: '20px', zIndex: 1000 }}>
        <ThemeToggle />
      </div>
      <div className="glass-card">
        {/* App Brand Wordmark */}
        <div className="brand-section">
          <h1 className="brand-wordmark">Pulse</h1>
          <p className="brand-tagline">Keep the momentum going..</p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleLogin} className="login-form">
          <h2 className="form-title">Welcome back</h2>

          <div className="form-group">
            <input
              type="email"
              placeholder=" "
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              id="email"
            />
            <label htmlFor="email">Email address</label>
          </div>

          <div className="form-group">
            <input
              type="password"
              placeholder=" "
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              id="password"
            />
            <label htmlFor="password">Password</label>
          </div>

          <button type="submit" className="login-button" disabled={loading}>
            {loading ? (
              <span className="loading-content">
                <div className="spinner"></div>
                Signing in...
              </span>
            ) : (
              "Sign in"
            )}
          </button>

          {message && (
            <div className={`message ${message.includes('✅') ? 'success' : 'error'}`}>
              {message}
            </div>
          )}

          {/* Forgot Password Link */}
          <button
            type="button"
            className="forgot-password-link"
            onClick={handleForgotPassword}
          >
            Forgot your password?
          </button>
        </form>

        {/* Sign Up Link */}
        <div className="signup-section">
          <p className="signup-text">
            Don't have an account?{" "}
            <Link to="/register" className="signup-link">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
