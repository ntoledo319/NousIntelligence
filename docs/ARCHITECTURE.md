# NOUS Architecture Overview

This document provides a comprehensive overview of the NOUS architecture, explaining how different components interact and the design principles behind the system.

## System Architecture

NOUS is built with a multi-layered architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                       Client Layer                           │
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ Web Browser │    │ Mobile View │    │ API Clients │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                         API Layer                            │
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  REST APIs  │    │ OAuth Routes │    │  Webhooks   │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ Controllers │    │  Services   │    │ Utils/Helpers│     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       Data Layer                             │
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ SQLAlchemy  │    │ Cache System │    │ File Storage│     │
│  │ Models/ORM  │    │              │    │             │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Infrastructure Layer                     │
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ PostgreSQL  │    │    Redis    │    │External APIs│     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Web Application (Flask)

The web application is built using Flask and provides both an HTML interface and RESTful APIs. Key components include:

- **Routes**: Defined in `app.py` and `routes/` directory
- **Templates**: Jinja2 templates in `templates/` directory
- **Static Assets**: CSS, JavaScript, and images in `static/` directory

### 2. Database Models (SQLAlchemy)

The application uses SQLAlchemy ORM for database interactions. Models are defined in `models.py` and include:

- **User**: Authentication and user profile information
- **UserSettings**: User preferences and settings
- **Knowledge Base**: Storage for learned information with embeddings
- **Various Domain Models**: Doctor, Appointment, ShoppingList, etc.

### 3. Utility Services

Utility modules in the `utils/` directory provide various services:

- **cache_helper.py**: Multi-tier caching (Redis, DB, File)
- **security_helper.py**: Authentication, CSRF protection, rate limiting
- **knowledge_helper.py**: Semantic search and knowledge base management
- **ai_helper.py**: AI service integrations
- **Various Helper Modules**: Domain-specific helper functions

### 4. External Integrations

NOUS integrates with several external services:

- **OAuth Providers**: Google, Spotify
- **AI Services**: OpenRouter, Hugging Face
- **Third-party APIs**: Weather, maps, etc.

## Key Design Patterns

### Multi-Tier Caching

The application implements a sophisticated caching system with multiple layers:

1. **In-Memory Cache**: First level, LRU-based cache for fastest access
2. **Redis Cache**: Second level, for distributed caching in production
3. **Database Cache**: Third level, for persistence across application restarts
4. **File Cache**: Fallback when other options are unavailable

### Fallback Chain for AI Services

To optimize costs and reliability, AI services are called in a fallback chain:

1. Try local cached responses first
2. Then try Hugging Face free models
3. Fall back to OpenRouter/OpenAI for complex tasks

### Security Architecture

Security is implemented through multiple layers:

1. **Authentication**: OAuth2 with JWT or session-based authentication
2. **Authorization**: Role-based access control
3. **Protection**: CSRF tokens, input validation, rate limiting
4. **Secure Storage**: Hashed secrets, encrypted sensitive data

## Data Flow

### 1. User Request Flow

When a user makes a request, it flows through these components:

1. **Flask Routes**: Handle incoming HTTP requests
2. **Authentication**: Verify user identity
3. **Request Processing**: Parse and validate inputs
4. **Service Logic**: Execute business logic
5. **Data Access**: Retrieve or store data using SQLAlchemy
6. **Response Generation**: Format and return response

### 2. AI Conversation Flow

For AI-powered conversations:

1. User sends a message
2. System retrieves relevant context from knowledge base
3. Context and user message are sent to AI service
4. Response is processed and enhanced
5. Response is returned to user and stored in conversation history

## Monitoring and Maintenance

The system includes components for monitoring and maintenance:

- **Health Checks**: Endpoint for system status verification
- **Logging**: Structured logging for debugging and auditing
- **Maintenance Tasks**: Scheduled tasks for database cleanup, etc.

## Future Architecture Plans

As the system evolves, several architectural improvements are planned:

1. **Microservices**: Split monolithic app into domain-specific services
2. **Event-Driven Architecture**: Implement message queues for asynchronous processing
3. **Edge Caching**: Distribute cache closer to users for better performance
4. **Containerization**: Package components as Docker containers for easier deployment

## Technology Stack

- **Backend**: Python 3.9+, Flask
- **Database**: PostgreSQL 13+
- **Caching**: Redis, SQLAlchemy, File-based
- **Authentication**: OAuth2 (Google, Spotify)
- **AI Services**: OpenRouter, Hugging Face
- **Frontend**: HTML, CSS, JavaScript
- **Infrastructure**: Replit hosting 