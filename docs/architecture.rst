System Architecture
==================

This document provides an in-depth analysis of NOUS Personal Assistant's system architecture, design patterns, and implementation strategies.

Architectural Overview
----------------------

NOUS follows a layered monolithic architecture optimized for simplicity, maintainability, and cost-effectiveness while providing enterprise-grade features.

.. code-block:: text

    ┌─────────────────────────────────────────────────────────┐
    │                    Presentation Layer                    │
    │  ┌─────────────────┐  ┌─────────────────┐ ┌──────────┐  │
    │  │   Landing Page  │  │   Chat Interface │ │ Admin UI │  │
    │  │  (Public Access)│  │ (Authenticated) │ │(Admin)   │  │
    │  └─────────────────┘  └─────────────────┘ └──────────┘  │
    └─────────────────────────────────────────────────────────┘
                                    │
    ┌─────────────────────────────────────────────────────────┐
    │                   Application Layer                     │
    │  ┌─────────────────┐  ┌─────────────────┐ ┌──────────┐  │
    │  │  Flask Router   │  │ Authentication  │ │Middleware│  │
    │  │   (Routes)      │  │   (OAuth)       │ │(ProxyFix)│  │
    │  └─────────────────┘  └─────────────────┘ └──────────┘  │
    └─────────────────────────────────────────────────────────┘
                                    │
    ┌─────────────────────────────────────────────────────────┐
    │                    Business Layer                       │
    │  ┌─────────────────┐  ┌─────────────────┐ ┌──────────┐  │
    │  │  Chat Handler   │  │  Health Monitor │ │Beta Mgmt │  │
    │  │  (AI Integration│  │ (System Status) │ │(Features)│  │
    │  └─────────────────┘  └─────────────────┘ └──────────┘  │
    └─────────────────────────────────────────────────────────┘
                                    │
    ┌─────────────────────────────────────────────────────────┐
    │                     Data Layer                          │
    │  ┌─────────────────┐  ┌─────────────────┐ ┌──────────┐  │
    │  │   SQLAlchemy    │  │   File Storage  │ │  Cache   │  │
    │  │  (PostgreSQL)   │  │   (Sessions)    │ │(Memory)  │  │
    │  └─────────────────┘  └─────────────────┘ └──────────┘  │
    └─────────────────────────────────────────────────────────┘
                                    │
    ┌─────────────────────────────────────────────────────────┐
    │                  External Services                      │
    │  ┌─────────────────┐  ┌─────────────────┐ ┌──────────┐  │
    │  │   OpenRouter    │  │  HuggingFace    │ │Google    │  │
    │  │   (AI Models)   │  │  (Free AI)      │ │(OAuth)   │  │
    │  └─────────────────┘  └─────────────────┘ └──────────┘  │
    └─────────────────────────────────────────────────────────┘

Core Design Principles
----------------------

Single Responsibility Principle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each component has a clearly defined purpose:

* **main.py**: Application entry point and launcher
* **app.py**: Flask application configuration and initialization
* **models/**: Database schema and ORM models
* **routes/**: HTTP request handlers and routing logic
* **utils/**: Utility functions and helper classes
* **api/**: RESTful API endpoints and serialization

Fail-Safe Design
~~~~~~~~~~~~~~~~~

The system is designed to gracefully handle failures:

* **Database Disconnection**: Automatic reconnection with exponential backoff
* **External API Failures**: Fallback responses and error handling
* **Authentication Issues**: Graceful degradation to public mode
* **Resource Exhaustion**: Rate limiting and resource monitoring

Cost Optimization
~~~~~~~~~~~~~~~~~~

Strategic architectural decisions minimize operational costs:

* **AI Provider Selection**: Free tier HuggingFace + low-cost OpenRouter
* **Database Strategy**: Efficient connection pooling and query optimization
* **Caching Strategy**: In-memory caching for frequently accessed data
* **Resource Management**: Optimized for Replit's resource constraints

Application Structure
---------------------

Directory Organization
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    nous-personal-assistant/
    ├── main.py                    # Application launcher
    ├── app.py                     # Main Flask application
    ├── models/                    # Database models
    │   ├── __init__.py
    │   ├── user.py               # User authentication model
    │   └── beta_models.py        # Beta testing models
    ├── routes/                    # Route handlers
    │   ├── __init__.py
    │   ├── main.py               # Public routes
    │   ├── api.py                # API endpoints
    │   └── beta_admin.py         # Admin interface
    ├── utils/                     # Utility modules
    │   ├── __init__.py
    │   ├── health_monitor.py     # System health monitoring
    │   ├── database_optimizer.py # Database performance
    │   └── cost_optimized_ai.py  # AI provider interface
    ├── api/                       # Chat API system
    │   ├── __init__.py
    │   └── chat.py               # Chat dispatcher
    ├── templates/                 # Jinja2 templates
    │   ├── base.html             # Base template
    │   ├── landing.html          # Public landing page
    │   ├── app.html              # Chat interface
    │   └── admin/                # Admin templates
    ├── static/                    # Static assets
    │   ├── styles.css            # Application CSS
    │   ├── app.js                # Frontend JavaScript
    │   └── service-worker.js     # PWA functionality
    ├── docs/                      # Documentation
    │   ├── conf.py               # Sphinx configuration
    │   └── *.rst                 # Documentation files
    └── tests/                     # Test suites
        ├── test_app.py           # Application tests
        └── test_api.py           # API tests

Module Dependencies
~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    main.py
    └── app.py
        ├── models/
        │   ├── user.py
        │   └── beta_models.py
        ├── routes/
        │   ├── main.py
        │   ├── api.py
        │   └── beta_admin.py
        ├── utils/
        │   ├── health_monitor.py
        │   ├── database_optimizer.py
        │   └── cost_optimized_ai.py
        └── api/
            └── chat.py

Data Architecture
-----------------

Database Schema
~~~~~~~~~~~~~~~

**User Management:**

.. code-block:: sql

    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        name VARCHAR(255),
        google_id VARCHAR(255) UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE
    );

**Beta Testing:**

.. code-block:: sql

    CREATE TABLE feature_flags (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) UNIQUE NOT NULL,
        description TEXT,
        enabled BOOLEAN DEFAULT FALSE,
        rollout_percentage INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE user_feedback (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        feedback_type VARCHAR(50),
        message TEXT,
        rating INTEGER CHECK (rating >= 1 AND rating <= 5),
        metadata JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

**Session Management:**

.. code-block:: sql

    CREATE TABLE sessions (
        id VARCHAR(255) PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        data JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP
    );

Connection Management
~~~~~~~~~~~~~~~~~~~~~

SQLAlchemy configuration optimized for Replit:

.. code-block:: python

    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_size": 2,                 # Small pool for resource efficiency
        "max_overflow": 10,             # Handle traffic spikes
        "pool_recycle": 3600,           # Prevent stale connections
        "pool_pre_ping": True,          # Validate connections
        "connect_args": {
            "options": "-c timezone=utc"  # Consistent timezone
        }
    }

Query Optimization
~~~~~~~~~~~~~~~~~~

Database queries are optimized for performance:

* **Indexed Lookups**: Primary keys and foreign keys indexed
* **Query Batching**: Bulk operations where possible
* **Connection Pooling**: Reused connections for efficiency
* **Prepared Statements**: SQLAlchemy automatic parameterization

Authentication Architecture
---------------------------

OAuth 2.0 Implementation
~~~~~~~~~~~~~~~~~~~~~~~~

Google OAuth integration follows standard OAuth 2.0 flow:

1. **Authorization Request**
   
   .. code-block:: python
   
       @app.route('/login')
       def login():
           authorization_url, state = google.authorization_url(
               'https://accounts.google.com/o/oauth2/auth',
               access_type="online",
               prompt="select_account"
           )
           session['oauth_state'] = state
           return redirect(authorization_url)

2. **Authorization Callback**
   
   .. code-block:: python
   
       @app.route('/oauth/callback')
       def oauth_callback():
           token = google.fetch_token(
               'https://oauth2.googleapis.com/token',
               authorization_response=request.url,
               state=session.get('oauth_state')
           )
           user_info = google.get('https://www.googleapis.com/userinfo/v2/me')
           # Create or update user session

Session Management
~~~~~~~~~~~~~~~~~~

Session security configuration:

.. code-block:: python

    app.config.update(
        SESSION_COOKIE_SECURE=True,      # HTTPS only in production
        SESSION_COOKIE_HTTPONLY=True,    # No JavaScript access
        SESSION_COOKIE_SAMESITE='Lax',   # CSRF protection
        PERMANENT_SESSION_LIFETIME=timedelta(days=30)
    )

Permission System
~~~~~~~~~~~~~~~~~

Role-based access control:

.. code-block:: python

    def require_auth(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('user_id'):
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function

    def require_admin(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_email = session.get('user_email')
            if user_email != 'toledonick98@gmail.com':
                abort(403)
            return f(*args, **kwargs)
        return decorated_function

API Architecture
----------------

RESTful Design
~~~~~~~~~~~~~~

API endpoints follow REST conventions:

.. code-block:: text

    GET    /api/user                 # Get current user
    POST   /api/chat                 # Send chat message
    GET    /api/health               # System health
    GET    /api/beta/flags           # List feature flags
    PUT    /api/beta/flags/{id}      # Update feature flag
    POST   /api/feedback             # Submit feedback

Response Format
~~~~~~~~~~~~~~~

Standardized JSON responses:

.. code-block:: python

    # Success response
    {
        "data": {...},
        "status": "success",
        "timestamp": "2025-06-27T12:00:00Z"
    }

    # Error response
    {
        "error": {
            "code": "ERROR_CODE",
            "message": "Human readable message",
            "details": "Technical details"
        },
        "status": "error",
        "timestamp": "2025-06-27T12:00:00Z"
    }

Error Handling
~~~~~~~~~~~~~~

Comprehensive error handling strategy:

.. code-block:: python

    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith('/api/'):
            return jsonify({
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Resource not found"
                },
                "status": "error"
            }), 404
        return render_template('404.html'), 404

Chat System Architecture
------------------------

Intent-Based Routing
~~~~~~~~~~~~~~~~~~~~

Chat messages are routed based on intent patterns:

.. code-block:: python

    class ChatDispatcher:
        def __init__(self):
            self.handlers = {}
            self.auto_discover_handlers()
        
        async def dispatch(self, message: str, context: Dict) -> Dict:
            intent = self.classify_intent(message)
            handler = self.get_handler(intent)
            return await handler(message, context)

Handler Registration
~~~~~~~~~~~~~~~~~~~~

Automatic handler discovery and registration:

.. code-block:: python

    def register_chat_handler(intent_patterns: list, handler_func):
        """Register a chat handler for specific intent patterns"""
        for pattern in intent_patterns:
            CHAT_HANDLERS[pattern] = handler_func

    # Example handler
    @register_chat_handler(['weather', 'forecast', 'temperature'])
    def handle_weather_query(message: str, context: Dict) -> Dict:
        location = extract_location(message)
        weather_data = get_weather(location)
        return format_weather_response(weather_data)

AI Provider Integration
~~~~~~~~~~~~~~~~~~~~~~~

Unified provider interface with fallbacks:

.. code-block:: python

    class AIProviderManager:
        def __init__(self):
            self.providers = [
                OpenRouterProvider(),
                HuggingFaceProvider(),
                FallbackProvider()
            ]
        
        async def generate_response(self, prompt: str) -> str:
            for provider in self.providers:
                try:
                    return await provider.generate(prompt)
                except Exception as e:
                    logging.warning(f"Provider {provider} failed: {e}")
            raise Exception("All AI providers failed")

Health Monitoring Architecture
------------------------------

Multi-Level Health Checks
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    class HealthMonitor:
        def __init__(self):
            self.checks = [
                DatabaseHealthCheck(),
                ExternalServiceHealthCheck(),
                SystemResourceHealthCheck()
            ]
        
        def get_health_status(self) -> Dict:
            results = {}
            overall_status = "healthy"
            
            for check in self.checks:
                try:
                    result = check.perform_check()
                    results[check.name] = result
                    if result['status'] != 'healthy':
                        overall_status = 'degraded'
                except Exception as e:
                    results[check.name] = {
                        'status': 'unhealthy',
                        'error': str(e)
                    }
                    overall_status = 'unhealthy'
            
            return {
                'overall_status': overall_status,
                'checks': results,
                'timestamp': datetime.utcnow().isoformat()
            }

Performance Monitoring
~~~~~~~~~~~~~~~~~~~~~~

Real-time performance metrics:

.. code-block:: python

    @app.before_request
    def before_request():
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        duration = time.time() - g.start_time
        if duration > 1.0:  # Log slow requests
            logging.warning(f"Slow request: {request.path} took {duration:.2f}s")
        return response

Beta Testing Architecture
-------------------------

Feature Flag System
~~~~~~~~~~~~~~~~~~~

Database-driven feature flags:

.. code-block:: python

    class FeatureFlagManager:
        def is_enabled(self, flag_name: str, user_id: int = None) -> bool:
            flag = FeatureFlag.query.filter_by(name=flag_name).first()
            if not flag or not flag.enabled:
                return False
            
            if flag.rollout_percentage == 100:
                return True
            
            if user_id:
                # Consistent user-based rollout
                user_hash = hash(f"{flag_name}:{user_id}") % 100
                return user_hash < flag.rollout_percentage
            
            return random.randint(0, 99) < flag.rollout_percentage

User Segmentation
~~~~~~~~~~~~~~~~~

Targeted feature rollouts:

.. code-block:: python

    def check_feature_access(flag_name: str, user: User) -> bool:
        flag = FeatureFlag.query.filter_by(name=flag_name).first()
        
        # Check user segments
        if flag.target_segments:
            user_segment = determine_user_segment(user)
            if user_segment not in flag.target_segments:
                return False
        
        # Check rollout percentage
        return flag_manager.is_enabled(flag_name, user.id)

Deployment Architecture
-----------------------

Replit Optimization
~~~~~~~~~~~~~~~~~~~

Configuration optimized for Replit Cloud:

.. code-block:: toml

    # replit.toml
    run = ["python3", "main.py"]
    
    [deployment]
    run = ["python3", "main.py"]
    deploymentTarget = "cloudrun"
    
    [env]
    PORT = "5000"
    PUBLIC_MODE = "true"
    
    [auth]
    pageEnabled = false
    buttonEnabled = false

ProxyFix Configuration
~~~~~~~~~~~~~~~~~~~~~~

Proper proxy handling for Replit:

.. code-block:: python

    from werkzeug.middleware.proxy_fix import ProxyFix
    
    app.wsgi_app = ProxyFix(
        app.wsgi_app, 
        x_for=1,     # Trust 1 proxy for X-Forwarded-For
        x_proto=1,   # Trust 1 proxy for X-Forwarded-Proto
        x_host=1,    # Trust 1 proxy for X-Forwarded-Host
        x_port=1     # Trust 1 proxy for X-Forwarded-Port
    )

Security Architecture
---------------------

Defense in Depth
~~~~~~~~~~~~~~~~~

Multiple security layers:

1. **Transport Security**: HTTPS/TLS encryption
2. **Authentication**: OAuth 2.0 with Google
3. **Session Security**: Secure cookie configuration
4. **Input Validation**: Form validation and sanitization
5. **CSRF Protection**: Token-based CSRF prevention
6. **Rate Limiting**: Request throttling
7. **Error Handling**: Secure error responses

Security Headers
~~~~~~~~~~~~~~~~

Comprehensive security header configuration:

.. code-block:: python

    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response

Future Architecture Considerations
----------------------------------

Microservices Migration
~~~~~~~~~~~~~~~~~~~~~~~

Potential service decomposition:

* **Authentication Service**: User management and OAuth
* **Chat Service**: AI integration and conversation handling
* **Analytics Service**: User behavior and system metrics
* **Admin Service**: Beta management and system administration

Caching Strategy
~~~~~~~~~~~~~~~~

Redis integration for improved performance:

* **Session Storage**: Distributed session management
* **API Response Caching**: Frequently accessed data
* **Rate Limiting**: Distributed rate limiting counters
* **Feature Flag Caching**: Reduce database queries

Event-Driven Architecture
~~~~~~~~~~~~~~~~~~~~~~~~~

Webhook and event system:

* **User Events**: Registration, login, feature usage
* **System Events**: Health changes, errors, deployments
* **External Events**: API webhooks, scheduled tasks
* **Analytics Events**: User interaction tracking

This comprehensive architecture documentation provides the foundation for understanding, maintaining, and extending the NOUS Personal Assistant system.