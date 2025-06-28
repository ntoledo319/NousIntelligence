# 🧹 COMPREHENSIVE DEPENDENCY AUDIT - June 28, 2025
======================================

## Executive Summary
This audit analyzes all dependency files in the NOUS Flask application, identifying conflicts, security issues, and optimization opportunities.

## 1. FULL DEPENDENCY INVENTORY

### Python Dependencies (pyproject.toml) - MODERN CONFIGURATION
| Package | Version | Purpose | Status |
|---------|---------|---------|--------|
| flask | >=3.1.1 | Web Framework | ✅ Current |
| psutil | >=7.0.0 | System Monitoring | ✅ Current |
| requests | >=2.32.3 | HTTP Client | ✅ Current |
| werkzeug | >=3.1.3 | WSGI Utilities | ✅ Current |
| authlib | >=1.3.0 | OAuth Authentication | ✅ Current |

### Python Dependencies (requirements.txt) - LEGACY FILE
| Package | Version | Purpose | Status |
|---------|---------|---------|--------|
| flask | ==3.0.0 | Web Framework | ⚠️ VERSION CONFLICT |
| werkzeug | ==3.0.1 | WSGI Utilities | ⚠️ VERSION CONFLICT |
| flask-sqlalchemy | ==3.1.1 | Database ORM | ❌ MISSING FROM PYPROJECT |
| markupsafe | ==2.1.5 | Template Security | 🔍 TRANSITIVE |
| gunicorn | ==21.2.0 | WSGI Server | ❌ MISSING FROM PYPROJECT |
| python-dotenv | ==0.19.0 | Environment Variables | ❌ MISSING FROM PYPROJECT |
| psutil | ==5.8.0 | System Monitoring | ⚠️ VERSION CONFLICT |
| Flask-Login | ==0.6.2 | User Session Management | ❌ MISSING FROM PYPROJECT |
| Flask-WTF | ==1.0.1 | CSRF Protection | ❌ MISSING FROM PYPROJECT |
| flask-session | - | Session Management | ❌ NO VERSION |
| Flask-Session | - | Session Management | ❌ DUPLICATE |
| Flask-SQLAlchemy | - | Database ORM | ❌ DUPLICATE |
| Flask-Migrate | - | Database Migrations | ❌ NO VERSION |
| psycopg2-binary | - | PostgreSQL Driver | ❌ NO VERSION |
| requests | - | HTTP Client | ❌ NO VERSION |
| soundfile | - | Audio Processing | ❌ NO VERSION |
| librosa | - | Audio Analysis | ❌ NO VERSION |
| google-generativeai | - | AI Integration | ❌ NO VERSION |

### Development Dependencies (requirements_dev.txt)
| Package | Version | Purpose | Status |
|---------|---------|---------|--------|
| pytest | ==7.4.0 | Testing Framework | ✅ Pinned |
| pytest-cov | ==4.1.0 | Coverage Testing | ✅ Pinned |
| pytest-mock | ==3.11.1 | Mock Testing | ✅ Pinned |
| pytest-flask | ==1.2.0 | Flask Testing | ✅ Pinned |
| flake8 | ==6.1.0 | Code Linting | ✅ Pinned |
| black | ==23.7.0 | Code Formatting | ✅ Pinned |
| mypy | ==1.5.1 | Type Checking | ✅ Pinned |
| isort | ==5.12.0 | Import Sorting | ✅ Pinned |
| bandit | ==1.7.5 | Security Linting | ✅ Pinned |
| coverage | ==7.3.0 | Test Coverage | ✅ Pinned |
| werkzeug | ==2.3.7 | WSGI Utilities | ⚠️ TRIPLE CONFLICT |
| Flask-Testing | ==0.8.1 | Flask Test Utilities | ✅ Pinned |

## 2. CRITICAL CONFLICTS IDENTIFIED

### Version Conflicts
1. **werkzeug**: Three different versions specified
   - pyproject.toml: >=3.1.3
   - requirements.txt: ==3.0.1
   - requirements_dev.txt: ==2.3.7

2. **flask**: Two different versions
   - pyproject.toml: >=3.1.1
   - requirements.txt: ==3.0.0

3. **psutil**: Two different versions
   - pyproject.toml: >=7.0.0
   - requirements.txt: ==5.8.0

