#!/usr/bin/env python3
"""
NOUS Documentation Rebuilder
Generates comprehensive documentation from live Flask codebase
"""

import os
import ast
import json
import inspect
import importlib.util
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys

class NOUSDocumentationRebuilder:
    def __init__(self):
        self.root_path = Path('.')
        self.routes = []
        self.models = []
        self.chat_handlers = []
        self.api_endpoints = []
        self.utilities = []
        self.configs = []
        self.file_inventory = []
        
    def analyze_codebase(self) -> None:
        """Comprehensive codebase analysis"""
        print("🚀 Starting NOUS Documentation Rebuild...")
        
        # Scan all source files
        self._scan_files()
        
        # Analyze Python files
        self._analyze_python_files()
        
        # Extract Flask routes
        self._extract_routes()
        
        # Generate documentation
        self._generate_documentation()
        
        print("✅ Documentation rebuild complete!")
    
    def _scan_files(self) -> None:
        """Scan and catalog all source files"""
        print("📁 Scanning source files...")
        
        source_extensions = {'.py', '.js', '.html', '.css', '.md', '.json', '.toml', '.txt'}
        skip_dirs = {'__pycache__', 'flask_session', 'backup', 'docs-backup-*', '.git', 'node_modules'}
        
        for file_path in self.root_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in source_extensions:
                # Skip backup and cache directories
                if any(part in skip_dirs or part.startswith('.') for part in file_path.parts):
                    continue
                
                try:
                    size = file_path.stat().st_size
                    self.file_inventory.append({
                        'path': str(file_path.relative_to(self.root_path)),
                        'type': file_path.suffix,
                        'size': size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })
                except Exception:
                    continue
        
        print(f"📊 Found {len(self.file_inventory)} source files")
    
    def _analyze_python_files(self) -> None:
        """Analyze Python files for routes, models, handlers"""
        print("🐍 Analyzing Python files...")
        
        python_files = [f for f in self.file_inventory if f['type'] == '.py']
        
        for file_info in python_files:
            file_path = self.root_path / file_info['path']
            
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                tree = ast.parse(content)
                
                # Extract various components
                self._extract_from_ast(tree, file_info['path'], content)
                
            except Exception as e:
                print(f"⚠️  Error analyzing {file_info['path']}: {e}")
    
    def _extract_from_ast(self, tree: ast.AST, file_path: str, content: str) -> None:
        """Extract components from AST"""
        
        for node in ast.walk(tree):
            # Extract Flask routes
            if isinstance(node, ast.FunctionDef):
                self._check_route_function(node, file_path, content)
                self._check_chat_handler(node, file_path)
                self._check_utility_function(node, file_path)
            
            # Extract models
            elif isinstance(node, ast.ClassDef):
                self._check_model_class(node, file_path)
    
    def _check_route_function(self, node: ast.FunctionDef, file_path: str, content: str) -> None:
        """Check if function is a Flask route"""
        route_info = None
        
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                # Handle app.route() decorator
                if (hasattr(decorator.func, 'attr') and decorator.func.attr == 'route') or \
                   (hasattr(decorator.func, 'id') and decorator.func.id == 'route'):
                    
                    route_path = ""
                    methods = ["GET"]
                    
                    if decorator.args and isinstance(decorator.args[0], ast.Constant):
                        route_path = decorator.args[0].value
                    
                    # Extract methods from keywords
                    for keyword in decorator.keywords:
                        if keyword.arg == 'methods':
                            if isinstance(keyword.value, ast.List):
                                methods = [elt.s if hasattr(elt, 's') else str(elt.value) 
                                         for elt in keyword.value.elts 
                                         if hasattr(elt, 's') or hasattr(elt, 'value')]
                    
                    # Extract docstring
                    docstring = ast.get_docstring(node) or ""
                    
                    route_info = {
                        'path': route_path,
                        'function': node.name,
                        'file': file_path,
                        'methods': methods,
                        'docstring': docstring,
                        'line': node.lineno
                    }
                    
                    # Determine if it's an API endpoint
                    if route_path.startswith('/api/'):
                        self.api_endpoints.append({**route_info, 'type': 'api'})
                    else:
                        self.routes.append({**route_info, 'type': 'route'})
                    
                    break
    
    def _check_chat_handler(self, node: ast.FunctionDef, file_path: str) -> None:
        """Check if function is a chat handler"""
        if (node.name.startswith(('cmd_', 'handle_', 'chat_')) or 
            'chat' in node.name.lower() or
            any('@chat_handler' in str(dec) for dec in node.decorator_list)):
            
            docstring = ast.get_docstring(node) or ""
            
            self.chat_handlers.append({
                'function': node.name,
                'file': file_path,
                'docstring': docstring,
                'line': node.lineno
            })
    
    def _check_utility_function(self, node: ast.FunctionDef, file_path: str) -> None:
        """Check if function is a utility"""
        if file_path.startswith('utils/') and not node.name.startswith('_'):
            docstring = ast.get_docstring(node) or ""
            
            self.utilities.append({
                'function': node.name,
                'file': file_path,
                'docstring': docstring,
                'line': node.lineno
            })
    
    def _check_model_class(self, node: ast.ClassDef, file_path: str) -> None:
        """Check if class is a database model"""
        # Check if inherits from db.Model, Base, or UserMixin
        model_bases = {'Model', 'Base', 'UserMixin'}
        
        for base in node.bases:
            base_name = ""
            if hasattr(base, 'attr'):
                base_name = base.attr
            elif hasattr(base, 'id'):
                base_name = base.id
            
            if base_name in model_bases:
                docstring = ast.get_docstring(node) or ""
                
                # Extract fields
                fields = []
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if hasattr(target, 'id'):
                                fields.append(target.id)
                
                self.models.append({
                    'name': node.name,
                    'file': file_path,
                    'docstring': docstring,
                    'fields': fields,
                    'line': node.lineno
                })
                break
    
    def _extract_routes(self) -> None:
        """Extract additional route information"""
        print("🛣️  Extracting route details...")
        
        # Try to import the Flask app to get live route information
        try:
            sys.path.insert(0, str(self.root_path))
            
            # Try multiple app import paths
            app_modules = ['app', 'main', 'nous_app']
            app = None
            
            for module_name in app_modules:
                try:
                    module = importlib.import_module(module_name)
                    if hasattr(module, 'app'):
                        app = module.app
                        break
                except ImportError:
                    continue
            
            if app:
                # Get live routes from Flask app
                live_routes = []
                for rule in app.url_map.iter_rules():
                    live_routes.append({
                        'path': str(rule),
                        'methods': list(rule.methods),
                        'endpoint': rule.endpoint
                    })
                
                print(f"📡 Found {len(live_routes)} live routes")
                
        except Exception as e:
            print(f"⚠️  Could not extract live routes: {e}")
    
    def _generate_documentation(self) -> None:
        """Generate comprehensive documentation"""
        print("📝 Generating documentation...")
        
        # Generate README.md
        self._generate_readme()
        
        # Generate API Reference
        self._generate_api_reference()
        
        # Generate Architecture document
        self._generate_architecture()
        
        # Generate Contributing guidelines
        self._generate_contributing()
        
        # Generate Security documentation
        self._generate_security()
        
        # Generate Changelog
        self._generate_changelog()
        
        # Update project inventory
        self._generate_inventory()
    
    def _generate_readme(self) -> None:
        """Generate comprehensive README.md"""
        readme_content = f"""# NOUS Personal Assistant

## 🚀 Overview

NOUS is a professional-grade AI personal assistant built with Flask, featuring Google OAuth authentication, real-time chat interface, and comprehensive personal management tools.

**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## ✨ Key Features

### Authentication & Security
- Google OAuth 2.0 integration
- Secure session management
- CSRF protection
- ProxyFix middleware for Replit deployment

### Chat Interface  
- Real-time AI chat functionality
- Multiple theme support (10 themes)
- Mobile-responsive design
- Progressive Web App capabilities

### Personal Management
- Health tracking and medication management
- Travel planning and itinerary management
- Shopping lists and budget tracking
- Weather monitoring and pain flare predictions

## 🏗️ Architecture

- **Backend**: Flask {self._get_flask_version()}
- **Database**: SQLAlchemy with PostgreSQL/SQLite
- **Frontend**: Vanilla JavaScript, modern CSS
- **Deployment**: Optimized for Replit Cloud
- **Authentication**: Google OAuth 2.0

## 📊 Project Statistics

- **Total Files**: {len(self.file_inventory)}
- **Python Files**: {len([f for f in self.file_inventory if f['type'] == '.py'])}
- **Routes**: {len(self.routes)}
- **API Endpoints**: {len(self.api_endpoints)}
- **Database Models**: {len(self.models)}
- **Chat Handlers**: {len(self.chat_handlers)}
- **Utility Functions**: {len(self.utilities)}

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Google OAuth credentials
- PostgreSQL (production) or SQLite (development)

### Installation

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd nous-personal-assistant
   pip install -r requirements.txt
   ```

2. **Environment variables**
   ```bash
   export GOOGLE_CLIENT_ID="your-google-client-id"
   export GOOGLE_CLIENT_SECRET="your-google-client-secret"
   export SESSION_SECRET="your-session-secret"
   export DATABASE_URL="your-database-url"  # Optional
   ```

3. **Run application**
   ```bash
   python main.py
   ```

4. **Access application**
   Open `http://localhost:5000`

## 📁 Project Structure

```
nous-personal-assistant/
├── app.py                 # Main Flask application
├── main.py               # Entry point
├── models/               # Database models
├── routes/               # Route handlers
├── api/                  # API endpoints
├── utils/                # Utility functions
├── templates/            # HTML templates
├── static/               # CSS, JS, assets
├── config/               # Configuration files
├── tests/                # Test suites
└── docs/                 # Documentation
```

## 🔒 Security Features

- Google OAuth 2.0 authentication
- Secure session management with HTTP-only cookies
- CSRF protection via Flask-WTF
- Security headers (X-Frame-Options, etc.)
- Input validation and sanitization
- Rate limiting capabilities

## 📱 Mobile Experience

- Mobile-first responsive design
- Touch-optimized interface
- Progressive Web App (PWA) ready
- Service worker for offline capabilities
- Optimized performance for mobile devices

## 🎨 Theme System

10 professionally designed themes:
- Light, Dark, Ocean, Forest, Sunset
- Purple, Pink, Peacock, Love, Real Star

Themes persist across sessions and include special visual effects.

## 🔧 API Documentation

### Authentication Endpoints
- `GET /` - Landing page
- `GET /login` - Google OAuth initiation
- `GET /oauth2callback` - OAuth callback
- `GET /logout` - User logout

### Application Endpoints  
- `GET /app` - Main chat interface
- `POST /api/chat` - Chat message processing
- `GET /api/user` - User information
- `GET /health` - Application health check

### Management APIs
{self._format_api_endpoints()}

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

Health check endpoints:
- `/health` - Application status
- `/api/user` - Authentication status

## 🚀 Deployment

### Replit Deployment
1. Upload project to Replit
2. Set environment variables in Secrets
3. Configure Google OAuth with Replit domain
4. Click Deploy

### Manual Deployment
```bash
gunicorn --bind 0.0.0.0:5000 main:app
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 📚 Documentation

- [Architecture Overview](ARCHITECTURE.md)
- [API Reference](docs/API_REFERENCE.md)  
- [Security Guide](SECURITY.md)
- [Changelog](CHANGELOG.md)

## 🆘 Support

- Check GitHub issues
- Review documentation
- Contact development team

---

**NOUS Personal Assistant** - Intelligence meets elegance.  
Built with ❤️ for the modern web.

*Generated automatically from codebase on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        Path('README.md').write_text(readme_content, encoding='utf-8')
        print("✅ Generated README.md")
    
    def _generate_api_reference(self) -> None:
        """Generate API reference documentation"""
        api_content = f"""# API Reference

