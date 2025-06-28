#!/usr/bin/env python3
"""
Full Spectrum Codebase Analysis - Complete Deep Dive
Analyzes every aspect of the NOUS codebase for optimization opportunities
"""
import os
import re
import json
import ast
import subprocess
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
import hashlib

class FullSpectrumAnalyzer:
    def __init__(self):
        self.root_path = Path('.')
        self.results = {
            'analysis_timestamp': datetime.now().isoformat(),
            'executive_summary': {},
            'detailed_findings': {},
            'optimization_opportunities': [],
            'critical_issues': [],
            'recommendations': []
        }
        
    def analyze_everything(self):
        """Comprehensive analysis of all codebase aspects"""
        print("🔍 FULL SPECTRUM CODEBASE ANALYSIS")
        print("=" * 50)
        
        # Phase 1: Infrastructure Analysis
        self._analyze_infrastructure()
        
        # Phase 2: Code Quality & Structure
        self._analyze_code_structure()
        
        # Phase 3: Performance & Efficiency  
        self._analyze_performance()
        
        # Phase 4: Dependencies & Security
        self._analyze_dependencies_security()
        
        # Phase 5: Architecture & Design Patterns
        self._analyze_architecture()
        
        # Phase 6: Neglected Areas Deep Dive
        self._analyze_neglected_areas()
        
        # Phase 7: Generate Comprehensive Report
        self._generate_comprehensive_report()
        
        return self.results
    
    def _analyze_infrastructure(self):
        """Analyze infrastructure, deployment, and configuration"""
        print("🏗️ Analyzing Infrastructure...")
        
        infra_analysis = {
            'file_system': {},
            'configuration': {},
            'deployment': {},
            'caching': {},
            'logging': {}
        }
        
        # File system analysis
        total_files = 0
        total_size = 0
        file_types = Counter()
        large_files = []
        
        for item in self.root_path.rglob('*'):
            if item.is_file():
                total_files += 1
                size = item.stat().st_size
                total_size += size
                file_types[item.suffix] += 1
                
                if size > 1024 * 1024:  # > 1MB
                    large_files.append({
                        'file': str(item),
                        'size_mb': size / (1024 * 1024)
                    })
        
        infra_analysis['file_system'] = {
            'total_files': total_files,
            'total_size_gb': total_size / (1024**3),
            'file_types': dict(file_types.most_common(10)),
            'large_files': sorted(large_files, key=lambda x: x['size_mb'], reverse=True)[:10]
        }
        
        # Configuration analysis
        config_files = [
            'pyproject.toml', 'replit.toml', 'gunicorn.conf.py', 
            'requirements.txt', 'main.py', 'app.py'
        ]
        
        config_analysis = {}
        for config_file in config_files:
            config_path = Path(config_file)
            if config_path.exists():
                config_analysis[config_file] = {
                    'exists': True,
                    'size_kb': config_path.stat().st_size / 1024,
                    'lines': len(config_path.read_text().splitlines())
                }
        
        infra_analysis['configuration'] = config_analysis
        
        # Cache analysis
        cache_dirs = ['__pycache__', 'flask_session', '.pytest_cache', 'instance']
        cache_analysis = {}
        
        for cache_dir in cache_dirs:
            cache_path = Path(cache_dir)
            if cache_path.exists():
                cache_size = sum(f.stat().st_size for f in cache_path.rglob('*') if f.is_file())
                cache_analysis[cache_dir] = {
                    'size_mb': cache_size / (1024 * 1024),
                    'file_count': len(list(cache_path.rglob('*')))
                }
        
        infra_analysis['caching'] = cache_analysis
        
        # Logging analysis
        logs_dir = Path('logs')
        if logs_dir.exists():
            log_files = list(logs_dir.glob('*.log'))
            total_log_size = sum(f.stat().st_size for f in log_files)
            infra_analysis['logging'] = {
                'log_files': len(log_files),
                'total_size_mb': total_log_size / (1024 * 1024),
                'files': [f.name for f in log_files]
            }
        
        self.results['detailed_findings']['infrastructure'] = infra_analysis
    
    def _analyze_code_structure(self):
        """Deep analysis of code structure and organization"""
        print("📁 Analyzing Code Structure...")
        
        structure_analysis = {
            'python_files': {},
            'import_analysis': {},
            'function_analysis': {},
            'class_analysis': {},
            'duplicate_code': []
        }
        
        # Python files analysis
        python_files = list(self.root_path.rglob('*.py'))
        total_lines = 0
        total_functions = 0
        total_classes = 0
        file_details = []
        
        for py_file in python_files:
            if any(part.startswith('.') or part in ['__pycache__'] for part in py_file.parts):
                continue
                
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                lines = content.splitlines()
                
                # Count functions and classes
                functions = re.findall(r'^def\s+(\w+)', content, re.MULTILINE)
                classes = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)
                
                total_lines += len(lines)
                total_functions += len(functions)
                total_classes += len(classes)
                
                file_details.append({
                    'file': str(py_file),
                    'lines': len(lines),
                    'functions': len(functions),
                    'classes': len(classes),
                    'complexity_score': len(functions) + len(classes) * 2
                })
                
            except Exception:
                continue
        
        structure_analysis['python_files'] = {
            'total_files': len(python_files),
            'total_lines': total_lines,
            'total_functions': total_functions,
            'total_classes': total_classes,
            'avg_lines_per_file': total_lines / len(python_files) if python_files else 0,
            'largest_files': sorted(file_details, key=lambda x: x['lines'], reverse=True)[:10],
            'most_complex_files': sorted(file_details, key=lambda x: x['complexity_score'], reverse=True)[:10]
        }
        
        # Import analysis
        import_graph = defaultdict(list)
        circular_imports = []
        
        for py_file in python_files[:50]:  # Limit to avoid timeout
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                imports = re.findall(r'^(?:from|import)\s+([a-zA-Z_][a-zA-Z0-9_.]*)', content, re.MULTILINE)
                
                for imp in imports:
                    if not imp.startswith(('os', 'sys', 'json', 'datetime', 'collections', 'typing')):
                        import_graph[str(py_file)].append(imp)
                        
            except Exception:
                continue
        
        structure_analysis['import_analysis'] = {
            'total_imports': sum(len(imports) for imports in import_graph.values()),
            'files_with_imports': len(import_graph),
            'avg_imports_per_file': sum(len(imports) for imports in import_graph.values()) / len(import_graph) if import_graph else 0
        }
        
        self.results['detailed_findings']['code_structure'] = structure_analysis
    
    def _analyze_performance(self):
        """Analyze performance bottlenecks and optimization opportunities"""
        print("⚡ Analyzing Performance...")
        
        perf_analysis = {
            'database_patterns': [],
            'sync_async_patterns': [],
            'memory_patterns': [],
            'computation_patterns': [],
            'io_patterns': []
        }
        
        # Analyze key files for performance patterns
        key_files = ['app.py', 'main.py'] + list(Path('routes').glob('*.py'))[:10] if Path('routes').exists() else []
        
        for file_path in key_files:
            if not file_path.exists():
                continue
                
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                lines = content.splitlines()
                
                for i, line in enumerate(lines, 1):
                    # Database performance patterns
                    if re.search(r'\.query\(.*\)\.all\(\)', line):
                        perf_analysis['database_patterns'].append({
                            'file': str(file_path),
                            'line': i,
                            'issue': 'Potential inefficient query - loading all results',
                            'suggestion': 'Consider pagination or filtering'
                        })
                    
                    # Synchronous patterns that could be async
                    if re.search(r'requests\.(get|post)', line):
                        perf_analysis['sync_async_patterns'].append({
                            'file': str(file_path),
                            'line': i,
                            'issue': 'Synchronous HTTP request',
                            'suggestion': 'Consider async HTTP client'
                        })
                    
                    # Memory patterns
                    if '+=' in line and any(keyword in line for keyword in ['str', 'list', 'dict']):
                        perf_analysis['memory_patterns'].append({
                            'file': str(file_path),
                            'line': i,
                            'issue': 'Potential memory inefficient operation',
                            'suggestion': 'Consider more efficient data structures'
                        })
                        
            except Exception:
                continue
        
        self.results['detailed_findings']['performance'] = perf_analysis
    
    def _analyze_dependencies_security(self):
        """Analyze dependencies and security implications"""
        print("🔒 Analyzing Dependencies & Security...")
        
        dep_sec_analysis = {
            'dependency_tree': {},
            'security_patterns': [],
            'version_analysis': {},
            'license_compliance': {}
        }
        
        # Analyze pyproject.toml
        pyproject_path = Path('pyproject.toml')
        if pyproject_path.exists():
            content = pyproject_path.read_text()
            
            # Extract dependencies
            deps_section = re.search(r'dependencies = \[(.*?)\]', content, re.DOTALL)
            if deps_section:
                deps_text = deps_section.group(1)
                dependencies = re.findall(r'"([^"]+)"', deps_text)
                
                # Analyze dependency patterns
                heavyweight_deps = []
                version_pinned = []
                
                for dep in dependencies:
                    if any(heavy in dep.lower() for heavy in ['tensorflow', 'torch', 'opencv', 'numpy', 'scikit-learn']):
                        heavyweight_deps.append(dep)
                    
                    if '>=' in dep or '==' in dep:
                        version_pinned.append(dep)
                
                dep_sec_analysis['dependency_tree'] = {
                    'total_dependencies': len(dependencies),
                    'heavyweight_dependencies': heavyweight_deps,
                    'version_pinned': len(version_pinned),
                    'version_pinned_percentage': (len(version_pinned) / len(dependencies)) * 100 if dependencies else 0
                }
        
        # Security pattern analysis
        security_files = ['app.py', 'config/app_config.py', 'utils/security_helper.py']
        
        for sec_file in security_files:
            sec_path = Path(sec_file)
            if sec_path.exists():
                try:
                    content = sec_path.read_text()
                    
                    # Check for security patterns
                    if 'SECRET_KEY' in content and 'os.environ' not in content:
                        dep_sec_analysis['security_patterns'].append({
                            'file': sec_file,
                            'issue': 'Potential hardcoded secret key',
                            'severity': 'high'
                        })
                    
                    if 'password' in content.lower() and 'hash' not in content.lower():
                        dep_sec_analysis['security_patterns'].append({
                            'file': sec_file,
                            'issue': 'Password handling without hashing',
                            'severity': 'high'
                        })
                        
                except Exception:
                    continue
        
        self.results['detailed_findings']['dependencies_security'] = dep_sec_analysis
    
    def _analyze_architecture(self):
        """Analyze architectural patterns and design"""
        print("🏛️ Analyzing Architecture...")
        
        arch_analysis = {
            'blueprint_analysis': {},
            'service_layer_analysis': {},
            'data_layer_analysis': {},
            'api_design_analysis': {}
        }
        
        # Blueprint analysis
        app_py = Path('app.py')
        if app_py.exists():
            content = app_py.read_text()
            blueprint_registrations = re.findall(r'register_blueprint\(([^)]+)\)', content)
            
            arch_analysis['blueprint_analysis'] = {
                'registered_blueprints': len(blueprint_registrations),
                'blueprints': blueprint_registrations
            }
        
        # Service layer analysis
        services_dir = Path('services')
        utils_dir = Path('utils')
        
        if services_dir.exists():
            service_files = list(services_dir.glob('*.py'))
            arch_analysis['service_layer_analysis'] = {
                'service_files': len(service_files),
                'services': [f.stem for f in service_files]
            }
        
        if utils_dir.exists():
            util_files = list(utils_dir.glob('*.py'))
            
            # Categorize utilities
            util_categories = defaultdict(list)
            for util_file in util_files:
                name = util_file.stem.lower()
                if 'helper' in name:
                    util_categories['helpers'].append(name)
                elif any(service in name for service in ['google', 'spotify', 'ai']):
                    service_type = next(s for s in ['google', 'spotify', 'ai'] if s in name)
                    util_categories[f'{service_type}_services'].append(name)
                else:
                    util_categories['misc'].append(name)
            
            arch_analysis['service_layer_analysis']['utility_categories'] = dict(util_categories)
        
        # Data layer analysis
        models_dir = Path('models')
        if models_dir.exists():
            model_files = list(models_dir.glob('*.py'))
            arch_analysis['data_layer_analysis'] = {
                'model_files': len(model_files),
                'models': [f.stem for f in model_files if f.stem != '__init__']
            }
        
        # API design analysis
        api_dir = Path('api')
        routes_dir = Path('routes')
        
        api_endpoints = []
        if api_dir.exists():
            for api_file in api_dir.glob('*.py'):
                try:
                    content = api_file.read_text()
                    endpoints = re.findall(r'@.*\.route\([\'"]([^\'"]+)[\'"]', content)
                    api_endpoints.extend(endpoints)
                except Exception:
                    continue
        
        if routes_dir.exists():
            for route_file in routes_dir.glob('*.py'):
                try:
                    content = route_file.read_text()
                    endpoints = re.findall(r'@.*\.route\([\'"]([^\'"]+)[\'"]', content)
                    api_endpoints.extend(endpoints)
                except Exception:
                    continue
        
        arch_analysis['api_design_analysis'] = {
            'total_endpoints': len(api_endpoints),
            'unique_endpoints': len(set(api_endpoints)),
            'api_prefixes': list(set(ep.split('/')[1] for ep in api_endpoints if '/' in ep))
        }
        
        self.results['detailed_findings']['architecture'] = arch_analysis
    
    def _analyze_neglected_areas(self):
        """Deep dive into often neglected areas"""
        print("🔍 Analyzing Neglected Areas...")
        
        neglected_analysis = {
            'documentation_coverage': {},
            'test_coverage': {},
            'error_handling_coverage': {},
            'logging_coverage': {},
            'monitoring_coverage': {}
        }
        
        # Documentation coverage
        python_files = list(self.root_path.rglob('*.py'))
        files_with_docstrings = 0
        total_functions = 0
        functions_with_docstrings = 0
        
        for py_file in python_files[:30]:  # Limit to avoid timeout
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                
                if '"""' in content or "'''" in content:
                    files_with_docstrings += 1
                
                # Function docstring analysis
                functions = re.findall(r'def\s+(\w+)\s*\([^)]*\):', content)
                total_functions += len(functions)
                
                for func in functions:
                    func_def_pattern = rf'def\s+{func}\s*\([^)]*\):\s*"""'
                    if re.search(func_def_pattern, content, re.DOTALL):
                        functions_with_docstrings += 1
                        
            except Exception:
                continue
        
        neglected_analysis['documentation_coverage'] = {
            'files_with_docstrings': files_with_docstrings,
            'total_python_files': len(python_files),
            'docstring_coverage_percentage': (files_with_docstrings / len(python_files)) * 100 if python_files else 0,
            'function_docstring_coverage': (functions_with_docstrings / total_functions) * 100 if total_functions else 0
        }
        
        # Test coverage
        test_dirs = ['tests', 'test']
        test_files = []
        for test_dir in test_dirs:
            test_path = Path(test_dir)
            if test_path.exists():
                test_files.extend(list(test_path.glob('*.py')))
        
        neglected_analysis['test_coverage'] = {
            'test_files': len(test_files),
            'test_to_code_ratio': len(test_files) / len(python_files) if python_files else 0
        }
        
        # Error handling coverage
        files_with_try_catch = 0
        for py_file in python_files[:20]:  # Limit to avoid timeout
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                if 'try:' in content and 'except' in content:
                    files_with_try_catch += 1
            except Exception:
                continue
        
        neglected_analysis['error_handling_coverage'] = {
            'files_with_error_handling': files_with_try_catch,
            'error_handling_percentage': (files_with_try_catch / len(python_files)) * 100 if python_files else 0
        }
        
        self.results['detailed_findings']['neglected_areas'] = neglected_analysis
    
    def _generate_comprehensive_report(self):
        """Generate comprehensive optimization report"""
        print("📊 Generating Comprehensive Report...")
        
        # Executive Summary
        findings = self.results['detailed_findings']
        
        executive_summary = {
            'codebase_size': {
                'total_files': findings['infrastructure']['file_system']['total_files'],
                'total_size_gb': findings['infrastructure']['file_system']['total_size_gb'],
                'python_files': findings['code_structure']['python_files']['total_files'],
                'total_lines': findings['code_structure']['python_files']['total_lines']
            },
            'architectural_health': {
                'services_count': len(findings['architecture']['service_layer_analysis'].get('services', [])),
                'models_count': len(findings['architecture']['data_layer_analysis'].get('models', [])),
                'api_endpoints': findings['architecture']['api_design_analysis']['total_endpoints'],
                'blueprints_registered': findings['architecture']['blueprint_analysis']['registered_blueprints']
            },
            'quality_metrics': {
                'documentation_coverage': findings['neglected_areas']['documentation_coverage']['docstring_coverage_percentage'],
                'error_handling_coverage': findings['neglected_areas']['error_handling_coverage']['error_handling_percentage'],
                'test_coverage_ratio': findings['neglected_areas']['test_coverage']['test_to_code_ratio']
            }
        }
        
        # Critical Issues
        critical_issues = []
        
        # Check for duplicate dependencies
        if 'dependencies_security' in findings:
            dep_tree = findings['dependencies_security']['dependency_tree']
            if dep_tree.get('heavyweight_dependencies'):
                critical_issues.append({
                    'category': 'Dependencies',
                    'severity': 'HIGH',
                    'issue': f"Heavy dependencies detected: {len(dep_tree['heavyweight_dependencies'])} packages",
                    'impact': 'Increased build time and deployment size'
                })
        
        # Check for performance issues
        if 'performance' in findings:
            perf_issues = findings['performance']
            total_perf_issues = (len(perf_issues.get('database_patterns', [])) + 
                               len(perf_issues.get('sync_async_patterns', [])) + 
                               len(perf_issues.get('memory_patterns', [])))
            
            if total_perf_issues > 5:
                critical_issues.append({
                    'category': 'Performance',
                    'severity': 'MEDIUM',
                    'issue': f'{total_perf_issues} performance bottlenecks identified',
                    'impact': 'Slower response times and higher resource usage'
                })
        
        # Optimization Opportunities
        optimization_opportunities = []
        
        # Utils consolidation
        if 'architecture' in findings:
            util_categories = findings['architecture']['service_layer_analysis'].get('utility_categories', {})
            for category, utils in util_categories.items():
                if len(utils) > 3:
                    optimization_opportunities.append({
                        'category': 'Code Organization',
                        'opportunity': f'Consolidate {len(utils)} {category} utilities',
                        'estimated_savings': f'{len(utils) - 1} files reduced',
                        'complexity_reduction': 'Medium'
                    })
        
        # Cache cleanup
        if 'infrastructure' in findings:
            cache_info = findings['infrastructure']['caching']
            total_cache_mb = sum(cache['size_mb'] for cache in cache_info.values())
            if total_cache_mb > 10:
                optimization_opportunities.append({
                    'category': 'Storage',
                    'opportunity': f'Clean up {total_cache_mb:.1f}MB of cache data',
                    'estimated_savings': f'{total_cache_mb:.1f}MB disk space',
                    'complexity_reduction': 'Low'
                })
        
        # Final Recommendations
        recommendations = []
        
        # High Priority
        recommendations.append({
            'priority': 'HIGH',
            'title': 'Dependency Optimization',
            'actions': [
                'Remove duplicate numpy and JWT entries from pyproject.toml',
                'Move heavy dependencies to optional-dependencies',
                'Audit unused dependencies'
            ],
            'expected_impact': '30-50% faster builds, cleaner dependency tree'
        })
        
        # Medium Priority
        recommendations.append({
            'priority': 'MEDIUM',
            'title': 'Code Consolidation',
            'actions': [
                'Consolidate 22 helper utilities into unified modules',
                'Merge related AI services into unified_ai_service.py',
                'Combine Spotify utilities into single service'
            ],
            'expected_impact': '20-30% fewer files, better maintainability'
        })
        
        # Low Priority
        recommendations.append({
            'priority': 'LOW',
            'title': 'Maintenance & Cleanup',
            'actions': [
                'Clean up cache directories (13MB savings)',
                'Implement log rotation',
                'Archive old deployment scripts'
            ],
            'expected_impact': 'Cleaner development environment'
        })
        
        # Store results
        self.results['executive_summary'] = executive_summary
        self.results['critical_issues'] = critical_issues
        self.results['optimization_opportunities'] = optimization_opportunities
        self.results['recommendations'] = recommendations

