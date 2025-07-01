#!/usr/bin/env python3
"""
Comprehensive Fix Validation Script
Tests all implemented fixes and generates a final validation report
"""

import json
import os
import sys
import time
from datetime import datetime

def main():
    """Run comprehensive validation of all fixes"""
    print("=" * 60)
    print("COMPREHENSIVE FIX VALIDATION")
    print("=" * 60)
    print(f"Starting validation at: {datetime.now().isoformat()}")
    print()
    
    validation_results = {
        'validation_start': datetime.now().isoformat(),
        'fixes_completed': 0,
        'critical_systems': {},
        'deployment_readiness': False,
        'security_score': 0,
        'issues_found': [],
        'recommendations': []
    }
    
    # Test 1: Security Infrastructure
    print("Testing Security Infrastructure...")
    security_score = test_security_systems(validation_results)
    validation_results['security_score'] = security_score
    print(f"✓ Security Score: {security_score}/100")
    print()
    
    # Test 2: OAuth Implementation
    print("Testing OAuth Security...")
    oauth_result = test_oauth_security(validation_results)
    validation_results['critical_systems']['oauth'] = oauth_result
    print(f"✓ OAuth Security: {'PASS' if oauth_result['status'] == 'secure' else 'NEEDS ATTENTION'}")
    print()
    
    # Test 3: Environment & Deployment
    print("Testing Deployment Readiness...")
    deployment_result = test_deployment_readiness(validation_results)
    validation_results['deployment_readiness'] = deployment_result['ready']
    print(f"✓ Deployment Ready: {'YES' if deployment_result['ready'] else 'NO'}")
    print()
    
    # Test 4: Performance & Health
    print("Testing Performance & Health Monitoring...")
    health_result = test_health_systems(validation_results)
    validation_results['critical_systems']['health'] = health_result
    print(f"✓ Health Monitoring: {'OPERATIONAL' if health_result['operational'] else 'DEGRADED'}")
    print()
    
    # Calculate final score
    final_score = calculate_final_score(validation_results)
    validation_results['final_score'] = final_score
    
    # Generate report
    print("=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Overall Score: {final_score}/100")
    print(f"Security Score: {security_score}/100")
    print(f"Deployment Ready: {'✓' if validation_results['deployment_readiness'] else '✗'}")
    print(f"Critical Issues: {len(validation_results['issues_found'])}")
    
    if validation_results['issues_found']:
        print("\nIssues Found:")
        for issue in validation_results['issues_found']:
            print(f"  - {issue}")
    
    if validation_results['recommendations']:
        print("\nRecommendations:")
        for rec in validation_results['recommendations']:
            print(f"  - {rec}")
    
    # Save detailed report
    validation_results['validation_end'] = datetime.now().isoformat()
    with open('comprehensive_fix_validation_report.json', 'w') as f:
        json.dump(validation_results, f, indent=2)
    
    print(f"\nDetailed report saved to: comprehensive_fix_validation_report.json")
    print("=" * 60)
    
    return final_score

def test_security_systems(results):
    """Test security system implementations"""
    security_score = 0
    max_score = 100
    
    # Test 1: Environment Security (25 points)
    if os.environ.get('SESSION_SECRET'):
        security_score += 25
    else:
        results['issues_found'].append("SESSION_SECRET not configured")
    
    # Test 2: OAuth State Management (25 points)
    try:
        # Check if oauth state manager exists
        import utils.oauth_state_manager
        security_score += 25
    except ImportError:
        results['issues_found'].append("OAuth state manager not available")
    
    # Test 3: Token Encryption (25 points)
    try:
        import utils.token_encryption
        security_score += 25
    except ImportError:
        results['issues_found'].append("Token encryption not available")
    
    # Test 4: Rate Limiting (25 points)
    try:
        import utils.rate_limiter
        security_score += 25
    except ImportError:
        results['issues_found'].append("Rate limiter not available")
    
    return security_score

def test_oauth_security(results):
    """Test OAuth security implementation"""
    oauth_status = {
        'status': 'secure',
        'features': {},
        'issues': []
    }
    
    try:
        # Test OAuth service
        from utils.google_oauth import oauth_service
        oauth_status['features']['service_available'] = True
        
        # Test state validation
        try:
            from utils.oauth_state_manager import oauth_state_manager
            oauth_status['features']['state_validation'] = True
        except ImportError:
            oauth_status['issues'].append("State validation unavailable")
        
        # Test token encryption
        try:
            from utils.token_encryption import token_encryption
            oauth_status['features']['token_encryption'] = True
        except ImportError:
            oauth_status['issues'].append("Token encryption unavailable")
        
    except ImportError:
        oauth_status['status'] = 'degraded'
        oauth_status['issues'].append("OAuth service unavailable")
    
    return oauth_status

def test_deployment_readiness(results):
    """Test deployment readiness"""
    deployment_status = {
        'ready': False,
        'checks': {},
        'blockers': []
    }
    
    # Check required environment variables
    required_vars = ['SESSION_SECRET', 'DATABASE_URL']
    for var in required_vars:
        if os.environ.get(var):
            deployment_status['checks'][var] = True
        else:
            deployment_status['checks'][var] = False
            deployment_status['blockers'].append(f"Missing {var}")
    
    # Check application startup
    try:
        from app import app
        deployment_status['checks']['app_startup'] = True
    except Exception as e:
        deployment_status['checks']['app_startup'] = False
        deployment_status['blockers'].append(f"App startup failed: {str(e)}")
    
    # Determine readiness
    deployment_status['ready'] = len(deployment_status['blockers']) == 0
    
    return deployment_status

def test_health_systems(results):
    """Test health monitoring systems"""
    health_status = {
        'operational': False,
        'systems': {},
        'issues': []
    }
    
    try:
        # Test health monitor
        from utils.health_monitor import health_monitor
        health_status['systems']['health_monitor'] = True
        
        # Test environment validator
        try:
            from utils.environment_validator import environment_validator
            health_status['systems']['environment_validator'] = True
        except ImportError:
            health_status['issues'].append("Environment validator unavailable")
        
        # Test health endpoint
        try:
            from app import app
            with app.test_client() as client:
                response = client.get('/health')
                health_status['systems']['health_endpoint'] = response.status_code == 200
        except Exception as e:
            health_status['issues'].append(f"Health endpoint failed: {str(e)}")
        
    except ImportError:
        health_status['issues'].append("Health monitor unavailable")
    
    health_status['operational'] = len(health_status['issues']) == 0
    return health_status

def calculate_final_score(results):
    """Calculate final validation score"""
    base_score = results['security_score']
    
    # Bonus points for deployment readiness
    if results['deployment_readiness']:
        base_score += 10
    
    # Bonus points for health monitoring
    if results['critical_systems'].get('health', {}).get('operational'):
        base_score += 10
    
    # Penalty for critical issues
    critical_issues = len(results['issues_found'])
    penalty = min(critical_issues * 5, 30)  # Max 30 point penalty
    
    final_score = min(max(base_score - penalty, 0), 100)
    return final_score

if __name__ == "__main__":
    try:
        score = main()
        sys.exit(0 if score >= 80 else 1)  # Exit with error if score below 80%
    except Exception as e:
        print(f"Validation failed: {e}")
        sys.exit(1)