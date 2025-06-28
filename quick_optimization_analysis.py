#!/usr/bin/env python3
"""
Quick Optimization Analysis for NOUS Codebase
Focus on high-impact optimization opportunities
"""
import os
import re
import json
from pathlib import Path
from collections import defaultdict, Counter

def analyze_codebase():
    """Quick analysis of key optimization areas"""
    print("🔍 Quick Optimization Analysis Starting...")
    
    analysis = {
        'file_counts': {},
        'size_analysis': {},
        'dependency_issues': {},
        'consolidation_opportunities': {},
        'performance_issues': {},
        'cache_analysis': {},
        'recommendations': []
    }
    
    # 1. File count analysis
    print("📊 Analyzing file structure...")
    for directory in ['routes', 'utils', 'models', 'templates', 'static']:
        if Path(directory).exists():
            py_files = list(Path(directory).glob('*.py'))
            analysis['file_counts'][directory] = len(py_files)
    
    # 2. Size analysis
    print("📏 Analyzing size...")
    total_size = 0
    cache_size = 0
    for item in Path('.').rglob('*'):
        if item.is_file():
            size = item.stat().st_size
            total_size += size
            if any(cache_dir in str(item) for cache_dir in ['__pycache__', 'flask_session', '.pytest_cache']):
                cache_size += size
    
    analysis['size_analysis'] = {
        'total_mb': total_size / (1024 * 1024),
        'cache_mb': cache_size / (1024 * 1024)
    }
    
    # 3. Dependency analysis
    print("📦 Analyzing dependencies...")
    pyproject_path = Path('pyproject.toml')
    if pyproject_path.exists():
        content = pyproject_path.read_text()
        
        # Count numpy duplicates
        numpy_count = content.lower().count('numpy')
        jwt_count = content.lower().count('jwt')
        
        analysis['dependency_issues'] = {
            'numpy_mentions': numpy_count,
            'jwt_mentions': jwt_count,
            'has_duplicates': numpy_count > 1 or jwt_count > 1
        }
    
    # 4. Utils consolidation analysis
    print("🔧 Analyzing utils consolidation...")
    utils_path = Path('utils')
    if utils_path.exists():
        util_files = list(utils_path.glob('*.py'))
        
        # Group by service type
        service_groups = defaultdict(list)
        for util_file in util_files:
            name = util_file.stem.lower()
            if 'google' in name:
                service_groups['google'].append(name)
            elif 'spotify' in name:
                service_groups['spotify'].append(name)
            elif 'ai' in name or 'gemini' in name:
                service_groups['ai'].append(name)
            elif 'security' in name or 'auth' in name:
                service_groups['security'].append(name)
            elif 'helper' in name:
                service_groups['helpers'].append(name)
        
        analysis['consolidation_opportunities'] = {
            group: files for group, files in service_groups.items() if len(files) > 2
        }
    
    # 5. Routes analysis
    print("🛣️ Analyzing routes...")
    routes_path = Path('routes')
    if routes_path.exists():
        route_files = list(routes_path.glob('*.py'))
        analysis['file_counts']['routes_total'] = len(route_files)
        
        # Check for consolidated files
        consolidated_files = [f for f in route_files if 'consolidated' in f.name]
        analysis['file_counts']['consolidated_routes'] = len(consolidated_files)
    
    # 6. Performance patterns
    print("⚡ Checking performance patterns...")
    performance_issues = []
    
    # Check app.py for common issues
    app_py = Path('app.py')
    if app_py.exists():
        content = app_py.read_text()
        if 'try:' in content and 'except ImportError:' in content:
            import_error_count = content.count('except ImportError:')
            performance_issues.append(f"Many optional imports ({import_error_count}) - may slow startup")
    
    analysis['performance_issues'] = performance_issues
    
    # 7. Generate recommendations
    print("💡 Generating recommendations...")
    recommendations = []
    
    # Dependency recommendations
    if analysis['dependency_issues'].get('has_duplicates'):
        recommendations.append({
            'priority': 'HIGH',
            'category': 'Dependencies',
            'issue': 'Duplicate dependencies detected',
            'action': 'Remove duplicate numpy and JWT entries from pyproject.toml',
            'impact': 'Faster builds, cleaner dependency tree'
        })
    
    # Utils consolidation
    consolidation_opps = analysis['consolidation_opportunities']
    if consolidation_opps:
        for service, files in consolidation_opps.items():
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Code Organization',
                'issue': f'{len(files)} separate {service} utilities',
                'action': f'Consolidate into unified_{service}_service.py',
                'impact': 'Reduced imports, better maintainability'
            })
    
    # Cache cleanup
    if analysis['size_analysis']['cache_mb'] > 10:
        recommendations.append({
            'priority': 'LOW',
            'category': 'Maintenance',
            'issue': f"Large cache size ({analysis['size_analysis']['cache_mb']:.1f}MB)",
            'action': 'Clean up __pycache__ and flask_session directories',
            'impact': 'Reduced disk usage'
        })
    
    # Routes optimization
    if analysis['file_counts'].get('routes_total', 0) > 30:
        recommendations.append({
            'priority': 'MEDIUM',
            'category': 'Architecture',
            'issue': f"Many route files ({analysis['file_counts']['routes_total']})",
            'action': 'Continue consolidating related routes into blueprint modules',
            'impact': 'Better organization, fewer files to maintain'
        })
    
    analysis['recommendations'] = recommendations
    
    return analysis

