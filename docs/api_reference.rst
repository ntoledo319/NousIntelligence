API Reference
=============

This section provides comprehensive documentation for all API endpoints, models, and utilities in the NOUS Personal Assistant application.

Core Application Module
-----------------------

.. automodule:: app
   :members:
   :undoc-members:
   :show-inheritance:

Authentication Endpoints
------------------------

Google OAuth Flow
~~~~~~~~~~~~~~~~~

**Login Endpoint**
  ``GET /login``
  
  Initiates Google OAuth authentication flow.

**OAuth Callback**
  ``GET /oauth/callback``
  
  Handles Google OAuth callback and creates user session.

**Demo Login** (Development Only)
  ``POST /demo-login``
  
  Creates demo session for development testing.

**Logout**
  ``POST /logout``
  
  Terminates user session and clears authentication data.

Core API Endpoints
------------------

Chat API
~~~~~~~~

**Main Chat Endpoint**
  ``POST /api/v1/chat``
  
  Primary chat interface for AI interactions.
  
  **Request Body:**
  
  .. code-block:: json
  
      {
          "message": "User input message",
          "context": {
              "conversation_id": "optional-uuid",
              "user_preferences": {}
          }
      }
  
  **Response:**
  
  .. code-block:: json
  
      {
          "response": "AI response text",
          "context": {
              "conversation_id": "uuid",
              "tokens_used": 150,
              "model": "gemini-pro"
          },
          "status": "success"
      }

**Chat Handler Registration**
  ``GET /api/v1/chat/handlers``
  
  Lists all available chat handlers and their intent patterns.

User Management API
~~~~~~~~~~~~~~~~~~~

**Get Current User**
  ``GET /api/v1/user``
  
  Returns current authenticated user information.
  
  **Response:**
  
  .. code-block:: json
  
      {
          "id": "user-uuid",
          "email": "user@example.com",
          "name": "User Name",
          "authenticated": true,
          "beta_access": false
      }

Health Monitoring API
~~~~~~~~~~~~~~~~~~~~~

**Application Health**
  ``GET /health``
  
  Basic application health check.

**Comprehensive Health**
  ``GET /healthz``
  
  Detailed system health with database connectivity.
  
  **Response:**
  
  .. code-block:: json
  
      {
          "status": "healthy",
          "timestamp": "2025-06-27T12:00:00Z",
          "database": {
              "status": "connected",
              "response_time_ms": 15
          },
          "external_services": {
              "openrouter": "operational",
              "huggingface": "operational"
          },
          "system": {
              "memory_usage": "45%",
              "cpu_usage": "12%"
          }
      }

**Chat API Health**
  ``GET /api/v1/health/chat``
  
  Chat system specific health checks.

Beta Management API
-------------------

.. note::
   Beta management endpoints require administrative privileges (toledonick98@gmail.com).

Feature Flags
~~~~~~~~~~~~~

**List Feature Flags**
  ``GET /api/beta/flags``
  
  Returns all feature flags and their current states.

**Update Feature Flag**
  ``PUT /api/beta/flags/{flag_id}``
  
  Updates feature flag configuration.
  
  **Request Body:**
  
  .. code-block:: json
  
      {
          "enabled": true,
          "rollout_percentage": 50,
          "target_users": ["user1", "user2"]
      }

User Feedback API
~~~~~~~~~~~~~~~~~

**Submit Feedback**
  ``POST /api/feedback``
  
  Submits user feedback for analysis.
  
  **Request Body:**
  
  .. code-block:: json
  
      {
          "type": "bug_report",
          "message": "Detailed feedback message",
          "rating": 4,
          "metadata": {
              "page": "/dashboard",
              "browser": "Chrome 91.0"
          }
      }

**Get Feedback Analytics** (Admin Only)
  ``GET /api/admin/feedback/analytics``
  
  Returns aggregated feedback analytics.

Database Models
---------------

.. automodule:: models
   :members:
   :undoc-members:
   :show-inheritance:

User Model
~~~~~~~~~~

.. autoclass:: models.User
   :members:
   :undoc-members:

Beta Models
~~~~~~~~~~~

.. automodule:: models.beta_models
   :members:
   :undoc-members:
   :show-inheritance:

Utility Modules
---------------

Health Monitor
~~~~~~~~~~~~~~

.. automodule:: utils.health_monitor
   :members:
   :undoc-members:
   :show-inheritance:

Database Optimizer
~~~~~~~~~~~~~~~~~~

