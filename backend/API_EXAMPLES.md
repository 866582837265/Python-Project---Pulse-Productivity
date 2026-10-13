# ML Prediction & Roadmap API Examples

## 1. ML Prediction API - `/api/model/predict`

### Request:
```json
POST /api/model/predict
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "correct_answers": 6,
  "total_questions": 10,
  "avg_time": 35
}
```

### Response:
```json
{
  "success": true,
  "predicted_level": "Intermediate",
  "confidence": 0.85,
  "features_used": {
    "correct_answers": 6,
    "total_questions": 10,
    "avg_time": 35,
    "accuracy": 60.0
  },
  "message": "Skill level predicted: Intermediate"
}
```

## 2. Personalized Roadmap API - `/api/roadmap`

### Request:
```json
GET /api/roadmap
Authorization: Bearer <jwt_token>
```

### Response:
```json
{
  "success": true,
  "skill_level": "Intermediate",
  "roadmap": {
    "title": "DSA Skill Development",
    "duration": "4-6 months",
    "description": "Master intermediate concepts and problem-solving patterns",
    "skill_level": "Intermediate",
    "generated_at": "2024-01-15T10:30:00Z",
    "topics": [
      {
        "week": "1-2",
        "topic": "Trees & Binary Search",
        "subtopics": ["Binary trees", "BST operations", "Tree traversals"],
        "problems": ["Binary Tree Inorder", "Validate BST", "Lowest Common Ancestor"],
        "resources": ["Tree algorithms", "Binary search patterns"]
      },
      {
        "week": "3-4",
        "topic": "Hash Tables & Maps",
        "subtopics": ["Hash functions", "Collision handling", "Applications"],
        "problems": ["Group Anagrams", "Subarray Sum", "Longest Substring"],
        "resources": ["Hash table implementations", "Time complexity analysis"]
      }
    ]
  },
  "message": "Personalized roadmap generated for Intermediate level"
}
```

## 3. Enhanced Quiz Submission - `/api/quiz/submit`

The quiz submission now automatically triggers ML prediction and returns both score and predicted level:

### Response:
```json
{
  "success": true,
  "domain": "programming",
  "score": 6,
  "total_questions": 10,
  "percentage": 60.0,
  "skill_level": "Intermediate",
  "roadmap": {
    "title": "DSA Skill Development",
    "duration": "4-6 months"
  },
  "message": "Quiz completed! Score: 6/10 (60.0%)"
}
```

## MongoDB Collections

### Users Collection (Updated):
```json
{
  "_id": ObjectId,
  "email": "user@example.com",
  "username": "john_doe",
  "skill_level": "Intermediate",
  "predicted_level": "Intermediate",
  "last_assessment": "2024-01-15T10:30:00Z",
  "problems_solved": 25,
  "streak": 5
}
```

### Roadmaps Collection (New):
```json
{
  "_id": ObjectId,
  "user_id": "user_123",
  "user_email": "user@example.com",
  "skill_level": "Intermediate",
  "roadmap": {
    "title": "DSA Skill Development",
    "topics": [...]
  },
  "created_at": "2024-01-15T10:30:00Z",
  "status": "active"
}
```