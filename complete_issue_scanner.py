#!/usr/bin/env python3
"""
Complete Issue Scanner - Identifies ALL issues in NOUS codebase
Systematic analysis of every file, import, function, and configuration
"""
import os
import sys
import ast
import json
import re
import subprocess
from pathlib import Path
from collections import defaultdict
from datetime import datetime

class CompleteIssueScanner:
    def __init__(self):
        self.all_issues = {
            'critical_errors': [],
            'import_failures': [],
            'syntax_errors': [],
            'type_errors': [],
            'missing_dependencies': [],
            'broken_functions': [],
            'configuration_issues': [],
            'security_vulnerabilities': [],
            'performance_issues': [],
            'dead_code': [],
            'circular_dependencies': [],
            'database_issues': [],
            'route_problems': [],
            'template_issues': [],
            'static_asset_problems': [],
            'documentation_gaps': [],
            'testing_deficiencies': [],
            'deployment_blockers': [],
            'accessibility_issues': [],
            'compatibility_problems': []
        }
        self.file_analysis = {}
        self.dependency_map = defaultdict(set)
        self.route_registry = {}
        self.model_registry = {}
        
    def scan_everything(self):
        """Comprehensive scan of entire codebase"""
        print("🔍 Starting complete issue scan...")
        
        # Systematic analysis of every component
        self._scan_python_files()
        self._scan_configuration_files()
        self._scan_templates()
        self._scan_static_assets()
        self._scan_database_structure()
        self._analyze_dependencies()
        self._test_imports()
        self._check_routes()
        self._validate_models()
        self._security_audit()
        self._performance_analysis()
        self._deployment_readiness()
        self._accessibility_check()
        
        return self.all_issues
    
    def _scan_python_files(self):
        """Scan every Python file for issues"""
        print("📁 Scanning all Python files...")
        
        for root, dirs, files in os.walk('.'):
            # Don't skip any directories for complete analysis
            dirs[:] = [d for d in dirs if not d.startswith('.git')]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self._analyze_python_file(file_path)
    
    def _analyze_python_file(self, file_path):
        """Comprehensive analysis of a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Initialize file analysis
            self.file_analysis[file_path] = {
                'syntax_valid': False,
                'imports': [],
                'functions': [],
                'classes': [],
                'routes': [],
                'issues': []
            }
            
            # 1. Syntax validation
            try:
                tree = ast.parse(content)
                self.file_analysis[file_path]['syntax_valid'] = True
                
                # Extract all code elements
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self.file_analysis[file_path]['imports'].append(alias.name)
                            
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self.file_analysis[file_path]['imports'].append(node.module)
                            
                    elif isinstance(node, ast.FunctionDef):
                        self.file_analysis[file_path]['functions'].append(node.name)
                        
                    elif isinstance(node, ast.ClassDef):
                        self.file_analysis[file_path]['classes'].append(node.name)
                        
            except SyntaxError as e:
                self.all_issues['syntax_errors'].append({
                    'file': file_path,
                    'line': e.lineno,
                    'error': str(e),
                    'severity': 'critical'
                })
                return
            
            # 2. Import validation
            self._validate_imports(file_path, content)
            
            # 3. Function analysis
            self._analyze_functions(file_path, content)
            
            # 4. Route detection
            self._detect_routes(file_path, content)
            
            # 5. Model detection
            self._detect_models(file_path, content)
            
            # 6. Security issues
            self._check_security_issues(file_path, content)
            
            # 7. Performance issues
            self._check_performance_issues(file_path, content)
            
            # 8. Dead code detection
            self._detect_dead_code(file_path, content)
            
        except Exception as e:
            self.all_issues['critical_errors'].append({
                'file': file_path,
                'error': f"File analysis failed: {str(e)}",
                'severity': 'critical'
            })
    
    def _validate_imports(self, file_path, content):
        """Validate all imports in the file"""
        import_lines = [line.strip() for line in content.split('\n') if line.strip().startswith(('import ', 'from '))]
        
        for line in import_lines:
            try:
                # Extract module name
                if line.startswith('from '):
                    module = line.split(' import ')[0].replace('from ', '').strip()
                else:
                    module = line.replace('import ', '').split(' as ')[0].strip()
                
                # Test if import would work
                try:
                    if '.' in module:
                        # Handle relative imports
                        base_module = module.split('.')[0]
                        if not self._module_exists(base_module):
                            self.all_issues['import_failures'].append({
                                'file': file_path,
                                'module': module,
                                'line': line,
                                'severity': 'high'
                            })
                    else:
                        if not self._module_exists(module):
                            self.all_issues['import_failures'].append({
                                'file': file_path,
                                'module': module,
                                'line': line,
                                'severity': 'high'
                            })
                            
                except Exception:
                    self.all_issues['import_failures'].append({
                        'file': file_path,
                        'module': module,
                        'line': line,
                        'severity': 'medium'
                    })
                    
            except Exception as e:
                self.all_issues['import_failures'].append({
                    'file': file_path,
                    'line': line,
                    'error': str(e),
                    'severity': 'medium'
                })
    
    def _module_exists(self, module_name):
        """Check if a module exists and can be imported"""
        if module_name in ['os', 'sys', 'json', 'datetime', 're', 'pathlib', 'subprocess']:
            return True
        
        # Check if it's a local module
        local_paths = [
            f"{module_name}.py",
            f"{module_name}/__init__.py",
            f"utils/{module_name}.py",
            f"routes/{module_name}.py",
            f"models/{module_name}.py",
            f"services/{module_name}.py"
        ]
        
        for path in local_paths:
            if os.path.exists(path):
                return True
        
        # Try to import it
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False
    
    def _analyze_functions(self, file_path, content):
        """Analyze all functions for issues"""
        lines = content.split('\n')
        
        # Find all function definitions
        for i, line in enumerate(lines):
            if re.match(r'^\s*def\s+\w+', line):
                func_name = re.search(r'def\s+(\w+)', line).group(1)
                
                # Check for common issues
                if 'pass' in line and i + 1 < len(lines) and 'pass' in lines[i + 1]:
                    self.all_issues['dead_code'].append({
                        'file': file_path,
                        'function': func_name,
                        'line': i + 1,
                        'issue': 'Empty function with only pass statement',
                        'severity': 'low'
                    })
                
                # Check for undefined variables (simplified)
                func_content = []
                indent_level = len(line) - len(line.lstrip())
                j = i + 1
                while j < len(lines) and (lines[j].strip() == '' or len(lines[j]) - len(lines[j].lstrip()) > indent_level):
                    func_content.append(lines[j])
                    j += 1
                
                func_text = '\n'.join(func_content)
                if 'undefined' in func_text.lower() or 'fixme' in func_text.lower():
                    self.all_issues['broken_functions'].append({
                        'file': file_path,
                        'function': func_name,
                        'line': i + 1,
                        'issue': 'Function contains FIXME or undefined references',
                        'severity': 'medium'
                    })
    
    def _detect_routes(self, file_path, content):
        """Detect and validate route definitions"""
        route_patterns = re.findall(r'@\w*\.route\(["\']([^"\']+)["\']([^)]*)\)', content)
        
        for pattern, options in route_patterns:
            route_info = {
                'file': file_path,
                'pattern': pattern,
                'options': options
            }
            
            if pattern in self.route_registry:
                self.all_issues['route_problems'].append({
                    'issue': 'Duplicate route pattern',
                    'pattern': pattern,
                    'files': [self.route_registry[pattern]['file'], file_path],
                    'severity': 'medium'
                })
            else:
                self.route_registry[pattern] = route_info
                
            # Check for common route issues
            if '<' in pattern and '>' in pattern:
                # Variable routes - check for proper validation
                if 'int:' not in pattern and 'string:' not in pattern and 'uuid:' not in pattern:
                    self.all_issues['route_problems'].append({
                        'file': file_path,
                        'pattern': pattern,
                        'issue': 'Route parameter without type specification',
                        'severity': 'low'
                    })
    
    def _detect_models(self, file_path, content):
        """Detect and validate database models"""
        model_classes = re.findall(r'class\s+(\w+)\s*\([^)]*db\.Model[^)]*\)', content)
        
        for model_name in model_classes:
            if model_name in self.model_registry:
                self.all_issues['database_issues'].append({
                    'issue': 'Duplicate model definition',
                    'model': model_name,
                    'files': [self.model_registry[model_name], file_path],
                    'severity': 'high'
                })
            else:
                self.model_registry[model_name] = file_path
                
            # Check for common model issues
            if 'db.Column' not in content:
                self.all_issues['database_issues'].append({
                    'file': file_path,
                    'model': model_name,
                    'issue': 'Model class without db.Column definitions',
                    'severity': 'medium'
                })
    
    def _check_security_issues(self, file_path, content):
        """Check for security vulnerabilities"""
        # Hardcoded secrets
        secret_patterns = [
            r'["\'][a-f0-9]{32,}["\']',  # Hex strings (potential keys)
            r'password\s*=\s*["\'][^"\']+["\']',  # Hardcoded passwords
            r'secret\s*=\s*["\'][^"\']+["\']',  # Hardcoded secrets
            r'api_key\s*=\s*["\'][^"\']+["\']',  # Hardcoded API keys
        ]
        
        for pattern in secret_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                if 'environ' not in match.group() and 'get(' not in match.group():
                    self.all_issues['security_vulnerabilities'].append({
                        'file': file_path,
                        'issue': 'Potential hardcoded secret',
                        'pattern': match.group()[:50] + '...',
                        'severity': 'high'
                    })
        
        # SQL injection risks
        if re.search(r'\.execute\s*\([^)]*%[^)]*\)', content):
            self.all_issues['security_vulnerabilities'].append({
                'file': file_path,
                'issue': 'Potential SQL injection vulnerability (string formatting in execute)',
                'severity': 'high'
            })
        
        # XSS risks
        if 'render_template_string' in content and 'escape' not in content:
            self.all_issues['security_vulnerabilities'].append({
                'file': file_path,
                'issue': 'render_template_string without escaping (XSS risk)',
                'severity': 'medium'
            })
    
    def _check_performance_issues(self, file_path, content):
        """Check for performance issues"""
        # Large loops
        if re.search(r'for\s+\w+\s+in\s+range\s*\(\s*\d{4,}', content):
            self.all_issues['performance_issues'].append({
                'file': file_path,
                'issue': 'Large range loop (potential performance issue)',
                'severity': 'medium'
            })
        
        # Inefficient database queries
        if '.all()' in content and 'limit' not in content:
            self.all_issues['performance_issues'].append({
                'file': file_path,
                'issue': 'Database query without limit (potential memory issue)',
                'severity': 'medium'
            })
        
        # File size check
        file_size = os.path.getsize(file_path)
        if file_size > 100000:  # 100KB
            line_count = len(content.split('\n'))
            self.all_issues['performance_issues'].append({
                'file': file_path,
                'issue': f'Large file ({file_size:,} bytes, {line_count:,} lines)',
                'severity': 'low'
            })
    
    def _detect_dead_code(self, file_path, content):
        """Detect potentially dead or unused code"""
        # Functions that are never called
        function_names = re.findall(r'def\s+(\w+)', content)
        for func_name in function_names:
            if func_name.startswith('_'):  # Private functions
                continue
                
            # Check if function is called anywhere in the file
            if content.count(func_name) == 1:  # Only the definition
                self.all_issues['dead_code'].append({
                    'file': file_path,
                    'function': func_name,
                    'issue': 'Function defined but never called in file',
                    'severity': 'low'
                })
        
        # Commented code blocks
        comment_lines = [line for line in content.split('\n') if line.strip().startswith('#')]
        if len(comment_lines) > 20:
            commented_code = [line for line in comment_lines if any(keyword in line for keyword in ['def ', 'class ', 'import ', 'from '])]
            if len(commented_code) > 5:
                self.all_issues['dead_code'].append({
                    'file': file_path,
                    'issue': f'Large amount of commented code ({len(commented_code)} lines)',
                    'severity': 'low'
                })
    
    def _scan_configuration_files(self):
        """Scan configuration files for issues"""
        print("⚙️ Scanning configuration files...")
        
        config_files = [
            'pyproject.toml', 'requirements.txt', 'setup.py', 'replit.toml',
            'config/app_config.py', 'database.py', 'app.py', 'main.py'
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                self._analyze_config_file(config_file)
    
    def _analyze_config_file(self, file_path):
        """Analyze a specific configuration file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            if file_path == 'pyproject.toml':
                self._check_pyproject_toml(content)
            elif file_path == 'replit.toml':
                self._check_replit_toml(content)
            elif file_path.endswith('.py'):
                self._check_python_config(file_path, content)
                
        except Exception as e:
            self.all_issues['configuration_issues'].append({
                'file': file_path,
                'error': f"Failed to read config file: {str(e)}",
                'severity': 'medium'
            })
    
    def _check_pyproject_toml(self, content):
        """Check pyproject.toml for issues"""
        try:
            import tomllib
            config = tomllib.loads(content)
            
            # Check for missing required fields
            required_fields = ['name', 'version', 'dependencies']
            for field in required_fields:
                if field not in config.get('project', {}):
                    self.all_issues['configuration_issues'].append({
                        'file': 'pyproject.toml',
                        'issue': f'Missing required field: project.{field}',
                        'severity': 'medium'
                    })
            
            # Check dependencies
            deps = config.get('project', {}).get('dependencies', [])
            if 'flask-socketio' not in str(deps):
                self.all_issues['missing_dependencies'].append({
                    'dependency': 'flask-socketio',
                    'required_for': 'Real-time chat functionality',
                    'severity': 'critical'
                })
                
        except Exception as e:
            self.all_issues['configuration_issues'].append({
                'file': 'pyproject.toml',
                'error': f"TOML parsing error: {str(e)}",
                'severity': 'high'
            })
    
    def _check_replit_toml(self, content):
        """Check replit.toml for deployment issues"""
        if 'run =' not in content:
            self.all_issues['deployment_blockers'].append({
                'file': 'replit.toml',
                'issue': 'Missing run command',
                'severity': 'high'
            })
        
        if 'modules =' not in content and 'language =' not in content:
            self.all_issues['deployment_blockers'].append({
                'file': 'replit.toml',
                'issue': 'Missing language or modules specification',
                'severity': 'medium'
            })
    
    def _check_python_config(self, file_path, content):
        """Check Python configuration files"""
        # Check for hardcoded values
        if 'localhost' in content and file_path not in ['app.py']:
            self.all_issues['configuration_issues'].append({
                'file': file_path,
                'issue': 'Hardcoded localhost (may cause deployment issues)',
                'severity': 'low'
            })
        
        # Check for missing environment variable handling
        if 'os.environ' in content and 'get(' not in content:
            self.all_issues['configuration_issues'].append({
                'file': file_path,
                'issue': 'Environment variable access without fallback',
                'severity': 'medium'
            })
    
    def _scan_templates(self):
        """Scan HTML templates for issues"""
        print("🌐 Scanning templates...")
        
        template_dir = 'templates'
        if os.path.exists(template_dir):
            for root, dirs, files in os.walk(template_dir):
                for file in files:
                    if file.endswith(('.html', '.htm')):
                        file_path = os.path.join(root, file)
                        self._analyze_template(file_path)
    
    def _analyze_template(self, file_path):
        """Analyze HTML template for issues"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Check for accessibility issues
            if '<img' in content and 'alt=' not in content:
                self.all_issues['accessibility_issues'].append({
                    'file': file_path,
                    'issue': 'Images without alt text',
                    'severity': 'medium'
                })
            
            # Check for security issues
            if '{{ request.' in content and '|safe' not in content:
                self.all_issues['security_vulnerabilities'].append({
                    'file': file_path,
                    'issue': 'Direct request object output (potential XSS)',
                    'severity': 'medium'
                })
            
            # Check for performance issues
            if content.count('<script') > 5:
                self.all_issues['performance_issues'].append({
                    'file': file_path,
                    'issue': 'Multiple script tags (consider bundling)',
                    'severity': 'low'
                })
                
        except Exception as e:
            self.all_issues['template_issues'].append({
                'file': file_path,
                'error': f"Template analysis failed: {str(e)}",
                'severity': 'low'
            })
    
    def _scan_static_assets(self):
        """Scan static assets for issues"""
        print("📦 Scanning static assets...")
        
        static_dir = 'static'
        if os.path.exists(static_dir):
            for root, dirs, files in os.walk(static_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    
                    # Check for large assets
                    if file_size > 1000000:  # 1MB
                        self.all_issues['performance_issues'].append({
                            'file': file_path,
                            'issue': f'Large static asset ({file_size:,} bytes)',
                            'severity': 'medium'
                        })
                    
                    # Check for missing minification
                    if file.endswith('.js') and not file.endswith('.min.js'):
                        if file_size > 10000:  # 10KB
                            self.all_issues['performance_issues'].append({
                                'file': file_path,
                                'issue': 'Large JavaScript file not minified',
                                'severity': 'low'
                            })
    
    def _scan_database_structure(self):
        """Scan database structure for issues"""
        print("🗄️ Scanning database structure...")
        
        # Check for migration files
        if not os.path.exists('migrations'):
            self.all_issues['database_issues'].append({
                'issue': 'No migrations directory found',
                'severity': 'medium'
            })
        
        # Check database configuration
        if os.path.exists('database.py'):
            with open('database.py', 'r') as f:
                content = f.read()
                if 'create_all' in content and 'if' not in content:
                    self.all_issues['database_issues'].append({
                        'file': 'database.py',
                        'issue': 'Unconditional create_all() call (development only)',
                        'severity': 'low'
                    })
    
    def _analyze_dependencies(self):
        """Analyze dependency tree for issues"""
        print("📦 Analyzing dependencies...")
        
        # Try to check installed packages
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                                  capture_output=True, text=True, timeout=120)
            installed_packages = result.stdout
            
            # Check for missing critical packages
            critical_packages = ['flask', 'sqlalchemy', 'werkzeug']
            for package in critical_packages:
                if package not in installed_packages.lower():
                    self.all_issues['missing_dependencies'].append({
                        'dependency': package,
                        'severity': 'critical'
                    })
                    
        except Exception as e:
            self.all_issues['dependency_issues'] = [f"Failed to check dependencies: {str(e)}"]
    
    def _test_imports(self):
        """Test all imports to identify failures"""
        print("🔗 Testing imports...")
        
        # Test critical imports
        critical_imports = [
            'flask',
            'flask_sqlalchemy',
            'werkzeug',
            'authlib',
            'flask_login',
            'flask_session',
            'flask_socketio',
            'psycopg2',
            'requests',
            'psutil',
            'numpy',
            'PyJWT'
        ]
        
        for module in critical_imports:
            try:
                __import__(module)
            except ImportError as e:
                self.all_issues['import_failures'].append({
                    'module': module,
                    'error': str(e),
                    'severity': 'high' if module in ['flask', 'flask_sqlalchemy'] else 'medium'
                })
    
    def _check_routes(self):
        """Check route functionality"""
        print("🛣️ Checking routes...")
        
        # Test route imports
        route_files = []
        if os.path.exists('routes'):
            for file in os.listdir('routes'):
                if file.endswith('.py') and file != '__init__.py':
                    route_files.append(f"routes.{file[:-3]}")
        
        for route_module in route_files:
            try:
                __import__(route_module)
            except Exception as e:
                self.all_issues['route_problems'].append({
                    'module': route_module,
                    'error': str(e),
                    'severity': 'medium'
                })
    
    def _validate_models(self):
        """Validate database models"""
        print("🗄️ Validating models...")
        
        # Check model imports
        model_files = []
        if os.path.exists('models'):
            for file in os.listdir('models'):
                if file.endswith('.py') and file != '__init__.py':
                    model_files.append(f"models.{file[:-3]}")
        
        for model_module in model_files:
            try:
                __import__(model_module)
            except Exception as e:
                self.all_issues['database_issues'].append({
                    'module': model_module,
                    'error': str(e),
                    'severity': 'medium'
                })
    
    def _security_audit(self):
        """Comprehensive security audit"""
        print("🔒 Security audit...")
        
        # Check for .env files in version control
        if os.path.exists('.env'):
            self.all_issues['security_vulnerabilities'].append({
                'file': '.env',
                'issue': 'Environment file should not be in version control',
                'severity': 'high'
            })
        
        # Check for exposed debug mode
        for file in ['app.py', 'main.py']:
            if os.path.exists(file):
                with open(file, 'r') as f:
                    content = f.read()
                    if 'debug=True' in content and 'production' not in content.lower():
                        self.all_issues['security_vulnerabilities'].append({
                            'file': file,
                            'issue': 'Debug mode enabled in production code',
                            'severity': 'medium'
                        })
    
    def _performance_analysis(self):
        """Performance analysis"""
        print("⚡ Performance analysis...")
        
        # Skip duplicate code analysis for performance - focus on file sizes
        large_files = []
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'archive']]
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        if size > 50000:  # Files > 50KB
                            large_files.append((file_path, size))
                    except Exception:
                        pass
        
        for file_path, size in large_files:
            self.all_issues['performance_issues'].append({
                'file': file_path,
                'issue': f'Large file ({size:,} bytes)',
                'severity': 'medium'
            })
    
    def _calculate_similarity(self, text1, text2):
        """Calculate text similarity (simplified)"""
        # Skip similarity check for performance - focus on critical issues
        return 0.0
    
    def _deployment_readiness(self):
        """Check deployment readiness"""
        print("🚀 Checking deployment readiness...")
        
        # Check for required files
        required_files = ['main.py', 'app.py', 'pyproject.toml', 'replit.toml']
        for file in required_files:
            if not os.path.exists(file):
                self.all_issues['deployment_blockers'].append({
                    'file': file,
                    'issue': 'Required deployment file missing',
                    'severity': 'high'
                })
        
        # Check for proper port configuration
        if os.path.exists('main.py'):
            with open('main.py', 'r') as f:
                content = f.read()
                if 'PORT' not in content and '5000' in content:
                    self.all_issues['deployment_blockers'].append({
                        'file': 'main.py',
                        'issue': 'Hardcoded port instead of environment variable',
                        'severity': 'medium'
                    })
    
    def _accessibility_check(self):
        """Check accessibility compliance"""
        print("♿ Checking accessibility...")
        
        # Check templates for accessibility
        if os.path.exists('templates'):
            for root, dirs, files in os.walk('templates'):
                for file in files:
                    if file.endswith('.html'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        # Check for missing ARIA labels
                        if '<button' in content and 'aria-label' not in content:
                            self.all_issues['accessibility_issues'].append({
                                'file': file_path,
                                'issue': 'Buttons without ARIA labels',
                                'severity': 'low'
                            })
    
    def generate_complete_report(self):
        """Generate comprehensive report of all issues"""
        total_issues = sum(len(issues) for issues in self.all_issues.values())
        
        # Create detailed report
        report = f"""# COMPLETE ISSUE ANALYSIS - NOUS Personal Assistant

