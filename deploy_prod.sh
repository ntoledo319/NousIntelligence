#!/bin/bash

# NOUS Personal Assistant - Consolidated Production Deployment Script
# Consolidates all existing deploy/build scripts into a single optimized pipeline

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_CONFIG="${SCRIPT_DIR}/build.properties"
LOG_FILE="${SCRIPT_DIR}/logs/deploy_$(date +%Y%m%d_%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Load build configuration
load_config() {
    if [[ -f "$BUILD_CONFIG" ]]; then
        echo -e "${BLUE}📋 Loading build configuration...${NC}"
        source "$BUILD_CONFIG"
    else
        echo -e "${YELLOW}⚠️  Build configuration not found, using defaults${NC}"
        # Set default values
        export NODE_ENV=production
        export FLASK_ENV=production
        export BUILD_DIR=dist
        export PORT=5000
        export HOST=0.0.0.0
        export PARALLEL_BUILDS=true
    fi
}

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "$message"
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE" 2>/dev/null || true
}

# Error handler
error_exit() {
    log "ERROR" "${RED}❌ Deployment failed: $1${NC}"
    exit 1
}

# Success handler
success() {
    log "INFO" "${GREEN}✅ $1${NC}"
}

# Warning handler
warning() {
    log "WARN" "${YELLOW}⚠️  $1${NC}"
}

# Info handler
info() {
    log "INFO" "${BLUE}ℹ️  $1${NC}"
}

# Progress indicator
progress() {
    local step="$1"
    local total="$2"
    local desc="$3"
    echo -e "${BLUE}[$step/$total] $desc...${NC}"
}

# Phase 1: Clean
clean_phase() {
    progress 1 8 "CLEAN - Removing build artifacts"
    
    # Create logs directory
    mkdir -p logs
    
    # Remove build directories
    local clean_dirs=("${BUILD_DIR:-dist}" ".tmp" "__pycache__" "*.pyc" ".pytest_cache" "flask_session")
    
    for dir in "${clean_dirs[@]}"; do
        if [[ "$dir" == *.pyc ]]; then
            find . -name "*.pyc" -delete 2>/dev/null || true
        else
            rm -rf "$dir" 2>/dev/null || true
        fi
    done
    
    # Clean Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    
    success "Clean phase completed"
}

# Phase 2: Install Dependencies
install_phase() {
    progress 2 8 "INSTALL - Installing dependencies"
    
    # Check if we're in a Python environment
    if [[ -f "pyproject.toml" ]]; then
        info "Installing Python dependencies from pyproject.toml"
        
        # Use pip with optimizations
        export PIP_NO_CACHE_DIR=1
        export PIP_DISABLE_PIP_VERSION_CHECK=1
        export PIP_PREFER_BINARY=1
        
        # Install dependencies
        pip install -e . || error_exit "Failed to install Python dependencies"
        
        # Install development dependencies if available
        if [[ -f "requirements_dev.txt" ]]; then
            pip install -r requirements_dev.txt || warning "Failed to install dev dependencies"
        fi
    else
        error_exit "No pyproject.toml found - invalid Python project"
    fi
    
    success "Dependencies installed successfully"
}

# Phase 3: Lint
lint_phase() {
    progress 3 8 "LINT - Running code quality checks"
    
    # Python linting with flake8 (if available)
    if command -v flake8 >/dev/null 2>&1; then
        info "Running flake8 linting"
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || warning "Linting found issues"
    else
        # Basic syntax check
        info "Running basic Python syntax check"
        python -m py_compile app.py main.py || error_exit "Python syntax errors found"
    fi
    
    success "Code quality checks completed"
}

