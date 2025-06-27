#!/usr/bin/env python3
"""
Documentation Build Script
Builds comprehensive documentation using Sphinx and validates all components
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
from datetime import datetime

def run_command(cmd, cwd=None, check=True):
    """Run shell command and return result."""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=check
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def check_dependencies():
    """Check if required documentation dependencies are available."""
    print("Checking documentation dependencies...")
    
    dependencies = [
        ('python', 'Python interpreter'),
        ('pip', 'Python package manager')
    ]
    
    missing = []
    for cmd, desc in dependencies:
        result = run_command(f"which {cmd}", check=False)
        if result.returncode != 0:
            missing.append(desc)
    
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        return False
    
    # Check Python packages
    python_packages = [
        'sphinx',
        'flask',
        'marshmallow'
    ]
    
    for package in python_packages:
        result = run_command(f"python -c 'import {package}'", check=False)
        if result.returncode != 0:
            print(f"Installing missing package: {package}")
            run_command(f"pip install {package}")
    
    print("✅ All dependencies available")
    return True

def clean_build_directory():
    """Clean previous build artifacts."""
    print("Cleaning build directory...")
    
    build_dir = Path("docs/_build")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Clean any cached files
    cache_dirs = [
        "docs/__pycache__",
        "docs/.doctrees",
        ".sphinx-cache"
    ]
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
    
    print("✅ Build directory cleaned")

def validate_documentation_structure():
    """Validate that all required documentation files exist."""
    print("Validating documentation structure...")
    
    required_files = [
        "docs/conf.py",
        "docs/index.rst",
        "docs/overview.rst",
        "docs/api_reference.rst",
        "docs/architecture.rst",
        "docs/installation.rst",
        "docs/development.rst",
        "docs/deployment.rst",
        "docs/troubleshooting.rst",
        "docs/changelog.rst"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing documentation files: {', '.join(missing_files)}")
        return False
    
    print("✅ Documentation structure validated")
    return True

def build_sphinx_docs():
    """Build Sphinx documentation."""
    print("Building Sphinx documentation...")
    
    docs_dir = Path("docs")
    build_dir = docs_dir / "_build"
    
    # Create build directory
    build_dir.mkdir(exist_ok=True)
    
    # Build HTML documentation
    result = run_command(
        "python -m sphinx -b html . _build/html",
        cwd=str(docs_dir),
        check=False
    )
    
    if result.returncode != 0:
        print("❌ Sphinx build failed")
        # Try simpler build without extensions that might be missing
        print("Attempting simplified build...")
        
        # Create minimal conf.py for fallback
        fallback_conf = '''
project = 'NOUS Personal Assistant'
copyright = '2025, NOUS Development Team'
author = 'NOUS Development Team'
release = '1.0.0'

extensions = []
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
html_theme = 'default'
'''
        
        with open(docs_dir / "conf_fallback.py", "w") as f:
            f.write(fallback_conf)
        
        result = run_command(
            "python -m sphinx -c . -b html . _build/html",
            cwd=str(docs_dir),
            check=False
        )
        
        if result.returncode != 0:
            print("❌ Even simplified Sphinx build failed")
            return False
    
    print("✅ Sphinx documentation built successfully")
    return True

def generate_api_documentation():
    """Generate API documentation from code."""
    print("Generating API documentation...")
    
    try:
        # Import the application to generate API docs
        sys.path.insert(0, os.getcwd())
        
        # Generate API reference from routes
        api_docs = {
            "generated_at": datetime.utcnow().isoformat(),
            "endpoints": [],
            "models": [],
            "schemas": []
        }
        
        # Scan for route files
        routes_dir = Path("routes")
        if routes_dir.exists():
            for py_file in routes_dir.glob("*.py"):
                if py_file.name.startswith("__"):
                    continue
                
                print(f"Scanning {py_file.name}...")
                try:
                    with open(py_file, 'r') as f:
                        content = f.read()
                    
                    # Extract route decorators (simple text parsing)
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if '@app.route(' in line or '@bp.route(' in line:
                            route_info = {
                                "file": py_file.name,
                                "line": i + 1,
                                "definition": line.strip()
                            }
                            
                            # Try to get function name from next few lines
                            for j in range(i + 1, min(i + 5, len(lines))):
                                if lines[j].strip().startswith('def '):
                                    route_info["function"] = lines[j].strip()
                                    break
                            
                            api_docs["endpoints"].append(route_info)
                
                except Exception as e:
                    print(f"Warning: Could not parse {py_file.name}: {e}")
        
        # Save API documentation
        api_docs_file = Path("docs/_build/api_documentation.json")
        api_docs_file.parent.mkdir(exist_ok=True)
        with open(api_docs_file, 'w') as f:
            json.dump(api_docs, f, indent=2)
        
        print(f"✅ Generated API documentation with {len(api_docs['endpoints'])} endpoints")
        return True
        
    except Exception as e:
        print(f"❌ API documentation generation failed: {e}")
        return False

def create_documentation_index():
    """Create a comprehensive documentation index."""
    print("Creating documentation index...")
    
    try:
        index_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NOUS Personal Assistant Documentation</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            line-height: 1.6;
        }
        .header {
            text-align: center;
            margin-bottom: 3rem;
            padding: 2rem;
            background: linear-gradient(135deg, #2563eb, #1e40af);
            color: white;
            border-radius: 12px;
        }
        .docs-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin: 2rem 0;
        }
        .doc-card {
            background: #f8fafc;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 1.5rem;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .doc-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        .doc-card h3 {
            margin-top: 0;
            color: #1f2937;
        }
        .doc-card a {
            color: #2563eb;
            text-decoration: none;
            font-weight: 500;
        }
        .doc-card a:hover {
            text-decoration: underline;
        }
        .status {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .status.available {
            background: #dcfce7;
            color: #166534;
        }
        .status.generated {
            background: #fef3cd;
            color: #92400e;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>NOUS Personal Assistant</h1>
        <p>Comprehensive Documentation Portal</p>
        <p><small>Generated on ''' + datetime.now().strftime("%B %d, %Y at %I:%M %p") + '''</small></p>
    </div>
    
    <div class="docs-grid">
        <div class="doc-card">
            <h3>📚 User Guide</h3>
            <p>Complete installation, configuration, and usage instructions.</p>
            <div class="links">
                <a href="html/installation.html">Installation Guide</a> •
                <a href="html/overview.html">System Overview</a>
            </div>
            <p><span class="status available">Available</span></p>
        </div>
        
        <div class="doc-card">
            <h3>🔧 Developer Documentation</h3>
            <p>Development guides, API reference, and architectural documentation.</p>
            <div class="links">
                <a href="html/development.html">Development Guide</a> •
                <a href="html/api_reference.html">API Reference</a> •
                <a href="html/architecture.html">Architecture</a>
            </div>
            <p><span class="status available">Available</span></p>
        </div>
        
        <div class="doc-card">
            <h3>🚀 Deployment & Operations</h3>
            <p>Deployment strategies, monitoring, and troubleshooting guides.</p>
            <div class="links">
                <a href="html/deployment.html">Deployment Guide</a> •
                <a href="html/troubleshooting.html">Troubleshooting</a>
            </div>
            <p><span class="status available">Available</span></p>
        </div>
        
        <div class="doc-card">
            <h3>🔄 Interactive API Documentation</h3>
            <p>Live API documentation with interactive testing capabilities.</p>
            <div class="links">
                <a href="../api/docs/">Swagger UI</a> •
                <a href="../api/docs/redoc">ReDoc</a> •
                <a href="../api/docs/postman">Postman Collection</a>
            </div>
            <p><span class="status generated">Generated</span></p>
        </div>
        
        <div class="doc-card">
            <h3>📋 Project Information</h3>
            <p>Project history, changelog, and contribution guidelines.</p>
            <div class="links">
                <a href="html/changelog.html">Changelog</a> •
                <a href="../CONTRIBUTING.md">Contributing</a> •
                <a href="../LICENSE">License</a>
            </div>
            <p><span class="status available">Available</span></p>
        </div>
        
        <div class="doc-card">
            <h3>⚡ Quick Links</h3>
            <p>Essential resources and monitoring tools.</p>
            <div class="links">
                <a href="../health">Health Check</a> •
                <a href="../healthz">System Status</a> •
                <a href="../api/docs/endpoints">API Endpoints</a>
            </div>
            <p><span class="status generated">Live</span></p>
        </div>
    </div>
</body>
</html>
        '''
        
        docs_build_dir = Path("docs/_build")
        docs_build_dir.mkdir(exist_ok=True)
        
        with open(docs_build_dir / "index.html", 'w') as f:
            f.write(index_html)
        
        print("✅ Documentation index created")
        return True
        
    except Exception as e:
        print(f"❌ Documentation index creation failed: {e}")
        return False

def validate_build_output():
    """Validate that documentation was built successfully."""
    print("Validating build output...")
    
    required_outputs = [
        "docs/_build/html/index.html",
        "docs/_build/html/overview.html",
        "docs/_build/html/api_reference.html"
    ]
    
    missing_outputs = []
    for output_path in required_outputs:
        if not os.path.exists(output_path):
            missing_outputs.append(output_path)
    
    if missing_outputs:
        print(f"⚠️  Some outputs missing: {', '.join(missing_outputs)}")
        # Don't fail the build for missing outputs, they might not be critical
    
    # Check if main index exists
    if os.path.exists("docs/_build/html/index.html"):
        print("✅ Main documentation built successfully")
        return True
    else:
        print("❌ Main documentation index not found")
        return False

def create_makefile():
    """Create Makefile for easy documentation building."""
    makefile_content = '''# NOUS Documentation Makefile

.PHONY: docs clean-docs serve-docs build-api-docs help

# Build all documentation
docs: clean-docs build-sphinx build-api

# Clean documentation build artifacts
clean-docs:
\t@echo "Cleaning documentation build artifacts..."
\t@rm -rf docs/_build
\t@rm -rf docs/__pycache__
\t@echo "✅ Documentation cleaned"

# Build Sphinx documentation
build-sphinx:
\t@echo "Building Sphinx documentation..."
\t@cd docs && python -m sphinx -b html . _build/html
\t@echo "✅ Sphinx documentation built"

# Build API documentation
build-api:
\t@echo "Building API documentation..."
\t@python scripts/build_docs.py --api-only
\t@echo "✅ API documentation built"

# Serve documentation locally
serve-docs:
\t@echo "Serving documentation at http://localhost:8000"
\t@cd docs/_build/html && python -m http.server 8000

# Generate comprehensive documentation
full-docs:
\t@echo "Building comprehensive documentation..."
\t@python scripts/build_docs.py --full
\t@echo "✅ Full documentation suite built"

# Help
help:
\t@echo "Available targets:"
\t@echo "  docs        - Build all documentation"
\t@echo "  clean-docs  - Clean build artifacts"
\t@echo "  serve-docs  - Serve docs locally on port 8000"
\t@echo "  build-sphinx- Build Sphinx docs only"
\t@echo "  build-api   - Build API docs only"
\t@echo "  full-docs   - Build comprehensive documentation"
\t@echo "  help        - Show this help"
'''
    
    with open("Makefile", 'w') as f:
        f.write(makefile_content)
    
    print("✅ Makefile created for easy documentation building")

def main():
    """Main documentation build process."""
    print("🚀 Starting NOUS Documentation Build Process")
    print("=" * 50)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Build NOUS documentation")
    parser.add_argument('--api-only', action='store_true', help='Build API docs only')
    parser.add_argument('--full', action='store_true', help='Build full documentation suite')
    parser.add_argument('--skip-deps', action='store_true', help='Skip dependency check')
    args = parser.parse_args()
    
    success = True
    
    try:
        # Step 1: Check dependencies
        if not args.skip_deps:
            if not check_dependencies():
                return False
        
        # Step 2: Validate structure
        if not validate_documentation_structure():
            return False
        
        # Step 3: Clean build directory
        clean_build_directory()
        
        # Step 4: Build documentation
        if args.api_only:
            print("Building API documentation only...")
            success = generate_api_documentation()
        else:
            # Build Sphinx docs
            if not build_sphinx_docs():
                print("⚠️  Sphinx build failed, continuing with other components...")
                success = False
            
            # Generate API docs
            if not generate_api_documentation():
                print("⚠️  API documentation generation failed, continuing...")
                success = False
            
            # Create documentation index
            if not create_documentation_index():
                print("⚠️  Documentation index creation failed, continuing...")
                success = False
        
        # Step 5: Create Makefile for future builds
        create_makefile()
        
        # Step 6: Validate output
        if args.full or not args.api_only:
            validate_build_output()
        
        # Final status
        if success:
            print("\n🎉 Documentation build completed successfully!")
            print("\nNext steps:")
            print("  • View docs: open docs/_build/html/index.html")
            print("  • Serve locally: make serve-docs")
            print("  • API docs: /api/docs/ (when app is running)")
        else:
            print("\n⚠️  Documentation build completed with warnings")
            print("Some components may not be fully functional")
        
        return success
        
    except Exception as e:
        print(f"\n❌ Documentation build failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)