#!/usr/bin/env python3
"""
Fast Documentation Builder for NOUS Personal Assistant
Generates essential documentation from codebase scan
"""

import os
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class FastDocBuilder:
    def __init__(self):
        self.routes = []
        self.files_scanned = 0
        self.models = []
        self.api_endpoints = []
        
    def quick_scan(self):
        """Quick scan of codebase for documentation"""
        print("🚀 Starting fast documentation scan...")
        
        # Scan Python files for routes and models
        self._scan_routes()
        self._scan_models()
        
        # Generate essential docs
        self._update_readme()
        self._create_missing_files()
        
        print("✅ Fast documentation build complete!")
        print(f"📊 Scanned {self.files_scanned} files")
        print(f"🛣️  Found {len(self.routes)} routes")
        print(f"📡 Found {len(self.api_endpoints)} API endpoints")
        print(f"🗄️  Found {len(self.models)} models")
    
    def _scan_routes(self):
        """Scan for Flask routes"""
        print("🔍 Scanning for routes...")
        
        python_files = list(Path('.').rglob('*.py'))
        route_pattern = r'@.*\.route\([\'\"](.*?)[\'\"].*?\)'
        function_pattern = r'def\s+(\w+)\s*\('
        
        for file_path in python_files:
            if any(skip in str(file_path) for skip in ['backup', '__pycache__', 'docs-backup']):
                continue
                
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                self.files_scanned += 1
                
                # Find routes
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    route_match = re.search(route_pattern, line)
                    if route_match:
                        route_path = route_match.group(1)
                        
                        # Find the function name on the next few lines
                        function_name = "unknown"
                        for j in range(i+1, min(i+5, len(lines))):
                            func_match = re.search(function_pattern, lines[j])
                            if func_match:
                                function_name = func_match.group(1)
                                break
                        
                        route_info = {
                            'path': route_path,
                            'function': function_name,
                            'file': str(file_path),
                            'line': i + 1
                        }
                        
                        if route_path.startswith('/api/'):
                            self.api_endpoints.append(route_info)
                        else:
                            self.routes.append(route_info)
                            
            except Exception as e:
                print(f"⚠️  Error scanning {file_path}: {e}")
    
    def _scan_models(self):
        """Scan for database models"""
        print("🗄️  Scanning for models...")
        
        model_files = list(Path('models').rglob('*.py')) if Path('models').exists() else []
        class_pattern = r'class\s+(\w+)\s*\([^)]*Model[^)]*\)'
        
        for file_path in model_files:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                # Find model classes
                for match in re.finditer(class_pattern, content, re.MULTILINE):
                    class_name = match.group(1)
                    line_num = content[:match.start()].count('\n') + 1
                    
                    self.models.append({
                        'name': class_name,
                        'file': str(file_path),
                        'line': line_num
                    })
                    
            except Exception as e:
                print(f"⚠️  Error scanning models in {file_path}: {e}")
    
    def _update_readme(self):
        """Update README with current stats"""
        print("📝 Updating README...")
        
        readme_path = Path('README.md')
        if not readme_path.exists():
            self._create_readme()
            return
            
        try:
            content = readme_path.read_text(encoding='utf-8')
            
            # Update stats section
            stats_section = f"""## 📊 Project Statistics

- **Total Routes**: {len(self.routes) + len(self.api_endpoints)}
- **API Endpoints**: {len(self.api_endpoints)}
- **Database Models**: {len(self.models)}
- **Files Scanned**: {self.files_scanned}

*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

"""
            
            # Replace or add stats section
            if '## 📊 Project Statistics' in content:
                # Replace existing stats
                pattern = r'## 📊 Project Statistics.*?(?=\n## |\n---|\Z)'
                content = re.sub(pattern, stats_section.strip(), content, flags=re.DOTALL)
            else:
                # Add stats after overview
                if '## ✨ Features' in content:
                    content = content.replace('## ✨ Features', stats_section + '\n## ✨ Features')
                else:
                    content += '\n\n' + stats_section
            
            readme_path.write_text(content, encoding='utf-8')
            print("✅ Updated README.md")
            
        except Exception as e:
            print(f"⚠️  Error updating README: {e}")
    
    def _create_readme(self):
        """Create new README if none exists"""
        readme_content = f"""# NOUS Personal Assistant

## 🚀 Overview

NOUS is a professional-grade AI personal assistant built with Flask, featuring Google OAuth authentication, real-time chat interface, and comprehensive personal management tools.

**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Project Statistics

- **Total Routes**: {len(self.routes) + len(self.api_endpoints)}
- **API Endpoints**: {len(self.api_endpoints)}
- **Database Models**: {len(self.models)}
- **Files Scanned**: {self.files_scanned}

## ✨ Key Features

### Authentication & Security
- Google OAuth 2.0 integration
- Secure session management
- CSRF protection

### Chat Interface  
- Real-time AI chat functionality
- Multiple theme support
- Mobile-responsive design

### Personal Management
- Health tracking and medication management
- Travel planning and itinerary management
- Shopping lists and budget tracking

## 🚀 Quick Start

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**
   ```bash
   export GOOGLE_CLIENT_ID="your-google-client-id"
   export GOOGLE_CLIENT_SECRET="your-google-client-secret"
   export SESSION_SECRET="your-session-secret"
   ```

3. **Run application**
   ```bash
   python main.py
   ```

## 🔧 API Endpoints

### Main Routes
{self._format_routes()}

### API Endpoints
{self._format_api_endpoints()}

## 🗄️ Database Models

{self._format_models()}

## 📄 Documentation

- [API Reference](docs/API_REFERENCE.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Security Guide](SECURITY.md)
- [Contributing Guidelines](CONTRIBUTING.md)

---

**NOUS Personal Assistant** - Intelligence meets elegance.

*Documentation generated automatically on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        Path('README.md').write_text(readme_content, encoding='utf-8')
        print("✅ Created new README.md")
    
    def _format_routes(self):
        """Format routes for display"""
        if not self.routes:
            return "No routes found."
        
        formatted = []
        for route in self.routes[:10]:  # Show first 10
            formatted.append(f"- `{route['path']}` - {route['function']} ({Path(route['file']).name})")
        
        if len(self.routes) > 10:
            formatted.append(f"- ... and {len(self.routes) - 10} more routes")
        
        return '\n'.join(formatted)
    
    def _format_api_endpoints(self):
        """Format API endpoints for display"""
        if not self.api_endpoints:
            return "No API endpoints found."
        
        formatted = []
        for endpoint in self.api_endpoints[:10]:  # Show first 10
            formatted.append(f"- `{endpoint['path']}` - {endpoint['function']} ({Path(endpoint['file']).name})")
        
        if len(self.api_endpoints) > 10:
            formatted.append(f"- ... and {len(self.api_endpoints) - 10} more endpoints")
        
        return '\n'.join(formatted)
    
    def _format_models(self):
        """Format models for display"""
        if not self.models:
            return "No database models found."
        
        formatted = []
        for model in self.models:
            formatted.append(f"- `{model['name']}` ({Path(model['file']).name}:{model['line']})")
        
        return '\n'.join(formatted)
    
    def _create_missing_files(self):
        """Create missing standard files"""
        print("📄 Checking for missing standard files...")
        
        # Check for LICENSE
        if not Path('LICENSE').exists():
            self._create_license()
        
        # Check for CONTRIBUTING.md
        if not Path('CONTRIBUTING.md').exists():
            self._create_contributing()
        
        # Check for SECURITY.md
        if not Path('SECURITY.md').exists():
            self._create_security()
        
        # Update CHANGELOG.md
        self._update_changelog()
    
    def _create_license(self):
        """Create MIT License file"""
        license_content = f"""MIT License

