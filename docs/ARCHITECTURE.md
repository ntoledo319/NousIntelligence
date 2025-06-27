
---
**MIGRATION NOTICE**: This file contains legacy information and may be outdated.

**Current Documentation**: 
- Complete documentation: `make docs && make serve-docs`
- API documentation: `/api/docs/` (when app is running)
- Architecture guide: `docs/architecture.rst`

**Last Updated**: June 27, 2025
---

# NOUS Architecture Documentation

*Generated: 2025-06-26 21:23:30*

## System Overview

NOUS Personal Assistant follows a modular, chat-first architecture designed for scalability and maintainability.

## Core Architecture Principles

### 1. Chat-First Design
- All functionality accessible through unified chat interface
- Intent-based message routing with auto-discovery
- Handler functions auto-registered from codebase analysis

### 2. Auto-Discovery System
- Automatic detection of handler functions using AST analysis
- Pattern-based intent matching (`cmd_*`, `handle_*`, etc.)
- Dynamic function loading and registration

### 3. Modular Blueprint Architecture
- Feature-based blueprints for logical separation
- Consistent route naming and error handling
- Pluggable component system

## System Statistics

- **Total Files**: 324
- **Python Modules**: 200
- **API Routes**: 398
- **Database Models**: 42
- **Chat Handlers**: 36

## Component Analysis

### Route Distribution (398 total routes)

Routes are distributed across 56 files:
- `api_documentation.py`: 2 routes
- `cleanup/app.py`: 93 routes
- `app.py`: 6 routes
- `app.py`: 9 routes
- `routes/aa_content.py`: 11 routes
- `routes/aa_routes.py`: 1 routes
- `routes/admin_routes.py`: 2 routes
- `routes/amazon_routes.py`: 7 routes
- `routes/api.py`: 12 routes
- `routes/api/shopping.py`: 10 routes
- `routes/api/v1/settings.py`: 3 routes
- `routes/api/v1/weather.py`: 7 routes
- `routes/api_key_routes.py`: 8 routes
- `routes/api_routes.py`: 3 routes
- `routes/async_api.py`: 4 routes
- `routes/auth/standardized_routes.py`: 5 routes
- `routes/auth_api.py`: 4 routes
- `routes/beta_routes.py`: 6 routes
- `routes/chat_routes.py`: 5 routes
- `routes/crisis_routes.py`: 9 routes
- `routes/dashboard.py`: 1 routes
- `routes/dbt_routes.py`: 24 routes
- `routes/forms_routes.py`: 12 routes
- `routes/health_api.py`: 4 routes
- `routes/health_check.py`: 4 routes
- `routes/image_routes.py`: 2 routes
- `routes/index.py`: 3 routes
- `routes/language_learning_routes.py`: 12 routes
- `routes/main.py`: 6 routes
- `routes/meet_routes.py`: 16 routes
- `routes/memory_dashboard_routes.py`: 1 routes
- `routes/memory_routes.py`: 7 routes
- `routes/price_routes.py`: 3 routes
- `routes/pulse.py`: 4 routes
- `routes/settings.py`: 6 routes
- `routes/setup_routes.py`: 12 routes
- `routes/smart_shopping_routes.py`: 3 routes
- `routes/spotify_commands.py`: 3 routes
- `routes/spotify_routes.py`: 3 routes
- `routes/spotify_visualization.py`: 9 routes
- `routes/two_factor_routes.py`: 7 routes
- `routes/user_routes.py`: 3 routes
- `routes/view/auth.py`: 4 routes
- `routes/view/dashboard.py`: 2 routes
- `routes/view/index.py`: 3 routes
- `routes/view/settings.py`: 3 routes
- `routes/view/user.py`: 4 routes
- `routes/voice_emotion_routes.py`: 2 routes
- `routes/voice_mindfulness_routes.py`: 5 routes
- `routes/voice_routes.py`: 7 routes
- `app.py`: 6 routes
- `tests/test_api_key_manager.py`: 2 routes
- `tests/test_jwt_auth.py`: 2 routes
- `tests/test_schema_validation.py`: 2 routes
- `tests/test_security_headers.py`: 2 routes
- `utils/db_optimizations.py`: 2 routes

