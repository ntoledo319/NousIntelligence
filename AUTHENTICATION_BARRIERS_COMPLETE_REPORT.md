
# COMPREHENSIVE AUTHENTICATION BARRIER REPORT
Generated: Sun Jun 29 07:18:25 AM UTC 2025

## EXECUTIVE SUMMARY
- Files Scanned: 436
- Total Barriers Found: 907
- Critical Barriers: 158
- High Priority Barriers: 315
- Medium Priority Barriers: 31
- Low Priority Barriers: 403
- Files Affected: 148

## CRITICAL BARRIERS (Immediate Fix Required)

### operation_public_or_bust_audit.py
- Line 123: `r'@login_required',`
- Pattern: @login_required

### operation_public_or_bust_audit.py
- Line 123: `r'@login_required',`
- Pattern: @login_required

### restore_full_functionality.py
- Line 334: `elif stripped.startswith('@login_required'):`
- Pattern: @login_required

### restore_full_functionality.py
- Line 334: `elif stripped.startswith('@login_required'):`
- Pattern: @login_required

### restore_full_functionality.py
- Line 335: `fixed_lines.append(line.replace('@login_required', '@login_required'))`
- Pattern: @login_required

### restore_full_functionality.py
- Line 335: `fixed_lines.append(line.replace('@login_required', '@login_required'))`
- Pattern: @login_required

### complete_functionality_restore.py
- Line 58: `@login_required`
- Pattern: @login_required

### complete_functionality_restore.py
- Line 58: `@login_required`
- Pattern: @login_required

### complete_functionality_restore.py
- Line 87: `@login_required`
- Pattern: @login_required

### complete_functionality_restore.py
- Line 87: `@login_required`
- Pattern: @login_required

### complete_functionality_restore.py
- Line 220: `@login_required`
- Pattern: @login_required

### complete_functionality_restore.py
- Line 220: `@login_required`
- Pattern: @login_required

### complete_functionality_restore.py
- Line 227: `@login_required`
- Pattern: @login_required

### complete_functionality_restore.py
- Line 227: `@login_required`
- Pattern: @login_required

### complete_functionality_restore.py
- Line 269: `@login_required`
- Pattern: @login_required

### complete_functionality_restore.py
- Line 269: `@login_required`
- Pattern: @login_required

### complete_functionality_restore.py
- Line 370: `@login_required`
- Pattern: @login_required

### complete_functionality_restore.py
- Line 370: `@login_required`
- Pattern: @login_required

### comprehensive_auth_barrier_scanner.py
- Line 18: `r'@login_required',`
- Pattern: @login_required

### comprehensive_auth_barrier_scanner.py
- Line 18: `r'@login_required',`
- Pattern: @login_required

### comprehensive_auth_barrier_scanner.py
- Line 36: `r'@login_required',`
- Pattern: @login_required

### comprehensive_auth_barrier_scanner.py
- Line 36: `r'@login_required',`
- Pattern: @login_required

### comprehensive_auth_barrier_scanner.py
- Line 89: `if any(p in pattern for p in ['@login_required', 'abort(401)', 'abort(403)']):`
- Pattern: @login_required

### comprehensive_auth_barrier_scanner.py
- Line 89: `if any(p in pattern for p in ['@login_required', 'abort(401)', 'abort(403)']):`
- Pattern: @login_required

### comprehensive_auth_barrier_scanner.py
- Line 210: `'Replace @login_required with session-based auth checks',`
- Pattern: @login_required

### comprehensive_auth_barrier_scanner.py
- Line 210: `'Replace @login_required with session-based auth checks',`
- Pattern: @login_required

### comprehensive_auth_barrier_scanner.py
- Line 219: `'Mass replace @login_required decorators',`
- Pattern: @login_required

### comprehensive_auth_barrier_scanner.py
- Line 219: `'Mass replace @login_required decorators',`
- Pattern: @login_required

### fix_all_authentication_barriers.py
- Line 48: `# Fix 1: Replace @login_required decorators`
- Pattern: @login_required

### fix_all_authentication_barriers.py
- Line 48: `# Fix 1: Replace @login_required decorators`
- Pattern: @login_required

### fix_all_authentication_barriers.py
- Line 50: `r'@login_required',`
- Pattern: @login_required

### fix_all_authentication_barriers.py
- Line 50: `r'@login_required',`
- Pattern: @login_required

### fix_all_authentication_barriers.py
- Line 51: `r'@login_required',`
- Pattern: @login_required

### fix_all_authentication_barriers.py
- Line 51: `r'@login_required',`
- Pattern: @login_required

### fix_all_authentication_barriers.py
- Line 52: `r'@login_required',`
- Pattern: @login_required

### fix_all_authentication_barriers.py
- Line 52: `r'@login_required',`
- Pattern: @login_required

### fix_all_authentication_barriers.py
- Line 53: `r'@login_required'`
- Pattern: @login_required

### fix_all_authentication_barriers.py
- Line 53: `r'@login_required'`
- Pattern: @login_required

### fix_all_authentication_barriers.py
- Line 73: `content = re.sub(pattern, '@login_required', content)`
- Pattern: @login_required

### fix_all_authentication_barriers.py
- Line 73: `content = re.sub(pattern, '@login_required', content)`
- Pattern: @login_required

### comprehensive_authentication_fixes.py
- Line 66: `# 2. Replace @login_required patterns`
- Pattern: @login_required

### comprehensive_authentication_fixes.py
- Line 66: `# 2. Replace @login_required patterns`
- Pattern: @login_required

