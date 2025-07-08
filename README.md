# NOUS Platform

[![CI/CD](https://github.com/nous/platform/workflows/CI%2FCD/badge.svg)](https://github.com/nous/platform/actions)
[![codecov](https://codecov.io/gh/nous/platform/branch/main/graph/badge.svg)](https://codecov.io/gh/nous/platform)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Your comprehensive AI-powered personal assistant for mental health, productivity, and life management.

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/nous/platform.git
cd platform

# Setup environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
npm install

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Setup database
flask db upgrade

# Build frontend
npm run build

# Start application
flask run
```

Visit http://localhost:5000 to see the application.

## 📋 Features

### 🧠 Mental Health Support
- **CBT Tools**: Thought records, mood tracking, behavioral experiments
- **DBT Integration**: Distress tolerance, emotion regulation
- **AA/Recovery**: Sobriety tracking, support resources
- **Crisis Support**: Emergency coping skills, crisis detection

### 👨‍👩‍👧‍👦 Family & Collaboration
- **Family Groups**: Create and manage family units
- **Shared Tasks**: Collaborative task management
- **Shopping Lists**: Shared grocery and shopping lists
- **Events**: Family calendar and event planning

### 📊 Analytics & Insights
- **Mood Analytics**: Pattern recognition and insights
- **Progress Tracking**: Goal achievement monitoring
- **Predictive Analytics**: Behavioral predictions
- **Custom Reports**: Personalized analytics

### 🤖 AI-Powered Features
- **Intelligent Chat**: Context-aware AI assistant
- **Emotion Detection**: Real-time emotional analysis
- **Smart Recommendations**: Personalized suggestions
- **Cost Optimization**: 97-99% AI cost savings

### 🛠️ Productivity Tools
- **Task Management**: Full-featured task system
- **Goal Setting**: SMART goal tracking
- **Time Management**: Schedule optimization
- **Habit Tracking**: Build and maintain habits

## 🏗️ Architecture

NOUS is built with a modern, scalable architecture:

- **Backend**: Flask with SQLAlchemy ORM
- **Frontend**: Modern JavaScript with Webpack
- **Database**: PostgreSQL with Redis caching
- **AI Services**: Multi-provider integration
- **Security**: HIPAA/GDPR compliant design

## 📖 Documentation

- [Deployment Guide](docs/DEPLOYMENT.md)
- [API Documentation](docs/api/)
- [Development Setup](docs/DEVELOPMENT.md)
- [Architecture Overview](docs/ARCHITECTURE.md)

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test category
pytest -m unit
pytest -m integration
```

## 🔒 Security

NOUS takes security seriously:

- End-to-end encryption for sensitive data
- HIPAA compliant health data handling
- GDPR compliant privacy controls
- Regular security audits and updates

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📧 Email: support@nous-platform.com
- 💬 Discord: [NOUS Community](https://discord.gg/nous)
- 📖 Docs: [docs.nous-platform.com](https://docs.nous-platform.com)
- 🐛 Issues: [GitHub Issues](https://github.com/nous/platform/issues)

## 🙏 Acknowledgments

- Mental health professionals who guided our therapeutic features
- Open source community for amazing tools and libraries
- Our users who provide valuable feedback and support

---

Made with ❤️ by the NOUS Team
