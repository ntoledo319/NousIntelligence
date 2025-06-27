# Contributing to NOUS Personal Assistant

We welcome contributions to NOUS Personal Assistant! This document outlines the process for contributing to this project.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Node.js 20 or higher (for development tools)
- PostgreSQL (for production) or SQLite (for development)
- Git

### Development Setup

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/your-username/nous-personal-assistant.git
   cd nous-personal-assistant
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements_dev.txt
   ```

3. **Set Up Environment Variables**
   Create a `.env` file with required environment variables:
   ```bash
   SESSION_SECRET=your-session-secret
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   DATABASE_URL=sqlite:///instance/nous.db
   ```

4. **Run the Application**
   ```bash
   python main.py
   ```

## Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use type hints where possible
- Write comprehensive docstrings for all functions and classes
- Use meaningful variable and function names

### Code Quality Tools

We use several tools to maintain code quality:

- **Flake8**: Code style and syntax checking
- **Bandit**: Security vulnerability scanning
- **pytest**: Unit testing framework
- **Sphinx**: Documentation generation

Run quality checks before submitting:
```bash
# Style checking
flake8 .

# Security scanning
bandit -r .

# Run tests
pytest

# Generate documentation
cd docs && sphinx-build -b html . _build/html
```

### Commit Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes (no functional changes)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Example:
```bash
git commit -m "feat: add new chat intent recognition system"
git commit -m "fix: resolve authentication loop on Replit deployment"
git commit -m "docs: update API documentation with new endpoints"
```

## Contributing Process

### 1. Create an Issue

Before starting work, create an issue to discuss:
- Bug reports with reproduction steps
- Feature requests with use cases
- Documentation improvements
- Performance enhancements

### 2. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
git checkout -b fix/issue-description
git checkout -b docs/documentation-update
```

### 3. Make Your Changes

- Write clear, concise code
- Add tests for new functionality
- Update documentation as needed
- Ensure all quality checks pass

### 4. Test Your Changes

```bash
# Run the full test suite
pytest

# Test with different Python versions if possible
python3.11 -m pytest
python3.12 -m pytest

# Manual testing
python main.py
# Test the application thoroughly
```

### 5. Submit a Pull Request

1. **Push your branch:**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request** with:
   - Clear title and description
   - Reference to related issues
   - Screenshots for UI changes
   - Test results and coverage information

3. **Respond to feedback** and make requested changes

## Architecture Guidelines

### Flask Application Structure

```
├── app.py                 # Main application factory
├── main.py               # Application entry point
├── models/               # Database models
├── routes/               # Route blueprints
├── utils/                # Utility functions and helpers
├── templates/            # Jinja2 templates
├── static/               # CSS, JavaScript, images
├── tests/                # Test files
└── docs/                 # Documentation
```

### Database Considerations

- Use SQLAlchemy ORM for all database operations
- Create migrations for schema changes
- Never commit sensitive data or credentials
- Use connection pooling for production deployments

### API Design

- Follow RESTful conventions
- Use appropriate HTTP status codes
- Include comprehensive error handling
- Document all endpoints with OpenAPI/Swagger

### Security

- Never hardcode secrets or API keys
- Use environment variables for configuration
- Implement proper input validation
- Follow OWASP security guidelines

## Documentation

### Code Documentation

- All functions and classes must have docstrings
- Use Google-style docstrings
- Include type hints for parameters and return values
- Document complex algorithms and business logic

Example:
```python
def process_chat_message(message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a chat message and generate an AI response.
    
    Args:
        message: The user's input message
        context: Additional context for the conversation
        
    Returns:
        Dictionary containing the AI response and metadata
        
    Raises:
        ValueError: If message is empty or invalid
        APIError: If AI service is unavailable
    """
```

### API Documentation

- Use OpenAPI 3.1 specifications
- Include request/response examples
- Document authentication requirements
- Provide error response formats

## Testing

### Test Coverage

- Aim for 80%+ test coverage
- Write unit tests for utility functions
- Integration tests for API endpoints
- End-to-end tests for critical user flows

### Test Structure

```python
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'
```

## Performance Guidelines

- Profile performance-critical code
- Use database indexing appropriately
- Implement caching for expensive operations
- Monitor response times and memory usage

## Security Guidelines

- Never commit secrets to version control
- Use environment variables for sensitive configuration
- Implement proper input validation and sanitization
- Follow secure coding practices
- Regular security audits with Bandit

## Release Process

1. **Version Bumping**: Update version in `pyproject.toml`
2. **Changelog**: Update `CHANGELOG.md` with new features and fixes
3. **Testing**: Ensure all tests pass and manual testing is complete
4. **Documentation**: Update documentation to reflect changes
5. **Tagging**: Create a git tag for the release
6. **Deployment**: Deploy to production environment

## Getting Help

- **Documentation**: Check the `/docs` directory for comprehensive guides
- **Issues**: Search existing issues or create a new one
- **Discord**: Join our community Discord server (link in README)
- **Email**: Contact the maintainers at support@nous.ai

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

## License

By contributing to NOUS Personal Assistant, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to NOUS Personal Assistant! Your efforts help make this project better for everyone.