### Missing Dependencies in pyproject.toml
- flask-sqlalchemy (critical for database functionality)
- gunicorn (critical for production deployment)
- python-dotenv (environment variable management)
- Flask-Login (user authentication)
- Flask-WTF (CSRF protection)
- Flask-Session (session management)
- Flask-Migrate (database migrations)
- psycopg2-binary (PostgreSQL connection)
- google-generativeai (AI functionality)
- soundfile & librosa (audio features)

### Duplicate Dependencies
- Flask-Session vs flask-session
- Flask-SQLAlchemy vs flask-sqlalchemy

## 3. SECURITY ANALYSIS

### Unpinned Dependencies (High Risk)
- flask-session
- Flask-Session
- Flask-SQLAlchemy
- Flask-Migrate
- psycopg2-binary
- requests (in requirements.txt)
- soundfile
- librosa
- google-generativeai

### Outdated Dependencies
- python-dotenv: 0.19.0 (latest: 1.0.1)
- psutil: 5.8.0 in requirements.txt (latest: 5.9.8)

## 4. RECOMMENDED FIXES

### Phase 1: Immediate Conflict Resolution
1. **Consolidate to pyproject.toml** as the single source of truth
2. **Remove requirements.txt** after migration
3. **Update werkzeug** to consistent version >=3.1.3
4. **Pin all missing dependencies** with current stable versions

### Phase 2: Security Hardening
1. **Pin all unpinned dependencies**
2. **Update outdated packages** to latest secure versions
3. **Add security scanning** to CI/CD pipeline

### Phase 3: Optimization
1. **Group dependencies** by function (core, auth, db, ai, audio)
2. **Add optional dependency groups** for features
3. **Implement dependency caching** strategies

## 5. PROPOSED NEW pyproject.toml

```toml
[project]
name = "nous-personal-assistant"
version = "0.2.0"
description = "AI-powered personal assistant with comprehensive life management"
requires-python = ">=3.11"
dependencies = [
    # Core Web Framework
    "flask>=3.1.1",
    "werkzeug>=3.1.3",
    "gunicorn>=22.0.0",
    
    # Database & ORM
    "flask-sqlalchemy>=3.1.1",
    "flask-migrate>=4.0.7",
    "psycopg2-binary>=2.9.9",
    
    # Authentication & Security
    "authlib>=1.3.0",
    "flask-login>=0.6.3",
    "flask-wtf>=1.2.1",
    "flask-session>=0.8.0",
    
    # Environment & Configuration
    "python-dotenv>=1.0.1",
    
    # HTTP & API
    "requests>=2.32.3",
    
    # System Monitoring
    "psutil>=5.9.8",
    
    # AI Integration
    "google-generativeai>=0.8.0",
    
    # Audio Processing (Optional)
    "soundfile>=0.12.1",
    "librosa>=0.10.1",
]

[project.optional-dependencies]
audio = ["soundfile>=0.12.1", "librosa>=0.10.1"]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.12.0",
    "pytest-flask>=1.3.0",
    "flask-testing>=0.8.1",
    "flake8>=7.0.0",
    "black>=24.0.0",
    "mypy>=1.8.0",
    "isort>=5.13.0",
    "bandit>=1.7.6",
    "coverage>=7.4.0",
]
```

## 6. ACTION PLAN

### Immediate Actions (Next 30 minutes)
1. ✅ Backup current dependency files
2. 🔄 Create unified pyproject.toml
3. 🔄 Remove legacy requirements.txt
4. 🔄 Update requirements_dev.txt references
5. 🔄 Test application startup

### Validation Steps
1. Install from new pyproject.toml
2. Run test suite
3. Start development server
4. Verify all features load correctly

### Risk Mitigation
- All changes are backed up in `/tmp/backups/dep-20250628_023202/`
- Can revert immediately if issues occur
- Staged approach allows incremental validation

## 7. NEXT STEPS AFTER AUDIT
1. User approval for proposed changes
2. Implementation of new dependency structure
3. Comprehensive testing
4. Documentation updates
5. CI/CD pipeline adjustments

---
**Audit completed at:** $(date)
**Backup location:** /tmp/backups/dep-20250628_023202/
**Status:** Ready for implementation pending user approval