**Generated:** {datetime.now().isoformat()}
**Total Issues Found:** {total_issues:,}

## CRITICAL ISSUES (Fix Immediately)

### Syntax Errors ({len(self.all_issues['syntax_errors'])})
"""
        
        for issue in self.all_issues['syntax_errors']:
            report += f"- **{issue['file']}** Line {issue['line']}: {issue['error']}\n"
        
        report += f"""
### Import Failures ({len(self.all_issues['import_failures'])})
"""
        
        for issue in self.all_issues['import_failures']:
            report += f"- **{issue['file']}**: Cannot import '{issue.get('module', 'unknown')}'\n"
        
        report += f"""
### Missing Dependencies ({len(self.all_issues['missing_dependencies'])})
"""
        
        for issue in self.all_issues['missing_dependencies']:
            report += f"- **{issue['dependency']}**: {issue.get('required_for', 'Critical functionality')}\n"
        
        # Continue with all other categories
        for category, issues in self.all_issues.items():
            if category not in ['syntax_errors', 'import_failures', 'missing_dependencies'] and issues:
                report += f"""
### {category.replace('_', ' ').title()} ({len(issues)})
"""
                for issue in issues[:10]:  # Limit to first 10 per category
                    if isinstance(issue, dict):
                        if 'file' in issue:
                            report += f"- **{issue['file']}**: {issue.get('issue', issue.get('error', 'Unknown issue'))}\n"
                        else:
                            report += f"- {issue.get('issue', issue.get('error', str(issue)))}\n"
                    else:
                        report += f"- {str(issue)}\n"
                
                if len(issues) > 10:
                    report += f"... and {len(issues) - 10} more issues\n"
        
        report += f"""