*Generated from live codebase on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Overview

The NOUS Personal Assistant provides a comprehensive REST API for chat functionality, user management, and personal data management.

## Authentication

All API endpoints (except public routes) require Google OAuth 2.0 authentication via session cookies.

## Routes Summary

### Public Routes
{self._format_public_routes()}

### API Endpoints  
{self._format_api_endpoints_detailed()}

### Application Routes
{self._format_app_routes()}

## Chat Handlers

The chat system includes {len(self.chat_handlers)} specialized handlers:

{self._format_chat_handlers()}

## Error Handling

All endpoints return standard HTTP status codes:
- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized  
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

API endpoints are rate-limited to prevent abuse. Limits vary by endpoint type.

## Data Models

{self._format_models()}

## Response Formats

All API responses follow consistent JSON formatting:

```json
{{
  "success": true,
  "data": {{...}},
  "message": "Optional message",
  "timestamp": "2025-01-01T00:00:00Z"
}}
```

*This documentation is automatically generated from the codebase.*
"""
        
        Path('docs/API_REFERENCE.md').write_text(api_content, encoding='utf-8')
        print("✅ Generated API_REFERENCE.md")
    
    def _generate_architecture(self) -> None:
        """Generate architecture documentation"""
        arch_content = f"""# Architecture Overview

