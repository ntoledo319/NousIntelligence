# Development Guide

## Setup Development Environment

### Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Redis 6+ (optional)

### Quick Setup

```bash
# Clone and setup
git clone https://github.com/nous/platform.git
cd platform
make dev-setup
```

### Manual Setup

```bash
# Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt

# Database
createdb nous_dev
flask db upgrade

# Frontend
npm install
npm run dev
```

## Development Workflow

### Code Style

We use Black, isort, and flake8 for code formatting:

```bash
make format  # Format code
make lint    # Check code quality
```

### Testing

```bash
make test           # Run all tests
make test-unit      # Unit tests only
make test-integration  # Integration tests
make coverage       # Generate coverage report
```

### Database

```bash
flask db migrate -m "Description"  # Create migration
flask db upgrade                   # Apply migrations
flask db downgrade                 # Rollback migration
```

### Frontend Development

```bash
npm run dev     # Development build with watch
npm run build   # Production build
npm run lint    # Lint JavaScript
```

## Project Structure

```
nous/
├── src/                    # Application source code
│   ├── application/        # Application services
│   ├── domain/            # Domain models and repositories
│   ├── infrastructure/    # Infrastructure code
│   └── presentation/      # API endpoints and views
├── tests/                 # Test suite
├── docs/                  # Documentation
├── static/               # Frontend assets
├── templates/            # HTML templates
└── migrations/           # Database migrations
```

## Common Tasks

### Adding a New Feature

1. Create feature branch
2. Add tests first (TDD)
3. Implement feature
4. Update documentation
5. Submit PR

### Adding API Endpoint

1. Create in `src/presentation/api/`
2. Add tests in `tests/test_api_endpoints.py`
3. Update OpenAPI spec
4. Add integration tests

### Database Changes

1. Create migration: `flask db migrate`
2. Review migration file
3. Test migration: `flask db upgrade`
4. Update models and tests

## Debugging

### Flask Debug Mode

```bash
FLASK_ENV=development flask run --debugger
```

### Database Debugging

```bash
# SQL logging
SQLALCHEMY_ECHO=True flask run

# Database shell
flask shell
>>> from models import User
>>> User.query.all()
```

### Frontend Debugging

- Use browser dev tools
- Check webpack output
- Enable source maps in development

## Performance

### Profiling

```bash
# Profile endpoint
flask profile /api/users

# Memory profiling
memory_profiler flask run
```

### Database Performance

- Use `explain analyze` for slow queries
- Monitor with `pg_stat_statements`
- Add indexes for common queries

## Deployment

### Local Docker

```bash
docker-compose up -d
```

### Staging

```bash
make deploy-staging
```

### Production

```bash
make deploy-production
```
