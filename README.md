# NOUS: Advanced CBT Support & Mental Health Platform

[![Health Status](https://img.shields.io/badge/Health-Operational-brightgreen?style=for-the-badge)](./health)
[![Security](https://img.shields.io/badge/Security-Compliant-blue?style=for-the-badge)](./docs/SECURITY_FEATURES.md)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](./LICENSE)

NOUS is an advanced Cognitive Behavioral Therapy (CBT) support system and comprehensive mental health platform that provides innovative technology-driven therapeutic interventions, monitoring, and scalable mental health resource infrastructure. Built with Flask and featuring AI-powered cognitive bias detection, dynamic intervention generation, and adaptive user experiences.

**Current Focus:** Advanced CBT therapeutic support with secure mental health data management, SEED optimization engine, autonomous drone swarm systems, and comprehensive authentication via Google OAuth.

## 🌟 Core Capabilities

- **🧠 Advanced CBT Support:** Comprehensive Cognitive Behavioral Therapy tools with AI-powered cognitive bias detection and personalized interventions
- **🤖 SEED Optimization Engine:** Self-learning optimization system that adapts therapeutic approaches based on user responses and effectiveness patterns
- **🚁 Autonomous Drone Swarm:** Intelligent software agents that continuously monitor, optimize, and maintain system performance
- **🔐 Enterprise Security:** Google OAuth 2.0 authentication with comprehensive security compliance and encrypted data management
- **🧬 Therapeutic Integration:** Combined DBT (Dialectical Behavior Therapy), CBT, and AA (Alcoholics Anonymous) support systems
- **📊 Real-Time Health Monitoring:** Advanced analytics and insights for mental health progress tracking
- **🎯 Dynamic Intervention Generation:** AI-powered personalized therapeutic recommendations based on current emotional state and progress
- **🔄 Adaptive User Experience:** System learns from user interactions to provide increasingly personalized support
- **💾 Scalable Infrastructure:** Microservices architecture with Flask blueprints supporting modular mental health resource expansion
- **📱 Secure Privacy-First Design:** HIPAA-compliant data handling with local processing and minimal data transmission

## ✨ Feature Matrix

| Category | Features | Therapeutic Capabilities |
|:---------|:---------|:------------------------|
| **🧠 CBT Support** | Thought records, Cognitive bias detection, Behavioral experiments, Mood tracking | Advanced cognitive restructuring, bias identification, evidence-based interventions |
| **🌱 DBT Skills** | Distress tolerance, Emotion regulation, Mindfulness practice, Interpersonal effectiveness | Comprehensive DBT skills library with usage tracking and effectiveness monitoring |
| **🍃 AA Recovery** | Big Book access, Speaker recordings, Step work guidance, Achievement tracking | Digital sobriety tools, meeting resources, sponsorship support |
| **🤖 SEED Engine** | Therapeutic optimization, Personalized recommendations, Effectiveness analysis | AI learns user response patterns to optimize intervention timing and type |
| **🚁 Drone Swarm** | System monitoring, Performance optimization, Self-healing capabilities | Autonomous agents for continuous platform improvement and health checks |
| **🔐 Security & Privacy** | Google OAuth 2.0, Encrypted data storage, HIPAA compliance, Privacy controls | Enterprise-grade security for sensitive mental health information |
| **📊 Analytics & Insights** | Progress tracking, Pattern recognition, Goal monitoring, Outcome measurement | Real-time therapeutic progress analysis and personalized insights |
| **🎯 Dynamic Interventions** | Context-aware suggestions, Crisis support, Skill recommendations | AI-powered therapeutic interventions based on current emotional state |
| **💭 Emotion Monitoring** | Mood tracking, Trigger identification, Pattern analysis, Early warning systems | Advanced emotional intelligence with predictive capabilities |
| **📱 User Experience** | Responsive design, Accessibility features, Multi-device sync, Offline capabilities | Seamless mental health support across all platforms and situations |
| **🔄 Adaptive Learning** | User preference learning, Effectiveness tracking, Personalization, Continuous improvement | System evolves to provide increasingly personalized therapeutic support |
| **📋 Assessment Tools** | Standardized assessments, Progress measurements, Outcome tracking, Clinical insights | Evidence-based evaluation tools integrated with therapeutic workflows |
| **⚡ Crisis Support** | 24/7 availability, Emergency protocols, Resource connections, Safety planning | Immediate access to crisis resources and emergency intervention capabilities |
| **🏥 Healthcare Integration** | Provider communication, Appointment tracking, Medication management, Care coordination | Seamless integration with existing healthcare systems and providers |

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.11+
- PostgreSQL database (or SQLite for development)

### 2. Environment Setup
Create a `.env` file using the `ENV_VARS.md` guide. Essential variables include:
- `DATABASE_URL` - Database connection string
- `GOOGLE_CLIENT_ID` & `GOOGLE_CLIENT_SECRET` - OAuth authentication
- `OPENROUTER_API_KEY` - Primary AI service
- `SESSION_SECRET` - Session security

### 3. Installation & Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Database tables are created automatically on startup
```

### 4. Running the Application
```bash
python main.py
```
Open `http://localhost:5000` and sign in with Google to start using NOUS.

### 5. Initial Setup
1. Complete the guided onboarding tour
2. Connect your Google and Spotify accounts
3. Explore the analytics dashboard
4. Set up your first goals and tasks

## 🏗️ Architecture

- **Backend**: Flask with SQLAlchemy ORM, modular blueprint architecture
- **Frontend**: Progressive Web App with vanilla JavaScript, responsive CSS Grid/Flexbox
- **Database**: PostgreSQL (production) / SQLite (development) with 20+ models
- **Authentication**: Google OAuth 2.0 with secure session management
- **AI Services**: OpenRouter (Gemini Pro), HuggingFace Inference API
- **Deployment**: Replit Cloud with automatic HTTPS and scaling

## 📡 API Endpoints

### Core Application
- `GET /` - Landing page
- `GET /app` - Main application interface
- `POST /api/chat` - Chat message processing
- `GET /health` - System health check
- `GET /healthz` - Detailed system metrics

### Analytics & Insights
- `GET /api/analytics/dashboard` - Analytics dashboard data
- `GET /api/analytics/activity` - User activity metrics
- `GET /api/analytics/insights` - AI-generated insights
- `POST /api/analytics/goals` - Goal management

### Search & Navigation
- `GET /api/search` - Global search with real-time suggestions
- `POST /api/search/index` - Content indexing
- `GET /api/search/suggestions` - Search suggestions

### Notifications
- `GET /api/notifications` - Get user notifications
- `POST /api/notifications` - Create notifications
- `PUT /api/notifications/<id>/read` - Mark as read
- `DELETE /api/notifications/<id>` - Delete notification

### Financial Management
- `GET /api/financial/accounts` - Bank account management
- `GET /api/financial/transactions` - Transaction history
- `POST /api/financial/transactions` - Log transactions
- `GET /api/financial/budgets` - Budget tracking

### Collaboration
- `GET /api/collaboration/families` - Family management
- `POST /api/collaboration/families` - Create family
- `GET /api/collaboration/shared-tasks` - Shared task management

### Authentication
- `GET /login` - Initiate Google OAuth
- `GET /oauth/callback` - OAuth callback handler
- `GET /logout` - End user session

## 💻 Development

### Project Structure
```
/
├── app.py                 # Main Flask application factory
├── main.py               # Application entry point
├── models/               # Database models (20+ models)
│   ├── analytics_models.py
│   ├── financial_models.py
│   ├── collaboration_models.py
│   └── enhanced_health_models.py
├── routes/               # Route handlers (25+ endpoints)
│   ├── analytics_routes.py
│   ├── search_routes.py
│   ├── notification_routes.py
│   ├── financial_routes.py
│   └── collaboration_routes.py
├── utils/                # Business logic services
│   ├── analytics_service.py
│   ├── search_service.py
│   ├── notification_service.py
│   └── 60+ utility modules
├── templates/            # Jinja2 templates
├── static/               # Progressive Web App assets
└── docs/                 # Comprehensive documentation
```

### Database Models
- **Analytics**: UserActivity, UserMetrics, UserInsight, UserGoal
- **Financial**: BankAccount, Transaction, Budget, ExpenseCategory
- **Collaboration**: Family, FamilyMember, SharedTask, ActivityLog
- **Health**: HealthMetric, HealthGoal, WellnessInsight
- **Core**: User, BetaUser, NotificationQueue

### New Features Architecture
- **Modular Design**: Each feature as self-contained blueprint
- **Service Layer**: Dedicated services for complex business logic
- **Real-time Updates**: Live data updates with polling mechanisms
- **Mobile Optimization**: Progressive Web App capabilities
- **Accessibility**: Full ARIA compliance and keyboard navigation

## 🧪 Testing

```bash
# Run comprehensive test suite
python -m pytest tests/

# Test specific features
pytest tests/test_analytics.py
pytest tests/test_search.py
pytest tests/test_notifications.py

# Health checks
curl http://localhost:5000/health
curl http://localhost:5000/healthz
```

## 🚀 Deployment

Optimized for Replit Cloud deployment:

1. Configure environment variables in Replit Secrets
2. Push code to repository
3. Application auto-deploys with HTTPS
4. Scales automatically based on usage

**Production Features:**
- Automatic database migrations
- Health monitoring endpoints
- Error tracking and logging
- Session persistence
- CORS configuration

## 🔒 Security

- **Authentication**: Google OAuth 2.0 with secure session management
- **Data Protection**: Encrypted data transmission and storage
- **Access Control**: Role-based permissions and family management
- **Input Security**: Comprehensive validation and sanitization
- **Privacy**: GDPR-compliant data handling

## 💰 Cost Analysis

**Monthly Operational Costs: ~$0.49**
- OpenRouter API (Gemini Pro): ~$0.30/month
- HuggingFace Inference: Free tier
- Database & hosting: Included with Replit
- Additional APIs: ~$0.19/month

**99.87% cost savings** compared to commercial alternatives while providing enterprise-grade functionality.

## 📱 Mobile Experience

NOUS is built as a Progressive Web App (PWA) with:
- **Offline Capabilities**: Core features work without internet
- **Mobile Optimization**: Touch-friendly interface and gestures
- **App-like Experience**: Install on home screen, full-screen mode
- **Push Notifications**: Real-time alerts and reminders
- **Responsive Design**: Adapts to all screen sizes

## 🎯 Quick Actions & Shortcuts

- **Global Search**: `Ctrl+K` or `Cmd+K`
- **Help System**: `Ctrl+/` or `Cmd+/`
- **Quick Actions**: `Ctrl+N` or `Cmd+N`
- **Notifications**: Click notification icon in header
- **Analytics**: Access via main navigation
- **Voice Commands**: Available in supported browsers

## 📚 Documentation

- **User Guide**: `docs/USER_GUIDE.md` - Complete user instructions
- **Developer Guide**: `docs/DEVELOPER_GUIDE.md` - Development setup
- **API Reference**: `docs/API_REFERENCE.md` - Complete API documentation
- **Architecture**: `ARCHITECTURE.md` - Technical architecture details
- **Deployment Guide**: `DEPLOYMENT_SUMMARY.md` - Deployment instructions

## 🤝 Support

For support, feature requests, or bug reports:
- **Health Status**: Check `/health` and `/healthz` endpoints
- **Logs**: Review application logs in `/logs` directory
- **Feedback API**: Use in-app feedback system
- **Documentation**: Comprehensive guides in `/docs`

## 📄 License

MIT License - See `LICENSE` file for details.

---

**NOUS**: Your comprehensive AI-powered life management platform. From simple tasks to complex analytics, NOUS helps you organize, optimize, and enhance every aspect of your daily life with enterprise-grade features at an unbeatable cost.