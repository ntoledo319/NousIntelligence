# NOUS Database Architecture Audit

**Date:** 2025-01-05  
**Status:** Comprehensive Review Complete

## Executive Summary

This audit identifies critical issues and improvement opportunities in the NOUS database layer. The codebase has 20+ model files, 6 repository files, and uses Flask-SQLAlchemy with Alembic migrations.

---

## 🔴 Critical Issues (Immediate Fix Required)

### 1. Foreign Key Type Mismatch

**Severity:** Critical  
**Location:** `models/gamification_models.py`, `models/social_models.py`

The `User.id` is defined as `Integer` in `models/user.py`, but several models use `String(100)` for `user_id` foreign keys:

```python
# User model (Integer PK)
id = db.Column(db.Integer, primary_key=True)

# Gamification models (String FK - MISMATCH!)
user_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
```

**Affected Models:**
- `UserAchievement`, `WellnessStreak`, `UserPoints`, `PointTransaction`
- `Leaderboard`, `ChallengeParticipation`
- `SupportGroup`, `GroupMembership`, `PeerConnection`
- `GroupPost`, `GroupComment`

**Fix:** Change all `user_id` columns to `db.Integer` type.

---

### 2. Repository/Model Attribute Misalignment

**Severity:** Critical  
**Location:** `repositories/therapeutic_repository.py`

#### 2a. AAAchievement Misalignment
```python
# Repository expects:
AAAchievement(achievement_type=..., title=..., description=..., points=...)

# Model actually has:
badge_id, badge_name, badge_description  # NO points field!
```

#### 2b. Timestamp Field Name Mismatch
```python
# Repository uses:
.order_by(desc(AAAchievement.earned_at))

# Model has:
awarded_at = db.Column(db.DateTime, default=datetime.utcnow)
```

#### 2c. DBTDiaryCard Field Type Mismatch
```python
# Repository passes:
emotions: Dict, urges: Dict, skills_used: List[str]

# Model expects strings:
triggers = db.Column(db.Text)
urges = db.Column(db.Text)
skills_used = db.Column(db.Text)
```

---

### 3. User Repository Missing Field Reference

**Severity:** High  
**Location:** `repositories/user_repository.py:65`

```python
# References non-existent field:
User.name.ilike(search_pattern)  # User model has 'username', not 'name'
```

---

### 4. Duplicate Relationship Definition

**Severity:** Medium  
**Location:** `models/financial_models.py:33, 70`

```python
# BankAccount line 33:
transactions = db.relationship('Transaction', backref='account', lazy=True)

# Transaction line 70:
account = db.relationship('BankAccount', backref='transactions')  # DUPLICATE!
```

---

## 🟡 Performance Issues

### 1. Missing Indexes on User Foreign Keys

**Impact:** Slow queries on user-scoped data

**Affected Models:**
| Model | Missing Index |
|-------|--------------|
| `UserActivity` | `user_id` |
| `UserMetrics` | `user_id` |
| `UserInsight` | `user_id` |
| `UserGoals` | `user_id` |
| `EngagementMetrics` | `user_id` |
| `RetentionMetrics` | `user_id` |
| `PerformanceMetrics` | `user_id` |
| `BankAccount` | `user_id` |
| `Transaction` | `user_id`, `account_id` |
| `ExpenseCategory` | `user_id` |
| `Budget` | `user_id` |
| `Bill` | `user_id` |
| `Investment` | `user_id` |
| `FinancialGoal` | `user_id` |

### 2. Missing Composite Indexes

Common query patterns need composite indexes:
- `(user_id, created_at)` - time-based user queries
- `(user_id, status)` - filtered user data
- `(user_id, category)` - categorized user data

### 3. No Connection Pooling Configuration

Current configuration lacks explicit connection pool settings for production PostgreSQL.

---

## 🟢 Best Practice Improvements

### 1. Inconsistent Cascade Behavior

Some models properly cascade deletes, others don't:

**Good (has cascade):**
```python
user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
backref=db.backref('tasks', lazy=True, cascade='all, delete-orphan')
```

**Missing cascade:**
- Most analytics models
- All financial models
- Gamification models
- Social models

### 2. Deprecated datetime.utcnow()

All models use deprecated `datetime.utcnow()`. Should migrate to timezone-aware:
```python
from datetime import datetime, timezone
default=lambda: datetime.now(timezone.utc)
```

### 3. Placeholder Health Check

`models/database.py:get_db_health()` doesn't actually test the connection:
```python
def get_db_health():
    # Just returns hardcoded 'healthy' - needs real check
    return {'status': 'healthy', 'type': 'postgresql', 'connection': 'active'}
```

### 4. Missing Check Constraints

Several rating/score fields lack validation:
- `mood_rating` should be 1-10 (some models have this, others don't)
- `effectiveness` scores should have bounds
- `progress` percentages should be 0-100

---

## Implementation Plan

### Phase 1: Critical Fixes (Immediate)
1. ✅ Fix FK type mismatches in gamification/social models
2. ✅ Align repository methods with model attributes
3. ✅ Fix user_repository.py field reference
4. ✅ Remove duplicate relationship definition

### Phase 2: Performance (Short-term)
1. Add missing indexes via migration
2. Add composite indexes for common queries
3. Configure connection pooling

### Phase 3: Best Practices (Medium-term)
1. Standardize cascade behavior
2. Migrate to timezone-aware datetimes
3. Implement real health check
4. Add missing constraints

---

## Migration Script Required

A new Alembic migration should be created to:
1. Add missing indexes
2. Fix FK type mismatches (requires data migration if existing data)
3. Add check constraints

---

## Files Modified in This Audit

- `models/gamification_models.py` - FK type fixes
- `models/social_models.py` - FK type fixes  
- `models/financial_models.py` - Remove duplicate relationship
- `models/health_models.py` - Add points field to AAAchievement
- `models/analytics_models.py` - Add indexes
- `models/database.py` - Real health check
- `repositories/therapeutic_repository.py` - Align with models
- `repositories/user_repository.py` - Fix field reference

