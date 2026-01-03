# NOUS Production Deployment Checklist

## Pre-Deployment Requirements

### Environment Variables (CRITICAL)
- [ ] `SESSION_SECRET` - 32+ character random string (REQUIRED)
- [ ] `DATABASE_URL` - PostgreSQL connection string
- [ ] `GOOGLE_CLIENT_ID` - Google OAuth client ID
- [ ] `GOOGLE_CLIENT_SECRET` - Google OAuth secret
- [ ] `TOKEN_ENCRYPTION_KEY` - For OAuth token encryption
- [ ] `SPOTIFY_CLIENT_ID` - Spotify app client ID
- [ ] `SPOTIFY_CLIENT_SECRET` - Spotify app secret
- [ ] `REDIS_URL` - For rate limiting (optional, uses memory otherwise)
- [ ] `FLASK_ENV` - Set to 'production'

### Generate Secrets
```bash
# SESSION_SECRET
python -c 'import secrets; print(secrets.token_hex(32))'

# TOKEN_ENCRYPTION_KEY
python -c 'import secrets; print(secrets.token_hex(32))'
```

### Database Setup
- [ ] PostgreSQL database created
- [ ] Database migrations run: `flask db upgrade`
- [ ] Database backups configured
- [ ] Connection pooling configured (handled by SQLAlchemy)

### OAuth Configuration
- [ ] Google OAuth app created in Google Cloud Console
- [ ] Authorized redirect URIs configured (https://yourdomain.com/callback/google)
- [ ] Spotify app created in Spotify Developer Dashboard
- [ ] Spotify redirect URI configured (https://yourdomain.com/callback/spotify)

### Security Hardening
- [ ] Rate limiting enabled (Flask-Limiter configured)
- [ ] CSRF protection enabled on all POST routes
- [ ] HTTPS enforced (handled by reverse proxy/load balancer)
- [ ] Security headers configured (done by security_middleware)
- [ ] Input validation on all endpoints
- [ ] SQL injection protection (parameterized queries used)

### Dependencies
- [ ] Install production dependencies: `pip install -r requirements.txt` or `poetry install`
- [ ] Install Flask-Limiter: `pip install Flask-Limiter`
- [ ] Install Google client libraries: `pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client`
- [ ] Install Spotipy: `pip install spotipy`

### Testing
- [ ] All unit tests passing: `pytest tests/`
- [ ] Integration tests for new routes passing
- [ ] Load testing completed
- [ ] Security scan completed

### Monitoring & Logging
- [ ] Error tracking configured (Sentry recommended)
- [ ] Log aggregation set up (CloudWatch, Datadog, etc.)
- [ ] Performance monitoring enabled
- [ ] Health check endpoint accessible: `/health`, `/healthz`

### Infrastructure
- [ ] Reverse proxy configured (Nginx, Caddy, etc.)
- [ ] SSL/TLS certificates installed
- [ ] CDN configured for static assets (optional)
- [ ] Auto-scaling configured (if applicable)
- [ ] Backup strategy implemented

## Deployment Steps

### 1. Pre-Deploy Verification
```bash
# Verify environment variables
python -c "from config.app_config import AppConfig; AppConfig.validate()"

# Run tests
pytest tests/ -v

# Check for security issues
bandit -r . -ll
```

### 2. Database Migration
```bash
# Backup database first!
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Run migrations
flask db upgrade
```

### 3. Deploy Application
```bash
# Pull latest code
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Restart application
sudo systemctl restart nous-app  # or your deployment method
```

### 4. Post-Deploy Verification
```bash
# Check health endpoint
curl https://yourdomain.com/health

# Check API endpoints
curl https://yourdomain.com/api/v1/therapeutic/crisis/resources

# Monitor logs
tail -f /var/log/nous/app.log
```

### 5. Smoke Tests
- [ ] Landing page loads
- [ ] Google OAuth login works
- [ ] API endpoints respond correctly
- [ ] Database queries work
- [ ] No errors in logs

## Rollback Procedure

If deployment fails:
```bash
# 1. Restore previous version
git checkout <previous-commit>

# 2. Restore database if migrations were run
psql $DATABASE_URL < backup_YYYYMMDD.sql

# 3. Restart application
sudo systemctl restart nous-app

# 4. Verify rollback
curl https://yourdomain.com/health
```

## Post-Deployment Tasks

### Immediate (Within 24 hours)
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Verify user flows work end-to-end
- [ ] Review security logs

### Short-term (Within 1 week)
- [ ] Analyze usage patterns
- [ ] Optimize slow queries
- [ ] Address any bugs reported
- [ ] Update documentation

### Long-term (Ongoing)
- [ ] Regular security audits
- [ ] Performance optimization
- [ ] Feature feedback collection
- [ ] Dependency updates

## Common Issues & Solutions

### Issue: Session invalidation on restart
**Solution**: Ensure `SESSION_SECRET` is set in environment, not generated at runtime

### Issue: Rate limiting not working
**Solution**: Install Flask-Limiter and configure REDIS_URL

### Issue: OAuth errors
**Solution**: Verify client IDs/secrets and redirect URIs match OAuth provider configuration

### Issue: Database connection errors
**Solution**: Check DATABASE_URL format (must be `postgresql://` not `postgres://`)

### Issue: CSRF validation failures
**Solution**: Ensure CSRF tokens are included in POST requests

## Performance Targets

- Response time: < 200ms (p95)
- Availability: 99.9%
- Error rate: < 0.1%
- Database connection pool: 20-50 connections

## Scaling Considerations

### Horizontal Scaling
- Use Redis for sessions (not memory)
- Use Redis for rate limiting
- Configure database connection pooling
- Load balancer health checks

### Vertical Scaling
- Monitor CPU/memory usage
- Optimize database queries
- Cache frequently accessed data
- Use CDN for static assets

## Contact Information

**On-Call Engineer**: [Your contact]  
**Database Admin**: [DBA contact]  
**Security Lead**: [Security contact]

## Emergency Procedures

### Total System Failure
1. Enable maintenance mode
2. Notify users via status page
3. Investigate root cause
4. Restore from backups if needed
5. Gradual traffic restoration

### Security Incident
1. Isolate affected systems
2. Rotate all credentials
3. Audit access logs
4. Patch vulnerability
5. Incident report

---

**Last Updated**: Implementation phase  
**Next Review**: After first production deployment
