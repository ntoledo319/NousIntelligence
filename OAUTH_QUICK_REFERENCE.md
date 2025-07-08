# 🚀 OAuth Quick Reference Card

## ✅ Your OAuth is NOW CONFIGURED!

### 📋 Your Credentials (Found in System):
```
Client ID: 1015094007473-337qm1ofr5htlodjmsf2p6r3fcht6pg2.apps.googleusercontent.com
Client Secret: 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
```

### 🔄 To Use OAuth in Future Sessions:
```bash
# Quick setup - run this each time you open a new terminal
source ./setup_oauth_found_creds.sh
```

### 🧪 Test OAuth is Working:
```bash
# Simple test (no dependencies needed)
python3 test_oauth_simple.py

# Should show all green checkmarks ✅
```

### 🚨 Missing Dependency:
You need to install Python packages:
```bash
pip install flask flask-login flask-sqlalchemy authlib python-dotenv
# OR
pip install -e .  # if using pyproject.toml
```

### 🎯 Quick Start:
```bash
# 1. Set up environment (if not already done)
source ./setup_oauth_found_creds.sh

# 2. Install dependencies
pip install flask authlib flask-login flask-sqlalchemy

# 3. Run the app
python3 app.py

# 4. Visit http://localhost:8080/auth/login
# 5. Click "Sign in with Google"
```

### 📱 Google Cloud Console Checklist:
Ensure these redirect URIs are added:
- [ ] `http://localhost:8080/auth/google/callback`
- [ ] `http://localhost:5000/auth/google/callback`  
- [ ] `https://nous.replit.app/auth/google/callback`
- [ ] `https://[your-repl-name].replit.app/auth/google/callback`

### 🔍 Debugging Commands:
```bash
# Check if credentials are set
echo $GOOGLE_CLIENT_ID

# Test OAuth service (after installing authlib)
python3 -c "from utils.google_oauth import oauth_service; print(oauth_service.is_configured())"
```

---
**Remember**: Run `source ./setup_oauth_found_creds.sh` each time you start a new terminal session! 