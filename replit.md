# NOUS Personal Assistant - Replit.md

## Overview

NOUS Personal Assistant is a Flask-based web application designed to provide intelligent, adaptive, and user-friendly AI interactions. The application is built with a focus on public accessibility while maintaining secure authentication features for protected routes. It serves as a comprehensive personal assistant platform with various integrated services and capabilities.

## System Architecture

### Frontend Architecture
- **Framework**: Flask with Jinja2 templating
- **Static Assets**: CSS, JavaScript, and images served from `/static` directory
- **Templates**: HTML templates in `/templates` directory with a base layout system
- **Responsive Design**: Mobile-first approach with system font stack

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLAlchemy ORM with support for SQLite (development) and PostgreSQL (production)
- **Authentication**: Flask-Login with Google OAuth integration
- **Session Management**: Flask-Session with filesystem storage
- **WSGI Server**: Gunicorn for production deployment

### Deployment Strategy
- **Primary Target**: Replit Cloud Run deployment
- **Public Access**: Configured to bypass Replit authentication while maintaining internal app security
- **Environment**: Production-ready with comprehensive logging and monitoring

## Key Components

### 1. Application Factory Pattern
- **Main Entry Points**: Multiple deployment configurations (`app.py`, `deployment.py`, `main.py`)
- **Configuration**: Environment-based configuration with secure defaults
- **Modular Design**: Separates concerns between routing, models, and utilities

### 2. Database Layer
- **ORM**: SQLAlchemy with declarative base
- **Models**: User authentication and application-specific models
- **Migrations**: Automated table creation with `AUTO_CREATE_TABLES` flag
- **Connection Management**: Pool management with connection recycling

### 3. Authentication & Authorization
- **User Management**: Registration, login, profile management
- **OAuth Integration**: Google OAuth for social login
- **Session Security**: Secure cookie configuration with proper lifetime management
- **Two-Factor Authentication**: Optional 2FA support for enhanced security

### 4. API & Route Structure
- **Blueprints**: Modular route organization (implied from multiple deployment files)
- **RESTful Design**: Standard HTTP methods for resource management
- **Error Handling**: Comprehensive error pages and logging
- **Health Monitoring**: Dedicated health check endpoints

### 5. Security Features
- **CSRF Protection**: Flask-WTF integration
- **Secure Headers**: CORS and frame options configuration
- **Rate Limiting**: Request throttling capabilities
- **Input Validation**: Form validation and sanitization

## Data Flow

### 1. Request Processing
```
User Request → Flask Router → Authentication Check → Route Handler → Template Rendering → Response
```

### 2. Authentication Flow
```
Login Request → Credential Validation → Session Creation → User Context → Protected Resource Access
```

### 3. Database Operations
```
Route Handler → SQLAlchemy Model → Database Query → Result Processing → Response Data
```

## External Dependencies

### Core Dependencies
- **Flask**: Web framework and core functionality
- **SQLAlchemy**: Database ORM and connection management
- **Gunicorn**: WSGI server for production deployment
- **Werkzeug**: WSGI utilities and security helpers

### Authentication Dependencies
- **Flask-Login**: User session management
- **Flask-WTF**: Form handling and CSRF protection
- **Google OAuth**: Social authentication integration

### Production Dependencies
- **psutil**: System monitoring and process management
- **python-dotenv**: Environment variable management
- **requests**: HTTP client for external API calls

### Database Support
- **SQLite**: Development database (file-based)
- **PostgreSQL**: Production database (via DATABASE_URL)

## Deployment Strategy

### 1. Environment Configuration
- **Development**: Local SQLite database with debug mode
- **Production**: PostgreSQL database with optimized settings
- **Replit**: Cloud-based deployment with public access configuration

### 2. Public Access Configuration
- **Authentication Bypass**: Configured to disable Replit login requirements
- **CORS Headers**: Set to allow public access from any origin
- **Security Balance**: Maintains internal application security while enabling public access

### 3. Monitoring & Health Checks
- **Health Endpoints**: Multiple health check routes for monitoring
- **Logging**: Comprehensive logging with file and console output
- **Process Management**: Automatic restart capabilities and process monitoring

### 4. Deployment Scripts
- **Multiple Deployment Options**: Various scripts for different deployment scenarios
- **Automated Setup**: Directory creation and environment preparation
- **Process Management**: Cleanup and restart functionality

### 5. Static File Handling
- **Asset Organization**: Structured static file directory
- **Template System**: Hierarchical template inheritance
- **Resource Optimization**: Efficient serving of static assets

## Changelog
- June 26, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.