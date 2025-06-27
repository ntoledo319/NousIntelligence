System Overview
===============

NOUS Personal Assistant is a comprehensive Flask-based web application that serves as an intelligent personal assistant platform. Built with enterprise-grade architecture and modern development practices, it provides a robust foundation for AI-powered interactions while maintaining strict security and performance standards.

Project Vision
--------------

NOUS aims to democratize access to AI-powered personal assistance by providing:

* **Public Accessibility**: No authentication barriers for basic functionality
* **Cost-Effective AI Integration**: 99.85% cost reduction through strategic provider selection
* **Enterprise-Grade Reliability**: Professional monitoring, error handling, and graceful degradation
* **Developer-Friendly Architecture**: Clean codebase with comprehensive documentation

Core Architecture Principles
----------------------------

1. **Single Responsibility**: Each component has a clearly defined purpose
2. **Fail-Safe Design**: Graceful degradation and comprehensive error handling
3. **Cost Optimization**: Strategic use of free and low-cost AI providers
4. **Security First**: OAuth integration with proper session management
5. **Documentation Driven**: Self-documenting code with automated API reference

Technology Stack
----------------

Backend Framework
~~~~~~~~~~~~~~~~~
* **Flask 3.0.0**: Modern Python web framework
* **SQLAlchemy 3.1.1**: Database ORM with PostgreSQL support
* **Gunicorn 21.2.0**: Production WSGI server
* **Werkzeug 3.0.1**: WSGI utilities and security

Authentication & Security
~~~~~~~~~~~~~~~~~~~~~~~~~
* **Google OAuth**: Social authentication integration
* **Flask-Login**: Session management
* **Flask-WTF**: CSRF protection and form handling
* **ProxyFix Middleware**: Secure proxy configuration for Replit

AI Integration
~~~~~~~~~~~~~~
* **OpenRouter API**: Cost-effective access to multiple AI models
* **HuggingFace Inference API**: Free tier for specialized tasks
* **Unified Provider Interface**: Abstracted AI service management

Development & Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~
* **Sphinx**: Professional documentation generation
* **Flask-Smorest**: OpenAPI/Swagger integration
* **Bandit**: Security analysis
* **Flake8**: Code quality enforcement

System Architecture
-------------------

Application Structure
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    NOUS/
    ├── app.py                 # Main Flask application
    ├── main.py               # Entry point launcher
    ├── models/               # Database models
    ├── routes/               # Route handlers
    ├── utils/                # Utility functions
    ├── api/                  # API endpoints
    ├── templates/            # Jinja2 templates
    ├── static/               # CSS, JS, images
    ├── docs/                 # Sphinx documentation
    └── tests/                # Test suites

Request Flow
~~~~~~~~~~~~

1. **Entry Point**: ``main.py`` imports and launches ``app.py``
2. **Middleware**: ProxyFix handles proxy headers for Replit
3. **Authentication**: Optional Google OAuth for protected routes
4. **Route Handling**: Modular blueprint-based routing
5. **Database Access**: SQLAlchemy ORM with connection pooling
6. **Response**: Jinja2 templating or JSON API responses

Data Flow Architecture
----------------------

Authentication Flow
~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    User Request → ProxyFix → Flask Router → Auth Check → Protected Resource
                                          ↓
                             Public Resource (bypass auth)

Database Operations
~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    Route Handler → SQLAlchemy Model → Connection Pool → PostgreSQL
                                   ↓
                            Result Processing → JSON/Template Response

AI Integration Flow
~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    User Input → Intent Classification → Provider Selection → API Call
                                      ↓
               Response Processing → Context Management → User Output

Deployment Architecture
-----------------------

Replit Cloud Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Public Access**: Bypasses Replit authentication requirements
* **Port Configuration**: Unified port 5000 for all services
* **Environment Variables**: Secure configuration management
* **Health Monitoring**: ``/healthz`` endpoints for uptime monitoring