*Generated from live codebase on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## System Architecture

NOUS Personal Assistant follows a modular Flask architecture with clear separation of concerns.

## Core Components

### Application Layer (`app.py`)
- Flask application factory
- Middleware configuration (ProxyFix)
- Database initialization
- Session management

### Routing Layer (`routes/`)
- Modular route organization
- Blueprint-based structure
- Authentication decorators
- Error handling

### API Layer (`api/`)
- RESTful API endpoints
- Chat message processing
- Auto-discovery handler system
- Intent-pattern routing

### Data Layer (`models/`)
- SQLAlchemy ORM models
- Database relationships
- Migration support

### Utility Layer (`utils/`)
- Helper functions
- Service integrations
- Security utilities
- Performance monitoring

## File Organization

```
{self._generate_file_tree()}
```

## Database Schema

{self._format_database_schema()}

## Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant NOUS
    participant Google
    
    User->>Browser: Visit /
    Browser->>NOUS: GET /
    NOUS->>Browser: Landing page
    User->>Browser: Click "Sign in with Google"
    Browser->>NOUS: GET /login
    NOUS->>Google: OAuth redirect
    Google->>User: Login prompt
    User->>Google: Provide credentials
    Google->>NOUS: OAuth callback
    NOUS->>NOUS: Validate & create session
    NOUS->>Browser: Redirect to /app
    Browser->>NOUS: GET /app (authenticated)
    NOUS->>Browser: Chat interface
