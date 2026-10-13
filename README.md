# Pulse App - Authentication System

A full-stack application with React frontend, Flask backend, and MongoDB database integration for user authentication and data management.

## 🚀 Features

- **User Registration & Login** with JWT authentication
- **Password Hashing** using bcrypt
- **Protected Routes** with JWT middleware
- **MongoDB Integration** with fallback in-memory storage
- **CORS Enabled** for frontend-backend communication
- **Responsive UI** with modern design

## 🛠️ Tech Stack

- **Frontend**: React (Vite), Axios, React Router
- **Backend**: Flask, Flask-CORS, PyMongo, bcrypt, PyJWT
- **Database**: MongoDB (with in-memory fallback for testing)
- **Authentication**: JWT tokens stored in localStorage

## 📁 Project Structure

```
pulse/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment variables
│   ├── .env.example          # Environment template
│   └── [ML model files]      # Existing ML components
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Main app with routing
│   │   ├── Login.jsx         # Login component
│   │   ├── Register.jsx      # Registration component
│   │   ├── Dashboard.jsx     # Protected dashboard
│   │   └── [other components]
│   ├── package.json          # Node dependencies
│   └── [Vite config files]
└── README.md
```

## 🔧 Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB (optional - app works with in-memory storage)

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file:
   ```env
   # For MongoDB Atlas (cloud):
   MONGO_URI=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/pulseDB?retryWrites=true&w=majority
   
   # For local MongoDB:
   # MONGO_URI=mongodb://localhost:27017/pulseDB
   
   # For testing without MongoDB (uses in-memory storage):
   MONGO_URI=
   
   JWT_SECRET=your-super-secret-jwt-key-change-in-production
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```

4. **Start the Flask server**:
   ```bash
   python app.py
   ```
   
   Server will run on `http://127.0.0.1:5000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Node dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```
   
   Frontend will run on `http://localhost:5173`

## 🔐 API Endpoints

### Authentication Routes

- **POST** `/api/auth/register`
  - Body: `{ "username": "string", "email": "string", "password": "string" }`
  - Response: `{ "success": true, "message": "Registration successful", "user": {...} }`

- **POST** `/api/auth/login`
  - Body: `{ "email": "string", "password": "string" }`
  - Response: `{ "success": true, "token": "jwt_token", "user": {...} }`

### Protected Routes (Require JWT Token)

- **GET** `/api/dashboard`
  - Headers: `Authorization: Bearer <jwt_token>`
  - Response: User dashboard data

- **GET** `/api/user/profile`
  - Headers: `Authorization: Bearer <jwt_token>`
  - Response: User profile information

## 🔄 User Flow

1. **Registration**: User registers → Redirected to login page
2. **Login**: User logs in → JWT token stored in localStorage → Redirected to dashboard
3. **Dashboard**: Protected route accessible only with valid JWT token
4. **Logout**: Token removed from localStorage → Redirected to login

## 🗄️ Database Schema

### Users Collection

```javascript
{
  _id: ObjectId,
  email: String (unique, required),
  username: String (required),
  password: String (hashed with bcrypt),
  createdAt: Date,
  skill_level: String (default: "Beginner"),
  problems_solved: Number (default: 0),
  streak: Number (default: 0),
  learning_style: String (default: "Balanced")
}
```

## 🛡️ Security Features

- **Password Hashing**: bcrypt with salt
- **JWT Authentication**: Secure token-based auth
- **CORS Protection**: Configured for specific origins
- **Input Validation**: Server-side validation for all inputs
- **Protected Routes**: Middleware to verify JWT tokens

## 🧪 Testing

The application includes fallback in-memory storage for testing without MongoDB:

1. Set `MONGO_URI=` (empty) in `.env`
2. Start the backend - it will use in-memory storage
3. Register and login will work normally
4. Data persists only during server runtime

## 🚀 Production Deployment

### Backend

1. Set production environment variables
2. Use a production WSGI server (e.g., Gunicorn)
3. Configure MongoDB Atlas or production MongoDB instance
4. Update CORS origins for production frontend URL

### Frontend

1. Build the production bundle: `npm run build`
2. Deploy to static hosting (Vercel, Netlify, etc.)
3. Update API URLs to production backend

## 🔧 MongoDB Setup Options

### Option 1: MongoDB Atlas (Cloud)

1. Create account at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a cluster
3. Get connection string
4. Update `MONGO_URI` in `.env`

### Option 2: Local MongoDB

1. Install [MongoDB Community Server](https://www.mongodb.com/try/download/community)
2. Start MongoDB service
3. Use `MONGO_URI=mongodb://localhost:27017/pulseDB`

### Option 3: In-Memory Testing

1. Set `MONGO_URI=` (empty)
2. Application will use in-memory storage
3. Perfect for development and testing

## 🐛 Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure backend CORS is configured for frontend URL
2. **MongoDB Connection**: Check connection string and network access
3. **JWT Errors**: Verify JWT_SECRET is set and consistent
4. **Port Conflicts**: Ensure ports 5000 (backend) and 5173 (frontend) are available

### Debug Mode

Enable debug logging by setting `FLASK_DEBUG=True` in `.env`

## 📝 License

This project is part of the Pulse productivity application.