Database Strategy
~~~~~~~~~~~~~~~~~

* **Development**: SQLite for local testing
* **Production**: PostgreSQL via ``DATABASE_URL``
* **Connection Management**: Pool recycling and pre-ping validation
* **Migration Strategy**: Automated table creation with ``AUTO_CREATE_TABLES``

Security Considerations
-----------------------

Authentication Security
~~~~~~~~~~~~~~~~~~~~~~~

* **OAuth 2.0**: Google-based authentication with proper token handling
* **Session Management**: Secure cookie configuration with lifetime limits
* **CSRF Protection**: Flask-WTF integration for form security

Application Security
~~~~~~~~~~~~~~~~~~~~

* **Proxy Configuration**: ProxyFix middleware for secure header handling
* **CORS Headers**: Controlled cross-origin resource sharing
* **Input Validation**: Comprehensive form validation and sanitization
* **Error Handling**: Secure error pages without information disclosure

Performance Optimizations
--------------------------

Database Performance
~~~~~~~~~~~~~~~~~~~~

* **Connection Pooling**: Optimized pool size and overflow handling
* **Query Optimization**: SQLAlchemy query analysis and indexing
* **Connection Recycling**: Automatic connection refresh for reliability

Frontend Performance
~~~~~~~~~~~~~~~~~~~~

* **Progressive Web App**: Service worker caching and offline support
* **Responsive Design**: Mobile-first CSS with system font stack
* **Asset Optimization**: Minified CSS/JS and optimized image formats

Cost Optimization Strategy
--------------------------

AI Provider Selection
~~~~~~~~~~~~~~~~~~~~~

* **OpenRouter**: Primary provider for chat completions (Google Gemini Pro)
* **HuggingFace**: Free tier for specialized tasks (TTS, STT, image processing)
* **Provider Abstraction**: Unified interface allowing easy provider switching

Resource Management
~~~~~~~~~~~~~~~~~~~

* **Database Optimization**: Efficient queries and connection management
* **Static Asset Serving**: Optimized file serving with appropriate caching
* **Memory Management**: Proper session cleanup and garbage collection

Monitoring & Health Checks
---------------------------

System Health Monitoring
~~~~~~~~~~~~~~~~~~~~~~~~~

* **Health Endpoints**: ``/healthz`` and ``/api/v1/health`` for monitoring
* **Database Health**: Connection status and query performance tracking
* **Service Dependencies**: External API status monitoring

Error Tracking
~~~~~~~~~~~~~~

* **Comprehensive Logging**: Structured logging with appropriate levels
* **Error Pages**: User-friendly error handling with developer information
* **Exception Handling**: Graceful degradation for service failures

Beta Testing Infrastructure
---------------------------

Feature Flag System
~~~~~~~~~~~~~~~~~~~

* **Database-Driven Flags**: PostgreSQL-backed feature toggles
* **User Segmentation**: Targeted feature rollouts by user attributes
* **Admin Controls**: Web-based management console for flag configuration

Feedback Collection
~~~~~~~~~~~~~~~~~~~

* **Feedback API**: RESTful endpoints for user feedback collection
* **Analytics Dashboard**: Admin console for feedback analysis
* **CSV Export**: Data export functionality for analysis tools

Future Architecture Considerations
----------------------------------

Scalability Planning
~~~~~~~~~~~~~~~~~~~~

* **Microservice Migration**: Potential service decomposition strategy
* **Caching Layer**: Redis integration for session and data caching
* **Load Balancing**: Multi-instance deployment considerations

Integration Expansion
~~~~~~~~~~~~~~~~~~~~~

* **External APIs**: Framework for additional service integrations
* **Plugin Architecture**: Extensible system for feature modules
* **Webhook Support**: Event-driven architecture capabilities

This overview provides the foundation for understanding NOUS's architecture, design decisions, and implementation strategy. Each component is designed with production deployment in mind while maintaining development simplicity and cost effectiveness.