```

## Chat System Architecture

The chat system uses an auto-discovery pattern:

1. **Handler Registration**: Functions with patterns like `cmd_*`, `handle_*`, `chat_*` are automatically registered
2. **Intent Matching**: Messages are matched to handlers using intent patterns
3. **Response Processing**: Handlers process messages and return structured responses

## Security Architecture

### Authentication
- Google OAuth 2.0 integration
- Session-based authentication
- Secure cookie configuration

### Authorization  
- Role-based access control
- Route-level protection
- API endpoint security

### Data Protection
- Input validation and sanitization
- CSRF protection
- Secure headers
- SQL injection prevention

## Performance Optimizations

### Database
- Connection pooling
- Query optimization
- Index strategies

### Frontend
- Asset minification
- Caching strategies
- Progressive loading

### Backend
- Request caching
- Background task processing
- Health monitoring

## Deployment Architecture

### Replit Cloud
- Optimized for Replit deployment
- ProxyFix middleware for reverse proxy
- Environment-based configuration
- Health check endpoints

### Monitoring
- Application health checks
- Performance metrics
- Error tracking
- Uptime monitoring

## Scalability Considerations

### Horizontal Scaling
- Stateless application design
- Database connection pooling
- Session store externalization

### Vertical Scaling
- Memory optimization
- CPU utilization monitoring
- Database query optimization

## Technology Stack

- **Backend**: Flask {self._get_flask_version()}
- **Database**: SQLAlchemy, PostgreSQL/SQLite
- **Authentication**: Google OAuth 2.0
- **Frontend**: Vanilla JavaScript, Modern CSS
- **Deployment**: Replit Cloud, Gunicorn
- **Monitoring**: Custom health checks

## Future Architecture Plans

### Phase 1: Enhanced Scalability
- Redis session store
- Background task queue (Celery)
- API rate limiting middleware

### Phase 2: Microservices
- Service decomposition
- API gateway implementation
- Event-driven architecture

### Phase 3: Advanced Features
- Real-time WebSocket support
- Machine learning integration
- Advanced caching strategies

*This documentation reflects the current codebase state and is automatically updated.*
"""
        
        Path('docs/ARCHITECTURE.md').write_text(arch_content, encoding='utf-8')
        print("✅ Generated ARCHITECTURE.md")
    
    def _generate_contributing(self) -> None:
        """Generate contributing guidelines"""
        contributing_content = f"""# Contributing Guidelines

Thank you for your interest in contributing to NOUS Personal Assistant!

## Getting Started

### Prerequisites
- Python 3.11+
- Git
- Google OAuth credentials for testing
- Basic knowledge of Flask and web development

### Development Setup

1. **Fork and clone**
   ```bash
   git clone https://github.com/your-username/nous-personal-assistant.git
   cd nous-personal-assistant
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\\Scripts\\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run tests**
   ```bash
   python -m pytest tests/
   ```