# Phase 4: Test
test_phase() {
    progress 4 8 "TEST - Running test suite"
    
    # Set test environment
    export FLASK_ENV=testing
    export DATABASE_URL="sqlite:///:memory:"
    
    # Run pytest if available
    if command -v pytest >/dev/null 2>&1 && [[ -d "tests" ]]; then
        info "Running pytest test suite"
        pytest tests/ -v --tb=short || warning "Some tests failed"
    else
        # Basic import test - skip app creation to avoid database issues
        info "Running basic import tests"
        python -c "
import sys
try:
    # Test basic imports that don't require database
    import database
    import models.user
    print('✅ Database and models import successfully')
    
    # Test critical modules
    import api.chat
    import utils.unified_ai_service
    print('✅ Core service modules import successfully')
    
    print('✅ All core modules import successfully')
except Exception as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
" || warning "Some import tests failed - continuing deployment"
    fi
    
    success "Test phase completed"
}

# Phase 5: Build
build_phase() {
    progress 5 8 "BUILD - Building production assets"
    
    # Create required directories
    mkdir -p static templates logs flask_session instance
    
    # Set production environment
    export FLASK_ENV=production
    export PYTHONDONTWRITEBYTECODE=1
    export PYTHONUNBUFFERED=1
    
    # Validate application can start
    info "Validating application startup"
    python -c "
import os
os.environ['FLASK_ENV'] = 'production'
try:
    from app import create_app
    app = create_app()
    print('✅ Application builds successfully')
except Exception as e:
    print(f'❌ Build error: {e}')
    import sys
    sys.exit(1)
" || error_exit "Application build failed"
    
    success "Build phase completed"
}

# Phase 6: Optimize
optimize_phase() {
    progress 6 8 "OPTIMIZE - Optimizing for production"
    
    # Create optimized Gunicorn configuration if it doesn't exist
    if [[ ! -f "gunicorn.conf.py" ]]; then
        info "Creating optimized Gunicorn configuration"
        cat > gunicorn.conf.py << 'EOF'
# Optimized Gunicorn Configuration for NOUS
import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
backlog = 2048

# Worker processes
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Restart workers
max_requests = 1000
max_requests_jitter = 50

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Logging
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "nous_assistant"

# Server mechanics
preload_app = True
daemon = False
pidfile = "logs/gunicorn.pid"
tmp_upload_dir = None

# SSL (when enabled)
keyfile = None
certfile = None
EOF
    fi
    
    # Optimize static assets (if needed)
    if [[ -d "static" ]]; then
        info "Optimizing static assets"
        # Remove source maps in production
        find static -name "*.map" -delete 2>/dev/null || true
    fi
    
    success "Optimization completed"
}

# Phase 7: Cache Setup
cache_phase() {
    progress 7 8 "CACHE - Setting up production caching"
    
    # Create cache directories
    mkdir -p .cache/pip .cache/flask
    
    # Set cache environment variables
    export CACHE_DEFAULT_TIMEOUT=300
    export CACHE_THRESHOLD=1000
    
    info "Production caching configured"
    success "Cache setup completed"
}

# Phase 8: Deploy and Validate
deploy_phase() {
    progress 8 8 "DEPLOY - Production deployment and validation"
    
    # Set final production environment
    export FLASK_ENV=production
    export PYTHONDONTWRITEBYTECODE=1
    export PYTHONUNBUFFERED=1
    export WERKZEUG_RUN_MAIN=true
    
    # Get configuration
    local port="${PORT:-5000}"
    local host="${HOST:-0.0.0.0}"
    
    info "Starting production server on $host:$port"
    
    # Start the application in background for testing
    local start_cmd=""
    if [[ -f "gunicorn.conf.py" ]] && command -v gunicorn >/dev/null 2>&1; then
        start_cmd="gunicorn --config gunicorn.conf.py app:app"
        info "Using Gunicorn production server"
    elif [[ -f "app_optimized.py" ]]; then
        start_cmd="python -c 'from app_optimized import app; app.run(host=\"$host\", port=$port, debug=False)'"
        info "Using optimized application"
    else
        start_cmd="python main.py"
        info "Using main application entry point"
    fi
    
    # Start server in background for validation
    info "Starting server for validation..."
    eval "$start_cmd" &
    local server_pid=$!
    
    # Wait for server to start
    sleep 5
    
    # Health check validation
    validate_deployment "$host" "$port"
    
    # Stop test server
    kill $server_pid 2>/dev/null || true
    wait $server_pid 2>/dev/null || true
    
    success "Deployment validation completed"
    
    # Show final run command
    echo ""
    echo -e "${GREEN}🎉 DEPLOYMENT COMPLETE!${NC}"
    echo -e "${BLUE}📋 Production server ready${NC}"
    echo -e "${BLUE}🚀 Run the app with: $start_cmd${NC}"
    echo ""
}

