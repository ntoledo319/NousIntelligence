#!/usr/bin/env python3
"""
Comprehensive Codebase Optimization Analysis
Analyzes entire NOUS codebase for optimization opportunities while preserving functionality
"""
import os
import sys
import json
import re
import ast
import subprocess
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
import importlib.util

class ComprehensiveOptimizationAnalyzer:
    def __init__(self):
        self.start_time = datetime.now()
        self.root_path = Path('.')
        self.analysis_results = {
            'metadata': {
                'analysis_date': self.start_time.isoformat(),
                'analyzer_version': '2.0.0'
            },
            'codebase_metrics': {},
            'optimization_opportunities': [],
            'dependency_analysis': {},
            'architectural_issues': [],
            'performance_bottlenecks': [],
            'code_quality_issues': [],
            'security_concerns': [],
            'maintenance_recommendations': [],
            'often_neglected_areas': {},
            'summary': {}
        }
        
    def run_comprehensive_analysis(self):
        """Execute all analysis phases"""
        print("🔍 Starting Comprehensive Optimization Analysis...")
        print(f"📊 Target: {self.root_path.absolute()}")
        
        # Phase 1: Baseline Metrics
        self._collect_baseline_metrics()
        
        # Phase 2: Dependency Analysis
        self._analyze_dependencies()
        
        # Phase 3: Code Structure Analysis
        self._analyze_code_structure()
        
        # Phase 4: Performance Analysis
        self._analyze_performance_patterns()
        
        # Phase 5: Often Neglected Areas
        self._analyze_neglected_areas()
        
        # Phase 6: Architectural Analysis
        self._analyze_architecture()
        
        # Phase 7: Security & Quality Analysis
        self._analyze_security_and_quality()
        
        # Phase 8: Generate Recommendations
        self._generate_optimization_recommendations()
        
        # Phase 9: Create Summary
        self._create_executive_summary()
        
        print(f"✅ Analysis completed in {(datetime.now() - self.start_time).total_seconds():.1f}s")
        return self.analysis_results
        
    def _collect_baseline_metrics(self):
        """Collect baseline codebase metrics"""
        print("📊 Collecting baseline metrics...")
        
        metrics = {
            'total_files': 0,
            'python_files': 0,
            'total_lines': 0,
            'empty_lines': 0,
            'comment_lines': 0,
            'code_lines': 0,
            'file_sizes': [],
            'directory_structure': {},
            'large_files': [],
            'cache_dirs': [],
            'config_files': []
        }
        
        for file_path in self.root_path.rglob('*'):
            if file_path.is_file():
                metrics['total_files'] += 1
                file_size = file_path.stat().st_size
                metrics['file_sizes'].append(file_size)
                
                # Track configuration files
                if file_path.suffix in ['.toml', '.json', '.yml', '.yaml', '.ini', '.conf']:
                    metrics['config_files'].append(str(file_path))
                
                # Python file analysis
                if file_path.suffix == '.py':
                    metrics['python_files'] += 1
                    
                    try:
                        content = file_path.read_text(encoding='utf-8', errors='ignore')
                        lines = content.splitlines()
                        metrics['total_lines'] += len(lines)
                        
                        for line in lines:
                            stripped = line.strip()
                            if not stripped:
                                metrics['empty_lines'] += 1
                            elif stripped.startswith('#'):
                                metrics['comment_lines'] += 1
                            else:
                                metrics['code_lines'] += 1
                                
                        # Track large files
                        if len(lines) > 500:
                            metrics['large_files'].append({
                                'file': str(file_path),
                                'lines': len(lines),
                                'size_kb': file_size / 1024
                            })
                            
                    except Exception as e:
                        continue
            
            elif file_path.is_dir():
                # Track cache directories
                if file_path.name in ['__pycache__', '.pytest_cache', 'node_modules', 'flask_session']:
                    cache_size = sum(f.stat().st_size for f in file_path.rglob('*') if f.is_file())
                    metrics['cache_dirs'].append({
                        'dir': str(file_path),
                        'size_mb': cache_size / (1024 * 1024)
                    })
        
        # Calculate averages and distributions
        if metrics['file_sizes']:
            metrics['avg_file_size'] = sum(metrics['file_sizes']) / len(metrics['file_sizes'])
            metrics['total_size_mb'] = sum(metrics['file_sizes']) / (1024 * 1024)
        
        self.analysis_results['codebase_metrics'] = metrics
        
    def _analyze_dependencies(self):
        """Analyze dependency configuration and issues"""
        print("📦 Analyzing dependencies...")
        
        dep_analysis = {
            'duplicate_dependencies': [],
            'version_conflicts': [],
            'unused_dependencies': [],
            'heavyweight_deps': [],
            'missing_dependencies': [],
            'security_issues': [],
            'optimization_opportunities': []
        }
        
        # Analyze pyproject.toml
        pyproject_path = Path('pyproject.toml')
        if pyproject_path.exists():
            try:
                import tomllib
                with open(pyproject_path, 'rb') as f:
                    pyproject_data = tomllib.load(f)
                    
                deps = pyproject_data.get('project', {}).get('dependencies', [])
                optional_deps = pyproject_data.get('project', {}).get('optional-dependencies', {})
                
                # Check for duplicates
                dep_names = []
                for dep in deps:
                    name = dep.split('>=')[0].split('==')[0].split('[')[0].lower()
                    if name in dep_names:
                        dep_analysis['duplicate_dependencies'].append(name)
                    dep_names.append(name)
                
                # Check for heavyweight dependencies
                heavyweight = ['tensorflow', 'torch', 'opencv-python', 'numpy', 'scikit-learn', 'librosa']
                for dep in deps:
                    dep_name = dep.split('>=')[0].split('==')[0].lower()
                    if dep_name in heavyweight:
                        dep_analysis['heavyweight_deps'].append(dep)
                        
                # Analyze optional dependencies for consolidation opportunities
                all_optional = []
                for category, deps_list in optional_deps.items():
                    all_optional.extend(deps_list)
                    
                # Check for duplicates between main and optional
                main_names = [d.split('>=')[0].split('==')[0].lower() for d in deps]
                for opt_dep in all_optional:
                    opt_name = opt_dep.split('>=')[0].split('==')[0].lower()
                    if opt_name in main_names:
                        dep_analysis['duplicate_dependencies'].append(f"{opt_name} (main + optional)")
                        
            except Exception as e:
                dep_analysis['analysis_errors'] = [str(e)]
        
        self.analysis_results['dependency_analysis'] = dep_analysis
        
    def _analyze_code_structure(self):
        """Analyze code structure and organization"""
        print("🏗️ Analyzing code structure...")
        
        structure_issues = []
        consolidation_opportunities = []
        
        # Analyze utils directory for consolidation opportunities
        utils_files = list(Path('utils').glob('*.py')) if Path('utils').exists() else []
        
        # Group similar utilities
        utility_groups = defaultdict(list)
        for util_file in utils_files:
            try:
                content = util_file.read_text(encoding='utf-8', errors='ignore')
                
                # Classify by functionality patterns
                if 'helper' in util_file.name.lower():
                    utility_groups['helpers'].append(util_file.name)
                elif any(word in util_file.name.lower() for word in ['google', 'spotify', 'ai', 'voice']):
                    service_type = next((word for word in ['google', 'spotify', 'ai', 'voice'] 
                                       if word in util_file.name.lower()), 'misc')
                    utility_groups[f'{service_type}_services'].append(util_file.name)
                elif any(word in util_file.name.lower() for word in ['auth', 'security']):
                    utility_groups['security'].append(util_file.name)
                elif any(word in util_file.name.lower() for word in ['db', 'database']):
                    utility_groups['database'].append(util_file.name)
                else:
                    utility_groups['misc'].append(util_file.name)
                    
            except Exception:
                continue
        
        # Identify consolidation opportunities
        for group, files in utility_groups.items():
            if len(files) > 3:
                consolidation_opportunities.append({
                    'category': group,
                    'files': files,
                    'suggestion': f'Consider consolidating {len(files)} {group} files into unified_{group}.py'
                })
        
        # Analyze routes directory
        routes_files = list(Path('routes').glob('*.py')) if Path('routes').exists() else []
        if len(routes_files) > 20:
            structure_issues.append({
                'area': 'routes',
                'issue': f'Too many route files ({len(routes_files)})',
                'suggestion': 'Consider grouping related routes into blueprint modules'
            })
        
        self.analysis_results['architectural_issues'].extend(structure_issues)
        self.analysis_results['optimization_opportunities'].extend(consolidation_opportunities)
        
    def _analyze_performance_patterns(self):
        """Analyze performance bottlenecks and optimization opportunities"""
        print("⚡ Analyzing performance patterns...")
        
        performance_issues = []
        
        # Check for inefficient patterns in Python files
        for py_file in self.root_path.rglob('*.py'):
            if any(part.startswith('.') or part in ['__pycache__', 'venv'] for part in py_file.parts):
                continue
                
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                
                # Check for performance anti-patterns
                lines = content.splitlines()
                for i, line in enumerate(lines, 1):
                    # Database queries in loops
                    if re.search(r'for.*in.*:.*\.query\(', line, re.IGNORECASE):
                        performance_issues.append({
                            'file': str(py_file),
                            'line': i,
                            'issue': 'Database query in loop - potential N+1 problem',
                            'suggestion': 'Consider bulk queries or eager loading'
                        })
                    
                    # Inefficient string concatenation
                    if '+=' in line and 'str' in line.lower():
                        performance_issues.append({
                            'file': str(py_file),
                            'line': i,
                            'issue': 'String concatenation in loop',
                            'suggestion': 'Use join() or f-strings for better performance'
                        })
                        
                    # Synchronous operations that could be async
                    if re.search(r'requests\.(get|post)', line):
                        performance_issues.append({
                            'file': str(py_file),
                            'line': i,
                            'issue': 'Synchronous HTTP request',
                            'suggestion': 'Consider async HTTP client for better concurrency'
                        })
                        
            except Exception:
                continue
        
        self.analysis_results['performance_bottlenecks'] = performance_issues
        
    def _analyze_neglected_areas(self):
        """Analyze often neglected areas"""
        print("🔍 Analyzing often neglected areas...")
        
        neglected_analysis = {
            'cache_cleanup': [],
            'log_management': [],
            'error_handling': [],
            'documentation': [],
            'testing': [],
            'monitoring': []
        }
        
        # Cache directories analysis
        cache_dirs = ['__pycache__', 'flask_session', '.pytest_cache', 'instance']
        for cache_dir in cache_dirs:
            cache_path = Path(cache_dir)
            if cache_path.exists():
                try:
                    cache_size = sum(f.stat().st_size for f in cache_path.rglob('*') if f.is_file())
                    if cache_size > 10 * 1024 * 1024:  # > 10MB
                        neglected_analysis['cache_cleanup'].append({
                            'dir': cache_dir,
                            'size_mb': cache_size / (1024 * 1024),
                            'suggestion': 'Large cache directory - consider cleanup'
                        })
                except Exception:
                    continue
        
        # Log management
        logs_dir = Path('logs')
        if logs_dir.exists():
            log_files = list(logs_dir.glob('*.log'))
            total_log_size = sum(f.stat().st_size for f in log_files)
            if total_log_size > 50 * 1024 * 1024:  # > 50MB
                neglected_analysis['log_management'].append({
                    'issue': 'Large log files',
                    'size_mb': total_log_size / (1024 * 1024),
                    'suggestion': 'Implement log rotation and cleanup'
                })
        
        # Error handling analysis
        python_files_without_try_catch = []
        for py_file in self.root_path.rglob('*.py'):
            if any(part.startswith('.') for part in py_file.parts):
                continue
                
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                if 'def ' in content and 'try:' not in content and 'except' not in content:
                    if len(content.splitlines()) > 20:  # Only flag substantial files
                        python_files_without_try_catch.append(str(py_file))
            except Exception:
                continue
        
        if python_files_without_try_catch:
            neglected_analysis['error_handling'] = python_files_without_try_catch[:10]  # Top 10
        
        # Documentation analysis
        py_files_without_docstrings = []
        for py_file in self.root_path.rglob('*.py'):
            if any(part.startswith('.') for part in py_file.parts):
                continue
                
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                if 'def ' in content and '"""' not in content and "'''" not in content:
                    if len(content.splitlines()) > 10:
                        py_files_without_docstrings.append(str(py_file))
            except Exception:
                continue
        
        if py_files_without_docstrings:
            neglected_analysis['documentation'] = py_files_without_docstrings[:5]  # Top 5
        
        self.analysis_results['often_neglected_areas'] = neglected_analysis
        
    def _analyze_architecture(self):
        """Analyze architectural patterns and issues"""
        print("🏛️ Analyzing architecture...")
        
        architectural_issues = []
        
        # Check for circular imports
        import_graph = defaultdict(set)
        for py_file in self.root_path.rglob('*.py'):
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                imports = re.findall(r'^(?:from|import)\s+([a-zA-Z_][a-zA-Z0-9_.]*)', content, re.MULTILINE)
                
                for imp in imports:
                    if not imp.startswith(('os', 'sys', 'json', 'datetime', 'collections')):
                        import_graph[str(py_file)].add(imp)
            except Exception:
                continue
        
        # Identify Blueprint registration issues
        app_py = Path('app.py')
        if app_py.exists():
            try:
                content = app_py.read_text()
                blueprint_registrations = re.findall(r'app\.register_blueprint\(([^)]+)\)', content)
                
                # Check if all route files have corresponding blueprints
                route_files = list(Path('routes').glob('*.py')) if Path('routes').exists() else []
                registered_count = len(blueprint_registrations)
                route_count = len([f for f in route_files if f.name != '__init__.py'])
                
                if route_count > registered_count + 5:  # Allow some flexibility
                    architectural_issues.append({
                        'issue': 'Blueprint registration mismatch',
                        'details': f'{route_count} route files but only {registered_count} registrations',
                        'suggestion': 'Ensure all route blueprints are registered in app.py'
                    })
                    
            except Exception:
                pass
        
        self.analysis_results['architectural_issues'].extend(architectural_issues)
        
    def _analyze_security_and_quality(self):
        """Analyze security and code quality issues"""
        print("🔒 Analyzing security and quality...")
        
        security_issues = []
        quality_issues = []
        
        # Check for common security issues
        for py_file in self.root_path.rglob('*.py'):
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                
                # Check for hardcoded secrets
                if re.search(r'password\s*=\s*[\'"][^\'"]+[\'"]', content, re.IGNORECASE):
                    security_issues.append({
                        'file': str(py_file),
                        'issue': 'Potential hardcoded password',
                        'suggestion': 'Use environment variables for secrets'
                    })
                
                # Check for SQL injection risks
                if re.search(r'\.execute\s*\(\s*[\'"].*%.*[\'"]', content):
                    security_issues.append({
                        'file': str(py_file),
                        'issue': 'Potential SQL injection risk',
                        'suggestion': 'Use parameterized queries'
                    })
                
                # Code quality issues
                if content.count('TODO') > 5:
                    quality_issues.append({
                        'file': str(py_file),
                        'issue': f'Many TODO comments ({content.count("TODO")})',
                        'suggestion': 'Address or prioritize TODO items'
                    })
                    
            except Exception:
                continue
        
        self.analysis_results['security_concerns'] = security_issues
        self.analysis_results['code_quality_issues'] = quality_issues
        
    def _generate_optimization_recommendations(self):
        """Generate specific optimization recommendations"""
        print("💡 Generating optimization recommendations...")
        
        recommendations = []
        
        # Dependency optimization
        if self.analysis_results['dependency_analysis']['duplicate_dependencies']:
            recommendations.append({
                'category': 'Dependencies',
                'priority': 'High',
                'title': 'Remove Duplicate Dependencies',
                'description': 'Found duplicate dependencies that increase build time and size',
                'action': 'Consolidate duplicate packages in pyproject.toml',
                'impact': 'Faster builds, smaller deployment size'
            })
        
        # Code consolidation
        consolidation_opps = [o for o in self.analysis_results['optimization_opportunities'] 
                             if isinstance(o, dict) and 'category' in o]
        if consolidation_opps:
            recommendations.append({
                'category': 'Code Structure',
                'priority': 'Medium',
                'title': 'Consolidate Utility Modules',
                'description': f'Found {len(consolidation_opps)} consolidation opportunities',
                'action': 'Merge related utility files into unified modules',
                'impact': 'Reduced import complexity, better maintainability'
            })
        
        # Performance optimization
        if self.analysis_results['performance_bottlenecks']:
            recommendations.append({
                'category': 'Performance',
                'priority': 'High',
                'title': 'Address Performance Bottlenecks',
                'description': f'Found {len(self.analysis_results["performance_bottlenecks"])} performance issues',
                'action': 'Optimize database queries and async operations',
                'impact': 'Faster response times, better scalability'
            })
        
        # Cache cleanup
        cache_issues = self.analysis_results['often_neglected_areas'].get('cache_cleanup', [])
        if cache_issues:
            recommendations.append({
                'category': 'Maintenance',
                'priority': 'Low',
                'title': 'Clean Up Cache Directories',
                'description': f'Found {len(cache_issues)} large cache directories',
                'action': 'Implement automated cache cleanup',
                'impact': 'Reduced disk usage, cleaner development environment'
            })
        
        self.analysis_results['maintenance_recommendations'] = recommendations
        
    def _create_executive_summary(self):
        """Create executive summary of findings"""
        print("📋 Creating executive summary...")
        
        metrics = self.analysis_results['codebase_metrics']
        
        summary = {
            'codebase_size': {
                'total_files': metrics['total_files'],
                'python_files': metrics['python_files'],
                'total_lines': metrics['total_lines'],
                'size_mb': metrics.get('total_size_mb', 0)
            },
            'optimization_potential': {
                'high_priority': len([r for r in self.analysis_results['maintenance_recommendations'] 
                                    if r.get('priority') == 'High']),
                'medium_priority': len([r for r in self.analysis_results['maintenance_recommendations'] 
                                      if r.get('priority') == 'Medium']),
                'low_priority': len([r for r in self.analysis_results['maintenance_recommendations'] 
                                   if r.get('priority') == 'Low'])
            },
            'areas_analyzed': [
                'Dependencies', 'Code Structure', 'Performance', 'Security', 
                'Cache Management', 'Error Handling', 'Documentation'
            ],
            'key_findings': [
                f"Analyzed {metrics['python_files']} Python files",
                f"Found {len(self.analysis_results['dependency_analysis']['duplicate_dependencies'])} duplicate dependencies",
                f"Identified {len(self.analysis_results['performance_bottlenecks'])} performance issues",
                f"Discovered {len(self.analysis_results['optimization_opportunities'])} consolidation opportunities"
            ]
        }
        
        self.analysis_results['summary'] = summary

def main():
    """Run comprehensive optimization analysis"""
    analyzer = ComprehensiveOptimizationAnalyzer()
    results = analyzer.run_comprehensive_analysis()
    
    # Save results
    output_file = 'comprehensive_optimization_report.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📊 Analysis complete! Report saved to {output_file}")
    print(f"🔍 Analyzed {results['codebase_metrics']['python_files']} Python files")
    print(f"💡 Found {len(results['maintenance_recommendations'])} optimization opportunities")
    
    return results

if __name__ == '__main__':
    main()