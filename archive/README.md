# Archived Files

This directory contains deprecated files that have been consolidated into unified implementations.

## Consolidation Map

### AI Services (Consolidated into `utils/unified_ai_service.py`)
- `cost_optimized_ai.py` - Cost optimization moved to unified service
- `ai_fallback_service.py` - Fallback logic integrated
- `ai_service_manager.py` - Management moved to unified service
- `consolidated_ai_services.py` - Merged into main unified service
- `enhanced_unified_ai_service.py` - Enhancements merged
- `unified_ai_services.py` - Duplicate of unified_ai_service.py

### Google OAuth (Kept `utils/google_oauth.py`)
- `google_oauth_fixed.py` - Fixes merged into main file
- `consolidated_google_services.py` - Duplicate functionality

### Rate Limiting (Kept `utils/rate_limiter.py`, added `utils/rate_limit_config.py`)
- `rate_limiting.py` - Duplicate implementation

### Error Handling (Kept `utils/error_handler.py`)
- `error_handlers.py` - Duplicate implementation

### Database Optimization (Kept `utils/database_optimizer.py`)
- `db_optimizations.py` - Duplicate
- `unified_database_optimization.py` - Duplicate
- `database_query_optimizer.py` - Query-specific, merged into main

### Two-Factor Auth (Kept `utils/two_factor.py`)
- `two_factor_auth.py` - Duplicate implementation

## Restoration

If you need to restore a file:
```bash
cp archive/utils/[filename] utils/[filename]
```
