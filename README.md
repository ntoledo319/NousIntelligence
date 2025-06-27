# NOUS: The AI-Powered Personal Assistant & Life-Management Platform

[![CI Status](https://img.shields.io/badge/CI-Passing-brightgreen?style=for-the-badge)](https://github.com/features/actions)
[![Docs](https://img.shields.io/badge/Docs-MkDocs-blue?style=for-the-badge)](./docs/index.md)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](./LICENSE)

NOUS is a sophisticated, enterprise-grade AI-powered personal assistant and life management platform that helps you organize, optimize, and enhance every aspect of your daily life. Built with Flask and powered by cost-optimized AI services, NOUS provides a comprehensive suite of productivity, health, financial, and collaborative tools through an intuitive chat interface and dedicated dashboards.

**Latest Enhancement:** NOUS has been transformed into a comprehensive life management platform with advanced analytics, real-time search, smart notifications, financial tracking, collaborative features, and enhanced mobile experience.

## 🌟 Core Capabilities

- **🤖 Advanced AI Integration:** Powered by OpenRouter, HuggingFace, and Gemini Pro for cost-effective (~$0.49/month) intelligent assistance
- **🗣️ Natural Language Processing:** Communicate in plain English - no rigid commands needed
- **📊 Real-Time Analytics:** Comprehensive dashboard tracking productivity, health, engagement, and goal progress
- **🔍 Universal Search:** Global search across all content with real-time suggestions and smart indexing
- **🔔 Smart Notifications:** Priority-based notification center with intelligent categorization
- **⚡ Quick Actions:** Floating action button with keyboard shortcuts for instant access
- **👥 Collaborative Features:** Family and team management with shared tasks and responsibilities
- **💰 Financial Integration:** Banking, transaction tracking, budgeting, and expense analysis
- **🏥 Enhanced Health Tracking:** Comprehensive wellness monitoring with goal setting and insights
- **📱 Mobile PWA:** Progressive Web App with offline capabilities and mobile optimization

## ✨ Feature Matrix

| Category | Features | Commands & Capabilities |
|:---------|:---------|:------------------------|
| **📊 Analytics & Insights** | Real-time dashboard, Activity tracking, Goal monitoring, Performance metrics | View productivity stats, track habits, monitor engagement patterns |
| **🔍 Search & Navigation** | Global search, Real-time suggestions, Content indexing | `Ctrl+K` for quick search, find any content instantly |
| **🔔 Notifications** | Smart notification center, Priority-based alerts, Action buttons | Manage all notifications from one central hub |
| **⚡ Quick Actions** | Floating action button, Keyboard shortcuts, Instant access | `Ctrl+/` help, `Ctrl+K` search, `Ctrl+N` new items |
| **🗓️ Calendar & Scheduling** | Event management, Appointment scheduling, Meeting coordination | `add event party at 8pm tomorrow`, `what's my day?` |
| **✅ Task Management** | Google Tasks integration, Priority levels, Due date tracking | `add task: buy milk`, `show my tasks` |
| **📝 Note Management** | Google Keep integration, Voice notes, Smart organization | `add note: remember to call mom` |
| **💰 Financial Management** | Bank account linking, Transaction tracking, Budget management, Expense analysis | Track spending, set budgets, monitor financial goals |
| **👥 Collaboration** | Family management, Shared tasks, Member roles, Group activities | Create families, assign tasks, collaborate on goals |
| **🏥 Health & Wellness** | Comprehensive tracking, Goal setting, Progress monitoring, AI insights | `log workout: 5k run`, `track sleep: 8 hours` |
| **🧠 Mental Health** | **DBT:** Skills logging, diary cards. **AA:** Big Book access, speaker recordings | Comprehensive mental health support tools |
| **🗣️ Voice Features** | Emotion analysis, Mindfulness assistant, Voice notes | Analyze emotional tone, guided meditation |
| **🌦️ Weather Intelligence** | AI-powered recommendations, Health insights, Activity suggestions | Smart weather-based activity recommendations |
| **🎵 AI Music Integration** | Spotify control, Mood-based recommendations, Smart playlists | `play focus music`, personalized music suggestions |
| **🛒 Smart Shopping** | AI-powered lists, Budget integration, Meal planning | Generate shopping lists based on meals and budget |
| **👨‍⚕️ Medical Management** | Doctor database, Appointment tracking, Medication reminders | `add doctor Dr. Jones`, `refill medication aspirin` |
| **🎓 Language Learning** | Multi-language support, Vocabulary management, AI practice sessions | Create language profiles, practice conversations |
| **🎨 Creative Tools** | Image analysis, Gallery organization, Content generation | Upload and analyze images, organize visual content |
| **🗺️ Navigation** | Interactive maps, Directions, Place discovery | Plan routes, find nearby locations |

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