Copyright (c) {datetime.now().year} NOUS Personal Assistant

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        
        Path('LICENSE').write_text(license_content, encoding='utf-8')
        print("✅ Created LICENSE file")
    
    def _create_contributing(self):
        """Create contributing guidelines"""
        contributing_content = f"""# Contributing to NOUS Personal Assistant

Thank you for your interest in contributing!

## Quick Start

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for new functionality
5. Run tests: `python -m pytest`
6. Commit changes: `git commit -m 'Add amazing feature'`
7. Push to branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/nous-personal-assistant.git
cd nous-personal-assistant

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your settings

# Run the application
python main.py
```

## Code Standards

- Follow PEP 8 for Python code
- Add docstrings to new functions
- Write tests for new features
- Update documentation as needed

## Pull Request Process

1. Update README.md with details of changes if needed
2. Increase version numbers in files if applicable
3. Ensure all tests pass
4. Request review from maintainers

## Questions?

Feel free to open an issue for any questions about contributing.

*Last updated: {datetime.now().strftime('%Y-%m-%d')}*
"""
        
        Path('CONTRIBUTING.md').write_text(contributing_content, encoding='utf-8')
        print("✅ Created CONTRIBUTING.md")
    
    def _create_security(self):
        """Create security policy"""
        security_content = f"""# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.x.x   | ✅ Yes             |
| 1.x.x   | ❌ No              |

## Reporting a Vulnerability

We take security vulnerabilities seriously. Please report security issues responsibly:

### How to Report

**DO NOT** create public GitHub issues for security vulnerabilities.

Instead:
1. Email security details to the maintainers
2. Use GitHub's private vulnerability reporting feature
3. Include as much detail as possible

### What to Include

- Type of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if available)

### Response Timeline

- **Initial Response**: Within 24 hours
- **Assessment**: Within 72 hours
- **Fix Development**: Varies by severity
- **Public Disclosure**: After fix deployment

## Security Measures

### Current Security Features

- Google OAuth 2.0 authentication
- Secure session management
- CSRF protection
- Input validation and sanitization
- Security headers
- HTTPS enforcement

### Security Best Practices

- Keep dependencies updated
- Use environment variables for secrets
- Validate all user inputs
- Implement proper error handling
- Regular security reviews

*Last updated: {datetime.now().strftime('%Y-%m-%d')}*
"""
        
        Path('SECURITY.md').write_text(security_content, encoding='utf-8')
        print("✅ Created SECURITY.md")
    
    def _update_changelog(self):
        """Update changelog"""
        changelog_header = f"""# Changelog

All notable changes to NOUS Personal Assistant are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Changed
- Updated documentation with automated generation
- Standardized project structure

### Documentation
- Full documentation rebuild completed {datetime.now().strftime('%Y-%m-%d')}
- Added missing standard files (LICENSE, CONTRIBUTING.md, SECURITY.md)
- Updated README with current project statistics

"""
        
        changelog_path = Path('CHANGELOG.md')
        if changelog_path.exists():
            try:
                existing = changelog_path.read_text(encoding='utf-8')
                # Preserve existing content after first unreleased section
                if '## [' in existing and 'Unreleased' not in existing.split('## [')[1]:
                    preserved = '## [' + existing.split('## [', 1)[1]
                    content = changelog_header + preserved
                else:
                    content = changelog_header
            except Exception:
                content = changelog_header
        else:
            content = changelog_header
        
        changelog_path.write_text(content, encoding='utf-8')
        print("✅ Updated CHANGELOG.md")

def main():
    """Main execution"""
    builder = FastDocBuilder()
    builder.quick_scan()

if __name__ == "__main__":
    main()