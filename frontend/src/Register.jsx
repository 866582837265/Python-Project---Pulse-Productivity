import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import { API_BASE_URL } from "./config";
import ThemeToggle from "./ThemeToggle";
import "./Register.css";

export default function Register({ onRegister }) {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");

    if (password !== confirmPassword) {
      setMessage("❌ Passwords do not match");
      setLoading(false);
      return;
    }

    if (password.length < 6) {
      setMessage("❌ Password must be at least 6 characters long");
      setLoading(false);
      return;
    }

    try {
      // Clear any existing user data to ensure clean registration
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      localStorage.removeItem("skillAssessment");
      
      console.log(`[REGISTER] Attempting registration for: ${email}`);
      
      const response = await axios.post(`${API_BASE_URL}/api/auth/register`, {
        username,
        email,
        password
      });

      const data = response.data;

      if (data.success) {
        console.log(`[REGISTER] Registration successful for: ${email}`);
        setMessage("✅ Registration successful! Redirecting to login...");
        
        setTimeout(() => {
          navigate("/");
        }, 1500);
      } else {
        setMessage(`❌ ${data.message || "Registration failed"}`);
      }
    } catch (error) {
      console.error(`[REGISTER] Registration error for ${email}:`, error);
      const errorMessage = error.response?.data?.message || error.message || "Network/server error";
      setMessage(`❌ ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-container">
      <div className="theme-toggle-container" style={{ position: 'absolute', top: '20px', right: '20px', zIndex: 1000 }}>
        <ThemeToggle />
      </div>
      <div className="glass-card">
        {/* App Brand Wordmark */}
        <div className="brand-section">
          <h1 className="brand-wordmark">Pulse</h1>
          <p className="brand-tagline">Keep the momentum going..</p>
        </div>

        {/* Register Form */}
        <form onSubmit={handleRegister} className="register-form">
          <h2 className="form-title">Create your account</h2>

          <div className="form-group">
            <input
              type="text"
              placeholder=" "
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              id="username"
            />
            <label htmlFor="username">Username</label>
          </div>

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
              minLength="6"
            />
            <label htmlFor="password">Password</label>
          </div>

          <div className="form-group">
            <input
              type="password"
              placeholder=" "
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              id="confirmPassword"
            />
            <label htmlFor="confirmPassword">Confirm Password</label>
          </div>

          <button type="submit" className="register-button" disabled={loading}>
            {loading ? (
              <span className="loading-content">
                <div className="spinner"></div>
                Creating account...
              </span>
            ) : (
              "Register"
            )}
          </button>

          {message && (
            <div className={`message ${message.includes('✅') ? 'success' : 'error'}`}>
              {message}
            </div>
          )}
        </form>

        {/* Login Link */}
        <div className="login-section">
          <p className="login-text">
            Already have an account?{" "}
            <Link to="/" className="login-link">
              Login
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}