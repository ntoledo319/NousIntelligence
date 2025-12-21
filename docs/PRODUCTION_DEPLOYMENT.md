# Production Deployment Guide

## Overview

This guide covers deploying NOUS to production environments with security, performance, and reliability best practices.

## Prerequisites

- Ubuntu 20.04+ or similar Linux distribution
- Python 3.11+
- PostgreSQL 13+
- Redis 6+
- Nginx
- SSL certificate

## Quick Deployment

### 1. System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3.11 python3.11-venv python3.11-dev -y
sudo apt install postgresql postgresql-contrib redis-server nginx -y
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Application Setup

```bash
# Create application user
sudo useradd -m -s /bin/bash nous
sudo usermod -aG sudo nous

# Setup application
sudo su - nous
mkdir -p /home/nous/app
cd /home/nous/app
git clone <repository_url> .
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment Configuration

Create `/home/nous/app/.env`:

```bash
FLASK_ENV=production
SECRET_KEY=your-secure-secret-key
SESSION_SECRET=your-session-secret
DATABASE_URL=postgresql://nous_user:password@localhost:5432/nous_db
REDIS_URL=redis://localhost:6379/0

# AI Services
OPENAI_API_KEY=your-openai-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### 4. Database Setup

```bash
# Create database
sudo su - postgres
createdb nous_db
createuser -P nous_user
psql -c "GRANT ALL PRIVILEGES ON DATABASE nous_db TO nous_user;"

# Initialize database
cd /home/nous/app
source venv/bin/activate
flask db upgrade
```

### 5. Service Configuration

Create `/etc/systemd/system/nous.service`:

```ini
[Unit]
Description=NOUS Web Application
After=network.target

[Service]
Type=notify
User=nous
Group=nous
WorkingDirectory=/home/nous/app
Environment=PATH=/home/nous/app/venv/bin
ExecStart=/home/nous/app/venv/bin/gunicorn --config gunicorn.conf.py main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### 6. Web Server Setup

Create `/etc/nginx/sites-available/nous`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 7. Start Services

```bash
# Enable and start application
sudo systemctl daemon-reload
sudo systemctl enable nous
sudo systemctl start nous

# Configure nginx
sudo ln -s /etc/nginx/sites-available/nous /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

## Monitoring and Maintenance

### Health Checks

```bash
# Check application health
curl https://your-domain.com/health

# Check services
sudo systemctl status nous postgresql redis nginx
```

### Backup Procedures

```bash
# Database backup
pg_dump -U nous_user nous_db | gzip > backup_$(date +%Y%m%d).sql.gz

# Application backup
tar -czf app_backup_$(date +%Y%m%d).tar.gz /home/nous/app
```

### Log Monitoring

```bash
# Application logs
sudo journalctl -u nous -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Advanced Features

### Drone Swarm Deployment

The autonomous drone swarm system runs automatically in production:

- Continuous system optimization
- Self-healing capabilities
- Performance monitoring
- Automated issue resolution

### SEED Engine Optimization

The SEED learning engine provides:

- Adaptive performance tuning
- Personalized user experiences
- Cost optimization
- Continuous learning

## Security

- Use strong passwords and API keys
- Keep system updated
- Monitor logs for suspicious activity
- Use HTTPS only
- Implement proper firewall rules

## Troubleshooting

### Common Issues

1. **Application won't start**: Check logs and environment variables
2. **Database connection failed**: Verify PostgreSQL status
3. **SSL certificate issues**: Check certbot renewal

### Support

For deployment support:

- Check application logs: `sudo journalctl -u nous`
- Review documentation
- Contact support team

---

_Last updated: 2025-07-01_
