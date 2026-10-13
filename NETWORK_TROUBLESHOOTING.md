# Network Error Troubleshooting Guide

## Quick Fix Checklist

### 1. Verify Both Servers Are Running

**Backend (Flask - Port 5000):**
```bash
cd backend
python app.py
```
Should show: `Running on http://127.0.0.1:5000`

**Frontend (React - Port 5173):**
```bash
cd frontend
npm run dev
```
Should show: `Local: http://localhost:5173`

### 2. Test Backend Health

Open in browser: http://127.0.0.1:5000/api/health

Should return:
```json
{
  "status": "ok",
  "message": "Backend is healthy",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 3. Run Automated Tests

**Backend Test:**
```bash
cd backend
python test_backend.py
```

**Full Setup Test:**
```bash
python test_setup.py
```

### 4. Common Issues & Solutions

#### Issue: "Network error. Please check your connection"

**Cause:** Frontend can't reach backend

**Solutions:**
1. Ensure backend is running on port 5000
2. Check if another process is using port 5000:
   ```bash
   netstat -an | findstr :5000
   ```
3. Try accessing backend directly: http://127.0.0.1:5000

#### Issue: CORS Errors in Browser Console

**Cause:** Cross-origin request blocked

**Solutions:**
1. Backend CORS is already configured for ports 3000 and 5173
2. Ensure you're using the correct frontend port
3. Check browser console for specific CORS error messages

#### Issue: "Authentication failed" or 401 Errors

**Cause:** JWT token issues

**Solutions:**
1. Clear browser localStorage:
   ```javascript
   localStorage.clear()
   ```
2. Login again to get fresh token
3. Check if token is being sent in requests

#### Issue: Backend Returns HTML Instead of JSON

**Cause:** Flask error page being returned

**Solutions:**
1. Check backend console for Python errors
2. Ensure all endpoints use `jsonify()` for responses
3. Global error handler is now configured to return JSON

### 5. Manual Testing Steps

1. **Test Backend Directly:**
   ```bash
   curl http://127.0.0.1:5000/api/health
   ```

2. **Test CORS:**
   ```bash
   curl -X OPTIONS http://127.0.0.1:5000/api/quiz/submit \
        -H "Origin: http://localhost:3000" \
        -H "Access-Control-Request-Method: POST"
   ```

3. **Test Quiz Submission (with token):**
   ```bash
   curl -X POST http://127.0.0.1:5000/api/quiz/submit \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer YOUR_TOKEN" \
        -d '{"score": 3}'
   ```

### 6. Frontend Network Test Component

Add this to your React app for live testing:

```jsx
import NetworkTest from './NetworkTest';

// Use in your app
<NetworkTest />
```

This component will test:
- Backend health check
- Basic API endpoints
- CORS configuration
- Authentication flow

### 7. Environment Configuration

**Backend (.env file):**
```env
FLASK_ENV=development
FLASK_DEBUG=True
JWT_SECRET=your-secret-key
MONGODB_URI=your-mongodb-connection-string
```

**Frontend (config.js):**
```javascript
const API_BASE_URL = 'http://localhost:5000';
```

### 8. Port Configuration

**Default Ports:**
- Backend: 5000 (Flask)
- Frontend: 5173 (Vite) or 3000 (Create React App)

**If ports conflict:**
1. Change backend port in `app.py`:
   ```python
   app.run(debug=True, host='localhost', port=5001)
   ```
2. Update frontend config:
   ```javascript
   const API_BASE_URL = 'http://localhost:5001';
   ```

### 9. Browser Developer Tools

**Check Network Tab:**
1. Open DevTools (F12)
2. Go to Network tab
3. Try the failing action
4. Look for failed requests (red entries)
5. Click on failed request to see details

**Check Console Tab:**
1. Look for JavaScript errors
2. Look for CORS errors
3. Look for network timeout errors

### 10. Success Indicators

When everything works correctly, you should see:

**Backend Console:**
```
[INFO] Connected to MongoDB Atlas
✅ [QUIZ] Processing submission for user: user@example.com
🧠 User user@example.com predicted as Intermediate
```

**Frontend Console:**
```
🔄 API POST /api/quiz/submit
📡 Response status: 200
✅ API POST /api/quiz/submit success
```

**Browser Network Tab:**
- All API calls return 200 status
- Response content-type is `application/json`
- No CORS errors

## Still Having Issues?

1. Run the full diagnostic: `python test_setup.py`
2. Check both server logs for error messages
3. Verify all dependencies are installed
4. Try restarting both servers
5. Clear browser cache and localStorage

The enhanced error handling should now provide more specific error messages to help identify the exact issue.