### comprehensive_authentication_fixes.py
- Line 68: `r'@login_required\s*\n',`
- Pattern: @login_required

### comprehensive_authentication_fixes.py
- Line 68: `r'@login_required\s*\n',`
- Pattern: @login_required

### comprehensive_authentication_fixes.py
- Line 86: `content = re.sub(pattern, '@login_required\n', content)`
- Pattern: @login_required

### comprehensive_authentication_fixes.py
- Line 86: `content = re.sub(pattern, '@login_required\n', content)`
- Pattern: @login_required

### routes/user_routes.py
- Line 11: `@login_required`
- Pattern: @login_required

### routes/user_routes.py
- Line 11: `@login_required`
- Pattern: @login_required

### routes/dashboard.py
- Line 11: `@login_required`
- Pattern: @login_required

### routes/dashboard.py
- Line 11: `@login_required`
- Pattern: @login_required

### routes/tasks_routes.py
- Line 11: `@login_required`
- Pattern: @login_required

### routes/tasks_routes.py
- Line 11: `@login_required`
- Pattern: @login_required

### routes/analytics_routes.py
- Line 11: `@login_required`
- Pattern: @login_required

### routes/analytics_routes.py
- Line 11: `@login_required`
- Pattern: @login_required

### routes/financial_routes.py
- Line 11: `@login_required`
- Pattern: @login_required

### routes/financial_routes.py
- Line 11: `@login_required`
- Pattern: @login_required

### routes/financial_routes.py
- Line 18: `@login_required`
- Pattern: @login_required

### routes/financial_routes.py
- Line 18: `@login_required`
- Pattern: @login_required

### routes/setup_routes.py
- Line 11: `@login_required`
- Pattern: @login_required

### routes/setup_routes.py
- Line 11: `@login_required`
- Pattern: @login_required

### routes/setup_routes.py
- Line 18: `@login_required`
- Pattern: @login_required

### routes/setup_routes.py
- Line 18: `@login_required`
- Pattern: @login_required

### routes/setup_routes.py
- Line 32: `@login_required`
- Pattern: @login_required

### routes/setup_routes.py
- Line 32: `@login_required`
- Pattern: @login_required

### archive/scripts_archive/code_surgeon_v4.py
- Line 140: `# Simple decorators like @login_required`
- Pattern: @login_required

### archive/scripts_archive/code_surgeon_v4.py
- Line 140: `# Simple decorators like @login_required`
- Pattern: @login_required

### archive/original_routes/api_key_routes.py
- Line 39: `@login_required`
- Pattern: @login_required

### archive/original_routes/api_key_routes.py
- Line 39: `@login_required`
- Pattern: @login_required

### archive/original_routes/api_key_routes.py
- Line 72: `@login_required`
- Pattern: @login_required

### archive/original_routes/api_key_routes.py
- Line 72: `@login_required`
- Pattern: @login_required

### archive/original_routes/api_key_routes.py
- Line 113: `@login_required`
- Pattern: @login_required

### archive/original_routes/api_key_routes.py
- Line 113: `@login_required`
- Pattern: @login_required

### archive/original_routes/api_key_routes.py
- Line 181: `@login_required`
- Pattern: @login_required

### archive/original_routes/api_key_routes.py
- Line 181: `@login_required`
- Pattern: @login_required

### archive/original_routes/api_key_routes.py
- Line 246: `@login_required`
- Pattern: @login_required

### archive/original_routes/api_key_routes.py
- Line 246: `@login_required`
- Pattern: @login_required

### archive/original_routes/api_key_routes.py
- Line 299: `@login_required`
- Pattern: @login_required

### archive/original_routes/api_key_routes.py
- Line 299: `@login_required`
- Pattern: @login_required

### archive/original_routes/voice_emotion_routes.py
- Line 32: `@login_required`
- Pattern: @login_required

### archive/original_routes/voice_emotion_routes.py
- Line 32: `@login_required`
- Pattern: @login_required

### archive/original_routes/voice_emotion_routes.py
- Line 47: `@login_required`
- Pattern: @login_required

### archive/original_routes/voice_emotion_routes.py
- Line 47: `@login_required`
- Pattern: @login_required

### archive/original_routes/voice_mindfulness_routes.py
- Line 41: `@login_required`
- Pattern: @login_required

### archive/original_routes/voice_mindfulness_routes.py
- Line 41: `@login_required`
- Pattern: @login_required

### archive/original_routes/voice_mindfulness_routes.py
- Line 60: `@login_required`
- Pattern: @login_required

### archive/original_routes/voice_mindfulness_routes.py
- Line 60: `@login_required`
- Pattern: @login_required

### archive/original_routes/voice_mindfulness_routes.py
- Line 92: `@login_required`
- Pattern: @login_required

### archive/original_routes/voice_mindfulness_routes.py
- Line 92: `@login_required`
- Pattern: @login_required

### archive/original_routes/voice_mindfulness_routes.py
- Line 123: `@login_required`
- Pattern: @login_required

### archive/original_routes/voice_mindfulness_routes.py
- Line 123: `@login_required`
- Pattern: @login_required

### archive/original_routes/voice_mindfulness_routes.py
- Line 164: `@login_required`
- Pattern: @login_required

### archive/original_routes/voice_mindfulness_routes.py
- Line 164: `@login_required`
- Pattern: @login_required

### archive/original_routes/spotify_routes.py
- Line 23: `@login_required`
- Pattern: @login_required

