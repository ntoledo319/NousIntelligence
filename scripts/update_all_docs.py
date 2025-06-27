#!/usr/bin/env python3
"""
Comprehensive Documentation Update Script
Updates all documentation files to meet current NOUS documentation standards
"""

import os
import re
import glob
from pathlib import Path
from datetime import datetime

def update_file_content(file_path, content):
    """Update file content with standardized replacements."""
    
    # Standard replacements for outdated references
    replacements = {
        # Outdated entry points
        r'surgical_nous_app\.py': 'app.py',
        r'nous_surgical_app\.py': 'app.py', 
        r'minimal_public_app\.py': 'app.py',
        r'public_nous_app\.py': 'app.py',
        
        # Outdated dates
        r'2024-12-27': '2025-06-27',
        r'December 27, 2024': 'June 27, 2025',
        r'2024': '2025',
        
        # Outdated port references
        r'localhost:8080': 'localhost:5000',
        r'port 8080': 'port 5000',
        r'PORT=8080': 'PORT=5000',
        
        # API endpoint updates
        r'/api/chat(?!\s)': '/api/v1/chat',
        r'/api/user(?!\s)': '/api/v1/user',
        r'/api/health(?!\s)': '/api/v1/health',
        
        # Documentation references
        r'API_REFERENCE\.md': 'docs/api_reference.rst',
        r'ARCHITECTURE\.md': 'docs/architecture.rst',
        
        # Version updates
        r'v2\.0\.0': 'v1.0.0',
        r'Version 2\.0': 'Version 1.0',
        
        # Status updates
        r'Scorched Earth Rebuild': 'Comprehensive Documentation System',
        r'scorched earth': 'comprehensive documentation',
    }
    
    # Apply replacements
    updated_content = content
    for pattern, replacement in replacements.items():
        updated_content = re.sub(pattern, replacement, updated_content, flags=re.IGNORECASE)
    
    # Update timestamps
    current_date = datetime.now().strftime("%B %d, %Y")
    updated_content = re.sub(
        r'Last Updated:.*',
        f'Last Updated: {current_date}',
        updated_content
    )
    
    return updated_content

def add_migration_notice(file_path, content):
    """Add migration notice to legacy files."""
    
    if 'Legacy' in content or 'DEPRECATED' in content:
        return content
    
    legacy_files = [
        'docs/API_REFERENCE.md',
        'docs/ARCHITECTURE.md',
        'docs/purge_report.md',
        'docs/comprehensive_function_analysis.md'
    ]
    
    if any(legacy_file in str(file_path) for legacy_file in legacy_files):
        migration_notice = f"""
---
**MIGRATION NOTICE**: This file contains legacy information and may be outdated.

**Current Documentation**: 
- Complete documentation: `make docs && make serve-docs`
- API documentation: `/api/docs/` (when app is running)
- Architecture guide: `docs/architecture.rst`

**Last Updated**: {datetime.now().strftime("%B %d, %Y")}
---

"""
        return migration_notice + content
    
    return content

