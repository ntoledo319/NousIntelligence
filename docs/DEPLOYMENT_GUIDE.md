# NOUS Deployment Guide

This comprehensive guide covers deploying NOUS with all its enhanced features including analytics, search, notifications, financial management, and collaboration capabilities.

## 🏗️ Architecture Overview

NOUS is built as a modular Flask application with:

- **20+ Database Models** across analytics, financial, collaboration, and health domains
- **25+ API Endpoints** for comprehensive feature coverage
- **Progressive Web App** with offline capabilities
- **Service Layer Architecture** for scalable business logic
- **Real-time Features** with polling and live updates

## 📋 Prerequisites

### System Requirements

- **Python**: 3.11+ (recommended 3.12)
- **Database**: PostgreSQL 13+ (SQLite for development)
- **Memory**: Minimum 512MB RAM (2GB+ recommended for production)
- **Storage**: 1GB available space
- **Network**: HTTPS-capable domain for production

### Required Services

- **Google Cloud Console**: OAuth2 credentials
- **OpenRouter**: AI service API key (primary)
- **HuggingFace**: Free API token (fallback)
- **Replit Account**: For cloud deployment

## 🔧 Environment Configuration

### Required Environment Variables

Create a `.env` file or configure in your deployment platform:

#### Core Application

```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here-minimum-32-characters
SESSION_SECRET=another-long-secret-for-session-security

# Database
DATABASE_URL=postgresql://user:password@host:port/database
# For Replit: Available automatically as DATABASE_URL

# Domain Configuration
DOMAIN_NAME=your-app.replit.app
ALLOWED_HOSTS=your-app.replit.app,localhost
```

#### Authentication

```bash
# Google OAuth (Required)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=https://your-app.replit.app/oauth/callback
```

#### AI Services

```bash
# Primary AI Service (Required)
OPENROUTER_API_KEY=your-openrouter-api-key

# Fallback AI Services
HUGGINGFACE_API_TOKEN=your-huggingface-token
GEMINI_API_KEY=your-gemini-api-key  # Optional

# Model Configuration
DEFAULT_MODEL=google/gemini-pro
FALLBACK_MODEL=microsoft/DialoGPT-medium
```

#### External Integrations (Optional)

```bash
# Google Workspace APIs
GOOGLE_CALENDAR_ENABLED=true
GOOGLE_TASKS_ENABLED=true
GOOGLE_KEEP_ENABLED=true

# Spotify Integration
SPOTIFY_CLIENT_ID=your-spotify-client-id
SPOTIFY_CLIENT_SECRET=your-spotify-client-secret

# Weather Services
OPENWEATHER_API_KEY=your-openweather-api-key

# Maps and Location
MAPS_API_KEY=your-google-maps-api-key
```

#### Feature Flags

```bash
# Analytics System
ANALYTICS_ENABLED=true
ANALYTICS_RETENTION_DAYS=365

# Financial Features
FINANCIAL_FEATURES_ENABLED=true
BANK_INTEGRATION_ENABLED=true

# Collaboration Features
COLLABORATION_ENABLED=true
FAMILY_FEATURES_ENABLED=true

# Notification System
NOTIFICATIONS_ENABLED=true
PUSH_NOTIFICATIONS_ENABLED=true

# Search Features
GLOBAL_SEARCH_ENABLED=true
SEARCH_INDEXING_ENABLED=true
```

## 🚀 Deployment Methods

### Method 1: Replit Cloud (Recommended)

#### 1. Repository Setup

```bash
# Clone or import the repository to Replit
git clone https://github.com/your-username/nous-assistant.git
```

#### 2. Environment Configuration

1. Open Replit Console
2. Navigate to "Secrets" in sidebar
3. Add all required environment variables
4. Replit automatically provides `DATABASE_URL` for PostgreSQL

#### 3. Dependency Installation

Replit automatically installs dependencies from `requirements.txt`:

```txt
Flask==3.0.0
SQLAlchemy==2.0.23
psycopg2-binary==2.9.9
google-auth==2.25.2
google-auth-httplib2==0.2.0
requests==2.31.0
python-dotenv==1.0.0
openai==1.6.1
werkzeug==3.0.1
```

#### 4. Database Setup

```python
# Database tables are created automatically on first run
# No manual migration needed
```

#### 5. Launch Application

