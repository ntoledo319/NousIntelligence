#!/usr/bin/env python3
"""
Comprehensive Feature Auditor for NOUS Platform
Deep dive analysis of actual vs documented features
"""

import os
import ast
import json
import importlib.util
import inspect
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set
import re

class ComprehensiveFeatureAuditor:
    """Audits actual implemented features vs documentation claims"""
    
    def __init__(self):
        self.results = {
            'analysis_timestamp': datetime.now().isoformat(),
            'actual_features': {},
            'documented_features': {},
            'discrepancies': [],
            'accuracy_score': 0,
            'recommendations': []
        }
        
        # Skip problematic directories
        self.skip_dirs = {
            '__pycache__', '.git', 'node_modules', 'venv', 'env',
            'cache', 'logs', 'instance', 'migrations', 'attached_assets',
            'security_fixes_backup', 'verification', 'tests/__pycache__'
        }
        
    def audit_complete_system(self) -> Dict[str, Any]:
        """Perform comprehensive system audit"""
        print("🔍 Starting comprehensive feature audit...")
        
        # Analyze actual implementation
        self._analyze_actual_implementation()
        
        # Analyze documentation claims
        self._analyze_documentation_claims()
        
        # Compare and find discrepancies
        self._compare_features()
        
        # Generate accuracy score
        self._calculate_accuracy()
        
        # Generate recommendations
        self._generate_recommendations()
        
        return self.results
    
    def _analyze_actual_implementation(self):
        """Analyze what's actually implemented in the codebase"""
        print("📊 Analyzing actual implementation...")
        
        actual = {
            'models': self._analyze_models(),
            'routes': self._analyze_routes(),
            'services': self._analyze_services(),
            'utilities': self._analyze_utilities(),
            'api_endpoints': self._analyze_api_endpoints(),
            'templates': self._analyze_templates(),
            'database_tables': self._analyze_database_structure(),
            'ai_services': self._analyze_ai_services(),
            'authentication': self._analyze_authentication(),
            'integrations': self._analyze_integrations()
        }
        
        self.results['actual_features'] = actual
        
    def _analyze_models(self) -> Dict[str, Any]:
        """Analyze database models"""
        models_info = {
            'count': 0,
            'files': [],
            'models': [],
            'relationships': []
        }
        
        models_dir = Path('models')
        if models_dir.exists():
            for py_file in models_dir.glob('*.py'):
                if py_file.name.startswith('__'):
                    continue
                    
                models_info['files'].append(str(py_file))
                
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        tree = ast.parse(content)
                        
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            # Look for SQLAlchemy models
                            for base in node.bases:
                                if (isinstance(base, ast.Attribute) and 
                                    base.attr == 'Model') or \
                                   (isinstance(base, ast.Name) and 
                                    base.id in ['UserMixin', 'Base']):
                                    models_info['models'].append({
                                        'name': node.name,
                                        'file': str(py_file),
                                        'line': node.lineno
                                    })
                                    models_info['count'] += 1
                                    break
                                    
                except Exception as e:
                    print(f"⚠️  Error analyzing {py_file}: {e}")
                    
        return models_info
    
    def _analyze_routes(self) -> Dict[str, Any]:
        """Analyze route implementations"""
        routes_info = {
            'count': 0,
            'files': [],
            'blueprints': [],
            'endpoints': []
        }
        
        routes_dir = Path('routes')
        if routes_dir.exists():
            for py_file in routes_dir.glob('*.py'):
                if py_file.name.startswith('__'):
                    continue
                    
                routes_info['files'].append(str(py_file))
                
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Count route decorators
                    route_patterns = [
                        r'@\w+\.route\(',
                        r'@app\.route\(',
                        r'@bp\.route\(',
                        r'@\w+_bp\.route\('
                    ]
                    
                    for pattern in route_patterns:
                        matches = re.findall(pattern, content)
                        routes_info['count'] += len(matches)
                    
                    # Find blueprint definitions
                    blueprint_matches = re.findall(r'Blueprint\([\'"](\w+)[\'"]', content)
                    routes_info['blueprints'].extend(blueprint_matches)
                    
                except Exception as e:
                    print(f"⚠️  Error analyzing {py_file}: {e}")
                    
        return routes_info
    
    def _analyze_services(self) -> Dict[str, Any]:
        """Analyze service layer implementations"""
        services_info = {
            'count': 0,
            'files': [],
            'services': []
        }
        
        services_dir = Path('services')
        if services_dir.exists():
            for py_file in services_dir.glob('*.py'):
                if py_file.name.startswith('__'):
                    continue
                    
                services_info['files'].append(str(py_file))
                services_info['count'] += 1
                
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        tree = ast.parse(content)
                    
                    # Find service classes
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            services_info['services'].append({
                                'name': node.name,
                                'file': str(py_file),
                                'methods': [method.name for method in node.body 
                                          if isinstance(method, ast.FunctionDef)]
                            })
                            
                except Exception as e:
                    print(f"⚠️  Error analyzing {py_file}: {e}")
                    
        return services_info
    
    def _analyze_utilities(self) -> Dict[str, Any]:
        """Analyze utility modules"""
        utils_info = {
            'count': 0,
            'files': [],
            'utilities': []
        }
        
        utils_dir = Path('utils')
        if utils_dir.exists():
            for py_file in utils_dir.glob('*.py'):
                if py_file.name.startswith('__'):
                    continue
                    
                utils_info['files'].append(str(py_file))
                utils_info['count'] += 1
                
                # Extract key utility info
                utils_info['utilities'].append({
                    'name': py_file.stem,
                    'file': str(py_file),
                    'size_kb': py_file.stat().st_size / 1024
                })
                    
        return utils_info
    
    def _analyze_api_endpoints(self) -> Dict[str, Any]:
        """Analyze API endpoint structure"""
        api_info = {
            'count': 0,
            'files': [],
            'endpoints': []
        }
        
        # Check api directory
        api_dir = Path('api')
        if api_dir.exists():
            for py_file in api_dir.glob('*.py'):
                if py_file.name.startswith('__'):
                    continue
                    
                api_info['files'].append(str(py_file))
                
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Count API endpoints
                    route_matches = re.findall(r'@\w+\.route\([\'"]([^\'"]+)[\'"]', content)
                    api_info['endpoints'].extend(route_matches)
                    api_info['count'] += len(route_matches)
                    
                except Exception as e:
                    print(f"⚠️  Error analyzing {py_file}: {e}")
                    
        return api_info
    
    def _analyze_templates(self) -> Dict[str, Any]:
        """Analyze template files"""
        templates_info = {
            'count': 0,
            'files': [],
            'templates': []
        }
        
        templates_dir = Path('templates')
        if templates_dir.exists():
            for html_file in templates_dir.glob('**/*.html'):
                templates_info['files'].append(str(html_file))
                templates_info['count'] += 1
                
                templates_info['templates'].append({
                    'name': html_file.name,
                    'path': str(html_file),
                    'size_kb': html_file.stat().st_size / 1024
                })
                    
        return templates_info
    
    def _analyze_database_structure(self) -> Dict[str, Any]:
        """Analyze database structure from models"""
        db_info = {
            'tables_estimated': 0,
            'relationships': 0,
            'foreign_keys': 0
        }
        
        # This would require importing models safely
        # For now, estimate from model files
        models_dir = Path('models')
        if models_dir.exists():
            for py_file in models_dir.glob('*.py'):
                if py_file.name.startswith('__'):
                    continue
                    
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Count likely table definitions
                    table_matches = re.findall(r'__tablename__\s*=', content)
                    db_info['tables_estimated'] += len(table_matches)
                    
                    # Count relationships
                    rel_matches = re.findall(r'db\.relationship\(', content)
                    db_info['relationships'] += len(rel_matches)
                    
                    # Count foreign keys
                    fk_matches = re.findall(r'ForeignKey\(', content)
                    db_info['foreign_keys'] += len(fk_matches)
                    
                except Exception as e:
                    print(f"⚠️  Error analyzing {py_file}: {e}")
                    
        return db_info
    
    def _analyze_ai_services(self) -> Dict[str, Any]:
        """Analyze AI service implementations"""
        ai_info = {
            'providers': [],
            'optimization_systems': [],
            'cost_management': False
        }
        
        # Check for AI-related files
        ai_patterns = [
            'ai_', 'gemini_', 'openai_', 'cost_optim', 
            'brain_', 'enhanced_ai', 'unified_ai'
        ]
        
        for pattern in ai_patterns:
            matches = list(Path('.').rglob(f'*{pattern}*.py'))
            for match in matches:
                if any(skip in str(match) for skip in self.skip_dirs):
                    continue
                    
                ai_info['optimization_systems'].append({
                    'name': match.name,
                    'path': str(match),
                    'size_kb': match.stat().st_size / 1024
                })
                
        # Check for provider mentions in code
        try:
            utils_dir = Path('utils')
            if utils_dir.exists():
                for py_file in utils_dir.glob('*ai*.py'):
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    providers = ['openai', 'gemini', 'openrouter', 'huggingface']
                    for provider in providers:
                        if provider.lower() in content.lower():
                            if provider not in ai_info['providers']:
                                ai_info['providers'].append(provider)
                    
                    if 'cost' in content.lower():
                        ai_info['cost_management'] = True
                        
        except Exception as e:
            print(f"⚠️  Error analyzing AI services: {e}")
                    
        return ai_info
    
    def _analyze_authentication(self) -> Dict[str, Any]:
        """Analyze authentication systems"""
        auth_info = {
            'methods': [],
            'oauth_providers': [],
            'security_features': []
        }
        
        # Check for auth-related files
        auth_files = list(Path('.').rglob('*auth*.py'))
        auth_files.extend(list(Path('.').rglob('*oauth*.py')))
        
        for auth_file in auth_files:
            if any(skip in str(auth_file) for skip in self.skip_dirs):
                continue
                
            try:
                with open(auth_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for authentication methods
                if 'google' in content.lower():
                    auth_info['oauth_providers'].append('Google')
                if 'session' in content.lower():
                    auth_info['methods'].append('Session-based')
                if 'token' in content.lower():
                    auth_info['methods'].append('Token-based')
                if 'flask_login' in content.lower():
                    auth_info['methods'].append('Flask-Login')
                    
                # Check for security features
                if 'csrf' in content.lower():
                    auth_info['security_features'].append('CSRF Protection')
                if 'rate_limit' in content.lower():
                    auth_info['security_features'].append('Rate Limiting')
                    
            except Exception as e:
                print(f"⚠️  Error analyzing {auth_file}: {e}")
                
        return auth_info
    
    def _analyze_integrations(self) -> Dict[str, Any]:
        """Analyze external service integrations"""
        integrations_info = {
            'google_services': [],
            'external_apis': [],
            'databases': []
        }
        
        # Search for integration patterns
        integration_patterns = {
            'google_services': ['gmail', 'drive', 'calendar', 'meet', 'tasks'],
            'external_apis': ['spotify', 'weather', 'maps'],
            'databases': ['postgresql', 'sqlite', 'sqlalchemy']
        }
        
        # Check all Python files for integration mentions
        for py_file in Path('.').rglob('*.py'):
            if any(skip in str(py_file) for skip in self.skip_dirs):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                
                for category, services in integration_patterns.items():
                    for service in services:
                        if service in content:
                            if service not in integrations_info[category]:
                                integrations_info[category].append(service)
                                
            except Exception as e:
                continue  # Skip problematic files
                
        return integrations_info
    
    def _analyze_documentation_claims(self):
        """Analyze what the documentation claims is implemented"""
        print("📚 Analyzing documentation claims...")
        
        doc_features = {
            'mental_health_features': 0,
            'ai_features': 0,
            'api_endpoints_claimed': 0,
            'database_models_claimed': 0,
            'cost_claims': {},
            'integration_claims': []
        }
        
        # Analyze key documentation files
        doc_files = [
            'docs/FEATURES.md',
            'docs/API_REFERENCE.md',
            'docs/COMPREHENSIVE_FEATURES_ANALYSIS.md',
            'NOUS_COMPREHENSIVE_EFFICIENCY_ANALYSIS.md',
            'PITCH_DECK.md'
        ]
        
        for doc_file in doc_files:
            if Path(doc_file).exists():
                try:
                    with open(doc_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract numerical claims
                    model_matches = re.findall(r'(\d+)\+?\s*(?:database\s*)?models?', content, re.IGNORECASE)
                    if model_matches:
                        doc_features['database_models_claimed'] = max(int(m) for m in model_matches)
                    
                    endpoint_matches = re.findall(r'(\d+)\+?\s*(?:API\s*)?endpoints?', content, re.IGNORECASE)
                    if endpoint_matches:
                        doc_features['api_endpoints_claimed'] = max(int(m) for m in endpoint_matches)
                    
                    # Extract cost claims
                    cost_matches = re.findall(r'\$(\d+\.?\d*)', content)
                    if cost_matches:
                        doc_features['cost_claims'][doc_file] = [float(c) for c in cost_matches]
                    
                    # Count feature mentions
                    mental_health_terms = ['CBT', 'DBT', 'therapy', 'mental health', 'therapeutic']
                    for term in mental_health_terms:
                        doc_features['mental_health_features'] += len(re.findall(term, content, re.IGNORECASE))
                    
                    ai_terms = ['AI', 'artificial intelligence', 'machine learning', 'optimization']
                    for term in ai_terms:
                        doc_features['ai_features'] += len(re.findall(term, content, re.IGNORECASE))
                        
                except Exception as e:
                    print(f"⚠️  Error analyzing {doc_file}: {e}")
        
        self.results['documented_features'] = doc_features
    
    def _compare_features(self):
        """Compare actual vs documented features"""
        print("⚖️  Comparing actual vs documented features...")
        
        actual = self.results['actual_features']
        documented = self.results['documented_features']
        
        discrepancies = []
        
        # Compare model counts
        actual_models = actual['models']['count']
        claimed_models = documented.get('database_models_claimed', 0)
        if claimed_models > 0 and abs(actual_models - claimed_models) > 10:
            discrepancies.append({
                'type': 'model_count',
                'actual': actual_models,
                'claimed': claimed_models,
                'severity': 'high' if abs(actual_models - claimed_models) > 50 else 'medium'
            })
        
        # Compare API endpoint counts
        actual_endpoints = actual['routes']['count'] + actual['api_endpoints']['count']
        claimed_endpoints = documented.get('api_endpoints_claimed', 0)
        if claimed_endpoints > 0 and abs(actual_endpoints - claimed_endpoints) > 20:
            discrepancies.append({
                'type': 'endpoint_count',
                'actual': actual_endpoints,
                'claimed': claimed_endpoints,
                'severity': 'high' if abs(actual_endpoints - claimed_endpoints) > 100 else 'medium'
            })
        
        # Check for missing critical features
        if actual['ai_services']['cost_management'] == False and documented['ai_features'] > 10:
            discrepancies.append({
                'type': 'missing_cost_optimization',
                'actual': 'Not implemented',
                'claimed': 'Heavily documented',
                'severity': 'high'
            })
        
        self.results['discrepancies'] = discrepancies
    
    def _calculate_accuracy(self):
        """Calculate documentation accuracy score"""
        print("📊 Calculating accuracy score...")
        
        total_claims = len(self.results['documented_features'])
        total_discrepancies = len(self.results['discrepancies'])
        
        if total_claims == 0:
            accuracy = 0
        else:
            # Weight discrepancies by severity
            severity_weights = {'low': 1, 'medium': 3, 'high': 5}
            weighted_discrepancies = sum(
                severity_weights.get(d.get('severity', 'medium'), 3) 
                for d in self.results['discrepancies']
            )
            
            # Calculate accuracy (0-100)
            max_possible_score = total_claims * 5  # Assuming all high severity
            accuracy = max(0, 100 - (weighted_discrepancies / max_possible_score * 100))
        
        self.results['accuracy_score'] = round(accuracy, 1)
    
    def _generate_recommendations(self):
        """Generate recommendations for fixing documentation"""
        print("💡 Generating recommendations...")
        
        recommendations = []
        
        for discrepancy in self.results['discrepancies']:
            if discrepancy['type'] == 'model_count':
                recommendations.append(
                    f"Update documentation to reflect actual {discrepancy['actual']} models "
                    f"instead of claimed {discrepancy['claimed']}"
                )
            elif discrepancy['type'] == 'endpoint_count':
                recommendations.append(
                    f"Verify and update API endpoint count: actual {discrepancy['actual']} "
                    f"vs claimed {discrepancy['claimed']}"
                )
            elif discrepancy['type'] == 'missing_cost_optimization':
                recommendations.append(
                    "Either implement the documented cost optimization features "
                    "or remove/reduce the claims in documentation"
                )
        
        # General recommendations
        actual = self.results['actual_features']
        
        if actual['models']['count'] > 0:
            recommendations.append(
                f"Document the {actual['models']['count']} database models with their relationships"
            )
        
        if actual['services']['count'] > 0:
            recommendations.append(
                f"Create API documentation for the {actual['services']['count']} service modules"
            )
        
        if len(actual['ai_services']['providers']) > 0:
            recommendations.append(
                f"Document AI provider integration: {', '.join(actual['ai_services']['providers'])}"
            )
        
        self.results['recommendations'] = recommendations
    
    def save_report(self, filename: str = None):
        """Save audit report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"feature_audit_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Report saved to: {filename}")
        return filename
    
    def print_summary(self):
        """Print audit summary"""
        actual = self.results['actual_features']
        
        print(f"\n{'='*60}")
        print("🎯 COMPREHENSIVE FEATURE AUDIT SUMMARY")
        print(f"{'='*60}")
        print(f"📅 Analysis Date: {self.results['analysis_timestamp']}")
        print(f"🎯 Accuracy Score: {self.results['accuracy_score']}/100")
        print(f"\n📊 ACTUAL IMPLEMENTATION:")
        print(f"   🗃️  Database Models: {actual['models']['count']}")
        print(f"   🛣️  Route Files: {len(actual['routes']['files'])}")
        print(f"   🔗 API Endpoints: {actual['api_endpoints']['count']}")
        print(f"   ⚙️  Services: {actual['services']['count']}")
        print(f"   🔧 Utilities: {actual['utilities']['count']}")
        print(f"   📄 Templates: {actual['templates']['count']}")
        print(f"   🤖 AI Providers: {len(actual['ai_services']['providers'])}")
        print(f"   🔐 Auth Methods: {len(actual['authentication']['methods'])}")
        
        if self.results['discrepancies']:
            print(f"\n⚠️  DISCREPANCIES FOUND: {len(self.results['discrepancies'])}")
            for i, disc in enumerate(self.results['discrepancies'], 1):
                print(f"   {i}. {disc['type']}: {disc['severity']} severity")
        
        if self.results['recommendations']:
            print(f"\n💡 RECOMMENDATIONS: {len(self.results['recommendations'])}")
            for i, rec in enumerate(self.results['recommendations'], 1):
                print(f"   {i}. {rec}")
        
        print(f"\n{'='*60}")

def main():
    """Main execution function"""
    auditor = ComprehensiveFeatureAuditor()
    results = auditor.audit_complete_system()
    
    # Print summary
    auditor.print_summary()
    
    # Save detailed report
    report_file = auditor.save_report()
    
    return results, report_file

if __name__ == "__main__":
    main()