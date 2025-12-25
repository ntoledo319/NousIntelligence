# NOUS Environment Setup Guide

*Zero to Production in 10 Minutes*

## 🚀 Quick Start (Replit)

1. **Fork the Replit**: [replit.com/@nous/nous-platform]
2. **Add Secrets**: Click "Secrets" → Add required variables
3. **Run**: Click "Run" button
4. **Done**: Access at `https://your-app.replit.app`

That's it. Seriously.

## 🔧 Environment Variables Reference

### 🔴 Required Variables (Must Set)

#### Authentication
```bash
# Google OAuth (Get from console.cloud.google.com)
GOOGLE_CLIENT_ID=123456789.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdef123456

# Session Security (Generate with: openssl rand -hex 32)
SESSION_SECRET=your-very-long-random-string-here
```

#### Database
```bash
# Production PostgreSQL
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Or use SQLite for development
DATABASE_URL=sqlite:///nous.db
```

### 🟡 Recommended Variables (For Full Features)

#### AI Services
```bash
# Primary AI Provider (https://openrouter.ai)
OPENROUTER_API_KEY=sk-or-v1-xxxxx

# Voice Features (https://huggingface.co)
HUGGINGFACE_API_KEY=hf_xxxxx

# Google Services (https://console.cloud.google.com)
GOOGLE_API_KEY=AIzaSyxxxxx

# OpenAI (optional - for direct OpenAI access)
OPENAI_API_KEY=sk-xxxxx
```

#### AI Model Configuration (2025 Latest - Optimized for Cost/Quality)
```bash
# OpenRouter Models - Automatically selected based on task complexity
OPENROUTER_FREE_MODEL=meta-llama/llama-3.3-70b-instruct:free
OPENROUTER_BASIC_MODEL=google/gemini-2.0-flash-exp:free
OPENROUTER_STANDARD_MODEL=deepseek/deepseek-v3.2          # $0.22/M - Best value!
OPENROUTER_COMPLEX_MODEL=google/gemini-2.5-flash           # $0.30/M input, $2.50/M output
OPENROUTER_RESEARCH_MODEL=anthropic/claude-sonnet-4.5      # $3/M input, $15/M output

# OpenAI Models (if using direct OpenAI API)
OPENAI_STANDARD_MODEL=gpt-4o-mini
OPENAI_RESEARCH_MODEL=gpt-4o

# Gemini Model (for Google AI)
GEMINI_MODEL=gemini-2.5-flash
```

#### External Integrations
```bash
# Spotify (https://developer.spotify.com)
SPOTIFY_CLIENT_ID=xxxxx
SPOTIFY_CLIENT_SECRET=xxxxx

# Weather (https://openweathermap.org/api)
WEATHER_API_KEY=xxxxx
```

### 🟢 Optional Variables (Advanced Features)

#### Application Configuration
```bash
# Server Settings
PORT=8080                    # Default: 5000
HOST=0.0.0.0                # Default: 0.0.0.0
FLASK_ENV=production        # Default: production
FLASK_DEBUG=False           # Default: False
BASE_URL=https://nous.app   # Your domain

# CORS Configuration
CORS_ORIGINS=https://nous.app,https://api.nous.app

# Performance
REDIS_URL=redis://localhost:6379/0  # For caching
```

#### Beta & Feature Management
```bash
# Beta Program
ENABLE_BETA_MODE=true
BETA_ACCESS_CODE=BETANOUS2025
MAX_BETA_TESTERS=30

# Feature Flags
ENABLE_VOICE_FEATURES=true
ENABLE_VISUAL_INTELLIGENCE=true
ENABLE_PREDICTIVE_ANALYTICS=false
```

## 📦 Installation Methods

### Method 1: Replit (Recommended)
```bash
# No installation needed!
# Just fork and run
```

### Method 2: Local Development
```bash
# Clone repository
git clone https://github.com/nous/nous
cd nous

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp env.example .env
# Edit .env with your variables

# Run application
python main.py
```

### Method 3: Docker
```bash
# Build image
docker build -t nous .

# Run container
docker run -p 8080:8080 \
  -e DATABASE_URL=$DATABASE_URL \
  -e SESSION_SECRET=$SESSION_SECRET \
  -e GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID \
  -e GOOGLE_CLIENT_SECRET=$GOOGLE_CLIENT_SECRET \
  nous
```

