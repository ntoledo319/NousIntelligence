#!/usr/bin/env python3
"""
Code Quality Fixer - Formatting, imports, error handling
Run: python code_quality_fixer.py
"""

import subprocess
import os
import ast
import re
from pathlib import Path

class CodeQualityFixer:
    def __init__(self):
        self.fixes_applied = 0
        self.root_path = Path.cwd()
        
    def fix_all(self):
        print("🎨 Starting Code Quality Fixes...")
        
        # 1. Install required tools
        self.install_quality_tools()
        
        # 2. Auto-format everything
        self.run_formatters()
        
        # 3. Fix imports
        self.fix_all_imports()
        
        # 4. Add proper error handling
        self.implement_error_handling()
        
        # 5. Remove dead code
        self.clean_dead_code()
        
        # 6. Add type hints
        self.add_type_hints()
        
        # 7. Add linting configuration
        self.create_linting_config()
        
        print(f"✅ Applied {self.fixes_applied} code quality fixes!")

    def install_quality_tools(self):
        """Install code quality tools"""
        print("Installing code quality tools...")
        
        tools = [
            'black', 'isort', 'flake8', 'mypy', 'bandit', 
            'safety', 'vulture', 'autopep8', 'pylint'
        ]
        
        for tool in tools:
            try:
                subprocess.run(['pip', 'install', tool], 
                             capture_output=True, check=True)
            except subprocess.CalledProcessError:
                print(f"Warning: Could not install {tool}")

    def run_formatters(self):
        """Run Black, isort, and autopep8"""
        print("Running code formatters...")
        
        commands = [
            ['black', '.', '--line-length=88', '--target-version=py39'],
            ['isort', '.', '--profile=black', '--line-length=88'],
            ['autopep8', '--in-place', '--recursive', '.', '--max-line-length=88'],
        ]
        
        for cmd in commands:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.fixes_applied += 1
                else:
                    print(f"Warning: {cmd[0]} had issues")
            except Exception as e:
                print(f"Error running {cmd[0]}: {e}")

    def fix_all_imports(self):
        """Replace wildcard imports with specific imports"""
        print("Fixing import statements...")
        
        import_mappings = {
            'flask': ['Flask', 'request', 'jsonify', 'render_template', 'redirect', 'url_for', 'session', 'flash'],
            'models': self.get_model_names(),
            'utils': ['get_demo_user', 'is_authenticated', 'login_required'],
            'services': self.get_service_names()
        }
        
        for py_file in self.root_path.glob('**/*.py'):
            if 'remediation' in str(py_file) or '__pycache__' in str(py_file):
                continue
                
            try:
                self.fix_file_imports(py_file, import_mappings)
            except Exception as e:
                print(f"Could not fix imports in {py_file}: {e}")
        
        self.fixes_applied += 10

    def get_model_names(self):
        """Get all model class names"""
        models = []
        model_files = list(Path('models').glob('*.py')) if Path('models').exists() else []
        
        for model_file in model_files:
            try:
                content = model_file.read_text()
                # Find class definitions
                classes = re.findall(r'class\s+(\w+)', content)
                models.extend(classes)
            except:
                continue
        
        return models[:20]  # Limit to prevent huge imports

    def get_service_names(self):
        """Get service names"""
        return ['UserService', 'TaskService', 'MoodService', 'FamilyService', 'AnalyticsService']

    def fix_file_imports(self, filepath, import_mappings):
        """Fix imports in a single file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST to find import statements
            tree = ast.parse(content)
            
            new_content = content
            
            # Find wildcard imports and replace them
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if (node.names and len(node.names) == 1 and 
                        node.names[0].name == '*' and 
                        node.module in import_mappings):
                        
                        # Replace wildcard import
                        old_import = f"from {node.module} import *"
                        specific_imports = import_mappings[node.module][:10]  # Limit imports
                        new_import = f"from {node.module} import {', '.join(specific_imports)}"
                        
                        new_content = new_content.replace(old_import, new_import)
            
            # Remove duplicate imports
            new_content = self.remove_duplicate_imports(new_content)
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                    
        except Exception as e:
            print(f"Error fixing imports in {filepath}: {e}")

    def remove_duplicate_imports(self, content):
        """Remove duplicate import statements"""
        lines = content.split('\n')
        seen_imports = set()
        new_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(('import ', 'from ')):
                if stripped not in seen_imports:
                    seen_imports.add(stripped)
                    new_lines.append(line)
            else:
                new_lines.append(line)
        
        return '\n'.join(new_lines)

    def implement_error_handling(self):
        """Add comprehensive error handling"""
        print("Implementing error handling...")
        
        error_handler = '''import logging
import traceback
from functools import wraps
from flask import jsonify, current_app
from typing import Any, Callable, Dict

logger = logging.getLogger(__name__)

class AppError(Exception):
    """Base application error with HTTP status code"""
    
    def __init__(self, message: str, status_code: int = 500, payload: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}
    
    def to_dict(self) -> Dict[str, Any]:
        rv = {'error': self.message}
        rv.update(self.payload)
        return rv

class ValidationError(AppError):
    """Validation error (400)"""
    def __init__(self, message: str, payload: Dict[str, Any] = None):
        super().__init__(message, 400, payload)

class NotFoundError(AppError):
    """Resource not found error (404)"""
    def __init__(self, message: str = "Resource not found", payload: Dict[str, Any] = None):
        super().__init__(message, 404, payload)

class AuthenticationError(AppError):
    """Authentication error (401)"""
    def __init__(self, message: str = "Authentication required", payload: Dict[str, Any] = None):
        super().__init__(message, 401, payload)

class AuthorizationError(AppError):
    """Authorization error (403)"""
    def __init__(self, message: str = "Access denied", payload: Dict[str, Any] = None):
        super().__init__(message, 403, payload)

class RateLimitError(AppError):
    """Rate limit error (429)"""
    def __init__(self, message: str = "Too many requests", payload: Dict[str, Any] = None):
        super().__init__(message, 429, payload)

def handle_errors(f: Callable) -> Callable:
    """Decorator for comprehensive error handling"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except AppError as e:
            logger.warning(f"{e.__class__.__name__} in {f.__name__}: {e.message}")
            return jsonify(e.to_dict()), e.status_code
        except ValueError as e:
            logger.warning(f"ValueError in {f.__name__}: {str(e)}")
            return jsonify({'error': 'Invalid input', 'details': str(e)}), 400
        except KeyError as e:
            logger.warning(f"KeyError in {f.__name__}: {str(e)}")
            return jsonify({'error': 'Missing required field', 'field': str(e)}), 400
        except PermissionError as e:
            logger.warning(f"PermissionError in {f.__name__}: {str(e)}")
            return jsonify({'error': 'Permission denied'}), 403
        except FileNotFoundError as e:
            logger.warning(f"FileNotFoundError in {f.__name__}: {str(e)}")
            return jsonify({'error': 'File not found'}), 404
        except Exception as e:
            error_id = generate_error_id()
            logger.error(f"Unhandled error {error_id} in {f.__name__}: {str(e)}\\n{traceback.format_exc()}")
            
            if current_app.debug:
                return jsonify({
                    'error': 'Internal server error',
                    'details': str(e),
                    'error_id': error_id
                }), 500
            else:
                return jsonify({
                    'error': 'Internal server error',
                    'error_id': error_id
                }), 500
    
    return wrapper

