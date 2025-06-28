#!/usr/bin/env python3
"""
Comprehensive NOUS Codebase Analysis Report
Analyzes entire codebase for functionality, issues, and optimization opportunities
"""
import os
import sys
import json
import ast
import subprocess
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import importlib.util

class CodebaseAnalyzer:
    def __init__(self):
        self.report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {},
            'critical_issues': [],
            'medium_issues': [],
            'low_issues': [],
            'optimization_opportunities': [],
            'functionality_analysis': {},
            'dependency_analysis': {},
            'performance_issues': [],
            'security_issues': [],
            'recommendations': []
        }
        self.file_count = 0
        self.total_lines = 0
        
    def analyze_codebase(self):
        """Run comprehensive codebase analysis"""
        print("🔍 Starting comprehensive codebase analysis...")
        
        # Core analysis components
        self._analyze_file_structure()
        self._analyze_dependencies()
        self._analyze_imports()
        self._analyze_route_functionality()
        self._analyze_database_models()
        self._analyze_configuration()
        self._analyze_security()
        self._analyze_performance()
        self._test_application_startup()
        self._analyze_neglected_areas()
        
        # Generate summary
        self._generate_summary()
        
        return self.report
    
    def _analyze_file_structure(self):
        """Analyze file organization and structure"""
        print("📁 Analyzing file structure...")
        
        structure = defaultdict(list)
        for root, dirs, files in os.walk('.'):
            # Skip cache and hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    self.file_count += 1
                    file_path = os.path.join(root, file)
                    category = root.split('/')[1] if len(root.split('/')) > 1 else 'root'
                    structure[category].append(file_path)
                    
                    # Count lines
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = len(f.readlines())
                            self.total_lines += lines
                    except:
                        pass
        
        self.report['functionality_analysis']['file_structure'] = dict(structure)
        print(f"✅ Analyzed {self.file_count} Python files ({self.total_lines:,} lines)")
    
    def _analyze_dependencies(self):
        """Analyze dependency configuration and issues"""
        print("📦 Analyzing dependencies...")
        
        dep_analysis = {
            'pyproject_status': 'not_found',
            'critical_missing': [],
            'version_conflicts': [],
            'unused_dependencies': [],
            'security_vulnerabilities': []
        }
        
        # Check pyproject.toml
        if os.path.exists('pyproject.toml'):
            dep_analysis['pyproject_status'] = 'found'
            try:
                import tomllib
                with open('pyproject.toml', 'rb') as f:
                    config = tomllib.load(f)
                    deps = config.get('project', {}).get('dependencies', [])
                    optional_deps = config.get('project', {}).get('optional-dependencies', {})
                    
                    dep_analysis['core_dependencies'] = len(deps)
                    dep_analysis['optional_groups'] = len(optional_deps)
                    
                    # Check for common issues
                    if 'flask-socketio' not in str(deps):
                        dep_analysis['critical_missing'].append('flask-socketio - required for chat functionality')
                    
                    # Check for version conflicts
                    werkzeug_deps = [d for d in deps if 'werkzeug' in d.lower()]
                    if len(werkzeug_deps) > 1:
                        dep_analysis['version_conflicts'].append('Multiple werkzeug versions specified')
                        
            except Exception as e:
                dep_analysis['parse_error'] = str(e)
        
        self.report['dependency_analysis'] = dep_analysis
    
    def _analyze_imports(self):
        """Analyze import issues across the codebase"""
        print("🔗 Analyzing imports...")
        
        import_issues = []
        circular_imports = []
        missing_modules = []
        
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'archive']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        # Parse imports
                        try:
                            tree = ast.parse(content)
                            for node in ast.walk(tree):
                                if isinstance(node, (ast.Import, ast.ImportFrom)):
                                    # Check for problematic imports
                                    if isinstance(node, ast.ImportFrom) and node.module:
                                        if 'flask_socketio' in node.module:
                                            # Test if import actually works
                                            try:
                                                import flask_socketio
                                            except ImportError:
                                                missing_modules.append(f"{file_path}: Missing flask_socketio")
                                        
                                        # Check for circular imports (simplified check)
                                        if node.module and any(part in file_path for part in node.module.split('.')):
                                            circular_imports.append(f"{file_path}: Potential circular import with {node.module}")
                        except SyntaxError:
                            import_issues.append(f"{file_path}: Syntax error preventing import analysis")
                            
                    except Exception as e:
                        import_issues.append(f"{file_path}: {str(e)}")
        
        if import_issues:
            self.report['critical_issues'].extend(import_issues[:10])  # Top 10
        if missing_modules:
            self.report['critical_issues'].extend(missing_modules)
        if circular_imports:
            self.report['medium_issues'].extend(circular_imports[:5])  # Top 5
    
    def _analyze_route_functionality(self):
        """Analyze route definitions and functionality"""
        print("🛣️ Analyzing routes...")
        
        route_analysis = {
            'total_routes': 0,
            'broken_routes': [],
            'duplicate_routes': [],
            'missing_blueprints': [],
            'working_routes': []
        }
        
        routes_found = {}
        
        # Check routes directory
        if os.path.exists('routes'):
            for file in os.listdir('routes'):
                if file.endswith('.py') and file != '__init__.py':
                    file_path = f"routes/{file}"
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        # Find route definitions
                        import re
                        route_patterns = re.findall(r'@\w*\.route\(["\']([^"\']+)["\']', content)
                        for pattern in route_patterns:
                            route_analysis['total_routes'] += 1
                            if pattern in routes_found:
                                route_analysis['duplicate_routes'].append(f"Duplicate route {pattern} in {file} and {routes_found[pattern]}")
                            else:
                                routes_found[pattern] = file
                                route_analysis['working_routes'].append(pattern)
                                
                        # Check for blueprint exports
                        if '_bp' in content and 'blueprint' not in content.lower():
                            route_analysis['missing_blueprints'].append(f"{file}: Blueprint defined but not properly exported")
                            
                    except Exception as e:
                        route_analysis['broken_routes'].append(f"{file}: {str(e)}")
        
        self.report['functionality_analysis']['routes'] = route_analysis
    
    def _analyze_database_models(self):
        """Analyze database model definitions"""
        print("🗄️ Analyzing database models...")
        
        model_analysis = {
            'total_models': 0,
            'broken_models': [],
            'missing_relationships': [],
            'model_files': []
        }
        
        if os.path.exists('models'):
            for file in os.listdir('models'):
                if file.endswith('.py') and file != '__init__.py':
                    file_path = f"models/{file}"
                    model_analysis['model_files'].append(file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        # Count model classes
                        import re
                        models = re.findall(r'class\s+(\w+)\s*\([^)]*db\.Model[^)]*\)', content)
                        model_analysis['total_models'] += len(models)
                        
                        # Check for common issues
                        if 'db.Model' in content and 'from database import db' not in content and 'from app import db' not in content:
                            model_analysis['broken_models'].append(f"{file}: Uses db.Model but doesn't import db")
                            
                    except Exception as e:
                        model_analysis['broken_models'].append(f"{file}: {str(e)}")
        
        self.report['functionality_analysis']['database'] = model_analysis
    
    def _analyze_configuration(self):
        """Analyze configuration management"""
        print("⚙️ Analyzing configuration...")
        
        config_analysis = {
            'config_files': [],
            'missing_env_vars': [],
            'security_issues': [],
            'hardcoded_values': []
        }
        
        # Check configuration files
        config_files = ['config/app_config.py', 'database.py', 'app.py', 'main.py']
        for config_file in config_files:
            if os.path.exists(config_file):
                config_analysis['config_files'].append(config_file)
                
                try:
                    with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    # Check for hardcoded secrets
                    import re
                    if re.search(r'["\'][a-f0-9]{32,}["\']', content):
                        config_analysis['security_issues'].append(f"{config_file}: Potential hardcoded secret")
                    
                    # Check for missing environment variable handling
                    if 'os.environ.get' in content and 'fallback' not in content.lower():
                        config_analysis['hardcoded_values'].append(f"{config_file}: Environment variables without fallbacks")
                        
                except Exception as e:
                    config_analysis['security_issues'].append(f"{config_file}: {str(e)}")
        
        self.report['functionality_analysis']['configuration'] = config_analysis
    
    def _analyze_security(self):
        """Analyze security configuration"""
        print("🔒 Analyzing security...")
        
        security_issues = []
        
        # Check for common security issues
        files_to_check = ['app.py', 'config/app_config.py']
        for file_path in files_to_check:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    # Check for security headers
                    if 'app.py' in file_path:
                        if 'X-Frame-Options' not in content:
                            security_issues.append("Missing X-Frame-Options header")
                        if 'SESSION_COOKIE_SECURE' in content and 'False' in content:
                            security_issues.append("Session cookies not secure (OK for development)")
                            
                    # Check for hardcoded secrets
                    if 'secret_key' in content.lower() and ('hardcoded' in content.lower() or len([line for line in content.split('\n') if 'secret_key' in line.lower() and '=' in line and 'environ' not in line]) > 0):
                        security_issues.append(f"{file_path}: Potential hardcoded secret key")
                        
                except Exception as e:
                    security_issues.append(f"Error analyzing {file_path}: {str(e)}")
        
        self.report['security_issues'] = security_issues
    
    def _analyze_performance(self):
        """Analyze performance issues"""
        print("⚡ Analyzing performance...")
        
        performance_issues = []
        
        # Check for common performance issues
        large_files = []
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        if size > 50000:  # Files > 50KB
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                lines = len(f.readlines())
                            large_files.append((file_path, size, lines))
                    except:
                        pass
        
        if large_files:
            large_files.sort(key=lambda x: x[1], reverse=True)
            for file_path, size, lines in large_files[:5]:
                performance_issues.append(f"Large file: {file_path} ({size:,} bytes, {lines:,} lines)")
        
        self.report['performance_issues'] = performance_issues
    
    def _test_application_startup(self):
        """Test if the application can start"""
        print("🚀 Testing application startup...")
        
        startup_test = {
            'can_import_app': False,
            'can_create_app': False,
            'startup_errors': []
        }
        
        try:
            # Test importing main modules
            sys.path.insert(0, '.')
            
            # Test app import
            try:
                from app import create_app
                startup_test['can_import_app'] = True
            except Exception as e:
                startup_test['startup_errors'].append(f"Cannot import app: {str(e)}")
            
            # Test app creation
            if startup_test['can_import_app']:
                try:
                    app = create_app()
                    startup_test['can_create_app'] = True
                except Exception as e:
                    startup_test['startup_errors'].append(f"Cannot create app: {str(e)}")
            
        except Exception as e:
            startup_test['startup_errors'].append(f"General startup error: {str(e)}")
        
        self.report['functionality_analysis']['startup'] = startup_test
        
        if startup_test['startup_errors']:
            self.report['critical_issues'].extend(startup_test['startup_errors'])
    
    def _analyze_neglected_areas(self):
        """Analyze often neglected areas"""
        print("🔍 Analyzing neglected areas...")
        
        neglected_issues = []
        
        # Check for unused files
        unused_files = []
        potentially_unused = ['build_test.py', 'setup.py']
        for file in potentially_unused:
            if os.path.exists(file):
                # Check if file is referenced anywhere
                referenced = False
                for root, dirs, files in os.walk('.'):
                    if referenced:
                        break
                    for f in files:
                        if f.endswith('.py') and f != file:
                            try:
                                with open(os.path.join(root, f), 'r', encoding='utf-8', errors='ignore') as content_file:
                                    if file.replace('.py', '') in content_file.read():
                                        referenced = True
                                        break
                            except:
                                pass
                if not referenced:
                    unused_files.append(file)
        
        if unused_files:
            neglected_issues.extend([f"Potentially unused file: {f}" for f in unused_files])
        
        # Check for empty or minimal files
        minimal_files = []
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__']]
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read().strip()
                            if len(content) < 100 and content != '':  # Very small files
                                minimal_files.append(file_path)
                    except:
                        pass
        
        if minimal_files:
            neglected_issues.extend([f"Minimal file (potential cleanup candidate): {f}" for f in minimal_files[:10]])
        
        # Check for TODO/FIXME comments
        todo_count = 0
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if file.endswith('.py'):
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            todo_count += content.lower().count('todo')
                            todo_count += content.lower().count('fixme')
                    except:
                        pass
        
        if todo_count > 10:
            neglected_issues.append(f"High number of TODO/FIXME comments: {todo_count}")
        
        self.report['optimization_opportunities'].extend(neglected_issues)
    
    def _generate_summary(self):
        """Generate analysis summary"""
        self.report['summary'] = {
            'total_files': self.file_count,
            'total_lines': self.total_lines,
            'critical_issues_count': len(self.report['critical_issues']),
            'medium_issues_count': len(self.report['medium_issues']),
            'low_issues_count': len(self.report['low_issues']),
            'security_issues_count': len(self.report['security_issues']),
            'performance_issues_count': len(self.report['performance_issues']),
            'optimization_opportunities_count': len(self.report['optimization_opportunities']),
            'overall_health': self._calculate_health_score()
        }
        
        # Generate recommendations
        self._generate_recommendations()
    
    def _calculate_health_score(self):
        """Calculate overall codebase health score"""
        critical_weight = 10
        medium_weight = 5
        low_weight = 1
        
        total_issues = (
            len(self.report['critical_issues']) * critical_weight +
            len(self.report['medium_issues']) * medium_weight +
            len(self.report['low_issues']) * low_weight +
            len(self.report['security_issues']) * critical_weight +
            len(self.report['performance_issues']) * medium_weight
        )
        
        max_score = 100
        health_score = max(0, max_score - total_issues)
        
        if health_score >= 90:
            return "Excellent"
        elif health_score >= 75:
            return "Good"
        elif health_score >= 60:
            return "Fair"
        elif health_score >= 40:
            return "Poor"
        else:
            return "Critical"
    
    def _generate_recommendations(self):
        """Generate specific recommendations"""
        recommendations = []
        
        # Critical issues recommendations
        if self.report['critical_issues']:
            recommendations.append({
                'priority': 'Critical',
                'title': 'Fix Critical Issues Immediately',
                'description': 'Address import errors, missing dependencies, and startup failures',
                'actions': [
                    'Install missing dependencies (flask-socketio, etc.)',
                    'Fix import paths and circular imports',
                    'Resolve application startup errors'
                ]
            })
        
        # Security recommendations
        if self.report['security_issues']:
            recommendations.append({
                'priority': 'High',
                'title': 'Address Security Concerns',
                'description': 'Fix security configuration and hardcoded values',
                'actions': [
                    'Review and fix hardcoded secrets',
                    'Ensure proper security headers',
                    'Validate environment variable handling'
                ]
            })
        
        # Performance recommendations
        if self.report['performance_issues']:
            recommendations.append({
                'priority': 'Medium',
                'title': 'Optimize Performance',
                'description': 'Address large files and performance bottlenecks',
                'actions': [
                    'Refactor large files into smaller modules',
                    'Optimize database queries',
                    'Implement caching where appropriate'
                ]
            })
        
        # Optimization recommendations
        if self.report['optimization_opportunities']:
            recommendations.append({
                'priority': 'Low',
                'title': 'Clean Up Codebase',
                'description': 'Remove unused files and optimize structure',
                'actions': [
                    'Remove unused files and dependencies',
                    'Consolidate similar functionality',
                    'Address TODO/FIXME comments'
                ]
            })
        
        self.report['recommendations'] = recommendations
    
    def generate_report(self):
        """Generate and save analysis report"""
        print("📊 Generating analysis report...")
        
        # Save detailed JSON report
        with open('codebase_analysis_detailed.json', 'w') as f:
            json.dump(self.report, f, indent=2)
        
        # Generate markdown report
        self._generate_markdown_report()
        
        print("✅ Analysis complete! Reports generated:")
        print("   - codebase_analysis_detailed.json (detailed data)")
        print("   - codebase_analysis_report.md (summary report)")
    
    def _generate_markdown_report(self):
        """Generate human-readable markdown report"""
        report_md = f"""# NOUS Personal Assistant - Comprehensive Codebase Analysis Report

**Generated:** {self.report['generated_at']}
**Analysis Type:** Complete system audit with functionality testing

## Executive Summary

**Codebase Health:** {self.report['summary']['overall_health']} 
**Total Files:** {self.report['summary']['total_files']:,} Python files
**Total Lines:** {self.report['summary']['total_lines']:,} lines of code

### Issue Summary
- 🔴 **Critical Issues:** {self.report['summary']['critical_issues_count']} (requires immediate attention)
- 🟡 **Medium Issues:** {self.report['summary']['medium_issues_count']} (address soon)
- 🟢 **Low Issues:** {self.report['summary']['low_issues_count']} (minor improvements)
- 🔒 **Security Issues:** {self.report['summary']['security_issues_count']} (security concerns)
- ⚡ **Performance Issues:** {self.report['summary']['performance_issues_count']} (optimization needed)

## Detailed Analysis

### 🔴 Critical Issues (Fix Immediately)
"""
        
        for issue in self.report['critical_issues']:
            report_md += f"- {issue}\n"
        
        report_md += f"""
### 🟡 Medium Priority Issues
"""
        
        for issue in self.report['medium_issues']:
            report_md += f"- {issue}\n"
        
        report_md += f"""
### 🔒 Security Analysis
"""
        
        for issue in self.report['security_issues']:
            report_md += f"- {issue}\n"
        
        report_md += f"""
### ⚡ Performance Analysis
"""
        
        for issue in self.report['performance_issues']:
            report_md += f"- {issue}\n"
        
        report_md += f"""
### 🛣️ Routes Analysis
- **Total Routes:** {self.report['functionality_analysis'].get('routes', {}).get('total_routes', 'Unknown')}
- **Working Routes:** {len(self.report['functionality_analysis'].get('routes', {}).get('working_routes', []))}
- **Broken Routes:** {len(self.report['functionality_analysis'].get('routes', {}).get('broken_routes', []))}
- **Duplicate Routes:** {len(self.report['functionality_analysis'].get('routes', {}).get('duplicate_routes', []))}

### 🗄️ Database Analysis
- **Total Models:** {self.report['functionality_analysis'].get('database', {}).get('total_models', 'Unknown')}
- **Model Files:** {len(self.report['functionality_analysis'].get('database', {}).get('model_files', []))}
- **Broken Models:** {len(self.report['functionality_analysis'].get('database', {}).get('broken_models', []))}

### 📦 Dependency Analysis
- **PyProject Status:** {self.report['dependency_analysis'].get('pyproject_status', 'Unknown')}
- **Core Dependencies:** {self.report['dependency_analysis'].get('core_dependencies', 'Unknown')}
- **Optional Groups:** {self.report['dependency_analysis'].get('optional_groups', 'Unknown')}
- **Critical Missing:** {len(self.report['dependency_analysis'].get('critical_missing', []))}

### 🚀 Application Startup Test
- **Can Import App:** {'✅' if self.report['functionality_analysis'].get('startup', {}).get('can_import_app') else '❌'}
- **Can Create App:** {'✅' if self.report['functionality_analysis'].get('startup', {}).get('can_create_app') else '❌'}
- **Startup Errors:** {len(self.report['functionality_analysis'].get('startup', {}).get('startup_errors', []))}

## 📋 Priority Recommendations

"""
        
        for rec in self.report['recommendations']:
            report_md += f"""
### {rec['priority']} Priority: {rec['title']}
{rec['description']}

**Actions:**
"""
            for action in rec['actions']:
                report_md += f"- {action}\n"
        
        report_md += f"""
## 🔧 Optimization Opportunities

"""
        
        for opportunity in self.report['optimization_opportunities']:
            report_md += f"- {opportunity}\n"
        
        report_md += f"""
## File Structure Overview

"""
        
        for category, files in self.report['functionality_analysis'].get('file_structure', {}).items():
            report_md += f"**{category}:** {len(files)} files\n"
        
        report_md += f"""
---

**Report Generated by NOUS Codebase Analyzer**
*For detailed technical data, see codebase_analysis_detailed.json*
"""
        
        with open('codebase_analysis_report.md', 'w') as f:
            f.write(report_md)

def main():
    """Run the complete codebase analysis"""
    analyzer = CodebaseAnalyzer()
    analyzer.analyze_codebase()
    analyzer.generate_report()
    
    # Print summary to console
    print("\n" + "="*60)
    print("🏁 ANALYSIS COMPLETE")
    print("="*60)
    print(f"Codebase Health: {analyzer.report['summary']['overall_health']}")
    print(f"Critical Issues: {analyzer.report['summary']['critical_issues_count']}")
    print(f"Total Files: {analyzer.report['summary']['total_files']:,}")
    print(f"Total Lines: {analyzer.report['summary']['total_lines']:,}")
    print("="*60)

if __name__ == "__main__":
    main()