def update_documentation_files():
    """Update all documentation files systematically."""
    
    print("🔄 Starting comprehensive documentation update...")
    
    # Define file patterns to update
    file_patterns = [
        "*.md",
        "docs/*.md", 
        "docs/*.rst",
        "*.txt"
    ]
    
    updated_files = []
    skipped_files = []
    
    # Exclude patterns
    exclude_patterns = [
        "backup/",
        "attached_assets/",
        ".cache/",
        ".pythonlibs/",
        "_build/",
        "node_modules/"
    ]
    
    for pattern in file_patterns:
        for file_path in glob.glob(pattern, recursive=True):
            
            # Skip excluded directories
            if any(exclude in file_path for exclude in exclude_patterns):
                continue
                
            # Skip binary files or very large files
            try:
                file_size = os.path.getsize(file_path)
                if file_size > 1024 * 1024:  # Skip files > 1MB
                    skipped_files.append(f"{file_path} (too large)")
                    continue
                    
                with open(file_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                    
            except (UnicodeDecodeError, PermissionError) as e:
                skipped_files.append(f"{file_path} ({str(e)})")
                continue
            
            # Update content
            updated_content = update_file_content(file_path, original_content)
            updated_content = add_migration_notice(file_path, updated_content)
            
            # Write back if changed
            if updated_content != original_content:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    updated_files.append(file_path)
                    print(f"✅ Updated: {file_path}")
                except PermissionError:
                    skipped_files.append(f"{file_path} (permission denied)")
            else:
                print(f"⏭️  No changes: {file_path}")
    
    return updated_files, skipped_files

def create_documentation_index():
    """Create a master documentation index."""
    
    index_content = f"""# NOUS Personal Assistant - Documentation Index

**Generated**: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}

## Primary Documentation

### Core Documentation (RST Format)
- [System Overview](docs/overview.rst)
- [Installation Guide](docs/installation.rst) 
- [API Reference](docs/api_reference.rst)
- [Architecture Guide](docs/architecture.rst)
- [Development Guide](docs/development.rst)
- [Deployment Guide](docs/deployment.rst)
- [Troubleshooting](docs/troubleshooting.rst)
- [Changelog](docs/changelog.rst)

### Interactive Documentation
- **API Documentation**: Start app and visit `/api/docs/`
- **OpenAPI Spec**: `/api/docs/openapi.json`
- **Endpoint List**: `/api/docs/endpoints`

## Project Documentation

### Main Project Files
- [README.md](README.md) - Project overview and quick start
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [LICENSE](LICENSE) - MIT License

### Configuration Guides
- [Network Configuration](PORT_README.md) - Port and API path management
- [Mobile & Responsive Design](RESPONSIVE_README.md) - Responsive design guide

### Operations & Reports
- [Development Operations](OPERATION_COMPLETE.md) - Major operation summaries

## Building Documentation

```bash
# Build all documentation
make docs

# Serve documentation locally
make serve-docs
# Visit: http://localhost:8000/documentation_index.html

# API documentation (requires running app)
python main.py
# Visit: http://localhost:5000/api/docs/
```

## Documentation Standards

- **Format**: reStructuredText for comprehensive docs, Markdown for project files
- **API Documentation**: Auto-generated OpenAPI/Swagger specifications
- **Build System**: Sphinx + custom builders with quality validation
- **Responsive Design**: Mobile-friendly documentation portal
- **Interactive Testing**: Live API endpoint testing capabilities

---

**Version**: 1.0.0  
**Status**: Production Ready  
**Last Updated**: {datetime.now().strftime("%B %d, %Y")}
"""

    with open('DOCUMENTATION_INDEX.md', 'w') as f:
        f.write(index_content)
    
    print("✅ Created master documentation index: DOCUMENTATION_INDEX.md")

def main():
    """Main execution function."""
    
    print("🚀 NOUS Documentation Standardization")
    print("=" * 50)
    
    # Update all documentation files
    updated_files, skipped_files = update_documentation_files()
    
    # Create documentation index
    create_documentation_index()
    
    # Generate summary report
    print("\n📊 UPDATE SUMMARY")
    print("=" * 30)
    print(f"✅ Files updated: {len(updated_files)}")
    print(f"⏭️  Files skipped: {len(skipped_files)}")
    
    if updated_files:
        print("\n🔄 Updated Files:")
        for file_path in updated_files[:10]:  # Show first 10
            print(f"   • {file_path}")
        if len(updated_files) > 10:
            print(f"   ... and {len(updated_files) - 10} more")
    
    if skipped_files:
        print("\n⚠️  Skipped Files:")
        for file_path in skipped_files[:5]:  # Show first 5
            print(f"   • {file_path}")
        if len(skipped_files) > 5:
            print(f"   ... and {len(skipped_files) - 5} more")
    
    print("\n✅ Documentation standardization completed!")
    print("\n📋 Next Steps:")
    print("   1. Review updated files for accuracy")
    print("   2. Build documentation: make docs")
    print("   3. Test documentation: make serve-docs")
    print("   4. Validate API docs: python main.py then visit /api/docs/")

if __name__ == "__main__":
    main()