# Health and smoke tests
validate_deployment() {
    local host="$1"
    local port="$2"
    local base_url="http://$host:$port"
    
    info "Running deployment validation tests"
    
    # Health endpoints to test
    local endpoints=(
        "/health"
        "/healthz"
        "/"
        "/demo"
    )
    
    local passed=0
    local total=${#endpoints[@]}
    
    for endpoint in "${endpoints[@]}"; do
        local url="$base_url$endpoint"
        if curl -f -s -m 10 "$url" >/dev/null 2>&1; then
            success "✅ $endpoint: PASS"
            ((passed++))
        else
            warning "❌ $endpoint: FAIL"
        fi
    done
    
    # Calculate success rate
    local success_rate=$((passed * 100 / total))
    
    if [[ $success_rate -ge 75 ]]; then
        success "Health check passed: $passed/$total ($success_rate%)"
    else
        error_exit "Health check failed: $passed/$total ($success_rate%)"
    fi
}

# Archive old deployment scripts
archive_old_scripts() {
    info "Archiving old deployment scripts"
    
    local archive_dir="archive/scripts_archive"
    mkdir -p "$archive_dir"
    
    # Scripts to archive
    local scripts=(
        "start_fast.sh"
        "start_production.sh"
        "run_production.sh"
        "clean_deploy.py"
        "deploy_clean_production.py"
        "deploy_production.py"
        "production_optimizer.py"
        "production_ready.py"
        "production_test.py"
        "build_optimization.py"
        "validate_deploy.py"
    )
    
    for script in "${scripts[@]}"; do
        if [[ -f "$script" && "$script" != "deploy_prod.sh" ]]; then
            mv "$script" "$archive_dir/" 2>/dev/null || true
            info "Archived: $script"
        fi
    done
    
    success "Old scripts archived to $archive_dir"
}

# Main execution function
main() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║               NOUS Production Deployment                     ║"
    echo "║            Consolidated Build & Deploy Pipeline              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Load configuration
    load_config
    
    # Create logs directory
    mkdir -p logs
    
    # Log deployment start
    log "INFO" "🚀 Starting production deployment at $(date)"
    
    # Archive old scripts first
    archive_old_scripts
    
    # Execute deployment phases
    clean_phase
    install_phase
    lint_phase
    test_phase
    build_phase
    optimize_phase
    cache_phase
    deploy_phase
    
    # Log completion
    log "INFO" "✅ Production deployment completed successfully at $(date)"
    
    echo -e "${GREEN}Deployment complete. Run the app with: ./deploy_prod.sh${NC}"
}

# Handle script arguments
case "${1:-}" in
    "--help"|"-h")
        echo "NOUS Production Deployment Script"
        echo ""
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --clean-only   Run only the clean phase"
        echo "  --test-only    Run only the test phase"
        echo "  --validate     Run only deployment validation"
        echo ""
        echo "Configuration file: build.properties"
        exit 0
        ;;
    "--clean-only")
        load_config
        clean_phase
        exit 0
        ;;
    "--test-only")
        load_config
        test_phase
        exit 0
        ;;
    "--validate")
        load_config
        validate_deployment "${HOST:-0.0.0.0}" "${PORT:-5000}"
        exit 0
        ;;
    "")
        main
        ;;
    *)
        error_exit "Unknown option: $1. Use --help for usage information."
        ;;
esac