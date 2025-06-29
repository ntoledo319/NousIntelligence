"""
Comprehensive Testing Configuration
Centralized configuration for all testing infrastructure
"""
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Testing configuration
TEST_CONFIG = {
    'base_url': 'http://localhost:5000',
    'timeout': 30,
    'max_retries': 3,
    'test_data_dir': PROJECT_ROOT / 'tests' / 'data',
    'reports_dir': PROJECT_ROOT / 'tests' / 'reports',
    'backup_dir': PROJECT_ROOT / 'tests' / 'backups'
}

# Ensure test directories exist
for dir_path in [TEST_CONFIG['test_data_dir'], TEST_CONFIG['reports_dir'], TEST_CONFIG['backup_dir']]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Environment configuration
def get_base_url():
    """Get application base URL from environment or config"""
    host = os.environ.get('HOST', 'localhost')
    port = os.environ.get('PORT', '5000')
    return f"http://{host}:{port}"

def get_database_url():
    """Get database URL for testing"""
    return os.environ.get('DATABASE_URL', 'sqlite:///test.db')

# Test authentication credentials for demo mode
DEMO_USER = {
    'id': 'demo_user',
    'name': 'Demo User',
    'email': 'demo@nous.app',
    'demo_mode': True,
    'authenticated': True
}

# API endpoints to test
CRITICAL_ENDPOINTS = [
    '/',
    '/health',
    '/healthz',
    '/api/health',
    '/demo',
    '/api/demo/chat'
]

# Security headers that should be present
REQUIRED_SECURITY_HEADERS = [
    'X-Content-Type-Options',
    'X-Frame-Options',
    'X-XSS-Protection'
]

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    'response_time_good': 1.0,
    'response_time_acceptable': 5.0,
    'memory_usage_good': 100,  # MB
    'memory_usage_acceptable': 500  # MB
}

# Files that should exist for deployment readiness
DEPLOYMENT_REQUIRED_FILES = [
    'app.py',
    'main.py',
    'pyproject.toml',
    'replit.toml',
    'utils/auth_compat.py'
]

# Authentication barrier patterns to detect
AUTH_BARRIER_PATTERNS = {
    'flask_login_decorators': [
        r'@login_required',
        r'from flask_login import.*login_required'
    ],
    'current_user_references': [
        r'current_user\.',
        r'from flask_login import.*current_user'
    ],
    'auth_redirects': [
        r'redirect.*login',
        r'url_for.*login'
    ],
    'auth_messages': [
        r'You must be logged in',
        r'Login required',
        r'Authentication required'
    ]
}

# Common error patterns to detect
ERROR_PATTERNS = {
    'syntax_errors': [
        r'SyntaxError',
        r'IndentationError',
        r'invalid syntax'
    ],
    'import_errors': [
        r'ImportError',
        r'ModuleNotFoundError',
        r'No module named'
    ],
    'runtime_errors': [
        r'AttributeError',
        r'NameError',
        r'TypeError',
        r'ValueError'
    ]
}

# Test severity levels
SEVERITY_LEVELS = {
    'CRITICAL': 4,
    'HIGH': 3,
    'MEDIUM': 2,
    'LOW': 1
}

def get_test_session():
    """Get configured requests session for testing"""
    import requests
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'NOUS-Test-Suite/1.0',
        'Accept': 'application/json,text/html,*/*'
    })
    return session

def should_skip_file(file_path: Path) -> bool:
    """Check if file should be skipped during scanning"""
    skip_patterns = [
        '__pycache__',
        '.git',
        'node_modules',
        'venv',
        '.pytest_cache',
        'backup',
        'archive',
        '.pyc',
        '.pyo'
    ]
    
    return any(pattern in str(file_path) for pattern in skip_patterns)

def get_python_files(root_dir: Path = None) -> list:
    """Get list of Python files to analyze"""
    if root_dir is None:
        root_dir = PROJECT_ROOT
    
    python_files = []
    for file_path in root_dir.rglob('*.py'):
        if not should_skip_file(file_path):
            python_files.append(file_path)
    
    return python_files

def setup_logging(log_level='INFO'):
    """Setup logging configuration for tests"""
    import logging
    
    # Create logs directory
    logs_dir = PROJECT_ROOT / 'tests' / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='[%(asctime)s] %(name)s - %(levelname)s: %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(logs_dir / 'test_suite.log')
        ]
    )
    
    return logging.getLogger(__name__)

# Export configuration
__all__ = [
    'TEST_CONFIG',
    'get_base_url',
    'get_database_url', 
    'DEMO_USER',
    'CRITICAL_ENDPOINTS',
    'REQUIRED_SECURITY_HEADERS',
    'PERFORMANCE_THRESHOLDS',
    'DEPLOYMENT_REQUIRED_FILES',
    'AUTH_BARRIER_PATTERNS',
    'ERROR_PATTERNS',
    'SEVERITY_LEVELS',
    'get_test_session',
    'should_skip_file',
    'get_python_files',
    'setup_logging',
    'PROJECT_ROOT'
]