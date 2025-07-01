# SQL Security Fix Guide

## Files requiring review:
- security_fix_orchestrator.py
- utils/enhanced_caching_system.py
- utils/enhanced_voice_emotion.py
- utils/enhanced_visual_intelligence.py
- utils/enhanced_therapeutic_ai.py
- utils/enhanced_ai_system.py

## Secure patterns to use:

1. Use SQLAlchemy ORM methods instead of raw SQL
2. Use parameterized queries with bound parameters
3. Validate and sanitize all user inputs

## Examples:

### ❌ Vulnerable (Don't use):
```python
query = f"SELECT * FROM users WHERE id = {user_id}"
db.session.execute(query)
```

### ✅ Secure (Use instead):
```python
user = User.query.filter_by(id=user_id).first()
# OR
query = text("SELECT * FROM users WHERE id = :user_id")
db.session.execute(query, {"user_id": user_id})
```