def print_report(analysis):
    """Print formatted analysis report"""
    print("\n" + "="*60)
    print(" NOUS CODEBASE OPTIMIZATION ANALYSIS REPORT")
    print("="*60)
    
    print(f"\n📊 CODEBASE METRICS:")
    print(f"   Total Size: {analysis['size_analysis']['total_mb']:.1f}MB")
    print(f"   Cache Size: {analysis['size_analysis']['cache_mb']:.1f}MB")
    
    for directory, count in analysis['file_counts'].items():
        print(f"   {directory.title()}: {count} files")
    
    print(f"\n📦 DEPENDENCY ANALYSIS:")
    dep_issues = analysis['dependency_issues']
    if dep_issues.get('has_duplicates'):
        print(f"   ⚠️  Duplicate dependencies detected!")
        print(f"   - numpy mentioned {dep_issues['numpy_mentions']} times")
        print(f"   - JWT mentioned {dep_issues['jwt_mentions']} times")
    else:
        print("   ✅ No obvious duplicate dependencies")
    
    print(f"\n🔧 CONSOLIDATION OPPORTUNITIES:")
    if analysis['consolidation_opportunities']:
        for service, files in analysis['consolidation_opportunities'].items():
            print(f"   📁 {service.title()}: {len(files)} files can be consolidated")
            print(f"      Files: {', '.join(files[:3])}{'...' if len(files) > 3 else ''}")
    else:
        print("   ✅ No major consolidation opportunities found")
    
    print(f"\n⚡ PERFORMANCE ANALYSIS:")
    if analysis['performance_issues']:
        for issue in analysis['performance_issues']:
            print(f"   ⚠️  {issue}")
    else:
        print("   ✅ No major performance issues detected")
    
    print(f"\n💡 OPTIMIZATION RECOMMENDATIONS:")
    recommendations = analysis['recommendations']
    
    high_priority = [r for r in recommendations if r['priority'] == 'HIGH']
    medium_priority = [r for r in recommendations if r['priority'] == 'MEDIUM']
    low_priority = [r for r in recommendations if r['priority'] == 'LOW']
    
    if high_priority:
        print(f"\n   🔴 HIGH PRIORITY ({len(high_priority)} items):")
        for rec in high_priority:
            print(f"      • {rec['issue']}")
            print(f"        Action: {rec['action']}")
            print(f"        Impact: {rec['impact']}")
    
    if medium_priority:
        print(f"\n   🟡 MEDIUM PRIORITY ({len(medium_priority)} items):")
        for rec in medium_priority:
            print(f"      • {rec['issue']}")
            print(f"        Action: {rec['action']}")
    
    if low_priority:
        print(f"\n   🟢 LOW PRIORITY ({len(low_priority)} items):")
        for rec in low_priority:
            print(f"      • {rec['issue']}")
            print(f"        Action: {rec['action']}")
    
    print(f"\n📋 SUMMARY:")
    print(f"   Total recommendations: {len(recommendations)}")
    print(f"   High priority: {len(high_priority)}")
    print(f"   Medium priority: {len(medium_priority)}")
    print(f"   Low priority: {len(low_priority)}")
    
    if not recommendations:
        print("   ✅ Codebase appears well-optimized!")
    
    print("\n" + "="*60)

def main():
    """Run analysis and generate report"""
    analysis = analyze_codebase()
    print_report(analysis)
    
    # Save detailed results
    with open('optimization_analysis_results.json', 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: optimization_analysis_results.json")
    return analysis

if __name__ == '__main__':
    main()