### Method 4: Production Server
```bash
# Ubuntu/Debian setup
sudo apt update
sudo apt install python3 python3-pip postgresql nginx

# Clone and setup
git clone https://github.com/nous/nous /opt/nous
cd /opt/nous
pip3 install -r requirements.txt

# Configure systemd service
sudo cp nous.service /etc/systemd/system/
sudo systemctl enable nous
sudo systemctl start nous

# Configure Nginx
sudo cp nginx.conf /etc/nginx/sites-available/nous
sudo ln -s /etc/nginx/sites-available/nous /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

## 🔐 Getting API Keys

### Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `http://localhost:5000/callback/google` (dev)
   - `https://your-app.replit.app/callback/google` (Replit)
   - `https://your-domain.com/callback/google` (production)

### OpenRouter API
1. Sign up at [openrouter.ai](https://openrouter.ai)
2. Add credit ($5 lasts months for testing)
3. Copy API key from dashboard

### Other Services
- **HuggingFace**: Free at [huggingface.co/settings/tokens]
- **Spotify**: Free at [developer.spotify.com/dashboard]
- **Weather**: Free tier at [openweathermap.org/api]

## 🗄️ Database Setup

### PostgreSQL (Production)
```sql
-- No manual setup needed!
-- Tables are created automatically on first run
```

### Connection String Format
```
postgresql://username:password@host:port/database
```

### Free PostgreSQL Options
- **Supabase**: 500MB free (supabase.com)
- **Neon**: 0.5GB free (neon.tech)
- **ElephantSQL**: 20MB free (elephantsql.com)
- **Aiven**: 1 month free trial (aiven.io)

## 🚨 Common Issues & Solutions

### Issue: "SESSION_SECRET environment variable is required"
```bash
# Solution: Set SESSION_SECRET
export SESSION_SECRET=$(openssl rand -hex 32)
```

### Issue: Google OAuth redirect mismatch
```bash
# Solution: Add exact callback URL to Google Console
# Must match exactly including http/https and trailing slashes
```

### Issue: Database connection failed
```bash
# Solution: Check DATABASE_URL format
# PostgreSQL: postgresql://user:pass@host/db
# SQLite: sqlite:///nous.db
```

### Issue: AI features not working
```bash
# Solution: Add at least one AI provider key
# OPENROUTER_API_KEY or GOOGLE_API_KEY
```

## 📊 Environment Templates

### Minimal Setup (.env.minimal)
```bash
DATABASE_URL=sqlite:///nous.db
SESSION_SECRET=dev-secret-key-change-in-production
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-secret
```

### Development Setup (.env.development)
```bash
# Core
DATABASE_URL=sqlite:///nous_dev.db
SESSION_SECRET=dev-secret-key-not-for-production
FLASK_DEBUG=True
FLASK_ENV=development

# OAuth
GOOGLE_CLIENT_ID=dev-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-dev-secret

# AI (Optional)
OPENROUTER_API_KEY=sk-or-v1-dev-key
```

### Production Setup (.env.production)
```bash
# Core
DATABASE_URL=postgresql://user:pass@db.example.com:5432/nous_prod
SESSION_SECRET=production-secret-use-strong-random-value
FLASK_ENV=production
BASE_URL=https://nous.example.com

# OAuth
GOOGLE_CLIENT_ID=prod-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-prod-secret

# AI Services
OPENROUTER_API_KEY=sk-or-v1-production-key
HUGGINGFACE_API_KEY=hf_production_key
GOOGLE_API_KEY=AIzaSy-production-key

# Monitoring
SENTRY_DSN=https://xxx@sentry.io/xxx
```

## 🔍 Verification Steps

### 1. Check Environment
```bash
python -c "import os; print('SESSION_SECRET set:', bool(os.getenv('SESSION_SECRET')))"
python -c "import os; print('DATABASE_URL:', os.getenv('DATABASE_URL', 'Not set'))"
```

### 2. Test Database Connection
```bash
python -c "from app import app; print('Database OK')"
```

### 3. Verify OAuth Setup
```bash
curl http://localhost:5000/auth/status
```

### 4. Health Check
```bash
curl http://localhost:5000/health
```

## 🤖 AI Model Selection Guide (2025)

### Automatic Model Selection
NOUS automatically selects the optimal model based on task complexity:

- **BASIC**: Free models for simple tasks (`google/gemini-2.0-flash-exp:free`)
- **STANDARD**: Cost-effective models for regular chat (`deepseek/deepseek-v3.2` - only $0.22/M!)
- **COMPLEX**: Balanced models for advanced tasks (`google/gemini-2.5-flash`)
- **RESEARCH**: Premium models for reasoning (`anthropic/claude-sonnet-4.5`)

### Recommended Model Configurations

#### Free Tier (No Cost)
```bash
OPENROUTER_FREE_MODEL=meta-llama/llama-3.3-70b-instruct:free
OPENROUTER_BASIC_MODEL=google/gemini-2.0-flash-exp:free
OPENROUTER_STANDARD_MODEL=meta-llama/llama-3.3-70b-instruct:free
```

#### Cost-Optimized ($5-10/month for moderate usage)
```bash
OPENROUTER_STANDARD_MODEL=deepseek/deepseek-v3.2        # Best value - $0.22/M
OPENROUTER_COMPLEX_MODEL=google/gemini-2.5-flash        # $0.30/M input
OPENROUTER_RESEARCH_MODEL=google/gemini-2.5-flash       # Use for all tasks
```

#### High Quality (Production-Ready)
```bash
OPENROUTER_STANDARD_MODEL=google/gemini-2.5-flash
OPENROUTER_COMPLEX_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_RESEARCH_MODEL=anthropic/claude-sonnet-4.5   # Best coding model
```

### Available Models on OpenRouter (Dec 2025)

#### **Free Models** 🆓
- `meta-llama/llama-3.3-70b-instruct:free` - Meta's latest, excellent quality
- `google/gemini-2.0-flash-exp:free` - Google's experimental fast model

#### **Cost-Effective Models** 💰
- `deepseek/deepseek-v3.2` - **$0.22/M** - Best value for quality!
- `google/gemini-2.5-flash` - $0.30/M input - State-of-the-art from Google
- `openai/gpt-4o-mini` - Balanced OpenAI option

#### **Premium Models** ⭐
- `anthropic/claude-sonnet-4.5` - $3/M input - Best coding & reasoning
- `anthropic/claude-3.7-sonnet` - Latest Claude with thinking
- `openai/gpt-4o` - Latest GPT-4 Omni

### Cost Comparison (Per Million Tokens)

| Model | Input Cost | Output Cost | Best For |
|-------|-----------|-------------|----------|
| DeepSeek V3.2 | $0.22 | $0.32 | **Best value overall** |
| Gemini 2.5 Flash | $0.30 | $2.50 | Fast, high-quality |
| GPT-4o-mini | $0.15 | $0.60 | OpenAI balanced |
| GPT-4o | $2.50 | $10.00 | Premium OpenAI |
| Claude Sonnet 4.5 | $3.00 | $15.00 | **Best coding/reasoning** |
| Llama 3.3 (free) | $0.00 | $0.00 | Testing/development |

## 🎯 Best Practices

### Security
1. **Never commit secrets** to version control
2. **Use strong SESSION_SECRET** (32+ characters)
3. **Rotate keys regularly** in production
4. **Use HTTPS always** in production

### Performance
1. **Use PostgreSQL** for production (not SQLite)
2. **Enable Redis** for caching if >1000 users
3. **Set connection pooling** for database
4. **Monitor AI costs** via dashboard

### Development
1. **Use .env files** for local development
2. **Keep separate configs** for dev/staging/prod
3. **Document custom variables** in your fork
4. **Test with minimal config** first

## 🚀 Deployment Checklist

- [ ] All required environment variables set
- [ ] Database connection tested
- [ ] Google OAuth callback URLs configured
- [ ] SESSION_SECRET is strong and unique
- [ ] FLASK_DEBUG is False in production
- [ ] Health endpoint responds with 200
- [ ] Test login flow works
- [ ] AI features tested (if API keys added)

## 📚 Additional Resources

- [Full Documentation](docs/)
- [API Reference](docs/API_REFERENCE.md)
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)
- [Security Best Practices](SECURITY.md)
- [Cost Optimization](COST_ANALYSIS.md)

---

*Remember: The beauty of NOUS is that it works with minimal configuration. Start simple, add features as needed.* 