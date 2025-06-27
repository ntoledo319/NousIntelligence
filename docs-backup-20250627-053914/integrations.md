# NOUS Personal Assistant - External Integrations Guide

## Overview

This document provides comprehensive setup instructions, required environment variables, and test procedures for all external service integrations in the NOUS Personal Assistant.

## Google OAuth & API Services

### Setup Instructions

1. **Google Cloud Console Setup**
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create or select your project
   - Enable required APIs:
     - Google+ API
     - Google Calendar API
     - Gmail API
     - Google Drive API
     - YouTube Data API v3

2. **OAuth Credentials**
   - Go to "Credentials" section
   - Create "OAuth 2.0 Client IDs"
   - Select "Web application"
   - Add authorized redirect URIs:
     - `https://your-replit-app.replit.app/auth/google/callback`
     - `https://your-domain.com/auth/google/callback` (if using custom domain)

3. **Download Credentials**
   - Download the credentials as `client_secret.json`
   - Place in project root directory

### Environment Variables

```bash
# Automatically loaded from client_secret.json
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### Test Commands

```bash
# Test Google OAuth integration
python -c "from test_oauth_integration import test_google_oauth_credentials; test_google_oauth_credentials()"

# Test via health API
curl https://your-app.replit.app/api/health/google-oauth
```

### Available Services

- **Google Calendar**: Event management, scheduling
- **Gmail**: Email processing, sending, organizing
- **Google Drive**: File storage and management
- **Google Docs**: Document creation and editing
- **YouTube**: Video analysis and management
- **Google Meet**: Meeting integration and scheduling

## AI Services

### OpenAI API

#### Setup Instructions
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create account and add payment method
3. Generate API key in API section
4. Add to Replit Secrets as `OPENAI_API_KEY`

#### Environment Variables
```bash
OPENAI_API_KEY=sk-your-openai-api-key
```

#### Test Commands
```bash
# Test OpenAI API
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models

# Test via health API
curl https://your-app.replit.app/api/health/ai-services
```

### OpenRouter API

#### Setup Instructions
1. Visit [OpenRouter](https://openrouter.ai/)
2. Create account
3. Generate API key
4. Add to Replit Secrets as `OPENROUTER_API_KEY`

#### Environment Variables
```bash
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key
```

#### Test Commands
```bash
# Test OpenRouter API
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" https://openrouter.ai/api/v1/models

# Test via health API
curl https://your-app.replit.app/api/health/ai-services
```

### Hugging Face API (Optional)

#### Setup Instructions
1. Visit [Hugging Face](https://huggingface.co/)
2. Create account
3. Generate access token in settings
4. Add to Replit Secrets as `HUGGINGFACE_API_KEY`

#### Environment Variables
```bash
HUGGINGFACE_API_KEY=hf_your-huggingface-token
```

#### Test Commands
```bash
# Test Hugging Face API
curl -H "Authorization: Bearer $HUGGINGFACE_API_KEY" https://huggingface.co/api/whoami-v2
```

## Database Configuration

### PostgreSQL (Production)

#### Automatic Setup
- Replit automatically provides `DATABASE_URL` for PostgreSQL
- No manual configuration required

#### Environment Variables
```bash
DATABASE_URL=postgresql://username:password@host:port/database
```

#### Test Commands
```bash
# Test database connectivity
python -c "from test_oauth_integration import test_database_config; test_database_config()"

# Test via health API
curl https://your-app.replit.app/api/health/database
```

## Health Check Endpoints

### Comprehensive Health Check
```bash
GET /api/health/
```

Returns overall system health with status of all services.

### Individual Service Checks
```bash
GET /api/health/google-oauth     # Google OAuth status
GET /api/health/ai-services      # All AI services status
GET /api/health/database         # Database connectivity
```

### Response Format
```json
{
  "overall_status": "healthy|degraded|unhealthy",
  "timestamp": "2025-06-26T09:47:26.100370Z",
  "summary": {
    "total_services": 5,
    "healthy": 4,
    "errors": 1,
    "not_configured": 0
  },
  "services": [
    {
      "service": "Google OAuth",
      "status": "healthy",
      "timestamp": "2025-06-26T09:47:26.100370Z",
      "details": {
        "credentials_configured": true,
        "discovery_endpoint": "accessible"
      }
    }
  ]
}
```

## Security Best Practices

### Environment Variable Management
- Store all secrets in Replit Secrets, never in code
- Use the provided `.env.example` as a template
- Never commit actual credentials to version control

### OAuth Security
- Use HTTPS for all OAuth redirect URIs
- Implement CSRF protection (already configured)
- Validate state parameters in OAuth flows
- Use secure session management

### API Key Security
- Rotate API keys regularly
- Monitor API usage for anomalies
- Implement rate limiting (already configured)
- Log authentication failures

## Troubleshooting

### Common Issues

#### Google OAuth "redirect_uri_mismatch"
- Verify redirect URIs in Google Cloud Console match your application URLs
- Ensure URIs include the full path: `/auth/google/callback`
- Check for HTTP vs HTTPS mismatch

#### OpenAI API 401 Unauthorized
- Verify API key is current and not expired
- Check account has sufficient credits
- Ensure key has proper permissions

#### Database Connection Issues
- Verify `DATABASE_URL` is properly set
- Check database service is running
- Ensure network connectivity

### Debug Commands

```bash
# Check environment variables
python -c "import os; print('GOOGLE_CLIENT_ID:', bool(os.environ.get('GOOGLE_CLIENT_ID')))"

# Run comprehensive health check
python test_oauth_integration.py

# Check logs for errors
tail -f logs/error.log
```

## Integration Examples

### Google Calendar Event Creation
```python
from utils.google_helper import create_calendar_event

event = create_calendar_event(
    title="Meeting with Team",
    start_time="2025-06-26T14:00:00Z",
    end_time="2025-06-26T15:00:00Z",
    description="Weekly team sync"
)
```

### AI Service Request
```python
from utils.ai_service_manager import ai_integration

response = ai_integration.get_chat_response(
    "What's the weather like today?",
    user_id="user123"
)
```

### Gmail Integration
```python
from utils.gmail_helper import send_email

send_email(
    to="user@example.com",
    subject="Hello from NOUS",
    body="This is a test email"
)
```

## Monitoring and Maintenance

### Regular Health Checks
- Monitor `/api/health/` endpoint
- Set up alerts for service degradation
- Review API usage and rate limits

### Key Rotation Schedule
- OpenAI API keys: Every 90 days
- Google OAuth credentials: Annually or when compromised
- Database credentials: As needed

### Performance Monitoring
- Track API response times
- Monitor error rates
- Review resource usage

## Support and Documentation

- **Google APIs**: [Google Developers](https://developers.google.com/)
- **OpenAI**: [OpenAI Documentation](https://platform.openai.com/docs)
- **OpenRouter**: [OpenRouter Documentation](https://openrouter.ai/docs)
- **Hugging Face**: [Hugging Face Documentation](https://huggingface.co/docs)

For additional support, check the project's main documentation or contact the development team.