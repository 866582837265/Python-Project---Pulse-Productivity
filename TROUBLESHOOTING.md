# Pulse App - Troubleshooting Guide

## Network Error for /api/roadmap - FIXED

### Issue
Frontend was getting "NETWORK ERROR" when trying to access `/api/roadmap` endpoint.

### Root Causes & Fixes Applied

1. **API Base URL Mismatch**
   - **Problem**: Frontend was using `http://localhost:5000` while backend was running on `http://127.0.0.1:5000`
   - **Fix**: Created `config.js` with `API_BASE_URL = 'http://127.0.0.1:5000'` and updated all components

2. **CORS Configuration**
   - **Problem**: CORS was set to allow all origins (`*`) which can cause issues
   - **Fix**: Updated CORS to allow specific origins: `["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"]`

3. **Backend Host Configuration**
   - **Problem**: Flask was running on default host
   - **Fix**: Explicitly set Flask to run on `host='127.0.0.1'`

4. **Error Handling in Roadmap Generation**
   - **Problem**: Poor error handling in roadmap generation
   - **Fix**: Added comprehensive error handling and logging

### Files Modified

#### Backend (`backend/app.py`)
- Fixed CORS configuration
- Updated Flask host configuration
- Enhanced error handling in `/api/roadmap` endpoint
- Added detailed logging for debugging

#### Frontend
- `src/config.js` - New API configuration file
- `src/App.jsx` - Updated API calls
- `src/Login.jsx` - Updated API calls
- `src/Register.jsx` - Updated API calls
- `src/Dashboard.jsx` - Updated API calls
- `src/DuolingoRoadmap.jsx` - Updated API calls
- `src/RoadmapIntegration.jsx` - Updated API calls
- `src/SkillAssessment.jsx` - Updated API calls

### Testing

1. **Backend Test Script**: `test_backend.py`
   ```bash
   python test_backend.py
   ```

2. **Manual Testing**:
   - Start backend: `start_backend.bat` or `python backend/app.py`
   - Start frontend: `start_frontend.bat` or `cd frontend && npm run dev`
   - Test roadmap endpoint: `http://127.0.0.1:5000/api/roadmap/test/Beginner`

## Common Issues & Solutions

### 1. "Network Error" or Connection Refused
- **Check**: Backend is running on `http://127.0.0.1:5000`
- **Check**: Frontend is using correct API_BASE_URL
- **Solution**: Use the provided startup scripts

### 2. CORS Errors
- **Check**: CORS configuration in `app.py`
- **Solution**: Ensure frontend origin is in allowed origins list

### 3. JWT Token Issues
- **Check**: Token is stored in localStorage
- **Check**: Token format is `Bearer <token>`
- **Solution**: Clear localStorage and login again

### 4. Roadmap Not Loading
- **Check**: User has completed skill assessment
- **Check**: Backend logs for roadmap generation errors
- **Solution**: Take assessment first, then access roadmap

### 5. Assessment Already Taken Error
- **Check**: User's assessment status in database
- **Solution**: Use reset endpoint or clear user data

## Environment Setup

### Backend Requirements
```bash
cd backend
pip install -r requirements.txt
```

### Frontend Requirements
```bash
cd frontend
npm install
```

### Environment Variables
Create `backend/.env`:
```env
MONGO_URI=mongodb://localhost:27017/pulseDB
JWT_SECRET=your-secret-key
FLASK_DEBUG=True
FLASK_ENV=development
```

## API Endpoints Status

✅ `/` - Health check
✅ `/api/auth/login` - User login
✅ `/api/auth/register` - User registration
✅ `/api/dashboard` - User dashboard data
✅ `/api/roadmap` - User's personalized roadmap
✅ `/api/roadmap/test/<level>` - Test roadmap generation
✅ `/api/quiz/submit` - Submit skill assessment
✅ `/api/user/assessment-status` - Check assessment status

## Debugging Tips

1. **Check Browser Console**: Look for network errors and API responses
2. **Check Backend Logs**: Look for detailed error messages and user isolation logs
3. **Test API Directly**: Use browser or Postman to test endpoints
4. **Clear Storage**: Clear localStorage if experiencing user data issues
5. **Use Test Scripts**: Run `test_backend.py` to verify backend functionality

## Contact & Support

If issues persist:
1. Check the console logs (both frontend and backend)
2. Verify all dependencies are installed
3. Ensure correct ports are being used (5000 for backend, 5173 for frontend)
4. Test with the provided scripts first