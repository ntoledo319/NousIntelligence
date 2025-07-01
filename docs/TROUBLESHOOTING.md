# Troubleshooting Guide

## Overview

This guide helps you diagnose and resolve common issues with the NOUS platform.

## Quick Diagnostics

### System Health Check

```bash
# Check application health
curl http://localhost:8000/health

# Check system resources
free -h
df -h
ps aux | grep nous
```

### Service Status

```bash
# Check all services
sudo systemctl status nous
sudo systemctl status postgresql
sudo systemctl status redis
sudo systemctl status nginx
```

## Common Issues

### Application Issues

#### 1. Application Won't Start

**Symptoms:**
- Service fails to start
- 502 Bad Gateway errors
- Connection refused

**Solutions:**

```bash
# Check service status
sudo systemctl status nous
sudo journalctl -u nous -f

# Verify environment variables
cat /home/nous/app/.env

# Test configuration
cd /home/nous/app
source venv/bin/activate
python -c "from app import create_app; app = create_app()"
```

#### 2. Database Connection Issues

**Symptoms:**
- Database connection failed errors
- 500 errors on database operations

**Solutions:**

```bash
# Check PostgreSQL
sudo systemctl status postgresql
psql -U nous_user -d nous_db -c "SELECT 1;"

# Verify connection string
echo $DATABASE_URL

# Check connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"
```

#### 3. Authentication Problems

**Symptoms:**
- Login failures
- OAuth redirect issues
- Session expired errors

**Solutions:**

```bash
# Check OAuth configuration
env | grep GOOGLE_CLIENT

# Test OAuth endpoints
curl -s "https://oauth2.googleapis.com/tokeninfo?id_token=test"

# Clear browser cache and try again
```

### Performance Issues

#### Slow Response Times

**Diagnosis:**
```bash
# Monitor response times
curl -w "%{time_total}" -s -o /dev/null http://localhost:8000/

# Check system resources
htop
iotop
```

**Solutions:**

1. **Database optimization:**
```sql
-- Check slow queries
SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;

-- Update statistics
ANALYZE;
```

2. **Application optimization:**
```bash
# Restart services
sudo systemctl restart nous

# Check configuration
cat /home/nous/app/gunicorn.conf.py
```

#### High Memory Usage

**Diagnosis:**
```bash
# Check memory usage
ps aux --sort=-%mem | head -10
free -h
```

**Solutions:**

```bash
# Restart application
sudo systemctl restart nous

# Monitor over time
watch -n 5 'free -h && ps aux --sort=-%mem | head -5'
```

### AI Service Issues

#### API Failures

**Symptoms:**
- AI responses fail
- Timeout errors
- Rate limit exceeded

**Solutions:**

```bash
# Check API keys
env | grep API_KEY

# Test OpenAI connectivity
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models

# Monitor usage
# Check rate limits in application logs
```

### Drone Swarm Issues

#### Swarm Not Operating

**Symptoms:**
- No autonomous improvements
- Swarm status shows inactive
- Performance not optimizing

**Solutions:**

```bash
# Check swarm status
curl http://localhost:8000/api/drone-swarm/status

# Restart swarm
curl -X POST http://localhost:8000/api/drone-swarm/start

# Check logs for swarm activity
grep -i "drone" /home/nous/app/logs/app.log
```

### SEED Engine Issues

#### Learning Not Working

**Symptoms:**
- No personalized recommendations
- System not adapting to usage patterns
- Optimization not improving

**Solutions:**

```bash
# Check SEED status
curl http://localhost:8000/api/seed/status

# Trigger manual optimization
curl -X POST http://localhost:8000/api/seed/optimize

# Check learning database
sqlite3 /home/nous/app/instance/seed_optimization.db "SELECT COUNT(*) FROM optimization_cycles;"
```

## Error Messages

### HTTP Error Codes

- **500 Internal Server Error**: Check application logs
- **502 Bad Gateway**: Application not running
- **503 Service Unavailable**: Database/service issues
- **401 Unauthorized**: Authentication problems
- **429 Too Many Requests**: Rate limiting active

### Database Errors

- **Connection refused**: PostgreSQL not running
- **Authentication failed**: Wrong credentials
- **Too many connections**: Connection pool exhausted

## Emergency Procedures

### Quick Service Restart

```bash
# Restart all critical services
sudo systemctl restart nous
sudo systemctl restart postgresql
sudo systemctl restart redis
sudo systemctl restart nginx
```

### Emergency Maintenance Mode

```bash
# Create maintenance page
echo "System under maintenance" > /var/www/html/maintenance.html

# Configure nginx for maintenance
# Edit /etc/nginx/sites-available/nous to serve maintenance page
```

### Database Recovery

```bash
# Restore from backup
gunzip -c backup_YYYYMMDD.sql.gz | psql -U nous_user -d nous_db
```

## Getting Help

### Self-Service

1. Check this troubleshooting guide
2. Review application logs: `sudo journalctl -u nous`
3. Check system resources: `htop`, `free -h`, `df -h`
4. Search documentation

### Professional Support

Gather this information before contacting support:

```bash
# System information
uname -a
python --version
pip list

# Service status
sudo systemctl status nous postgresql redis nginx

# Recent logs
sudo journalctl -u nous --since "1 hour ago"

# Configuration (sanitized)
grep -v "SECRET\|KEY\|PASSWORD" /home/nous/app/.env
```

### Support Channels

- **Documentation**: Complete guides and references
- **Community**: GitHub issues and discussions
- **Professional Support**: Email support with priority response
- **Emergency**: Critical issue hotline

---

*Last updated: 2025-07-01*
