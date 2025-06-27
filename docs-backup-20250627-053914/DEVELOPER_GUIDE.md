# NOUS Developer Guide

This guide provides instructions for setting up the NOUS development environment, understanding the architecture, and contributing to the project.

## Table of Contents
1. [Environment Setup](#environment-setup)
2. [Project Structure](#project-structure)
3. [Running the Application](#running-the-application)
4. [Testing](#testing)
5. [Working with the Database](#working-with-the-database)
6. [API Integration](#api-integration)
7. [Development Workflow](#development-workflow)
8. [Code Style Guide](#code-style-guide)
9. [Troubleshooting](#troubleshooting)

## Environment Setup

### Prerequisites
- Python 3.9+ 
- PostgreSQL 13+
- Redis (optional, for production caching)

### Setting Up the Development Environment

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/nous.git
   cd nous
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements_dev.txt  # Install development dependencies
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root with the following variables:
   ```
   # Required Environment Variables
   DATABASE_URL=postgresql://username:password@localhost:5432/nous
   FLASK_SECRET=your_secure_secret_key
   SESSION_SECRET=another_secure_secret_key
   
   # OAuth Configuration
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   GOOGLE_REDIRECT_URI=http://localhost:5000/callback/google
   
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   SPOTIFY_REDIRECT_URI=http://localhost:5000/callback/spotify
   
   # AI Service Configuration
   OPENROUTER_API_KEY=your_openrouter_api_key
   
   # Optional Configuration
   REDIS_URL=redis://localhost:6379/0
   ENABLE_BETA_MODE=true
   BETA_ACCESS_CODE=BETANOUS2025
   MAX_BETA_TESTERS=30
   ```

5. **Set up the database**
   ```bash
   # Create a PostgreSQL database
   createdb nous
   
   # Initialize the database schema
   flask db upgrade
   ```

## Project Structure

The NOUS codebase is organized as follows:

```
nous/
├── app.py                 # Main Flask application
├── models.py              # SQLAlchemy models
├── routes/                # API route blueprints
├── utils/                 # Utility modules
├── templates/             # HTML templates
├── static/                # Static assets (CSS, JS, images)
├── tests/                 # Unit and integration tests
├── migrations/            # Database migration scripts
├── cache/                 # Cache files (when using file cache)
├── docs/                  # Documentation
└── requirements.txt       # Project dependencies
```

### Key Components:

- **app.py**: Main Flask application with route definitions
- **models.py**: Database models for SQLAlchemy
- **utils/**: Utility modules for various functions
  - **cache_helper.py**: Caching system for improved performance
  - **security_helper.py**: Security functions for authentication and protection
  - **ai_helper.py**: AI service integration
  - **knowledge_helper.py**: Knowledge base management
- **routes/**: Blueprints for API routes
- **tests/**: Test modules organized by component

## Running the Application

1. **Development Server**
   ```bash
   python main.py
   ```
   This will start the Flask development server at http://localhost:5000

2. **Production Deployment**
   ```bash
   python deploy.py
   ```
   This runs the deployment script that validates the environment and runs migrations.

## Testing

The project uses pytest for testing. Tests are located in the `tests/` directory.

1. **Running All Tests**
   ```bash
   python run_tests.py
   ```

2. **Running with Coverage**
   ```bash
   python run_tests.py --html
   ```
   This generates an HTML coverage report in the `htmlcov/` directory.

3. **Running Specific Tests**
   ```bash
   python -m pytest tests/test_security_helper.py
   ```

## Working with the Database

### Migrations

Database migrations are handled using Flask-Migrate (Alembic).

1. **Creating a Migration**
   ```bash
   flask db migrate -m "Description of changes"
   ```

2. **Applying Migrations**
   ```bash
   flask db upgrade
   ```

3. **Reverting Migrations**
   ```bash
   flask db downgrade
   ```

### Model Relationships

The database schema is defined in `models.py`. Key relationships include:

- User → UserSettings (one-to-one)
- User → UserMemoryEntry (one-to-many)
- User → UserTopicInterest (one-to-many)
- User → UserEntityMemory (one-to-many)

## API Integration

### OAuth Setup

1. **Google OAuth**:
   - Create a project in the [Google Developer Console](https://console.developers.google.com/)
   - Configure OAuth consent screen
   - Create OAuth credentials
   - Set the redirect URI to `http://localhost:5000/callback/google`

2. **Spotify OAuth**:
   - Create an app in the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
   - Set the redirect URI to `http://localhost:5000/callback/spotify`

### AI Service Integration

1. **OpenRouter Setup**:
   - Create an account at [OpenRouter](https://openrouter.ai/)
   - Generate an API key
   - Add it to your `.env` file as `OPENROUTER_API_KEY`

## Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and test**
   ```bash
   # Run tests to ensure changes don't break existing functionality
   python run_tests.py
   ```

3. **Commit changes with descriptive messages**
   ```bash
   git commit -m "Add feature: detailed description of changes"
   ```

4. **Push changes and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Style Guide

The project follows PEP 8 style guidelines with the following tools:

- **Black**: Code formatting
  ```bash
  black .
  ```

- **Flake8**: Linting
  ```bash
  flake8 .
  ```

- **isort**: Import sorting
  ```bash
  isort .
  ```

### Documentation Standards

- All modules should have a module-level docstring
- All public functions should have docstrings with parameter descriptions
- Use type hints for function parameters and return values

Example:
```python
def secure_hash(data: str, salt: Optional[bytes] = None) -> str:
    """
    Create a secure hash using SHA-256.
    
    Args:
        data: The string to hash
        salt: Optional salt for the hash
        
    Returns:
        A secure hash string
    """
    # Implementation...
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Verify PostgreSQL is running
   - Check DATABASE_URL environment variable
   - Ensure database user has proper permissions

2. **OAuth Authentication Failures**
   - Verify client IDs and secrets
   - Check that redirect URIs match exactly
   - Ensure OAuth consent screen is configured properly

3. **Redis Connection Issues**
   - Verify Redis is running if using Redis cache
   - Check REDIS_URL environment variable
   - Application will fall back to file cache if Redis is unavailable

### Getting Help

If you encounter issues not covered here, please:
1. Check existing GitHub issues
2. Create a new issue with detailed information about your problem
3. Include environment details and steps to reproduce 