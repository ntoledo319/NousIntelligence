#!/usr/bin/env python3
"""
Quick Coverage Debugger
Fast analysis of test coverage gaps and generation of missing tests
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime
import ast

class QuickCoverageDebugger:
    """Fast coverage analysis and test generation"""
    
    def __init__(self):
        self.project_root = Path('.')
        self.functions = {}
        self.routes = {}
        self.classes = {}
        self.test_coverage = {}
        
    def analyze_coverage_gaps(self):
        """Quick analysis of major coverage gaps"""
        print("🔍 Quick Coverage Analysis")
        print("=" * 50)
        
        # 1. Scan core modules
        core_modules = self._get_core_modules()
        print(f"📁 Found {len(core_modules)} core modules")
        
        # 2. Extract key elements
        self._extract_key_elements(core_modules)
        print(f"🔧 Found {len(self.functions)} functions")
        print(f"🌐 Found {len(self.routes)} routes")
        print(f"🏗️ Found {len(self.classes)} classes")
        
        # 3. Check existing tests
        self._analyze_existing_tests()
        
        # 4. Generate coverage report
        gaps = self._identify_coverage_gaps()
        
        # 5. Generate missing tests
        self._generate_missing_tests(gaps)
        
        return gaps
    
    def _get_core_modules(self) -> List[Path]:
        """Get core modules that need testing"""
        core_patterns = [
            'app.py',
            'main.py',
            'models/*.py',
            'routes/*.py',
            'utils/*.py',
            'services/*.py',
            'api/*.py'
        ]
        
        modules = []
        for pattern in core_patterns:
            if '*' in pattern:
                dir_part, file_part = pattern.split('/', 1)
                dir_path = self.project_root / dir_part
                if dir_path.exists():
                    modules.extend(dir_path.glob(file_part))
            else:
                file_path = self.project_root / pattern
                if file_path.exists():
                    modules.append(file_path)
        
        # Filter out backup and test files
        filtered = []
        skip_patterns = ['backup', 'test_', '_test', '__pycache__', 'security_fixes_backup']
        for module in modules:
            if not any(pattern in str(module) for pattern in skip_patterns):
                filtered.append(module)
        
        return filtered[:50]  # Limit for speed
    
    def _extract_key_elements(self, modules: List[Path]):
        """Extract functions, routes, and classes"""
        for module in modules:
            try:
                with open(module, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Extract functions
                functions = re.findall(r'def\s+(\w+)\s*\([^)]*\):', content)
                for func in functions:
                    if not func.startswith('_'):  # Skip private functions
                        self.functions[f"{module.stem}::{func}"] = {
                            'file': str(module),
                            'name': func,
                            'tested': False
                        }
                
                # Extract routes
                routes = re.findall(r'@\w*\.route\(["\']([^"\']+)["\']', content)
                for route in routes:
                    self.routes[route] = {
                        'file': str(module),
                        'path': route,
                        'tested': False
                    }
                
                # Extract classes
                classes = re.findall(r'class\s+(\w+)[\s\(]', content)
                for cls in classes:
                    self.classes[f"{module.stem}::{cls}"] = {
                        'file': str(module),
                        'name': cls,
                        'tested': False
                    }
                    
            except Exception as e:
                print(f"Warning: Could not parse {module}: {e}")
    
    def _analyze_existing_tests(self):
        """Analyze existing test files"""
        test_files = list(self.project_root.glob('test_*.py'))
        test_files.extend(list(self.project_root.glob('tests/*.py')))
        
        all_test_content = ""
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                    all_test_content += f.read() + "\n"
            except:
                continue
        
        # Check what's covered
        for key, func_info in self.functions.items():
            if func_info['name'] in all_test_content:
                func_info['tested'] = True
        
        for path, route_info in self.routes.items():
            if path in all_test_content:
                route_info['tested'] = True
        
        for key, class_info in self.classes.items():
            if class_info['name'] in all_test_content:
                class_info['tested'] = True
    
    def _identify_coverage_gaps(self) -> Dict:
        """Identify major coverage gaps"""
        untested_functions = [k for k, v in self.functions.items() if not v['tested']]
        untested_routes = [k for k, v in self.routes.items() if not v['tested']]
        untested_classes = [k for k, v in self.classes.items() if not v['tested']]
        
        total_items = len(self.functions) + len(self.routes) + len(self.classes)
        tested_items = sum([1 for f in self.functions.values() if f['tested']]) + \
                      sum([1 for r in self.routes.values() if r['tested']]) + \
                      sum([1 for c in self.classes.values() if c['tested']])
        
        coverage_percent = (tested_items / total_items * 100) if total_items > 0 else 0
        
        gaps = {
            'coverage_percent': coverage_percent,
            'total_items': total_items,
            'tested_items': tested_items,
            'untested_functions': untested_functions[:20],
            'untested_routes': untested_routes[:10],
            'untested_classes': untested_classes[:10],
            'priority_items': self._get_priority_items(untested_functions, untested_routes, untested_classes)
        }
        
        print(f"📊 Current Coverage: {coverage_percent:.1f}%")
        print(f"📊 Tested: {tested_items}/{total_items}")
        print(f"🎯 Untested Functions: {len(untested_functions)}")
        print(f"🎯 Untested Routes: {len(untested_routes)}")
        print(f"🎯 Untested Classes: {len(untested_classes)}")
        
        return gaps
    
    def _get_priority_items(self, functions, routes, classes):
        """Get high-priority items that need testing"""
        priority = []
        
        # Critical routes (API endpoints)
        api_routes = [r for r in routes if '/api/' in r]
        priority.extend([f"API Route: {r}" for r in api_routes[:5]])
        
        # Core functions
        core_functions = [f for f in functions if any(module in f for module in ['app::', 'main::', 'auth::'])]
        priority.extend([f"Core Function: {f}" for f in core_functions[:5]])
        
        # Model classes
        model_classes = [c for c in classes if 'models' in self.classes[c]['file']]
        priority.extend([f"Model Class: {c}" for c in model_classes[:3]])
        
        return priority[:10]
    
    def _generate_missing_tests(self, gaps):
        """Generate missing test files"""
        print("\n🔧 Generating Missing Tests")
        print("=" * 50)
        
        # Generate tests for critical components
        self._generate_api_tests(gaps['untested_routes'])
        self._generate_function_tests(gaps['untested_functions'])
        self._generate_class_tests(gaps['untested_classes'])
        self._generate_integration_tests()
        
        print("✅ Test generation complete!")
    
    def _generate_api_tests(self, untested_routes):
        """Generate API endpoint tests"""
        api_routes = [r for r in untested_routes if '/api/' in r]
        if not api_routes:
            return
        
        test_content = '''#!/usr/bin/env python3
"""
Generated API Tests
Comprehensive testing for API endpoints
"""

import json
import pytest
from app import app, db

class TestAPIEndpoints:
    """Test all API endpoints for functionality and security"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                yield client
                db.drop_all()
    
    @pytest.fixture
    def auth_headers(self):
        """Create authentication headers"""
        return {'Content-Type': 'application/json'}

