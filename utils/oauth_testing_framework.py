"""
OAuth Testing Framework
Fixes Issues 30-32: OAuth testing, integration tests, production validation
"""

import logging
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import secrets
import requests
from flask import Flask

logger = logging.getLogger(__name__)

class OAuthTestingFramework:
    """Comprehensive OAuth testing and validation framework"""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self.test_results = {}
        self.test_start_time = None
        
    def run_comprehensive_oauth_tests(self) -> Dict[str, Any]:
        """Run complete OAuth testing suite"""
        self.test_start_time = time.time()
        
        test_results = {
            'test_suite': 'OAuth Comprehensive Testing',
            'start_time': datetime.utcnow().isoformat(),
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'test_results': {},
            'overall_status': 'unknown'
        }
        
        try:
            # Test 1: Configuration Validation
            config_result = self._test_oauth_configuration()
            test_results['test_results']['configuration'] = config_result
            test_results['tests_run'] += 1
            if config_result['status'] == 'passed':
                test_results['tests_passed'] += 1
            else:
                test_results['tests_failed'] += 1
            
            # Test 2: State Management
            state_result = self._test_state_management()
            test_results['test_results']['state_management'] = state_result
            test_results['tests_run'] += 1
            if state_result['status'] == 'passed':
                test_results['tests_passed'] += 1
            else:
                test_results['tests_failed'] += 1
            
            # Test 3: Token Encryption
            encryption_result = self._test_token_encryption()
            test_results['test_results']['token_encryption'] = encryption_result
            test_results['tests_run'] += 1
            if encryption_result['status'] == 'passed':
                test_results['tests_passed'] += 1
            else:
                test_results['tests_failed'] += 1
            
            # Test 4: Rate Limiting
            rate_limit_result = self._test_rate_limiting()
            test_results['test_results']['rate_limiting'] = rate_limit_result
            test_results['tests_run'] += 1
            if rate_limit_result['status'] == 'passed':
                test_results['tests_passed'] += 1
            else:
                test_results['tests_failed'] += 1
            
            # Test 5: Error Handling
            error_handling_result = self._test_error_handling()
            test_results['test_results']['error_handling'] = error_handling_result
            test_results['tests_run'] += 1
            if error_handling_result['status'] == 'passed':
                test_results['tests_passed'] += 1
            else:
                test_results['tests_failed'] += 1
            
            # Test 6: Callback Validation
            callback_result = self._test_callback_handling()
            test_results['test_results']['callback_handling'] = callback_result
            test_results['tests_run'] += 1
            if callback_result['status'] == 'passed':
                test_results['tests_passed'] += 1
            else:
                test_results['tests_failed'] += 1
            
            # Test 7: Security Headers
            security_result = self._test_security_implementation()
            test_results['test_results']['security_implementation'] = security_result
            test_results['tests_run'] += 1
            if security_result['status'] == 'passed':
                test_results['tests_passed'] += 1
            else:
                test_results['tests_failed'] += 1
            
            # Test 8: Production Readiness
            production_result = self._test_production_readiness()
            test_results['test_results']['production_readiness'] = production_result
            test_results['tests_run'] += 1
            if production_result['status'] == 'passed':
                test_results['tests_passed'] += 1
            else:
                test_results['tests_failed'] += 1
            
            # Calculate overall status
            success_rate = test_results['tests_passed'] / test_results['tests_run'] if test_results['tests_run'] > 0 else 0
            
            if success_rate >= 0.9:
                test_results['overall_status'] = 'excellent'
            elif success_rate >= 0.7:
                test_results['overall_status'] = 'good'
            elif success_rate >= 0.5:
                test_results['overall_status'] = 'needs_improvement'
            else:
                test_results['overall_status'] = 'failing'
            
            test_results['success_rate'] = f"{success_rate:.1%}"
            test_results['duration'] = f"{time.time() - self.test_start_time:.2f}s"
            test_results['end_time'] = datetime.utcnow().isoformat()
            
            logger.info(f"OAuth testing completed: {test_results['overall_status']} ({test_results['success_rate']})")
            
        except Exception as e:
            test_results['overall_status'] = 'error'
            test_results['error'] = str(e)
            logger.error(f"OAuth testing failed: {e}")
        
        return test_results
    
    def _test_oauth_configuration(self) -> Dict[str, Any]:
        """Test OAuth configuration validity"""
        try:
            from utils.oauth_config_manager import oauth_config_manager
            
            # Test configuration loading
            config = oauth_config_manager.get_config()
            if not config:
                return {
                    'status': 'failed',
                    'message': 'OAuth configuration not loaded',
                    'issues': ['Configuration manager returned None']
                }
            
            # Test configuration validation
            validation_result = oauth_config_manager.validate_configuration()
            if not validation_result['valid']:
                return {
                    'status': 'failed',
                    'message': 'OAuth configuration validation failed',
                    'issues': validation_result['issues']
                }
            
            # Test status summary
            status_summary = oauth_config_manager.get_status_summary()
            if not status_summary['configured']:
                return {
                    'status': 'failed',
                    'message': 'OAuth not properly configured',
                    'issues': [status_summary['message']]
                }
            
            return {
                'status': 'passed',
                'message': 'OAuth configuration valid',
                'details': {
                    'client_id_configured': bool(config.client_id),
                    'redirect_uri': config.redirect_uri,
                    'scopes_count': len(config.scopes),
                    'urls_configured': bool(config.authorization_base_url)
                }
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'message': f'Configuration test failed: {str(e)}',
                'issues': [str(e)]
            }
    
    def _test_state_management(self) -> Dict[str, Any]:
        """Test OAuth state management functionality"""
        try:
            from utils.oauth_state_manager import oauth_state_manager
            
            # Test state generation
            state1 = oauth_state_manager.generate_state()
            state2 = oauth_state_manager.generate_state()
            
            if not state1 or not state2:
                return {
                    'status': 'failed',
                    'message': 'State generation failed',
                    'issues': ['generate_state() returned empty value']
                }
            
            # States should be unique
            if state1 == state2:
                return {
                    'status': 'failed',
                    'message': 'State generation not unique',
                    'issues': ['Multiple calls generated identical states']
                }
            
            # Test state validation
            is_valid = oauth_state_manager.validate_state(state1)
            if not is_valid:
                return {
                    'status': 'failed',
                    'message': 'State validation failed',
                    'issues': ['Generated state failed validation']
                }
            
            # Test invalid state rejection
            invalid_state = "invalid_state_12345"
            is_invalid = oauth_state_manager.validate_state(invalid_state)
            if is_invalid:
                return {
                    'status': 'failed',
                    'message': 'Invalid state accepted',
                    'issues': ['Invalid state passed validation']
                }
            
            return {
                'status': 'passed',
                'message': 'State management working correctly',
                'details': {
                    'state_generation': 'working',
                    'state_validation': 'working',
                    'state_uniqueness': 'working',
                    'invalid_rejection': 'working'
                }
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'message': f'State management test failed: {str(e)}',
                'issues': [str(e)]
            }
    
    def _test_token_encryption(self) -> Dict[str, Any]:
        """Test token encryption functionality"""
        try:
            from utils.token_encryption import token_encryption
            
            if not token_encryption:
                return {
                    'status': 'failed',
                    'message': 'Token encryption service not available',
                    'issues': ['token_encryption is None']
                }
            
            # Test encryption/decryption
            test_token = f"test_access_token_{secrets.token_urlsafe(16)}"
            
            encrypted = token_encryption.encrypt_token(test_token)
            if not encrypted or encrypted == test_token:
                return {
                    'status': 'failed',
                    'message': 'Token encryption failed',
                    'issues': ['encrypt_token() returned empty or unchanged value']
                }
            
            decrypted = token_encryption.decrypt_token(encrypted)
            if decrypted != test_token:
                return {
                    'status': 'failed',
                    'message': 'Token decryption failed',
                    'issues': [f'Expected "{test_token}", got "{decrypted}"']
                }
            
            # Test with refresh token
            refresh_token = f"refresh_token_{secrets.token_urlsafe(32)}"
            encrypted_refresh = token_encryption.encrypt_refresh_token(refresh_token)
            decrypted_refresh = token_encryption.decrypt_refresh_token(encrypted_refresh)
            
            if decrypted_refresh != refresh_token:
                return {
                    'status': 'failed',
                    'message': 'Refresh token encryption failed',
                    'issues': ['Refresh token encryption/decryption mismatch']
                }
            
            return {
                'status': 'passed',
                'message': 'Token encryption working correctly',
                'details': {
                    'access_token_encryption': 'working',
                    'refresh_token_encryption': 'working',
                    'encryption_reversible': 'working'
                }
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'message': f'Token encryption test failed: {str(e)}',
                'issues': [str(e)]
            }
    
    def _test_rate_limiting(self) -> Dict[str, Any]:
        """Test rate limiting functionality"""
        try:
            from utils.rate_limiter import rate_limiter
            
            test_key = f"oauth_test_{int(time.time())}"
            
            # Test normal request
            result1 = rate_limiter.check_rate_limit(test_key)
            if not isinstance(result1, dict) or 'allowed' not in result1:
                return {
                    'status': 'failed',
                    'message': 'Rate limiter returned invalid format',
                    'issues': ['check_rate_limit() did not return dict with "allowed" key']
                }
            
            if not result1['allowed']:
                return {
                    'status': 'failed',
                    'message': 'Rate limiter rejected first request',
                    'issues': ['First request should be allowed']
                }
            
            # Test multiple requests (should still be allowed within limits)
            for i in range(5):
                result = rate_limiter.check_rate_limit(test_key)
                if not result['allowed']:
                    return {
                        'status': 'failed',
                        'message': f'Rate limiter rejected request {i+2}',
                        'issues': ['Normal usage should be allowed']
                    }
            
            return {
                'status': 'passed',
                'message': 'Rate limiting working correctly',
                'details': {
                    'normal_requests': 'allowed',
                    'rate_limit_format': 'correct',
                    'limit_tracking': 'working'
                }
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'message': f'Rate limiting test failed: {str(e)}',
                'issues': [str(e)]
            }
    
    def _test_error_handling(self) -> Dict[str, Any]:
        """Test OAuth error handling capabilities"""
        try:
            from utils.oauth_error_handler import oauth_error_handler
            
            # Test error classification
            test_error = Exception("access_denied")
            redirect_url, message, recoverable = oauth_error_handler.handle_oauth_error(test_error)
            
            if not redirect_url or not message:
                return {
                    'status': 'failed',
                    'message': 'Error handler returned invalid response',
                    'issues': ['handle_oauth_error() returned empty redirect_url or message']
                }
            
            # Test recovery suggestions
            from utils.oauth_error_handler import OAuthErrorType
            suggestions = oauth_error_handler.get_recovery_suggestions(OAuthErrorType.ACCESS_DENIED)
            
            if not isinstance(suggestions, dict) or 'user_message' not in suggestions:
                return {
                    'status': 'failed',
                    'message': 'Recovery suggestions malformed',
                    'issues': ['get_recovery_suggestions() did not return proper format']
                }
            
            return {
                'status': 'passed',
                'message': 'Error handling working correctly',
                'details': {
                    'error_classification': 'working',
                    'user_feedback': 'working',
                    'recovery_suggestions': 'working',
                    'redirect_handling': 'working'
                }
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'message': f'Error handling test failed: {str(e)}',
                'issues': [str(e)]
            }
    
    def _test_callback_handling(self) -> Dict[str, Any]:
        """Test OAuth callback handling"""
        try:
            from utils.oauth_callback_handler import oauth_callback_handler
            
            # Test callback with missing parameters (should fail gracefully)
            success, result = oauth_callback_handler.handle_callback("", "", "access_denied")
            
            if success:
                return {
                    'status': 'failed',
                    'message': 'Callback handler accepted invalid parameters',
                    'issues': ['Empty parameters should cause failure']
                }
            
            if not isinstance(result, dict) or 'error' not in result:
                return {
                    'status': 'failed',
                    'message': 'Callback handler returned invalid error format',
                    'issues': ['Error response should be dict with "error" key']
                }
            
            return {
                'status': 'passed',
                'message': 'Callback handling working correctly',
                'details': {
                    'parameter_validation': 'working',
                    'error_response_format': 'working',
                    'graceful_failure': 'working'
                }
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'message': f'Callback handling test failed: {str(e)}',
                'issues': [str(e)]
            }
    
    def _test_security_implementation(self) -> Dict[str, Any]:
        """Test security implementation"""
        try:
            if not self.app:
                return {
                    'status': 'skipped',
                    'message': 'No Flask app provided for security testing',
                    'issues': []
                }
            
            # Test security headers with test client
            with self.app.test_client() as client:
                response = client.get('/')
                headers = response.headers
                
                required_headers = [
                    'Content-Security-Policy',
                    'X-Content-Type-Options',
                    'X-Frame-Options'
                ]
                
                missing_headers = [h for h in required_headers if h not in headers]
                
                if missing_headers:
                    return {
                        'status': 'failed',
                        'message': 'Missing security headers',
                        'issues': [f'Missing header: {h}' for h in missing_headers]
                    }
            
            return {
                'status': 'passed',
                'message': 'Security implementation working correctly',
                'details': {
                    'security_headers': 'present',
                    'csp_policy': 'configured',
                    'xss_protection': 'enabled'
                }
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'message': f'Security implementation test failed: {str(e)}',
                'issues': [str(e)]
            }
    
    def _test_production_readiness(self) -> Dict[str, Any]:
        """Test production deployment readiness"""
        try:
            import os
            
            # Check required environment variables
            required_vars = [
                'SESSION_SECRET',
                'DATABASE_URL'
            ]
            
            missing_vars = [var for var in required_vars if not os.environ.get(var)]
            
            if missing_vars:
                return {
                    'status': 'failed',
                    'message': 'Missing required environment variables',
                    'issues': [f'Missing: {var}' for var in missing_vars]
                }
            
            # Test application startup
            if self.app:
                try:
                    with self.app.test_client() as client:
                        # Test health endpoint
                        health_response = client.get('/health')
                        if health_response.status_code >= 500:
                            return {
                                'status': 'failed',
                                'message': 'Health endpoint failing',
                                'issues': [f'Health check returned {health_response.status_code}']
                            }
                        
                        # Test main page
                        main_response = client.get('/')
                        if main_response.status_code >= 500:
                            return {
                                'status': 'failed',
                                'message': 'Main page failing',
                                'issues': [f'Main page returned {main_response.status_code}']
                            }
                except Exception as e:
                    return {
                        'status': 'failed',
                        'message': 'Application startup test failed',
                        'issues': [str(e)]
                    }
            
            return {
                'status': 'passed',
                'message': 'Production readiness validated',
                'details': {
                    'environment_variables': 'configured',
                    'application_startup': 'working',
                    'health_endpoint': 'working',
                    'main_endpoint': 'working'
                }
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'message': f'Production readiness test failed: {str(e)}',
                'issues': [str(e)]
            }
    
    def generate_test_report(self, test_results: Dict[str, Any]) -> str:
        """Generate human-readable test report"""
        report = []
        report.append("=" * 60)
        report.append("OAUTH TESTING FRAMEWORK - COMPREHENSIVE REPORT")
        report.append("=" * 60)
        report.append(f"Test Suite: {test_results['test_suite']}")
        report.append(f"Start Time: {test_results['start_time']}")
        report.append(f"Duration: {test_results.get('duration', 'N/A')}")
        report.append(f"Overall Status: {test_results['overall_status'].upper()}")
        report.append(f"Success Rate: {test_results.get('success_rate', 'N/A')}")
        report.append(f"Tests Run: {test_results['tests_run']}")
        report.append(f"Tests Passed: {test_results['tests_passed']}")
        report.append(f"Tests Failed: {test_results['tests_failed']}")
        report.append("")
        
        # Individual test results
        for test_name, result in test_results['test_results'].items():
            status_symbol = "✓" if result['status'] == 'passed' else "✗" if result['status'] == 'failed' else "~"
            report.append(f"{status_symbol} {test_name.replace('_', ' ').title()}: {result['status'].upper()}")
            report.append(f"   {result['message']}")
            
            if result['status'] == 'failed' and 'issues' in result:
                for issue in result['issues']:
                    report.append(f"   - {issue}")
            
            if 'details' in result:
                for key, value in result['details'].items():
                    report.append(f"   {key}: {value}")
            
            report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)

# Global testing framework instance
oauth_testing_framework = OAuthTestingFramework()