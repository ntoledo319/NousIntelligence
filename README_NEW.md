# NOUS Intelligence Platform
## Open Source AI Mental Health Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Development Status](https://img.shields.io/badge/status-active%20development-blue)]()
[![GitHub Sponsors](https://img.shields.io/badge/sponsor-support%20development-pink)](https://github.com/sponsors/ntoledo319)

> **Mission:** Making evidence-based mental health support accessible through AI and open source technology

---

## 🎯 Project Status (January 2026)

**Current State:** Active Development - Beta Ready

### ✅ What Works Now

| Feature | Status | Description |
|---------|--------|-------------|
| **AI Chat** | ✅ Functional | Real therapeutic conversations with emotion detection |
| **CBT Thought Records** | ✅ Complete | Full CRUD - create, view, challenge negative thoughts |
| **Mood Tracking** | ✅ Complete | Log moods, view trends, identify patterns |
| **Crisis Support** | ✅ Complete | 24/7 crisis resources and safety planning |
| **Demo Mode** | ✅ Works | Try without signup/OAuth |
| **Deployment** | ✅ Ready | Render (free tier), Docker, local setup |

### 🚧 In Development

| Feature | Status | Notes |
|---------|--------|-------|
| **Google OAuth** | Partial | Works with configuration, demo mode fallback |
| **DBT Skills** | Backend Ready | Frontend UI needs completion |
| **AA Recovery** | Backend Ready | Frontend UI needs completion |
| **Test Suite** | 65% passing | Security tests need fixes |
| **Documentation** | In Progress | API docs, guides being added |

### 📋 Roadmap

**Next 2 Weeks:**
- Complete DBT diary cards UI
- Fix remaining test failures
- Add onboarding flow
- Create demo video

**Next Month:**
- Complete AA recovery UI
- Add data export (GDPR)
- Performance optimization
- Integration tests

---

## 🚀 Quick Start

### Try the Demo (1 minute)

No installation required:

1. Visit deployed instance (coming soon) or deploy your own
2. Click "Demo Mode"
3. Try the chat, create a thought record, log your mood

### Deploy Your Own (5 minutes)

**Render (Free Tier):**
```bash
# 1. Fork this repo
# 2. Create Render account
# 3. New Web Service → Connect repo
# 4. Add environment variables:
DATABASE_URL: <from Render PostgreSQL>
SESSION_SECRET: <generate random>
GEMINI_API_KEY: <get free from Google>

# 5. Deploy! 
```

See [DEPLOYMENT_QUICKSTART.md](DEPLOYMENT_QUICKSTART.md) for detailed guide.

### Local Development (5 minutes)

```bash
git clone https://github.com/ntoledo319/NousIntelligence.git
cd NousIntelligence

python3 -m venv venv
source venv/bin/activate
pip install -e .

cp .env.example .env
# Edit .env: add DATABASE_URL, SESSION_SECRET, GEMINI_API_KEY

python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
python3 main.py
```

Visit `http://localhost:5000`

---

## 💡 Core Features

### Therapeutic Tools

**CBT (Cognitive Behavioral Therapy)**
- ✅ Thought records with cognitive bias detection
- ✅ Evidence gathering and balanced thinking
- ✅ Mood tracking with pattern analysis
- 🚧 Behavioral experiments (planned)
- 🚧 Activity scheduling (planned)

**DBT (Dialectical Behavior Therapy)**
- ✅ Emotion-aware AI responses
- ✅ Skill recommendations based on emotional state
- 🚧 Diary cards (backend complete, UI in progress)
- 🚧 Skill practice tracking (backend complete)
- 🚧 Crisis tolerance tools (backend complete)

**AA Recovery Support**
- ✅ Crisis resources
- 🚧 Sobriety tracking (backend complete, UI in progress)
- 🚧 Meeting finder (planned)
- 🚧 Step work guides (planned)

### AI Integration

**Supported Providers:**
- ✅ Google Gemini (free tier)
- ✅ OpenRouter (free & paid models)
- ✅ OpenAI (paid)
- ✅ HuggingFace (free)

**AI Capabilities:**
- Emotion detection from text
- Therapeutic response generation
- Crisis keyword detection
- Context-aware skill recommendations
- Multi-provider fallback chain

**Cost:** Use 100% free tiers (Gemini recommended)

See [AI Setup Guide](docs/AI_SETUP_GUIDE.md) for configuration.

### Security & Privacy

- ✅ CSRF protection
- ✅ XSS prevention
- ✅ Secure session management
- ✅ SQL injection protection (ORM)
- ✅ Security headers (CSP, X-Frame-Options, etc.)
- ⚠️ Rate limiting (partial - needs completion)
- 🚧 HIPAA compliance audit (planned)

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [DEPLOYMENT_QUICKSTART.md](DEPLOYMENT_QUICKSTART.md) | Deploy in 5 minutes |
| [AI_SETUP_GUIDE.md](docs/AI_SETUP_GUIDE.md) | Configure AI providers |
| [SPONSORSHIP_ROADMAP.md](SPONSORSHIP_ROADMAP.md) | Development roadmap |
| [COMPREHENSIVE_CODEBASE_AUDIT_REPORT.md](COMPREHENSIVE_CODEBASE_AUDIT_REPORT.md) | Honest technical assessment |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute |

---

## 🏗️ Architecture

### Tech Stack

**Backend:**
- Flask 3.1+ (Python 3.11+)
- PostgreSQL (SQLAlchemy ORM)
- 192 database models across 13 files
- 21 registered blueprints
- Unified AI service (multi-provider)

**Frontend:**
- Server-rendered Jinja2 templates
- Vanilla JavaScript (no build step)
- Bootstrap 5 + custom CSS
- *(React components exist but not integrated)*

**Infrastructure:**
- Gunicorn (WSGI server)
- Docker support
- Render.com deployment ready
- Redis support (optional)

### Project Structure

```
├── app.py                 # Flask application factory
├── main.py               # Entry point
├── models/               # 13 model files (192 models)
├── routes/               # 74 route files (needs consolidation)
├── services/             # Business logic
├── utils/                # Helpers and utilities
├── templates/            # Jinja2 templates
├── static/               # CSS, JS, images
├── tests/                # Test suite
└── docs/                 # Documentation
```

---

## 🧪 Testing

### Current Test Status

- **Total Tests:** 120
- **Passing:** 78 (65%)
- **Failing:** 34 (28%)
- **Skipped:** 8 (7%)

### Run Tests

```bash
python -m pytest
python -m pytest --cov=. --cov-report=html
```

### Known Test Issues

- Security tests (CSRF, rate limiting) - 500 errors
- Route registration - Some 404s
- OAuth integration - Configuration dependent

See [test documentation](docs/TESTING.md) for details.

---

## 💰 The Cost Revolution

### Traditional Costs (Per Month)

| Service | Cost |
|---------|------|
| BetterHelp | $240-$320 |
| ChatGPT Plus | $20 |
| Notion AI | $10 |
| **Total** | **$270-$350** |

### NOUS Costs (Per Month)

| Component | Cost |
|-----------|------|
| Render Free Tier | $0 |
| PostgreSQL Free Tier | $0 |
| Gemini AI Free Tier | $0 |
| **Total** | **$0** |

**Scalable to paid tiers for $14-20/month when needed**

---

## 🤝 Contributing

We welcome contributions! Areas where you can help:

### Priority Needs

1. **Frontend Work**
   - Complete DBT diary cards UI
   - Complete AA recovery UI
   - Mobile responsiveness improvements
   - Accessibility enhancements

2. **Testing**
   - Fix failing security tests
   - Add integration tests
   - Improve test coverage

3. **Documentation**
   - API documentation
   - User guides
   - Video tutorials

4. **Clinical Input**
   - Mental health professional guidance
   - Evidence-based practice review
   - Safety protocol improvements

### How to Contribute

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 💖 Support This Project

NOUS is **open source and free forever**. If you find it valuable:

### GitHub Sponsors

- **$1/month** - Supporter (recognition in README)
- **$5/month** - Advocate (monthly updates)
- **$10/month** - Champion (priority issue response)
- **$25/month** - Founding Sponsor (logo placement)

[Become a Sponsor →](https://github.com/sponsors/ntoledo319)

### Other Ways to Support

- ⭐ Star this repository
- 🐛 Report bugs
- 📝 Improve documentation
- 💬 Share with others who might benefit
- 🔧 Contribute code

---

## 🎯 Mission & Vision

### Why NOUS Exists

Mental health support costs are prohibitive. BetterHelp charges $3,000+/year. Many evidence-based tools (CBT, DBT) are locked behind paywalls or require expensive therapy sessions.

**NOUS makes these tools free and accessible.**

### Our Principles

1. **Open Source:** Code is free, forever
2. **Privacy First:** Your data, your control
3. **Evidence-Based:** CBT, DBT, AA methodologies
4. **Cost-Conscious:** Free tiers wherever possible
5. **Accessible:** No barriers to entry

### Long-Term Vision

- ✅ Free, self-hostable mental health toolkit
- 🚧 HIPAA-compliant hosting option
- 🚧 Mobile apps (iOS/Android)
- 🚧 Offline-first PWA
- 🚧 Multi-language support
- 🚧 Integration with healthcare providers

---

## ⚠️ Important Notes

### This is NOT a Replacement for Professional Help

NOUS is a **supplement** to professional mental health care, not a replacement. If you're in crisis:

- 🇺🇸 **988** - Suicide & Crisis Lifeline
- 🇺🇸 **Text HOME to 741741** - Crisis Text Line
- 🌍 **Call emergency services** in your country

### Data Privacy

- Your data stays on your instance (self-hosted)
- No tracking or analytics by default
- Google OAuth is optional (demo mode available)
- AI providers may log conversations (check their policies)

### Development Status

This is **active development software**. Expect:
- Bugs and issues
- Breaking changes
- Incomplete features
- Database migrations

**Use at your own risk. Not for production medical use.**

---

## 📊 Honest Metrics

### What We've Built

- 25,000+ lines of Python code
- 192 database models
- 74 route files
- 48 HTML templates
- Comprehensive AI integration
- Security middleware
- Testing infrastructure

### What Needs Work

- Frontend architecture consolidation
- Route file organization (74 → ~20)
- Test failure resolution
- Documentation completion
- UI/UX polish

**We're transparent about where we are. See [COMPREHENSIVE_CODEBASE_AUDIT_REPORT.md](COMPREHENSIVE_CODEBASE_AUDIT_REPORT.md) for full details.**

---

## 🙏 Acknowledgments

- Mental health professionals who provided guidance
- Open source community for tools and frameworks
- AI providers offering free tiers
- Contributors and early testers
- Everyone who believes mental health support should be accessible

---

## 📞 Contact & Community

- **Issues:** [GitHub Issues](https://github.com/ntoledo319/NousIntelligence/issues)
- **Discussions:** [GitHub Discussions](https://github.com/ntoledo319/NousIntelligence/discussions)
- **Email:** Open an issue for now
- **Documentation:** [docs/](docs/)

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

**TL;DR:** Use it, modify it, distribute it. Just keep it open source.

---

## 🚀 Ready to Get Started?

1. **Try it:** [Deploy to Render](DEPLOYMENT_QUICKSTART.md) (5 minutes, free)
2. **Learn more:** Read the [docs](docs/)
3. **Contribute:** See [CONTRIBUTING.md](CONTRIBUTING.md)
4. **Support:** [Become a sponsor](https://github.com/sponsors/ntoledo319)

**Mental health support for everyone. No exceptions. No paywalls.**

---

*Built with ❤️ and a commitment to accessibility. Last updated: January 2026.*
