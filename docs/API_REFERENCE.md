# NOUS Personal Assistant - API Reference

## Overview

The NOUS API provides endpoints for health monitoring, user authentication, chat functionality, and feedback collection. All endpoints return JSON responses and use standard HTTP status codes.

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

Main chat interface (requires authentication).

**Response**
- HTML chat application interface

**Status Codes**
- `200 OK` - Chat interface loaded
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

## Feedback Endpoints

### POST /api/feedback/submit

Submit user feedback for beta testing program.

**Request Body**
```json
{
  "feedback": "The chat interface is very responsive and helpful.",
  "rating": 5,
  "category": "interface",
  "user_email": "user@example.com"
}
```

**Response**
```json
{
  "status": "success",
  "message": "Feedback submitted successfully"
}
```

**Status Codes**
- `200 OK` - Feedback submitted successfully
- `400 Bad Request` - Missing required fields
- `500 Internal Server Error` - Submission error

### GET /api/feedback/status

Get feedback system status.

**Response**
```json
{
  "status": "operational",
  "system": "feedback_api",
  "version": "1.0.0"
}
```

## Error Responses

All endpoints may return the following error response format:

```json
{
  "error": "Error description",
  "code": "ERROR_CODE",
  "timestamp": "2025-06-27T12:00:00.000Z"
}
```

### Common Error Codes

- `400 Bad Request` - Invalid request format or missing parameters
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service temporarily unavailable

## Rate Limiting

Currently no rate limiting is implemented. This may be added in future versions.

## CORS Policy

The API supports cross-origin requests with the following headers:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS`
- `Access-Control-Allow-Headers: Content-Type, Authorization`

## Examples

### Check Application Health

```bash
curl -X GET http://localhost:5000/health
```

### Submit Feedback

```bash
curl -X POST http://localhost:5000/api/feedback/submit \
  -H "Content-Type: application/json" \
  -d '{
    "feedback": "Great application!",
    "rating": 5
  }'
```

### Send Chat Message (requires authentication)

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -H "Cookie: session=your-session-cookie" \
  -d '{
    "message": "What can you help me with?"
  }'
```

## SDK and Client Libraries

Currently, no official SDKs are available. The API is designed to be RESTful and can be consumed by any HTTP client.

## Changelog

- **v1.0.0** - Initial API release with health, auth, chat, and feedback endpoints
- **v1.0.1** - Added detailed system metrics to healthz endpoint
- **v1.0.2** - Enhanced error response format and CORS support