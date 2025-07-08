# NOUS Platform Deployment Guide

## Table of Contents
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Database Setup](#database-setup)
- [Application Deployment](#application-deployment)
- [Production Configuration](#production-configuration)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **Python**: 3.9 or higher
- **Database**: PostgreSQL 13+ (recommended) or SQLite for development
- **Cache**: Redis 6+ (optional but recommended)
- **Node.js**: 16+ (for frontend builds)
- **Memory**: Minimum 2GB RAM, 4GB+ recommended
- **Storage**: 10GB+ available space

### External Services
- Google OAuth (for authentication)
- Email service (SMTP)
- AI API keys (OpenAI, etc.)

## Environment Setup

### 1. Clone Repository
```bash
git clone https://github.com/nous/platform.git
cd platform
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Python dependencies
pip install -r requirements.txt

# Development dependencies (optional)
pip install -r requirements-dev.txt

# Frontend dependencies
npm install
```

### 4. Environment Variables
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your values
nano .env
```

Required environment variables:
```bash
# Database
DATABASE_URL=postgresql://username:password@localhost/nous_platform

# Security
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here

# OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# AI Services
OPENAI_API_KEY=your-openai-api-key

# Email (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email
SMTP_PASSWORD=your-email-password

# Redis (optional)
REDIS_URL=redis://localhost:6379/0
```

## Database Setup

### PostgreSQL (Recommended)
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE nous_platform;
CREATE USER nous_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE nous_platform TO nous_user;
\q
```

### Run Migrations
```bash
# Initialize database
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

## Application Deployment

### Development
```bash
# Start development server
flask run

# Or with auto-reload
FLASK_ENV=development flask run --reload
```

### Production

#### Using Gunicorn
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -c gunicorn.conf.py app:app
```

#### Using Docker
```bash
# Build image
docker build -t nous-platform .

# Run container
docker run -d \
  --name nous-app \
  -p 8000:8000 \
  --env-file .env \
  nous-platform
```

#### Using Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Production Configuration

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static {
        alias /path/to/nous/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
0 12 * * * /usr/bin/certbot renew --quiet
```

### System Service
```bash
# Create systemd service
sudo nano /etc/systemd/system/nous.service
```

```ini
[Unit]
Description=NOUS Platform
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/nous
Environment=PATH=/path/to/nous/venv/bin
ExecStart=/path/to/nous/venv/bin/gunicorn -c gunicorn.conf.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable nous.service
sudo systemctl start nous.service
sudo systemctl status nous.service
```

## Monitoring & Maintenance

### Health Checks
- **Application**: `GET /api/health/health`
- **Database**: Monitor connection pool
- **Cache**: Monitor Redis if used
- **Disk Space**: Monitor logs and uploads

### Log Management
```bash
# View application logs
tail -f /var/log/nous/app.log

# Rotate logs
sudo logrotate /etc/logrotate.d/nous
```

### Backup Strategy
```bash
# Database backup
pg_dump nous_platform > backup_$(date +%Y%m%d).sql

# Application backup
tar -czf app_backup_$(date +%Y%m%d).tar.gz /path/to/nous
```

### Updates
```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Run migrations
flask db upgrade

# Restart service
sudo systemctl restart nous.service
```

## Troubleshooting

### Common Issues

#### Database Connection Error
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U nous_user -d nous_platform
```

#### Permission Errors
```bash
# Fix file permissions
sudo chown -R www-data:www-data /path/to/nous
sudo chmod -R 755 /path/to/nous
```

#### Memory Issues
```bash
# Check memory usage
free -h
top -p $(pgrep gunicorn)

# Restart application
sudo systemctl restart nous.service
```

### Performance Issues
- Enable Redis caching
- Optimize database queries
- Use CDN for static files
- Monitor application metrics

### Support
- Check logs: `/var/log/nous/`
- GitHub Issues: https://github.com/nous/platform/issues
- Documentation: https://docs.nous-platform.com
