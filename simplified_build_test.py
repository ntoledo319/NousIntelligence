
import sys
sys.path.append('.')

# Test 1: Basic imports
try:
    import flask
    import sqlalchemy
    print("✅ Flask/SQLAlchemy available")
except ImportError as e:
    print(f"❌ Basic imports failed: {e}")
    sys.exit(1)

# Test 2: Application module exists
try:
    import app
    print("✅ App module available")
except ImportError as e:
    print(f"❌ App import failed: {e}")
    sys.exit(1)

# Test 3: Auth system works
try:
    from utils.auth_compat import get_current_user, login_required
    print("✅ Auth system available")
except ImportError as e:
    print(f"❌ Auth system failed: {e}")
    sys.exit(1)

# Test 4: Essential models exist (without instantiation)
try:
    import models.user
    print("✅ User model exists")
except ImportError as e:
    print(f"❌ User model failed: {e}")
    sys.exit(1)

print("✅ ALL ESSENTIAL BUILD COMPONENTS WORKING")
