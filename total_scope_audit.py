#!/usr/bin/env python3
"""
Total Scope Codebase Audit
Comprehensive analysis of every aspect of the NOUS codebase
"""
import os
import sys
import json
import ast
import re
import subprocess
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
import traceback

class TotalScopeAuditor:
    def __init__(self):
        self.root_path = Path('.')
        self.audit_results = {
            'timestamp': datetime.now().isoformat(),
            'file_system': {},
            'dependencies': {},
            'routes': {},
            'models': {},
            'imports': {},
            'code_quality': {},
            'security': {},
            'performance': {},
            'optimization_opportunities': [],
            'critical_issues': [],
            'statistics': {}
        }
        
    def execute_total_audit(self):
        """Execute comprehensive audit of everything"""
        print("🎯 TOTAL SCOPE CODEBASE AUDIT")
        print("=" * 50)
        
        try:
            # Core Infrastructure
            self._audit_file_system()
            self._audit_dependencies()
            self._audit_configuration()
            
            # Code Analysis
            self._audit_python_files()
            self._audit_routes()
            self._audit_models()
            self._audit_imports()
            
            # Quality & Performance
            self._audit_code_quality()
            self._audit_security()
            self._audit_performance()
            
            # Templates & Static Assets
            self._audit_templates()
            self._audit_static_assets()
            
            # Generate Final Analysis
            self._compile_statistics()
            self._identify_optimizations()
            self._rank_critical_issues()
            
            print("✅ Total scope audit completed successfully")
            return self.audit_results
            
        except Exception as e:
            print(f"❌ Audit failed: {e}")
            traceback.print_exc()
            return self.audit_results
    
    def _audit_file_system(self):
        """Complete file system analysis"""
        print("📁 Auditing file system structure...")
        
        fs_data = {
            'total_files': 0,
            'total_size_bytes': 0,
            'directories': {},
            'file_types': defaultdict(int),
            'large_files': [],
            'empty_files': [],
            'cache_files': [],
            'log_files': [],
            'backup_files': [],
            'duplicate_names': defaultdict(list)
        }
        
        for item in self.root_path.rglob('*'):
            if not item.is_file():
                continue
                
            size = item.stat().st_size
            fs_data['total_files'] += 1
            fs_data['total_size_bytes'] += size
            fs_data['file_types'][item.suffix or 'no_extension'] += 1
            fs_data['duplicate_names'][item.name].append(str(item))
            
            # Categorize files
            if size > 1024 * 1024:  # >1MB
                fs_data['large_files'].append({
                    'path': str(item),
                    'size_mb': size / (1024 * 1024)
                })
            
            if size == 0:
                fs_data['empty_files'].append(str(item))
            
            if any(cache in str(item) for cache in ['__pycache__', 'flask_session', '.pytest_cache', 'cache']):
                fs_data['cache_files'].append(str(item))
            
            if item.suffix == '.log':
                fs_data['log_files'].append({
                    'path': str(item),
                    'size_mb': size / (1024 * 1024)
                })
            
            if any(backup in item.name.lower() for backup in ['backup', 'bak', 'old', 'archive']):
                fs_data['backup_files'].append(str(item))
        
        # Directory analysis
        for dir_path in self.root_path.iterdir():
            if dir_path.is_dir() and not dir_path.name.startswith('.'):
                file_count = len(list(dir_path.rglob('*')))
                fs_data['directories'][dir_path.name] = file_count
        
        # Find actual duplicates
        fs_data['potential_duplicates'] = {
            name: paths for name, paths in fs_data['duplicate_names'].items()
            if len(paths) > 1 and not name.startswith('__')
        }
        
        self.audit_results['file_system'] = fs_data
    
    def _audit_dependencies(self):
        """Complete dependency analysis"""
        print("📦 Auditing dependencies...")
        
        dep_data = {
            'pyproject_analysis': {},
            'requirements_files': [],
            'dependency_conflicts': [],
            'unused_dependencies': [],
            'security_vulnerabilities': [],
            'version_issues': []
        }
        
        # Analyze pyproject.toml
        pyproject_path = Path('pyproject.toml')
        if pyproject_path.exists():
            content = pyproject_path.read_text()
            
            # Extract dependencies
            dependencies = re.findall(r'"([^"]+)"', content)
            dep_data['pyproject_analysis'] = {
                'total_dependencies': len(dependencies),
                'dependencies': dependencies,
                'file_size': len(content),
                'line_count': len(content.splitlines())
            }
            
            # Check for duplicates
            dep_counter = Counter(dep.split('>=')[0].split('==')[0].split('~=')[0] for dep in dependencies)
            duplicates = {dep: count for dep, count in dep_counter.items() if count > 1}
            if duplicates:
                dep_data['dependency_conflicts'].extend([f"{dep} appears {count} times" for dep, count in duplicates.items()])
        
        # Find all requirements files
        for req_file in self.root_path.glob('requirements*.txt'):
            dep_data['requirements_files'].append({
                'file': str(req_file),
                'size': req_file.stat().st_size,
                'exists': True
            })
        
        self.audit_results['dependencies'] = dep_data
    
    def _audit_configuration(self):
        """Audit configuration files"""
        print("⚙️ Auditing configuration...")
        
        config_files = [
            'replit.toml', 'pyproject.toml', 'main.py', 'app.py',
            'gunicorn.conf.py', 'setup.py', 'MANIFEST.in'
        ]
        
        config_data = {}
        for config_file in config_files:
            config_path = Path(config_file)
            if config_path.exists():
                config_data[config_file] = {
                    'exists': True,
                    'size': config_path.stat().st_size,
                    'lines': len(config_path.read_text().splitlines())
                }
            else:
                config_data[config_file] = {'exists': False}
        
        self.audit_results['configuration'] = config_data
    
    def _audit_python_files(self):
        """Comprehensive Python file analysis"""
        print("🐍 Auditing Python files...")
        
        py_data = {
            'total_python_files': 0,
            'total_lines': 0,
            'functions': [],
            'classes': [],
            'syntax_errors': [],
            'long_files': [],
            'complex_files': []
        }
        
        for py_file in self.root_path.rglob('*.py'):
            py_data['total_python_files'] += 1
            
            try:
                content = py_file.read_text(encoding='utf-8')
                lines = content.splitlines()
                py_data['total_lines'] += len(lines)
                
                # Long files analysis
                if len(lines) > 500:
                    py_data['long_files'].append({
                        'file': str(py_file),
                        'lines': len(lines)
                    })
                
                # Parse AST for functions and classes
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            py_data['functions'].append({
                                'name': node.name,
                                'file': str(py_file),
                                'line': node.lineno
                            })
                        elif isinstance(node, ast.ClassDef):
                            py_data['classes'].append({
                                'name': node.name,
                                'file': str(py_file),
                                'line': node.lineno
                            })
                except SyntaxError as e:
                    py_data['syntax_errors'].append({
                        'file': str(py_file),
                        'error': str(e)
                    })
                    
            except Exception as e:
                py_data['syntax_errors'].append({
                    'file': str(py_file),
                    'error': f"Read error: {e}"
                })
        
        self.audit_results['python_files'] = py_data
    
    def _audit_routes(self):
        """Complete route analysis"""
        print("🛣️ Auditing routes...")
        
        route_data = {
            'route_files': [],
            'blueprints': [],
            'total_routes': 0,
            'route_patterns': [],
            'duplicate_routes': [],
            'missing_routes': []
        }
        
        routes_dir = Path('routes')
        if routes_dir.exists():
            for py_file in routes_dir.glob('*.py'):
                if py_file.name == '__init__.py':
                    continue
                
                route_file_data = {
                    'file': py_file.name,
                    'size': py_file.stat().st_size,
                    'routes': [],
                    'blueprints': []
                }
                
                try:
                    content = py_file.read_text(encoding='utf-8')
                    
                    # Find route decorators
                    routes = re.findall(r'@\w+\.route\([\'"]([^\'"]+)[\'"]', content)
                    route_file_data['routes'] = routes
                    route_data['route_patterns'].extend(routes)
                    route_data['total_routes'] += len(routes)
                    
                    # Find blueprints
                    blueprints = re.findall(r'(\w+)\s*=\s*Blueprint\([\'"]([^\'"]+)[\'"]', content)
                    route_file_data['blueprints'] = blueprints
                    route_data['blueprints'].extend(blueprints)
                    
                except Exception as e:
                    route_data['missing_routes'].append({
                        'file': py_file.name,
                        'error': str(e)
                    })
                
                route_data['route_files'].append(route_file_data)
        
        # Find duplicate routes
        route_counter = Counter(route_data['route_patterns'])
        route_data['duplicate_routes'] = [
            (route, count) for route, count in route_counter.items() if count > 1
        ]
        
        self.audit_results['routes'] = route_data
    
    def _audit_models(self):
        """Audit database models"""
        print("🗃️ Auditing models...")
        
        model_data = {
            'model_files': [],
            'total_models': 0,
            'models': [],
            'relationships': [],
            'missing_models': []
        }
        
        models_dir = Path('models')
        if models_dir.exists():
            for py_file in models_dir.glob('*.py'):
                if py_file.name == '__init__.py':
                    continue
                
                try:
                    content = py_file.read_text(encoding='utf-8')
                    
                    # Find model classes
                    models = re.findall(r'class\s+(\w+)\s*\([^)]*db\.Model', content)
                    model_data['models'].extend([{
                        'name': model,
                        'file': py_file.name
                    } for model in models])
                    model_data['total_models'] += len(models)
                    
                    # Find relationships
                    relationships = re.findall(r'(\w+)\s*=\s*db\.relationship', content)
                    model_data['relationships'].extend(relationships)
                    
                    model_data['model_files'].append({
                        'file': py_file.name,
                        'models': len(models),
                        'relationships': len(relationships)
                    })
                    
                except Exception as e:
                    model_data['missing_models'].append({
                        'file': py_file.name,
                        'error': str(e)
                    })
        
        self.audit_results['models'] = model_data
    
    def _audit_imports(self):
        """Audit import statements"""
        print("📥 Auditing imports...")
        
        import_data = {
            'import_errors': [],
            'circular_imports': [],
            'unused_imports': [],
            'heavy_imports': [],
            'relative_imports': []
        }
        
        for py_file in self.root_path.rglob('*.py'):
            try:
                content = py_file.read_text(encoding='utf-8')
                
                # Check for heavy imports
                heavy_modules = ['tensorflow', 'torch', 'cv2', 'pandas', 'numpy']
                for module in heavy_modules:
                    if f'import {module}' in content:
                        import_data['heavy_imports'].append({
                            'file': str(py_file),
                            'module': module
                        })
                
                # Check for relative imports
                if 'from .' in content or 'from ..' in content:
                    import_data['relative_imports'].append(str(py_file))
                
                # Check for potential circular imports
                if 'from app import' in content and 'app.py' not in str(py_file):
                    import_data['circular_imports'].append(str(py_file))
                    
            except Exception as e:
                import_data['import_errors'].append({
                    'file': str(py_file),
                    'error': str(e)
                })
        
        self.audit_results['imports'] = import_data
    
    def _audit_code_quality(self):
        """Audit code quality metrics"""
        print("🔍 Auditing code quality...")
        
        quality_data = {
            'todo_comments': [],
            'hardcoded_values': [],
            'print_statements': [],
            'long_lines': [],
            'complexity_issues': []
        }
        
        for py_file in self.root_path.rglob('*.py'):
            try:
                content = py_file.read_text(encoding='utf-8')
                lines = content.splitlines()
                
                for i, line in enumerate(lines, 1):
                    # TODO comments
                    if any(keyword in line.upper() for keyword in ['TODO', 'FIXME', 'HACK', 'XXX']):
                        quality_data['todo_comments'].append({
                            'file': str(py_file),
                            'line': i,
                            'text': line.strip()
                        })
                    
                    # Print statements (potential debug code)
                    if 'print(' in line and not line.strip().startswith('#'):
                        quality_data['print_statements'].append({
                            'file': str(py_file),
                            'line': i
                        })
                    
                    # Long lines
                    if len(line) > 120:
                        quality_data['long_lines'].append({
                            'file': str(py_file),
                            'line': i,
                            'length': len(line)
                        })
                
                # Hardcoded values
                if re.search(r'localhost|127\.0\.0\.1|:\d{4,5}', content):
                    quality_data['hardcoded_values'].append(str(py_file))
                    
            except Exception:
                continue
        
        self.audit_results['code_quality'] = quality_data
    
    def _audit_security(self):
        """Audit security issues"""
        print("🔒 Auditing security...")
        
        security_data = {
            'hardcoded_secrets': [],
            'sql_injection_risks': [],
            'xss_risks': [],
            'insecure_patterns': []
        }
        
        sensitive_patterns = [
            (r'password\s*=\s*[\'"][^\'"]+[\'"]', 'hardcoded_password'),
            (r'secret\s*=\s*[\'"][^\'"]+[\'"]', 'hardcoded_secret'),
            (r'api_key\s*=\s*[\'"][^\'"]+[\'"]', 'hardcoded_api_key'),
            (r'\.execute\([\'"].*%.*[\'"]', 'sql_injection_risk'),
            (r'render_template_string', 'template_injection_risk')
        ]
        
        for py_file in self.root_path.rglob('*.py'):
            try:
                content = py_file.read_text(encoding='utf-8')
                
                for pattern, issue_type in sensitive_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        security_data['insecure_patterns'].append({
                            'file': str(py_file),
                            'issue': issue_type,
                            'matches': len(matches)
                        })
                        
            except Exception:
                continue
        
        self.audit_results['security'] = security_data
    
    def _audit_performance(self):
        """Audit performance issues"""
        print("⚡ Auditing performance...")
        
        perf_data = {
            'inefficient_patterns': [],
            'database_issues': [],
            'memory_issues': [],
            'slow_operations': []
        }
        
        performance_patterns = [
            (r'\.query\.all\(\)', 'potential_n_plus_1'),
            (r'for.*in.*\.query\.', 'loop_with_query'),
            (r'time\.sleep\(', 'blocking_sleep'),
            (r'\.read\(\)', 'unbounded_read')
        ]
        
        for py_file in self.root_path.rglob('*.py'):
            try:
                content = py_file.read_text(encoding='utf-8')
                
                for pattern, issue_type in performance_patterns:
                    if re.search(pattern, content):
                        perf_data['inefficient_patterns'].append({
                            'file': str(py_file),
                            'issue': issue_type
                        })
                        
            except Exception:
                continue
        
        self.audit_results['performance'] = perf_data
    
    def _audit_templates(self):
        """Audit HTML templates"""
        print("📄 Auditing templates...")
        
        template_data = {
            'total_templates': 0,
            'template_files': [],
            'missing_templates': [],
            'unused_templates': []
        }
        
        templates_dir = Path('templates')
        if templates_dir.exists():
            for template_file in templates_dir.rglob('*.html'):
                template_data['total_templates'] += 1
                template_data['template_files'].append({
                    'file': str(template_file),
                    'size': template_file.stat().st_size
                })
        
        self.audit_results['templates'] = template_data
    
    def _audit_static_assets(self):
        """Audit static assets"""
        print("🎨 Auditing static assets...")
        
        static_data = {
            'css_files': [],
            'js_files': [],
            'image_files': [],
            'other_files': [],
            'total_size_mb': 0
        }
        
        static_dir = Path('static')
        if static_dir.exists():
            for asset_file in static_dir.rglob('*'):
                if not asset_file.is_file():
                    continue
                
                size = asset_file.stat().st_size
                static_data['total_size_mb'] += size / (1024 * 1024)
                
                if asset_file.suffix == '.css':
                    static_data['css_files'].append(str(asset_file))
                elif asset_file.suffix == '.js':
                    static_data['js_files'].append(str(asset_file))
                elif asset_file.suffix in ['.jpg', '.jpeg', '.png', '.gif', '.svg']:
                    static_data['image_files'].append(str(asset_file))
                else:
                    static_data['other_files'].append(str(asset_file))
        
        self.audit_results['static_assets'] = static_data
    
    def _compile_statistics(self):
        """Compile overall statistics"""
        print("📊 Compiling statistics...")
        
        fs = self.audit_results['file_system']
        py = self.audit_results.get('python_files', {})
        routes = self.audit_results['routes']
        models = self.audit_results['models']
        
        self.audit_results['statistics'] = {
            'total_files': fs['total_files'],
            'total_size_mb': fs['total_size_bytes'] / (1024 * 1024),
            'python_files': py.get('total_python_files', 0),
            'total_lines': py.get('total_lines', 0),
            'total_functions': len(py.get('functions', [])),
            'total_classes': len(py.get('classes', [])),
            'total_routes': routes['total_routes'],
            'total_blueprints': len(routes['blueprints']),
            'total_models': models['total_models'],
            'cache_files': len(fs['cache_files']),
            'log_files': len(fs['log_files']),
            'backup_files': len(fs['backup_files'])
        }
    
    def _identify_optimizations(self):
        """Identify optimization opportunities"""
        print("💡 Identifying optimizations...")
        
        optimizations = []
        
        # File system optimizations
        fs = self.audit_results['file_system']
        if fs['cache_files']:
            optimizations.append({
                'category': 'cleanup',
                'priority': 'high',
                'title': 'Remove cache files',
                'description': f"Remove {len(fs['cache_files'])} cache files",
                'impact': 'reduced storage, faster builds',
                'files_affected': len(fs['cache_files'])
            })
        
        if fs['empty_files']:
            optimizations.append({
                'category': 'cleanup',
                'priority': 'medium',
                'title': 'Remove empty files',
                'description': f"Remove {len(fs['empty_files'])} empty files",
                'impact': 'cleaner codebase',
                'files_affected': len(fs['empty_files'])
            })
        
        if fs['backup_files']:
            optimizations.append({
                'category': 'cleanup',
                'priority': 'medium',
                'title': 'Archive backup files',
                'description': f"Archive {len(fs['backup_files'])} backup files",
                'impact': 'reduced storage',
                'files_affected': len(fs['backup_files'])
            })
        
        # Route optimizations
        routes = self.audit_results['routes']
        if len(routes['route_files']) > 15:
            optimizations.append({
                'category': 'consolidation',
                'priority': 'medium',
                'title': 'Consolidate route files',
                'description': f"Consider consolidating {len(routes['route_files'])} route files",
                'impact': 'better organization, faster imports',
                'files_affected': len(routes['route_files'])
            })
        
        # Code quality optimizations
        quality = self.audit_results['code_quality']
        if quality['print_statements']:
            optimizations.append({
                'category': 'code_quality',
                'priority': 'low',
                'title': 'Remove debug print statements',
                'description': f"Remove {len(quality['print_statements'])} print statements",
                'impact': 'cleaner code, better performance',
                'files_affected': len(set(item['file'] for item in quality['print_statements']))
            })
        
        # Dependencies
        deps = self.audit_results['dependencies']
        if deps['dependency_conflicts']:
            optimizations.append({
                'category': 'dependencies',
                'priority': 'high',
                'title': 'Fix dependency conflicts',
                'description': f"Resolve {len(deps['dependency_conflicts'])} dependency conflicts",
                'impact': 'stable builds, reduced conflicts',
                'files_affected': 1
            })
        
        self.audit_results['optimization_opportunities'] = optimizations
    
    def _rank_critical_issues(self):
        """Rank critical issues by severity"""
        print("🚨 Ranking critical issues...")
        
        critical_issues = []
        
        # Syntax errors
        py = self.audit_results.get('python_files', {})
        if py.get('syntax_errors'):
            critical_issues.append({
                'severity': 'critical',
                'category': 'syntax',
                'title': 'Python syntax errors',
                'description': f"{len(py['syntax_errors'])} files have syntax errors",
                'impact': 'application failure',
                'files_affected': [item['file'] for item in py['syntax_errors']]
            })
        
        # Security issues
        security = self.audit_results['security']
        if security['insecure_patterns']:
            critical_issues.append({
                'severity': 'high',
                'category': 'security',
                'title': 'Security vulnerabilities detected',
                'description': f"{len(security['insecure_patterns'])} potential security issues",
                'impact': 'security breach risk',
                'files_affected': [item['file'] for item in security['insecure_patterns']]
            })
        
        # Route conflicts
        routes = self.audit_results['routes']
        if routes['duplicate_routes']:
            critical_issues.append({
                'severity': 'medium',
                'category': 'routes',
                'title': 'Duplicate route definitions',
                'description': f"{len(routes['duplicate_routes'])} duplicate routes",
                'impact': 'routing conflicts',
                'routes_affected': routes['duplicate_routes']
            })
        
        self.audit_results['critical_issues'] = critical_issues
    
    def print_comprehensive_report(self):
        """Print comprehensive audit report"""
        print("\n" + "="*70)
        print("📊 TOTAL SCOPE AUDIT COMPREHENSIVE REPORT")
        print("="*70)
        
        stats = self.audit_results['statistics']
        
        print(f"\n📈 CODEBASE STATISTICS:")
        print(f"   Total Files: {stats['total_files']:,}")
        print(f"   Total Size: {stats['total_size_mb']:.1f}MB")
        print(f"   Python Files: {stats['python_files']:,}")
        print(f"   Lines of Code: {stats['total_lines']:,}")
        print(f"   Functions: {stats['total_functions']:,}")
        print(f"   Classes: {stats['total_classes']:,}")
        print(f"   Routes: {stats['total_routes']:,}")
        print(f"   Blueprints: {stats['total_blueprints']:,}")
        print(f"   Models: {stats['total_models']:,}")
        
        # Critical Issues
        critical = self.audit_results['critical_issues']
        print(f"\n🚨 CRITICAL ISSUES ({len(critical)}):")
        for issue in critical:
            print(f"   [{issue['severity'].upper()}] {issue['title']}")
            print(f"      {issue['description']}")
            print(f"      Impact: {issue['impact']}")
        
        # Optimization Opportunities
        optimizations = self.audit_results['optimization_opportunities']
        print(f"\n💡 OPTIMIZATION OPPORTUNITIES ({len(optimizations)}):")
        for opt in optimizations:
            print(f"   [{opt['priority'].upper()}] {opt['title']}")
            print(f"      {opt['description']}")
            print(f"      Impact: {opt['impact']}")
        
        # File System Breakdown
        fs = self.audit_results['file_system']
        print(f"\n📁 FILE SYSTEM BREAKDOWN:")
        print(f"   Cache Files: {len(fs['cache_files'])}")
        print(f"   Log Files: {len(fs['log_files'])}")
        print(f"   Backup Files: {len(fs['backup_files'])}")
        print(f"   Empty Files: {len(fs['empty_files'])}")
        print(f"   Large Files (>1MB): {len(fs['large_files'])}")
        
        return self.audit_results

def main():
    """Execute total scope audit"""
    auditor = TotalScopeAuditor()
    results = auditor.execute_total_audit()
    auditor.print_comprehensive_report()
    
    # Save detailed results
    with open('total_scope_audit_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Complete results saved to: total_scope_audit_results.json")
    print(f"⏱️ Audit completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return results

if __name__ == "__main__":
    main()