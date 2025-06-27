# NOUS Personal Assistant - Architecture

## System Overview

NOUS is a Flask-based personal assistant application designed for deployment on Replit Cloud. The architecture emphasizes simplicity, maintainability, and cost-effectiveness while providing comprehensive personal management capabilities.

## Application Architecture

### Core Components

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Frontend Layer    │    │   Backend Layer     │    │   Data Layer        │
│                     │    │                     │    │                     │
│ • Landing Page      │◄──►│ • Flask App         │◄──►│ • PostgreSQL        │
│ • Chat Interface    │    │ • Route Handlers    │    │ • SQLAlchemy ORM    │
│ • 6 Theme System    │    │ • Authentication    │    │ • User Models       │
│ • PWA Features      │    │ • Health Monitoring │    │ • Session Storage   │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

### Request Flow

```
User Request → ProxyFix → Flask Router → Authentication Check → Route Handler → Response
     ↓              ↓           ↓              ↓                ↓              ↓
Browser → Replit Cloud → app.py → Google OAuth → routes/ → templates/
```

## Frontend Architecture

### Templates Structure
- **Base Template**: Shared layout with theme support
- **Landing Page**: `templates/landing.html` - Public access with Google OAuth
- **Chat Interface**: `templates/app.html` - Authenticated chat application
- **Admin Interface**: Beta management console (restricted access)

### Static Assets
- **CSS**: `static/styles.css` - 6 themes with mobile-first responsive design
- **JavaScript**: `static/app.js` - Chat functionality and PWA features  
- **PWA**: `static/manifest.json`, `static/sw.js` - Progressive Web App support

### UI Architecture
- **Design System**: CSS custom properties for theme variables
- **Responsive Design**: CSS Grid and Flexbox with 5 breakpoints (320px-1920px+)
- **Performance**: Service worker caching, lazy loading, optimized assets

## Backend Architecture

### Flask Application (`app.py`)
- **Application Factory**: `create_app()` function for configuration
- **Middleware**: ProxyFix for Replit deployment
- **Security**: CORS headers, session management, input validation
- **Health Monitoring**: System metrics and uptime tracking

### Route Organization
```
routes/
├── api/                 # API endpoints
│   └── feedback.py      # User feedback collection
├── auth/                # Authentication handlers
├── dashboard.py         # Main application routes
├── index.py            # Landing page
└── user_routes.py      # User management
```

### Utility Modules (64 modules)
```
utils/
├── Core Services/
│   ├── health_monitor.py      # System health tracking
│   ├── database_optimizer.py  # DB performance monitoring
│   └── security_helper.py     # Security utilities
├── Integrations/
│   ├── weather_helper.py      # Weather API integration
│   ├── spotify_helper.py      # Spotify API integration
│   ├── maps_helper.py         # Location services
│   └── smart_home_helper.py   # IoT device integration
└── Features/
    ├── travel_helper.py       # Travel management
    ├── shopping_helper.py     # Shopping lists
    ├── medication_helper.py   # Health tracking
    └── voice_interaction.py   # Speech processing
```

## Data Architecture

### Database Models
```python
models/
├── user.py           # User accounts and authentication
├── beta_models.py    # Beta testing program
└── database.py       # Database configuration
```

### Database Configuration
- **Development**: SQLite for local development
- **Production**: PostgreSQL with connection pooling
- **ORM**: SQLAlchemy with declarative base
- **Migrations**: Automatic table creation

### Session Management
- **Storage**: Server-side session storage
- **Security**: Secure cookies with SameSite protection
- **Lifetime**: 24-hour session timeout

## Authentication & Security

### Google OAuth Integration
```
User → Google OAuth → Callback → Session Creation → Access Control
```

- **Provider**: Google OAuth 2.0
- **Credentials**: Environment variables (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
- **Scopes**: Basic profile information
- **Security**: State parameter validation, CSRF protection

### Security Measures
- **HTTPS Enforcement**: Secure cookie settings
- **CORS Policy**: Configured for public API access
- **Input Validation**: Request sanitization and validation
- **Session Security**: HttpOnly cookies, secure flags

## API Architecture

### Health Endpoints
- `GET /health` - Basic application health
- `GET /healthz` - Detailed system metrics (CPU, memory, uptime)

### Authentication Endpoints  
- `GET /login` - Initiate Google OAuth flow
- `GET /oauth/callback` - OAuth callback handler
- `GET /logout` - Session termination

### Application Endpoints
- `POST /api/chat` - Chat message processing
- `POST /api/feedback/submit` - User feedback collection
- `GET /api/feedback/status` - Feedback system status

## Deployment Architecture

### Replit Cloud Configuration
```yaml
# replit.toml
[deployment]
run = "python main.py"
port = 5000
publicAccess = true

[env]
DATABASE_URL = "postgresql://..."
GOOGLE_CLIENT_ID = "..."
GOOGLE_CLIENT_SECRET = "..."
```

### Environment Configuration
- **Host**: 0.0.0.0 (public access)
- **Port**: 5000 (Replit standard)
- **Debug**: False (production)
- **Database**: PostgreSQL connection string

### Performance Optimizations
- **Connection Pooling**: SQLAlchemy pool configuration
- **Static Assets**: Efficient serving with caching headers
- **Health Monitoring**: Real-time system metrics
- **Error Handling**: Comprehensive logging and error pages

## Development Architecture

### Code Organization
- **Single Entry Point**: `main.py` → `app.py`
- **Configuration**: Centralized in `config/` directory
- **Testing**: Test suite in `tests/` directory
- **Documentation**: Consolidated in `docs/` directory

### Development Workflow
1. Local development with SQLite
2. Feature development in utility modules
3. Integration testing with health endpoints
4. Deployment to Replit Cloud

## Monitoring & Maintenance

### Health Monitoring
- **System Metrics**: CPU, memory, disk usage
- **Application Metrics**: Uptime, response times
- **Database Health**: Connection status, query performance

### Logging
- **Application Logs**: `logs/app.log`
- **Access Logs**: `logs/access.log`  
- **Error Logs**: `logs/error.log`
- **Health Logs**: `logs/health_check.log`

### Performance Monitoring
- **Database Optimization**: Query performance tracking
- **Response Times**: Endpoint performance metrics
- **Resource Usage**: System resource monitoring

This architecture provides a robust, scalable foundation for the NOUS Personal Assistant while maintaining simplicity and cost-effectiveness.