### archive/original_routes/spotify_routes.py
- Line 23: `@login_required`
- Pattern: @login_required

### archive/original_routes/spotify_commands.py
- Line 27: `@login_required`
- Pattern: @login_required

### archive/original_routes/spotify_commands.py
- Line 27: `@login_required`
- Pattern: @login_required

### archive/original_routes/spotify_commands.py
- Line 510: `@login_required`
- Pattern: @login_required

### archive/original_routes/spotify_commands.py
- Line 510: `@login_required`
- Pattern: @login_required

### archive/original_routes/spotify_commands.py
- Line 555: `@login_required`
- Pattern: @login_required

### archive/original_routes/spotify_commands.py
- Line 555: `@login_required`
- Pattern: @login_required

### archive/original_routes/spotify_visualization.py
- Line 25: `@login_required`
- Pattern: @login_required

### archive/original_routes/spotify_visualization.py
- Line 25: `@login_required`
- Pattern: @login_required

### archive/original_routes/spotify_visualization.py
- Line 31: `@login_required`
- Pattern: @login_required

### archive/original_routes/spotify_visualization.py
- Line 31: `@login_required`
- Pattern: @login_required

### archive/original_routes/spotify_visualization.py
- Line 57: `@login_required`
- Pattern: @login_required

### archive/original_routes/spotify_visualization.py
- Line 57: `@login_required`
- Pattern: @login_required

### archive/original_routes/spotify_visualization.py
- Line 86: `@login_required`
- Pattern: @login_required

### archive/original_routes/spotify_visualization.py
- Line 86: `@login_required`
- Pattern: @login_required

### archive/original_routes/spotify_visualization.py
- Line 115: `@login_required`
- Pattern: @login_required

### archive/original_routes/spotify_visualization.py
- Line 115: `@login_required`
- Pattern: @login_required

### archive/original_routes/spotify_visualization.py
- Line 143: `@login_required`
- Pattern: @login_required

### archive/original_routes/spotify_visualization.py
- Line 143: `@login_required`
- Pattern: @login_required

### archive/original_routes/spotify_visualization.py
- Line 171: `@login_required`
- Pattern: @login_required

### archive/original_routes/spotify_visualization.py
- Line 171: `@login_required`
- Pattern: @login_required

### archive/original_routes/spotify_visualization.py
- Line 203: `@login_required`
- Pattern: @login_required

### archive/original_routes/spotify_visualization.py
- Line 203: `@login_required`
- Pattern: @login_required

### archive/original_routes/spotify_visualization.py
- Line 237: `@login_required`
- Pattern: @login_required

### archive/original_routes/spotify_visualization.py
- Line 237: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/complete_functionality_restore.py
- Line 58: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/complete_functionality_restore.py
- Line 58: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/complete_functionality_restore.py
- Line 87: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/complete_functionality_restore.py
- Line 87: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/complete_functionality_restore.py
- Line 220: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/complete_functionality_restore.py
- Line 220: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/complete_functionality_restore.py
- Line 227: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/complete_functionality_restore.py
- Line 227: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/complete_functionality_restore.py
- Line 269: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/complete_functionality_restore.py
- Line 269: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/complete_functionality_restore.py
- Line 370: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/complete_functionality_restore.py
- Line 370: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/restore_full_functionality.py
- Line 334: `elif stripped.startswith('@login_required'):`
- Pattern: @login_required

### backup_auth_fixes/restore_full_functionality.py
- Line 334: `elif stripped.startswith('@login_required'):`
- Pattern: @login_required

### backup_auth_fixes/restore_full_functionality.py
- Line 335: `fixed_lines.append(line.replace('@login_required', '@login_required'))`
- Pattern: @login_required

### backup_auth_fixes/restore_full_functionality.py
- Line 335: `fixed_lines.append(line.replace('@login_required', '@login_required'))`
- Pattern: @login_required

### backup_auth_fixes/fix_all_authentication_barriers.py
- Line 48: `# Fix 1: Replace @login_required decorators`
- Pattern: @login_required

### backup_auth_fixes/fix_all_authentication_barriers.py
- Line 48: `# Fix 1: Replace @login_required decorators`
- Pattern: @login_required

### backup_auth_fixes/fix_all_authentication_barriers.py
- Line 50: `r'@login_required',`
- Pattern: @login_required

### backup_auth_fixes/fix_all_authentication_barriers.py
- Line 50: `r'@login_required',`
- Pattern: @login_required

### backup_auth_fixes/fix_all_authentication_barriers.py
- Line 73: `content = re.sub(pattern, '@login_required', content)`
- Pattern: @login_required

### backup_auth_fixes/fix_all_authentication_barriers.py
- Line 73: `content = re.sub(pattern, '@login_required', content)`
- Pattern: @login_required

### backup_auth_fixes/routes/tasks_routes.py
- Line 11: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/routes/tasks_routes.py
- Line 11: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/routes/financial_routes.py
- Line 11: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/routes/financial_routes.py
- Line 11: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/routes/financial_routes.py
- Line 18: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/routes/financial_routes.py
- Line 18: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/routes/setup_routes.py
- Line 11: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/routes/setup_routes.py
- Line 11: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/routes/setup_routes.py
- Line 18: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/routes/setup_routes.py
- Line 18: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/routes/setup_routes.py
- Line 32: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/routes/setup_routes.py
- Line 32: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/routes/dashboard.py
- Line 11: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/routes/dashboard.py
- Line 11: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/routes/user_routes.py
- Line 11: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/routes/user_routes.py
- Line 11: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/routes/analytics_routes.py
- Line 11: `@login_required`
- Pattern: @login_required

