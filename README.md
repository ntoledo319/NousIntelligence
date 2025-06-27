# NOUS Personal Assistant

A modern Flask-based AI personal assistant with Google OAuth authentication, responsive design, and comprehensive utility modules.

## Features

### Core Application
- **Professional Chat Interface** - Clean, responsive chat UI with 6 theme options
- **Google OAuth Authentication** - Secure authentication using Google accounts
- **Health Monitoring** - System health endpoints with CPU and memory metrics
- **Progressive Web App** - Mobile-first responsive design with offline support

### Utilities & Integrations
- **Weather Services** - Weather data integration and forecasting
- **Spotify Integration** - Music platform connectivity and mood analysis
- **Travel Management** - Trip planning and itinerary management
- **Shopping Lists** - Smart shopping list management with automation
- **Health Tracking** - Medication reminders and appointment management
- **Financial Tools** - Budget tracking and price monitoring
- **Voice Interface** - Speech recognition and synthesis capabilities
- **Smart Home** - IoT device integration framework
- **Maps & Navigation** - Location services and mapping integration
- **Email Notifications** - Email-based alerts and notifications
- **In-App Notifications** - Web dashboard notifications and alerts

### Communication Limitations
- **SMS/Text Messaging** - Not currently supported (use email or in-app notifications instead)
- **Push Notifications** - Not currently supported
- **Phone Calls** - Not currently supported

## Quick Start

1. **Install Dependencies**
   ```bash
   # Dependencies are managed automatically by Replit
   ```

2. **Environment Setup**
   ```bash
   # Required environment variables:
   # DATABASE_URL - PostgreSQL connection string
   # GOOGLE_CLIENT_ID - Google OAuth client ID  
   # GOOGLE_CLIENT_SECRET - Google OAuth client secret
   ```

3. **Run Application**
   ```bash
   python main.py
   ```

4. **Access Application**
   - Landing page: `http://localhost:5000/`
   - Health check: `http://localhost:5000/health`
   - Chat interface: `http://localhost:5000/app` (requires login)

## Architecture

- **Backend**: Flask with SQLAlchemy ORM
- **Frontend**: Vanilla JavaScript with CSS Grid/Flexbox
- **Database**: PostgreSQL (production) / SQLite (development)
- **Authentication**: Google OAuth 2.0
- **Deployment**: Replit Cloud with public access

## API Endpoints

### Health & Status
- `GET /health` - Basic health check
- `GET /healthz` - Detailed system metrics
- `GET /api/feedback/status` - Feedback system status

### Authentication
- `GET /` - Landing page
- `GET /login` - Initiate Google OAuth
- `GET /logout` - End user session
- `GET /oauth/callback` - OAuth callback handler

### Application
- `GET /app` - Main chat interface (authenticated)
- `POST /api/chat` - Chat message processing
- `POST /api/feedback/submit` - Submit user feedback

## Development

### Project Structure
```
/
├── app.py              # Main Flask application
├── main.py             # Application entry point
├── config/             # Configuration modules
├── models/             # Database models
├── routes/             # Route handlers
├── utils/              # 64 utility modules
├── templates/          # Jinja2 templates
├── static/             # CSS, JavaScript, assets
└── docs/               # Documentation
```

### Database Models
- `User` - User accounts and authentication
- `BetaUser` - Beta testing program participants
- Additional models for various features

### Testing
```bash
# Run test suite
python -m pytest tests/

# Health check test
curl http://localhost:5000/health
```

## Deployment

The application is configured for deployment on Replit Cloud:

1. Push code to repository
2. Configure environment variables
3. Deploy via Replit interface
4. Application runs on port 5000 with public access

## Security

- Google OAuth for secure authentication
- CORS headers for API access
- Session management with secure cookies
- ProxyFix middleware for deployment
- Input validation and sanitization

## Cost Analysis

**Monthly Operational Costs: ~$0.49**
- OpenRouter API (Gemini Pro): ~$0.30/month
- HuggingFace Inference: Free tier
- Database hosting: Included with Replit

**99.87% cost savings** compared to commercial alternatives while maintaining full functionality.

## Support

For issues, questions, or feature requests:
- Check the health endpoints for system status
- Review logs in the `/logs` directory
- Use the feedback API to report issues

## License

[Add your license information here]