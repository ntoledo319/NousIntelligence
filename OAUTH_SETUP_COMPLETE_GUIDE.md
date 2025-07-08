# 🔐 Complete Google OAuth Setup Guide for NOUS Intelligence

## 📋 Table of Contents
1. [Current Status](#current-status)
2. [Root Causes](#root-causes)
3. [Step-by-Step Fix](#step-by-step-fix)
4. [Testing OAuth](#testing-oauth)
5. [Troubleshooting](#troubleshooting)

---

## 🚨 Current Status

Based on the diagnostic results:
- ❌ **No OAuth credentials are set** in your environment
- ✅ All OAuth code files exist and are properly structured
- ❌ Environment variable name mismatch has been fixed
- ❌ Database connection is not configured

## 🔍 Root Causes

1. **Missing Environment Variables**: No OAuth credentials are configured
2. **Variable Name Mismatch**: Code was looking for `GOOGLE_OAUTH_CLIENT_ID` but documentation showed `GOOGLE_CLIENT_ID` (now fixed)
3. **Missing Dependencies**: Python packages like `authlib` need to be installed
4. **No Database Configuration**: `DATABASE_URL` is not set

---

## 🛠️ Step-by-Step Fix

### Step 1: Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API" and enable it
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Web application"
   - Add these Authorized redirect URIs:
     ```
     http://localhost:8080/auth/google/callback
     http://localhost:8080/callback/google
     https://your-app-name.replit.app/auth/google/callback
     https://your-app-name.replit.app/callback/google
     ```
5. Copy your credentials:
   - Client ID: `[numbers]-[random].apps.googleusercontent.com`
   - Client Secret: `GOCSPX-[random characters]`

### Step 2: Set Environment Variables

#### Option A: Local Development (.env file)

1. Create a `.env` file in your project root:
```bash
# Generate a secure session secret
python3 -c "import secrets; print('SESSION_SECRET=' + secrets.token_urlsafe(32))"
```

2. Add to `.env`:
```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-secret-here
SESSION_SECRET=your-generated-secret-from-above
DATABASE_URL=sqlite:///nous.db
```

3. Load environment variables:
```bash
export $(cat .env | xargs)
```

#### Option B: Replit Deployment

1. Go to your Replit project
2. Click on "Secrets" (🔒 icon) in the left sidebar
3. Add these secrets:
   - Key: `GOOGLE_CLIENT_ID`, Value: your client ID
   - Key: `GOOGLE_CLIENT_SECRET`, Value: your client secret
   - Key: `SESSION_SECRET`, Value: (generate with command above)
   - Key: `DATABASE_URL`, Value: `sqlite:///nous.db`

### Step 3: Install Dependencies

```bash
pip install authlib flask flask-login flask-sqlalchemy
```

Or if using requirements.txt:
```bash
pip install -r requirements.txt
```

### Step 4: Verify Setup

Run the verification script:
```bash
python3 test_oauth_simple.py
```

You should see all green checkmarks (✅) for environment variables.

---

## 🧪 Testing OAuth

### 1. Quick Test
```bash
# Test if OAuth service is configured
python3 -c "from utils.google_oauth import oauth_service; print('OAuth configured:', oauth_service.is_configured())"
```

Expected output: `OAuth configured: True`

### 2. Full Application Test

1. Start the application:
```bash
python3 app.py
```

2. Visit: `http://localhost:8080/auth/login`

3. Click "Sign in with Google"

4. You should be redirected to Google's login page

### 3. Debug Mode Test

Create and run this test script:
```python
# test_oauth_flow.py
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from utils.google_oauth import oauth_service

with app.app_context():
    print("OAuth Service Configured:", oauth_service.is_configured())
    print("OAuth Client ID:", os.environ.get('GOOGLE_CLIENT_ID', 'NOT SET')[:20] + '...')
    print("Session Secret Set:", bool(os.environ.get('SESSION_SECRET')))
    print("Database URL Set:", bool(os.environ.get('DATABASE_URL')))
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. "OAuth not configured" error
- **Cause**: Environment variables not set
- **Fix**: Ensure all 4 environment variables are set correctly
- **Check**: Run `env | grep GOOGLE` to verify

#### 2. "redirect_uri_mismatch" error
- **Cause**: Callback URL doesn't match Google Console
- **Fix**: Add exact URL from error message to Google Console
- **Note**: URLs must match exactly (http vs https, trailing slashes)

#### 3. "Authentication failed" after Google login
- **Cause**: State token mismatch or expired session
- **Fix**: Clear browser cookies and try again
- **Check**: Ensure SESSION_SECRET is set and consistent

#### 4. Database errors
- **Cause**: DATABASE_URL not set or database not initialized
- **Fix**: Set DATABASE_URL and run migrations
- **Initialize**: `python3 -c "from app import app, db; app.app_context().push(); db.create_all()"`

### Debug Checklist

Run this comprehensive check:
```bash
# 1. Check environment
echo "=== Environment Check ==="
echo "GOOGLE_CLIENT_ID: $([ -z "$GOOGLE_CLIENT_ID" ] && echo "NOT SET" || echo "SET")"
echo "GOOGLE_CLIENT_SECRET: $([ -z "$GOOGLE_CLIENT_SECRET" ] && echo "NOT SET" || echo "SET")"
echo "SESSION_SECRET: $([ -z "$SESSION_SECRET" ] && echo "NOT SET" || echo "SET")"
echo "DATABASE_URL: $([ -z "$DATABASE_URL" ] && echo "NOT SET" || echo "SET")"

# 2. Check Python dependencies
echo -e "\n=== Dependencies Check ==="
python3 -c "import authlib; print('authlib:', authlib.__version__)" 2>/dev/null || echo "authlib: NOT INSTALLED"
python3 -c "import flask; print('flask:', flask.__version__)" 2>/dev/null || echo "flask: NOT INSTALLED"

# 3. Check OAuth service
echo -e "\n=== OAuth Service Check ==="
python3 -c "from utils.google_oauth import oauth_service; print('OAuth configured:', oauth_service.is_configured())" 2>/dev/null || echo "OAuth service: FAILED TO LOAD"
```

---

## 📝 Final Notes

1. **Security**: Never commit `.env` files or secrets to version control
2. **HTTPS**: In production, always use HTTPS for OAuth callbacks
3. **Session Management**: Ensure SESSION_SECRET is truly random and never shared
4. **Token Storage**: OAuth tokens are stored encrypted in the database
5. **Refresh Tokens**: The system automatically handles token refresh

If you still have issues after following this guide, the problem might be:
- Network/firewall blocking Google OAuth
- Browser extensions interfering (try incognito mode)
- Cached redirect URLs (wait 5-10 minutes after Google Console changes)

For additional help, check the logs:
```bash
# Check application logs
tail -f logs/app.log

# Check for OAuth-specific errors
grep -i oauth logs/error.log
``` 