### backup_auth_fixes/routes/analytics_routes.py
- Line 11: `@login_required`
- Pattern: @login_required

## HIGH PRIORITY BARRIERS

### operation_public_or_bust_audit.py
- Line 130: `r'redirect.*login',`
- Pattern: redirect.*login

### operation_public_or_bust_audit.py
- Line 226: `'if not', 'return.*401', 'redirect.*login'`
- Pattern: redirect.*login

### operation_public_or_bust_audit.py
- Line 346: `if 'return.*401' in barrier['content'] or 'redirect.*login' in barrier['content']]`
- Pattern: redirect.*login

### public_access_verification.py
- Line 141: `# If we get redirected to login, that's OK, but should not loop`
- Pattern: redirect.*login

### fix_syntax_errors.py
- Line 82: `# For web routes, redirect to login`
- Pattern: redirect.*login

### restore_full_functionality.py
- Line 107: `# For web routes, redirect to login`
- Pattern: redirect.*login

### restore_full_functionality.py
- Line 137: `# For web routes, redirect to login`
- Pattern: redirect.*login

### comprehensive_auth_barrier_scanner.py
- Line 28: `r'return redirect.*login',`
- Pattern: return redirect.*login

### comprehensive_auth_barrier_scanner.py
- Line 28: `r'return redirect.*login',`
- Pattern: redirect.*login

### comprehensive_auth_barrier_scanner.py
- Line 51: `r'redirect.*login',`
- Pattern: redirect.*login

