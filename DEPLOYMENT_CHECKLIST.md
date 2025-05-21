# NOUS Deployment Checklist

This checklist helps ensure the NOUS application deploys successfully and remains stable in production.

## Pre-Deployment Requirements

- [ ] Database connection string is properly set in environment variables
- [ ] Secret key is properly set and secured
- [ ] Static files are properly organized and accessible
- [ ] Required dependencies are listed in requirements.txt
- [ ] Database migrations are up-to-date
- [ ] Error pages are properly configured
- [ ] Session management is configured correctly
- [ ] CSRF protection is enabled
- [ ] Google OAuth credentials are configured (if using Google login)

## Environment Variables

Ensure these environment variables are properly set:

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY` or `SESSION_SECRET`: For secure session management
- `FLASK_ENV`: Set to "production" for deployment
- `PORT`: Usually 8080 for Replit deployment
- `GOOGLE_CLIENT_ID`: If using Google authentication
- `GOOGLE_CLIENT_SECRET`: If using Google authentication
- `GOOGLE_REDIRECT_URI`: Callback URL for Google OAuth

## Deployment Process

1. Verify all checks in the pre-deployment section
2. Run database migrations: `python run_migrations.py`
3. Test application startup: `gunicorn -c gunicorn_config.py main:app`
4. Verify application routes and static file serving
5. Check error handling functionality
6. Verify session handling and persistence
7. Monitor application logs for any errors

## Common Deployment Issues

- **Database Connection Errors**: Verify DATABASE_URL is correct and the database is accessible
- **Static File Serving Issues**: Check MIME types and file paths
- **OAuth Callback Errors**: Ensure the redirect URI matches what's configured in the Google Developer Console
- **Session Storage Issues**: Ensure flask_session directory exists and has proper permissions
- **Missing Dependencies**: Make sure all requirements are installed
- **Port Binding Issues**: Make sure the correct port is being used (8080 for Replit)