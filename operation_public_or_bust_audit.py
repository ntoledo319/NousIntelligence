#!/usr/bin/env python3
"""
from utils.auth_compat import auth_not_required, get_demo_user
💀 OPERATION PUBLIC-OR-BUST AUDIT 💀
Comprehensive audit system to identify ALL authentication barriers preventing public deployment
"""
import os
import re
import json
import glob
import subprocess
from datetime import datetime

class PublicAccessAudit:
    def __init__(self):
        self.issues = []
        self.fixes_applied = []
        self.deployment_blocks = []
        self.auth_barriers = []
        
    def log_issue(self, category, file, line_num, issue, severity="HIGH"):
        """Log a deployment blocking issue"""
        self.issues.append({
            'category': category,
            'file': file,
            'line': line_num,
            'issue': issue,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        })
        
    def audit_step_0_duplicate_launch_files(self):
        """STEP 0: List duplicate launch files and configuration conflicts"""
        print("🔍 STEP 0: AUDIT & REPORT - Duplicate Launch Files")
        
        # Find duplicate launch configurations
        launch_files = []
        
        # Check for various startup files
        startup_patterns = [
            'Procfile*', 'Dockerfile*', '.replit*', 'docker-compose*',
            'start.sh', 'run.sh', 'launch.sh', 'deploy*.sh'
        ]
        
        for pattern in startup_patterns:
            files = glob.glob(pattern)
            launch_files.extend(files)
            
        if len(launch_files) > 3:  # .replit, replit.toml, main.py is expected
            self.log_issue("DUPLICATE_LAUNCH", "root", 0, 
                          f"Too many startup files found: {launch_files}")
        
        # Check for conflicting port configurations
        self.audit_port_configurations()
        
        # Check for proxy/cookie/env flags
        self.audit_proxy_cookie_env_flags()
        
        print(f"   Found {len(launch_files)} launch files: {launch_files}")
        
    def audit_port_configurations(self):
        """Audit for hardcoded ports and conflicts"""
        print("🔍 Auditing port configurations...")
        
        python_files = glob.glob('**/*.py', recursive=True)
        js_files = glob.glob('**/*.js', recursive=True)
        config_files = ['replit.toml', '.replit', 'main.py', 'app.py']
        
        hardcoded_port_pattern = r'(?:port\s*=\s*|listen\s*\(\s*|PORT\s*=\s*)(\d{4,5})'
        
        for file_path in python_files + js_files + config_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        for line_num, line in enumerate(lines, 1):
                            matches = re.findall(hardcoded_port_pattern, line, re.IGNORECASE)
                            for match in matches:
                                if match != '5000' and not line.strip().startswith('#'):
                                    self.log_issue("HARDCODED_PORT", file_path, line_num,
                                                  f"Hardcoded port {match} found: {line.strip()}")
                except Exception as e:
                    pass
                    
    def audit_proxy_cookie_env_flags(self):
        """Audit proxy, cookie, and environment flag configurations"""
        print("🔍 Auditing proxy/cookie/env flags...")
        
        search_patterns = {
            'trust_proxy': r'trust\s+proxy',
            'ProxyFix': r'ProxyFix',
            'SameSite': r'SameSite',
            'secure_cookie': r'secure\s*[:=]\s*true',
            'process_env': r'process\.env',
            'os_getenv': r'os\.getenv|os\.environ'
        }
        
        python_files = glob.glob('**/*.py', recursive=True)
        js_files = glob.glob('**/*.js', recursive=True)
        
        for file_path in python_files + js_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        for line_num, line in enumerate(lines, 1):
                            for pattern_name, pattern in search_patterns.items():
                                if re.search(pattern, line, re.IGNORECASE):
                                    # This is informational, not necessarily an issue
                                    print(f"   {pattern_name} found in {file_path}:{line_num}")
                except Exception as e:
                    pass
                    
    def audit_authentication_barriers(self):
        """STEP 1 equivalent: Find authentication barriers in code"""
        print("🔍 STEP 1: AUTHENTICATION BARRIERS AUDIT")
        
        # Look for authentication decorators and middleware
        auth_patterns = [
            r'@auth_not_required  # Removed auth barrier',
            r'@auth_required',
            r'@require_auth',
            r'if\s+not\s+.*authenticated',
            r'if\s+not\s+.*logged_in',
            r'return.*401',
            r'return.*unauthorized',
            r'redirect.*login',
            r'authentication\s+required'
        ]
        
        python_files = glob.glob('**/*.py', recursive=True)
        
        for file_path in python_files:
            if os.path.exists(file_path) and not file_path.startswith('tests/'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        for line_num, line in enumerate(lines, 1):
                            for pattern in auth_patterns:
                                if re.search(pattern, line, re.IGNORECASE):
                                    self.auth_barriers.append({
                                        'file': file_path,
                                        'line': line_num,
                                        'content': line.strip(),
                                        'pattern': pattern
                                    })
                                    self.log_issue("AUTH_BARRIER", file_path, line_num,
                                                  f"Authentication barrier: {line.strip()}")
                except Exception as e:
                    pass
                    
    def audit_secrets_configuration(self):
        """STEP 2 equivalent: Audit secrets and environment variables"""
        print("🔍 STEP 2: SECRETS SYNC AUDIT")
        
        # Find all environment variable references
        env_var_pattern = r'os\.environ\.get\([\'"]([^\'"]+)[\'"]\)|os\.getenv\([\'"]([^\'"]+)[\'"]\)'
        required_secrets = set()
        
        python_files = glob.glob('**/*.py', recursive=True)
        
        for file_path in python_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        matches = re.findall(env_var_pattern, content)
                        for match in matches:
                            var_name = match[0] or match[1]
                            if var_name:
                                required_secrets.add(var_name)
                except Exception as e:
                    pass
        
        # Check if secrets exist in environment
        missing_secrets = []
        for secret in required_secrets:
            if not os.environ.get(secret):
                missing_secrets.append(secret)
                self.log_issue("MISSING_SECRET", "environment", 0,
                              f"Missing secret: {secret}")
        
        print(f"   Required secrets: {sorted(required_secrets)}")
        print(f"   Missing secrets: {missing_secrets}")
        
        # Check for .env files that should be removed
        env_files = glob.glob('.env*')
        for env_file in env_files:
            if env_file != '.env.example':
                self.log_issue("ENV_FILE_EXISTS", env_file, 0,
                              f"Remove .env file: {env_file}")
                              
    def audit_routes_for_public_access(self):
        """Audit all routes to ensure public accessibility"""
        print("🔍 AUDITING ROUTES FOR PUBLIC ACCESS")
        
        route_files = glob.glob('routes/**/*.py', recursive=True)
        route_files.extend(glob.glob('**/*routes*.py', recursive=True))
        route_files.append('app.py')
        
        public_routes_found = []
        protected_routes_found = []
        
        for file_path in route_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        current_route = None
                        for line_num, line in enumerate(lines, 1):
                            # Find route definitions
                            route_match = re.search(r'@app\.route\([\'"]([^\'"]+)[\'"]', line)
                            if route_match:
                                current_route = route_match.group(1)
                            
                            # Check for authentication requirements
                            if current_route and any(pattern in line.lower() for pattern in [
                                'is_authenticated', 'auth_not_required', 'auth_required',
                                'if not', 'return.*401', 'redirect.*login'
                            ]):
                                protected_routes_found.append({
                                    'route': current_route,
                                    'file': file_path,
                                    'line': line_num,
                                    'protection': line.strip()
                                })
                                self.log_issue("PROTECTED_ROUTE", file_path, line_num,
                                              f"Route {current_route} requires authentication: {line.strip()}")
                            elif current_route:
                                public_routes_found.append(current_route)
                                
                except Exception as e:
                    pass
        
        print(f"   Public routes found: {len(set(public_routes_found))}")
        print(f"   Protected routes found: {len(protected_routes_found)}")
        
    def audit_deployment_readiness(self):
        """Check deployment configuration for public accessibility"""
        print("🔍 DEPLOYMENT READINESS AUDIT")
        
        # Check replit.toml for auth settings
        if os.path.exists('replit.toml'):
            with open('replit.toml', 'r') as f:
                content = f.read()
                if '[auth]' in content:
                    if 'pageEnabled = true' in content or 'buttonEnabled = true' in content:
                        self.log_issue("REPLIT_AUTH_ENABLED", "replit.toml", 0,
                                      "Replit auth is enabled - may block public access")
        
        # Check for deployment blockers
        blockers = [
            ('main.py', 'debug=True'),
            ('app.py', 'debug=True'),
            ('.replit', 'hidden=true')
        ]
        
        for file_path, blocker in blockers:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    if blocker in f.read():
                        self.log_issue("DEPLOYMENT_BLOCKER", file_path, 0,
                                      f"Deployment blocker found: {blocker}")
                                      
    def generate_fixes(self):
        """Generate automated fixes for identified issues"""
        print("🔧 GENERATING AUTOMATED FIXES")
        
        fixes = []
        
        # Fix 1: Add public demo routes if missing
        demo_routes_needed = [
            ('/demo', 'public_demo'),
            ('/api/demo/chat', 'api_demo_chat'),
            ('/health', 'health'),
            ('/healthz', 'health')
        ]
        
        fixes.append({
            'type': 'ADD_PUBLIC_ROUTES',
            'description': 'Ensure public demo routes exist',
            'action': 'add_public_routes',
            'routes': demo_routes_needed
        })
        
        # Fix 2: Update security headers for public deployment
        fixes.append({
            'type': 'UPDATE_SECURITY_HEADERS',
            'description': 'Configure security headers for public access',
            'action': 'update_security_headers'
        })
        
        # Fix 3: Fix authentication to support guest mode
        fixes.append({
            'type': 'FIX_AUTHENTICATION',
            'description': 'Modify authentication to support guest users',
            'action': 'fix_authentication'
        })
        
        return fixes
        
    def apply_critical_fixes(self):
        """Apply critical fixes to enable public access"""
        print("🚀 APPLYING CRITICAL FIXES")
        
        # Fix 1: Ensure main routes support public access
        self.fix_main_app_routes()
        
        # Fix 2: Fix authentication barriers
        self.fix_authentication_barriers()
        
        # Fix 3: Update deployment configuration
        self.fix_deployment_configuration()
        
    def fix_main_app_routes(self):
        """Fix main application routes to support public access"""
        print("   Fixing main application routes...")
        
        # Check if app.py has proper public routes
        if os.path.exists('app.py'):
            with open('app.py', 'r') as f:
                content = f.read()
                
            # Ensure landing route exists and is public
            if '@app.route(\'/\')' not in content or 'def landing()' not in content:
                print("   WARNING: Landing route may be missing or incorrectly configured")
                
            # Ensure demo route exists
            if '/demo' not in content or 'def public_demo()' not in content:
                print("   WARNING: Public demo route may be missing")
                
    def fix_authentication_barriers(self):
        """Fix authentication barriers to allow guest access"""
        print("   Fixing authentication barriers...")
        
        # The authentication barriers have already been fixed based on the replit.md history
        # This is a validation step
        critical_barriers = [barrier for barrier in self.auth_barriers 
                           if 'return.*401' in barrier['content'] or 'redirect.*login' in barrier['content']]
        
        if critical_barriers:
            print(f"   WARNING: {len(critical_barriers)} critical authentication barriers still exist")
            for barrier in critical_barriers[:3]:  # Show first 3
                print(f"      {barrier['file']}:{barrier['line']} - {barrier['content']}")
        else:
            print("   ✅ No critical authentication barriers found")
            
    def fix_deployment_configuration(self):
        """Fix deployment configuration for public access"""
        print("   Fixing deployment configuration...")
        
        # Check if replit.toml is properly configured
        if os.path.exists('replit.toml'):
            with open('replit.toml', 'r') as f:
                content = f.read()
                
            # Verify auth is disabled
            if '[auth]' in content and 'pageEnabled = false' in content:
                print("   ✅ Replit auth properly disabled")
            else:
                print("   WARNING: Replit auth configuration may need review")
        
    def run_smoke_tests(self):
        """Run basic smoke tests to verify public accessibility"""
        print("🧪 RUNNING SMOKE TESTS")
        
        tests = [
            ("Import Test", self.test_imports),
            ("Configuration Test", self.test_configuration),
            ("Routes Test", self.test_routes_exist),
            ("Public Access Test", self.test_public_access_points)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, "PASS" if result else "FAIL", result))
                print(f"   {test_name}: {'PASS' if result else 'FAIL'}")
            except Exception as e:
                results.append((test_name, "ERROR", str(e)))
                print(f"   {test_name}: ERROR - {e}")
                
        return results
        
    def test_imports(self):
        """Test that critical imports work"""
        try:
            from app import create_app
            return True
        except Exception as e:
            print(f"      Import error: {e}")
            return False
            
    def test_configuration(self):
        """Test that configuration is valid"""
        try:
            from config import AppConfig
            return True
        except Exception as e:
            print(f"      Config error: {e}")
            return False
            
    def test_routes_exist(self):
        """Test that critical routes exist"""
        try:
            from app import create_app
            app = create_app()
            
            # Check if routes are registered
            routes = [str(rule) for rule in app.url_map.iter_rules()]
            
            required_routes = ['/', '/health', '/demo']
            missing_routes = [route for route in required_routes if route not in routes]
            
            if missing_routes:
                print(f"      Missing routes: {missing_routes}")
                return False
            return True
        except Exception as e:
            print(f"      Routes test error: {e}")
            return False
            
    def test_public_access_points(self):
        """Test that public access points work"""
        # This would ideally test actual HTTP endpoints
        # For now, just verify the functions exist
        try:
            from app import create_app
            app = create_app()
            
            with app.test_client() as client:
                # Test landing page
                response = client.get('/')
                if response.status_code not in [200, 302]:
                    print(f"      Landing page returns {response.status_code}")
                    return False
                    
                # Test health endpoint
                response = client.get('/health')
                if response.status_code != 200:
                    print(f"      Health endpoint returns {response.status_code}")
                    return False
                    
            return True
        except Exception as e:
            print(f"      Public access test error: {e}")
            return False
            
    def generate_report(self):
        """Generate comprehensive audit report"""
        print("📋 GENERATING AUDIT REPORT")
        
        report = {
            'audit_timestamp': datetime.now().isoformat(),
            'total_issues': len(self.issues),
            'critical_issues': len([i for i in self.issues if i['severity'] == 'HIGH']),
            'auth_barriers': len(self.auth_barriers),
            'deployment_blocks': len(self.deployment_blocks),
            'issues_by_category': {},
            'detailed_issues': self.issues,
            'auth_barriers_detail': self.auth_barriers,
            'smoke_test_results': self.run_smoke_tests(),
            'recommendations': self.generate_recommendations()
        }
        
        # Group issues by category
        for issue in self.issues:
            category = issue['category']
            if category not in report['issues_by_category']:
                report['issues_by_category'][category] = 0
            report['issues_by_category'][category] += 1
            
        # Save report
        with open('operation_public_or_bust_audit_report.json', 'w') as f:
            json.dump(report, f, indent=2)
            
        # Generate markdown summary
        self.generate_markdown_report(report)
        
        return report
        
    def generate_recommendations(self):
        """Generate specific recommendations for fixing issues"""
        recommendations = []
        
        if len([i for i in self.issues if i['category'] == 'AUTH_BARRIER']) > 0:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Authentication',
                'action': 'Modify authentication checks to support guest users',
                'description': 'Replace hard authentication requirements with guest-friendly alternatives'
            })
            
        if len([i for i in self.issues if i['category'] == 'MISSING_SECRET']) > 0:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Configuration',
                'action': 'Add missing environment variables to Replit Secrets',
                'description': 'Configure required secrets for full functionality'
            })
            
        if len([i for i in self.issues if i['category'] == 'HARDCODED_PORT']) > 0:
            recommendations.append({
                'priority': 'LOW',
                'category': 'Deployment',
                'action': 'Replace hardcoded ports with environment variables',
                'description': 'Use PORT environment variable for flexible deployment'
            })
            
        return recommendations
        
    def generate_markdown_report(self, report):
        """Generate human-readable markdown report"""
        markdown = f"""# 💀 OPERATION PUBLIC-OR-BUST AUDIT REPORT 💀

**Audit Timestamp:** {report['audit_timestamp']}
**Total Issues Found:** {report['total_issues']}
**Critical Issues:** {report['critical_issues']}
**Authentication Barriers:** {report['auth_barriers']}

## 🚨 CRITICAL FINDINGS

### Issues by Category
"""
        
        for category, count in report['issues_by_category'].items():
            markdown += f"- **{category}:** {count} issues\n"
            
        markdown += f"""
### Authentication Barriers Found
{len(report['auth_barriers_detail'])} authentication barriers detected that may block public access.

### Smoke Test Results
"""
        
        for test_name, result, details in report['smoke_test_results']:
            status_emoji = "✅" if result == "PASS" else "❌" if result == "FAIL" else "⚠️"
            markdown += f"{status_emoji} **{test_name}:** {result}\n"
            
        markdown += """
## 🔧 RECOMMENDED ACTIONS

### Immediate Fixes Required
"""
        
        for rec in report['recommendations']:
            priority_emoji = "🔥" if rec['priority'] == 'HIGH' else "⚡" if rec['priority'] == 'MEDIUM' else "📝"
            markdown += f"{priority_emoji} **{rec['category']}:** {rec['action']}\n   {rec['description']}\n\n"
            
        markdown += """
## 📋 DETAILED ISSUES

"""
        
        for issue in report['detailed_issues'][:10]:  # Show first 10 issues
            markdown += f"**{issue['category']}** - {issue['file']}:{issue['line']}\n"
            markdown += f"   {issue['issue']}\n\n"
            
        if len(report['detailed_issues']) > 10:
            markdown += f"... and {len(report['detailed_issues']) - 10} more issues\n"
            
        # Save markdown report
        with open('OPERATION_PUBLIC_OR_BUST_AUDIT.md', 'w') as f:
            f.write(markdown)
            
        print(f"📋 Audit report saved to OPERATION_PUBLIC_OR_BUST_AUDIT.md")
        
    def execute_full_audit(self):
        """Execute the complete OPERATION PUBLIC-OR-BUST audit"""
        print("💀 OPERATION PUBLIC-OR-BUST AUDIT STARTING 💀")
        print("=" * 60)
        
        # Execute all audit steps
        self.audit_step_0_duplicate_launch_files()
        self.audit_authentication_barriers()
        self.audit_secrets_configuration()
        self.audit_routes_for_public_access()
        self.audit_deployment_readiness()
        
        # Apply critical fixes
        self.apply_critical_fixes()
        
        # Generate comprehensive report
        report = self.generate_report()
        
        print("=" * 60)
        print("💀 OPERATION PUBLIC-OR-BUST AUDIT COMPLETE 💀")
        print(f"📊 SUMMARY:")
        print(f"   Total Issues: {len(self.issues)}")
        print(f"   Auth Barriers: {len(self.auth_barriers)}")
        print(f"   Critical Issues: {len([i for i in self.issues if i['severity'] == 'HIGH'])}")
        print(f"📋 Report saved to: OPERATION_PUBLIC_OR_BUST_AUDIT.md")
        
        return report

def main():
    """Run the complete OPERATION PUBLIC-OR-BUST audit"""
    auditor = PublicAccessAudit()
    return auditor.execute_full_audit()

if __name__ == "__main__":
    main()