### comprehensive_auth_barrier_scanner.py
- Line 93: `if any(p in pattern for p in ['redirect.*login', 'You must be logged in']):`
- Pattern: ["\']You must be logged in

### comprehensive_auth_barrier_scanner.py
- Line 93: `if any(p in pattern for p in ['redirect.*login', 'You must be logged in']):`
- Pattern: redirect.*login

### comprehensive_auth_barrier_scanner.py
- Line 276: `print(f"   - These will cause 'You must be logged in' errors")`
- Pattern: ["\']You must be logged in

### fix_all_authentication_barriers.py
- Line 94: `(r'return redirect\([\'"].*login.*[\'"]\)', 'return redirect("/demo")'),`
- Pattern: return redirect.*login

### fix_all_authentication_barriers.py
- Line 94: `(r'return redirect\([\'"].*login.*[\'"]\)', 'return redirect("/demo")'),`
- Pattern: redirect.*login

### fix_all_authentication_barriers.py
- Line 95: `(r'redirect\([\'"].*login.*[\'"]\)', 'redirect("/demo")'),`
- Pattern: redirect.*login

### comprehensive_authentication_fixes.py
- Line 109: `(r'redirect\([\'"][^\'"]*/login[^\'\"]*[\'\"]\)', 'redirect("/demo")'),`
- Pattern: redirect.*login

### comprehensive_authentication_fixes.py
- Line 138: `(r'"You must be logged in[^"]*"', '"Demo mode - limited access"'),`
- Pattern: ["\']You must be logged in

### comprehensive_authentication_fixes.py
- Line 139: `(r"'You must be logged in[^']*'", "'Demo mode - limited access'"),`
- Pattern: ["\']You must be logged in

### comprehensive_authentication_fixes.py
- Line 341: `print(f"✅ Zero 'You must be logged in' errors")`
- Pattern: ["\']You must be logged in

### routes/settings.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/index.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/pulse.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/beta_admin.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/api.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/admin_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/amazon_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/async_api.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/beta_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/chat_meet_commands.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/chat_router.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/crisis_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/forms_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/health_check.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/image_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/image_routes.py
- Line 155: `return redirect(url_for("main.demo"))  # Or wherever your login route is`
- Pattern: return redirect.*login

### routes/image_routes.py
- Line 155: `return redirect(url_for("main.demo"))  # Or wherever your login route is`
- Pattern: redirect.*login

### routes/language_learning_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/meet_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/memory_dashboard_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/memory_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/price_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/smart_shopping_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/two_factor_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/consolidated_voice_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/consolidated_spotify_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/enhanced_api_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/adaptive_ai_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/api_key_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/messaging_status.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/consolidated_api_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/auth_api.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/collaboration_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/onboarding_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/nous_tech_status_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/nous_tech_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/aa_content.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/api/shopping.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/api/health.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/api/v1/settings.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/api/v1/weather.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/view/settings.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/view/user.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/view/index.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/view/dashboard.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/view/auth.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/view/auth.py
- Line 111: `Redirect to dashboard on success or login page on failure`
- Pattern: redirect.*login

### routes/view/auth.py
- Line 165: `Redirects to the Google OAuth login route`
- Pattern: redirect.*login

### routes/view/auth.py
- Line 170: `# Redirect to Google auth login`
- Pattern: redirect.*login

### routes/auth/standardized_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### routes/auth/standardized_routes.py
- Line 108: `This endpoint clears the user session and redirects to the login page.`
- Pattern: redirect.*login

### routes/auth/standardized_routes.py
- Line 113: `# Redirect to login page`
- Pattern: redirect.*login

### archive/scripts_archive/backend_stability_test.py
- Line 106: `# Should redirect to login for non-authenticated users`
- Pattern: redirect.*login

### archive/consolidated_security_services_backup/security_helper.py
- Line 58: `return redirect(url_for('auth.login', next=request.url))`
- Pattern: return redirect.*login

### archive/consolidated_security_services_backup/security_helper.py
- Line 58: `return redirect(url_for('auth.login', next=request.url))`
- Pattern: redirect.*login

### archive/consolidated_security_services_backup/security_middleware.py
- Line 296: `# Redirect to admin login`
- Pattern: redirect.*login

### backup_corrupted_routes/simple_auth_api.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_corrupted_routes/simple_auth_api.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_corrupted_routes/simple_auth_api.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_corrupted_routes/dashboard.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_corrupted_routes/dashboard.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_corrupted_routes/dashboard.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_corrupted_routes/user_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_corrupted_routes/user_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_corrupted_routes/user_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_corrupted_routes/chat_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_corrupted_routes/chat_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_corrupted_routes/chat_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_corrupted_routes/dbt_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_corrupted_routes/dbt_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_corrupted_routes/dbt_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_corrupted_routes/cbt_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_corrupted_routes/cbt_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_corrupted_routes/cbt_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_corrupted_routes/aa_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_corrupted_routes/aa_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_corrupted_routes/aa_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_corrupted_routes/financial_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_corrupted_routes/financial_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_corrupted_routes/financial_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_corrupted_routes/search_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_corrupted_routes/search_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_corrupted_routes/search_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_corrupted_routes/analytics_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_corrupted_routes/analytics_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_corrupted_routes/analytics_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_corrupted_routes/analytics_routes.py
- Line 203: `return redirect('/login')`
- Pattern: return redirect.*login

### backup_corrupted_routes/analytics_routes.py
- Line 203: `return redirect('/login')`
- Pattern: redirect.*login

### backup_corrupted_routes/notification_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_corrupted_routes/notification_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_corrupted_routes/notification_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_corrupted_routes/maps_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_corrupted_routes/maps_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_corrupted_routes/maps_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_corrupted_routes/weather_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_corrupted_routes/weather_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_corrupted_routes/weather_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_corrupted_routes/tasks_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_corrupted_routes/tasks_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_corrupted_routes/tasks_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_corrupted_routes/tasks_routes.py
- Line 90: `return redirect(url_for('auth.authorize')) # Or your Google login route`
- Pattern: return redirect.*login

### backup_corrupted_routes/tasks_routes.py
- Line 90: `return redirect(url_for('auth.authorize')) # Or your Google login route`
- Pattern: redirect.*login

### backup_auth_fixes/fix_syntax_errors.py
- Line 82: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/fix_syntax_errors.py
- Line 83: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/fix_syntax_errors.py
- Line 83: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/restore_full_functionality.py
- Line 107: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/restore_full_functionality.py
- Line 108: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/restore_full_functionality.py
- Line 108: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/restore_full_functionality.py
- Line 137: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/restore_full_functionality.py
- Line 138: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/restore_full_functionality.py
- Line 138: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/public_access_verification.py
- Line 141: `# If we get redirected to login, that's OK, but should not loop`
- Pattern: redirect.*login

### backup_auth_fixes/app.py
- Line 384: `return redirect(url_for('demo_login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/app.py
- Line 384: `return redirect(url_for('demo_login'))`
- Pattern: redirect.*login

### backup_auth_fixes/app.py
- Line 459: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/app.py
- Line 459: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/fix_all_authentication_barriers.py
- Line 94: `(r'return redirect\([\'"].*login.*[\'"]\)', 'return redirect("/demo")'),`
- Pattern: return redirect.*login

### backup_auth_fixes/fix_all_authentication_barriers.py
- Line 94: `(r'return redirect\([\'"].*login.*[\'"]\)', 'return redirect("/demo")'),`
- Pattern: redirect.*login

### backup_auth_fixes/fix_all_authentication_barriers.py
- Line 95: `(r'redirect\([\'"].*login.*[\'"]\)', 'redirect("/demo")'),`
- Pattern: redirect.*login

### backup_auth_fixes/enhanced_app.py
- Line 480: `return redirect('/login')`
- Pattern: return redirect.*login

### backup_auth_fixes/enhanced_app.py
- Line 480: `return redirect('/login')`
- Pattern: redirect.*login

### backup_auth_fixes/routes/index.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/index.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/index.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/settings.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/settings.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/settings.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/two_factor_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/two_factor_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/two_factor_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/two_factor_routes.py
- Line 171: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/two_factor_routes.py
- Line 171: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/two_factor_routes.py
- Line 400: `"message": "You must be logged in to verify 2FA"`
- Pattern: ["\']You must be logged in

### backup_auth_fixes/routes/memory_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/memory_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/memory_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/nous_tech_status_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/nous_tech_status_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/nous_tech_status_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/async_api.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/async_api.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/async_api.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/memory_dashboard_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/memory_dashboard_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/memory_dashboard_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/nous_tech_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/nous_tech_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/nous_tech_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/auth_api.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/auth_api.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/auth_api.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/collaboration_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/collaboration_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/collaboration_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/pulse.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/pulse.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/pulse.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/api.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/api.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/api.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/image_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/image_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/image_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/image_routes.py
- Line 154: `flash("You must be logged in to view your gallery.")`
- Pattern: ["\']You must be logged in

### backup_auth_fixes/routes/image_routes.py
- Line 155: `return redirect(url_for('auth.login'))  # Or wherever your login route is`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/image_routes.py
- Line 155: `return redirect(url_for('auth.login'))  # Or wherever your login route is`
- Pattern: redirect.*login

### backup_auth_fixes/routes/aa_content.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/aa_content.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/aa_content.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/beta_admin.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/beta_admin.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/beta_admin.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/beta_admin.py
- Line 64: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/beta_admin.py
- Line 64: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/forms_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/forms_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/forms_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/messaging_status.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/messaging_status.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/messaging_status.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/adaptive_ai_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/adaptive_ai_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/adaptive_ai_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/api_key_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/api_key_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/api_key_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/beta_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/beta_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/beta_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/language_learning_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/language_learning_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/language_learning_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/smart_shopping_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/smart_shopping_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/smart_shopping_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/admin_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/admin_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/admin_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/consolidated_voice_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/consolidated_voice_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/consolidated_voice_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/crisis_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/crisis_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/crisis_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/consolidated_spotify_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/consolidated_spotify_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/consolidated_spotify_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/amazon_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/amazon_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/amazon_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/price_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/price_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/price_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/chat_meet_commands.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/chat_meet_commands.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/chat_meet_commands.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/onboarding_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/onboarding_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/onboarding_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/onboarding_routes.py
- Line 203: `return redirect(url_for('auth.login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/onboarding_routes.py
- Line 203: `return redirect(url_for('auth.login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/onboarding_routes.py
- Line 227: `return redirect(url_for('auth.login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/onboarding_routes.py
- Line 227: `return redirect(url_for('auth.login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/onboarding_routes.py
- Line 496: `return redirect(url_for('auth.login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/onboarding_routes.py
- Line 496: `return redirect(url_for('auth.login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/enhanced_api_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/enhanced_api_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/enhanced_api_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/health_check.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/health_check.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/health_check.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/chat_router.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/chat_router.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/chat_router.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/consolidated_api_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/consolidated_api_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/consolidated_api_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/meet_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/meet_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/meet_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/view/dashboard.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/view/dashboard.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/view/dashboard.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/view/auth.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/view/auth.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/view/auth.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/view/auth.py
- Line 111: `Redirect to dashboard on success or login page on failure`
- Pattern: redirect.*login

### backup_auth_fixes/routes/view/auth.py
- Line 119: `return redirect(url_for('auth.login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/view/auth.py
- Line 119: `return redirect(url_for('auth.login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/view/auth.py
- Line 126: `return redirect(url_for('auth.login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/view/auth.py
- Line 126: `return redirect(url_for('auth.login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/view/auth.py
- Line 151: `return redirect(url_for('auth.login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/view/auth.py
- Line 151: `return redirect(url_for('auth.login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/view/auth.py
- Line 165: `Redirects to the Google OAuth login route`
- Pattern: redirect.*login

### backup_auth_fixes/routes/view/auth.py
- Line 170: `# Redirect to Google auth login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/view/auth.py
- Line 171: `return redirect(url_for("google_auth.login"))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/view/auth.py
- Line 171: `return redirect(url_for("google_auth.login"))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/view/settings.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/view/settings.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/view/settings.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/view/user.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/view/user.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/view/user.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/view/index.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/view/index.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/view/index.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/view/index.py
- Line 103: `return redirect(url_for("auth.login"))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/view/index.py
- Line 103: `return redirect(url_for("auth.login"))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/api/health.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/api/health.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/api/health.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/api/shopping.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/api/shopping.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/api/shopping.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/api/v1/settings.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/api/v1/settings.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/api/v1/settings.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/api/v1/weather.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/api/v1/weather.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/api/v1/weather.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/auth/standardized_routes.py
- Line 19: `# For web routes, redirect to login`
- Pattern: redirect.*login

### backup_auth_fixes/routes/auth/standardized_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/auth/standardized_routes.py
- Line 20: `return redirect(url_for('login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/auth/standardized_routes.py
- Line 108: `This endpoint clears the user session and redirects to the login page.`
- Pattern: redirect.*login

### backup_auth_fixes/routes/auth/standardized_routes.py
- Line 113: `# Redirect to login page`
- Pattern: redirect.*login

### backup_auth_fixes/routes/auth/standardized_routes.py
- Line 114: `return redirect(url_for('auth.login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/auth/standardized_routes.py
- Line 114: `return redirect(url_for('auth.login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/auth/standardized_routes.py
- Line 146: `return redirect(url_for('auth.login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/auth/standardized_routes.py
- Line 146: `return redirect(url_for('auth.login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/auth/standardized_routes.py
- Line 181: `return redirect(url_for('auth.login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/auth/standardized_routes.py
- Line 181: `return redirect(url_for('auth.login'))`
- Pattern: redirect.*login

### backup_auth_fixes/routes/auth/standardized_routes.py
- Line 228: `return redirect(url_for('auth.login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/routes/auth/standardized_routes.py
- Line 228: `return redirect(url_for('auth.login'))`
- Pattern: redirect.*login

### backup_auth_fixes/utils/unified_security_services.py
- Line 130: `return redirect(url_for('login'))`
- Pattern: return redirect.*login

### backup_auth_fixes/utils/unified_security_services.py
- Line 130: `return redirect(url_for('login'))`
- Pattern: redirect.*login

## FILES REQUIRING ATTENTION

### operation_public_or_bust_audit.py
- Total barriers: 7
- Critical/High: 5

### public_access_verification.py
- Total barriers: 1
- Critical/High: 1

### fix_syntax_errors.py
- Total barriers: 6
- Critical/High: 1

### restore_full_functionality.py
- Total barriers: 11
- Critical/High: 6

### complete_functionality_restore.py
- Total barriers: 12
- Critical/High: 12

### comprehensive_auth_barrier_scanner.py
- Total barriers: 30
- Critical/High: 16

### fix_all_authentication_barriers.py
- Total barriers: 18
- Critical/High: 15

### comprehensive_authentication_fixes.py
- Total barriers: 25
- Critical/High: 10

### routes/settings.py
- Total barriers: 2
- Critical/High: 1

### routes/user_routes.py
- Total barriers: 2
- Critical/High: 2

### routes/index.py
- Total barriers: 2
- Critical/High: 1

### routes/dashboard.py
- Total barriers: 2
- Critical/High: 2

### routes/pulse.py
- Total barriers: 2
- Critical/High: 1

### routes/beta_admin.py
- Total barriers: 2
- Critical/High: 1

### routes/api.py
- Total barriers: 5
- Critical/High: 1

### routes/admin_routes.py
- Total barriers: 4
- Critical/High: 1

### routes/amazon_routes.py
- Total barriers: 2
- Critical/High: 1

### routes/async_api.py
- Total barriers: 2
- Critical/High: 1

### routes/beta_routes.py
- Total barriers: 2
- Critical/High: 1

### routes/chat_meet_commands.py
- Total barriers: 2
- Critical/High: 1

### routes/chat_router.py
- Total barriers: 2
- Critical/High: 1

### routes/crisis_routes.py
- Total barriers: 2
- Critical/High: 1

### routes/forms_routes.py
- Total barriers: 3
- Critical/High: 1

### routes/health_check.py
- Total barriers: 2
- Critical/High: 1

### routes/image_routes.py
- Total barriers: 5
- Critical/High: 3

### routes/language_learning_routes.py
- Total barriers: 2
- Critical/High: 1

### routes/meet_routes.py
- Total barriers: 3
- Critical/High: 1

### routes/memory_dashboard_routes.py
- Total barriers: 2
- Critical/High: 1

### routes/memory_routes.py
- Total barriers: 2
- Critical/High: 1

### routes/price_routes.py
- Total barriers: 2
- Critical/High: 1

### routes/smart_shopping_routes.py
- Total barriers: 2
- Critical/High: 1

### routes/two_factor_routes.py
- Total barriers: 4
- Critical/High: 1

### routes/tasks_routes.py
- Total barriers: 2
- Critical/High: 2

### routes/analytics_routes.py
- Total barriers: 2
- Critical/High: 2

### routes/consolidated_voice_routes.py
- Total barriers: 2
- Critical/High: 1

### routes/consolidated_spotify_routes.py
- Total barriers: 2
- Critical/High: 1

### routes/enhanced_api_routes.py
- Total barriers: 2
- Critical/High: 1

### routes/adaptive_ai_routes.py
- Total barriers: 2
- Critical/High: 1

### routes/api_key_routes.py
- Total barriers: 2
- Critical/High: 1

### routes/messaging_status.py
- Total barriers: 2
- Critical/High: 1

### routes/consolidated_api_routes.py
- Total barriers: 2
- Critical/High: 1

### routes/auth_api.py
- Total barriers: 5
- Critical/High: 1

### routes/financial_routes.py
- Total barriers: 4
- Critical/High: 4

### routes/collaboration_routes.py
- Total barriers: 2
- Critical/High: 1

### routes/onboarding_routes.py
- Total barriers: 2
- Critical/High: 1

### routes/nous_tech_status_routes.py
- Total barriers: 2
- Critical/High: 1

### routes/nous_tech_routes.py
- Total barriers: 2
- Critical/High: 1

### routes/aa_content.py
- Total barriers: 2
- Critical/High: 1

### routes/setup_routes.py
- Total barriers: 6
- Critical/High: 6

### routes/api/shopping.py
- Total barriers: 2
- Critical/High: 1

### routes/api/health.py
- Total barriers: 2
- Critical/High: 1

### routes/api/v1/settings.py
- Total barriers: 2
- Critical/High: 1

### routes/api/v1/weather.py
- Total barriers: 2
- Critical/High: 1

### routes/view/settings.py
- Total barriers: 2
- Critical/High: 1

### routes/view/user.py
- Total barriers: 2
- Critical/High: 1

### routes/view/index.py
- Total barriers: 4
- Critical/High: 1

### routes/view/dashboard.py
- Total barriers: 2
- Critical/High: 1

### routes/view/auth.py
- Total barriers: 5
- Critical/High: 4

### routes/auth/standardized_routes.py
- Total barriers: 4
- Critical/High: 3

### archive/scripts_archive/backend_stability_test.py
- Total barriers: 1
- Critical/High: 1

### archive/scripts_archive/code_surgeon_v4.py
- Total barriers: 2
- Critical/High: 2

### archive/original_routes/api_key_routes.py
- Total barriers: 16
- Critical/High: 12

### archive/original_routes/voice_emotion_routes.py
- Total barriers: 4
- Critical/High: 4

### archive/original_routes/voice_mindfulness_routes.py
- Total barriers: 10
- Critical/High: 10

### archive/original_routes/spotify_routes.py
- Total barriers: 2
- Critical/High: 2

### archive/original_routes/spotify_commands.py
- Total barriers: 6
- Critical/High: 6

### archive/original_routes/spotify_visualization.py
- Total barriers: 18
- Critical/High: 18

### archive/consolidated_security_services_backup/security_helper.py
- Total barriers: 4
- Critical/High: 2

### archive/consolidated_security_services_backup/security_middleware.py
- Total barriers: 1
- Critical/High: 1

### backup_corrupted_routes/simple_auth_api.py
- Total barriers: 9
- Critical/High: 3

### backup_corrupted_routes/dashboard.py
- Total barriers: 6
- Critical/High: 3

### backup_corrupted_routes/user_routes.py
- Total barriers: 6
- Critical/High: 3

### backup_corrupted_routes/chat_routes.py
- Total barriers: 6
- Critical/High: 3

### backup_corrupted_routes/dbt_routes.py
- Total barriers: 6
- Critical/High: 3

### backup_corrupted_routes/cbt_routes.py
- Total barriers: 6
- Critical/High: 3

### backup_corrupted_routes/aa_routes.py
- Total barriers: 6
- Critical/High: 3

### backup_corrupted_routes/financial_routes.py
- Total barriers: 14
- Critical/High: 3

### backup_corrupted_routes/search_routes.py
- Total barriers: 12
- Critical/High: 3

### backup_corrupted_routes/analytics_routes.py
- Total barriers: 12
- Critical/High: 5

### backup_corrupted_routes/notification_routes.py
- Total barriers: 12
- Critical/High: 3

### backup_corrupted_routes/maps_routes.py
- Total barriers: 6
- Critical/High: 3

### backup_corrupted_routes/weather_routes.py
- Total barriers: 6
- Critical/High: 3

### backup_corrupted_routes/tasks_routes.py
- Total barriers: 9
- Critical/High: 5

### backup_auth_fixes/fix_syntax_errors.py
- Total barriers: 10
- Critical/High: 3

### backup_auth_fixes/complete_functionality_restore.py
- Total barriers: 12
- Critical/High: 12

### backup_auth_fixes/restore_full_functionality.py
- Total barriers: 19
- Critical/High: 10

### backup_auth_fixes/public_access_verification.py
- Total barriers: 1
- Critical/High: 1

### backup_auth_fixes/app.py
- Total barriers: 7
- Critical/High: 4

### backup_auth_fixes/fix_all_authentication_barriers.py
- Total barriers: 19
- Critical/High: 9

### backup_auth_fixes/enhanced_app.py
- Total barriers: 2
- Critical/High: 2

### backup_auth_fixes/routes/index.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/settings.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/two_factor_routes.py
- Total barriers: 13
- Critical/High: 6

### backup_auth_fixes/routes/memory_routes.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/nous_tech_status_routes.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/tasks_routes.py
- Total barriers: 2
- Critical/High: 2

### backup_auth_fixes/routes/async_api.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/memory_dashboard_routes.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/nous_tech_routes.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/auth_api.py
- Total barriers: 10
- Critical/High: 3

### backup_auth_fixes/routes/collaboration_routes.py
- Total barriers: 15
- Critical/High: 3

### backup_auth_fixes/routes/pulse.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/api.py
- Total barriers: 12
- Critical/High: 3

### backup_auth_fixes/routes/image_routes.py
- Total barriers: 10
- Critical/High: 6

### backup_auth_fixes/routes/aa_content.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/beta_admin.py
- Total barriers: 11
- Critical/High: 5

### backup_auth_fixes/routes/financial_routes.py
- Total barriers: 4
- Critical/High: 4

### backup_auth_fixes/routes/forms_routes.py
- Total barriers: 7
- Critical/High: 3

### backup_auth_fixes/routes/messaging_status.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/adaptive_ai_routes.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/api_key_routes.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/setup_routes.py
- Total barriers: 6
- Critical/High: 6

### backup_auth_fixes/routes/beta_routes.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/language_learning_routes.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/smart_shopping_routes.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/admin_routes.py
- Total barriers: 10
- Critical/High: 3

### backup_auth_fixes/routes/consolidated_voice_routes.py
- Total barriers: 12
- Critical/High: 3

### backup_auth_fixes/routes/crisis_routes.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/consolidated_spotify_routes.py
- Total barriers: 18
- Critical/High: 3

### backup_auth_fixes/routes/amazon_routes.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/dashboard.py
- Total barriers: 2
- Critical/High: 2

### backup_auth_fixes/routes/price_routes.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/chat_meet_commands.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/onboarding_routes.py
- Total barriers: 20
- Critical/High: 9

### backup_auth_fixes/routes/user_routes.py
- Total barriers: 2
- Critical/High: 2

### backup_auth_fixes/routes/enhanced_api_routes.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/analytics_routes.py
- Total barriers: 2
- Critical/High: 2

### backup_auth_fixes/routes/health_check.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/chat_router.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/consolidated_api_routes.py
- Total barriers: 9
- Critical/High: 3

### backup_auth_fixes/routes/meet_routes.py
- Total barriers: 7
- Critical/High: 3

### backup_auth_fixes/routes/view/dashboard.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/view/auth.py
- Total barriers: 21
- Critical/High: 14

### backup_auth_fixes/routes/view/settings.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/view/user.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/view/index.py
- Total barriers: 12
- Critical/High: 5

### backup_auth_fixes/routes/api/health.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/api/shopping.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/api/v1/settings.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/api/v1/weather.py
- Total barriers: 6
- Critical/High: 3

### backup_auth_fixes/routes/auth/standardized_routes.py
- Total barriers: 20
- Critical/High: 13

### backup_auth_fixes/utils/unified_security_services.py
- Total barriers: 7
- Critical/High: 2