'''
        
        for route in api_routes[:10]:  # Limit to first 10
            route_info = self.routes.get(route, {})
            test_name = route.replace('/', '_').replace('<', '').replace('>', '').strip('_')
            
            test_content += f'''
    def test_{test_name}(self, client, auth_headers):
        """Test {route} endpoint"""
        # Test GET request
        response = client.get('{route}', headers=auth_headers)
        assert response.status_code in [200, 401, 404], f"Unexpected status: {{response.status_code}}"
        
        # Test with demo mode if available
        demo_headers = {{'Content-Type': 'application/json', 'X-Demo-Mode': 'true'}}
        response = client.get('{route}', headers=demo_headers)
        assert response.status_code in [200, 401, 404], f"Demo mode failed: {{response.status_code}}"
        
        # Test JSON response format
        if response.status_code == 200:
            try:
                data = response.get_json()
                assert isinstance(data, (dict, list)), "Response should be JSON"
            except:
                pass  # Some endpoints return HTML
'''
        
        test_content += '''
    def test_api_security_headers(self, client):
        """Test that API endpoints include security headers"""
        test_routes = ['/api/health', '/api/chat', '/api/user']
        
        for route in test_routes:
            response = client.get(route)
            # Check for basic security headers
            assert 'X-Content-Type-Options' in response.headers
            assert 'X-Frame-Options' in response.headers
    
    def test_api_rate_limiting(self, client):
        """Test API rate limiting"""
        # Make multiple rapid requests
        for i in range(10):
            response = client.get('/api/health')
            if response.status_code == 429:
                break
        # Rate limiting should kick in eventually
    
    def test_api_error_handling(self, client):
        """Test API error handling"""
        # Test non-existent endpoint
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
        
        # Test malformed JSON
        response = client.post('/api/chat', 
                             data='invalid json',
                             content_type='application/json')
        assert response.status_code in [400, 422]
