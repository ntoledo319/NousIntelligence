# NOUS Personal Assistant - Deployment Guide

This guide provides instructions for deploying the NOUS Personal Assistant application on Replit.

## Quick Start

For quick deployment, simply run:

```bash
./deploy.sh
```

This script will:
1. Create necessary directories
2. Verify database connectivity
3. Check for static files
4. Start the application
5. Set up health monitoring

## Manual Deployment Steps

If you prefer to deploy manually, follow these steps:

1. **Prepare the environment**
   ```bash
   mkdir -p logs static templates flask_session instance uploads
   ```

2. **Verify database connectivity**
   ```bash
   python -c "from sqlalchemy import create_engine, text; engine = create_engine('$DATABASE_URL'); print(engine.execute(text('SELECT 1')).scalar())"
   ```

3. **Start the application**
   ```bash
   # For development
   ./run_app.sh
   
   # For production
   ./public_start.sh
   ```

4. **Monitor the application**
   ```bash
   ./health_check.sh
   ```

## Troubleshooting

### Application not starting

If the application doesn't start:

1. Check logs: `cat logs/deployment_*.log`
2. Verify database connectivity
3. Ensure port 8080 is not already in use
4. Try running in debug mode: `DEBUG_MODE=true ./public_start.sh`

### Database connection issues

If you encounter database connection problems:

1. Verify the `DATABASE_URL` environment variable is set correctly
2. Check database server status
3. Ensure the database exists and has the correct tables

### Static file issues

If you encounter issues with static files:

1. Check if `static/styles.css` exists
2. If missing, the deployment script will attempt to extract styles from `templates/layout.html`
3. Verify that `templates/layout.html` contains the necessary CSS styles

## Replit Deployment

For Replit deployment:

1. Make sure the `.replit.workflows` file is properly configured
2. Use the "Run" button in Replit to start the application
3. For continuous operation, use the Replit deployment feature in the tools panel

## Health Monitoring

The application includes a health monitoring system that:

1. Automatically checks the application health every minute
2. Restarts the application if it becomes unresponsive
3. Logs all health events to `logs/health_monitor.log`

To check the current health status, visit `/health` endpoint in your browser or use:

```bash
curl http://localhost:8080/health
```