# NOUS Intelligence - Deployment Quick Start

## 🚀 Get Running in 5 Minutes

### Prerequisites

- Python 3.11 or higher
- PostgreSQL database (or use Render's free tier)
- At least ONE free AI API key (see [AI Setup Guide](docs/AI_SETUP_GUIDE.md))

---

## Option 1: Render (Recommended - Free Tier)

**Perfect for:** Public demo, production deployment, sponsors to test

### Step 1: Fork Repository

```bash
# Fork at https://github.com/ntoledo319/NousIntelligence
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/NousIntelligence.git
cd NousIntelligence
```

### Step 2: Create Render Account

1. Go to [https://render.com](https://render.com)
2. Sign up (free account)
3. Connect your GitHub account

### Step 3: Create PostgreSQL Database

1. In Render Dashboard → "New" → "PostgreSQL"
2. Name: `nous-database`
3. Region: Choose closest to you
4. Plan: **Free** (sufficient for demo/testing)
5. Click "Create Database"
6. **Copy the Internal Database URL** (starts with `postgresql://`)

### Step 4: Create Web Service

1. Render Dashboard → "New" → "Web Service"
2. Connect your forked repository
3. Configure:
   - **Name:** `nous-intelligence` (or your choice)
   - **Region:** Same as database
   - **Branch:** `main`
   - **Root Directory:** Leave blank
   - **Runtime:** Python 3
   - **Build Command:** `pip install -e .`
   - **Start Command:** `gunicorn --config gunicorn.conf.py main:app`
   - **Plan:** Free

### Step 5: Set Environment Variables

In the web service settings, add these environment variables:

| Variable | Notes |
|---|---|
| `DATABASE_URL` | Paste the Render *Internal Database URL* from step 3 |
| `SESSION_SECRET` | Generate random (`python3 -c "import secrets; print(secrets.token_urlsafe(32))"`) |
| `GEMINI_API_KEY` | Free key from https://makersuite.google.com/app/apikey |
| `GOOGLE_CLIENT_ID` | Optional (Google OAuth) |
| `GOOGLE_CLIENT_SECRET` | Optional (Google OAuth) |

### Step 6: Deploy

1. Click "Create Web Service"
2. Wait for deployment (3-5 minutes)
3. Your app will be live at: `https://your-app-name.onrender.com`

### Step 7: Test

Visit your URL:
- Landing page should load
- Click "Demo Mode" to try without OAuth
- Test the chat - should give real AI responses (not echoes)

**Done! Your NOUS instance is live. Share the URL with sponsors.**

---

## Option 2: Local Development

**Perfect for:** Testing before deployment, development work

### Step 1: Clone and Setup

```bash
git clone https://github.com/ntoledo319/NousIntelligence.git
cd NousIntelligence

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Step 2: Create .env File

```bash
cp .env.example .env
```

Edit `.env` and add:

- `DATABASE_URL`: `sqlite:///instance/nous_local.db` (SQLite for local testing)
- `SESSION_SECRET`: generate a random secret
- `GEMINI_API_KEY`: your Gemini key (free)

### Step 3: Initialize Database

```bash
python3 -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database created!')"
```

### Step 4: Run

```bash
python3 main.py
```

Visit: `http://localhost:5000`

---

## Option 3: Docker

**Perfect for:** Consistent environments, containerized deployments

### Using Docker Compose (Easiest)

```bash
# Clone repository
git clone https://github.com/ntoledo319/NousIntelligence.git
cd NousIntelligence

# Create .env file
cp .env.example .env
# Edit .env and add your API keys

# Start everything
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Using Dockerfile Only

```bash
# Build
docker build -t nous-intelligence .

# Run
docker run --env-file .env -p 5000:5000 nous-intelligence
```

---

## Getting API Keys (All FREE)

### Gemini (Recommended - Easiest)

1. Go to [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy key → Add to `GEMINI_API_KEY` in `.env`

**Cost:** FREE (generous free tier)

### OpenRouter (Optional - More Models)

1. Go to [https://openrouter.ai/](https://openrouter.ai/)
2. Sign up
3. Go to Keys → Create Key
4. Copy key → Add to `OPENROUTER_API_KEY` in `.env`

**Cost:** Some models free, some paid ($0.22-$3 per 1M tokens)

### Google OAuth (Optional - For Real Login)

1. Go to [https://console.cloud.google.com](https://console.cloud.google.com)
2. Create new project or select existing
3. Enable "Google+ API"
4. Go to Credentials → Create OAuth 2.0 Client ID
5. Application type: Web application
6. Authorized redirect URIs:
   - For Render: `https://your-app.onrender.com/callback/google`
   - For local: `http://localhost:5000/callback/google`
7. Copy Client ID and Client Secret to `.env`

**Cost:** FREE

---

## Troubleshooting

### "Application Error" on Render

**Check logs:** Render Dashboard → Your Service → Logs

Common issues:
- Missing environment variables
- Database URL incorrect
- Build failed (check Python version)

### "No AI providers available"

- Verify API key is set in environment variables
- Check key format (Gemini starts with `AI`, OpenRouter with `sk-or-v1-`)
- Restart application after adding keys

### "Database errors"

**Local:**
```bash
# Reset database
rm -rf instance/
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
```

**Render:**
- Database URL must be the Internal Database URL
- Check database is created and running

### Chat returns echoes

- AI key not loaded properly
- Restart web service on Render
- Check logs for "Unified AI Service initialized with providers: []"

---

## Configuration Options

### Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ Yes | - | PostgreSQL or SQLite connection string |
| `SESSION_SECRET` | ✅ Yes | - | Secret key for sessions (generate random) |
| `GEMINI_API_KEY` | ⚠️ Recommended | - | Google Gemini API key (free) |
| `OPENROUTER_API_KEY` | ❌ Optional | - | OpenRouter API key |
| `OPENAI_API_KEY` | ❌ Optional | - | OpenAI API key |
| `GOOGLE_CLIENT_ID` | ❌ Optional | - | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | ❌ Optional | - | Google OAuth secret |

### Minimum for Demo

Just these three:
- `DATABASE_URL`: `...`
- `SESSION_SECRET`: `...`
- `GEMINI_API_KEY`: `...`

---

## Post-Deployment Checklist

- [ ] Application loads at URL
- [ ] Landing page displays correctly
- [ ] Demo mode accessible
- [ ] Chat provides real AI responses (not echoes)
- [ ] Can create thought record
- [ ] Can log mood
- [ ] No console errors

---

## Updating Your Deployment

### Render (Auto-Deploy)

Render auto-deploys on git push:

```bash
git pull origin main  # Get latest changes
git push origin main  # Triggers auto-deploy
```

### Manual Redeploy

Render Dashboard → Your Service → "Manual Deploy" → Deploy latest commit

---

## Scaling

### Current Setup Supports

- **Users:** 100-500 concurrent
- **Requests:** Moderate traffic
- **Cost:** $0/month (free tiers)

### To Scale Up

1. **Render Standard Plan** ($7/month)
   - More memory/CPU
   - No sleep time
   - 1K+ concurrent users

2. **PostgreSQL Starter** ($7/month)
   - More storage
   - Better performance
   - Connection pooling

3. **Add Redis** (caching)
   ```bash
   # Add to Render
   REDIS_URL=redis://...
   ```

4. **CDN** for static files
   - Cloudflare (free)
   - Improves load times

---

## Support

- **Documentation:** [Full docs](docs/)
- **Issues:** [GitHub Issues](https://github.com/ntoledo319/NousIntelligence/issues)
- **Discussions:** [GitHub Discussions](https://github.com/ntoledo319/NousIntelligence/discussions)

---

## Next Steps

1. ✅ Deploy successfully
2. 📝 Test all features
3. 🔐 Set up Google OAuth (optional)
4. 🎨 Customize branding (optional)
5. 📊 Monitor usage
6. 💰 Consider sponsoring if you find it useful!

**Ready to launch? Start with Option 1 (Render) - it's free and takes 5 minutes!**
