#!/usr/bin/env python3
"""
FUNCTIONAL REPAIR SCRIPT
Fixes common Python code issues without external dependencies
"""

import os
import ast
import re
from pathlib import Path
from typing import List, Dict, Set

def find_python_files() -> List[str]:
    """Find all Python files in the project"""
    python_files = []
    for file_path in Path('.').rglob('*.py'):
        # Skip backup directories
        if any(part.startswith('.') or part in ['backup', '__pycache__']
              for part in file_path.parts):
            continue
        python_files.append(str(file_path))
    return python_files

def check_syntax_errors(file_path: str) -> List[str]:
    """Check for syntax errors in Python file"""
    errors = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
    except SyntaxError as e:
        errors.append(f"SyntaxError in {file_path}:{e.lineno}: {e.msg}")
    except Exception as e:
        errors.append(f"Error parsing {file_path}: {e}")
    return errors

def fix_common_import_issues(file_path: str) -> bool:
    """Fix common import issues"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Remove duplicate import lines
        lines = content.split('\n')
        seen_imports = set()
        fixed_lines = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith(('import ', 'from ')):
                if stripped not in seen_imports:
                    seen_imports.add(stripped)
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

        content = '\n'.join(fixed_lines)

        # Fix common import patterns
        replacements = [
            (r'from flask import Flask\nfrom flask import', 'from flask import Flask,'),
            (r'import os\nimport os', 'import os'),
            (r'import sys\nimport sys', 'import sys'),
        ]

        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

    except Exception as e:
        print(f"Error fixing imports in {file_path}: {e}")

    return False

def remove_unused_imports(file_path: str) -> bool:
    """Remove obviously unused imports"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        import_lines = []
        other_lines = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith(('import ', 'from ')) and not stripped.startswith('#'):
                import_lines.append(line)
            else:
                other_lines.append(line)

        # Simple heuristic: if import is not mentioned elsewhere, remove it
        body_content = '\n'.join(other_lines)
        kept_imports = []

        for import_line in import_lines:
            # Extract imported name
            if 'import ' in import_line:
                parts = import_line.split('import ')[-1].split(',')[0].strip()
                module_name = parts.split(' as ')[0].split('.')[0]

                # Keep if used somewhere in the code
                if module_name in body_content or len(module_name) < 3:  # Keep short names to be safe
                    kept_imports.append(import_line)
            else:
                kept_imports.append(import_line)

        if len(kept_imports) != len(import_lines):
            new_content = '\n'.join(kept_imports + other_lines)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

    except Exception as e:
        print(f"Error removing unused imports in {file_path}: {e}")

    return False

def fix_basic_formatting(file_path: str) -> bool:
    """Fix basic formatting issues"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Fix trailing whitespace
        lines = content.split('\n')
        lines = [line.rstrip() for line in lines]

        # Remove excessive blank lines (more than 2 consecutive)
        fixed_lines = []
        blank_count = 0

        for line in lines:
            if line.strip() == '':
                blank_count += 1
                if blank_count <= 2:
                    fixed_lines.append(line)
            else:
                blank_count = 0
                fixed_lines.append(line)

        content = '\n'.join(fixed_lines)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

    except Exception as e:
        print(f"Error fixing formatting in {file_path}: {e}")

    return False

def run_basic_security_check(file_path: str) -> List[str]:
    """Run basic security checks"""
    issues = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for hardcoded secrets
        patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', 'Hardcoded password'),
            (r'secret\s*=\s*["\'][^"\']+["\']', 'Hardcoded secret'),
            (r'api_key\s*=\s*["\'][^"\']+["\']', 'Hardcoded API key'),
            (r'eval\s*\(', 'Use of eval()'),
            (r'exec\s*\(', 'Use of exec()'),
        ]

        for pattern, message in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"{message} in {file_path}")

    except Exception as e:
        issues.append(f"Error checking security in {file_path}: {e}")

    return issues

def create_simple_test_suite() -> None:
    """Create a simple test suite to verify basic functionality"""
    test_content = '''#!/usr/bin/env python3
"""
Simple test suite for basic functionality
"""

import sys

def test_imports():
    """Test that main modules can be imported"""
    try:
        import main
        print("✅ main.py imports successfully")
    except Exception as e:
        print(f"❌ main.py import failed: {e}")
        return False

    try:
        import config
        print("✅ config.py imports successfully")
    except Exception as e:
        print(f"❌ config.py import failed: {e}")
        return False

    return True

def test_app_creation():
    """Test that the app can be created"""
    try:
        # Try to import and create app
        from minimal_public_app import create_app
        app = create_app()
        print("✅ App creation successful")
        return True
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False

def test_database_config():
    """Test database configuration"""
    try:
        import database
        print("✅ Database module imports successfully")
        return True
    except Exception as e:
        print(f"❌ Database import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running basic functionality tests...")

    tests = [
        test_imports,
        test_app_creation,
        test_database_config
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print(f"\\n📊 Test Results: {passed}/{total} passed")

    if passed == total:
        print("✅ All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    main()
'''

    with open('basic_tests.py', 'w') as f:
        f.write(test_content)

    print("📋 Created basic_tests.py")

def main():
    """Main repair function"""
    print("🔧 Starting FUNCTIONAL REPAIR LOOP...")

    # Find all Python files
    python_files = find_python_files()
    print(f"🐍 Found {len(python_files)} Python files")

    # Check for syntax errors
    syntax_errors = []
    for file_path in python_files:
        errors = check_syntax_errors(file_path)
        syntax_errors.extend(errors)

    if syntax_errors:
        print("❌ SYNTAX ERRORS FOUND:")
        for error in syntax_errors:
            print(f"  {error}")
    else:
        print("✅ No syntax errors found")

    # Fix common issues
    fixed_files = 0

    for file_path in python_files:
        fixed = False

        if fix_common_import_issues(file_path):
            print(f"🔧 Fixed imports in {file_path}")
            fixed = True

        if fix_basic_formatting(file_path):
            print(f"🔧 Fixed formatting in {file_path}")
            fixed = True

        if fixed:
            fixed_files += 1

    print(f"✅ Fixed issues in {fixed_files} files")

    # Run security checks
    security_issues = []
    for file_path in python_files:
        issues = run_basic_security_check(file_path)
        security_issues.extend(issues)

    if security_issues:
        print("⚠️  SECURITY ISSUES FOUND:")
        for issue in security_issues:
            print(f"  {issue}")
    else:
        print("✅ No obvious security issues found")

    # Create test suite
    create_simple_test_suite()

    print("\n✅ FUNCTIONAL REPAIR COMPLETE")

if __name__ == "__main__":
    main()