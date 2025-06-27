Development Guide
=================

This guide provides comprehensive information for developers working on NOUS Personal Assistant, including development workflows, coding standards, testing practices, and contribution guidelines.

Development Environment Setup
-----------------------------

Prerequisites
~~~~~~~~~~~~~

* **Python 3.11+**: Core runtime environment
* **PostgreSQL 13+**: Production database (SQLite for development)
* **Git**: Version control
* **Code Editor**: VS Code, PyCharm, or similar with Python support

Quick Setup
~~~~~~~~~~~

.. code-block:: bash

    # Clone repository
    git clone https://github.com/your-username/nous-personal-assistant.git
    cd nous-personal-assistant
    
    # Create and activate virtual environment
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    
    # Install dependencies
    pip install -r requirements.txt
    pip install -r requirements_dev.txt
    
    # Set up environment
    cp .env.example .env
    # Edit .env with your configuration
    
    # Initialize database
    python -c "from app import app, db; app.app_context().push(); db.create_all()"
    
    # Run application
    python main.py

Development Workflow
--------------------

Git Workflow
~~~~~~~~~~~~

We follow a simplified Git flow:

.. code-block:: bash

    # Create feature branch
    git checkout -b feature/your-feature-name
    
    # Make changes
    git add .
    git commit -m "feat: add new feature description"
    
    # Push branch
    git push origin feature/your-feature-name
    
    # Create pull request via GitHub

Commit Message Convention
~~~~~~~~~~~~~~~~~~~~~~~~~

We use conventional commit format:

.. code-block:: text

    type(scope): description
    
    [optional body]
    
    [optional footer]

**Types:**

* ``feat``: New feature
* ``fix``: Bug fix
* ``docs``: Documentation changes
* ``style``: Code formatting changes
* ``refactor``: Code refactoring
* ``test``: Adding or updating tests
* ``chore``: Maintenance tasks

**Examples:**

.. code-block:: text

    feat(auth): add Google OAuth integration
    fix(api): resolve chat endpoint error handling
    docs(api): update API reference documentation
    refactor(utils): optimize database connection pooling

Code Quality Standards
----------------------

Code Style
~~~~~~~~~~

We follow PEP 8 with some modifications:

