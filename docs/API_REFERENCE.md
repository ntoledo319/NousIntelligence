# NOUS Personal Assistant - API Reference

## Overview

The NOUS API provides comprehensive endpoints for health monitoring, authentication, analytics, search, notifications, financial management, collaboration, and more. All endpoints return JSON responses and use standard HTTP status codes.

## Base URL

- **Local Development**: `http://localhost:5000`
- **Production**: `https://your-app.replit.app`

## Authentication

The application uses Google OAuth 2.0 for authentication. Most endpoints require authentication except for public health checks and the landing page.

### Authentication Flow

1. User visits landing page
2. Click "Sign in with Google"
3. Redirect to Google OAuth
4. Return to application with session
5. Access protected endpoints

## Health & Monitoring Endpoints

### GET /health

Basic health check endpoint.

**Response**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-27T12:00:00.000Z",
  "uptime": 3600.5
}
```

**Status Codes**
- `200 OK` - Service is healthy

### GET /healthz

Detailed health check with system metrics.

**Response**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-27T12:00:00.000Z",
  "uptime": 3600.5,
  "system": {
    "memory_percent": 45.2,
    "cpu_percent": 12.8,
    "available_memory": 2147483648
  }
}
```

**Status Codes**
- `200 OK` - Service is healthy
- `503 Service Unavailable` - Service is degraded

## Authentication Endpoints

### GET /

Landing page with Google OAuth login button.

**Response**
- HTML page with login interface

### GET /login

Initiate Google OAuth authentication flow.

**Response**
- Redirect to Google OAuth consent screen

### GET /oauth/callback

Handle Google OAuth callback with authorization code.

**Parameters**
- `code` (query) - Authorization code from Google
- `state` (query) - CSRF protection token

**Response**
- Redirect to `/app` on success
- Redirect to `/` on error

### GET /logout

End user session and log out.

**Response**
- Redirect to landing page
- Clear session data

## Application Endpoints

### GET /app

Main application interface (requires authentication).

**Response**
- HTML application interface with all features

**Status Codes**
- `200 OK` - Application interface loaded
- `302 Found` - Redirect to login if not authenticated

### POST /api/chat

Process chat messages and return AI responses.

**Request Body**
```json
{
  "message": "Hello, how can you help me today?",
  "context": {
    "conversation_id": "optional-conversation-id",
    "user_preferences": {}
  }
}
```

**Response**
```json
{
  "response": "Hello! I'm NOUS, your personal assistant. I can help you with...",
  "conversation_id": "generated-or-existing-id",
  "timestamp": "2025-06-27T12:00:00.000Z"
}
```

**Status Codes**
- `200 OK` - Message processed successfully
- `400 Bad Request` - Invalid request format
- `401 Unauthorized` - Authentication required
- `500 Internal Server Error` - Processing error

## Analytics Endpoints

### GET /api/analytics/dashboard

Get comprehensive analytics dashboard data.

**Response**
```json
{
  "productivity_score": 85.2,
  "total_activities": 1247,
  "engagement_rate": 78.5,
  "goals_progress": 67.3,
  "insights": [
    {
      "type": "productivity",
      "message": "Your morning productivity is 23% higher than afternoon",
      "confidence": 0.92
    }
  ],
  "recent_activity": [...]
}
```

### GET /api/analytics/activity

Get user activity metrics and patterns.

**Parameters**
- `period` (query) - Time period (day, week, month, year)
- `metric` (query) - Specific metric to filter

**Response**
```json
{
  "total_sessions": 156,
  "average_session_duration": 847,
  "peak_activity_hours": [9, 14, 19],
  "feature_usage": {
    "chat": 45.2,
    "analytics": 23.1,
    "search": 18.7,
    "financial": 8.9,
    "health": 4.1
  },
  "weekly_trend": [...]
}
```

### POST /api/analytics/goals

Create or update user goals.

**Request Body**
```json
{
  "title": "Daily Exercise",
  "description": "Exercise for 30 minutes daily",
  "target_type": "daily",
  "target_value": 30,
  "unit": "minutes",
  "category": "health"
}
```

**Response**
```json
{
  "id": 123,
  "title": "Daily Exercise",
  "progress": 0.0,
  "created_at": "2025-06-27T12:00:00.000Z",
  "status": "active"
}
```

### GET /api/analytics/insights

Get AI-generated insights and recommendations.

**Response**
```json
{
  "insights": [
    {
      "category": "productivity",
      "title": "Peak Performance Hours",
      "description": "You're most productive between 9-11 AM",
      "confidence": 0.89,
      "actionable_tips": [
        "Schedule important tasks during morning hours",
        "Take breaks every 90 minutes for sustained focus"
      ]
    }
  ],
  "recommendations": [...]
}
```

## Search Endpoints

### GET /api/search

Perform global search across all content.

**Parameters**
- `q` (query) - Search query string
- `limit` (query) - Maximum results (default: 20)
- `category` (query) - Filter by category

**Response**
```json
{
  "results": [
    {
      "id": "task_123",
      "title": "Buy groceries",
      "category": "tasks",
      "snippet": "Weekly grocery shopping for the family",
      "relevance_score": 0.95,
      "url": "/tasks/123"
    }
  ],
  "total_count": 47,
  "query_time": 0.023,
  "suggestions": ["grocery store", "shopping list"]
}
```

### GET /api/search/suggestions

Get real-time search suggestions.

**Parameters**
- `q` (query) - Partial search query

**Response**
```json
{
  "suggestions": [
    {
      "text": "grocery shopping",
      "category": "tasks",
      "count": 12
    },
    {
      "text": "grocery budget",
      "category": "financial",
      "count": 8
    }
  ]
}
```

