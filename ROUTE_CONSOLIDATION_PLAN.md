# Backend Route Consolidation Plan - Phase 1.2

## Current State
73 route files with massive duplication across:
- `api_routes.py`, `api_v2.py`, `enhanced_api_routes.py`, `consolidated_api_routes.py`, `missing_api_routes.py`
- `chat_routes.py`, `chat_router.py`, `chat_meet_commands.py`
- Multiple health check implementations

## Consolidation Strategy

### Core API (Keep & Migrate to `consolidated_routes.py`)
- ✅ `/api/v1/health` - Single health endpoint
- ✅ `/api/v1/user` - User info
- ✅ `/api/v1/chat` - Connected to EmotionAwareTherapeuticAssistant
- ✅ `/api/v1/conversations` - List conversations
- ✅ `/api/v1/conversations/<id>/messages` - Get messages

### Therapeutic Routes (Keep `therapeutic_routes.py`)
- `/api/v1/therapeutic/dbt/*` - DBT skills
- `/api/v1/therapeutic/cbt/*` - CBT thought records
- `/api/v1/therapeutic/mood` - Mood tracking
- `/api/v1/therapeutic/crisis/*` - Crisis resources

### Auth Routes (Keep `routes/auth/*`)
- `/auth/google` - OAuth
- `/auth/logout` - Sign out
- `/auth/callback` - OAuth callback

### Feature Routes (Consolidate or Remove)
- **Spotify** → Keep `routes/spotify_routes.py` (functional integration)
- **Gamification** → Keep `routes/gamification_routes.py` (complete backend)
- **Analytics** → Keep `routes/analytics_routes.py` (event logging)
- **AA Content** → Keep `routes/aa_routes.py` (recovery features)

### Files to DEPRECATE
- ❌ `api_v2.py` (10,021 lines) - Migrate essentials to consolidated
- ❌ `enhanced_api_routes.py` (21,062 lines) - Mostly redundant
- ❌ `missing_api_routes.py` (3,777 lines) - Stub implementations
- ❌ `chat_router.py` (4,316 lines) - Duplicate of chat_routes
- ❌ `chat_meet_commands.py` (19,280 lines) - Over-engineered
- ❌ `health_api.py` & `health_check.py` - Consolidated to single endpoint

## Target Architecture
```
routes/
├── consolidated_routes.py    # Core API (chat, user, conversations)
├── therapeutic_routes.py     # CBT/DBT/Crisis features
├── auth/
│   └── google_auth.py        # OAuth only
├── spotify_routes.py         # Music integration
├── gamification_routes.py    # Achievements
├── analytics_routes.py       # Event tracking
└── aa_routes.py              # Recovery content
```

**Goal: 73 files → ~8 focused route modules**

## Migration Steps
1. ✅ Create `consolidated_routes.py` with core endpoints
2. Update `routes/__init__.py` to register consolidated blueprint
3. Mark deprecated files with warnings
4. Run tests to verify no regressions
5. Remove deprecated files after validation

## Next Actions
- Update blueprint registration in `routes/__init__.py`
- Add deprecation warnings to old route files
- Update frontend to use `/api/v1/*` endpoints consistently
