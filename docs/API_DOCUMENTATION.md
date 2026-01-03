# NOUS Intelligence Platform - API Documentation

## Base URL
```
Production: https://nous-intelligence.onrender.com/api/v1
Development: http://localhost:5000/api/v1
```

## Authentication

All endpoints except `/health` require authentication. Authentication is handled via:
- Google OAuth 2.0 (production)
- Demo mode (development/testing)

### Headers
```
Content-Type: application/json
```

### Session-based Authentication
After OAuth login, a session cookie is set. Include this cookie in subsequent requests.

---

## Core Endpoints

### Health Check
Check API health and availability.

**GET** `/health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1704672000.0,
  "version": "1.0.0"
}
```

---

### Get Current User
Retrieve authenticated user information.

**GET** `/user`

**Response:**
```json
{
  "user": {
    "id": "user_123",
    "name": "John Doe",
    "email": "john@example.com",
    "isDemo": false
  }
}
```

---

### Chat with AI Assistant
Send a message to the emotion-aware therapeutic AI assistant.

**POST** `/chat`

**Request:**
```json
{
  "message": "I'm feeling anxious about my presentation tomorrow"
}
```

**Response:**
```json
{
  "response": "I understand that presentations can be anxiety-inducing. Let's work through this together...",
  "emotion": "anxious",
  "skill_recommendations": ["TIPP", "Paced Breathing", "Grounding"],
  "confidence": 0.87
}
```

**Error Responses:**
- `400` - Missing or empty message
- `413` - Message too long (>10,000 characters)
- `500` - Server error

---

### Get Conversations
Retrieve user's conversation history.

**GET** `/conversations`

**Query Parameters:**
- `limit` (optional): Number of conversations to return (default: 50)

**Response:**
```json
[
  {
    "id": "conv_abc123",
    "title": "Anxiety Management",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-02T15:30:00Z"
  }
]
```

---

### Get Conversation Messages
Retrieve messages for a specific conversation.

**GET** `/conversations/{conversation_id}/messages`

**Response:**
```json
{
  "messages": [
    {
      "id": "msg_xyz789",
      "text": "Hello, I need help with anxiety",
      "sender": "user",
      "timestamp": "2024-01-01T12:00:00Z"
    },
    {
      "id": "msg_abc456",
      "text": "I'm here to help. Tell me more about what you're experiencing.",
      "sender": "assistant",
      "timestamp": "2024-01-01T12:00:05Z"
    }
  ]
}
```

---

## Therapeutic Endpoints

### Log Mood Entry
Record a mood entry for tracking.

**POST** `/therapeutic/mood`

**Request:**
```json
{
  "mood": 7,
  "note": "Feeling pretty good today",
  "activities": ["exercise", "meditation"]
}
```

**Response:**
```json
{
  "id": "mood_123",
  "mood": 7,
  "note": "Feeling pretty good today",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### Get Mood History
Retrieve mood entries.

**GET** `/therapeutic/mood`

**Query Parameters:**
- `start_date` (optional): ISO 8601 date
- `end_date` (optional): ISO 8601 date
- `limit` (optional): Max entries to return

**Response:**
```json
[
  {
    "id": "mood_123",
    "mood": 7,
    "note": "Feeling pretty good today",
    "timestamp": "2024-01-01T12:00:00Z"
  }
]
```

---

### Create CBT Thought Record
Log a cognitive behavioral therapy thought record.

**POST** `/therapeutic/cbt/thoughts`

**Request:**
```json
{
  "situation": "Failed a test",
  "automaticThought": "I'm stupid and will never succeed",
  "emotion": "despair",
  "evidence": "I studied hard but still failed",
  "alternativeThought": "One test doesn't define my intelligence",
  "outcome": "Feeling slightly better, more balanced perspective"
}
```

**Response:**
```json
{
  "id": "thought_abc123",
  "message": "Thought record created"
}
```

---

### Get Thought Records
Retrieve CBT thought records.

**GET** `/therapeutic/cbt/thoughts`

**Query Parameters:**
- `limit` (optional): Max records to return

**Response:**
```json
[
  {
    "id": "thought_abc123",
    "situation": "Failed a test",
    "automaticThought": "I'm stupid and will never succeed",
    "emotion": "despair",
    "alternativeThought": "One test doesn't define my intelligence",
    "timestamp": "2024-01-01T12:00:00Z"
  }
]
```

---

### Log DBT Skill
Record usage of a Dialectical Behavior Therapy skill.

**POST** `/therapeutic/dbt/skills/log`

**Request:**
```json
{
  "skill_name": "TIPP",
  "category": "Distress Tolerance",
  "situation": "Feeling overwhelmed before meeting",
  "effectiveness": 8,
  "notes": "Cold water on face helped immediately"
}
```

**Response:**
```json
{
  "id": "skill_xyz789",
  "skill_name": "TIPP",
  "effectiveness": 8,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### Get DBT Skill Logs
Retrieve logged DBT skills.

**GET** `/therapeutic/dbt/skills/logs`

**Query Parameters:**
- `limit` (optional): Max logs to return (default: 50)

**Response:**
```json
[
  {
    "id": "skill_xyz789",
    "skill_name": "TIPP",
    "category": "Distress Tolerance",
    "effectiveness": 8,
    "timestamp": "2024-01-01T12:00:00Z"
  }
]
```

---

### Get DBT Skill Statistics
Retrieve statistics about skill usage.

**GET** `/therapeutic/dbt/skills/stats`

**Query Parameters:**
- `days` (optional): Number of days to include (default: 30)

**Response:**
```json
{
  "total_skills_used": 45,
  "most_used_skill": "TIPP",
  "average_effectiveness": 7.2,
  "skills_by_category": {
    "Distress Tolerance": 20,
    "Emotion Regulation": 15,
    "Mindfulness": 10
  }
}
```

---

### Get Crisis Resources
Retrieve crisis support resources.

**GET** `/therapeutic/crisis/resources`

**Query Parameters:**
- `emergency` (optional): Filter for emergency resources only

**Response:**
```json
[
  {
    "id": "resource_1",
    "name": "988 Suicide & Crisis Lifeline",
    "contact_info": "988",
    "resource_type": "hotline",
    "is_emergency": true,
    "description": "24/7 free and confidential support"
  }
]
```

---

## Error Responses

All endpoints may return these error codes:

- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `413 Payload Too Large` - Request body too large
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

**Error Response Format:**
```json
{
  "error": "Error message describing what went wrong"
}
```

---

## Rate Limiting

API requests are rate-limited to prevent abuse:
- **Authenticated users**: 100 requests per minute
- **Demo mode**: 20 requests per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1704672060
```

---

## Webhooks (Coming Soon)

Webhook support for real-time notifications is planned for a future release.

---

## Support

For API support, contact: support@nous-intelligence.com
