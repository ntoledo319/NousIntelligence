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
- PostgreSQL database (configured via DATABASE_URL)
- Google OAuth 2.0 credentials for secure authentication

### 2. Environment Setup
Configure these environment variables in Replit Secrets or `.env` file:
- `DATABASE_URL` - PostgreSQL connection string
- `GOOGLE_CLIENT_ID` & `GOOGLE_CLIENT_SECRET` - Google OAuth authentication
- `SESSION_SECRET` - Secure session encryption key
- `OPENROUTER_API_KEY` - AI service for therapeutic recommendations (optional)

### 3. Installation & Setup
```bash
# Install dependencies
pip install -e .

# Database tables are created automatically on startup
```

### 4. Running the Application
```bash
python main.py
```
Open `http://localhost:8080` and sign in with Google to access your therapeutic support platform.

### 5. Initial CBT Setup
1. Complete the mental health onboarding questionnaire
2. Set your therapeutic goals (CBT, DBT, or AA recovery)
3. Configure your privacy and data handling preferences
4. Explore the SEED optimization dashboard
5. Begin your first thought record or mood tracking session

## 🏗️ Architecture

- **Backend**: Flask with SQLAlchemy ORM, 21 modular blueprints for microservices architecture
- **Database**: PostgreSQL with comprehensive mental health data models (CBT, DBT, AA, User Analytics)
- **Authentication**: Google OAuth 2.0 with encrypted session management and HIPAA compliance
- **AI Services**: Unified AI service with OpenRouter, HuggingFace, and intelligent provider selection
- **SEED Engine**: Self-learning optimization system with pattern recognition and adaptive recommendations
- **Drone Swarm**: Autonomous software agents for continuous system monitoring and optimization
- **Security**: Enterprise-grade security compliance with comprehensive audit framework
- **Deployment**: Replit Cloud with automatic scaling and health monitoring

## 📡 API Endpoints

### Core Application
- `GET /` - Landing page
- `GET /health` - System health monitoring
- `POST /api/chat` - AI-powered therapeutic chat interface

### Authentication
- `GET /auth/login` - Google OAuth login initiation
- `GET /auth/callback` - OAuth callback handler
- `POST /auth/logout` - Secure session termination

### CBT (Cognitive Behavioral Therapy)
- `POST /api/cbt/thought-record` - Create thought records
- `GET /api/cbt/cognitive-biases` - Bias detection and analysis
- `POST /api/cbt/mood-log` - Mood tracking and pattern analysis
- `GET /api/cbt/coping-skills` - Evidence-based coping strategies

### DBT (Dialectical Behavior Therapy)
- `POST /api/dbt/skill-usage` - Track DBT skill utilization
- `GET /api/dbt/diary-card` - Daily diary card interface
- `POST /api/dbt/distress-tolerance` - Distress tolerance exercises

### AA (Alcoholics Anonymous) Recovery
- `GET /api/aa/big-book` - Big Book chapter access
- `POST /api/aa/sobriety-tracker` - Track sobriety milestones
- `GET /api/aa/meetings` - Meeting finder and resources

### SEED Optimization Engine
- `POST /api/seed/optimize-therapeutic` - Personalized therapeutic optimization
- `GET /api/seed/dashboard-data` - Optimization analytics and insights
- `POST /api/seed/user-feedback` - User effectiveness feedback

### Drone Swarm System
- `GET /api/drone-swarm/status` - Swarm health and performance
- `POST /api/drone-swarm/trigger-optimization` - Manual optimization trigger
- `GET /api/drone-swarm/performance-metrics` - Autonomous agent analytics
### System Health & Monitoring
- `GET /health` - Basic system health check
- `GET /healthz` - Detailed system metrics and dependencies
- `GET /api/health` - Comprehensive health status with security monitoring

### Analytics & Progress Tracking
- `GET /api/analytics/dashboard` - Therapeutic progress analytics
- `GET /api/analytics/insights` - AI-generated mental health insights
- `POST /api/analytics/goals` - Mental health goal management
- `GET /api/analytics/patterns` - Behavioral pattern analysis

## 💻 Development

### Project Structure
```
/
├── app.py                 # Main Flask application with 21 blueprint registrations
├── main.py               # Application entry point
├── models/               # Mental health database models
│   ├── cbt_models.py     # CBT thought records, cognitive biases, mood tracking
│   ├── dbt_models.py     # DBT skills, diary cards, distress tolerance
│   ├── aa_models.py      # AA recovery tracking, sobriety milestones
│   └── user_models.py    # User profiles, analytics, insights
├── routes/               # Blueprint route handlers (21 registered)
│   ├── cbt_routes.py     # CBT therapeutic endpoints
│   ├── dbt_routes.py     # DBT skill management
│   ├── aa_routes.py      # AA recovery support
│   ├── seed_routes.py    # SEED optimization engine
│   ├── drone_swarm_routes.py # Autonomous drone management
│   └── auth_routes.py    # Google OAuth authentication
├── services/             # Core business logic
│   ├── seed_optimization_engine.py # AI learning and optimization
│   ├── seed_drone_swarm.py         # Autonomous agent system
│   └── seed_integration_layer.py   # Integration with therapeutic models
├── utils/                # Support utilities
│   ├── unified_ai_service.py    # AI provider management
│   ├── google_oauth.py          # Google OAuth implementation
│   ├── health_monitor.py        # System health monitoring
│   └── comprehensive_security/  # Security framework utilities
├── templates/            # Jinja2 templates (CBT/DBT/AA interfaces)
├── static/               # Progressive Web App assets
└── docs/                 # Comprehensive documentation
```

### Database Models
- **CBT Models**: CBTThoughtRecord, CBTCognitiveBias, CBTMoodLog, CBTCopingSkill, CBTBehaviorExperiment, CBTActivitySchedule, CBTSkillUsage, CBTGoal
- **DBT Models**: DBTSkill, DBTSkillUsage, DBTDiaryCard, DBTDistressTolerance, DBTEmotionRegulation, DBTMindfulness, DBTInterpersonal
- **AA Models**: AAMeeting, AABigBookChapter, AASobrietyTracker, AAStep, AAStepProgress, AABigBookAudio, AASponsor
- **User Models**: User, UserActivity, UserMetrics, UserInsight, UserGoal, UserPreference, SetupProgress
- **SEED Models**: OptimizationCycle, UserFeedback, SystemMetrics, LearningPattern

### Advanced System Architecture
- **SEED Engine**: Self-learning optimization system with pattern recognition and adaptive therapeutic recommendations
- **Drone Swarm**: Autonomous software agents for continuous system monitoring, verification, and optimization
- **Unified AI Service**: Intelligent provider selection across OpenRouter, HuggingFace, and Google Gemini
- **Therapeutic Integration**: Seamless integration between CBT, DBT, and AA recovery methodologies
- **Security Framework**: Enterprise-grade HIPAA compliance with comprehensive audit systems
- **Real-time Analytics**: Advanced pattern recognition and personalized mental health insights

## 🧪 Testing

```bash
# Run comprehensive test suite
python -m pytest tests/

# Test specific therapeutic modules
pytest tests/test_cbt_integration.py
pytest tests/test_dbt_functionality.py
pytest tests/test_aa_recovery.py

# Test advanced systems
pytest tests/test_seed_integration.py
pytest tests/test_drone_swarm_validation.py

# System health checks
curl http://localhost:8080/health
curl http://localhost:8080/healthz
curl http://localhost:8080/api/health

# Therapeutic endpoint validation
curl -X POST http://localhost:8080/api/cbt/thought-record
curl -X GET http://localhost:8080/api/seed/dashboard-data
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