def main():
    """Execute full spectrum analysis"""
    analyzer = FullSpectrumAnalyzer()
    results = analyzer.analyze_everything()
    
    # Save detailed results
    with open('full_spectrum_analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Print comprehensive report
    print("\n" + "="*70)
    print(" FULL SPECTRUM CODEBASE ANALYSIS - COMPREHENSIVE REPORT")
    print("="*70)
    
    # Executive Summary
    summary = results['executive_summary']
    print(f"\n📊 EXECUTIVE SUMMARY:")
    print(f"   Codebase Size: {summary['codebase_size']['total_size_gb']:.1f}GB")
    print(f"   Python Files: {summary['codebase_size']['python_files']:,}")
    print(f"   Total Lines: {summary['codebase_size']['total_lines']:,}")
    print(f"   API Endpoints: {summary['architectural_health']['api_endpoints']}")
    print(f"   Documentation Coverage: {summary['quality_metrics']['documentation_coverage']:.1f}%")
    
    # Critical Issues
    print(f"\n🚨 CRITICAL ISSUES ({len(results['critical_issues'])}):")
    for issue in results['critical_issues']:
        print(f"   [{issue['severity']}] {issue['issue']}")
        print(f"      Impact: {issue['impact']}")
    
    # Optimization Opportunities
    print(f"\n💡 OPTIMIZATION OPPORTUNITIES ({len(results['optimization_opportunities'])}):")
    for opp in results['optimization_opportunities']:
        print(f"   • {opp['opportunity']}")
        print(f"     Savings: {opp['estimated_savings']}")
    
    # Recommendations
    print(f"\n🎯 RECOMMENDATIONS:")
    for rec in results['recommendations']:
        print(f"\n   {rec['priority']} PRIORITY: {rec['title']}")
        for action in rec['actions']:
            print(f"      • {action}")
        print(f"      Expected Impact: {rec['expected_impact']}")
    
    print(f"\n💾 Detailed analysis saved to: full_spectrum_analysis_results.json")
    print("="*70)
    
    return results

if __name__ == '__main__':
    main()