Click "Run" in Replit interface or:

```bash
python main.py
```

### Method 2: Local Development

#### 1. Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

#### 2. Database Setup

```bash
# For PostgreSQL
createdb nous_development

# For SQLite (automatic)
# Database file created automatically
```

#### 3. Environment Variables

```bash
# Copy environment template
cp .env.example .env
# Edit .env with your configuration
```

#### 4. Run Application

```bash
python main.py
```

### Method 3: Docker Deployment

#### 1. Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "main.py"]
```

#### 2. Docker Compose

```yaml
version: '3.8'

services:
  nous:
    build: .
    ports:
      - '5000:5000'
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/nous
      - SECRET_KEY=your-secret-key
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=nous
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### 3. Deploy

```bash
docker-compose up -d
```

## 🗄️ Database Configuration

### Automatic Migrations

NOUS automatically creates and updates database tables:

```python
# app.py - Automatic table creation
with app.app_context():
    db.create_all()
    print("Database tables created successfully")
```

### Database Models Overview

#### Analytics Models

- `UserActivity` - User interaction tracking
- `UserMetrics` - Calculated performance metrics
- `UserInsight` - AI-generated insights
- `UserGoal` - Goal management and tracking

#### Financial Models

- `BankAccount` - Linked bank accounts
- `Transaction` - Financial transactions
- `Budget` - Budget management
- `ExpenseCategory` - Expense categorization
- `FinancialGoal` - Financial objectives

#### Collaboration Models

- `Family` - Family group management
- `FamilyMember` - Member roles and permissions
- `SharedTask` - Shared task coordination
- `ActivityLog` - Family activity tracking

#### Health Models

- `HealthMetric` - Health and wellness data
- `HealthGoal` - Wellness objectives
- `WellnessInsight` - Health insights
- `MoodEntry` - Mood tracking

### Database Optimization

```sql
-- Recommended indexes for performance
CREATE INDEX idx_user_activity_user_id ON user_activity(user_id);
CREATE INDEX idx_user_activity_timestamp ON user_activity(timestamp);
CREATE INDEX idx_transactions_user_date ON transaction(user_id, date);
CREATE INDEX idx_notifications_user_priority ON notification_queue(user_id, priority);
```

## 🔒 Security Configuration

### SSL/TLS Setup

#### Replit (Automatic)

Replit automatically provides SSL certificates and HTTPS.

#### Custom Domain

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Security Headers

```python
# app.py - Security headers configuration
@app.after_request
def after_request(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

### OAuth Configuration

```python
# Google OAuth Setup
GOOGLE_OAUTH = {
    'client_id': 'your-client-id',
    'client_secret': 'your-client-secret',
    'redirect_uri': 'https://your-app.com/oauth/callback',
    'scope': [
        'openid',
        'email',
        'profile',
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/tasks'
    ]
}
```

## 📊 Monitoring & Analytics

### Application Monitoring

#### Health Endpoints

```bash
# Basic health check
curl https://your-app.com/health

# Detailed system metrics
curl https://your-app.com/healthz
```

#### Response Examples

```json
// /health
{
  "status": "healthy",
  "timestamp": "2024-12-27T12:00:00Z",
  "uptime": 3600.5
}

// /healthz
{
  "status": "healthy",
  "timestamp": "2024-12-27T12:00:00Z",
  "uptime": 3600.5,
  "system": {
    "memory_percent": 45.2,
    "cpu_percent": 12.8,
    "available_memory": 2147483648
  },
  "features": {
    "analytics": "operational",
    "search": "operational",
    "notifications": "operational",
    "financial": "operational",
    "collaboration": "operational"
  }
}
```

### Performance Monitoring

```python
# utils/monitoring.py
import time
import psutil
from flask import g

def track_request_metrics():
    """Track request performance metrics"""
    g.start_time = time.time()

def log_request_completion():
    """Log request completion metrics"""
    duration = time.time() - g.start_time
    memory_usage = psutil.virtual_memory().percent
    cpu_usage = psutil.cpu_percent()

    # Log to analytics system
    analytics_service.track_performance_metric({
        'duration': duration,
        'memory_usage': memory_usage,
        'cpu_usage': cpu_usage
    })
