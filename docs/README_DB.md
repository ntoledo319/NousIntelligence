# 🗄️ Database Configuration Guide - NOUS Personal Assistant

## Overview

NOUS uses a centralized database configuration system that supports both PostgreSQL (production) and SQLite (development) with automatic fallback and robust error handling.

## Database Architecture

### Primary Configuration

- **Production**: PostgreSQL via `DATABASE_URL` environment variable
- **Development**: SQLite fallback with `pathlib` for reliable paths
- **Configuration**: Centralized in `config/app_config.py`

### File Structure

```
config/
├── app_config.py           # ✅ Centralized database configuration
models/
├── database.py             # ✅ Database initialization module
├── user.py                 # User models
├── analytics_models.py     # Analytics and metrics
├── financial_models.py     # Financial tracking
├── collaboration_models.py # Family/team features
└── enhanced_health_models.py # Health and wellness tracking
instance/
└── nous.db                 # SQLite development database
```

## Configuration Details

### Environment Variables

```bash
# Production (Required)
DATABASE_URL=postgresql://username:password@host:port/database

# Development (Optional - falls back to SQLite)
FLASK_ENV=development
SESSION_SECRET=your-session-secret
```

### Connection Handling

- **PostgreSQL**: Automatic `postgres://` → `postgresql://` conversion for SQLAlchemy compatibility
- **SQLite**: Dynamic path resolution using `pathlib` for cross-platform compatibility
- **Pool Configuration**: Optimized for Replit deployment with pre-ping and recycling

### Usage Examples

#### In Application Code

```python
from config.app_config import AppConfig

# Get database URL with automatic fallback
database_url = AppConfig.get_database_url()

# Validate configuration
issues = AppConfig.validate()
if issues:
    for issue in issues:
        print(f"Config issue: {issue}")
```

#### In Flask App

```python
app.config['SQLALCHEMY_DATABASE_URI'] = AppConfig.get_database_url()
```

## Database Health Monitoring

### Health Check Endpoint

- **URL**: `/healthz`
- **Response**: Database connection status and type
- **Usage**: Deployment monitoring and debugging

### Connection Pool Settings

```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 2,
    'max_overflow': 10,
    'pool_timeout': 30,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}
```

## Migration Strategy

### Current State

- **No Alembic**: Database schema managed through SQLAlchemy models
- **Schema Changes**: Applied via `db.create_all()` in development
- **Production**: Requires manual schema coordination

### Future Recommendations

1. Implement Alembic for production migrations
2. Add database versioning system
3. Create migration testing pipeline

## Troubleshooting

### Common Issues

#### 1. Missing DATABASE_URL in Production

```
Error: DATABASE_URL environment variable is required in production
Solution: Set DATABASE_URL environment variable
```

#### 2. PostgreSQL Connection Issues

```
Error: psycopg2.OperationalError
Solution: Verify DATABASE_URL format and database accessibility
```

#### 3. SQLite Permission Issues

```
Error: OperationalError: unable to open database file
Solution: Check file permissions in instance/ directory
```

### Debug Commands

```bash
# Check database connectivity
python -c "from config.app_config import AppConfig; print(AppConfig.get_database_url())"

# Validate configuration
python -c "from config.app_config import AppConfig; print(AppConfig.validate())"

# Test database connection
python -c "from app import create_app; app = create_app(); print('Database configured successfully')"
```

## Security Considerations

### Environment Variables

- **Never commit** `.env` files with real credentials
- **Use Replit Secrets** for production environment variables
- **Rotate credentials** regularly

### Database Access

- **Connection pooling** prevents connection exhaustion
- **SSL enforcement** in production PostgreSQL connections
- **Prepared statements** via SQLAlchemy prevent SQL injection

## Backup Strategy

### Automated Backups

- **SQLite**: Daily file-based backups to `/tmp/backups/`
- **PostgreSQL**: `pg_dump` scheduled backups (requires compatible client)

### Manual Backup Commands

```bash
# SQLite backup
cp instance/nous.db /tmp/backups/nous-$(date +%s).db

# PostgreSQL backup
pg_dump $DATABASE_URL > backup-$(date +%s).sql
```

---

**Last Updated**: June 27, 2025  
**Database Pathway Overhaul**: Completed by Replit Agent  
**Configuration Status**: ✅ Centralized and Future-Proof