## Notification Endpoints

### GET /api/notifications

Get user notifications with pagination.

**Parameters**
- `page` (query) - Page number (default: 1)
- `limit` (query) - Items per page (default: 20)
- `status` (query) - Filter by status (unread, read, all)

**Response**
```json
{
  "notifications": [
    {
      "id": 456,
      "title": "Daily Goal Reminder",
      "message": "You're 70% towards your daily exercise goal!",
      "type": "reminder",
      "priority": "medium",
      "is_read": false,
      "created_at": "2025-06-27T12:00:00.000Z",
      "action_url": "/analytics/goals"
    }
  ],
  "total_count": 23,
  "unread_count": 7
}
```

### POST /api/notifications

Create a new notification.

**Request Body**
```json
{
  "title": "Budget Alert",
  "message": "You've exceeded 80% of your monthly dining budget",
  "type": "alert",
  "priority": "high",
  "action_url": "/financial/budgets"
}
```

### PUT /api/notifications/<id>/read

Mark notification as read.

**Response**
```json
{
  "status": "success",
  "message": "Notification marked as read"
}
```

## Financial Endpoints

### GET /api/financial/accounts

Get user's linked bank accounts.

**Response**
```json
{
  "accounts": [
    {
      "id": 789,
      "name": "Main Checking",
      "account_type": "checking",
      "balance": 2547.83,
      "currency": "USD",
      "last_updated": "2025-06-27T08:00:00.000Z"
    }
  ]
}
```

### GET /api/financial/transactions

Get transaction history with filtering.

**Parameters**
- `account_id` (query) - Filter by account
- `category` (query) - Filter by expense category
- `start_date` (query) - Date range start
- `end_date` (query) - Date range end

**Response**
```json
{
  "transactions": [
    {
      "id": 101112,
      "amount": -45.67,
      "description": "Grocery Store",
      "category": "food",
      "date": "2025-06-26T15:30:00.000Z",
      "account_id": 789
    }
  ],
  "summary": {
    "total_income": 3200.00,
    "total_expenses": 1847.32,
    "net_change": 1352.68
  }
}
```

### GET /api/financial/budgets

Get budget information and progress.

**Response**
```json
{
  "budgets": [
    {
      "id": 555,
      "category": "dining",
      "budget_amount": 400.00,
      "spent_amount": 327.50,
      "remaining": 72.50,
      "percentage_used": 81.9,
      "status": "warning"
    }
  ]
}
```

## Collaboration Endpoints

### GET /api/collaboration/families

Get user's family groups.

**Response**
```json
{
  "families": [
    {
      "id": 777,
      "name": "The Smith Family",
      "role": "admin",
      "member_count": 4,
      "created_at": "2025-01-15T10:00:00.000Z"
    }
  ]
}
```

### POST /api/collaboration/families

Create a new family group.

**Request Body**
```json
{
  "name": "Johnson Family",
  "description": "Our family coordination group"
}
```

### GET /api/collaboration/shared-tasks

Get shared tasks across family groups.

**Response**
```json
{
  "shared_tasks": [
    {
      "id": 888,
      "title": "Weekly house cleaning",
      "assigned_to": "Mom",
      "family_id": 777,
      "status": "pending",
      "due_date": "2025-06-28T18:00:00.000Z"
    }
  ]
}
```

## Onboarding Endpoints

### GET /api/onboarding/status

Get user's onboarding completion status.

**Response**
```json
{
  "completed": false,
  "current_step": 2,
  "total_steps": 3,
  "steps": [
    {
      "id": 1,
      "title": "Welcome Tour",
      "completed": true
    },
    {
      "id": 2,
      "title": "Connect Accounts",
      "completed": false
    },
    {
      "id": 3,
      "title": "Set Goals",
      "completed": false
    }
  ]
}
```

### POST /api/onboarding/complete-step

Mark an onboarding step as completed.

**Request Body**
```json
{
  "step_id": 2
}
```

## Error Responses

All endpoints may return the following error response format:

```json
{
  "error": "Error description",
  "code": "ERROR_CODE",
  "timestamp": "2025-06-27T12:00:00.000Z",
  "details": {
    "field": "specific error details"
  }
}
```

### Common Error Codes

- `400 Bad Request` - Invalid request format or missing parameters
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service temporarily unavailable

## Rate Limiting

API endpoints are rate limited to prevent abuse:
- **Anonymous users**: 100 requests per hour
- **Authenticated users**: 1000 requests per hour
- **Premium users**: 5000 requests per hour

Rate limit headers are included in all responses:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Time when rate limit resets

## Webhooks

NOUS supports webhooks for real-time notifications:

### POST /api/webhooks/register

Register a webhook endpoint.

**Request Body**
```json
{
  "url": "https://your-app.com/webhook",
  "events": ["goal_completed", "budget_exceeded", "task_due"],
  "secret": "webhook_secret_key"
}
```

## SDK and Client Libraries

Currently, no official SDKs are available. The API is designed to be RESTful and can be consumed by any HTTP client.

### Example Usage

```javascript
// Fetch analytics data
const response = await fetch('/api/analytics/dashboard', {
  headers: {
    'Authorization': 'Bearer ' + sessionToken
  }
});
const analytics = await response.json();

// Perform search
const searchResponse = await fetch('/api/search?q=' + encodeURIComponent(query));
const results = await searchResponse.json();
```

## Changelog

- **v2.0.0** - Major feature enhancement with analytics, search, notifications, financial, and collaboration endpoints
- **v1.0.2** - Enhanced error response format and CORS support
- **v1.0.1** - Added detailed system metrics to healthz endpoint
- **v1.0.0** - Initial API release with health, auth, chat, and feedback endpoints