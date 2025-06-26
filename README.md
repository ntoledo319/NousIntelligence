# NOUS Personal Assistant

A streamlined, unified Flask-based personal assistant web application with public access and intelligent AI interactions.

## Overview

NOUS Personal Assistant has been completely refactored and consolidated into a single, clean application. All redundant entry points, deployment scripts, and duplicate files have been eliminated, resulting in a production-ready solution with a clear architecture.

## Quick Start

### Local Development
```bash
python3 main.py
```

### Production Deployment
The application is configured for automatic deployment on Replit with public access (no login required).

## Architecture

### Unified Entry Point
- **`nous_app.py`**: Single authoritative application file
- **`main.py`**: Clean entry point that launches the unified app
- **`replit.toml`**: Streamlined configuration for deployment

### Key Features
- **Public Access**: No Replit authentication required
- **Health Monitoring**: Built-in health check endpoints
- **Error Handling**: Comprehensive error pages and logging
- **Template Support**: Full HTML template system with fallback JSON responses
- **Responsive Design**: Mobile-first frontend approach

### Routes
- `/` - Main landing page
- `/health` - Health check endpoint (JSON/HTML)
- `/about` - About page
- `/features` - Features overview
- Error pages for 404 and 500 responses

## Project Structure

```
NOUS/
├── nous_app.py           # Unified application (main entry point)
├── main.py               # Application launcher
├── replit.toml           # Deployment configuration
├── templates/            # HTML templates
├── static/               # CSS, JS, images
├── backup/               # Archived redundant files
└── README.md             # This file
```

## Configuration

### Environment Variables
- `PORT`: Server port (default: 8080)
- `SESSION_SECRET`: Flask session secret key
- `FLASK_ENV`: Environment mode (production/development)

### Public Access
The application is configured with headers to ensure public accessibility:
- CORS enabled for all origins
- X-Frame-Options set to ALLOWALL
- Replit authentication disabled

## Health Monitoring

The `/health` endpoint provides:
- Application status
- System information
- Python version
- Timestamp
- Environment details

Returns JSON for API calls and HTML for browser requests.

## Deployment

### Replit Deployment
1. Click the "Deploy" button in Replit
2. The application will automatically start with public access
3. No additional configuration required

### Manual Deployment
```bash
python3 main.py
```

The server will start on `http://0.0.0.0:8080` with public access enabled.

## Refactoring History

This version represents a complete consolidation of multiple redundant entry points:
- Eliminated 15+ duplicate application files
- Consolidated 10+ deployment scripts
- Removed redundant configuration files
- Unified documentation
- Cleaned up project structure

All obsolete files have been moved to `backup/consolidated_redundant_files/` for reference.

## Version

Current Version: 1.0.0 (Unified Release)