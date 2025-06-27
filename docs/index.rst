NOUS Personal Assistant Documentation
=====================================

Welcome to the comprehensive documentation for NOUS Personal Assistant, an advanced AI-powered personal assistant web application that leverages cutting-edge technologies to provide intelligent, adaptive, and user-friendly multi-modal interactions.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   getting_started
   architecture
   api_reference
   user_guide
   developer_guide
   security
   changelog

Quick Start
-----------

NOUS Personal Assistant is a Flask-based web application with Google OAuth authentication and a modern chat interface. 

Key Features:
- **AI-Powered Chat Interface**: Intelligent conversation handling with intent recognition
- **Google OAuth Integration**: Secure authentication with Google accounts
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Progressive Web App**: Offline support and native app-like experience
- **Comprehensive Health Monitoring**: Built-in health checks and performance monitoring
- **Beta Testing Framework**: Advanced feature flag system for gradual rollouts

Installation
------------

1. Clone the repository
2. Install dependencies: ``pip install -r requirements.txt``
3. Set up environment variables
4. Run the application: ``python main.py``

See :doc:`getting_started` for detailed installation instructions.

Architecture Overview
--------------------

The application follows a modular architecture with:

- **Flask Backend**: RESTful API with comprehensive route structure
- **SQLAlchemy ORM**: Database abstraction with PostgreSQL support
- **Modern Frontend**: Progressive Web App with service worker caching
- **AI Integration**: Cost-optimized AI providers for intelligent responses
- **Security Features**: OAuth, CORS, rate limiting, and security headers

See :doc:`architecture` for detailed architectural information.

API Documentation
-----------------

.. toctree::
   :maxdepth: 2
   :caption: API Reference:

   autoapi/index

The API documentation is automatically generated from the source code using Sphinx AutoAPI.

Database Schema
---------------

.. mermaid::

   erDiagram
       User {
           int id PK
           string email UK
           string name
           datetime created_at
           datetime updated_at
       }
       
       BetaUser {
           int id PK
           int user_id FK
           string email
           string status
           datetime invited_at
           datetime activated_at
       }
       
       FeatureFlag {
           int id PK
           string name UK
           string description
           boolean enabled
           float rollout_percentage
           datetime created_at
           datetime updated_at
       }
       
       UserFeedback {
           int id PK
           int user_id FK
           string feature_name
           int rating
           text feedback
           datetime created_at
       }
       
       User ||--o{ BetaUser : "can be"
       User ||--o{ UserFeedback : "provides"

Application Flow
----------------

.. mermaid::

   sequenceDiagram
       participant U as User
       participant W as Web App
       participant G as Google OAuth
       participant D as Database
       participant A as AI Service
       
       U->>W: Access Application
       W->>G: Redirect to Google OAuth
       G->>U: Show Login Screen
       U->>G: Provide Credentials
       G->>W: Return Auth Code
       W->>G: Exchange for Access Token
       G->>W: Return User Info
       W->>D: Store/Update User
       D->>W: Confirm User Stored
       W->>U: Show Chat Interface
       
       U->>W: Send Chat Message
       W->>A: Process Message
       A->>W: Return AI Response
       W->>U: Display Response

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`