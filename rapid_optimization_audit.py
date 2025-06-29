#!/usr/bin/env python3
"""
Rapid Optimization Audit for NOUS Codebase
Fast analysis to identify key optimization opportunities
"""
import os
import sys
from pathlib import Path
from collections import defaultdict, Counter
import json
import ast
import re
from datetime import datetime

class RapidOptimizationAuditor:
    def __init__(self):
        self.root_path = Path('.')
        self.analysis = {
            'timestamp': datetime.now().isoformat(),
            'file_analysis': {},
            'dependency_analysis': {},
            'route_analysis': {},
            'optimization_opportunities': [],
            'critical_issues': [],
            'quick_wins': []
        }
        
    def run_audit(self):
        """Run comprehensive but fast audit"""
        print("🚀 Starting Rapid Optimization Audit...")
        
        # Phase 1: File System Analysis
        self._analyze_file_system()
        
        # Phase 2: Dependency Analysis
        self._analyze_dependencies()
        
        # Phase 3: Route Analysis
        self._analyze_routes()
        
        # Phase 4: Import Analysis
        self._analyze_imports()
        
        # Phase 5: Code Quality Analysis
        self._analyze_code_quality()
        
        # Phase 6: Generate Recommendations
        self._generate_recommendations()
        
        return self.analysis
    
    def _analyze_file_system(self):
        """Analyze file system structure and sizes"""
        print("📁 Analyzing file system...")
        
        file_stats = {
            'total_files': 0,
            'python_files': 0,
            'total_size_mb': 0,
            'cache_size_mb': 0,
            'log_size_mb': 0,
            'large_files': [],
            'empty_files': [],
            'duplicate_candidates': []
        }
        
        file_sizes = defaultdict(list)
        
        for file_path in self.root_path.rglob('*'):
            if not file_path.is_file():
                continue
                
            size = file_path.stat().st_size
            file_stats['total_files'] += 1
            file_stats['total_size_mb'] += size / (1024 * 1024)
            
            # Track by extension
            if file_path.suffix == '.py':
                file_stats['python_files'] += 1
                
            # Cache files
            if any(cache in str(file_path) for cache in ['__pycache__', 'flask_session', '.pytest_cache']):
                file_stats['cache_size_mb'] += size / (1024 * 1024)
                
            # Log files
            if file_path.suffix == '.log':
                file_stats['log_size_mb'] += size / (1024 * 1024)
                
            # Large files (>1MB)
            if size > 1024 * 1024:
                file_stats['large_files'].append({
                    'path': str(file_path),
                    'size_mb': size / (1024 * 1024)
                })
                
            # Empty files
            if size == 0:
                file_stats['empty_files'].append(str(file_path))
                
            # Track files by name for duplicate detection
            file_sizes[file_path.name].append(str(file_path))
        
        # Find potential duplicates
        for filename, paths in file_sizes.items():
            if len(paths) > 1 and filename.endswith('.py'):
                file_stats['duplicate_candidates'].append({
                    'filename': filename,
                    'paths': paths
                })
        
        self.analysis['file_analysis'] = file_stats
        
    def _analyze_dependencies(self):
        """Analyze dependency configuration"""
        print("📦 Analyzing dependencies...")
        
        dep_analysis = {
            'pyproject_issues': [],
            'duplicate_deps': [],
            'unused_deps': [],
            'version_conflicts': []
        }
        
        # Check pyproject.toml
        pyproject_path = Path('pyproject.toml')
        if pyproject_path.exists():
            try:
                import tomllib
                content = pyproject_path.read_text()
                
                # Look for duplicate entries
                if content.count('numpy') > 1:
                    dep_analysis['duplicate_deps'].append('numpy (found multiple times)')
                    
                # Look for version conflicts
                werkzeug_matches = re.findall(r'werkzeug[>=<~!]+[\d.]+', content.lower())
                if len(werkzeug_matches) > 1:
                    dep_analysis['version_conflicts'].append(f'werkzeug: {werkzeug_matches}')
                    
            except Exception as e:
                dep_analysis['pyproject_issues'].append(f'Parse error: {e}')
        
        self.analysis['dependency_analysis'] = dep_analysis
        
    def _analyze_routes(self):
        """Analyze route definitions across the application"""
        print("🛣️ Analyzing routes...")
        
        route_stats = {
            'total_route_files': 0,
            'total_routes': 0,
            'blueprint_count': 0,
            'route_conflicts': [],
            'missing_routes': [],
            'route_files': []
        }
        
        routes_dir = Path('routes')
        if routes_dir.exists():
            route_patterns = []
            
            for py_file in routes_dir.glob('*.py'):
                if py_file.name == '__init__.py':
                    continue
                    
                route_stats['total_route_files'] += 1
                route_stats['route_files'].append(py_file.name)
                
                try:
                    content = py_file.read_text(encoding='utf-8')
                    
                    # Count routes
                    route_decorators = re.findall(r'@\w+\.route\([\'"]([^\'"]+)[\'"]', content)
                    route_stats['total_routes'] += len(route_decorators)
                    route_patterns.extend(route_decorators)
                    
                    # Count blueprints
                    if 'Blueprint(' in content:
                        route_stats['blueprint_count'] += 1
                        
                except Exception as e:
                    route_stats['missing_routes'].append(f'{py_file.name}: {e}')
            
            # Check for duplicate routes
            route_counter = Counter(route_patterns)
            duplicates = [(route, count) for route, count in route_counter.items() if count > 1]
            if duplicates:
                route_stats['route_conflicts'] = duplicates
        
        self.analysis['route_analysis'] = route_stats
        
    def _analyze_imports(self):
        """Analyze import statements for optimization"""
        print("📥 Analyzing imports...")
        
        import_stats = {
            'circular_imports': [],
            'unused_imports': [],
            'heavy_imports': [],
            'import_errors': []
        }
        
        # Check for common circular import patterns
        for py_file in self.root_path.rglob('*.py'):
            try:
                content = py_file.read_text(encoding='utf-8')
                
                # Look for heavy imports
                if 'import tensorflow' in content or 'import torch' in content:
                    import_stats['heavy_imports'].append(str(py_file))
                    
                # Look for potential circular imports
                if 'from app import' in content and py_file.name != 'main.py':
                    import_stats['circular_imports'].append(str(py_file))
                    
            except Exception as e:
                import_stats['import_errors'].append(f'{py_file}: {e}')
        
        self.analysis['import_analysis'] = import_stats
        
    def _analyze_code_quality(self):
        """Quick code quality analysis"""
        print("🔍 Analyzing code quality...")
        
        quality_stats = {
            'long_files': [],
            'complex_functions': [],
            'todo_comments': [],
            'hardcoded_values': []
        }
        
        for py_file in self.root_path.rglob('*.py'):
            try:
                content = py_file.read_text(encoding='utf-8')
                lines = content.splitlines()
                
                # Long files (>500 lines)
                if len(lines) > 500:
                    quality_stats['long_files'].append({
                        'file': str(py_file),
                        'lines': len(lines)
                    })
                
                # TODO comments
                todos = [i for i, line in enumerate(lines) if 'TODO' in line.upper() or 'FIXME' in line.upper()]
                if todos:
                    quality_stats['todo_comments'].append({
                        'file': str(py_file),
                        'count': len(todos)
                    })
                
                # Hardcoded ports or URLs
                if re.search(r':\d{4,5}[^)]', content) or 'localhost' in content:
                    quality_stats['hardcoded_values'].append(str(py_file))
                    
            except Exception:
                continue
        
        self.analysis['code_quality'] = quality_stats
        
    def _generate_recommendations(self):
        """Generate optimization recommendations"""
        print("💡 Generating recommendations...")
        
        recommendations = []
        
        # File system recommendations
        file_analysis = self.analysis['file_analysis']
        if file_analysis['cache_size_mb'] > 10:
            recommendations.append({
                'type': 'cleanup',
                'priority': 'high',
                'title': 'Clean up cache files',
                'description': f"Remove {file_analysis['cache_size_mb']:.1f}MB of cache files",
                'action': 'Delete __pycache__, flask_session, .pytest_cache directories'
            })
        
        if file_analysis['log_size_mb'] > 5:
            recommendations.append({
                'type': 'cleanup',
                'priority': 'medium',
                'title': 'Archive log files',
                'description': f"Archive {file_analysis['log_size_mb']:.1f}MB of log files",
                'action': 'Move old logs to archive or implement log rotation'
            })
        
        if file_analysis['empty_files']:
            recommendations.append({
                'type': 'cleanup',
                'priority': 'low',
                'title': 'Remove empty files',
                'description': f"Remove {len(file_analysis['empty_files'])} empty files",
                'action': 'Delete files with 0 bytes'
            })
        
        # Route recommendations
        route_analysis = self.analysis['route_analysis']
        if route_analysis['total_route_files'] > 20:
            recommendations.append({
                'type': 'consolidation',
                'priority': 'medium',
                'title': 'Consolidate route files',
                'description': f"Consider consolidating {route_analysis['total_route_files']} route files",
                'action': 'Group related routes into fewer, more cohesive modules'
            })
        
        # Dependency recommendations
        dep_analysis = self.analysis['dependency_analysis']
        if dep_analysis['duplicate_deps']:
            recommendations.append({
                'type': 'dependencies',
                'priority': 'high',
                'title': 'Fix duplicate dependencies',
                'description': f"Fix {len(dep_analysis['duplicate_deps'])} duplicate dependencies",
                'action': 'Remove duplicate entries from pyproject.toml'
            })
        
        # Code quality recommendations
        if 'code_quality' in self.analysis:
            quality = self.analysis['code_quality']
            if quality['long_files']:
                recommendations.append({
                    'type': 'refactoring',
                    'priority': 'medium',
                    'title': 'Refactor long files',
                    'description': f"Break down {len(quality['long_files'])} files >500 lines",
                    'action': 'Split large files into smaller, focused modules'
                })
        
        self.analysis['recommendations'] = recommendations
        
    def print_summary(self):
        """Print audit summary"""
        print("\n" + "="*60)
        print("🏁 RAPID OPTIMIZATION AUDIT COMPLETE")
        print("="*60)
        
        file_stats = self.analysis['file_analysis']
        print(f"📊 File Statistics:")
        print(f"   Total Files: {file_stats['total_files']:,}")
        print(f"   Python Files: {file_stats['python_files']:,}")
        print(f"   Total Size: {file_stats['total_size_mb']:.1f}MB")
        print(f"   Cache Size: {file_stats['cache_size_mb']:.1f}MB")
        print(f"   Log Size: {file_stats['log_size_mb']:.1f}MB")
        
        route_stats = self.analysis['route_analysis']
        print(f"\n🛣️ Route Statistics:")
        print(f"   Route Files: {route_stats['total_route_files']}")
        print(f"   Total Routes: {route_stats['total_routes']}")
        print(f"   Blueprints: {route_stats['blueprint_count']}")
        
        recommendations = self.analysis['recommendations']
        print(f"\n💡 Optimization Opportunities: {len(recommendations)}")
        for rec in recommendations[:5]:  # Show top 5
            print(f"   [{rec['priority'].upper()}] {rec['title']}")
        
        return self.analysis

def main():
    """Run rapid optimization audit"""
    auditor = RapidOptimizationAuditor()
    results = auditor.run_audit()
    auditor.print_summary()
    
    # Save results
    with open('rapid_optimization_audit.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n📄 Detailed results saved to: rapid_optimization_audit.json")
    return results

if __name__ == "__main__":
    main()