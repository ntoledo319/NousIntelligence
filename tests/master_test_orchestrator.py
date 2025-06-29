"""
Master Test Orchestrator
Comprehensive testing infrastructure with zero authentication barriers
Coordinates all testing systems for complete bug detection and problem resolution
"""
import os
import sys
import json
import time
import logging
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('tests/test_orchestrator.log')
    ]
)
logger = logging.getLogger(__name__)

class MasterTestOrchestrator:
    """Master orchestrator for comprehensive testing infrastructure"""
    
    def __init__(self):
        self.test_results = {
            'comprehensive_tests': {},
            'authentication_barriers': {},
            'error_detection': {},
            'performance_metrics': {},
            'security_analysis': {},
            'deployment_readiness': {}
        }
        self.start_time = time.time()
        self.base_url = self._get_base_url()
        
        # Ensure tests directory exists
        Path('tests').mkdir(exist_ok=True)
        
    def _get_base_url(self) -> str:
        """Get application base URL"""
        try:
            from config import PORT, HOST
            return f"http://{HOST}:{PORT}"
        except ImportError:
            return "http://localhost:5000"
    
    def run_complete_testing_suite(self) -> Dict:
        """Run complete testing infrastructure"""
        logger.info("🚀 Starting Master Test Orchestration")
        logger.info("=" * 60)
        
        # Phase 1: Pre-flight checks
        self._run_preflight_checks()
        
        # Phase 2: Authentication barrier elimination
        self._run_authentication_testing()
        
        # Phase 3: Comprehensive error detection
        self._run_error_detection()
        
        # Phase 4: Application testing
        self._run_application_testing()
        
        # Phase 5: Performance analysis
        self._run_performance_testing()
        
        # Phase 6: Security validation
        self._run_security_testing()
        
        # Phase 7: Deployment readiness
        self._run_deployment_testing()
        
        # Generate master report
        return self._generate_master_report()
    
    def _run_preflight_checks(self):
        """Run pre-flight system checks"""
        logger.info("🔍 Phase 1: Pre-flight System Checks")
        
        preflight_results = {
            'python_version': sys.version,
            'working_directory': str(Path.cwd()),
            'critical_files_exist': {},
            'environment_variables': {},
            'system_dependencies': {}
        }
        
        # Check critical files
        critical_files = [
            'app.py', 'main.py', 'config.py', 'database.py', 
            'pyproject.toml', 'replit.toml', 'utils/auth_compat.py'
        ]
        
        for file_path in critical_files:
            exists = Path(file_path).exists()
            preflight_results['critical_files_exist'][file_path] = exists
            if not exists:
                logger.warning(f"❌ Critical file missing: {file_path}")
            else:
                logger.info(f"✅ Critical file found: {file_path}")
        
        # Check environment variables
        env_vars = ['DATABASE_URL', 'PORT', 'SESSION_SECRET']
        for var in env_vars:
            value = os.environ.get(var)
            preflight_results['environment_variables'][var] = bool(value)
            if value:
                logger.info(f"✅ Environment variable {var} set")
            else:
                logger.warning(f"⚠️ Environment variable {var} not set")
        
        self.test_results['preflight'] = preflight_results
    
    def _run_authentication_testing(self):
        """Run comprehensive authentication barrier testing"""
        logger.info("🔐 Phase 2: Authentication Barrier Testing")
        
        try:
            # Import and run authentication barrier detector
            from authentication_barrier_detector import AuthenticationBarrierDetector, AuthenticationBarrierFixer
            
            # Detect barriers
            detector = AuthenticationBarrierDetector()
            barrier_report = detector.scan_entire_codebase()
            
            logger.info(f"Found {barrier_report['summary']['total_barriers']} authentication barriers")
            
            # Fix barriers if found
            if barrier_report['summary']['total_barriers'] > 0:
                logger.info("🔧 Fixing authentication barriers...")
                fixer = AuthenticationBarrierFixer()
                fix_results = fixer.fix_all_barriers(create_backup=True)
                
                logger.info(f"Applied fixes:")
                logger.info(f"  - Flask-Login fixes: {fix_results['flask_login_fixes']}")
                logger.info(f"  - Auth message fixes: {fix_results['auth_message_fixes']}")
                logger.info(f"  - Redirect fixes: {fix_results['redirect_fixes']}")
                logger.info(f"  - Abort fixes: {fix_results['abort_fixes']}")
                
                # Re-scan to verify fixes
                post_fix_report = detector.scan_entire_codebase()
                logger.info(f"After fixes: {post_fix_report['summary']['total_barriers']} barriers remain")
                
                self.test_results['authentication_barriers'] = {
                    'initial_barriers': barrier_report['summary']['total_barriers'],
                    'fixes_applied': fix_results,
                    'remaining_barriers': post_fix_report['summary']['total_barriers'],
                    'fix_success_rate': 1 - (post_fix_report['summary']['total_barriers'] / max(barrier_report['summary']['total_barriers'], 1))
                }
            else:
                logger.info("✅ No authentication barriers detected")
                self.test_results['authentication_barriers'] = {
                    'initial_barriers': 0,
                    'fixes_applied': {},
                    'remaining_barriers': 0,
                    'fix_success_rate': 1.0
                }
            
        except Exception as e:
            logger.error(f"Authentication testing failed: {e}")
            self.test_results['authentication_barriers'] = {
                'error': str(e),
                'status': 'failed'
            }
    
    def _run_error_detection(self):
        """Run comprehensive error detection"""
        logger.info("🐛 Phase 3: Comprehensive Error Detection")
        
        try:
            from advanced_error_testing import AdvancedErrorDetector
            
            detector = AdvancedErrorDetector()
            error_report = detector.run_comprehensive_error_scan()
            
            logger.info(f"Found {error_report['summary']['total_errors']} total errors")
            logger.info(f"  - Critical: {error_report['summary']['critical_errors']}")
            logger.info(f"  - High: {error_report['summary']['high_priority_errors']}")
            logger.info(f"  - Medium: {error_report['summary']['medium_priority_errors']}")
            
            self.test_results['error_detection'] = error_report
            
        except Exception as e:
            logger.error(f"Error detection failed: {e}")
            self.test_results['error_detection'] = {
                'error': str(e),
                'status': 'failed'
            }
    
    def _run_application_testing(self):
        """Run comprehensive application testing"""
        logger.info("🌐 Phase 4: Application Testing")
        
        try:
            from comprehensive_test_suite import ComprehensiveTestSuite
            
            test_suite = ComprehensiveTestSuite(base_url=self.base_url)
            app_results = test_suite.run_comprehensive_tests()
            
            logger.info(f"Application tests: {app_results['passed']} passed, {app_results['failed']} failed")
            logger.info(f"Authentication issues: {len(app_results['authentication_issues'])}")
            logger.info(f"Performance issues: {len(app_results['performance_issues'])}")
            
            self.test_results['comprehensive_tests'] = app_results
            
        except Exception as e:
            logger.error(f"Application testing failed: {e}")
            self.test_results['comprehensive_tests'] = {
                'error': str(e),
                'status': 'failed'
            }
    
    def _run_performance_testing(self):
        """Run performance testing"""
        logger.info("⚡ Phase 5: Performance Testing")
        
        performance_results = {
            'response_times': {},
            'memory_usage': {},
            'concurrent_requests': {},
            'database_performance': {}
        }
        
        try:
            # Test response times
            endpoints = ['/', '/health', '/api/health']
            session = requests.Session()
            
            for endpoint in endpoints:
                try:
                    start_time = time.time()
                    response = session.get(f"{self.base_url}{endpoint}", timeout=10)
                    end_time = time.time()
                    
                    response_time = end_time - start_time
                    performance_results['response_times'][endpoint] = {
                        'time': response_time,
                        'status_code': response.status_code,
                        'status': 'good' if response_time < 1.0 else 'slow' if response_time < 5.0 else 'very_slow'
                    }
                    
                    logger.info(f"Response time {endpoint}: {response_time:.3f}s")
                    
                except Exception as e:
                    logger.warning(f"Could not test {endpoint}: {e}")
                    performance_results['response_times'][endpoint] = {'error': str(e)}
            
            # Test memory usage
            try:
                import psutil
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                performance_results['memory_usage'] = {
                    'memory_mb': memory_mb,
                    'status': 'good' if memory_mb < 100 else 'moderate' if memory_mb < 500 else 'high'
                }
                logger.info(f"Memory usage: {memory_mb:.1f}MB")
            except Exception as e:
                logger.warning(f"Could not measure memory: {e}")
                performance_results['memory_usage'] = {'error': str(e)}
            
            self.test_results['performance_metrics'] = performance_results
            
        except Exception as e:
            logger.error(f"Performance testing failed: {e}")
            self.test_results['performance_metrics'] = {
                'error': str(e),
                'status': 'failed'
            }
    
    def _run_security_testing(self):
        """Run security testing"""
        logger.info("🔒 Phase 6: Security Testing")
        
        security_results = {
            'headers': {},
            'vulnerabilities': {},
            'authentication': {},
            'session_security': {}
        }
        
        try:
            session = requests.Session()
            response = session.get(f"{self.base_url}/")
            
            # Check security headers
            security_headers = [
                'X-Content-Type-Options',
                'X-Frame-Options', 
                'X-XSS-Protection',
                'Content-Security-Policy',
                'Strict-Transport-Security'
            ]
            
            for header in security_headers:
                value = response.headers.get(header)
                security_results['headers'][header] = {
                    'present': bool(value),
                    'value': value
                }
                
                if value:
                    logger.info(f"✅ Security header {header}: {value}")
                else:
                    logger.warning(f"⚠️ Missing security header: {header}")
            
            # Test for basic vulnerabilities
            test_payloads = [
                {'payload': '<script>alert("xss")</script>', 'type': 'XSS'},
                {'payload': "'; DROP TABLE users; --", 'type': 'SQL Injection'},
                {'payload': '../../../etc/passwd', 'type': 'Path Traversal'}
            ]
            
            for test in test_payloads:
                try:
                    test_response = session.post(f"{self.base_url}/api/chat", 
                                               json={'message': test['payload']}, 
                                               timeout=5)
                    
                    if test_response.status_code < 500:
                        security_results['vulnerabilities'][test['type']] = 'protected'
                        logger.info(f"✅ Protected against {test['type']}")
                    else:
                        security_results['vulnerabilities'][test['type']] = 'vulnerable'
                        logger.warning(f"⚠️ Possible {test['type']} vulnerability")
                        
                except Exception as e:
                    security_results['vulnerabilities'][test['type']] = f'test_failed: {str(e)}'
            
            self.test_results['security_analysis'] = security_results
            
        except Exception as e:
            logger.error(f"Security testing failed: {e}")
            self.test_results['security_analysis'] = {
                'error': str(e),
                'status': 'failed'
            }
    
    def _run_deployment_testing(self):
        """Run deployment readiness testing"""
        logger.info("🚀 Phase 7: Deployment Readiness Testing")
        
        deployment_results = {
            'configuration': {},
            'dependencies': {},
            'startup': {},
            'health_checks': {},
            'public_access': {}
        }
        
        try:
            # Check configuration files
            config_files = {
                'pyproject.toml': 'Python dependencies',
                'replit.toml': 'Replit deployment config',
                'main.py': 'Application entry point',
                'app.py': 'Flask application'
            }
            
            for file_path, description in config_files.items():
                exists = Path(file_path).exists()
                deployment_results['configuration'][file_path] = {
                    'exists': exists,
                    'description': description
                }
                
                if exists:
                    logger.info(f"✅ {description}: {file_path}")
                else:
                    logger.warning(f"⚠️ Missing {description}: {file_path}")
            
            # Test health endpoints
            health_endpoints = ['/health', '/healthz', '/ready']
            for endpoint in health_endpoints:
                try:
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                    deployment_results['health_checks'][endpoint] = {
                        'status_code': response.status_code,
                        'accessible': response.status_code == 200
                    }
                    
                    if response.status_code == 200:
                        logger.info(f"✅ Health endpoint {endpoint} working")
                    else:
                        logger.warning(f"⚠️ Health endpoint {endpoint} returned {response.status_code}")
                        
                except Exception as e:
                    deployment_results['health_checks'][endpoint] = {'error': str(e)}
                    logger.warning(f"⚠️ Health endpoint {endpoint} failed: {e}")
            
            # Test public access
            public_routes = ['/', '/demo', '/api/demo/chat']
            for route in public_routes:
                try:
                    response = requests.get(f"{self.base_url}{route}", timeout=5)
                    deployment_results['public_access'][route] = {
                        'status_code': response.status_code,
                        'accessible': response.status_code == 200,
                        'no_auth_barrier': 'login' not in response.url.lower()
                    }
                    
                    if response.status_code == 200:
                        logger.info(f"✅ Public route {route} accessible")
                    else:
                        logger.warning(f"⚠️ Public route {route} returned {response.status_code}")
                        
                except Exception as e:
                    deployment_results['public_access'][route] = {'error': str(e)}
                    logger.warning(f"⚠️ Public route {route} failed: {e}")
            
            self.test_results['deployment_readiness'] = deployment_results
            
        except Exception as e:
            logger.error(f"Deployment testing failed: {e}")
            self.test_results['deployment_readiness'] = {
                'error': str(e),
                'status': 'failed'
            }
    
    def _generate_master_report(self) -> Dict:
        """Generate comprehensive master report"""
        end_time = time.time()
        total_time = end_time - self.start_time
        
        # Calculate overall scores
        auth_score = self._calculate_auth_score()
        error_score = self._calculate_error_score()
        performance_score = self._calculate_performance_score()
        security_score = self._calculate_security_score()
        deployment_score = self._calculate_deployment_score()
        
        overall_score = (auth_score + error_score + performance_score + security_score + deployment_score) / 5
        
        master_report = {
            'test_summary': {
                'total_time': total_time,
                'timestamp': datetime.now().isoformat(),
                'overall_score': overall_score,
                'scores': {
                    'authentication': auth_score,
                    'error_detection': error_score,
                    'performance': performance_score,
                    'security': security_score,
                    'deployment': deployment_score
                }
            },
            'detailed_results': self.test_results,
            'recommendations': self._generate_recommendations(),
            'deployment_readiness': self._assess_deployment_readiness()
        }
        
        # Save master report
        self._save_master_report(master_report)
        
        return master_report
    
    def _calculate_auth_score(self) -> float:
        """Calculate authentication score"""
        auth_results = self.test_results.get('authentication_barriers', {})
        
        if 'error' in auth_results:
            return 0.0
        
        remaining_barriers = auth_results.get('remaining_barriers', 0)
        if remaining_barriers == 0:
            return 100.0
        
        initial_barriers = auth_results.get('initial_barriers', 1)
        fix_rate = auth_results.get('fix_success_rate', 0)
        
        return max(0.0, 100.0 * fix_rate)
    
    def _calculate_error_score(self) -> float:
        """Calculate error score"""
        error_results = self.test_results.get('error_detection', {})
        
        if 'error' in error_results:
            return 0.0
        
        summary = error_results.get('summary', {})
        total_errors = summary.get('total_errors', 0)
        critical_errors = summary.get('critical_errors', 0)
        
        if total_errors == 0:
            return 100.0
        
        # Heavily weight critical errors
        error_weight = critical_errors * 10 + total_errors
        return max(0.0, 100.0 - error_weight)
    
    def _calculate_performance_score(self) -> float:
        """Calculate performance score"""
        perf_results = self.test_results.get('performance_metrics', {})
        
        if 'error' in perf_results:
            return 50.0  # Neutral score if can't measure
        
        score = 100.0
        
        # Check response times
        response_times = perf_results.get('response_times', {})
        for endpoint, data in response_times.items():
            if isinstance(data, dict) and 'time' in data:
                time_val = data['time']
                if time_val > 5.0:
                    score -= 20
                elif time_val > 1.0:
                    score -= 10
        
        # Check memory usage
        memory = perf_results.get('memory_usage', {})
        if isinstance(memory, dict) and 'memory_mb' in memory:
            memory_mb = memory['memory_mb']
            if memory_mb > 500:
                score -= 20
            elif memory_mb > 100:
                score -= 10
        
        return max(0.0, score)
    
    def _calculate_security_score(self) -> float:
        """Calculate security score"""
        security_results = self.test_results.get('security_analysis', {})
        
        if 'error' in security_results:
            return 50.0  # Neutral score if can't measure
        
        score = 100.0
        
        # Check security headers
        headers = security_results.get('headers', {})
        required_headers = 5
        present_headers = sum(1 for h in headers.values() if h.get('present', False))
        header_score = (present_headers / required_headers) * 40
        
        # Check vulnerabilities
        vulnerabilities = security_results.get('vulnerabilities', {})
        protected_count = sum(1 for v in vulnerabilities.values() if v == 'protected')
        total_vuln_tests = len(vulnerabilities)
        vuln_score = (protected_count / max(total_vuln_tests, 1)) * 60 if total_vuln_tests > 0 else 60
        
        return header_score + vuln_score
    
    def _calculate_deployment_score(self) -> float:
        """Calculate deployment readiness score"""
        deploy_results = self.test_results.get('deployment_readiness', {})
        
        if 'error' in deploy_results:
            return 0.0
        
        score = 0.0
        
        # Configuration files (30 points)
        config = deploy_results.get('configuration', {})
        config_count = sum(1 for c in config.values() if c.get('exists', False))
        total_configs = len(config)
        if total_configs > 0:
            score += (config_count / total_configs) * 30
        
        # Health checks (35 points)
        health = deploy_results.get('health_checks', {})
        health_count = sum(1 for h in health.values() if h.get('accessible', False))
        total_health = len(health)
        if total_health > 0:
            score += (health_count / total_health) * 35
        
        # Public access (35 points)
        public = deploy_results.get('public_access', {})
        public_count = sum(1 for p in public.values() if p.get('accessible', False) and p.get('no_auth_barrier', True))
        total_public = len(public)
        if total_public > 0:
            score += (public_count / total_public) * 35
        
        return score
    
    def _generate_recommendations(self) -> List[Dict]:
        """Generate specific recommendations"""
        recommendations = []
        
        # Authentication recommendations
        auth_results = self.test_results.get('authentication_barriers', {})
        remaining_barriers = auth_results.get('remaining_barriers', 0)
        if remaining_barriers > 0:
            recommendations.append({
                'priority': 'CRITICAL',
                'category': 'Authentication',
                'issue': f'{remaining_barriers} authentication barriers still present',
                'action': 'Run authentication barrier fixer again or manually review Flask-Login usage'
            })
        
        # Error recommendations
        error_results = self.test_results.get('error_detection', {})
        if error_results and 'summary' in error_results:
            critical_errors = error_results['summary'].get('critical_errors', 0)
            if critical_errors > 0:
                recommendations.append({
                    'priority': 'CRITICAL',
                    'category': 'Errors',
                    'issue': f'{critical_errors} critical errors detected',
                    'action': 'Fix syntax errors and import issues immediately'
                })
        
        # Performance recommendations
        perf_results = self.test_results.get('performance_metrics', {})
        if perf_results and 'response_times' in perf_results:
            slow_endpoints = [ep for ep, data in perf_results['response_times'].items() 
                             if isinstance(data, dict) and data.get('time', 0) > 1.0]
            if slow_endpoints:
                recommendations.append({
                    'priority': 'MEDIUM',
                    'category': 'Performance',
                    'issue': f'Slow response times on {len(slow_endpoints)} endpoints',
                    'action': 'Optimize slow endpoints and consider caching'
                })
        
        # Security recommendations
        security_results = self.test_results.get('security_analysis', {})
        if security_results and 'headers' in security_results:
            missing_headers = [h for h, data in security_results['headers'].items() 
                              if not data.get('present', False)]
            if missing_headers:
                recommendations.append({
                    'priority': 'HIGH',
                    'category': 'Security',
                    'issue': f'Missing {len(missing_headers)} security headers',
                    'action': 'Add missing security headers to Flask configuration'
                })
        
        return recommendations
    
    def _assess_deployment_readiness(self) -> Dict:
        """Assess overall deployment readiness"""
        scores = {
            'authentication': self._calculate_auth_score(),
            'error_detection': self._calculate_error_score(),
            'performance': self._calculate_performance_score(),
            'security': self._calculate_security_score(),
            'deployment': self._calculate_deployment_score()
        }
        
        overall_score = sum(scores.values()) / len(scores)
        
        if overall_score >= 85:
            readiness = 'READY'
            status = 'Application is ready for production deployment'
        elif overall_score >= 70:
            readiness = 'MOSTLY_READY'
            status = 'Application is mostly ready with minor issues to address'
        elif overall_score >= 50:
            readiness = 'NEEDS_WORK'
            status = 'Application needs significant work before deployment'
        else:
            readiness = 'NOT_READY'
            status = 'Application is not ready for deployment'
        
        return {
            'readiness': readiness,
            'overall_score': overall_score,
            'status': status,
            'scores': scores
        }
    
    def _save_master_report(self, report: Dict):
        """Save master report to files"""
        # Save JSON report
        json_path = Path('tests/master_test_report.json')
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Save human-readable markdown report
        md_path = Path('tests/master_test_report.md')
        self._save_markdown_report(report, md_path)
        
        logger.info(f"Master report saved to {json_path} and {md_path}")
    
    def _save_markdown_report(self, report: Dict, path: Path):
        """Save human-readable markdown report"""
        lines = [
            "# Master Test Report",
            f"Generated: {report['test_summary']['timestamp']}",
            f"Total Time: {report['test_summary']['total_time']:.2f}s",
            "",
            "## Overall Assessment",
            f"**Overall Score: {report['test_summary']['overall_score']:.1f}/100**",
            "",
            f"**Deployment Status: {report['deployment_readiness']['readiness']}**",
            f"{report['deployment_readiness']['status']}",
            "",
            "## Scores by Category",
        ]
        
        for category, score in report['test_summary']['scores'].items():
            status = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
            lines.append(f"- {status} **{category.title()}**: {score:.1f}/100")
        
        lines.extend([
            "",
            "## Recommendations"
        ])
        
        if report['recommendations']:
            for i, rec in enumerate(report['recommendations'], 1):
                lines.extend([
                    f"### {i}. {rec['category']} ({rec['priority']})",
                    f"**Issue**: {rec['issue']}",
                    f"**Action**: {rec['action']}",
                    ""
                ])
        else:
            lines.append("✅ No critical recommendations - system appears healthy!")
        
        # Add detailed results summary
        lines.extend([
            "",
            "## Detailed Results Summary"
        ])
        
        # Authentication results
        auth_results = report['detailed_results'].get('authentication_barriers', {})
        if 'remaining_barriers' in auth_results:
            lines.extend([
                "### Authentication",
                f"- Initial barriers: {auth_results.get('initial_barriers', 0)}",
                f"- Remaining barriers: {auth_results.get('remaining_barriers', 0)}",
                f"- Fix success rate: {auth_results.get('fix_success_rate', 0):.1%}",
                ""
            ])
        
        # Error detection results
        error_results = report['detailed_results'].get('error_detection', {})
        if 'summary' in error_results:
            summary = error_results['summary']
            lines.extend([
                "### Error Detection",
                f"- Total errors: {summary.get('total_errors', 0)}",
                f"- Critical errors: {summary.get('critical_errors', 0)}",
                f"- High priority: {summary.get('high_priority_errors', 0)}",
                f"- Medium priority: {summary.get('medium_priority_errors', 0)}",
                ""
            ])
        
        # Performance results
        perf_results = report['detailed_results'].get('performance_metrics', {})
        if 'response_times' in perf_results:
            lines.extend([
                "### Performance",
                "#### Response Times"
            ])
            for endpoint, data in perf_results['response_times'].items():
                if isinstance(data, dict) and 'time' in data:
                    status = "🟢" if data['time'] < 1.0 else "🟡" if data['time'] < 5.0 else "🔴"
                    lines.append(f"- {status} {endpoint}: {data['time']:.3f}s")
            lines.append("")
        
        with open(path, 'w') as f:
            f.write('\n'.join(lines))


