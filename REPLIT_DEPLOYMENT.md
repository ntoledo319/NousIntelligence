# NOUS App - Replit Deployment Guide

This document explains how to deploy the NOUS Personal Assistant application on Replit.

## Replit Deployment

### Initial Setup

1. **Fork the Repl**: If you haven't already, fork this Repl to your account.

2. **Environment Variables**: Set up the following environment variables in the Replit Secrets tab:
   - `SECRET_KEY`: A random secret key for Flask session security
   - `GOOGLE_CLIENT_ID`: Your Google OAuth client ID
   - `GOOGLE_CLIENT_SECRET`: Your Google OAuth client secret
   - `GOOGLE_REDIRECT_URI`: Will be automatically set to your Replit URL, but you can override it if needed

3. **Run the Application**: Click the Run button or use the automatically configured start script.

### Authentication

The application uses Google OAuth for authentication. You need to:

1. Create a Google Cloud Platform project
2. Enable the Google OAuth API
3. Configure OAuth consent screen
4. Create OAuth credentials (Web application type)
5. Add the following Authorized redirect URIs:
   - `https://[your-repl-slug].replit.app/callback/google`

### Database

The application uses SQLite by default. The database file will be stored in the `instance` directory.

### Troubleshooting

If you encounter issues with the deployment, try the following:

1. **Session Issues**: Clear the session directory with `rm -rf flask_session/*`
2. **Database Issues**: Reset the database with `rm -rf instance/*.sqlite && python run_migrations.py`
3. **Dependencies**: If new dependencies have been added, they should be installed automatically. If not, run `pip install -r requirements.txt`

## File Structure

```
NOUS/
├── app.py                  # Application entry point
├── app_factory.py          # App factory pattern implementation
├── main.py                 # Main application runner
├── config.py               # Configuration settings
├── models.py               # Database models
├── auth/                   # Authentication modules
├── routes/                 # Route definitions
├── static/                 # Static assets
├── templates/              # HTML templates
├── utils/                  # Utility functions
├── run_migrations.py       # Database migration script
├── gunicorn_config.py      # Gunicorn configuration for production
├── start.sh                # Startup script
└── .replit                 # Replit configuration
```

## Commands

- `./start.sh` - Start the application (used by Replit automatically)
- `./run.sh` - Start in development mode (for local development)

## Common Issues and Solutions

### OAuth Callback Issues

If you encounter problems with Google OAuth callbacks:

1. Make sure your redirect URI in Google Cloud Console exactly matches your Replit URL
2. Check the console logs for any errors related to the OAuth flow
3. Try clearing your browser cookies and cache

### Port Configuration

The application runs on port 8080 in Replit. This is automatically configured by the start script.

### Session Persistence

If you're having issues with session persistence:

1. Make sure the `flask_session` directory has the correct permissions
2. Check that the `SECRET_KEY` environment variable is set
3. Clear the session directory and restart the application

---

If you need further assistance, please check the application logs or contact the developer. 