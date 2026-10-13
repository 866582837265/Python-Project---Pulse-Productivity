import React, { createContext, useContext, useState, useEffect } from "react";
import api from "../api";
import { STREAK_DATA } from "../constants/streakConstants";

const StreakContext = createContext();

export function StreakProvider({ children }) {
  const [streak, setStreak] = useState(STREAK_DATA);
  const [loading, setLoading] = useState(true);

  async function fetchStreak() {
    try {
      setLoading(true);
      // Use fixed streak data for now
      setStreak(STREAK_DATA);
    } catch (err) {
      console.error("fetchStreak error", err);
    } finally {
      setLoading(false);
    }
  }

  async function refreshStreak() {
    try {
      // Use fixed streak data for now
      setStreak(STREAK_DATA);
      return STREAK_DATA;
    } catch (err) {
      console.error("refreshStreak error", err);
      await fetchStreak();
    }
  }

  useEffect(() => {
    fetchStreak();
  }, []);

  return (
    <StreakContext.Provider value={{ 
      streak, 
      setStreak, 
      fetchStreak, 
      refreshStreak,
      loading 
    }}>
      {children}
    </StreakContext.Provider>
  );
}

export function useStreak() {
  const context = useContext(StreakContext);
  if (!context) {
    throw new Error("useStreak must be used within a StreakProvider");
  }
  return context;
}