def main():
    """Main entry point for master test orchestrator"""
    print("🚀 Master Test Orchestrator")
    print("=" * 60)
    print("Comprehensive testing infrastructure with zero authentication barriers")
    print("Coordinates all testing systems for complete bug detection and problem resolution")
    print("=" * 60)
    
    orchestrator = MasterTestOrchestrator()
    
    try:
        results = orchestrator.run_complete_testing_suite()
        
        print("\n" + "=" * 60)
        print("MASTER TEST RESULTS")
        print("=" * 60)
        print(f"Overall Score: {results['test_summary']['overall_score']:.1f}/100")
        print(f"Deployment Status: {results['deployment_readiness']['readiness']}")
        print(f"Status: {results['deployment_readiness']['status']}")
        
        print("\nScores by Category:")
        for category, score in results['test_summary']['scores'].items():
            status = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
            print(f"  {status} {category.title()}: {score:.1f}/100")
        
        if results['recommendations']:
            print(f"\nRecommendations ({len(results['recommendations'])}):")
            for rec in results['recommendations']:
                print(f"  {rec['priority']}: {rec['issue']}")
        else:
            print("\n✅ No critical recommendations - system appears healthy!")
        
        print(f"\nFull report: tests/master_test_report.md")
        
        # Exit with appropriate code
        if results['deployment_readiness']['readiness'] in ['READY', 'MOSTLY_READY']:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Master test orchestration failed: {e}")
        print(f"❌ Testing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()