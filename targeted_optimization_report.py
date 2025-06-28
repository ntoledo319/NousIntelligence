#!/usr/bin/env python3
"""
Targeted Optimization Report - Fast Deep Analysis
Focus on critical optimization areas without timeout
"""
import os
import re
import json
from pathlib import Path
from collections import defaultdict, Counter

def analyze_critical_areas():
    """Analyze critical optimization areas efficiently"""
    
    report = {
        'timestamp': '2025-06-28T12:00:00Z',
        'codebase_overview': {},
        'critical_findings': {},
        'optimization_plan': {},
        'immediate_actions': []
    }
    
    print("🔍 TARGETED OPTIMIZATION ANALYSIS")
    print("=" * 50)
    
    # 1. CODEBASE OVERVIEW
    print("📊 Analyzing codebase overview...")
    
    # Quick file count
    py_files = list(Path('.').rglob('*.py'))
    total_size = sum(f.stat().st_size for f in Path('.').rglob('*') if f.is_file())
    
    report['codebase_overview'] = {
        'total_python_files': len(py_files),
        'total_size_mb': total_size / (1024 * 1024),
        'key_directories': {
            'routes': len(list(Path('routes').glob('*.py'))) if Path('routes').exists() else 0,
            'utils': len(list(Path('utils').glob('*.py'))) if Path('utils').exists() else 0,
            'models': len(list(Path('models').glob('*.py'))) if Path('models').exists() else 0,
            'services': len(list(Path('services').glob('*.py'))) if Path('services').exists() else 0
        }
    }
    
    # 2. DEPENDENCY ANALYSIS
    print("📦 Analyzing dependencies...")
    
    dependency_issues = {}
    pyproject_path = Path('pyproject.toml')
    
    if pyproject_path.exists():
        content = pyproject_path.read_text()
        
        # Count duplicates
        numpy_count = content.lower().count('numpy')
        jwt_count = content.lower().count('jwt') + content.lower().count('pyjwt')
        
        # Find heavyweight dependencies
        heavyweight_deps = []
        for line in content.splitlines():
            if any(heavy in line.lower() for heavy in ['opencv', 'tensorflow', 'torch', 'scikit-learn', 'librosa']):
                heavyweight_deps.append(line.strip())
        
        dependency_issues = {
            'duplicate_numpy': numpy_count > 1,
            'duplicate_jwt': jwt_count > 1,
            'heavyweight_count': len(heavyweight_deps),
            'heavyweight_deps': heavyweight_deps
        }
    
    # 3. UTILS CONSOLIDATION ANALYSIS
    print("🔧 Analyzing utils consolidation...")
    
    utils_analysis = {}
    utils_path = Path('utils')
    
    if utils_path.exists():
        util_files = list(utils_path.glob('*.py'))
        
        # Group by service type
        service_groups = defaultdict(list)
        for util_file in util_files:
            name = util_file.stem.lower()
            
            if any(word in name for word in ['google', 'gmail', 'drive', 'docs', 'maps', 'photos']):
                service_groups['google_services'].append(name)
            elif any(word in name for word in ['spotify', 'music']):
                service_groups['spotify_services'].append(name)
            elif any(word in name for word in ['ai', 'gemini', 'openai', 'huggingface']):
                service_groups['ai_services'].append(name)
            elif any(word in name for word in ['auth', 'security', 'jwt', 'two_factor']):
                service_groups['security_services'].append(name)
            elif 'helper' in name:
                service_groups['helper_utilities'].append(name)
            elif any(word in name for word in ['db', 'database']):
                service_groups['database_services'].append(name)
        
        # Find consolidation opportunities
        consolidation_opportunities = {}
        for group, files in service_groups.items():
            if len(files) > 2:
                consolidation_opportunities[group] = {
                    'current_files': len(files),
                    'files': files,
                    'potential_reduction': len(files) - 1
                }
        
        utils_analysis = {
            'total_utils': len(util_files),
            'service_groups': dict(service_groups),
            'consolidation_opportunities': consolidation_opportunities
        }
    
    # 4. ROUTES OPTIMIZATION ANALYSIS
    print("🛣️ Analyzing routes optimization...")
    
    routes_analysis = {}
    routes_path = Path('routes')
    
    if routes_path.exists():
        route_files = list(routes_path.glob('*.py'))
        
        # Check for consolidated files
        consolidated_files = [f for f in route_files if 'consolidated' in f.name.lower()]
        regular_files = [f for f in route_files if 'consolidated' not in f.name.lower() and f.name != '__init__.py']
        
        routes_analysis = {
            'total_route_files': len(route_files),
            'consolidated_files': len(consolidated_files),
            'regular_files': len(regular_files),
            'consolidation_progress': len(consolidated_files) / len(route_files) * 100 if route_files else 0
        }
    
    # 5. PERFORMANCE HOTSPOTS
    print("⚡ Analyzing performance hotspots...")
    
    performance_issues = []
    
    # Check app.py for import issues
    app_py = Path('app.py')
    if app_py.exists():
        content = app_py.read_text()
        import_error_count = content.count('except ImportError:')
        try_import_count = content.count('try:')
        
        if import_error_count > 5:
            performance_issues.append({
                'file': 'app.py',
                'issue': f'{import_error_count} optional imports with error handling',
                'impact': 'Slower application startup',
                'priority': 'MEDIUM'
            })
    
    # Check for database connection patterns
    config_files = ['config/app_config.py', 'database.py']
    for config_file in config_files:
        config_path = Path(config_file)
        if config_path.exists():
            content = config_path.read_text()
            if 'pool_recycle' not in content and 'SQLALCHEMY' in content:
                performance_issues.append({
                    'file': config_file,
                    'issue': 'Missing database connection pooling configuration',
                    'impact': 'Potential connection leaks',
                    'priority': 'HIGH'
                })
    
    # 6. CACHE AND STORAGE ANALYSIS
    print("💾 Analyzing cache and storage...")
    
    cache_analysis = {}
    cache_dirs = ['__pycache__', 'flask_session', '.pytest_cache', 'instance']
    
    total_cache_size = 0
    for cache_dir in cache_dirs:
        cache_path = Path(cache_dir)
        if cache_path.exists():
            cache_size = sum(f.stat().st_size for f in cache_path.rglob('*') if f.is_file())
            total_cache_size += cache_size
            cache_analysis[cache_dir] = cache_size / (1024 * 1024)  # MB
    
    cache_analysis['total_cache_mb'] = total_cache_size / (1024 * 1024)
    
    # Store findings
    report['critical_findings'] = {
        'dependencies': dependency_issues,
        'utils_consolidation': utils_analysis,
        'routes_optimization': routes_analysis,
        'performance_hotspots': performance_issues,
        'cache_storage': cache_analysis
    }
    
    # 7. GENERATE OPTIMIZATION PLAN
    print("📋 Generating optimization plan...")
    
    # High Priority Actions
    high_priority = []
    
    if dependency_issues.get('duplicate_numpy') or dependency_issues.get('duplicate_jwt'):
        high_priority.append({
            'action': 'Remove duplicate dependencies',
            'details': 'Clean up duplicate numpy and JWT entries in pyproject.toml',
            'impact': 'Faster builds, cleaner dependency tree',
            'effort': 'LOW'
        })
    
    if dependency_issues.get('heavyweight_count', 0) > 0:
        high_priority.append({
            'action': 'Optimize heavyweight dependencies',
            'details': f'Move {dependency_issues["heavyweight_count"]} heavy deps to optional-dependencies',
            'impact': '30-50% faster builds for basic features',
            'effort': 'MEDIUM'
        })
    
    # Medium Priority Actions
    medium_priority = []
    
    consolidation_opps = utils_analysis.get('consolidation_opportunities', {})
    for group, details in consolidation_opps.items():
        medium_priority.append({
            'action': f'Consolidate {group}',
            'details': f'Merge {details["current_files"]} files into unified_{group}.py',
            'impact': f'Reduce {details["potential_reduction"]} files, better organization',
            'effort': 'MEDIUM'
        })
    
    # Low Priority Actions
    low_priority = []
    
    if cache_analysis.get('total_cache_mb', 0) > 10:
        low_priority.append({
            'action': 'Clean up cache directories',
            'details': f'Remove {cache_analysis["total_cache_mb"]:.1f}MB of cache data',
            'impact': 'Cleaner development environment',
            'effort': 'LOW'
        })
    
    report['optimization_plan'] = {
        'high_priority': high_priority,
        'medium_priority': medium_priority,
        'low_priority': low_priority
    }
    
    # 8. IMMEDIATE ACTIONS
    immediate_actions = []
    
    # Most impactful immediate actions
    if dependency_issues.get('duplicate_numpy') or dependency_issues.get('duplicate_jwt'):
        immediate_actions.append('Fix duplicate dependencies in pyproject.toml')
    
    if len(consolidation_opps) > 0:
        top_consolidation = max(consolidation_opps.items(), key=lambda x: x[1]['potential_reduction'])
        immediate_actions.append(f'Consolidate {top_consolidation[0]} ({top_consolidation[1]["current_files"]} files)')
    
    if cache_analysis.get('total_cache_mb', 0) > 20:
        immediate_actions.append('Clean up large cache directories')
    
    report['immediate_actions'] = immediate_actions
    
    return report

