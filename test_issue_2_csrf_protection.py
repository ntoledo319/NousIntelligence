#!/usr/bin/env python3
"""
Test Issue 2: Missing CSRF Protection on POST Routes
This test demonstrates that POST routes lack CSRF token validation
"""
import os
import sys
sys.path.insert(0, '.')

def test_csrf_missing_in_post_routes():
    """Test that POST routes don't validate CSRF tokens"""
    
    # Read routes that have POST methods
    post_routes_files = [
        'routes/api_routes.py',
        'routes/messaging_status.py', 
        'routes/user_routes.py'
    ]
    
    csrf_protected_routes = 0
    total_post_routes = 0
    
    for file_path in post_routes_files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Count POST routes
            post_count = content.count("methods=['POST']") + content.count('methods=["POST"]')
            total_post_routes += post_count
            
            # Check for CSRF protection patterns
            csrf_patterns = [
                'csrf_token',
                'csrf_protect',
                'validate_csrf_token',
                '@csrf.protect'
            ]
            
            for pattern in csrf_patterns:
                if pattern in content:
                    csrf_protected_routes += 1
                    break
    
    # Most POST routes should be missing CSRF protection
    assert total_post_routes > 0, "Should find POST routes"
    csrf_coverage = csrf_protected_routes / max(len(post_routes_files), 1)
    assert csrf_coverage < 0.5, f"CSRF protection coverage too high: {csrf_coverage}"

def test_api_routes_missing_csrf():
    """Test that API routes specifically lack CSRF protection"""
    
    if os.path.exists('routes/api_routes.py'):
        with open('routes/api_routes.py', 'r') as f:
            content = f.read()
        
        # Should have POST route
        assert 'methods=[\'POST\']' in content or 'methods=["POST"]' in content
        
        # Should NOT have CSRF protection
        csrf_patterns = ['csrf_token', 'csrf_protect', 'X-CSRF-Token']
        for pattern in csrf_patterns:
            assert pattern not in content, f"Unexpected CSRF protection found: {pattern}"

def test_demonstrates_csrf_vulnerability():
    """Demonstrate the CSRF vulnerability exists"""
    
    # This test shows that routes can be called without CSRF tokens
    # In a real test, this would make HTTP requests without CSRF tokens
    # and they would succeed, proving the vulnerability
    
    vulnerable_patterns = [
        "request.get_json()",  # No CSRF validation before processing JSON
        "@.*route.*methods.*POST.*def.*:.*request",  # POST route pattern without CSRF
    ]
    
    files_with_vulnerabilities = []
    
    route_files = ['routes/api_routes.py', 'routes/messaging_status.py']
    for file_path in route_files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            for pattern in vulnerable_patterns:
                if 'request.get_json()' in content:
                    files_with_vulnerabilities.append(file_path)
                    break
    
    assert len(files_with_vulnerabilities) > 0, "Should find files with CSRF vulnerabilities"

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])