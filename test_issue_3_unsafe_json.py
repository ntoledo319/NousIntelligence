#!/usr/bin/env python3
"""
Test Issue 3: Unsafe JSON Request Handling
This test demonstrates unsafe usage of request.get_json() and request.json
"""
import os
import sys
sys.path.insert(0, '.')

def test_unsafe_request_json_usage():
    """Test that routes use request.json or request.get_json() without validation"""
    
    route_files = [
        'routes/api_routes.py',
        'routes/forms_routes.py', 
        'routes/meet_routes.py'
    ]
    
    unsafe_patterns = []
    
    for file_path in route_files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                # Check for unsafe patterns
                if 'request.json' in line and 'get_json' not in line:
                    unsafe_patterns.append("{}:{} - Direct request.json access".format(file_path, i))
                elif 'request.get_json()' in line:
                    # Check if there's validation nearby
                    context_lines = lines[max(0, i-3):min(len(lines), i+3)]
                    context = '\n'.join(context_lines)
                    
                    if not any(check in context.lower() for check in ['if not data', 'if data is none', 'validate', 'try:']):
                        unsafe_patterns.append("{}:{} - request.get_json() without validation".format(file_path, i))
    
    assert len(unsafe_patterns) > 0, "Should find unsafe JSON patterns, found: {}".format(unsafe_patterns)

def test_request_json_without_error_handling():
    """Test that request.json is used without proper error handling"""
    
    if os.path.exists('routes/forms_routes.py'):
        with open('routes/forms_routes.py', 'r') as f:
            content = f.read()
        
        # Should have direct request.json usage
        assert 'data = request.json' in content, "Should find direct request.json usage"
        
        # Should NOT have proper error handling around it
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'data = request.json' in line:
                # Check 3 lines before and after for try/except
                context_start = max(0, i-3)
                context_end = min(len(lines), i+3)
                context = '\n'.join(lines[context_start:context_end])
                
                # Should NOT have proper error handling
                has_try_except = 'try:' in context and 'except' in context
                assert not has_try_except, "Found unexpected error handling around request.json"

def test_demonstrates_json_vulnerability():
    """Demonstrate that malformed JSON can cause issues"""
    
    # This test simulates what happens when malformed JSON is sent
    # In a real scenario, this would crash the application
    
    vulnerable_files = []
    
    for file_path in ['routes/forms_routes.py', 'routes/enhanced_api_routes.py']:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for unsafe JSON access patterns
            if 'request.json' in content and 'try:' not in content:
                vulnerable_files.append(file_path)
    
    assert len(vulnerable_files) > 0, "Should find files vulnerable to JSON parsing errors"

if __name__ == "__main__":
    test_unsafe_request_json_usage()
    test_request_json_without_error_handling()
    test_demonstrates_json_vulnerability()
    print("All tests completed - JSON handling vulnerabilities confirmed")