```

## 🚦 Load Balancing & Scaling

### Horizontal Scaling

```yaml
# kubernetes-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nous-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nous
  template:
    metadata:
      labels:
        app: nous
    spec:
      containers:
        - name: nous
          image: nous:latest
          ports:
            - containerPort: 5000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: nous-secrets
                  key: database-url
```

### Load Balancer Configuration

```nginx
upstream nous_backend {
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
    server 127.0.0.1:5003;
}

server {
    listen 80;
    server_name your-app.com;

    location / {
        proxy_pass http://nous_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 🔄 Backup & Recovery

### Database Backup

```bash
# PostgreSQL backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL > "$BACKUP_DIR/nous_backup_$TIMESTAMP.sql"
find $BACKUP_DIR -name "nous_backup_*.sql" -mtime +7 -delete
```

### Application Backup

```bash
# Backup application files and user data
tar -czf nous_app_backup_$(date +%Y%m%d).tar.gz \
    --exclude=__pycache__ \
    --exclude=.git \
    --exclude=venv \
    --exclude=logs/*.log \
    .
```

### Recovery Procedures

```bash
# Database restoration
psql $DATABASE_URL < backup_20241227_120000.sql

# Application restoration
tar -xzf nous_app_backup_20241227.tar.gz
pip install -r requirements.txt
python main.py
```

## 🔧 Troubleshooting

### Common Issues

#### Database Connection Issues

```python
# Check database connectivity
def test_database_connection():
    try:
        db.engine.execute('SELECT 1')
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
```

#### Performance Issues

```bash
# Check system resources
htop  # Monitor CPU and memory usage
iotop # Monitor disk I/O
netstat -tulpn | grep :5000  # Check port usage
```

#### API Response Issues

```python
# Debug API responses
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable Flask debug mode (development only)
app.config['DEBUG'] = True
```

### Logs and Debugging

```python
# Enhanced logging configuration
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler(
        'logs/nous.log',
        maxBytes=10240000,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
```

### Health Check Script

```bash
#!/bin/bash
# health_check.sh

HEALTH_URL="https://your-app.com/health"
HEALTHZ_URL="https://your-app.com/healthz"

# Basic health check
if curl -s "$HEALTH_URL" | grep -q '"status":"healthy"'; then
    echo "✅ Basic health check passed"
else
    echo "❌ Basic health check failed"
    exit 1
fi

# Detailed health check
if curl -s "$HEALTHZ_URL" | grep -q '"status":"healthy"'; then
    echo "✅ Detailed health check passed"
else
    echo "❌ Detailed health check failed"
    exit 1
fi

echo "🎉 All health checks passed"
```

## 📈 Performance Optimization

### Database Optimization

```sql
-- Optimize query performance
EXPLAIN ANALYZE SELECT * FROM user_activity WHERE user_id = $1 ORDER BY timestamp DESC LIMIT 100;

-- Add missing indexes
CREATE INDEX CONCURRENTLY idx_user_metrics_date ON user_metrics(user_id, date);
CREATE INDEX CONCURRENTLY idx_notifications_created ON notification_queue(created_at);
```

### Application Optimization

```python
# Connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_recycle=300
)
```

### Frontend Optimization

```javascript
// Service worker for caching
const CACHE_NAME = 'nous-v2.0.0';
const urlsToCache = ['/', '/static/styles.css', '/static/app.js', '/static/manifest.json'];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(urlsToCache)));
});
```

## 🎯 Production Checklist

### Pre-Deployment

- [ ] Environment variables configured
- [ ] Database migrations tested
- [ ] SSL certificates installed
- [ ] OAuth credentials verified
- [ ] API keys validated
- [ ] Security headers configured
- [ ] Backup procedures established

### Post-Deployment

- [ ] Health endpoints responding
- [ ] Analytics tracking working
- [ ] Search functionality operational
- [ ] Notifications delivering
- [ ] Financial features secure
- [ ] Collaboration features accessible
- [ ] Mobile PWA functioning
- [ ] Performance metrics within targets

### Ongoing Maintenance

- [ ] Regular database backups
- [ ] Security updates applied
- [ ] Performance monitoring active
- [ ] Error tracking configured
- [ ] User feedback collected
- [ ] Feature usage analyzed
- [ ] Cost optimization reviewed

---

This deployment guide provides comprehensive instructions for deploying NOUS with all its enhanced features. Follow the appropriate method for your infrastructure and ensure all security and monitoring considerations are addressed.
