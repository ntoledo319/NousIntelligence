# NOUS Authentication System Documentation

## Overview

The NOUS platform implements a multi-layered authentication system supporting Google OAuth, Demo Mode, and API token authentication. This document provides a comprehensive guide for developers and administrators.

---

## Authentication Methods

### 1. Google OAuth (Primary Method)

**Implementation:** `@/Users/nicholastoledo/CascadeProjects/NousIntelligence/utils/google_oauth.py`

**Features:**
- HMAC-signed state tokens with CSRF protection
- Client fingerprinting (IP + User-Agent)
- Token encryption at rest
- Automatic token refresh
- Secure redirect URI validation

**Configuration:**
```bash
# Required environment variables
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
```

**Routes:**
- `/auth/login` - Login page with Google OAuth button
- `/auth/google` - Initiates OAuth flow
- `/callback/google` - OAuth callback handler (configure in Google Cloud Console)

**Security Features:**
- State token expires in 10 minutes
- Timing-safe comparisons prevent timing attacks
- IP fingerprinting logs suspicious activity
- Tokens encrypted before database storage

---

### 2. Demo Mode (Testing/Preview)

**Implementation:** `@/Users/nicholastoledo/CascadeProjects/NousIntelligence/routes/auth_routes.py:109-154`

**Purpose:** Allow users to preview the platform without creating an account

**Features:**
- CSRF-protected activation
- 2-hour session expiration
- Unique session ID per activation
- No persistent data storage

**Access:**
- Click "Try Demo Mode" button on login page
- Automatic activation for unauthenticated API requests (with demo flag)

**Security Considerations:**
- CSRF bypass only allowed in non-production testing
- Sessions automatically expire
- Limited functionality compared to authenticated users

---

### 3. API Token Authentication

**Implementation:** `@/Users/nicholastoledo/CascadeProjects/NousIntelligence/utils/unified_auth.py:79-106`

**Usage:**
```http
Authorization: Bearer <your_api_token>
```

**Features:**
- Stateless authentication for API clients
- Falls back to session auth if no token provided
- Validates through APIKeyManager when available

---

## Authentication Utilities

### Primary System: `unified_auth.py`

**Use this for:** Most route decorators and authentication checks

**Key Functions:**
```python
from utils.unified_auth import login_required, demo_allowed, get_current_user, is_authenticated

@app.route('/protected')
@login_required
def protected_route():
    user = get_current_user()
    return f"Hello {user['name']}"

@app.route('/public-or-demo')
@demo_allowed
def public_route():
    # Allows authenticated users OR demo mode
    pass
```

**Supported Session Keys:**
- `session['user']` - Dict with user info (preferred)
- `session['user_id']` - Legacy support

---

### Alternative: `simple_auth.py`

**Use for:** Simple session-based auth without external dependencies

**Key Functions:**
```python
from utils.simple_auth import SimpleAuth

SimpleAuth.init_app(app)
SimpleAuth.login_user(user_data)
SimpleAuth.logout_user()
SimpleAuth.is_authenticated()
```

---

### OAuth-Specific: `google_oauth.py`

**Use for:** Direct OAuth operations, token refresh, etc.

**Key Functions:**
```python
from utils.google_oauth import oauth_service

# Check if configured
if oauth_service.is_configured():
    # Initiate login
    return oauth_service.get_authorization_url(redirect_uri)
    
# Handle callback
user = oauth_service.handle_callback(redirect_uri)

# Refresh token
new_token = oauth_service.refresh_token(user)
```

---

## Security Features

### CSRF Protection

**Implementation:** `@/Users/nicholastoledo/CascadeProjects/NousIntelligence/utils/csrf_protection.py`

- Flask-WTF CSRFProtect enabled globally
- Automatic token injection in templates: `{{ csrf_token() }}`
- Testing mode disables CSRF for API tests
- All state-changing forms require CSRF tokens

**Example Form:**
```html
<form method="POST" action="/auth/logout">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <button type="submit">Logout</button>
</form>
```

---

### Rate Limiting

**Implementation:** `@/Users/nicholastoledo/CascadeProjects/NousIntelligence/utils/rate_limiter.py`

**Preconfigured Limits:**
- Login attempts: 5 per minute
- OAuth requests: 10 per minute

**Usage:**
```python
from utils.rate_limiter import rate_limit

@app.route('/api/endpoint')
@rate_limit(limit=60, window=60)  # 60 requests per minute
def my_endpoint():
    pass
```

**Custom Rate Limits:**
```python
@rate_limit(limit=100, window=3600, per="user")  # Per user
@rate_limit(limit=10, window=60, per="ip")       # Per IP
```

---

### Session Security

**Implementation:** `@/Users/nicholastoledo/CascadeProjects/NousIntelligence/utils/session_security.py`

**Features:**
- HTTPOnly, Secure, SameSite=Lax cookies
- 8-hour regular session timeout
- 2-hour demo session timeout
- IP change detection and logging
- Automatic session rotation on expiry

**Configuration:**
```python
SESSION_COOKIE_SECURE=True          # HTTPS only
SESSION_COOKIE_HTTPONLY=True        # No JavaScript access
SESSION_COOKIE_SAMESITE='Lax'       # CSRF protection
PERMANENT_SESSION_LIFETIME=8 hours  # Auto logout
```

---

### Security Headers

**Implementation:** `@/Users/nicholastoledo/CascadeProjects/NousIntelligence/utils/security_headers.py`

