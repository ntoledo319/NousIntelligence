#!/usr/bin/env python3
"""
Test Issue 1: Syntax Errors in API Routes
This test demonstrates that routes/api.py cannot be imported due to syntax errors
"""
import pytest
import sys
import os

def test_api_routes_import_fails():
    """Test that routes/api.py fails to import due to syntax errors"""
    
    # Add the workspace to Python path
    sys.path.insert(0, os.path.abspath('.'))
    
    # This should fail due to syntax errors
    with pytest.raises((SyntaxError, ImportError)):
        import routes.api

def test_api_routes_syntax_validation():
    """Test that the API routes file has valid Python syntax"""
    
    # Read the file content
    with open('routes/api.py', 'r') as f:
        content = f.read()
    
    # Try to compile it - should raise SyntaxError
    with pytest.raises(SyntaxError):
        compile(content, 'routes/api.py', 'exec')

def test_broken_function_definitions():
    """Test demonstrates broken function definitions in api.py"""
    
    with open('routes/api.py', 'r') as f:
        content = f.read()
    
    # Check for broken patterns that cause syntax errors
    broken_patterns = [
        'session.get(\'user\', {}).get(\'to_dict())',  # Missing closing quote
        'def get_get_demo_user()()',  # Double parentheses 
        'session.get(\'user\', {}).get(\'settings:',  # Missing closing quote
        'session.get(\'user\', {}).get(\'settings = settings',  # Invalid assignment
    ]
    
    for pattern in broken_patterns:
        assert pattern in content, f"Expected broken pattern not found: {pattern}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])