# NOUS Personal Assistant

## Overview

NOUS Personal Assistant is a Flask-based web application designed to provide intelligent, adaptive, and user-friendly AI interactions. The application serves as a comprehensive personal assistant platform with various integrated services and capabilities.

## Executive Summary

NOUS Personal Assistant is a comprehensive Flask-based AI-powered personal assistant featuring **257 distinct utility functions** across **67 specialized modules**. The application provides extensive life management capabilities including medical care coordination, financial management, crisis intervention, DBT therapy support, smart shopping, entertainment integration, and advanced AI chat functionality.

**Technical Architecture:**
- **47 Route Handler Files** with 150+ endpoints
- **67 Utility Modules** with specialized helper functions
- **15 Core Life Management Domains** covered
- **Cost-Optimized AI Integration** (99.85% cost reduction achieved)
- **Multi-Modal Interfaces** (Web, Voice, Mobile)

---

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python main.py
   ```

3. **Access the Application**:
   - Web Interface: `http://localhost:5000`
   - API Endpoint: `http://localhost:5000/api/chat`

## Architecture

### Core Components
- **Flask Application**: Web framework with blueprint architecture
- **Database Layer**: SQLAlchemy ORM with PostgreSQL/SQLite support
- **Chat System**: Auto-discovery chat handler registration
- **API Layer**: RESTful API with comprehensive routing

### Key Features
- **Chat-First Design**: Unified chat interface with intent-based routing
- **Auto-Discovery**: Automatic handler registration from codebase analysis
- **Multi-Modal Support**: Web, API, and voice interfaces
- **Cost-Optimized AI**: Efficient AI provider integration

## Feature Highlights

### Healthcare Coordination
- Doctor and appointment management
- Medication tracking and refill reminders
- Health data integration

### Crisis Support
- DBT therapy integration
- Crisis intervention resources
- Grounding exercises

### Financial Management
- Budget tracking
- Expense categorization
- Financial goal monitoring

## Deployment

### Replit Cloud
The application is optimized for Replit Cloud deployment:

```toml
# replit.toml
[deployment]
run = "python main.py"
deploymentTarget = "cloudrun"
```

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `SESSION_SECRET`: Flask session secret key
- `OPENROUTER_API_KEY`: OpenRouter API key for AI features

## Documentation

- [Architecture Guide](docs/ARCHITECTURE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Developer Guide](docs/DEVELOPER_GUIDE.md)
- [Security Audit](docs/SECURITY_AUDIT.md)

## License

This project is proprietary software. All rights reserved.
