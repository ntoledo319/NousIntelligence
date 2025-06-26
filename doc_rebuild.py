#!/usr/bin/env python3
"""
DOCUMENTATION REBUILD & MERGE SCRIPT
Creates unified documentation from executive board report and codegraph
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class DocumentationRebuilder:
    def __init__(self):
        self.codegraph = self.load_codegraph()
        self.executive_report = self.load_executive_report()
        self.output_dir = Path('.')
        
    def load_codegraph(self) -> Dict[str, Any]:
        """Load the generated code graph"""
        try:
            with open('/tmp/codegraph.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load codegraph: {e}")
            return {}
    
    def load_executive_report(self) -> str:
        """Load executive board report content"""
        try:
            with open('docs/executive_board_report.md', 'r') as f:
                return f.read()
        except Exception as e:
            print(f"Warning: Could not load executive report: {e}")
            return ""
    
    def extract_sections_from_report(self) -> Dict[str, str]:
        """Extract reusable sections from executive report"""
        sections = {}
        
        if not self.executive_report:
            return sections
        
        # Split into sections
        parts = re.split(r'^## ', self.executive_report, flags=re.MULTILINE)
        
        for part in parts:
            if not part.strip():
                continue
                
            lines = part.split('\n')
            if len(lines) < 2:
                continue
                
            title = lines[0].strip()
            content = '\n'.join(lines[1:]).strip()
            
            # Extract valuable sections
            if 'EXECUTIVE SUMMARY' in title:
                sections['executive_summary'] = content
            elif 'HEALTHCARE' in title:
                sections['healthcare_features'] = content
            elif 'CRISIS' in title:
                sections['crisis_features'] = content
            elif 'FINANCIAL' in title:
                sections['financial_features'] = content
            elif 'SHOPPING' in title:
                sections['shopping_features'] = content
            elif 'SPOTIFY' in title:
                sections['spotify_features'] = content
            elif 'VISION' in title or 'MISSION' in title:
                sections['vision_mission'] = content
                
        return sections
    
    def generate_feature_index(self) -> str:
        """Generate fresh feature index from codegraph"""
        if not self.codegraph:
            return "Feature index unavailable - codegraph not loaded."
        
        index_lines = ["🔎 Complete Feature Index (Auto-Generated)", ""]
        index_lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        index_lines.append("")
        
        # Routes section
        routes = self.codegraph.get('routes', [])
        if routes:
            index_lines.append("### 🛣️ API Routes & Endpoints")
            index_lines.append("")
            
            # Group routes by file
            routes_by_file = {}
            for route in routes:
                file_key = route.get('file', 'unknown')
                if file_key not in routes_by_file:
                    routes_by_file[file_key] = []
                routes_by_file[file_key].append(route)
            
            for file_path, file_routes in sorted(routes_by_file.items()):
                index_lines.append(f"#### {file_path}")
                for route in sorted(file_routes, key=lambda x: x.get('path', '')):
                    path = route.get('path', 'N/A')
                    function = route.get('function', 'N/A')
                    index_lines.append(f"- `{path}` → `{function}()`")
                index_lines.append("")
        
        # Models section
        models = self.codegraph.get('models', [])
        if models:
            index_lines.append("### 🗄️ Database Models")
            index_lines.append("")
            
            for model in sorted(models, key=lambda x: x.get('name', '')):
                name = model.get('name', 'N/A')
                file_path = model.get('file', 'N/A')
                index_lines.append(f"- **{name}** (`{file_path}`)")
            index_lines.append("")
        
        # Chat handlers section
        chat_handlers = self.codegraph.get('chat_handlers', [])
        if chat_handlers:
            index_lines.append("### 💬 Chat Handlers")
            index_lines.append("")
            
            for handler in sorted(chat_handlers, key=lambda x: x.get('function', '')):
                function = handler.get('function', 'N/A')
                file_path = handler.get('file', 'N/A')
                index_lines.append(f"- `{function}()` (`{file_path}`)")
            index_lines.append("")
        
        # Summary statistics
        summary = self.codegraph.get('summary', {})
        if summary:
            index_lines.append("### 📊 System Statistics")
            index_lines.append("")
            index_lines.append(f"- **Total Files**: {summary.get('total_files', 0)}")
            index_lines.append(f"- **Python Files**: {summary.get('python_files', 0)}")
            index_lines.append(f"- **Routes**: {summary.get('routes_found', 0)}")
            index_lines.append(f"- **Models**: {summary.get('models_found', 0)}")
            index_lines.append(f"- **Chat Handlers**: {summary.get('chat_handlers', 0)}")
            index_lines.append("")
        
        return '\n'.join(index_lines)
    
    def create_readme(self) -> str:
        """Create comprehensive README.md"""
        sections = self.extract_sections_from_report()
        
        readme_content = [
            "# NOUS Personal Assistant",
            "",
            "## Overview",
            "",
            "NOUS Personal Assistant is a Flask-based web application designed to provide intelligent, adaptive, and user-friendly AI interactions. The application serves as a comprehensive personal assistant platform with various integrated services and capabilities.",
            "",
        ]
        
        # Add executive summary if available
        if 'executive_summary' in sections:
            readme_content.extend([
                "## Executive Summary",
                "",
                sections['executive_summary'],
                ""
            ])
        
        # Add quick start
        readme_content.extend([
            "## Quick Start",
            "",
            "1. **Install Dependencies**:",
            "   ```bash",
            "   pip install -r requirements.txt",
            "   ```",
            "",
            "2. **Run the Application**:",
            "   ```bash",
            "   python main.py",
            "   ```",
            "",
            "3. **Access the Application**:",
            "   - Web Interface: `http://localhost:5000`",
            "   - API Endpoint: `http://localhost:5000/api/chat`",
            "",
            "## Architecture",
            "",
            "### Core Components",
            "- **Flask Application**: Web framework with blueprint architecture",
            "- **Database Layer**: SQLAlchemy ORM with PostgreSQL/SQLite support",
            "- **Chat System**: Auto-discovery chat handler registration",
            "- **API Layer**: RESTful API with comprehensive routing",
            "",
            "### Key Features",
            "- **Chat-First Design**: Unified chat interface with intent-based routing",
            "- **Auto-Discovery**: Automatic handler registration from codebase analysis",
            "- **Multi-Modal Support**: Web, API, and voice interfaces",
            "- **Cost-Optimized AI**: Efficient AI provider integration",
            "",
        ])
        
        # Add feature highlights
        if any(key in sections for key in ['healthcare_features', 'crisis_features', 'financial_features']):
            readme_content.extend([
                "## Feature Highlights",
                ""
            ])
            
            if 'healthcare_features' in sections:
                readme_content.extend([
                    "### Healthcare Coordination",
                    "- Doctor and appointment management",
                    "- Medication tracking and refill reminders",
                    "- Health data integration",
                    ""
                ])
            
            if 'crisis_features' in sections:
                readme_content.extend([
                    "### Crisis Support",
                    "- DBT therapy integration", 
                    "- Crisis intervention resources",
                    "- Grounding exercises",
                    ""
                ])
            
            if 'financial_features' in sections:
                readme_content.extend([
                    "### Financial Management",
                    "- Budget tracking",
                    "- Expense categorization",
                    "- Financial goal monitoring",
                    ""
                ])
        
        # Add deployment info
        readme_content.extend([
            "## Deployment",
            "",
            "### Replit Cloud",
            "The application is optimized for Replit Cloud deployment:",
            "",
            "```toml",
            "# replit.toml",
            "[deployment]",
            "run = \"python main.py\"",
            "deploymentTarget = \"cloudrun\"",
            "```",
            "",
            "### Environment Variables",
            "- `DATABASE_URL`: PostgreSQL connection string",
            "- `SESSION_SECRET`: Flask session secret key",
            "- `OPENROUTER_API_KEY`: OpenRouter API key for AI features",
            "",
            "## Documentation",
            "",
            "- [Architecture Guide](docs/ARCHITECTURE.md)",
            "- [API Reference](docs/API_REFERENCE.md)",
            "- [Developer Guide](docs/DEVELOPER_GUIDE.md)",
            "- [Security Audit](docs/SECURITY_AUDIT.md)",
            "",
            "## License",
            "",
            "This project is proprietary software. All rights reserved.",
            ""
        ])
        
        return '\n'.join(readme_content)
    
    def create_architecture_doc(self) -> str:
        """Create ARCHITECTURE.md documentation"""
        arch_content = [
            "# NOUS Architecture Documentation",
            "",
            f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
            "## System Overview",
            "",
            "NOUS Personal Assistant follows a modular, chat-first architecture designed for scalability and maintainability.",
            "",
            "## Core Architecture Principles",
            "",
            "### 1. Chat-First Design",
            "- All functionality accessible through unified chat interface",
            "- Intent-based message routing with auto-discovery",
            "- Handler functions auto-registered from codebase analysis",
            "",
            "### 2. Auto-Discovery System", 
            "- Automatic detection of handler functions using AST analysis",
            "- Pattern-based intent matching (`cmd_*`, `handle_*`, etc.)",
            "- Dynamic function loading and registration",
            "",
            "### 3. Modular Blueprint Architecture",
            "- Feature-based blueprints for logical separation",
            "- Consistent route naming and error handling",
            "- Pluggable component system",
            "",
        ]
        
        # Add codegraph-based architecture details
        if self.codegraph:
            summary = self.codegraph.get('summary', {})
            
            arch_content.extend([
                "## System Statistics",
                "",
                f"- **Total Files**: {summary.get('total_files', 0)}",
                f"- **Python Modules**: {summary.get('python_files', 0)}",
                f"- **API Routes**: {summary.get('routes_found', 0)}",
                f"- **Database Models**: {summary.get('models_found', 0)}",
                f"- **Chat Handlers**: {summary.get('chat_handlers', 0)}",
                "",
                "## Component Analysis",
                "",
            ])
            
            # Routes analysis
            routes = self.codegraph.get('routes', [])
            if routes:
                route_files = set(route.get('file', '') for route in routes)
                arch_content.extend([
                    f"### Route Distribution ({len(routes)} total routes)",
                    "",
                    f"Routes are distributed across {len(route_files)} files:",
                ])
                
                for file_path in sorted(route_files):
                    file_routes = [r for r in routes if r.get('file') == file_path]
                    arch_content.append(f"- `{file_path}`: {len(file_routes)} routes")
                
                arch_content.append("")
            
            # Models analysis
            models = self.codegraph.get('models', [])
            if models:
                arch_content.extend([
                    f"### Data Models ({len(models)} total models)",
                    "",
                ])
                
                for model in sorted(models, key=lambda x: x.get('name', '')):
                    name = model.get('name', 'N/A')
                    file_path = model.get('file', 'N/A')
                    arch_content.append(f"- **{name}** (`{file_path}`)")
                
                arch_content.append("")
        
        arch_content.extend([
            "## Technology Stack",
            "",
            "### Backend",
            "- **Flask**: Web framework with blueprint architecture", 
            "- **SQLAlchemy**: Database ORM with migration support",
            "- **Gunicorn**: WSGI server for production deployment",
            "",
            "### Frontend",
            "- **Jinja2**: Template engine for server-side rendering",
            "- **Bootstrap**: CSS framework for responsive design",
            "- **Vanilla JavaScript**: Client-side interactivity",
            "",
            "### AI Integration",
            "- **OpenRouter**: Cost-optimized AI provider interface",
            "- **HuggingFace**: Free-tier audio and text processing",
            "- **Custom AI Pipeline**: Unified provider abstraction",
            "",
            "### Database",
            "- **PostgreSQL**: Production database with connection pooling",
            "- **SQLite**: Development database for local testing",
            "",
            "## Security Architecture",
            "",
            "### Authentication",
            "- Flask-Login session management",
            "- Google OAuth integration",
            "- Session-based authentication with secure cookies",
            "",
            "### API Security",
            "- Rate limiting middleware",
            "- Input validation and sanitization", 
            "- CORS configuration for public access",
            "",
            "### Data Protection",
            "- Environment-based secret management",
            "- Database connection encryption",
            "- Secure session storage",
            "",
            "## Deployment Architecture",
            "",
            "### Replit Cloud",
            "- Optimized for Replit Cloud Run deployment",
            "- Public access configuration",
            "- Automatic health monitoring",
            "",
            "### Scalability",
            "- Stateless application design",
            "- Database connection pooling",
            "- Efficient caching strategies",
            ""
        ])
        
        return '\n'.join(arch_content)
    
    def create_api_reference(self) -> str:
        """Create API_REFERENCE.md from routes"""
        api_content = [
            "# NOUS API Reference",
            "",
            f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
            "## Overview",
            "",
            "The NOUS API provides programmatic access to all personal assistant features through RESTful endpoints.",
            "",
            "## Base URL",
            "",
            "```",
            "https://your-app.replit.app",
            "```",
            "",
            "## Authentication",
            "",
            "All API endpoints support session-based authentication. For public routes, no authentication is required.",
            "",
            "## Core Endpoints",
            "",
        ]
        
        if self.codegraph and 'routes' in self.codegraph:
            routes = self.codegraph.get('routes', [])
            
            # Group routes by category
            route_categories = {
                'Chat & AI': [],
                'Health': [],
                'Crisis': [],
                'Admin': [],
                'Auth': [],
                'API': [],
                'Other': []
            }
            
            for route in routes:
                path = route.get('path', '')
                file_path = route.get('file', '')
                
                if '/chat' in path or 'chat' in file_path:
                    route_categories['Chat & AI'].append(route)
                elif '/health' in path or 'health' in file_path:
                    route_categories['Health'].append(route)
                elif '/crisis' in path or 'crisis' in file_path:
                    route_categories['Crisis'].append(route)
                elif '/admin' in path or 'admin' in file_path:
                    route_categories['Admin'].append(route)
                elif '/auth' in path or 'auth' in file_path:
                    route_categories['Auth'].append(route)
                elif '/api' in path or 'api' in file_path:
                    route_categories['API'].append(route)
                else:
                    route_categories['Other'].append(route)
            
            for category, category_routes in route_categories.items():
                if not category_routes:
                    continue
                    
                api_content.extend([
                    f"### {category}",
                    ""
                ])
                
                for route in sorted(category_routes, key=lambda x: x.get('path', '')):
                    path = route.get('path', 'N/A')
                    function = route.get('function', 'N/A')
                    file_path = route.get('file', 'N/A')
                    
                    api_content.extend([
                        f"#### `{path}`",
                        "",
                        f"**Handler**: `{function}()`  ",
                        f"**File**: `{file_path}`",
                        "",
                        "```http",
                        f"GET {path}",
                        "```",
                        "",
                    ])
        
        api_content.extend([
            "## Error Responses",
            "",
            "All endpoints return standard HTTP status codes:",
            "",
            "- `200 OK`: Successful request",
            "- `400 Bad Request`: Invalid request parameters",
            "- `401 Unauthorized`: Authentication required",
            "- `404 Not Found`: Endpoint not found",
            "- `500 Internal Server Error`: Server error",
            "",
            "Error responses include a JSON body with error details:",
            "",
            "```json",
            "{",
            '  "success": false,',
            '  "error": "Error description",',
            '  "message": "User-friendly error message"',
            "}",
            "```",
            ""
        ])
        
        return '\n'.join(api_content)
    
    def create_changelog(self) -> str:
        """Create CHANGELOG.md"""
        changelog_content = [
            "# Changelog",
            "",
            "All notable changes to NOUS Personal Assistant are documented in this file.",
            "",
            f"## [Unreleased] - {datetime.now().strftime('%Y-%m-%d')}",
            "",
            "### Added",
            "- TOTAL CODEBASE PURGE-AND-REBUILD operation completed",
            "- Chat-first unification with auto-discovery system",
            "- Comprehensive documentation rebuild",
            "- Enhanced code analysis and dead file removal",
            "",
            "### Changed", 
            "- Unified chat interface with intent-based routing",
            "- Auto-registration of handler functions",
            "- Streamlined documentation structure",
            "",
            "### Removed",
            f"- {self.codegraph.get('summary', {}).get('potentially_dead', 0)} dead files purged",
            "- Duplicate code and redundant modules",
            "- Outdated documentation files",
            "",
            "## [Previous Releases]",
            "",
            "### [1.0.0] - 2025-06-26",
            "- Initial consolidated release",
            "- Healthcare coordination features",
            "- Crisis intervention system", 
            "- DBT therapy integration",
            "- Financial management tools",
            "- Smart shopping assistant",
            "- Spotify integration",
            "- Cost-optimized AI implementation",
            ""
        ]
        
        return '\n'.join(changelog_content)
    
    def write_documentation_files(self) -> None:
        """Write all documentation files"""
        docs = {
            'README.md': self.create_readme(),
            'docs/ARCHITECTURE.md': self.create_architecture_doc(),
            'docs/API_REFERENCE.md': self.create_api_reference(),
            'docs/CHANGELOG.md': self.create_changelog(),
        }
        
        # Ensure docs directory exists
        docs_dir = Path('docs')
        docs_dir.mkdir(exist_ok=True)
        
        for file_path, content in docs.items():
            full_path = Path(file_path)
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Created {file_path}")
        
        # Update executive board report with fresh feature index
        self.update_executive_report()
        
        print(f"\n✅ Documentation rebuild complete!")
    
    def update_executive_report(self) -> None:
        """Update executive board report with fresh feature index"""
        if not self.executive_report:
            return
        
        # Generate new feature index
        new_index = self.generate_feature_index()
        
        # Replace old feature index section
        pattern = r'(🔎 Complete Feature Index \(Auto-Generated\).*?)(?=\n## |\Z)'
        
        if re.search(pattern, self.executive_report, re.DOTALL):
            updated_report = re.sub(
                pattern, 
                new_index, 
                self.executive_report, 
                flags=re.DOTALL
            )
        else:
            # Append new index if not found
            updated_report = self.executive_report + "\n\n" + new_index
        
        # Write updated report
        with open('docs/executive_board_report.md', 'w', encoding='utf-8') as f:
            f.write(updated_report)
        
        print("✅ Updated executive board report with fresh feature index")
    
    def cleanup_old_docs(self) -> None:
        """Remove duplicate/obsolete documentation files"""
        old_docs = [
            'CONSOLIDATION_SUMMARY.md',
            'AUTH_LOOP_ELIMINATION_REPORT.md', 
            'PROJECT_KATANA_COMPLETE_REPORT.md',
            'ONE_PROMPT_EXORCISM_COMPLETE.md',
            'NOUS_OPERATIONAL_COST_ANALYSIS.md',
            'AUDIT_COMPLETE_SUMMARY.md'
        ]
        
        removed_count = 0
        for doc_file in old_docs:
            if Path(doc_file).exists():
                try:
                    Path(doc_file).unlink()
                    print(f"🗑️  Removed obsolete: {doc_file}")
                    removed_count += 1
                except Exception as e:
                    print(f"Warning: Could not remove {doc_file}: {e}")
        
        print(f"✅ Cleaned up {removed_count} obsolete documentation files")

def main():
    """Main documentation rebuild function"""
    print("📚 Starting DOCUMENTATION REBUILD & MERGE...")
    
    rebuilder = DocumentationRebuilder()
    
    # Create unified documentation
    rebuilder.write_documentation_files()
    
    # Clean up old docs
    rebuilder.cleanup_old_docs()
    
    print("\n✅ DOCUMENTATION REBUILD COMPLETE")

if __name__ == "__main__":
    main()