.. automodule:: utils.database_optimizer
   :members:
   :undoc-members:
   :show-inheritance:

Cost Optimized AI
~~~~~~~~~~~~~~~~~~

.. automodule:: utils.cost_optimized_ai
   :members:
   :undoc-members:
   :show-inheritance:

Route Handlers
--------------

Main Routes
~~~~~~~~~~~

.. automodule:: routes.main
   :members:
   :undoc-members:
   :show-inheritance:

API Routes
~~~~~~~~~~

.. automodule:: routes.api
   :members:
   :undoc-members:
   :show-inheritance:

Beta Admin Routes
~~~~~~~~~~~~~~~~~

.. automodule:: routes.beta_admin
   :members:
   :undoc-members:
   :show-inheritance:

Error Handling
--------------

Standard Error Responses
~~~~~~~~~~~~~~~~~~~~~~~~

All API endpoints return standardized error responses:

.. code-block:: json

    {
        "error": {
            "code": "ERROR_CODE",
            "message": "Human readable error message",
            "details": "Additional technical details",
            "timestamp": "2025-06-27T12:00:00Z"
        },
        "status": "error"
    }

Common Error Codes
~~~~~~~~~~~~~~~~~~

* ``AUTHENTICATION_REQUIRED`` - User must be logged in
* ``INSUFFICIENT_PERMISSIONS`` - User lacks required permissions
* ``INVALID_REQUEST`` - Request format or parameters invalid
* ``RESOURCE_NOT_FOUND`` - Requested resource does not exist
* ``RATE_LIMIT_EXCEEDED`` - Too many requests from user
* ``EXTERNAL_SERVICE_ERROR`` - Third-party service unavailable
* ``DATABASE_ERROR`` - Database connectivity or query error

HTTP Status Codes
~~~~~~~~~~~~~~~~~

* ``200 OK`` - Successful request
* ``201 Created`` - Resource successfully created
* ``400 Bad Request`` - Invalid request format
* ``401 Unauthorized`` - Authentication required
* ``403 Forbidden`` - Insufficient permissions
* ``404 Not Found`` - Resource not found
* ``429 Too Many Requests`` - Rate limit exceeded
* ``500 Internal Server Error`` - Server error
* ``503 Service Unavailable`` - External service error

Authentication & Authorization
------------------------------

OAuth 2.0 Flow
~~~~~~~~~~~~~~~

NOUS uses Google OAuth 2.0 for user authentication:

1. **Authorization Request**: User clicks login, redirected to Google
2. **Authorization Grant**: User approves access, Google redirects with code
3. **Access Token Request**: Application exchanges code for access token
4. **Resource Access**: Token used to access user information
5. **Session Creation**: User session established in Flask application

Session Management
~~~~~~~~~~~~~~~~~~

* **Session Duration**: 30 days default, configurable
* **Session Storage**: Filesystem-based (development) or Redis (production)
* **CSRF Protection**: Enabled for all forms
* **Secure Cookies**: HTTPOnly and Secure flags enabled in production

Permission Levels
~~~~~~~~~~~~~~~~~

* **Public Access**: Landing page, health checks, static assets
* **Authenticated Users**: Chat interface, user settings, API access
* **Beta Users**: Feature flag enabled features
* **Administrators**: Beta management, user analytics, system administration

Rate Limiting
~~~~~~~~~~~~~

* **Chat API**: 100 requests per hour per user
* **Health Endpoints**: 1000 requests per hour per IP
* **Admin APIs**: 50 requests per hour per admin user
* **Public Assets**: No rate limiting

Data Privacy & Security
-----------------------

Data Collection
~~~~~~~~~~~~~~~

* **User Information**: Email, name, OAuth profile data
* **Chat History**: Conversation data for context (encrypted at rest)
* **Analytics Data**: Anonymous usage statistics
* **Feedback Data**: User feedback and ratings

Data Retention
~~~~~~~~~~~~~~

* **Session Data**: 30 days after last activity
* **Chat History**: 90 days, then archived
* **Analytics**: Aggregated data retained indefinitely
* **Feedback**: 1 year retention policy

Security Measures
~~~~~~~~~~~~~~~~~

* **Data Encryption**: AES-256 encryption for sensitive data
* **Transport Security**: TLS 1.3 for all communications
* **Access Logging**: Comprehensive audit trail
* **Regular Security Scans**: Automated vulnerability assessments

This API reference provides comprehensive documentation for integrating with and extending the NOUS Personal Assistant platform. For additional examples and tutorials, see the development guide.