def print_comprehensive_report(report):
    """Print the comprehensive optimization report"""
    
    print("\n" + "="*70)
    print(" COMPREHENSIVE CODEBASE OPTIMIZATION REPORT")
    print("="*70)
    
    # Overview
    overview = report['codebase_overview']
    print(f"\n📊 CODEBASE OVERVIEW:")
    print(f"   Total Size: {overview['total_size_mb']:.1f}MB")
    print(f"   Python Files: {overview['total_python_files']:,}")
    print(f"   Routes: {overview['key_directories']['routes']} files")
    print(f"   Utils: {overview['key_directories']['utils']} files")
    print(f"   Models: {overview['key_directories']['models']} files")
    print(f"   Services: {overview['key_directories']['services']} files")
    
    # Critical Findings
    findings = report['critical_findings']
    
    print(f"\n🚨 CRITICAL FINDINGS:")
    
    # Dependencies
    deps = findings['dependencies']
    print(f"   📦 Dependencies:")
    if deps.get('duplicate_numpy') or deps.get('duplicate_jwt'):
        print(f"      ⚠️  Duplicate dependencies detected!")
        if deps.get('duplicate_numpy'):
            print(f"         - numpy appears multiple times")
        if deps.get('duplicate_jwt'):
            print(f"         - JWT packages appear multiple times")
    
    if deps.get('heavyweight_count', 0) > 0:
        print(f"      ⚠️  {deps['heavyweight_count']} heavyweight dependencies")
        for dep in deps['heavyweight_deps'][:3]:  # Show top 3
            print(f"         - {dep}")
    
    # Utils Consolidation
    utils = findings['utils_consolidation']
    print(f"\n   🔧 Utils Consolidation:")
    print(f"      Total Utils: {utils.get('total_utils', 0)}")
    
    consolidation_opps = utils.get('consolidation_opportunities', {})
    if consolidation_opps:
        print(f"      Consolidation Opportunities:")
        for group, details in consolidation_opps.items():
            print(f"         • {group}: {details['current_files']} files → 1 file ({details['potential_reduction']} reduction)")
    
    # Routes
    routes = findings['routes_optimization']
    if routes:
        print(f"\n   🛣️  Routes Optimization:")
        print(f"      Total Route Files: {routes['total_route_files']}")
        print(f"      Consolidated Files: {routes['consolidated_files']}")
        print(f"      Consolidation Progress: {routes['consolidation_progress']:.1f}%")
    
    # Performance
    perf_issues = findings['performance_hotspots']
    if perf_issues:
        print(f"\n   ⚡ Performance Issues:")
        for issue in perf_issues:
            print(f"      [{issue['priority']}] {issue['file']}: {issue['issue']}")
    
    # Cache
    cache = findings['cache_storage']
    print(f"\n   💾 Cache Analysis:")
    print(f"      Total Cache Size: {cache.get('total_cache_mb', 0):.1f}MB")
    for cache_dir, size_mb in cache.items():
        if cache_dir != 'total_cache_mb' and size_mb > 1:
            print(f"         - {cache_dir}: {size_mb:.1f}MB")
    
    # Optimization Plan
    plan = report['optimization_plan']
    
    print(f"\n🎯 OPTIMIZATION PLAN:")
    
    if plan['high_priority']:
        print(f"\n   🔴 HIGH PRIORITY ({len(plan['high_priority'])} actions):")
        for action in plan['high_priority']:
            print(f"      • {action['action']}")
            print(f"        Details: {action['details']}")
            print(f"        Impact: {action['impact']}")
            print(f"        Effort: {action['effort']}")
    
    if plan['medium_priority']:
        print(f"\n   🟡 MEDIUM PRIORITY ({len(plan['medium_priority'])} actions):")
        for action in plan['medium_priority']:
            print(f"      • {action['action']}")
            print(f"        Impact: {action['impact']}")
    
    if plan['low_priority']:
        print(f"\n   🟢 LOW PRIORITY ({len(plan['low_priority'])} actions):")
        for action in plan['low_priority']:
            print(f"      • {action['action']}")
            print(f"        Impact: {action['impact']}")
    
    # Immediate Actions
    print(f"\n⚡ IMMEDIATE ACTIONS RECOMMENDED:")
    for i, action in enumerate(report['immediate_actions'], 1):
        print(f"   {i}. {action}")
    
    print(f"\n📊 SUMMARY:")
    total_actions = len(plan['high_priority']) + len(plan['medium_priority']) + len(plan['low_priority'])
    print(f"   Total optimization opportunities: {total_actions}")
    print(f"   High impact actions: {len(plan['high_priority'])}")
    print(f"   Expected improvements: 30-50% faster builds, better maintainability")
    
    print("\n" + "="*70)

def main():
    """Execute targeted optimization analysis"""
    report = analyze_critical_areas()
    print_comprehensive_report(report)
    
    # Save report
    with open('targeted_optimization_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Report saved to: targeted_optimization_report.json")
    
    return report

if __name__ == '__main__':
    main()