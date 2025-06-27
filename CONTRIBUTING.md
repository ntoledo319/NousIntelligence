# Contributing to NOUS Personal Assistant

Thank you for your interest in contributing to NOUS Personal Assistant! This document outlines how to contribute to this project.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a new branch for your feature or bug fix
4. Make your changes
5. Test your changes thoroughly
6. Submit a pull request

## Development Setup

### Prerequisites
- Python 3.11+
- PostgreSQL (or SQLite for development)
- Node.js (for build tools)

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/nous-personal-assistant.git
cd nous-personal-assistant

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize the database
python -c "from app import db; db.create_all()"

# Run the application
python main.py
```

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Write unit tests for new functionality
- Ensure all tests pass before submitting

## Project Structure

```
├── api/                 # API endpoints and chat handlers
├── models/             # Database models
├── routes/             # Web route handlers
├── utils/              # Utility functions and helpers
├── templates/          # HTML templates
├── static/             # CSS, JavaScript, and static assets
├── tests/              # Test files
├── docs/               # Documentation
└── scripts/            # Utility scripts
```

## Types of Contributions

### Bug Reports
- Use the issue template
- Include steps to reproduce
- Provide error messages and logs
- Specify your environment details

### Feature Requests
- Describe the feature clearly
- Explain the use case
- Consider implementation complexity
- Check if it aligns with project goals

### Pull Requests
- Reference related issues
- Include tests for new functionality
- Update documentation as needed
- Follow the code review process

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

For specific test categories:
```bash
# Unit tests
python -m pytest tests/unit/

# Integration tests
python -m pytest tests/integration/

# Smoke tests
python -m pytest tests/smoke_test_suite.py
```

## Documentation

- Update relevant documentation for your changes
- Add docstrings to new functions and classes
- Update the CHANGELOG.md for significant changes
- Consider updating the user guide for user-facing features

## Security

- Report security vulnerabilities privately
- Follow secure coding practices
- Don't commit sensitive information
- Use environment variables for secrets

## Code Review Process

1. All changes require code review
2. At least one approval required
3. All tests must pass
4. Documentation must be updated
5. No merge conflicts

## Release Process

1. Update version numbers
2. Update CHANGELOG.md
3. Create release notes
4. Tag the release
5. Deploy to production

## Community Guidelines

- Be respectful and inclusive
- Follow the Code of Conduct
- Ask questions if unclear
- Help others when possible
- Keep discussions on-topic

## Getting Help

- Check existing issues and documentation
- Ask questions in discussions
- Join our community chat
- Contact maintainers for complex issues

## License

By contributing, you agree that your contributions will be licensed under the MIT License.