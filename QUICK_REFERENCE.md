# NOUS Intelligence - Quick Reference

## 🚀 Common Commands

### Local Development

```bash
# First time setup
./quickstart.sh

# OR manual setup
python3 -m venv venv
source venv/bin/activate
pip install -e .
cp .env.example .env
# Edit .env with your keys
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"

# Run server
python3 main.py

# Run tests
python -m pytest
python -m pytest --cov=. --cov-report=html

# Seed demo data
python3 seed_demo_data.py

# Verify sponsor readiness
python3 verify_sponsor_ready.py
```

### Docker

```bash
# Start everything
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild
docker-compose up -d --build
```

### Database

```bash
# Initialize database
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"

# Reset database (WARNING: Deletes all data)
rm -rf instance/
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"

# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade
```

## 📁 Important Files

### Configuration
- `.env` - Environment variables (never commit!)
- `.env.example` - Template for .env
- `config/` - Configuration modules

### Documentation
- `README.md` - Main documentation
- `SPONSORS.md` - Sponsorship information
- `DEPLOYMENT_QUICKSTART.md` - 5-minute deploy guide
- `docs/AI_SETUP_GUIDE.md` - AI provider setup
- `LAUNCH_CHECKLIST.md` - Pre-launch tasks

### Core Application
- `app.py` - Flask app factory
- `main.py` - Entry point
- `routes/` - API and page routes
- `models/` - Database models
- `services/` - Business logic
- `templates/` - HTML templates

### Deployment
- `Dockerfile` - Container definition
- `docker-compose.yml` - Multi-container setup
- `gunicorn.conf.py` - Production WSGI config

## 🔑 Environment Variables

### Required for Basic Operation

| Variable | Example |
|---|---|
| `DATABASE_URL` | `sqlite:///instance/nous_local.db` |
| `SESSION_SECRET` | `<generate a random secret>` |
| `GEMINI_API_KEY` | `<your Gemini key>` |

### Optional but Recommended

| Variable | Example |
|---|---|
| `OPENROUTER_API_KEY` | `<your OpenRouter key>` |
| `OPENAI_API_KEY` | `<your OpenAI key>` |
| `GOOGLE_CLIENT_ID` | `<your-id>.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | `<your OAuth client secret>` |

### Generate Secrets

```bash
# SESSION_SECRET
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Strong password
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

## 🔗 Key URLs (Local)

- **Landing:** http://localhost:5000
- **Demo Mode:** http://localhost:5000 (click "Demo Mode")
- **CBT Thought Records:** http://localhost:5000/cbt/thought-records
- **Mood Tracking:** http://localhost:5000/cbt/mood-tracking
- **Chat:** http://localhost:5000/chat
- **Health Check:** http://localhost:5000/api/health

## 🧪 Testing

### Run All Tests
```bash
python -m pytest
```

### Run Specific Test
```bash
python -m pytest tests/test_api_routes.py::test_chat_endpoint
```

### With Coverage
```bash
python -m pytest --cov=. --cov-report=html
open htmlcov/index.html
```

### Test Categories
```bash
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -k "cbt"         # Tests matching "cbt"
```

## 🐛 Troubleshooting

### "Application Error" or won't start

```bash
# Check logs
docker-compose logs -f web   # If using Docker

# Verify environment variables
cat .env | grep -v "^#"

# Check Python version
python3 --version  # Should be 3.11+

# Reinstall dependencies
pip install -e . --force-reinstall
```

### Database errors

```bash
# Reset database (WARNING: Deletes all data!)
rm -rf instance/
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### Chat returns echoes (not real AI)

```bash
# Verify API key is loaded
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print(f'GEMINI_API_KEY: {os.environ.get(\"GEMINI_API_KEY\", \"NOT SET\")[:20]}...')"

# Check unified AI service
python3 -c "from utils.unified_ai_service import UnifiedAIService; s = UnifiedAIService(); print(f'Providers: {s.available_providers}')"
```

### Port already in use

```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>

# Or use different port
python3 main.py --port 5001
```

## 📊 Monitoring

### Check Application Health

```bash
curl http://localhost:5000/api/health
```

### View Logs

```bash
# Docker
docker-compose logs -f

# Local
tail -f logs/app.log
```

## 🚀 Deployment

### Render (Free Tier)

1. Create account at render.com
2. New Web Service → Connect repo
3. Add environment variables
4. Deploy!

See `DEPLOYMENT_QUICKSTART.md` for details.

### Environment Variables for Render

| Variable | Notes |
|---|---|
| `DATABASE_URL` | Render internal database URL |
| `SESSION_SECRET` | Generate a random secret |
| `GEMINI_API_KEY` | Your Gemini key |

## 💡 Common Tasks

### Add New Route

1. Create route in `routes/` directory
2. Register blueprint in `app.py`
3. Add tests in `tests/`

### Add New Model

1. Create model in `models/` directory
2. Import in `models/__init__.py`
3. Run migration: `flask db migrate -m "Add model"`
4. Apply: `flask db upgrade`

### Update Documentation

1. Edit relevant .md file
2. Follow existing format
3. Keep it honest and clear

## 🆘 Getting Help

- **Documentation:** Check README.md and docs/
- **Issues:** https://github.com/ntoledo319/NousIntelligence/issues
- **Discussions:** https://github.com/ntoledo319/NousIntelligence/discussions

## 🎯 Quick Checks

### Is it working?

```bash
# Run verification script
python3 verify_sponsor_ready.py

# Check tests
python -m pytest

# Try demo mode
curl http://localhost:5000
```

### Ready to deploy?

1. All tests passing (or most)
2. .env variables set
3. Demo mode works
4. Chat gives real AI responses
5. Can create thought record

See `LAUNCH_CHECKLIST.md` for complete pre-launch tasks.

---

**Keep this handy!** Bookmark for quick reference during development and deployment.