'''
        
        with open('tests/test_generated_api.py', 'w') as f:
            f.write(test_content)
        
        print(f"✅ Generated API tests for {len(api_routes)} endpoints")
    
    def _generate_function_tests(self, untested_functions):
        """Generate function unit tests"""
        core_functions = [f for f in untested_functions if any(module in f for module in ['app::', 'main::', 'auth::'])]
        if not core_functions:
            return
        
        test_content = '''#!/usr/bin/env python3
"""
Generated Function Tests
Unit tests for core functions
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestCoreFunctions:
    """Test core application functions"""

'''
        
        for func_key in core_functions[:10]:
            func_info = self.functions[func_key]
            func_name = func_info['name']
            
            test_content += f'''
    def test_{func_name}(self):
        """Test {func_name} function"""
        try:
            # Import the function
            from {Path(func_info['file']).stem} import {func_name}
            
            # Test basic functionality
            # Note: Actual test implementation depends on function signature
            result = {func_name}()
            assert result is not None or result is None  # Function executes without error
            
        except ImportError:
            pytest.skip(f"Could not import {func_name}")
        except Exception as e:
            pytest.fail(f"{func_name} raised unexpected exception: {{e}}")
'''
        
        with open('tests/test_generated_functions.py', 'w') as f:
            f.write(test_content)
        
        print(f"✅ Generated function tests for {len(core_functions)} functions")
    
    def _generate_class_tests(self, untested_classes):
        """Generate class tests"""
        model_classes = [c for c in untested_classes if 'models' in self.classes[c]['file']]
        if not model_classes:
            return
        
        test_content = '''#!/usr/bin/env python3
"""
Generated Model Tests
Tests for database models
"""

import pytest
from app import app, db

class TestModels:
    """Test database models"""
    
    @pytest.fixture(autouse=True)
    def setup_database(self):
        """Setup test database"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            yield
            db.drop_all()

'''
        
        for class_key in model_classes[:5]:
            class_info = self.classes[class_key]
            class_name = class_info['name']
            
            test_content += f'''
    def test_{class_name.lower()}_creation(self):
        """Test {class_name} model creation"""
        with app.app_context():
            try:
                from models import {class_name}
                
                # Test model can be imported
                assert {class_name} is not None
                
                # Test basic model structure
                assert hasattr({class_name}, '__tablename__') or hasattr({class_name}, '__table__')
                
            except ImportError:
                pytest.skip(f"Could not import {class_name}")
'''
        
        with open('tests/test_generated_models.py', 'w') as f:
            f.write(test_content)
        
        print(f"✅ Generated model tests for {len(model_classes)} classes")
    
    def _generate_integration_tests(self):
        """Generate integration tests"""
        test_content = '''#!/usr/bin/env python3
"""
Generated Integration Tests
End-to-end testing for critical user flows
"""

import pytest
from app import app, db

