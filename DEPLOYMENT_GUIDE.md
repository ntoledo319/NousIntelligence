# NOUS Deployment Guide

This guide outlines the deployment process and improvements made to ensure reliable deployment of the NOUS application.

## Deployment Improvements

The following improvements have been made to ensure reliable deployment:

### 1. Error Handling and Recovery
- Enhanced error handling in `start.sh` with better logging and error recovery
- Improved exception handling in `main.py` to gracefully handle and recover from errors
- Added database connection health checks and automatic reconnection
- Created custom error pages (404, 500, 503) for better user experience

### 2. Deployment Verification
- Created `verify_deployment.py` to check all prerequisites before deployment
- Implemented `deployment_recovery.py` to automatically fix common deployment issues
- Added comprehensive health check endpoint at `/health` for system monitoring
- Enhanced logging through `utils/deployment_logger.py` for better visibility into issues

### 3. Configuration Enhancements
- Improved Gunicorn configuration with environment validation
- Better environment variable handling with defaults and validation
- Enhanced directory and permission management
- Added proper workflow configuration for Replit

## Deployment Process

To deploy the NOUS application, follow these steps:

1. **Verify Deployment Readiness**:
   ```
   python verify_deployment.py
   ```
   Resolve any critical issues reported before proceeding.

2. **Set Required Environment Variables**:
   - `DATABASE_URL`: PostgreSQL connection string
   - `SECRET_KEY` or `SESSION_SECRET`: For secure session management
   - `FLASK_ENV`: Set to "production" for deployment

3. **Optional Environment Variables**:
   - `GOOGLE_CLIENT_ID` & `GOOGLE_CLIENT_SECRET`: For Google authentication
   - `SPOTIFY_CLIENT_ID` & `SPOTIFY_CLIENT_SECRET`: For Spotify integration

4. **Deploy the Application**:
   Use Replit's deployment feature to deploy the application.

## Troubleshooting

If deployment issues occur, you can use the following tools:

1. **Automatic Recovery**:
   ```
   python deployment_recovery.py --fix-all
   ```
   This will automatically fix common deployment issues.

2. **Health Check**:
   Access the `/health` endpoint to see detailed system status.

3. **Check Logs**:
   Examine logs in the `logs` directory, particularly the deployment logs.

## Maintenance

For ongoing maintenance:

1. **Database Migrations**:
   ```
   python run_migrations.py
   ```

2. **Verify Secret Key**:
   Ensure the `.secret_key` file exists and has proper permissions.

3. **Directory Permissions**:
   Periodically verify that critical directories (`flask_session`, `uploads`, `logs`, `instance`) have proper permissions.

## Deployment Best Practices

1. Always run `verify_deployment.py` before deploying
2. Test the application thoroughly after deployment
3. Monitor the application using the `/health` endpoint
4. Keep database migrations up to date
5. Ensure proper error pages are in place
6. Configure OAuth redirects to match the deployed domain
7. Use production-grade settings in `gunicorn_config.py`