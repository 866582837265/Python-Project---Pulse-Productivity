# Profile Page Debug Guide

## Issues Fixed ✅

### 1. **AuthContext Mismatch**
- **Problem**: App.jsx didn't use AuthProvider but UserProfile.jsx expected it
- **Solution**: Wrapped App with AuthProvider and made UserProfile work with both contexts and props

### 2. **Missing Props**
- **Problem**: UserProfile expected user prop but wasn't receiving it
- **Solution**: Added user prop passing in App.jsx routes

### 3. **Navigation Props Mismatch**
- **Problem**: Navigation component expected different props
- **Solution**: Fixed prop passing to Navigation component

### 4. **API Method Mismatches**
- **Problem**: Some API calls didn't match available methods
- **Solution**: Updated API calls to use correct methods

## Quick Debug Steps

### Step 1: Check if Backend is Running
```bash
cd backend
python app.py
```
Backend should start on `http://localhost:5000`

### Step 2: Check if Frontend is Running
```bash
cd frontend
npm run dev
```
Frontend should start on `http://localhost:5173`

### Step 3: Test Profile Page Access

1. **Login first** - Go to `http://localhost:5173` and login
2. **Navigate to profile** - Click Profile in navigation or go to `http://localhost:5173/profile`
3. **Check browser console** - Look for any JavaScript errors

### Step 4: Common Issues & Solutions

#### Issue: "Profile page shows blank/loading forever"
**Check:**
- Browser console for errors
- Network tab for failed API calls
- User data in localStorage

**Solution:**
```javascript
// Check in browser console:
localStorage.getItem('user')
localStorage.getItem('token')
```

#### Issue: "Navigation not showing"
**Check:**
- User prop is being passed correctly
- Navigation.jsx is imported properly

**Solution:**
```javascript
// In UserProfile.jsx, check if user exists:
console.log('User data:', user);
```

#### Issue: "API calls failing"
**Check:**
- Backend is running on port 5000
- CORS is configured properly
- JWT token is valid

**Solution:**
```bash
# Test backend health:
curl http://localhost:5000/api/health
```

## Files Modified

### Frontend Files:
1. **App.jsx** - Added AuthProvider wrapper and user prop passing
2. **UserProfile.jsx** - Made compatible with both AuthContext and props
3. **UserProfile.css** - Ensured proper styling (already existed)

### Key Changes Made:

#### App.jsx:
```javascript
// Added AuthProvider wrapper
function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ThemeProvider>
  );
}

// Added user prop to profile route
<Route
  path="/profile"
  element={
    user ? (
      <UserProfile user={user} onLogout={handleLogout} />
    ) : (
      <Navigate to="/" replace />
    )
  }
/>
```

#### UserProfile.jsx:
```javascript
// Made compatible with both prop and localStorage user
const user = propUser || JSON.parse(localStorage.getItem('user') || '{}');

// Added proper error handling
if (!user?.email) {
  console.error('[PROFILE] No user data available');
  navigate('/');
  return;
}
```

## Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend starts without errors  
- [ ] Can login successfully
- [ ] Profile page loads (shows loading spinner first)
- [ ] Profile data displays correctly
- [ ] Navigation works
- [ ] No console errors
- [ ] Can change avatar
- [ ] Can add platform links
- [ ] Progress data loads (if platform links exist)

## Debug Commands

### Check User Data:
```javascript
// In browser console:
console.log('User:', JSON.parse(localStorage.getItem('user')));
console.log('Token:', localStorage.getItem('token'));
```

### Test API Endpoints:
```bash
# Health check
curl http://localhost:5000/api/health

# Profile endpoint (replace TOKEN with actual token)
curl -H "Authorization: Bearer TOKEN" http://localhost:5000/api/user/profile
```

### Check Network Requests:
1. Open browser DevTools (F12)
2. Go to Network tab
3. Navigate to profile page
4. Look for failed requests (red entries)

## Expected Behavior

1. **On Profile Page Load:**
   - Shows loading spinner initially
   - Makes API call to `/api/user/profile`
   - Displays user information
   - Shows platform connection status

2. **User Information Displayed:**
   - Username/name
   - Email address
   - Skill level
   - Assessment status
   - Avatar (clickable to change)

3. **Platform Integration:**
   - Input fields for LeetCode/HackerRank usernames
   - Connect/Save buttons
   - Progress stats (if connected)
   - Sync functionality

## Troubleshooting

### If Profile Page is Blank:
1. Check browser console for errors
2. Verify user is logged in
3. Check if API calls are successful
4. Ensure CSS is loading

### If Getting 401 Errors:
1. Check if token exists in localStorage
2. Try logging out and back in
3. Verify backend JWT secret matches

### If Styling is Missing:
1. Check if UserProfile.css is imported
2. Verify CSS file exists
3. Check for CSS syntax errors

The profile page should now load correctly with proper error handling and fallbacks!