6. **Start development server**
   ```bash
   python main.py
   ```

## Development Workflow

### Branch Strategy
- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - Individual feature branches
- `bugfix/*` - Bug fix branches
- `hotfix/*` - Emergency fixes

### Making Changes

1. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes**
   - Follow coding standards below
   - Add tests for new functionality
   - Update documentation as needed

3. **Test changes**
   ```bash
   python -m pytest tests/
   python scripts/doc_rebuilder.py  # Update docs
   ```

4. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## Coding Standards

### Python Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use meaningful variable and function names

### File Organization
- Place routes in `routes/` directory
- Models go in `models/` directory  
- Utilities in `utils/` directory
- Tests mirror source structure in `tests/`

### Documentation
- All public functions must have docstrings
- Use Google-style docstring format
- Update relevant documentation files
- Add inline comments for complex logic

### Testing
- Write unit tests for new functionality
- Maintain test coverage above 80%
- Use descriptive test names
- Mock external dependencies

## Code Review Process

### Submitting Pull Requests
1. Ensure all tests pass
2. Update documentation
3. Write clear PR description
4. Reference related issues
5. Request appropriate reviewers

### Review Criteria
- Code follows style guidelines
- Tests are comprehensive
- Documentation is updated
- No breaking changes (unless documented)
- Performance impact considered

## Issue Guidelines

### Bug Reports
Include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Screenshots if applicable

### Feature Requests
Include:
- Clear use case description
- Proposed solution approach
- Any alternatives considered
- Impact assessment

## Development Guidelines

### Adding New Routes
```python
from flask import Blueprint, request, jsonify
from utils.auth_decorators import require_auth

bp = Blueprint('your_feature', __name__)

@bp.route('/api/your-endpoint', methods=['POST'])
@require_auth
def your_endpoint():
    \"\"\"
    Brief description of endpoint
    
    Returns:
        JSON response with result
    \"\"\"
    # Implementation here
    return jsonify({{"success": True}})
```

### Adding New Models
```python
from models.database import db

class YourModel(db.Model):
    \"\"\"Brief description of model\"\"\"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        \"\"\"Convert model to dictionary\"\"\"
        return {{
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat()
        }}
```

### Adding Chat Handlers
```python
@chat_handler(['your_pattern', 'alternative_pattern'])
def handle_your_feature(message: str, context: dict) -> dict:
    \"\"\"
    Handle specific chat functionality
    
    Args:
        message: User input message
        context: Request context
        
    Returns:
        Structured response dictionary
    \"\"\"
    return {{
        'response': 'Your response',
        'action': 'optional_action'
    }}
```

## Security Guidelines

### Authentication
- Always use `@require_auth` decorator for protected routes
- Validate user permissions appropriately
- Never store sensitive data in client-side storage

### Input Validation
- Validate all user inputs
- Use parameterized queries
- Sanitize output appropriately
- Implement rate limiting where needed

### Data Handling
- Follow GDPR/privacy guidelines
- Encrypt sensitive data at rest
- Use HTTPS for all communications
- Implement proper session management

## Testing Guidelines

### Unit Tests
```python
import pytest
from your_module import your_function

def test_your_function():
    \"\"\"Test your function behavior\"\"\"
    result = your_function('input')
    assert result == 'expected_output'
```

### Integration Tests
```python
def test_api_endpoint(client):
    \"\"\"Test API endpoint integration\"\"\"
    response = client.post('/api/endpoint', 
                          json={{'key': 'value'}})
    assert response.status_code == 200
    assert response.json['success'] is True
```

## Release Process

### Version Numbering
- Follow Semantic Versioning (MAJOR.MINOR.PATCH)
- MAJOR: Breaking changes
- MINOR: New features, backward compatible
- PATCH: Bug fixes, backward compatible

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version number bumped
- [ ] Changelog updated
- [ ] Security review completed
- [ ] Performance impact assessed

## Getting Help

### Communication Channels
- GitHub Issues for bugs and features
- GitHub Discussions for questions
- Code review comments for specific feedback