.. code-block:: python

    # Maximum line length: 88 characters (Black default)
    # Use double quotes for strings
    # Use trailing commas in multi-line structures
    
    # Good example
    def process_chat_message(
        message: str,
        context: Dict[str, Any],
        user_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Process a chat message and return response."""
        return {
            "response": "Generated response",
            "context": updated_context,
            "metadata": {"model": "gemini-pro"},
        }

Type Hints
~~~~~~~~~~

Use type hints for all functions and class methods:

.. code-block:: python

    from typing import Dict, List, Optional, Union, Any
    
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Retrieve user by ID."""
        return User.query.get(user_id)
    
    def process_api_response(
        response: Dict[str, Any]
    ) -> Union[str, Dict[str, Any]]:
        """Process external API response."""
        if response.get("error"):
            return {"error": response["error"]}
        return response.get("data", "")

Documentation Standards
~~~~~~~~~~~~~~~~~~~~~~~

Use Google-style docstrings:

.. code-block:: python

    def calculate_health_score(
        database_latency: float,
        memory_usage: float,
        cpu_usage: float
    ) -> Dict[str, Any]:
        """Calculate system health score based on metrics.
        
        Args:
            database_latency: Database response time in milliseconds
            memory_usage: Memory usage percentage (0-100)
            cpu_usage: CPU usage percentage (0-100)
            
        Returns:
            Dict containing health score and component ratings:
                {
                    "overall_score": 85,
                    "database": "healthy",
                    "memory": "warning",
                    "cpu": "healthy"
                }
                
        Raises:
            ValueError: If any metric is outside valid range
            
        Example:
            >>> calculate_health_score(25.5, 45.0, 12.3)
            {"overall_score": 92, "database": "healthy", ...}
        """
        if not (0 <= memory_usage <= 100):
            raise ValueError("Memory usage must be between 0 and 100")
        
        # Implementation here...

Error Handling
~~~~~~~~~~~~~~

Implement comprehensive error handling:

.. code-block:: python

    import logging
    from typing import Optional
    
    logger = logging.getLogger(__name__)
    
    def safe_api_call(url: str, timeout: int = 30) -> Optional[Dict]:
        """Make API call with comprehensive error handling."""
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error(f"API call timeout: {url}")
            return None
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for {url}: {e.response.status_code}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {str(e)}")
            return None
            
        except ValueError as e:
            logger.error(f"Invalid JSON response from {url}: {str(e)}")
            return None

Testing Guidelines
------------------

Test Structure
~~~~~~~~~~~~~~

Organize tests to mirror the application structure:

.. code-block:: text

    tests/
    ├── __init__.py
    ├── conftest.py              # Pytest configuration and fixtures
    ├── test_app.py              # Main application tests
    ├── test_models.py           # Database model tests
    ├── test_routes.py           # Route handler tests
    ├── test_api.py              # API endpoint tests
    ├── test_utils.py            # Utility function tests
    └── integration/             # Integration tests
        ├── test_auth_flow.py    # Authentication flow tests
        └── test_chat_system.py  # Chat system tests

Test Writing Guidelines
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import pytest
    from app import app, db
    from models.user import User
    
    @pytest.fixture
    def client():
        """Create test client."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                yield client
                db.drop_all()
    
    @pytest.fixture
    def sample_user():
        """Create sample user for testing."""
        user = User(
            email='test@example.com',
            name='Test User',
            google_id='123456789'
        )
        db.session.add(user)
        db.session.commit()
        return user
    
    def test_user_creation(client, sample_user):
        """Test user creation and retrieval."""
        assert sample_user.email == 'test@example.com'
        assert sample_user.name == 'Test User'
        assert User.query.count() == 1
    
    def test_api_health_endpoint(client):
        """Test health check API endpoint."""
        response = client.get('/api/v1/health')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data

Running Tests
~~~~~~~~~~~~~

.. code-block:: bash

    # Run all tests
    pytest
    
    # Run with coverage
    pytest --cov=. --cov-report=html
    
    # Run specific test file
    pytest tests/test_api.py
    
    # Run tests with specific marker
    pytest -m "not slow"
    
    # Verbose output
    pytest -v

Database Development
--------------------

Model Development
~~~~~~~~~~~~~~~~~

Create models following SQLAlchemy best practices:

.. code-block:: python

    from datetime import datetime
    from app import db
    from sqlalchemy.dialects.postgresql import UUID
    import uuid
    
    class BaseModel(db.Model):
        """Base model with common fields."""
        __abstract__ = True
        
        id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
        updated_at = db.Column(
            db.DateTime, 
            default=datetime.utcnow, 
            onupdate=datetime.utcnow, 
            nullable=False
        )
    
    class User(BaseModel):
        """User model with OAuth integration."""
        __tablename__ = 'users'
        
        email = db.Column(db.String(255), unique=True, nullable=False, index=True)
        name = db.Column(db.String(255))
        google_id = db.Column(db.String(255), unique=True, index=True)
        is_active = db.Column(db.Boolean, default=True, nullable=False)
        last_login = db.Column(db.DateTime)
        
        # Relationships
        feedback = db.relationship('UserFeedback', backref='user', lazy='dynamic')
        
        def __repr__(self):
            return f'<User {self.email}>'
        
        def to_dict(self):
            """Convert user to dictionary for JSON serialization."""
            return {
                'id': str(self.id),
                'email': self.email,
                'name': self.name,
                'is_active': self.is_active,
                'created_at': self.created_at.isoformat(),
                'last_login': self.last_login.isoformat() if self.last_login else None
            }

Migration Strategy
~~~~~~~~~~~~~~~~~~

While we use ``db.create_all()`` for simplicity, consider Flask-Migrate for production:

.. code-block:: bash

    # Initialize migrations (one time)
    flask db init
    
    # Create migration
    flask db migrate -m "Add user table"
    
    # Apply migration
    flask db upgrade
    
    # Downgrade if needed
    flask db downgrade

Query Optimization
~~~~~~~~~~~~~~~~~~

Write efficient database queries:

.. code-block:: python

    # Good: Use eager loading to avoid N+1 queries
    users_with_feedback = User.query.options(
        db.joinedload(User.feedback)
    ).filter(User.is_active == True).all()
    
    # Good: Use pagination for large datasets
    def get_users_paginated(page: int = 1, per_page: int = 20):
        return User.query.filter(User.is_active == True).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
    
    # Good: Use database-level filtering
    recent_users = User.query.filter(
        User.created_at >= datetime.utcnow() - timedelta(days=30)
    ).count()

API Development
---------------

Endpoint Design
~~~~~~~~~~~~~~~

Follow RESTful conventions:

.. code-block:: python

    from flask import Blueprint, request, jsonify
    from utils.auth import require_auth, get_current_user
    
    api_bp = Blueprint('api', __name__, url_prefix='/api')
    
    @api_bp.route('/user', methods=['GET'])
    @require_auth
    def get_current_user_info():
        """Get current authenticated user information."""
        try:
            user = get_current_user()
            return jsonify({
                'data': user.to_dict(),
                'status': 'success'
            })
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'USER_FETCH_ERROR',
                    'message': 'Failed to retrieve user information'
                },
                'status': 'error'
            }), 500
    
    @api_bp.route('/feedback', methods=['POST'])
    @require_auth
    def submit_feedback():
        """Submit user feedback."""
        try:
            data = request.get_json()
            
            # Validate input
            if not data or not data.get('message'):
                return jsonify({
                    'error': {
                        'code': 'INVALID_INPUT',
                        'message': 'Feedback message is required'
                    },
                    'status': 'error'
                }), 400
            
            # Create feedback record
            feedback = UserFeedback(
                user_id=get_current_user().id,
                feedback_type=data.get('type', 'general'),
                message=data['message'],
                rating=data.get('rating'),
                metadata=data.get('metadata', {})
            )
            
            db.session.add(feedback)
            db.session.commit()
            
            return jsonify({
                'data': {'id': str(feedback.id)},
                'status': 'success'
            }), 201
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Feedback submission error: {str(e)}")
            return jsonify({
                'error': {
                    'code': 'FEEDBACK_SUBMISSION_ERROR',
                    'message': 'Failed to submit feedback'
                },
                'status': 'error'
            }), 500

Input Validation
~~~~~~~~~~~~~~~~

Validate all API inputs:

.. code-block:: python

    from marshmallow import Schema, fields, validate, ValidationError
    
    class FeedbackSchema(Schema):
        """Schema for feedback validation."""
        type = fields.Str(
            validate=validate.OneOf(['bug_report', 'feature_request', 'general']),
            missing='general'
        )
        message = fields.Str(required=True, validate=validate.Length(min=1, max=1000))
        rating = fields.Int(validate=validate.Range(min=1, max=5))
        metadata = fields.Dict()
    
    @api_bp.route('/feedback', methods=['POST'])
    @require_auth
    def submit_feedback():
        """Submit user feedback with validation."""
        schema = FeedbackSchema()
        
        try:
            data = schema.load(request.get_json() or {})
        except ValidationError as e:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Invalid input data',
                    'details': e.messages
                },
                'status': 'error'
            }), 400
        
        # Process valid data...

Frontend Development
--------------------

JavaScript Standards
~~~~~~~~~~~~~~~~~~~~

Use modern JavaScript with consistent style:

.. code-block:: javascript

    // Good: Use const/let, arrow functions, async/await
    const ChatInterface = {
        async sendMessage(message) {
            try {
                const response = await fetch('/api/v1/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify({ message })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                this.displayResponse(data.response);
                
            } catch (error) {
                console.error('Chat error:', error);
                this.displayError('Failed to send message. Please try again.');
            }
        },
        
        displayResponse(response) {
            const chatContainer = document.getElementById('chat-messages');
            const messageElement = document.createElement('div');
            messageElement.className = 'message ai-message';
            messageElement.textContent = response;
            chatContainer.appendChild(messageElement);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        },
        
        getCSRFToken() {
            return document.querySelector('meta[name=csrf-token]')?.getAttribute('content');
        }
    };

CSS Architecture
~~~~~~~~~~~~~~~~

Use consistent CSS methodology:

.. code-block:: css

    /* Use BEM methodology for CSS classes */
    .chat-interface {
        display: flex;
        flex-direction: column;
        height: 100vh;
    }
    
    .chat-interface__header {
        padding: 1rem;
        border-bottom: 1px solid var(--border-color);
        background: var(--header-bg);
    }
    
    .chat-interface__messages {
        flex: 1;
        overflow-y: auto;
        padding: 1rem;
    }
    
    .message {
        margin-bottom: 1rem;
        padding: 0.75rem;
        border-radius: 0.5rem;
        max-width: 80%;
    }
    
    .message--user {
        background: var(--user-message-bg);
        margin-left: auto;
        text-align: right;
    }
    
    .message--ai {
        background: var(--ai-message-bg);
        margin-right: auto;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .message {
            max-width: 95%;
        }
        
        .chat-interface__header {
            padding: 0.5rem;
        }
    }

Performance Optimization
------------------------

Database Performance
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Use database indexes
    class User(db.Model):
        email = db.Column(db.String(255), unique=True, nullable=False, index=True)
        google_id = db.Column(db.String(255), unique=True, index=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Use query optimization
    def get_active_users_with_recent_activity():
        """Optimized query for active users."""
        return db.session.query(User).filter(
            User.is_active == True,
            User.last_login >= datetime.utcnow() - timedelta(days=30)
        ).options(
            db.load_only(User.id, User.email, User.name, User.last_login)
        ).limit(100).all()

Caching Strategy
~~~~~~~~~~~~~~~~

.. code-block:: python

    from functools import lru_cache
    import time
    
    # Simple in-memory caching
    @lru_cache(maxsize=128)
    def get_feature_flag_cached(flag_name: str) -> bool:
        """Get feature flag with caching."""
        flag = FeatureFlag.query.filter_by(name=flag_name).first()
        return flag.enabled if flag else False
    
    # Time-based cache invalidation
    class TimedCache:
        def __init__(self, ttl_seconds: int = 300):
            self.cache = {}
            self.ttl = ttl_seconds
        
        def get(self, key: str):
            if key in self.cache:
                value, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl:
                    return value
                del self.cache[key]
            return None
        
        def set(self, key: str, value):
            self.cache[key] = (value, time.time())

Debugging and Logging
---------------------

Logging Configuration
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import logging
    import sys
    from datetime import datetime
    
    def setup_logging(app):
        """Configure application logging."""
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        simple_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        
        # File handler
        file_handler = logging.FileHandler(f'logs/app_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Configure app logger
        app.logger.setLevel(logging.DEBUG)
        app.logger.addHandler(console_handler)
        app.logger.addHandler(file_handler)

Debug Utilities
~~~~~~~~~~~~~~~

.. code-block:: python

    import functools
    import time
    
    def debug_timing(func):
        """Decorator to measure function execution time."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            if duration > 0.1:  # Log slow functions
                logging.warning(f"{func.__name__} took {duration:.3f}s")
            
            return result
        return wrapper
    
    def debug_api_call(url: str, method: str = 'GET', **kwargs):
        """Debug utility for API calls."""
        logging.debug(f"API Call: {method} {url}")
        logging.debug(f"Parameters: {kwargs}")
        
        start_time = time.time()
        response = requests.request(method, url, **kwargs)
        duration = time.time() - start_time
        
        logging.debug(f"Response: {response.status_code} in {duration:.3f}s")
        return response

Contributing Guidelines
-----------------------

Pull Request Process
~~~~~~~~~~~~~~~~~~~~

1. **Branch Naming**: Use descriptive branch names
   
   .. code-block:: bash
   
       feature/add-chat-history
       bugfix/fix-oauth-redirect
       docs/update-api-reference

2. **Commit Quality**: Write clear, descriptive commits

3. **Testing**: Ensure all tests pass

4. **Documentation**: Update relevant documentation

5. **Code Review**: Address all review comments

Code Review Checklist
~~~~~~~~~~~~~~~~~~~~~~

**Functionality:**

* ✅ Code works as intended
* ✅ Handles edge cases appropriately
* ✅ Error handling is comprehensive
* ✅ Performance considerations addressed

**Code Quality:**

* ✅ Follows project coding standards
* ✅ Functions are appropriately sized
* ✅ Variable names are descriptive
* ✅ Comments explain complex logic

**Testing:**

* ✅ Unit tests cover new functionality
* ✅ Integration tests pass
* ✅ Edge cases are tested
* ✅ Test coverage maintained

**Documentation:**

* ✅ Function docstrings updated
* ✅ API documentation current
* ✅ README updated if needed
* ✅ Architecture docs updated

Development Tools
-----------------

Recommended VS Code Extensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Python**: Microsoft Python extension
* **Pylance**: Enhanced Python language server
* **Black Formatter**: Code formatting
* **autoDocstring**: Generate docstrings
* **GitLens**: Git integration
* **Thunder Client**: API testing

Useful Scripts
~~~~~~~~~~~~~~

Create helpful development scripts:

.. code-block:: bash

    #!/bin/bash
    # scripts/dev-setup.sh
    
    echo "Setting up development environment..."
    
    # Create virtual environment
    python -m venv venv
    source venv/bin/activate
    
    # Install dependencies
    pip install -r requirements.txt
    pip install -r requirements_dev.txt
    
    # Set up pre-commit hooks
    pre-commit install
    
    # Initialize database
    python -c "from app import app, db; app.app_context().push(); db.create_all()"
    
    echo "Development environment ready!"

.. code-block:: bash

    #!/bin/bash
    # scripts/test-all.sh
    
    echo "Running full test suite..."
    
    # Code formatting
    black --check .
    
    # Linting
    flake8 .
    
    # Security scan
    bandit -r .
    
    # Type checking
    mypy .
    
    # Unit tests
    pytest --cov=. --cov-report=html
    
    echo "All tests completed!"

This development guide provides the foundation for maintaining code quality, consistency, and developer productivity on the NOUS Personal Assistant project.