## SUMMARY BY SEVERITY

- **Critical Issues:** {len(self.all_issues['critical_errors']) + len(self.all_issues['syntax_errors'])}
- **High Priority:** {len(self.all_issues['import_failures']) + len(self.all_issues['missing_dependencies'])}
- **Medium Priority:** {len(self.all_issues['configuration_issues']) + len(self.all_issues['route_problems'])}
- **Low Priority:** {len(self.all_issues['performance_issues']) + len(self.all_issues['dead_code'])}

## RECOMMENDATIONS

1. **Immediate Action Required:**
   - Fix all syntax errors preventing application startup
   - Install missing dependencies (especially flask-socketio)
   - Resolve import failures in critical modules

2. **Short Term (1-2 weeks):**
   - Complete broken route implementations
   - Fix database model issues
   - Address security vulnerabilities

3. **Long Term (1+ months):**
   - Performance optimization
   - Code cleanup and dead code removal
   - Accessibility improvements

---

**Analysis completed successfully. Address critical issues first for system stability.**
"""
        
        # Save report
        with open('COMPLETE_ISSUE_REPORT.md', 'w') as f:
            f.write(report)
        
        # Save detailed JSON
        with open('complete_issues.json', 'w') as f:
            json.dump(self.all_issues, f, indent=2, default=str)
        
        print(f"✅ Complete analysis finished. Found {total_issues:,} total issues.")
        print("📄 Reports saved:")
        print("   - COMPLETE_ISSUE_REPORT.md")
        print("   - complete_issues.json")
        
        return self.all_issues

def main():
    """Run complete issue scan"""
    scanner = CompleteIssueScanner()
    scanner.scan_everything()
    scanner.generate_complete_report()

if __name__ == "__main__":
    main()