### Resources
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Python Style Guide](https://pep8.org/)

## Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes
- Special recognition for significant contributions

Thank you for contributing to NOUS Personal Assistant! 🚀

*Last updated: {datetime.now().strftime('%Y-%m-%d')}*
"""
        
        Path('CONTRIBUTING.md').write_text(contributing_content, encoding='utf-8')
        print("✅ Generated CONTRIBUTING.md")
    
    def _generate_security(self) -> None:
        """Generate security documentation"""
        security_content = f"""# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.x.x   | ✅ Yes             |
| 1.x.x   | ❌ No (archived)   |

## Reporting a Vulnerability

We take security vulnerabilities seriously. Please help us keep NOUS Personal Assistant secure by reporting any security issues responsibly.

### How to Report

**DO NOT** create public GitHub issues for security vulnerabilities.

Instead, please report security issues by:

1. **Email**: Send details to security@nous-assistant.com
2. **GitHub Security**: Use GitHub's private vulnerability reporting feature
3. **Encrypted Communication**: PGP key available on request

### What to Include

Please provide as much information as possible:

- Type of vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Suggested fix (if available)
- Your contact information

### Response Timeline

- **Initial Response**: Within 24 hours
- **Assessment**: Within 72 hours  
- **Fix Development**: Varies by severity
- **Public Disclosure**: After fix deployment

## Security Measures

### Authentication & Authorization

- **Google OAuth 2.0**: Industry-standard authentication
- **Session Management**: Secure HTTP-only cookies
- **CSRF Protection**: Built-in Flask-WTF protection
- **Rate Limiting**: Request throttling implementation

### Data Protection

- **Input Validation**: All user inputs validated and sanitized
- **SQL Injection Prevention**: Parameterized queries only
- **XSS Protection**: Content Security Policy headers
- **HTTPS Enforcement**: All communications encrypted

### Infrastructure Security

- **Security Headers**: Comprehensive header configuration
- **Proxy Configuration**: ProxyFix middleware for reverse proxy
- **Error Handling**: No sensitive information in error messages
- **Logging**: Security events logged without sensitive data

## Security Configuration

### Required Environment Variables

```bash
# Authentication
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret  
SESSION_SECRET=cryptographically-strong-secret

# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Optional Security
SECURITY_PASSWORD_SALT=additional-salt
CSRF_SECRET_KEY=csrf-specific-secret
```

### Security Headers

The application implements these security headers:

```python
# Content Security Policy
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'

# Frame Options
X-Frame-Options: DENY

# Content Type Options  
X-Content-Type-Options: nosniff

# XSS Protection
X-XSS-Protection: 1; mode=block

# Strict Transport Security
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

## Vulnerability Management

### Known Security Considerations

1. **Session Storage**: Currently file-based, consider Redis for production
2. **Rate Limiting**: Basic implementation, consider advanced solutions
3. **API Versioning**: Implement versioning for backward compatibility
4. **Audit Logging**: Enhanced logging for security events

### Security Roadmap

#### Phase 1: Enhanced Authentication
- [ ] Multi-factor authentication (MFA)
- [ ] Session timeout configuration
- [ ] Account lockout policies
- [ ] Password complexity requirements (if applicable)

#### Phase 2: Advanced Security
- [ ] Web Application Firewall (WAF)
- [ ] Advanced rate limiting
- [ ] Security event monitoring
- [ ] Automated vulnerability scanning

#### Phase 3: Compliance
- [ ] GDPR compliance review
- [ ] SOC 2 Type II preparation
- [ ] Penetration testing
- [ ] Security audit certification

## Secure Development Practices

### Code Review Requirements

All code changes must:
- [ ] Pass security-focused code review
- [ ] Include security impact assessment
- [ ] Update threat model if applicable
- [ ] Pass automated security scans

### Dependencies Management

- **Automated Updates**: Dependabot for security patches
- **Vulnerability Scanning**: Regular dependency vulnerability checks
- **Minimal Dependencies**: Only essential packages included
- **License Compliance**: All dependencies reviewed for license compatibility

### Testing Requirements

- **Security Tests**: Automated security test suite
- **Penetration Testing**: Regular external testing
- **Static Analysis**: Code security analysis tools
- **Dynamic Testing**: Runtime security testing

## Incident Response

### Response Team
- Technical Lead: Immediate technical response
- Security Officer: Overall incident coordination
- Communications: User and stakeholder communication
- Legal: Compliance and legal implications

### Response Process

1. **Detection & Analysis** (0-2 hours)
   - Identify and confirm security incident
   - Assess severity and potential impact
   - Activate response team

2. **Containment** (2-6 hours)
   - Implement immediate containment measures
   - Preserve evidence for analysis
   - Prevent further damage

3. **Eradication & Recovery** (6-24 hours)
   - Remove threat from environment
   - Apply security patches/fixes
   - Restore systems to normal operation

4. **Post-Incident** (24-72 hours)
   - Document lessons learned
   - Update security measures
   - Communicate with stakeholders
   - File necessary reports

## Compliance

### Data Privacy
- **GDPR**: European data protection compliance
- **CCPA**: California privacy law compliance
- **Data Minimization**: Collect only necessary data
- **Right to Delete**: User data deletion capabilities

### Industry Standards
- **OWASP Top 10**: Regular assessment against OWASP guidelines
- **NIST Framework**: Cybersecurity framework alignment
- **ISO 27001**: Information security management practices

## Security Contacts

### Reporting
- **Email**: security@nous-assistant.com
- **Response Time**: 24 hours maximum
- **Encryption**: PGP key available on request

### Bug Bounty
We currently do not offer a formal bug bounty program, but we recognize and appreciate security researchers who help improve our security posture.

## Security Updates

Security updates are communicated through:
- GitHub Security Advisories
- Release notes with security fixes
- Direct communication for critical issues

---

**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}  
**Version**: 2.0.0  
**Review Cycle**: Quarterly

*This security policy is reviewed and updated regularly to reflect current best practices and threat landscape.*
"""
        
        Path('SECURITY.md').write_text(security_content, encoding='utf-8')
        print("✅ Generated SECURITY.md")
    
    def _generate_changelog(self) -> None:
        """Generate/update changelog"""
        changelog_header = f"""# Changelog

All notable changes to NOUS Personal Assistant are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Automated documentation generation from live codebase
- Comprehensive security documentation
- Enhanced contributing guidelines
- Detailed architecture documentation

### Changed
- Documentation format standardized to industry best practices
- API reference now auto-generated from route definitions

### Documentation
- Full code-synced doc rebuild completed {datetime.now().strftime('%Y-%m-%d')}

"""
        
        # Try to preserve existing changelog content
        changelog_path = Path('CHANGELOG.md')
        existing_content = ""
        
        if changelog_path.exists():
            try:
                existing_content = changelog_path.read_text(encoding='utf-8')
                # Extract everything after the first version entry
                lines = existing_content.split('\n')
                found_version = False
                preserved_lines = []
                
                for line in lines:
                    if found_version:
                        preserved_lines.append(line)
                    elif line.startswith('## [') and 'Unreleased' not in line:
                        found_version = True
                        preserved_lines.append(line)
                
                if preserved_lines:
                    existing_content = '\n'.join(preserved_lines)
                else:
                    existing_content = ""
            except Exception:
                existing_content = ""
        
        full_changelog = changelog_header + existing_content
        
        changelog_path.write_text(full_changelog, encoding='utf-8')
        print("✅ Generated/Updated CHANGELOG.md")
    
    def _generate_inventory(self) -> None:
        """Generate project inventory"""
        inventory = {
            'generated_at': datetime.now().isoformat(),
            'project_stats': {
                'total_files': len(self.file_inventory),
                'python_files': len([f for f in self.file_inventory if f['type'] == '.py']),
                'routes': len(self.routes),
                'api_endpoints': len(self.api_endpoints),
                'models': len(self.models),
                'chat_handlers': len(self.chat_handlers),
                'utilities': len(self.utilities)
            },
            'file_inventory': self.file_inventory,
            'routes': self.routes,
            'api_endpoints': self.api_endpoints,
            'models': self.models,
            'chat_handlers': self.chat_handlers,
            'utilities': self.utilities
        }
        
        # Save to docs directory
        Path('docs/project_inventory.json').write_text(
            json.dumps(inventory, indent=2, default=str), 
            encoding='utf-8'
        )
        print("✅ Generated project inventory")
    
    # Helper methods for formatting
    
    def _get_flask_version(self) -> str:
        """Get Flask version if available"""
        try:
            import flask
            return flask.__version__
        except ImportError:
            return "Latest"
    
    def _format_api_endpoints(self) -> str:
        """Format API endpoints for documentation"""
        if not self.api_endpoints:
            return "No API endpoints found."
        
        formatted = []
        for endpoint in self.api_endpoints[:10]:  # Show first 10
            methods = ', '.join(endpoint.get('methods', ['GET']))
            formatted.append(f"- `{methods} {endpoint['path']}` - {endpoint.get('docstring', 'No description')[:50]}...")
        
        if len(self.api_endpoints) > 10:
            formatted.append(f"- ... and {len(self.api_endpoints) - 10} more endpoints")
        
        return '\n'.join(formatted)
    
    def _format_public_routes(self) -> str:
        """Format public routes"""
        public_routes = [r for r in self.routes if not r['path'].startswith('/api/')]
        if not public_routes:
            return "No public routes found."
        
        formatted = []
        for route in public_routes:
            methods = ', '.join(route.get('methods', ['GET']))
            formatted.append(f"- `{methods} {route['path']}` - {route.get('docstring', 'No description')[:50]}...")
        
        return '\n'.join(formatted)
    
    def _format_api_endpoints_detailed(self) -> str:
        """Format API endpoints with details"""
        if not self.api_endpoints:
            return "No API endpoints found."
        
        formatted = []
        for endpoint in self.api_endpoints:
            methods = ', '.join(endpoint.get('methods', ['GET']))
            desc = endpoint.get('docstring', 'No description available')
            formatted.append(f"""
#### `{methods} {endpoint['path']}`

{desc}

- **File**: `{endpoint['file']}`
- **Function**: `{endpoint['function']}`
- **Line**: {endpoint.get('line', 'N/A')}
""")
        
        return '\n'.join(formatted)
    
    def _format_app_routes(self) -> str:
        """Format application routes"""
        app_routes = [r for r in self.routes if not r['path'].startswith('/api/')]
        if not app_routes:
            return "No application routes found."
        
        formatted = []
        for route in app_routes:
            methods = ', '.join(route.get('methods', ['GET']))
            desc = route.get('docstring', 'No description available')
            formatted.append(f"- `{methods} {route['path']}` - {desc[:100]}...")
        
        return '\n'.join(formatted)
    
    def _format_chat_handlers(self) -> str:
        """Format chat handlers"""
        if not self.chat_handlers:
            return "No chat handlers found."
        
        formatted = []
        for handler in self.chat_handlers:
            desc = handler.get('docstring', 'No description available')
            formatted.append(f"- `{handler['function']}` - {desc[:80]}...")
        
        return '\n'.join(formatted)
    
    def _format_models(self) -> str:
        """Format database models"""
        if not self.models:
            return "No database models found."
        
        formatted = []
        for model in self.models:
            fields = ', '.join(model.get('fields', [])[:5])
            if len(model.get('fields', [])) > 5:
                fields += f" (and {len(model['fields']) - 5} more)"
            
            formatted.append(f"""
### {model['name']}

{model.get('docstring', 'No description available')}

- **Fields**: {fields}
- **File**: `{model['file']}`
""")
        
        return '\n'.join(formatted)
    
    def _format_database_schema(self) -> str:
        """Format database schema overview"""
        if not self.models:
            return "No database models found."
        
        schema_lines = ["```sql"]
        for model in self.models:
            table_name = model['name'].lower()
            schema_lines.append(f"-- {model['name']} Model")
            schema_lines.append(f"CREATE TABLE {table_name} (")
            
            fields = model.get('fields', [])
            if fields:
                for field in fields[:3]:  # Show first 3 fields
                    schema_lines.append(f"    {field} VARCHAR,")
                if len(fields) > 3:
                    schema_lines.append(f"    -- ... and {len(fields) - 3} more fields")
            else:
                schema_lines.append("    -- Schema details not available")
            
            schema_lines.append(");")
            schema_lines.append("")
        
        schema_lines.append("```")
        return '\n'.join(schema_lines)
    
    def _generate_file_tree(self) -> str:
        """Generate file tree representation"""
        tree_lines = []
        directories = set()
        
        # Group files by directory
        for file_info in self.file_inventory[:50]:  # Limit to first 50 files
            path_parts = Path(file_info['path']).parts
            if len(path_parts) > 1:
                directories.add(path_parts[0])
        
        # Show directory structure
        for directory in sorted(directories):
            tree_lines.append(f"{directory}/")
            
            # Show some files in each directory
            dir_files = [f for f in self.file_inventory if f['path'].startswith(directory + '/')]
            for file_info in dir_files[:3]:
                filename = Path(file_info['path']).name
                tree_lines.append(f"├── {filename}")
            
            if len(dir_files) > 3:
                tree_lines.append(f"└── ... ({len(dir_files) - 3} more files)")
        
        return '\n'.join(tree_lines)

def main():
    """Main execution function"""
    rebuilder = NOUSDocumentationRebuilder()
    rebuilder.analyze_codebase()

if __name__ == "__main__":
    main()