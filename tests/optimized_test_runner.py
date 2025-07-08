"""
Optimized Test Runner for Flask Applications
Focuses on core application files, excludes cache and backup directories
"""
import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, List

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class OptimizedTester:
    """Optimized testing focused on core Flask app files"""
    
    def __init__(self):
        self.results = {
            'files_scanned': 0,
            'auth_barriers': [],
            'critical_errors': [],
            'app_health': {},
            'recommendations': []
        }
        
    def get_core_app_files(self) -> List[Path]:
        """Get core application files only"""
        core_patterns = [
            'app.py',
            'main.py', 
            'database.py',
            'config.py',
            'models.py',
            'routes/*.py',
            'utils/auth_compat.py',
            'utils/unified_*.py',
            'services/*.py'
        ]
        
        # Exclude patterns
        exclude_patterns = [
            '.cache',
            '__pycache__',
            'backup',
            'archive',
            'venv',
            'node_modules',
            '.git',
            '.pytest_cache',
            'build',
            'dist',
            '.egg-info'
        ]
        
        files = []
        
        # Get specific core files
        for pattern in core_patterns:
            if '*' in pattern:
                # Handle wildcard patterns
                if '/' in pattern:
                    dir_part, file_part = pattern.split('/', 1)
                    dir_path = PROJECT_ROOT / dir_part
                    if dir_path.exists():
                        for file_path in dir_path.glob(file_part):
                            if file_path.is_file() and not any(ex in str(file_path) for ex in exclude_patterns):
                                files.append(file_path)
                else:
                    for file_path in PROJECT_ROOT.glob(pattern):
                        if file_path.is_file() and not any(ex in str(file_path) for ex in exclude_patterns):
                            files.append(file_path)
            else:
                file_path = PROJECT_ROOT / pattern
                if file_path.exists():
                    files.append(file_path)
        
        return files
    
    def check_auth_barriers(self, files: List[Path]) -> Dict:
        """Check for authentication barriers in core files"""
        auth_issues = []
        
        barrier_patterns = [
            r'@login_required',
            r'from flask_login import.*login_required',
            r'current_user\.',
            r'You must be logged in',
            r'Login required',
            r'abort\(401\)',
            r'abort\(403\)'
        ]
        
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                for pattern in barrier_patterns:
                    import re
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        auth_issues.append({
                            'file': str(file_path.relative_to(PROJECT_ROOT)),
                            'pattern': pattern,
                            'matches': len(matches),
                            'severity': 'CRITICAL' if 'login_required' in pattern else 'HIGH'
                        })
                        
            except Exception as e:
                logger.warning(f"Could not scan {file_path}: {e}")
        
        return {
            'total_barriers': len(auth_issues),
            'critical_barriers': len([i for i in auth_issues if i['severity'] == 'CRITICAL']),
            'issues': auth_issues
        }
    
    def check_critical_errors(self, files: List[Path]) -> Dict:
        """Check for critical errors in core files"""
        errors = []
        
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                # Check syntax
                try:
                    import ast
                    ast.parse(content)
                except SyntaxError as e:
                    errors.append({
                        'file': str(file_path.relative_to(PROJECT_ROOT)),
                        'type': 'SyntaxError',
                        'line': e.lineno,
                        'message': str(e),
                        'severity': 'CRITICAL'
                    })
                
                # Check for obvious import issues
                import re
                missing_imports = re.findall(r'ModuleNotFoundError|ImportError', content)
                if missing_imports:
                    errors.append({
                        'file': str(file_path.relative_to(PROJECT_ROOT)),
                        'type': 'ImportError',
                        'message': f'{len(missing_imports)} import errors detected',
                        'severity': 'HIGH'
                    })
                    
            except Exception as e:
                logger.warning(f"Could not check errors in {file_path}: {e}")
        
        return {
            'total_errors': len(errors),
            'critical_errors': len([e for e in errors if e['severity'] == 'CRITICAL']),
            'errors': errors
        }
    
    def test_app_health(self) -> Dict:
        """Test basic application health"""
        health = {
            'app_importable': False,
            'database_accessible': False,
            'auth_system_working': False,
            'basic_routes_exist': False
        }
        
        try:
            # Test app import
            import app
            health['app_importable'] = True
            logger.info("✅ App imports successfully")
        except Exception as e:
            logger.error(f"❌ App import failed: {e}")
        
        try:
            # Test database import
            import database
            health['database_accessible'] = True
            logger.info("✅ Database module accessible")
        except Exception as e:
            logger.warning(f"⚠️ Database import issue: {e}")
        
        try:
            # Test auth system
            from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
            user = get_current_user()
            auth_status = is_authenticated()
            health['auth_system_working'] = True
            logger.info("✅ Authentication system working")
        except Exception as e:
            logger.error(f"❌ Auth system issue: {e}")
        
        # Check for route files
        routes_dir = PROJECT_ROOT / 'routes'
        if routes_dir.exists():
            route_files = list(routes_dir.glob('*.py'))
            health['basic_routes_exist'] = len(route_files) > 0
            logger.info(f"✅ Found {len(route_files)} route files")
        
        return health
    
    def run_optimized_tests(self) -> Dict:
        """Run optimized testing suite"""
        logger.info("🚀 Starting Optimized Testing Suite")
        start_time = time.time()
        
        # Get core files only
        core_files = self.get_core_app_files()
        logger.info(f"📁 Scanning {len(core_files)} core application files")
        
        self.results['files_scanned'] = len(core_files)
        
        # Print scanned files for transparency
        logger.info("Core files being scanned:")
        for file_path in core_files[:10]:  # Show first 10
            logger.info(f"  - {file_path.relative_to(PROJECT_ROOT)}")
        if len(core_files) > 10:
            logger.info(f"  ... and {len(core_files) - 10} more")
        
        # Check authentication barriers
        logger.info("🔐 Checking authentication barriers...")
        auth_result = self.check_auth_barriers(core_files)
        self.results['auth_barriers'] = auth_result
        
        # Check critical errors
        logger.info("🐛 Checking critical errors...")
        error_result = self.check_critical_errors(core_files)
        self.results['critical_errors'] = error_result
        
        # Test application health
        logger.info("🏥 Testing application health...")
        health_result = self.test_app_health()
        self.results['app_health'] = health_result
        
        # Generate recommendations
        self.results['recommendations'] = self._generate_recommendations()
        
        end_time = time.time()
        self.results['test_duration'] = end_time - start_time
        
        return self.results
    
    def _generate_recommendations(self) -> List[Dict]:
        """Generate specific recommendations"""
        recommendations = []
        
        # Authentication recommendations
        auth_barriers = self.results['auth_barriers']['total_barriers']
        if auth_barriers > 0:
            recommendations.append({
                'priority': 'CRITICAL',
                'category': 'Authentication',
                'issue': f'{auth_barriers} authentication barriers found',
                'action': 'Run authentication barrier fixer or manually remove @login_required decorators'
            })
        
        # Error recommendations
        critical_errors = self.results['critical_errors']['critical_errors']
        if critical_errors > 0:
            recommendations.append({
                'priority': 'CRITICAL',
                'category': 'Syntax',
                'issue': f'{critical_errors} critical syntax errors found',
                'action': 'Fix syntax errors in Python files before deployment'
            })
        
        # Health recommendations
        health = self.results['app_health']
        if not health['app_importable']:
            recommendations.append({
                'priority': 'CRITICAL',
                'category': 'Application',
                'issue': 'Application cannot be imported',
                'action': 'Fix import errors in app.py'
            })
        
        if not health['auth_system_working']:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Authentication',
                'issue': 'Authentication system not working',
                'action': 'Check utils/auth_compat.py and fix authentication system'
            })
        
        return recommendations
    
    def save_results(self):
        """Save test results"""
        # Save JSON report
        report_path = PROJECT_ROOT / 'tests' / 'optimized_test_results.json'
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        # Save markdown report
        md_path = PROJECT_ROOT / 'tests' / 'optimized_test_results.md'
        self._save_markdown_report(md_path)
        
        logger.info(f"📄 Results saved to {report_path} and {md_path}")
    
    def _save_markdown_report(self, path: Path):
        """Save human-readable markdown report"""
        lines = [
            "# Optimized Test Results",
            f"**Test Duration**: {self.results['test_duration']:.2f}s",
            f"**Files Scanned**: {self.results['files_scanned']} (core files only)",
            "",
            "## Summary"
        ]
        
        # Authentication summary
        auth = self.results['auth_barriers']
        if auth['total_barriers'] == 0:
            lines.append("✅ **Authentication**: No barriers detected")
        else:
            lines.append(f"❌ **Authentication**: {auth['total_barriers']} barriers found ({auth['critical_barriers']} critical)")
        
        # Error summary
        errors = self.results['critical_errors']
        if errors['total_errors'] == 0:
            lines.append("✅ **Errors**: No critical errors detected")
        else:
            lines.append(f"❌ **Errors**: {errors['total_errors']} errors found ({errors['critical_errors']} critical)")
        
        # Health summary
        health = self.results['app_health']
        healthy_systems = sum(1 for v in health.values() if v)
        total_systems = len(health)
        lines.append(f"🏥 **Application Health**: {healthy_systems}/{total_systems} systems working")
        
        # Recommendations
        recommendations = self.results['recommendations']
        if recommendations:
            lines.extend([
                "",
                "## Recommendations"
            ])
            for i, rec in enumerate(recommendations, 1):
                lines.extend([
                    f"### {i}. {rec['category']} ({rec['priority']})",
                    f"**Issue**: {rec['issue']}",
                    f"**Action**: {rec['action']}",
                    ""
                ])
        else:
            lines.extend([
                "",
                "## Recommendations",
                "✅ No critical issues found - system appears healthy!"
            ])
        
        # Detailed findings
        if auth['issues']:
            lines.extend([
                "",
                "## Authentication Barriers Found",
                "| File | Pattern | Matches | Severity |",
                "|------|---------|---------|----------|"
            ])
            for issue in auth['issues']:
                lines.append(f"| {issue['file']} | {issue['pattern']} | {issue['matches']} | {issue['severity']} |")
        
        if errors['errors']:
            lines.extend([
                "",
                "## Critical Errors Found",
                "| File | Type | Message | Severity |",
                "|------|------|---------|----------|"
            ])
            for error in errors['errors']:
                msg = error['message'][:50] + "..." if len(error['message']) > 50 else error['message']
                lines.append(f"| {error['file']} | {error['type']} | {msg} | {error['severity']} |")
        
        with open(path, 'w') as f:
            f.write('\n'.join(lines))

