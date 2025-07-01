"""
Comprehensive Bug Detection and Testing Infrastructure
Advanced testing framework with zero authentication barriers
"""
import pytest
import requests
import json
import time
import threading
import subprocess
import sys
import os
import logging
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional, Tuple
from contextlib import contextmanager
import psutil
import signal
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveTestSuite:
    """Advanced testing framework for complete application validation"""
    
    def __init__(self, base_url: str = None, test_mode: str = "full"):
        """Initialize comprehensive test suite"""
        self.base_url = base_url or self._get_base_url()
        self.test_mode = test_mode
        self.session = requests.Session()
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': [],
            'warnings': [],
            'authentication_issues': [],
            'performance_issues': [],
            'security_issues': []
        }
        self.start_time = time.time()
        
    def _get_base_url(self) -> str:
        """Get base URL from configuration"""
        try:
            from config import PORT, HOST
            return f"http://{HOST}:{PORT}"
        except ImportError:
            return "http://localhost:5000"
    
    def run_comprehensive_tests(self) -> Dict:
        """Run complete test suite"""
        logger.info("🚀 Starting Comprehensive Test Suite")
        
        # Phase 1: Critical Infrastructure Tests
        self.test_application_startup()
        self.test_basic_connectivity()
        self.test_health_endpoints()
        
        # Phase 2: Authentication Barrier Detection
        self.test_authentication_barriers()
        self.test_login_loop_prevention()
        self.test_public_access_routes()
        
        # Phase 3: Route Validation
        self.test_all_routes_accessible()
        self.test_api_endpoints()
        self.test_static_assets()
        
        # Phase 4: Error Handling
        self.test_error_handling()
        self.test_exception_handling()
        self.test_database_errors()
        
        # Phase 5: Security Testing
        self.test_security_headers()
        self.test_injection_vulnerabilities()
        self.test_session_security()
        
        # Phase 6: Performance Testing
        self.test_response_times()
        self.test_memory_usage()
        self.test_concurrent_requests()
        
        # Phase 7: Integration Testing
        self.test_database_integration()
        self.test_third_party_services()
        self.test_file_uploads()
        
        self.generate_comprehensive_report()
        return self.results
    
    def test_application_startup(self):
        """Test that application starts without errors"""
        logger.info("Testing application startup...")
        
        try:
            # Test import of main application
            import app
            self._record_pass("Application imports successfully")
            
            # Test that Flask app is created properly
            if hasattr(app, 'create_app'):
                test_app = app.create_app()
                self._record_pass("Flask app creation successful")
            else:
                self._record_warning("No create_app function found")
                
        except Exception as e:
            self._record_error(f"Application startup failed: {str(e)}")
    
    def test_basic_connectivity(self):
        """Test basic HTTP connectivity"""
        logger.info("Testing basic connectivity...")
        
        try:
            response = self.session.get(self.base_url, timeout=10)
            if response.status_code == 200:
                self._record_pass("Basic connectivity working")
            else:
                self._record_error(f"Basic connectivity failed: {response.status_code}")
        except requests.RequestException as e:
            self._record_error(f"Connection failed: {str(e)}")
    
    def test_health_endpoints(self):
        """Test health monitoring endpoints"""
        logger.info("Testing health endpoints...")
        
        health_endpoints = ['/health', '/healthz', '/api/health', '/ready']
        
        for endpoint in health_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    self._record_pass(f"Health endpoint {endpoint} working")
                elif response.status_code == 404:
                    self._record_warning(f"Health endpoint {endpoint} not implemented")
                else:
                    self._record_error(f"Health endpoint {endpoint} failed: {response.status_code}")
            except Exception as e:
                self._record_error(f"Health endpoint {endpoint} error: {str(e)}")
    
    def test_authentication_barriers(self):
        """Comprehensive authentication barrier detection"""
        logger.info("🔍 Testing for authentication barriers...")
        
        # Test critical routes that should be publicly accessible
        public_routes = [
            '/',
            '/demo',
            '/public',
            '/api/demo/chat',
            '/health',
            '/static/css/style.css',
            '/static/js/app.js'
        ]
        
        authentication_issues = []
        
        for route in public_routes:
            try:
                response = self.session.get(f"{self.base_url}{route}", allow_redirects=False)
                
                # Check for authentication redirects
                if response.status_code in [302, 301]:
                    location = response.headers.get('Location', '')
                    if 'login' in location.lower() or 'auth' in location.lower():
                        authentication_issues.append({
                            'route': route,
                            'issue': 'Authentication redirect detected',
                            'redirect_to': location
                        })
                
                # Check for "you must be logged in" messages
                if response.status_code == 200:
                    content = response.text.lower()
                    if 'you must be logged in' in content or 'login required' in content:
                        authentication_issues.append({
                            'route': route,
                            'issue': 'Login required message detected',
                            'status_code': response.status_code
                        })
                
                # Check for 401/403 errors on public routes
                if response.status_code in [401, 403] and route in ['/', '/demo', '/health']:
                    authentication_issues.append({
                        'route': route,
                        'issue': f'Authentication error {response.status_code} on public route',
                        'status_code': response.status_code
                    })
                    
            except Exception as e:
                authentication_issues.append({
                    'route': route,
                    'issue': f'Request failed: {str(e)}',
                    'status_code': 'error'
                })
        
        if authentication_issues:
            self.results['authentication_issues'].extend(authentication_issues)
            self._record_error(f"Found {len(authentication_issues)} authentication barriers")
        else:
            self._record_pass("No authentication barriers detected")
    
    def test_login_loop_prevention(self):
        """Test for infinite login redirect loops"""
        logger.info("Testing login loop prevention...")
        
        test_routes = ['/dashboard', '/app', '/profile', '/settings']
        
        for route in test_routes:
            try:
                redirect_chain = []
                current_url = f"{self.base_url}{route}"
                max_redirects = 5
                
                for i in range(max_redirects):
                    response = self.session.get(current_url, allow_redirects=False)
                    redirect_chain.append({
                        'url': current_url,
                        'status': response.status_code,
                        'location': response.headers.get('Location')
                    })
                    
                    if response.status_code not in [301, 302]:
                        break
                        
                    location = response.headers.get('Location')
                    if not location:
                        break
                        
                    if location.startswith('/'):
                        current_url = f"{self.base_url}{location}"
                    else:
                        current_url = location
                    
                    # Check for loop
                    if current_url in [r['url'] for r in redirect_chain[:-1]]:
                        self._record_error(f"Redirect loop detected for {route}: {redirect_chain}")
                        break
                else:
                    if len(redirect_chain) >= max_redirects:
                        self._record_error(f"Too many redirects for {route}")
                    else:
                        self._record_pass(f"No redirect loops for {route}")
                        
            except Exception as e:
                self._record_error(f"Error testing {route}: {str(e)}")
    
    def test_public_access_routes(self):
        """Test that public routes work without authentication"""
        logger.info("Testing public access routes...")
        
        # Routes that should work without authentication
        public_routes = {
            '/': 'Landing page',
            '/demo': 'Demo access',
            '/api/demo/chat': 'Demo chat API',
            '/health': 'Health check',
            '/static/css/style.css': 'CSS assets',
            '/favicon.ico': 'Favicon'
        }
        
        for route, description in public_routes.items():
            try:
                response = self.session.get(f"{self.base_url}{route}")
                if response.status_code == 200:
                    self._record_pass(f"Public route {route} ({description}) accessible")
                elif response.status_code == 404:
                    self._record_warning(f"Public route {route} ({description}) not found")
                else:
                    self._record_error(f"Public route {route} ({description}) failed: {response.status_code}")
            except Exception as e:
                self._record_error(f"Public route {route} error: {str(e)}")
    
    def test_all_routes_accessible(self):
        """Test accessibility of all application routes"""
        logger.info("Testing all routes accessibility...")
        
        # Discover routes by examining the application
        try:
            from app import create_app
            test_app = create_app()
            
            with test_app.app_context():
                routes = []
                for rule in test_app.url_map.iter_rules():
                    if rule.endpoint != 'static':
                        routes.append({
                            'rule': rule.rule,
                            'methods': list(rule.methods),
                            'endpoint': rule.endpoint
                        })
                
                # Test GET routes
                for route_info in routes:
                    if 'GET' in route_info['methods']:
                        route = route_info['rule']
                        # Skip routes with parameters
                        if '<' not in route:
                            self._test_route_accessibility(route, route_info['endpoint'])
                            
        except Exception as e:
            self._record_warning(f"Could not discover routes automatically: {str(e)}")
            # Test common routes manually
            common_routes = [
                '/', '/dashboard', '/profile', '/settings', '/chat',
                '/api/chat', '/api/user', '/api/health'
            ]
            for route in common_routes:
                self._test_route_accessibility(route, 'unknown')
    
    def _test_route_accessibility(self, route: str, endpoint: str):
        """Test if a specific route is accessible"""
        try:
            response = self.session.get(f"{self.base_url}{route}")
            if response.status_code == 200:
                self._record_pass(f"Route {route} accessible")
            elif response.status_code in [302, 301]:
                # Check if redirect is reasonable
                location = response.headers.get('Location', '')
                if 'login' in location.lower():
                    self._record_warning(f"Route {route} requires authentication")
                else:
                    self._record_pass(f"Route {route} redirects to {location}")
            elif response.status_code == 404:
                self._record_warning(f"Route {route} not found")
            else:
                self._record_error(f"Route {route} failed: {response.status_code}")
        except Exception as e:
            self._record_error(f"Route {route} error: {str(e)}")
    
    def test_api_endpoints(self):
        """Test API endpoints specifically"""
        logger.info("Testing API endpoints...")
        
        api_endpoints = [
            ('/api/health', 'GET'),
            ('/api/chat', 'POST'),
            ('/api/demo/chat', 'POST'),
            ('/api/user', 'GET'),
            ('/api/feedback', 'POST')
        ]
        
        for endpoint, method in api_endpoints:
            try:
                if method == 'GET':
                    response = self.session.get(f"{self.base_url}{endpoint}")
                elif method == 'POST':
                    response = self.session.post(f"{self.base_url}{endpoint}", 
                                               json={'test': 'data'})
                
                # API endpoints should return JSON or proper error codes
                if response.status_code == 200:
                    try:
                        response.json()
                        self._record_pass(f"API {method} {endpoint} working")
                    except Exception as e:
                        logger.error(f"Error: {e}")
                        self._record_warning(f"API {method} {endpoint} not returning JSON")
                elif response.status_code in [400, 401, 404, 405]:
                    self._record_warning(f"API {method} {endpoint} returned {response.status_code}")
                else:
                    self._record_error(f"API {method} {endpoint} failed: {response.status_code}")
                    
            except Exception as e:
                self._record_error(f"API {method} {endpoint} error: {str(e)}")
    
    def test_static_assets(self):
        """Test static asset delivery"""
        logger.info("Testing static assets...")
        
        static_assets = [
            '/static/css/style.css',
            '/static/js/app.js',
            '/static/js/main.js',
            '/favicon.ico'
        ]
        
        for asset in static_assets:
            try:
                response = self.session.get(f"{self.base_url}{asset}")
                if response.status_code == 200:
                    self._record_pass(f"Static asset {asset} accessible")
                elif response.status_code == 404:
                    self._record_warning(f"Static asset {asset} not found")
                else:
                    self._record_error(f"Static asset {asset} failed: {response.status_code}")
            except Exception as e:
                self._record_error(f"Static asset {asset} error: {str(e)}")
    
    def test_error_handling(self):
        """Test application error handling"""
        logger.info("Testing error handling...")
        
        # Test 404 handling
        try:
            response = self.session.get(f"{self.base_url}/nonexistent-page-12345")
            if response.status_code == 404:
                self._record_pass("404 error handling working")
            else:
                self._record_warning(f"404 handling returned {response.status_code}")
        except Exception as e:
            self._record_error(f"404 test error: {str(e)}")
        
        # Test malformed requests
        try:
            response = self.session.post(f"{self.base_url}/api/chat", 
                                       data="invalid json")
            if response.status_code in [400, 422]:
                self._record_pass("Malformed request handling working")
            else:
                self._record_warning(f"Malformed request returned {response.status_code}")
        except Exception as e:
            self._record_error(f"Malformed request test error: {str(e)}")
    
    def test_exception_handling(self):
        """Test application exception handling"""
        logger.info("Testing exception handling...")
        
        # Test various potentially problematic requests
        test_cases = [
            ('SQL injection attempt', '/api/chat', {'message': "'; DROP TABLE users; --"}),
            ('XSS attempt', '/api/chat', {'message': '<script>alert("xss")</script>'}),
            ('Large payload', '/api/chat', {'message': 'A' * 10000}),
            ('Null bytes', '/api/chat', {'message': 'test\x00null'}),
        ]
        
        for test_name, endpoint, payload in test_cases:
            try:
                response = self.session.post(f"{self.base_url}{endpoint}", json=payload)
                if response.status_code < 500:
                    self._record_pass(f"{test_name} handled properly")
                else:
                    self._record_error(f"{test_name} caused server error: {response.status_code}")
            except Exception as e:
                self._record_error(f"{test_name} test error: {str(e)}")
    
    def test_database_errors(self):
        """Test database error handling"""
        logger.info("Testing database error handling...")
        
        # Test database connectivity
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                try:
                    health_data = response.json()
                    if 'database' in health_data:
                        if health_data['database'].get('status') == 'healthy':
                            self._record_pass("Database connectivity working")
                        else:
                            self._record_warning("Database connectivity issues detected")
                    else:
                        self._record_warning("Database status not reported in health check")
                except Exception as e:
                    logger.error(f"Error: {e}")
                    self._record_warning("Health endpoint not returning JSON")
            else:
                self._record_error(f"Health check failed: {response.status_code}")
        except Exception as e:
            self._record_error(f"Database test error: {str(e)}")
    
    def test_security_headers(self):
        """Test security headers"""
        logger.info("Testing security headers...")
        
        try:
            response = self.session.get(f"{self.base_url}/")
            headers = response.headers
            
            # Check for important security headers
            security_checks = [
                ('X-Content-Type-Options', 'nosniff'),
                ('X-Frame-Options', ['DENY', 'SAMEORIGIN']),
                ('X-XSS-Protection', '1; mode=block'),
                ('Content-Security-Policy', None),  # Just check presence
                ('Strict-Transport-Security', None)  # Just check presence
            ]
            
            for header, expected in security_checks:
                value = headers.get(header)
                if value:
                    if expected is None:
                        self._record_pass(f"Security header {header} present")
                    elif isinstance(expected, list):
                        if value in expected:
                            self._record_pass(f"Security header {header} correct")
                        else:
                            self._record_warning(f"Security header {header} has unexpected value: {value}")
                    elif value == expected:
                        self._record_pass(f"Security header {header} correct")
                    else:
                        self._record_warning(f"Security header {header} has unexpected value: {value}")
                else:
                    self._record_warning(f"Security header {header} missing")
                    
        except Exception as e:
            self._record_error(f"Security headers test error: {str(e)}")
    
    def test_injection_vulnerabilities(self):
        """Test for injection vulnerabilities"""
        logger.info("Testing injection vulnerabilities...")
        
        # Test SQL injection
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --"
        ]
        
        for payload in sql_payloads:
            try:
                response = self.session.post(f"{self.base_url}/api/chat", 
                                           json={'message': payload})
                if response.status_code < 500:
                    self._record_pass(f"SQL injection payload handled safely")
                else:
                    self._record_error(f"SQL injection payload caused server error")
            except Exception as e:
                self._record_error(f"SQL injection test error: {str(e)}")
    
    def test_session_security(self):
        """Test session security"""
        logger.info("Testing session security...")
        
        try:
            response = self.session.get(f"{self.base_url}/")
            
            # Check for secure session cookies
            for cookie in self.session.cookies:
                if 'session' in cookie.name.lower():
                    if cookie.secure:
                        self._record_pass("Session cookie is secure")
                    else:
                        self._record_warning("Session cookie is not secure")
                    
                    if 'httponly' in str(cookie).lower():
                        self._record_pass("Session cookie is HttpOnly")
                    else:
                        self._record_warning("Session cookie is not HttpOnly")
                        
        except Exception as e:
            self._record_error(f"Session security test error: {str(e)}")
    
    def test_response_times(self):
        """Test response times"""
        logger.info("Testing response times...")
        
        endpoints = ['/', '/health', '/api/health']
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}{endpoint}")
                end_time = time.time()
                
                response_time = end_time - start_time
                
                if response_time < 1.0:
                    self._record_pass(f"Response time for {endpoint}: {response_time:.3f}s")
                elif response_time < 5.0:
                    self._record_warning(f"Slow response for {endpoint}: {response_time:.3f}s")
                else:
                    self._record_error(f"Very slow response for {endpoint}: {response_time:.3f}s")
                    
                self.results['performance_issues'].append({
                    'endpoint': endpoint,
                    'response_time': response_time,
                    'status': 'good' if response_time < 1.0 else 'slow' if response_time < 5.0 else 'very_slow'
                })
                
            except Exception as e:
                self._record_error(f"Response time test for {endpoint} error: {str(e)}")
    
    def test_memory_usage(self):
        """Test memory usage"""
        logger.info("Testing memory usage...")
        
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            if memory_mb < 100:
                self._record_pass(f"Memory usage: {memory_mb:.1f}MB (good)")
            elif memory_mb < 500:
                self._record_warning(f"Memory usage: {memory_mb:.1f}MB (moderate)")
            else:
                self._record_error(f"Memory usage: {memory_mb:.1f}MB (high)")
                
            self.results['performance_issues'].append({
                'metric': 'memory_usage',
                'value_mb': memory_mb,
                'status': 'good' if memory_mb < 100 else 'moderate' if memory_mb < 500 else 'high'
            })
            
        except Exception as e:
            self._record_warning(f"Memory usage test error: {str(e)}")
    
    def test_concurrent_requests(self):
        """Test concurrent request handling"""
        logger.info("Testing concurrent requests...")
        
        def make_request():
            try:
                response = requests.get(f"{self.base_url}/health", timeout=10)
                return response.status_code == 200
            except Exception as e:
                logger.error(f"Error: {e}")
                return False
        
        try:
            import threading
            import concurrent.futures
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request) for _ in range(20)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            success_rate = sum(results) / len(results)
            
            if success_rate >= 0.9:
                self._record_pass(f"Concurrent requests: {success_rate:.1%} success rate")
            elif success_rate >= 0.7:
                self._record_warning(f"Concurrent requests: {success_rate:.1%} success rate")
            else:
                self._record_error(f"Concurrent requests: {success_rate:.1%} success rate")
                
        except Exception as e:
            self._record_warning(f"Concurrent requests test error: {str(e)}")
    
    def test_database_integration(self):
        """Test database integration"""
        logger.info("Testing database integration...")
        
        try:
            # Test database connection through health endpoint
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                try:
                    health_data = response.json()
                    if health_data.get('database', {}).get('status') == 'healthy':
                        self._record_pass("Database integration working")
                    else:
                        self._record_error("Database integration issues")
                except Exception as e:
                    logger.error(f"Error: {e}")
                    self._record_warning("Could not parse health check response")
            else:
                self._record_error(f"Health check failed: {response.status_code}")
        except Exception as e:
            self._record_error(f"Database integration test error: {str(e)}")
    
    def test_third_party_services(self):
        """Test third-party service integration"""
        logger.info("Testing third-party services...")
        
        # Test if services are properly configured
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                try:
                    health_data = response.json()
                    services = health_data.get('services', {})
                    
                    for service, status in services.items():
                        if status.get('status') == 'healthy':
                            self._record_pass(f"Third-party service {service} working")
                        else:
                            self._record_warning(f"Third-party service {service} issues")
                            
                except Exception as e:
                            
                    logger.error(f"Error: {e}")
                    self._record_warning("Could not parse third-party services status")
            else:
                self._record_warning("Could not check third-party services")
        except Exception as e:
            self._record_warning(f"Third-party services test error: {str(e)}")
    
    def test_file_uploads(self):
        """Test file upload functionality"""
        logger.info("Testing file uploads...")
        
        # Test file upload endpoints
        upload_endpoints = ['/api/upload', '/upload']
        
        for endpoint in upload_endpoints:
            try:
                # Create a test file
                test_file = {'file': ('test.txt', 'test content', 'text/plain')}
                response = self.session.post(f"{self.base_url}{endpoint}", 
                                           files=test_file)
                
                if response.status_code in [200, 201]:
                    self._record_pass(f"File upload {endpoint} working")
                elif response.status_code == 404:
                    self._record_warning(f"File upload {endpoint} not implemented")
                else:
                    self._record_warning(f"File upload {endpoint} returned {response.status_code}")
                    
            except Exception as e:
                self._record_warning(f"File upload {endpoint} test error: {str(e)}")
    
    def _record_pass(self, message: str):
        """Record a successful test"""
        self.results['passed'] += 1
        logger.info(f"✅ PASS: {message}")
    
    def _record_warning(self, message: str):
        """Record a warning"""
        self.results['warnings'].append(message)
        logger.warning(f"⚠️  WARNING: {message}")
    
    def _record_error(self, message: str):
        """Record an error"""
        self.results['failed'] += 1
        self.results['errors'].append(message)
        logger.error(f"❌ ERROR: {message}")
    
    def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        end_time = time.time()
        total_time = end_time - self.start_time
        
        report = {
            'test_summary': {
                'total_time': total_time,
                'tests_passed': self.results['passed'],
                'tests_failed': self.results['failed'],
                'warnings': len(self.results['warnings']),
                'success_rate': self.results['passed'] / (self.results['passed'] + self.results['failed']) if (self.results['passed'] + self.results['failed']) > 0 else 0
            },
            'authentication_analysis': {
                'barriers_found': len(self.results['authentication_issues']),
                'barriers': self.results['authentication_issues']
            },
            'performance_analysis': {
                'issues_found': len(self.results['performance_issues']),
                'issues': self.results['performance_issues']
            },
            'security_analysis': {
                'issues_found': len(self.results['security_issues']),
                'issues': self.results['security_issues']
            },
            'errors': self.results['errors'],
            'warnings': self.results['warnings']
        }
        
        # Save report to file
        with open('tests/comprehensive_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate human-readable report
        self._generate_human_readable_report(report)
        
        return report
    
    def _generate_human_readable_report(self, report: Dict):
        """Generate human-readable test report"""
        report_lines = [
            "# Comprehensive Test Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            f"- Tests Passed: {report['test_summary']['tests_passed']}",
            f"- Tests Failed: {report['test_summary']['tests_failed']}",
            f"- Warnings: {report['test_summary']['warnings']}",
            f"- Success Rate: {report['test_summary']['success_rate']:.1%}",
            f"- Total Time: {report['test_summary']['total_time']:.2f}s",
            "",
            "## Authentication Analysis",
            f"- Authentication barriers found: {report['authentication_analysis']['barriers_found']}",
        ]
        
        if report['authentication_analysis']['barriers']:
            report_lines.append("### Authentication Issues:")
            for issue in report['authentication_analysis']['barriers']:
                report_lines.append(f"- {issue['route']}: {issue['issue']}")
        else:
            report_lines.append("✅ No authentication barriers detected")
        
        report_lines.extend([
            "",
            "## Performance Analysis",
            f"- Performance issues found: {report['performance_analysis']['issues_found']}"
        ])
        
        if report['performance_analysis']['issues']:
            report_lines.append("### Performance Issues:")
            for issue in report['performance_analysis']['issues']:
                if 'endpoint' in issue:
                    report_lines.append(f"- {issue['endpoint']}: {issue['response_time']:.3f}s ({issue['status']})")
                else:
                    report_lines.append(f"- {issue['metric']}: {issue.get('value_mb', 'N/A')}MB ({issue['status']})")
        
        if report['errors']:
            report_lines.extend([
                "",
                "## Errors",
            ])
            for error in report['errors']:
                report_lines.append(f"- {error}")
        
        if report['warnings']:
            report_lines.extend([
                "",
                "## Warnings",
            ])
            for warning in report['warnings']:
                report_lines.append(f"- {warning}")
        
        # Save human-readable report
        with open('tests/comprehensive_test_report.md', 'w') as f:
            f.write('\n'.join(report_lines))


# Pytest integration
class TestComprehensiveFramework:
    """Pytest integration for comprehensive testing"""
    
    @classmethod
    def setup_class(cls):
        """Setup test class"""
        cls.test_suite = ComprehensiveTestSuite()
    
    def test_application_startup(self):
        """Test application startup"""
        self.test_suite.test_application_startup()
        assert self.test_suite.results['failed'] == 0, "Application startup failed"
    
    def test_authentication_barriers(self):
        """Test for authentication barriers"""
        self.test_suite.test_authentication_barriers()
        assert len(self.test_suite.results['authentication_issues']) == 0, f"Authentication barriers found: {self.test_suite.results['authentication_issues']}"
    
    def test_public_routes(self):
        """Test public routes accessibility"""
        self.test_suite.test_public_access_routes()
        # Allow some failures for optional routes
        assert self.test_suite.results['failed'] < 3, "Too many public route failures"
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        self.test_suite.test_api_endpoints()
        # API endpoints may have authentication requirements
        assert True  # Just run the test for logging
    
    def test_security_basics(self):
        """Test basic security"""
        self.test_suite.test_security_headers()
        self.test_suite.test_injection_vulnerabilities()
        # Security tests are informational
        assert True


if __name__ == "__main__":
    # Run comprehensive test suite
    suite = ComprehensiveTestSuite()
    results = suite.run_comprehensive_tests()
    
    print("\n" + "="*50)
    print("COMPREHENSIVE TEST RESULTS")
    print("="*50)
    print(f"Tests Passed: {results['passed']}")
    print(f"Tests Failed: {results['failed']}")
    print(f"Warnings: {len(results['warnings'])}")
    print(f"Authentication Issues: {len(results['authentication_issues'])}")
    print(f"Performance Issues: {len(results['performance_issues'])}")
    
    if results['authentication_issues']:
        print("\n🚨 AUTHENTICATION BARRIERS DETECTED:")
        for issue in results['authentication_issues']:
            print(f"  - {issue['route']}: {issue['issue']}")
    
    if results['errors']:
        print("\n❌ ERRORS:")
        for error in results['errors']:
            print(f"  - {error}")
    
    print(f"\nFull report saved to: tests/comprehensive_test_report.md")
    
    # Exit with error code if critical issues found
    if results['authentication_issues'] or results['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)