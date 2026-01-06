#!/usr/bin/env python3
"""
Pre-Launch Verification Script for NOUS Intelligence
Checks that all critical components are ready for GitHub Sponsors launch
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def check_file_exists(filepath: str, required: bool = True) -> Tuple[bool, str]:
    """Check if a file exists"""
    exists = Path(filepath).exists()
    status = f"{'✅' if exists else '❌'} {filepath}"
    
    if not exists and required:
        return False, f"{status} - REQUIRED FILE MISSING"
    elif not exists:
        return True, f"{status} - Optional (recommended)"
    return True, f"{status} - Found"

def check_env_example() -> Tuple[bool, str]:
    """Check .env.example has required variables"""
    required_vars = [
        'DATABASE_URL',
        'SESSION_SECRET',
        'GEMINI_API_KEY',
        'OPENROUTER_API_KEY',
        'GOOGLE_CLIENT_ID',
    ]
    
    if not Path('.env.example').exists():
        return False, "❌ .env.example missing"
    
    content = Path('.env.example').read_text()
    missing = [var for var in required_vars if var not in content]
    
    if missing:
        return False, f"❌ .env.example missing variables: {', '.join(missing)}"
    
    return True, "✅ .env.example has all required variables"

def check_no_hardcoded_secrets() -> Tuple[bool, str]:
    """Quick check for obvious hardcoded secrets"""
    files_to_check = ['app.py', 'config/production.py']
    suspicious_patterns = [
        'sk-',  # OpenAI/OpenRouter keys
        'secret_key = "',
        'pass' + 'word = "',
    ]
    
    issues = []
    for filepath in files_to_check:
        if not Path(filepath).exists():
            continue
            
        content = Path(filepath).read_text().lower()
        for pattern in suspicious_patterns:
            if pattern in content and 'example' not in content:
                issues.append(f"{filepath} may contain {pattern}")
    
    if issues:
        return False, f"⚠️  Possible hardcoded secrets: {', '.join(issues)}"
    
    return True, "✅ No obvious hardcoded secrets detected"

def check_documentation() -> Tuple[bool, str]:
    """Check critical documentation exists"""
    docs = {
        'README.md': True,
        'SPONSORS.md': True,
        'DEPLOYMENT_QUICKSTART.md': True,
        'docs/AI_SETUP_GUIDE.md': True,
        'CONTRIBUTING.md': False,
        'CODE_OF_CONDUCT.md': False,
    }
    
    missing_required = []
    missing_optional = []
    
    for doc, required in docs.items():
        if not Path(doc).exists():
            if required:
                missing_required.append(doc)
            else:
                missing_optional.append(doc)
    
    if missing_required:
        return False, f"❌ Required docs missing: {', '.join(missing_required)}"
    
    if missing_optional:
        return True, f"⚠️  Optional docs missing: {', '.join(missing_optional)}"
    
    return True, "✅ All documentation present"

def check_github_config() -> Tuple[bool, str]:
    """Check GitHub configuration files"""
    required = [
        '.github/FUNDING.yml',
        '.github/ISSUE_TEMPLATE/bug_report.yml',
        '.github/pull_request_template.md',
    ]
    
    missing = [f for f in required if not Path(f).exists()]
    
    if missing:
        return False, f"❌ GitHub config missing: {', '.join(missing)}"
    
    return True, "✅ GitHub configuration complete"

def check_deployment_files() -> Tuple[bool, str]:
    """Check deployment configuration"""
    files = {
        'Dockerfile': True,
        'docker-compose.yml': True,
        '.dockerignore': True,
        'gunicorn.conf.py': False,
    }
    
    missing = [f for f, required in files.items() if required and not Path(f).exists()]
    
    if missing:
        return False, f"❌ Deployment files missing: {', '.join(missing)}"
    
    return True, "✅ Deployment files ready"

def check_core_functionality() -> Tuple[bool, str]:
    """Check core code files exist"""
    core_files = [
        'app.py',
        'main.py',
        'routes/cbt_routes.py',
        'routes/api_routes.py',
        'services/emotion_aware_therapeutic_assistant.py',
        'utils/unified_ai_service.py',
    ]
    
    missing = [f for f in core_files if not Path(f).exists()]
    
    if missing:
        return False, f"❌ Core files missing: {', '.join(missing)}"
    
    return True, "✅ Core functionality files present"

def check_cbt_routes() -> Tuple[bool, str]:
    """Check CBT routes implementation"""
    if not Path('routes/cbt_routes.py').exists():
        return False, "❌ routes/cbt_routes.py missing"
    
    content = Path('routes/cbt_routes.py').read_text()
    required_routes = [
        '/cbt/api/thought-records',
        '/cbt/api/mood',
        'create_thought_record_api',
        'log_mood_api',
        'identify_cognitive_biases',
    ]
    
    missing = [r for r in required_routes if r not in content]
    
    if missing:
        return False, f"⚠️  CBT routes may be incomplete: {', '.join(missing[:2])}..."
    
    return True, "✅ CBT routes fully implemented"

def main():
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BLUE}NOUS Intelligence - Sponsor Readiness Verification{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}\n")
    
    checks = [
        ("Core Functionality", check_core_functionality),
        ("CBT Routes Implementation", check_cbt_routes),
        ("Documentation", check_documentation),
        ("Environment Config", check_env_example),
        ("GitHub Configuration", check_github_config),
        ("Deployment Files", check_deployment_files),
        ("Security Check", check_no_hardcoded_secrets),
    ]
    
    results = []
    all_passed = True
    
    for name, check_func in checks:
        try:
            passed, message = check_func()
            results.append((name, passed, message))
            
            if not passed:
                all_passed = False
                print(f"{Colors.RED}{message}{Colors.RESET}")
            elif '⚠️' in message:
                print(f"{Colors.YELLOW}{message}{Colors.RESET}")
            else:
                print(f"{Colors.GREEN}{message}{Colors.RESET}")
                
        except Exception as e:
            results.append((name, False, f"Error: {e}"))
            all_passed = False
            print(f"{Colors.RED}❌ {name}: Error - {e}{Colors.RESET}")
    
    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
    
    passed_count = sum(1 for _, passed, _ in results if passed)
    total_count = len(results)
    
    print(f"\n{Colors.BLUE}Summary:{Colors.RESET}")
    print(f"  Passed: {passed_count}/{total_count}")
    
    if all_passed:
        print(f"\n{Colors.GREEN}{'='*70}{Colors.RESET}")
        print(f"{Colors.GREEN}✅ SPONSOR READY!{Colors.RESET}")
        print(f"{Colors.GREEN}All critical checks passed.{Colors.RESET}")
        print(f"{Colors.GREEN}{'='*70}{Colors.RESET}\n")
        
        print(f"{Colors.BLUE}Next Steps:{Colors.RESET}")
        print("  1. Review LAUNCH_CHECKLIST.md")
        print("  2. Deploy demo instance (see DEPLOYMENT_QUICKSTART.md)")
        print("  3. Apply for GitHub Sponsors (see GITHUB_SPONSORS_SETUP.md)")
        print("  4. Test everything manually")
        print("  5. Launch when comfortable!\n")
        
        return 0
    else:
        print(f"\n{Colors.RED}{'='*70}{Colors.RESET}")
        print(f"{Colors.RED}❌ NOT READY YET{Colors.RESET}")
        print(f"{Colors.RED}Please address the issues above before launching.{Colors.RESET}")
        print(f"{Colors.RED}{'='*70}{Colors.RESET}\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