def main():
    """Main entry point"""
    print("⚡ Optimized NOUS Testing Suite")
    print("Focused testing on core Flask application files")
    print("=" * 50)
    
    tester = OptimizedTester()
    results = tester.run_optimized_tests()
    tester.save_results()
    
    print("\n" + "=" * 50)
    print("OPTIMIZED TEST RESULTS")
    print("=" * 50)
    
    # Summary
    print(f"Files Scanned: {results['files_scanned']} (core files only)")
    print(f"Test Duration: {results['test_duration']:.2f}s")
    
    # Authentication status
    auth = results['auth_barriers']
    if auth['total_barriers'] == 0:
        print("✅ Authentication: No barriers detected")
    else:
        print(f"❌ Authentication: {auth['total_barriers']} barriers found")
    
    # Error status
    errors = results['critical_errors']
    if errors['total_errors'] == 0:
        print("✅ Errors: No critical errors detected")
    else:
        print(f"❌ Errors: {errors['total_errors']} errors found")
    
    # Health status
    health = results['app_health']
    healthy_count = sum(1 for v in health.values() if v)
    total_count = len(health)
    print(f"🏥 Health: {healthy_count}/{total_count} systems working")
    
    # Recommendations
    recommendations = results['recommendations']
    if recommendations:
        print(f"\n🔧 Recommendations ({len(recommendations)}):")
        for rec in recommendations:
            print(f"  {rec['priority']}: {rec['issue']}")
    else:
        print("\n✅ No critical issues found!")
    
    print("\nDetailed results: tests/optimized_test_results.md")
    
    # Return exit code
    critical_issues = auth['critical_barriers'] + errors['critical_errors']
    return 1 if critical_issues > 0 else 0

if __name__ == "__main__":
    sys.exit(main())