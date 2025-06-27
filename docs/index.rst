NOUS Personal Assistant Documentation
====================================

Welcome to the comprehensive documentation for NOUS Personal Assistant, a sophisticated Flask-based web application that provides intelligent, adaptive, and user-friendly AI interactions.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   installation
   api_reference
   architecture
   development
   deployment
   troubleshooting
   changelog

Quick Start
-----------

NOUS Personal Assistant is designed to be easily deployable on Replit with minimal configuration:

1. **Authentication**: Google OAuth integration for secure access
2. **AI Integration**: Multi-modal AI interactions with cost-optimized providers
3. **Health Monitoring**: Comprehensive system health checks and monitoring
4. **Beta Management**: Feature flag system with administrative controls

Key Features
------------

* **Professional Chat Interface**: Modern, responsive chat UI with 6 theme options
* **Enterprise-Grade Backend**: Health monitoring, database optimization, graceful shutdown
* **Beta Testing Infrastructure**: Feature flags, user management, feedback collection
* **Public Access Configuration**: Bypasses Replit authentication while maintaining security
* **Cost-Optimized AI**: Uses OpenRouter and HuggingFace for 99.85% cost reduction
* **Comprehensive Documentation**: Auto-generated API docs, architecture diagrams

System Architecture
------------------

NOUS follows a modular Flask architecture with:

* **Single Entry Point**: ``main.py`` → ``app.py`` for clean deployment
* **Database Layer**: SQLAlchemy ORM with PostgreSQL support
* **Authentication**: Google OAuth with session management
* **API Design**: RESTful endpoints with comprehensive health checks
* **Frontend**: Progressive Web App with offline support

Core Components
---------------

.. autosummary::
   :toctree: _autosummary

   app
   models
   routes
   utils
   api

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Development Status
==================

**Current Version**: 1.0.0 (Production Ready)

**Last Updated**: June 27, 2025

**Deployment Status**: Ready for Replit Cloud deployment

**Documentation Coverage**: Complete API reference, architecture documentation, and development guides

Getting Help
============

* **GitHub Issues**: Report bugs and feature requests
* **Documentation**: Comprehensive guides and API reference
* **Health Monitoring**: Real-time system status at ``/healthz`` endpoints
* **Admin Console**: Beta management and user analytics (restricted access)

License
=======

This project is licensed under the MIT License - see the ``LICENSE`` file for details.