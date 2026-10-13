# 🔥 Enhanced Streak Tracking System

## Overview

The Pulse application now features a comprehensive streak tracking system that automatically monitors user activity and maintains learning streaks based on login and practice activities.

## Features

### ✨ Dynamic Streak Calculation
- **Automatic tracking** of login and practice activities
- **Smart streak logic** that handles edge cases properly
- **Real-time updates** with immediate feedback
- **Persistent storage** in both MongoDB and file-based systems

### 📊 Comprehensive Analytics
- Current streak counter
- Longest streak achieved
- Total active days
- Weekly and monthly activity summaries
- Streak risk assessment
- Activity history visualization

### 🎯 Activity Types Supported
- **Login streaks** - Daily login tracking
- **Practice streaks** - Coding practice and problem solving
- **Quiz streaks** - Assessment and quiz completion
- **Pomodoro streaks** - Focus session completion

## How It Works

### Streak Logic Rules

1. **If last activity was yesterday**: Increment streak by 1
2. **If last activity was today**: Do nothing (no update)
3. **If last activity was before yesterday**: Reset streak to 1
4. **If no previous activity**: Start streak at 1

### Automatic Triggers

The system automatically updates streaks when users:
- Log into the application
- Complete practice problems
- Finish quiz assessments
- Complete Pomodoro sessions
- Mark practice as complete

## API Endpoints

### Get Streak Data
```http
GET /api/streaks
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "current_streak": 5,
    "longest_streak": 12,
    "total_active_days": 45,
    "last_activity": "2024-01-15T10:30:00Z",
    "last_activity_type": "practice",
    "streak_risk": "Low",
    "recent_activity": {
      "days_active_last_week": 6,
      "days_active_last_month": 22
    }
  }
}
```

### Update Streak Manually
```http
POST /api/streaks/update
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "activity_type": "practice"
}
```

### Get Streak History
```http
GET /api/streaks/history
Authorization: Bearer <jwt_token>
```

## Frontend Integration

### StreakTracker Component

The enhanced `StreakTracker.jsx` component provides:

- **Visual streak display** with animated counters
- **Activity buttons** for manual streak updates
- **Risk indicators** showing streak status
- **Historical calendar** showing last 30 days
- **Real-time notifications** for streak updates

### Key Features

```jsx
// Automatic data fetching
useEffect(() => {
  fetchStreakData();
  fetchStreakHistory();
}, []);

// Manual streak updates
const updateStreak = async (activityType = 'practice') => {
  // Updates streak and shows notification
};

// Risk assessment display
const getStreakRiskMessage = (risk, lastActivity) => {
  // Returns appropriate message based on risk level
};
```

## Database Schema

### User Document Extensions
```javascript
{
  // Existing user fields...
  
  // Enhanced streak tracking
  current_streak: Number,
  longest_streak: Number,
  total_active_days: Number,
  last_streak_activity: String, // ISO date
  last_activity_type: String,   // "login", "practice", "quiz"
  streak_history: [
    {
      date: String,        // YYYY-MM-DD
      streak: Number,      // Streak count on that day
      activity_type: String,
      timestamp: String    // Full ISO timestamp
    }
  ],
  streak_risk: String,     // "Low", "Medium", "High"
  streak_updated_at: String
}
```

## Edge Cases Handled

### ✅ Proper Date Handling
- Timezone-aware calculations using UTC
- Handles date parsing errors gracefully
- Validates date formats before processing

### ✅ Multiple Activities Per Day
- Only counts one streak increment per day
- Tracks multiple activity types in history
- Prevents duplicate streak updates

### ✅ Streak Breaks
- Automatically detects gaps in activity
- Resets streaks appropriately
- Provides clear feedback on streak status

### ✅ Data Persistence
- Works with both MongoDB and file storage
- Handles database connection failures
- Maintains data integrity across sessions

## Usage Examples

### Backend Integration

```python
from streak_service import StreakService

# Update streak on login
result = StreakService.trigger_login_streak(
    users_collection, 
    in_memory_users, 
    user_email
)

# Update streak on practice
result = StreakService.trigger_practice_streak(
    users_collection, 
    in_memory_users, 
    user_email
)

# Get comprehensive streak data
streak_data = StreakService.get_streak_data(
    users_collection, 
    in_memory_users, 
    user_email
)
```

### Frontend Usage

```jsx
import StreakTracker from './StreakTracker';

function App() {
  return (
    <div>
      <StreakTracker />
    </div>
  );
}
```

## Testing

Run the test script to verify functionality:

```bash
cd backend
python test_streak_system.py
```

This will test:
- First-time activity tracking
- Consecutive day logic
- Gap detection and reset
- Risk assessment
- Edge cases and error handling

## Customization

### Streak Risk Thresholds
Modify `_calculate_streak_risk()` in `streak_service.py`:

```python
@staticmethod
def _calculate_streak_risk(last_activity: Optional[str]) -> str:
    # Customize risk calculation logic
    if days_since == 0:
        return "Low"     # Active today
    elif days_since == 1:
        return "Medium"  # Need activity today
    else:
        return "High"    # Streak broken
```

### Activity Types
Add new activity types by calling:

```python
StreakService.update_user_streak(
    users_collection, 
    in_memory_users, 
    user_email, 
    "custom_activity_type"
)
```

## Troubleshooting

### Common Issues

1. **Streaks not updating**: Check JWT token validity
2. **Date calculation errors**: Verify timezone settings
3. **Database connection issues**: Check MongoDB connection
4. **Frontend not refreshing**: Clear browser cache

### Debug Mode

Enable debug logging in the backend:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Considerations

- Streak history is limited to 60 days to prevent excessive storage
- Database queries are optimized for single-user lookups
- Frontend updates are batched to reduce API calls
- Caching is implemented for frequently accessed data

## Future Enhancements

- [ ] Weekly and monthly streak challenges
- [ ] Social streak sharing and leaderboards
- [ ] Streak recovery mechanisms
- [ ] Advanced analytics and insights
- [ ] Integration with external fitness/habit trackers
- [ ] Customizable streak goals and milestones

---

**Note**: This system is designed to encourage consistent learning habits while providing meaningful feedback to users about their progress and engagement patterns.