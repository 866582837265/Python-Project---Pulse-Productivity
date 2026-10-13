import React from "react";
import { useStreak } from "./contexts/StreakContext";
import { DISPLAY_STREAK, STREAK_DATA } from "./constants/streakConstants";

function StreakBadge() {
  const { streak, loading } = useStreak();
  
  if (loading) return <div>Loading...</div>;
  if (!streak) return <div>No streak</div>;

  const thisWeekCount = (streak.week_counts || []).reduce((a, b) => a + b, 0);

  return (
    <div className="streak-badge">
      <div>🔥 Current streak: {DISPLAY_STREAK}</div>
      <div>📅 Total days: {STREAK_DATA.total_days}</div>
      <div>📈 This week: {STREAK_DATA.this_week}/7</div>
      <div>Weekly summary: {streak.weekly_summary_in_progress ? "In progress" : "Complete"}</div>
    </div>
  );
}

export default StreakBadge;