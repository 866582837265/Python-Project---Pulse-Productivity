import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./Dashboard.css";

export default function DashboardSimple({ user: propUser, onLogout }) {
  const [user, setUser] = useState(propUser || { name: "User", username: "User" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        navigate("/");
        return;
      }

      console.log("Fetching dashboard data...");
      
      const response = await axios.get("http://localhost:5000/api/dashboard", {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      console.log("Dashboard response:", response.data);
      
      if (response.data?.success) {
        setUser(response.data.user);
        setError(null);
      } else {
        setError("Failed to load user data");
      }
    } catch (error) {
      console.error("Dashboard error:", error);
      setError(error.message);
      
      if (error.response?.status === 401) {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        navigate("/");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    if (onLogout) onLogout();
    navigate("/");
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading-state">
          <h2>Loading dashboard...</h2>
          <button onClick={() => setLoading(false)}>Skip Loading</button>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <div className="loading-state">
          <h2>Error: {error}</h2>
          <button onClick={fetchUserData}>Retry</button>
          <button onClick={handleLogout}>Logout</button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <nav className="dashboard-nav">
        <div className="nav-content">
          <div className="nav-brand">
            <h1 className="brand-wordmark">Pulse</h1>
          </div>
          <div className="nav-profile">
            <button onClick={handleLogout}>Logout</button>
          </div>
        </div>
      </nav>

      <main className="dashboard-main">
        <section className="welcome-section">
          <div className="welcome-header">
            <h1>Welcome back, {user.username || user.name || 'User'}! 👋</h1>
            <p>Dashboard is working!</p>
          </div>
          
          <div className="quick-stats">
            <div className="stat-card">
              <div className="stat-number">{user.problems_solved || 0}</div>
              <div className="stat-label">Problems Solved</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{user.streak || 0}</div>
              <div className="stat-label">Day Streak</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{user.skill_level || 'Beginner'}</div>
              <div className="stat-label">Skill Level</div>
            </div>
          </div>

          <div className="action-buttons">
            <button className="btn-primary">Take Assessment</button>
            <button className="btn-secondary">View Roadmap</button>
          </div>
        </section>
      </main>
    </div>
  );
}