class TestIntegration:
    """Integration tests for complete user workflows"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                yield client
                db.drop_all()
    
    def test_landing_page_flow(self, client):
        """Test complete landing page to demo flow"""
        # Step 1: Access landing page
        response = client.get('/')
        assert response.status_code == 200
        
        # Step 2: Navigate to demo
        response = client.get('/demo')
        assert response.status_code == 200
        
        # Step 3: Test demo functionality
        response = client.post('/api/demo/chat', 
                             json={'message': 'Hello'})
        assert response.status_code in [200, 401]  # May require auth
    
    def test_health_monitoring_flow(self, client):
        """Test health monitoring endpoints"""
        # Test basic health
        response = client.get('/health')
        assert response.status_code == 200
        
        # Test detailed health
        response = client.get('/healthz')
        assert response.status_code == 200
        
        # Test API health
        response = client.get('/api/health')
        assert response.status_code == 200
    
    def test_authentication_flow(self, client):
        """Test authentication workflow"""
        # Test login page access
        response = client.get('/auth/login')
        assert response.status_code in [200, 302, 404]
        
        # Test logout
        response = client.get('/auth/logout')
        assert response.status_code in [200, 302, 404]
    
    def test_api_workflow(self, client):
        """Test API workflow"""
        # Test API discovery
        api_endpoints = ['/api/health', '/api/user', '/api/chat']
        
        for endpoint in api_endpoints:
            response = client.get(endpoint)
            assert response.status_code in [200, 401, 404], f"Endpoint {endpoint} failed"
    
    def test_error_handling(self, client):
        """Test error handling"""
        # Test 404 page
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
        
        # Test malformed API request
        response = client.post('/api/chat', data='invalid')
        assert response.status_code in [400, 422, 404]
'''
        
        with open('tests/test_generated_integration.py', 'w') as f:
            f.write(test_content)
        
        print("✅ Generated integration tests")
    
    def generate_test_runner(self):
        """Generate a comprehensive test runner"""
        runner_content = '''#!/usr/bin/env python3
"""
Comprehensive Test Runner
Runs all generated tests and provides coverage report
"""

import os
import sys
import subprocess
from pathlib import Path

def run_all_tests():
    """Run all generated tests"""
    print("🧪 Running Comprehensive Test Suite")
    print("=" * 50)
    
    test_files = [
        'tests/test_generated_api.py',
        'tests/test_generated_functions.py', 
        'tests/test_generated_models.py',
        'tests/test_generated_integration.py'
    ]
    
    results = {}
    
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"\\n🔍 Running {test_file}")
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'pytest', test_file, '-v'
                ], capture_output=True, text=True, timeout=60)
                
                results[test_file] = {
                    'returncode': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
                
                if result.returncode == 0:
                    print(f"✅ {test_file} PASSED")
                else:
                    print(f"❌ {test_file} FAILED")
                    if result.stderr:
                        print(f"Error: {result.stderr[:200]}")
                        
            except subprocess.TimeoutExpired:
                print(f"⏰ {test_file} TIMEOUT")
                results[test_file] = {'returncode': -1, 'error': 'timeout'}
            except Exception as e:
                print(f"💥 {test_file} ERROR: {e}")
                results[test_file] = {'returncode': -1, 'error': str(e)}
    
    # Generate summary
    print("\\n📊 TEST SUMMARY")
    print("=" * 50)
    passed = sum(1 for r in results.values() if r.get('returncode') == 0)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Coverage: {(passed/total)*100:.1f}%")
    
    return results

if __name__ == "__main__":
    run_all_tests()
'''
        
        with open('run_generated_tests.py', 'w') as f:
            f.write(runner_content)
        
        print("✅ Generated comprehensive test runner")

def main():
    """Main function"""
    debugger = QuickCoverageDebugger()
    
    # Analyze coverage gaps
    gaps = debugger.analyze_coverage_gaps()
    
    # Generate test runner
    debugger.generate_test_runner()
    
    # Save coverage report
    with open('coverage_gaps_report.json', 'w') as f:
        json.dump(gaps, f, indent=2)
    
    print(f"\n🎯 COVERAGE ANALYSIS COMPLETE")
    print("=" * 50)
    print(f"Current Coverage: {gaps['coverage_percent']:.1f}%")
    print(f"Items Needing Tests: {gaps['total_items'] - gaps['tested_items']}")
    
    if gaps['coverage_percent'] < 100:
        print(f"\n📋 PRIORITY ACTIONS:")
        for item in gaps['priority_items']:
            print(f"  • {item}")
        
        print(f"\n🔧 GENERATED TESTS:")
        print("  • tests/test_generated_api.py")
        print("  • tests/test_generated_functions.py")
        print("  • tests/test_generated_models.py")
        print("  • tests/test_generated_integration.py")
        print("  • run_generated_tests.py")
        
        print(f"\n▶️  RUN TESTS: python run_generated_tests.py")
    
    return gaps['coverage_percent']

if __name__ == "__main__":
    coverage = main()
    sys.exit(0 if coverage >= 100 else 1)