### Data Models (42 total models)

- **AAAchievement** (`models/health_models.py`)
- **AABigBook** (`models/aa_content_models.py`)
- **AABigBookAudio** (`models/aa_content_models.py`)
- **AADailyReflection** (`models/aa_content_models.py`)
- **AAFavorite** (`models/aa_content_models.py`)
- **AASpeakerRecording** (`models/aa_content_models.py`)
- **AIModelConfig** (`models/ai_models.py`)
- **AIServiceConfig** (`models/ai_models.py`)
- **AccountLockout** (`models/security_models.py`)
- **AuthToken** (`models/security_models.py`)
- **BetaTester** (`models/user_models.py`)
- **ConversationPrompt** (`models/language_learning_models.py`)
- **ConversationTemplate** (`models/language_learning_models.py`)
- **DBTCrisisResource** (`models/health_models.py`)
- **DBTDiaryCard** (`models/health_models.py`)
- **DBTEmotionTrack** (`models/health_models.py`)
- **DBTSkillCategory** (`models/health_models.py`)
- **DBTSkillChallenge** (`models/health_models.py`)
- **DBTSkillLog** (`models/health_models.py`)
- **DBTSkillRecommendation** (`models/health_models.py`)
- **Deal** (`models/deal_models.py`)
- **LanguageProfile** (`models/language_learning_models.py`)
- **LearningSession** (`models/language_learning_models.py`)
- **LoginAttempt** (`models/security_models.py`)
- **Product** (`models/deal_models.py`)
- **SecurityAuditLog** (`models/security_models.py`)
- **SystemSettings** (`models/system_models.py`)
- **Task** (`models/task_models.py`)
- **TrustedDevice** (`models/security_models.py`)
- **TwoFactorAuth** (`models/security_models.py`)
- **TwoFactorBackupCode** (`models/security_models.py`)
- **User** (`models.py`)
- **User** (`models/user_models.py`)
- **User** (`models/user.py`)
- **UserAIPreferences** (`models/ai_models.py`)
- **UserAIUsage** (`models/ai_models.py`)
- **UserEntityMemory** (`models/memory_models.py`)
- **UserMemoryEntry** (`models/memory_models.py`)
- **UserSettings** (`models.py`)
- **UserSettings** (`models/user_models.py`)
- **UserTopicInterest** (`models/memory_models.py`)
- **VocabularyItem** (`models/language_learning_models.py`)

## Technology Stack

### Backend
- **Flask**: Web framework with blueprint architecture
- **SQLAlchemy**: Database ORM with migration support
- **Gunicorn**: WSGI server for production deployment

### Frontend
- **Jinja2**: Template engine for server-side rendering
- **Bootstrap**: CSS framework for responsive design
- **Vanilla JavaScript**: Client-side interactivity

### AI Integration
- **OpenRouter**: Cost-optimized AI provider interface
- **HuggingFace**: Free-tier audio and text processing
- **Custom AI Pipeline**: Unified provider abstraction

### Database
- **PostgreSQL**: Production database with connection pooling
- **SQLite**: Development database for local testing

## Security Architecture

### Authentication
- Flask-Login session management
- Google OAuth integration
- Session-based authentication with secure cookies

### API Security
- Rate limiting middleware
- Input validation and sanitization
- CORS configuration for public access

### Data Protection
- Environment-based secret management
- Database connection encryption
- Secure session storage

## Deployment Architecture

### Replit Cloud
- Optimized for Replit Cloud Run deployment
- Public access configuration
- Automatic health monitoring

### Scalability
- Stateless application design
- Database connection pooling
- Efficient caching strategies
