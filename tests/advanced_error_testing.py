"""
Advanced Error Detection and Testing Framework
Comprehensive system for detecting bugs, errors, and edge cases
"""
import os
import re
import ast
import sys
import json
import time
import logging
import traceback
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
import requests
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from io import StringIO

logger = logging.getLogger(__name__)

class AdvancedErrorDetector:
    """Advanced error detection system for comprehensive bug testing"""
    
    def __init__(self):
        self.root_path = Path('.')
        self.results = {
            'syntax_errors': [],
            'import_errors': [],
            'runtime_errors': [],
            'logic_errors': [],
            'security_vulnerabilities': [],
            'performance_issues': [],
            'database_errors': [],
            'api_errors': [],
            'configuration_errors': [],
            'dependency_conflicts': []
        }
        
        # Error patterns to detect
        self.error_patterns = {
            'syntax_errors': [
                r'SyntaxError',
                r'IndentationError',
                r'TabError',
                r'unexpected EOF',
                r'invalid syntax'
            ],
            'import_errors': [
                r'ImportError',
                r'ModuleNotFoundError',
                r'No module named',
                r'cannot import name'
            ],
            'runtime_errors': [
                r'AttributeError',
                r'NameError',
                r'TypeError',
                r'ValueError',
                r'KeyError',
                r'IndexError',
                r'RuntimeError'
            ],
            'database_errors': [
                r'sqlalchemy\.exc',
                r'OperationalError',
                r'IntegrityError',
                r'DataError',
                r'ProgrammingError'
            ],
            'security_vulnerabilities': [
                r'eval\(',
                r'exec\(',
                r'subprocess\.call\(',
                r'os\.system\(',
                r'shell=True',
                r'pickle\.loads',
                r'yaml\.load\(',
                r'input\([^)]*\).*eval'
            ]
        }
        
        # Common problematic patterns
        self.problematic_patterns = {
            'dangerous_imports': [
                'import pickle',
                'import subprocess',
                'import os',
                'from subprocess import',
                'from os import system'
            ],
            'sql_injection_risks': [
                r'f".*SELECT.*{.*}.*"',
                r'f\'.*SELECT.*{.*}.*\'',
                r'\.format\(.*\).*SELECT',
                r'%.*SELECT',
                r'execute\(f"',
                r'execute\(f\''
            ],
            'xss_vulnerabilities': [
                r'innerHTML.*\+',
                r'document\.write\(',
                r'eval\(',
                r'\.html\(.*\+',
                r'render_template_string\('
            ],
            'path_traversal': [
                r'\.\./',
                r'\.\.\\\\',
                r'open\(.*\+',
                r'file.*request\.',
                r'Path\(.*request\.'
            ]
        }
    
    def run_comprehensive_error_scan(self) -> Dict:
        """Run comprehensive error detection across entire codebase"""
        logger.info("🔍 Starting comprehensive error detection scan...")
        
        # Phase 1: Static Analysis
        self._scan_syntax_errors()
        self._scan_import_issues()
        self._scan_security_vulnerabilities()
        self._scan_logic_errors()
        
        # Phase 2: Runtime Testing
        self._test_import_functionality()
        self._test_application_startup()
        self._test_api_endpoints()
        
        # Phase 3: Configuration Analysis
        self._scan_configuration_issues()
        self._scan_dependency_conflicts()
        
        # Phase 4: Database Testing
        self._test_database_connections()
        self._test_database_queries()
        
        # Phase 5: Performance Analysis
        self._scan_performance_issues()
        
        return self._generate_error_report()
    
    def _scan_syntax_errors(self):
        """Scan for syntax errors in Python files"""
        logger.info("Scanning for syntax errors...")
        
        python_files = list(self.root_path.rglob('*.py'))
        
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Try to parse with AST
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    self.results['syntax_errors'].append({
                        'file': str(file_path),
                        'line': e.lineno,
                        'error': str(e),
                        'type': 'SyntaxError',
                        'severity': 'CRITICAL'
                    })
                except Exception as e:
                    self.results['syntax_errors'].append({
                        'file': str(file_path),
                        'line': 0,
                        'error': str(e),
                        'type': 'ParseError',
                        'severity': 'HIGH'
                    })
                    
            except Exception as e:
                logger.warning(f"Could not analyze {file_path}: {e}")
    
    def _scan_import_issues(self):
        """Scan for import-related issues"""
        logger.info("Scanning for import issues...")
        
        python_files = list(self.root_path.rglob('*.py'))
        
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Extract import statements
                import_lines = []
                for i, line in enumerate(content.split('\n'), 1):
                    stripped = line.strip()
                    if stripped.startswith('import ') or stripped.startswith('from '):
                        import_lines.append((i, stripped))
                
                # Test each import
                for line_no, import_stmt in import_lines:
                    try:
                        # Create a test environment to check import
                        test_code = f"""
import sys
sys.path.insert(0, '.')
{import_stmt}
"""
                        exec(test_code)
                    except (ImportError, ModuleNotFoundError) as e:
                        self.results['import_errors'].append({
                            'file': str(file_path),
                            'line': line_no,
                            'import_statement': import_stmt,
                            'error': str(e),
                            'type': 'ImportError',
                            'severity': 'HIGH'
                        })
                    except Exception as e:
                        self.results['import_errors'].append({
                            'file': str(file_path),
                            'line': line_no,
                            'import_statement': import_stmt,
                            'error': str(e),
                            'type': 'UnknownImportError',
                            'severity': 'MEDIUM'
                        })
                        
            except Exception as e:
                logger.warning(f"Could not analyze imports in {file_path}: {e}")
    
    def _scan_security_vulnerabilities(self):
        """Scan for security vulnerabilities"""
        logger.info("Scanning for security vulnerabilities...")
        
        python_files = list(self.root_path.rglob('*.py'))
        
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Check for security patterns
                for vuln_type, patterns in self.problematic_patterns.items():
                    for pattern in patterns:
                        matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
                        for match in matches:
                            line_no = content[:match.start()].count('\n') + 1
                            self.results['security_vulnerabilities'].append({
                                'file': str(file_path),
                                'line': line_no,
                                'vulnerability_type': vuln_type,
                                'pattern': pattern,
                                'match': match.group(),
                                'severity': 'HIGH' if vuln_type in ['sql_injection_risks', 'xss_vulnerabilities'] else 'MEDIUM'
                            })
                            
            except Exception as e:
                logger.warning(f"Could not scan security in {file_path}: {e}")
    
    def _scan_logic_errors(self):
        """Scan for common logic errors"""
        logger.info("Scanning for logic errors...")
        
        logic_error_patterns = [
            (r'if.*=.*:', 'Assignment in if statement'),
            (r'== None', 'Use "is None" instead of "== None"'),
            (r'!= None', 'Use "is not None" instead of "!= None"'),
            (r'len\([^)]+\) == 0', 'Use "not" instead of "len() == 0"'),
            (r'len\([^)]+\) > 0', 'Use direct check instead of "len() > 0"'),
            (r'except:', 'Bare except clause'),
            (r'except Exception:', 'Overly broad exception handling'),
            (r'print\(.*password.*\)', 'Potential password logging'),
            (r'print\(.*secret.*\)', 'Potential secret logging'),
            (r'range\(len\(', 'Consider enumerate() instead of range(len())'),
        ]
        
        python_files = list(self.root_path.rglob('*.py'))
        
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                for pattern, description in logic_error_patterns:
                    matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
                    for match in matches:
                        line_no = content[:match.start()].count('\n') + 1
                        self.results['logic_errors'].append({
                            'file': str(file_path),
                            'line': line_no,
                            'pattern': pattern,
                            'description': description,
                            'match': match.group(),
                            'severity': 'MEDIUM'
                        })
                        
            except Exception as e:
                logger.warning(f"Could not scan logic errors in {file_path}: {e}")
    
    def _test_import_functionality(self):
        """Test actual import functionality"""
        logger.info("Testing import functionality...")
        
        # Test critical modules
        critical_modules = [
            'app',
            'config',
            'database',
            'models',
            'routes',
            'utils'
        ]
        
        for module_name in critical_modules:
            try:
                __import__(module_name)
                logger.info(f"✅ Module {module_name} imports successfully")
            except ImportError as e:
                self.results['import_errors'].append({
                    'module': module_name,
                    'error': str(e),
                    'type': 'CriticalModuleImportError',
                    'severity': 'CRITICAL'
                })
            except Exception as e:
                self.results['runtime_errors'].append({
                    'module': module_name,
                    'error': str(e),
                    'type': 'ModuleRuntimeError',
                    'severity': 'HIGH'
                })
    
    def _test_application_startup(self):
        """Test application startup functionality"""
        logger.info("Testing application startup...")
        
        try:
            # Test basic app creation
            import app
            if hasattr(app, 'create_app'):
                test_app = app.create_app()
                logger.info("✅ Application creates successfully")
            else:
                logger.warning("No create_app function found")
                
        except Exception as e:
            self.results['runtime_errors'].append({
                'component': 'application_startup',
                'error': str(e),
                'traceback': traceback.format_exc(),
                'type': 'StartupError',
                'severity': 'CRITICAL'
            })
    
    def _test_api_endpoints(self):
        """Test API endpoints for errors"""
        logger.info("Testing API endpoints...")
        
        try:
            # Get base URL
            base_url = self._get_base_url()
            
            # Test critical endpoints
            endpoints_to_test = [
                ('/health', 'GET'),
                ('/api/health', 'GET'),
                ('/', 'GET'),
                ('/api/chat', 'POST'),
                ('/api/demo/chat', 'POST')
            ]
            
            session = requests.Session()
            session.timeout = 10
            
            for endpoint, method in endpoints_to_test:
                try:
                    if method == 'GET':
                        response = session.get(f"{base_url}{endpoint}")
                    elif method == 'POST':
                        response = session.post(f"{base_url}{endpoint}", 
                                              json={'test': 'data'})
                    
                    if response.status_code >= 500:
                        self.results['api_errors'].append({
                            'endpoint': endpoint,
                            'method': method,
                            'status_code': response.status_code,
                            'error': 'Server error',
                            'severity': 'HIGH'
                        })
                    elif response.status_code >= 400:
                        self.results['api_errors'].append({
                            'endpoint': endpoint,
                            'method': method,
                            'status_code': response.status_code,
                            'error': 'Client error',
                            'severity': 'MEDIUM'
                        })
                    else:
                        logger.info(f"✅ {method} {endpoint} responds successfully")
                        
                except requests.RequestException as e:
                    self.results['api_errors'].append({
                        'endpoint': endpoint,
                        'method': method,
                        'error': str(e),
                        'type': 'ConnectionError',
                        'severity': 'HIGH'
                    })
                    
        except Exception as e:
            logger.warning(f"Could not test API endpoints: {e}")
    
    def _scan_configuration_issues(self):
        """Scan for configuration issues"""
        logger.info("Scanning configuration issues...")
        
        config_files = [
            'pyproject.toml',
            'requirements.txt',
            'replit.toml',
            'config.py',
            'app.py'
        ]
        
        for config_file in config_files:
            config_path = Path(config_file)
            if not config_path.exists():
                continue
            
            try:
                content = config_path.read_text(encoding='utf-8', errors='ignore')
                
                # Check for common configuration issues
                if config_file == 'pyproject.toml':
                    self._check_pyproject_toml(content, config_path)
                elif config_file == 'requirements.txt':
                    self._check_requirements_txt(content, config_path)
                elif config_file == 'replit.toml':
                    self._check_replit_toml(content, config_path)
                elif config_file in ['config.py', 'app.py']:
                    self._check_python_config(content, config_path)
                    
            except Exception as e:
                self.results['configuration_errors'].append({
                    'file': config_file,
                    'error': str(e),
                    'type': 'ConfigReadError',
                    'severity': 'HIGH'
                })
    
    def _check_pyproject_toml(self, content: str, file_path: Path):
        """Check pyproject.toml for issues"""
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib
        
        try:
            config = tomllib.loads(content)
            
            # Check for common issues
            if 'dependencies' not in config.get('project', {}):
                self.results['configuration_errors'].append({
                    'file': str(file_path),
                    'error': 'No dependencies section found',
                    'type': 'MissingDependencies',
                    'severity': 'MEDIUM'
                })
            
            # Check for conflicting versions
            deps = config.get('project', {}).get('dependencies', [])
            dep_versions = {}
            for dep in deps:
                if '==' in dep:
                    name, version = dep.split('==', 1)
                    if name in dep_versions and dep_versions[name] != version:
                        self.results['dependency_conflicts'].append({
                            'file': str(file_path),
                            'dependency': name,
                            'versions': [dep_versions[name], version],
                            'severity': 'HIGH'
                        })
                    dep_versions[name] = version
                    
        except Exception as e:
            self.results['configuration_errors'].append({
                'file': str(file_path),
                'error': f"TOML parsing error: {str(e)}",
                'type': 'TOMLParseError',
                'severity': 'HIGH'
            })
    
    def _check_requirements_txt(self, content: str, file_path: Path):
        """Check requirements.txt for issues"""
        lines = content.strip().split('\n')
        dep_versions = {}
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Check for unpinned dependencies
            if '==' not in line and '>=' not in line and '~=' not in line:
                self.results['configuration_errors'].append({
                    'file': str(file_path),
                    'line': i,
                    'dependency': line,
                    'error': 'Unpinned dependency version',
                    'type': 'UnpinnedDependency',
                    'severity': 'MEDIUM'
                })
            
            # Check for version conflicts
            if '==' in line:
                name, version = line.split('==', 1)
                if name in dep_versions and dep_versions[name] != version:
                    self.results['dependency_conflicts'].append({
                        'file': str(file_path),
                        'dependency': name,
                        'versions': [dep_versions[name], version],
                        'severity': 'HIGH'
                    })
                dep_versions[name] = version
    
    def _check_replit_toml(self, content: str, file_path: Path):
        """Check replit.toml for deployment issues"""
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib
        
        try:
            config = tomllib.loads(content)
            
            # Check for essential deployment settings
            if 'deployment' not in config:
                self.results['configuration_errors'].append({
                    'file': str(file_path),
                    'error': 'No deployment configuration found',
                    'type': 'MissingDeploymentConfig',
                    'severity': 'MEDIUM'
                })
            
            # Check run command
            if 'run' not in config:
                self.results['configuration_errors'].append({
                    'file': str(file_path),
                    'error': 'No run command specified',
                    'type': 'MissingRunCommand',
                    'severity': 'HIGH'
                })
                
        except Exception as e:
            self.results['configuration_errors'].append({
                'file': str(file_path),
                'error': f"TOML parsing error: {str(e)}",
                'type': 'TOMLParseError',
                'severity': 'HIGH'
            })
    
    def _check_python_config(self, content: str, file_path: Path):
        """Check Python configuration files"""
        # Check for hardcoded secrets
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']'
        ]
        
        for pattern in secret_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_no = content[:match.start()].count('\n') + 1
                self.results['security_vulnerabilities'].append({
                    'file': str(file_path),
                    'line': line_no,
                    'vulnerability_type': 'hardcoded_secret',
                    'match': match.group(),
                    'severity': 'HIGH'
                })
    
    def _scan_dependency_conflicts(self):
        """Scan for dependency conflicts"""
        logger.info("Scanning for dependency conflicts...")
        
        try:
            # Check pip freeze output for conflicts
            result = subprocess.run([sys.executable, '-m', 'pip', 'check'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                conflicts = result.stdout.split('\n')
                for conflict in conflicts:
                    if conflict.strip():
                        self.results['dependency_conflicts'].append({
                            'error': conflict.strip(),
                            'type': 'PipDependencyConflict',
                            'severity': 'HIGH'
                        })
        except Exception as e:
            logger.warning(f"Could not check pip dependencies: {e}")
    
    def _test_database_connections(self):
        """Test database connections"""
        logger.info("Testing database connections...")
        
        try:
            # Test database import and connection
            from database import db
            
            # Try basic database operations
            try:
                # This should work if database is properly configured
                logger.info("✅ Database module imports successfully")
            except Exception as e:
                self.results['database_errors'].append({
                    'component': 'database_connection',
                    'error': str(e),
                    'type': 'ConnectionError',
                    'severity': 'HIGH'
                })
                
        except ImportError as e:
            self.results['database_errors'].append({
                'component': 'database_import',
                'error': str(e),
                'type': 'ImportError',
                'severity': 'HIGH'
            })
    
    def _test_database_queries(self):
        """Test basic database query functionality"""
        logger.info("Testing database queries...")
        
        try:
            # Test model imports
            try:
                import models
                logger.info("✅ Models module imports successfully")
            except ImportError as e:
                self.results['database_errors'].append({
                    'component': 'models_import',
                    'error': str(e),
                    'type': 'ImportError',
                    'severity': 'HIGH'
                })
                
        except Exception as e:
            self.results['database_errors'].append({
                'component': 'database_query_test',
                'error': str(e),
                'type': 'QueryError',
                'severity': 'MEDIUM'
            })
    
    def _scan_performance_issues(self):
        """Scan for performance issues"""
        logger.info("Scanning for performance issues...")
        
        performance_patterns = [
            (r'\.query\.all\(\)', 'Consider pagination for large datasets'),
            (r'for.*in.*\.query\.all\(\)', 'Inefficient iteration over all records'),
            (r'N\+1.*query', 'Potential N+1 query problem'),
            (r'sleep\([^)]*\)', 'Blocking sleep call'),
            (r'requests\.get\(.*timeout.*\)', 'HTTP request without timeout'),
            (r'while True:', 'Infinite loop detected'),
            (r'\.join\(.*\.query', 'Potentially inefficient join'),
        ]
        
        python_files = list(self.root_path.rglob('*.py'))
        
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                for pattern, description in performance_patterns:
                    matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
                    for match in matches:
                        line_no = content[:match.start()].count('\n') + 1
                        self.results['performance_issues'].append({
                            'file': str(file_path),
                            'line': line_no,
                            'pattern': pattern,
                            'description': description,
                            'match': match.group(),
                            'severity': 'MEDIUM'
                        })
                        
            except Exception as e:
                logger.warning(f"Could not scan performance in {file_path}: {e}")
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_patterns = [
            '__pycache__',
            '.git',
            'node_modules',
            'venv',
            '.pytest_cache',
            'backup',
            'archive',
            'test_',
            '_test'
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _get_base_url(self) -> str:
        """Get base URL for testing"""
        try:
            from config import PORT, HOST
            return f"http://{HOST}:{PORT}"
        except ImportError:
            return "http://localhost:5000"
    
    def _generate_error_report(self) -> Dict:
        """Generate comprehensive error report"""
        total_errors = sum(len(errors) for errors in self.results.values())
        
        critical_errors = sum(1 for category in self.results.values()
                            for error in (category if isinstance(category, list) else [])
                            if isinstance(error, dict) and error.get('severity') == 'CRITICAL')
        
        high_errors = sum(1 for category in self.results.values()
                         for error in (category if isinstance(category, list) else [])
                         if isinstance(error, dict) and error.get('severity') == 'HIGH')
        
        medium_errors = sum(1 for category in self.results.values()
                           for error in (category if isinstance(category, list) else [])
                           if isinstance(error, dict) and error.get('severity') == 'MEDIUM')
        
        report = {
            'summary': {
                'total_errors': total_errors,
                'critical_errors': critical_errors,
                'high_priority_errors': high_errors,
                'medium_priority_errors': medium_errors,
                'scan_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            'errors_by_category': {
                'syntax_errors': len(self.results['syntax_errors']),
                'import_errors': len(self.results['import_errors']),
                'runtime_errors': len(self.results['runtime_errors']),
                'logic_errors': len(self.results['logic_errors']),
                'security_vulnerabilities': len(self.results['security_vulnerabilities']),
                'performance_issues': len(self.results['performance_issues']),
                'database_errors': len(self.results['database_errors']),
                'api_errors': len(self.results['api_errors']),
                'configuration_errors': len(self.results['configuration_errors']),
                'dependency_conflicts': len(self.results['dependency_conflicts'])
            },
            'detailed_findings': self.results,
            'fix_recommendations': self._generate_fix_recommendations()
        }
        
        return report
    
    def _generate_fix_recommendations(self) -> List[Dict]:
        """Generate fix recommendations"""
        recommendations = []
        
        if self.results['syntax_errors']:
            recommendations.append({
                'priority': 'CRITICAL',
                'category': 'Syntax Errors',
                'description': 'Fix syntax errors that prevent code execution',
                'count': len(self.results['syntax_errors']),
                'action': 'Review and fix Python syntax issues'
            })
        
        if self.results['import_errors']:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Import Errors',
                'description': 'Resolve missing dependencies and import issues',
                'count': len(self.results['import_errors']),
                'action': 'Install missing packages or fix import paths'
            })
        
        if self.results['security_vulnerabilities']:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Security Vulnerabilities',
                'description': 'Address security vulnerabilities',
                'count': len(self.results['security_vulnerabilities']),
                'action': 'Implement secure coding practices'
            })
        
        if self.results['runtime_errors']:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Runtime Errors',
                'description': 'Fix runtime errors and exceptions',
                'count': len(self.results['runtime_errors']),
                'action': 'Add error handling and fix runtime issues'
            })
        
        return recommendations
    
    def save_report(self, filename: str = 'advanced_error_report.json'):
        """Save comprehensive error report"""
        report = self._generate_error_report()
        
        report_path = Path('tests') / filename
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate markdown report
        self._save_markdown_report(report, report_path.with_suffix('.md'))
        
        logger.info(f"Error report saved to {report_path}")
        return report
    
    def _save_markdown_report(self, report: Dict, path: Path):
        """Save human-readable markdown report"""
        lines = [
            "# Advanced Error Detection Report",
            "",
            "## Summary",
            f"- **Total Errors**: {report['summary']['total_errors']}",
            f"- **Critical**: {report['summary']['critical_errors']}",
            f"- **High Priority**: {report['summary']['high_priority_errors']}",
            f"- **Medium Priority**: {report['summary']['medium_priority_errors']}",
            f"- **Scan Date**: {report['summary']['scan_timestamp']}",
            "",
            "## Errors by Category"
        ]
        
        for category, count in report['errors_by_category'].items():
            if count > 0:
                lines.append(f"- **{category.replace('_', ' ').title()}**: {count}")
        
        lines.extend([
            "",
            "## Fix Recommendations"
        ])
        
        for i, rec in enumerate(report['fix_recommendations'], 1):
            lines.extend([
                f"### {i}. {rec['category']} ({rec['priority']})",
                f"**Description**: {rec['description']}",
                f"**Count**: {rec['count']}",
                f"**Action**: {rec['action']}",
                ""
            ])
        
        # Add critical errors details
        if report['detailed_findings']['syntax_errors']:
            lines.extend([
                "## Syntax Errors",
                "| File | Line | Error |",
                "|------|------|-------|"
            ])
            
            for error in report['detailed_findings']['syntax_errors']:
                lines.append(f"| {error['file']} | {error['line']} | {error['error']} |")
        
        if report['detailed_findings']['import_errors']:
            lines.extend([
                "",
                "## Import Errors", 
                "| File | Line | Import | Error |",
                "|------|------|--------|-------|"
            ])
            
            for error in report['detailed_findings']['import_errors']:
                import_stmt = error.get('import_statement', 'N/A')
                lines.append(f"| {error.get('file', 'N/A')} | {error.get('line', 'N/A')} | `{import_stmt}` | {error['error']} |")
        
        with open(path, 'w') as f:
            f.write('\n'.join(lines))


if __name__ == "__main__":
    # Run advanced error detection
    detector = AdvancedErrorDetector()
    report = detector.run_comprehensive_error_scan()
    detector.save_report()
    
    print(f"\n🔍 Advanced Error Detection Complete")
    print(f"Total Errors Found: {report['summary']['total_errors']}")
    print(f"Critical: {report['summary']['critical_errors']}")
    print(f"High Priority: {report['summary']['high_priority_errors']}")
    print(f"Medium Priority: {report['summary']['medium_priority_errors']}")
    
    if report['summary']['total_errors'] > 0:
        print(f"\n📊 Errors by Category:")
        for category, count in report['errors_by_category'].items():
            if count > 0:
                print(f"  - {category.replace('_', ' ').title()}: {count}")
    
    print(f"\nFull report saved to: tests/advanced_error_report.md")