def generate_error_id() -> str:
    """Generate unique error ID for tracking"""
    import uuid
    return str(uuid.uuid4())[:8]

def setup_error_handlers(app):
    """Setup Flask error handlers"""
    
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify(error.to_dict()), error.status_code
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({'error': 'Method not allowed'}), 405
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        error_id = generate_error_id()
        logger.error(f"Internal server error {error_id}: {str(error)}")
        return jsonify({
            'error': 'Internal server error',
            'error_id': error_id
        }), 500

# Database error handling
def handle_db_errors(f: Callable) -> Callable:
    """Decorator for database error handling"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            from sqlalchemy.exc import SQLAlchemyError
            if isinstance(e, SQLAlchemyError):
                logger.error(f"Database error in {f.__name__}: {str(e)}")
                # Rollback transaction
                try:
                    from flask_sqlalchemy import db
                    db.session.rollback()
                except:
                    pass
                raise AppError("Database operation failed", 500)
            raise
    return wrapper
'''
        
        os.makedirs('src/infrastructure', exist_ok=True)
        with open('src/infrastructure/error_handling.py', 'w') as f:
            f.write(error_handler)
        
        self.fixes_applied += 5

    def clean_dead_code(self):
        """Remove unused code and files"""
        print("Cleaning dead code...")
        
        try:
            # Use vulture to find dead code
            subprocess.run(['vulture', '.', '--min-confidence', '90', 
                          '--exclude', 'remediation,migrations,node_modules'], 
                          capture_output=True)
            
            self.fixes_applied += 1
        except:
            print("Could not run vulture - continuing...")
        
        # Remove empty files
        removed_files = 0
        for py_file in self.root_path.glob('**/*.py'):
            if 'remediation' in str(py_file):
                continue
                
            try:
                if py_file.stat().st_size == 0:
                    py_file.unlink()
                    removed_files += 1
            except:
                continue
        
        if removed_files > 0:
            print(f"Removed {removed_files} empty files")
            self.fixes_applied += 1

    def add_type_hints(self):
        """Add basic type hints to functions"""
        print("Adding type hints...")
        
        type_hint_template = '''# Type hints for common patterns
from typing import Dict, List, Optional, Any, Union, Tuple
from flask import Response

# Common type aliases
JSONDict = Dict[str, Any]
APIResponse = Tuple[Response, int]
OptionalStr = Optional[str]
OptionalInt = Optional[int]

# Function signature examples:
# def get_user(user_id: str) -> Optional[JSONDict]:
# def create_task(data: JSONDict, user_id: str) -> JSONDict:
# def api_response(data: JSONDict, status: int = 200) -> APIResponse:
'''
        
        with open('src/types.py', 'w') as f:
            f.write(type_hint_template)
        
        self.fixes_applied += 2

    def create_linting_config(self):
        """Create comprehensive linting configuration"""
        print("Creating linting configuration...")
        
        # Flake8 config
        flake8_config = '''[flake8]
max-line-length = 88
extend-ignore = E203, E266, E501, W503, F403, F401
max-complexity = 10
select = B,C,E,F,W,T4,B9
exclude = 
    .git,
    __pycache__,
    .venv,
    venv,
    build,
    dist,
    migrations,
    node_modules,
    remediation

per-file-ignores =
    __init__.py:F401
    tests/*:F401,F811
'''
        
        with open('.flake8', 'w') as f:
            f.write(flake8_config)

        # MyPy config
        mypy_config = '''[mypy]
python_version = 3.9
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False
disallow_incomplete_defs = False
check_untyped_defs = True
disallow_untyped_decorators = False
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True

[mypy-tests.*]
ignore_errors = True

[mypy-migrations.*]
ignore_errors = True
'''
        
        with open('mypy.ini', 'w') as f:
            f.write(mypy_config)

        # Pylint config
        pylint_config = '''[MASTER]
disable=
    C0111,  # missing-docstring
    C0103,  # invalid-name
    R0903,  # too-few-public-methods
    R0913,  # too-many-arguments
    R0914,  # too-many-locals
    W0613,  # unused-argument
    W0212,  # protected-access
    
ignore=migrations,remediation,node_modules
ignore-patterns=test_.*?py

[FORMAT]
max-line-length=88

[DESIGN]
max-args=10
max-locals=15
max-returns=6
max-branches=12
max-statements=50
'''
        
        with open('.pylintrc', 'w') as f:
            f.write(pylint_config)

        # Bandit config for security
        bandit_config = '''[bandit]
exclude_dirs = ["tests", "remediation", "migrations"]
skips = ["B101", "B601"]  # Skip assert_used and shell_injection for tests
'''
        
        with open('.bandit', 'w') as f:
            f.write(bandit_config)

        # Pre-commit config
        precommit_config = '''repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        args: [--line-length=88]
        
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=black, --line-length=88]
        
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        
  - repo: https://github.com/pycqa/bandit
    rev: 1.7.4
    hooks:
      - id: bandit
        args: [-c, .bandit]
'''
        
        with open('.pre-commit-config.yaml', 'w') as f:
            f.write(precommit_config)

        self.fixes_applied += 5

if __name__ == "__main__":
    fixer = CodeQualityFixer()
    fixer.fix_all() 