**Applied to All Responses:**
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`
- Content Security Policy with Google OAuth domains whitelisted
- `Referrer-Policy: strict-origin-when-cross-origin`

---

## Blueprint Registration

**Core Auth Blueprints:**

1. **`auth_bp`** (`routes/auth_routes.py`) - Main authentication routes
   - `/auth/login` - Login page
   - `/auth/google` - Initiate OAuth
   - `/auth/demo-mode` - Activate demo
   - `/auth/logout` - User logout
   - `/auth/status` - Auth status check
   - `/auth/profile` - User profile

2. **`callback_bp`** (`routes/callback_routes.py`) - OAuth callbacks
   - `/callback/google` - Google OAuth callback
   - `/auth/google/callback` - Alternative callback URL
   - `/oauth2callback` - Legacy callback support

3. **`simple_auth_api`** (`routes/simple_auth_api.py`) - API authentication
   - `/api/auth/login` - API login endpoint
   - `/api/auth/logout` - API logout endpoint

---

## Common Decorators

### Authentication Decorators

```python
from utils.unified_auth import login_required, demo_allowed
from utils.user_decorators import (
    authenticated_user,
    public_or_demo,
    therapeutic_endpoint,
    admin_endpoint
)

# Require authentication (no demo)
@login_required
def strict_auth_route():
    pass

# Allow demo mode OR authenticated users
@demo_allowed
def flexible_route():
    pass

# Complete auth + session validation + tracking
@authenticated_user
def full_auth_route():
    pass

# Public access with demo fallback + crisis detection
@therapeutic_endpoint
def therapy_route():
    pass

# Admin only with rate limiting
@admin_endpoint
def admin_route():
    pass
```

---

## User Context Access

### In Routes:
```python
from utils.unified_auth import get_current_user, is_authenticated

def my_route():
    if is_authenticated():
        user = get_current_user()
        user_id = user['id']
        user_email = user['email']
        is_demo = user.get('demo_mode', False)
```

### In Templates:
```html
{% if current_user %}
    <p>Welcome, {{ current_user.name }}</p>
{% endif %}

{% if is_demo_mode %}
    <div class="alert">You're in demo mode</div>
{% endif %}
```

---

## Testing Considerations

### Test Mode Behaviors:
- CSRF validation disabled for API tests
- Any Bearer token accepted as valid
- Demo mode CSRF bypass allowed (non-production only)

### Testing Authentication:
```python
def test_protected_route(client):
    # Set up session
    with client.session_transaction() as sess:
        sess['user'] = {
            'id': 'test_user',
            'name': 'Test User',
            'email': 'test@example.com'
        }
    
    # Make authenticated request
    response = client.get('/protected-route')
    assert response.status_code == 200
```

---

## Troubleshooting

### OAuth Not Working

1. **Check credentials:**
   ```bash
   echo $GOOGLE_CLIENT_ID
   echo $GOOGLE_CLIENT_SECRET
   ```

2. **Verify callback URL in Google Console:**
   - Must exactly match: `https://your-domain.com/callback/google`
   - Include all deployment environments (localhost, staging, production)

3. **Check logs:**
   ```python
   logger.info("OAuth is configured: %s", oauth_service.is_configured())
   ```

### CSRF Token Errors

1. **Form missing token:**
   ```html
   <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
   ```

2. **API requests:**
   - Include `X-CSRFToken` header
   - Or disable CSRF for specific API routes (not recommended)

### Session Issues

1. **Check SECRET_KEY is set:**
   ```bash
   echo $SECRET_KEY
   ```

2. **Verify session cookie settings:**
   - Ensure `SESSION_COOKIE_SECURE=True` only in HTTPS environments
   - Check browser cookie settings

### Rate Limiting

1. **View current status:**
   ```python
   from utils.rate_limiter import get_rate_limit_status
   status = get_rate_limit_status()
   print(f"Remaining: {status['remaining']}/{status['limit']}")
   ```

2. **Clear rate limits (development):**
   ```python
   rate_limiter.requests.clear()
   ```

---

## Security Best Practices

### DO:
✅ Always use HTTPS in production  
✅ Rotate SECRET_KEY regularly  
✅ Use strong, unique OAuth client secrets  
✅ Enable rate limiting on all auth endpoints  
✅ Log authentication failures for monitoring  
✅ Implement session timeout  
✅ Use CSRF protection on all state-changing operations  

### DON'T:
❌ Store OAuth secrets in version control  
❌ Disable CSRF in production  
❌ Use weak SECRET_KEY values  
❌ Allow unlimited login attempts  
❌ Trust client-provided authentication data  
❌ Store plaintext passwords or tokens  

---

## Production Deployment Checklist

- [ ] Set strong `SECRET_KEY` and `SESSION_SECRET`
- [ ] Configure real OAuth credentials (not placeholders)
- [ ] Set `ENV=production` environment variable
- [ ] Enable `SESSION_COOKIE_SECURE=True`
- [ ] Configure allowed OAuth redirect URIs in Google Console
- [ ] Set up token encryption keys
- [ ] Enable rate limiting
- [ ] Configure session timeout appropriately
- [ ] Test OAuth flow end-to-end
- [ ] Verify CSRF protection is active
- [ ] Set up authentication monitoring/alerting
- [ ] Review and limit demo mode access if needed

---

## Additional Resources

- **Google OAuth Setup:** `@/Users/nicholastoledo/CascadeProjects/NousIntelligence/OAUTH_SETUP.md`
- **Security Configuration:** `@/Users/nicholastoledo/CascadeProjects/NousIntelligence/utils/security_headers.py`
- **Rate Limiting:** `@/Users/nicholastoledo/CascadeProjects/NousIntelligence/utils/rate_limiter.py`
- **User Decorators:** `@/Users/nicholastoledo/CascadeProjects/NousIntelligence/utils/user_decorators.py`

---

*Last Updated: January 2026*  
*Audit Completed: Full authentication system review and fixes applied*
