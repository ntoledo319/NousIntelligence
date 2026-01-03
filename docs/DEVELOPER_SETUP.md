# NOUS Intelligence Platform - Developer Setup Guide

## Prerequisites

- **Python**: 3.9 or higher
- **Node.js**: 16 or higher
- **PostgreSQL**: 14 or higher
- **Redis** (optional): For caching
- **Git**: For version control

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/your-org/NousIntelligence.git
cd NousIntelligence
```

### 2. Environment Setup

#### Backend (Python)
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Frontend (React)
```bash
# Install Node dependencies
npm install
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb nous_platform

# Run migrations
python -m flask db upgrade
```

### 4. Environment Variables

Copy `.env.example` to `.env` and fill in required values:

```bash
cp .env.example .env
```

**Required variables:**
```bash
# Generate a secure secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Add to .env
SECRET_KEY=<generated-secret>
DATABASE_URL=postgresql://localhost/nous_platform

# Google OAuth (get from Google Cloud Console)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-secret
```

### 5. Start Development Servers

#### Terminal 1 - Backend (Flask)
```bash
source venv/bin/activate
python app.py
# Runs on http://localhost:5000
```

#### Terminal 2 - Frontend (React)
```bash
npm run dev
# Runs on http://localhost:3000
```

## Project Structure

```
NousIntelligence/
├── src/                    # React frontend
│   ├── components/         # Reusable React components
│   ├── pages/             # Page components
│   ├── store/             # Zustand state management
│   ├── router/            # React Router configuration
│   └── theme.ts           # Styled-components theme
├── routes/                # Flask API routes
│   ├── consolidated_routes.py  # Core API endpoints
│   └── therapeutic_routes.py   # CBT/DBT/Mood endpoints
├── services/              # Business logic
│   ├── emotion_aware_therapeutic_assistant.py
│   ├── cache_service.py
│   └── ...
├── models/                # SQLAlchemy database models
├── utils/                 # Utilities and helpers
├── middleware/            # Custom middleware
├── tests/                 # Test files
└── docs/                  # Documentation
```

## Development Workflow

### Running Tests

```bash
# Backend tests
pytest

# Frontend tests
npm test

# Run with coverage
pytest --cov=. --cov-report=html
```

### Code Quality

```bash
# Format code
npm run format
black .  # Python formatting

# Lint code
npm run lint
flake8 .  # Python linting

# Type checking
npm run type-check
mypy .  # Python type checking
```

### Database Migrations

```bash
# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback
flask db downgrade
```

### Building for Production

```bash
# Build frontend
npm run build

# Frontend build output goes to static/dist/
```

## Common Issues

### Issue: Database connection failed
**Solution:** Ensure PostgreSQL is running and DATABASE_URL is correct
```bash
# Check PostgreSQL status
pg_isready

# Restart PostgreSQL
brew services restart postgresql  # macOS
sudo systemctl restart postgresql # Linux
```

### Issue: OAuth redirect mismatch
**Solution:** Add http://localhost:5000/callback/google to authorized redirect URIs in Google Cloud Console

### Issue: Port already in use
**Solution:** Kill the process or use a different port
```bash
# Find process on port 5000
lsof -ti:5000 | xargs kill

# Or run on different port
PORT=5001 python app.py
```

### Issue: Module not found errors
**Solution:** Reinstall dependencies
```bash
rm -rf venv node_modules
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
npm install
```

## Environment-Specific Configuration

### Development
- Debug mode enabled
- Hot reload enabled
- Verbose logging
- Demo mode available

### Staging
- Production-like environment
- Real OAuth
- Performance monitoring enabled

### Production
- Debug mode OFF
- Minified assets
- Structured JSON logging
- Rate limiting enforced
- Security headers enabled

## Useful Commands

```bash
# Clean build artifacts
npm run clean
find . -type d -name __pycache__ -exec rm -rf {} +

# Reset database
dropdb nous_platform
createdb nous_platform
flask db upgrade

# View logs
tail -f logs/app.log

# Check for security vulnerabilities
npm audit
pip check
```

## IDE Setup

### VS Code
Recommended extensions:
- Python
- ESLint
- Prettier
- SQLTools PostgreSQL

Recommended settings (`.vscode/settings.json`):
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "editor.formatOnSave": true,
  "python.formatting.provider": "black"
}
```

### PyCharm
- Enable Django support
- Configure Python interpreter to use venv
- Set code style to Black

## Contributing

1. Create a feature branch: `git checkout -b feature/amazing-feature`
2. Make changes and commit: `git commit -m 'Add amazing feature'`
3. Run tests: `pytest && npm test`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## Getting Help

- **Documentation**: See `/docs` directory
- **Issues**: GitHub Issues
- **Chat**: Join our Discord server
- **Email**: dev@nous-intelligence.com

## Next Steps

- Read [API Documentation](./API_DOCUMENTATION.md)
- Review [Architecture Guide](./ARCHITECTURE.md)
- Check [Deployment Guide](./DEPLOYMENT_GUIDE.md)
