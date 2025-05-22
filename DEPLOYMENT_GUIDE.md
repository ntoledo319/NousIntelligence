# NOUS Personal Assistant - Deployment Guide

This guide provides instructions for properly deploying the NOUS Personal Assistant application and preventing common deployment issues.

## Pre-Deployment Checklist

Before deploying, ensure that:

- [ ] Database connection string is properly set in the environment (`DATABASE_URL`)
- [ ] Secret key is generated or provided (automatically handled by deployment scripts)
- [ ] Static files are in place in the `static` directory
- [ ] Template files are in place in the `templates` directory
- [ ] Required Python packages are installed (especially `gunicorn`)
- [ ] Log directories exist and have proper permissions

## Deployment Process

1. **Initialize the deployment environment**

   Run the deployment initialization script:
   ```bash
   ./deploy_init.sh
   ```
   
   This will:
   - Check database connectivity
   - Generate a secret key if needed
   - Create required directories
   - Set up logging

2. **Start the application**

   Run the production deployment script:
   ```bash
   ./public_start.sh
   ```
   
   This will:
   - Set required environment variables
   - Kill any conflicting processes
   - Start the application with Gunicorn using production settings

3. **Verify deployment**

   Check that the application is running by accessing the health check endpoint:
   ```bash
   curl http://localhost:8080/health
   ```

## Deployment Monitoring

The application includes a monitoring setup that:

1. Automatically logs deployment events to `logs/deployment_YYYYMMDD.log`
2. Provides a `/health` endpoint for checking application status
3. Includes the `monitor_deploy.sh` script that can be run to check and restart the application if needed

To set up regular monitoring, you can run:
```bash
./monitor_deploy.sh
```

## Troubleshooting Common Issues

### Application Not Starting

If the application doesn't start:

1. Check deployment logs: `cat logs/deployment_*.log`
2. Verify database connectivity
3. Ensure port 8080 is not already in use
4. Verify Gunicorn is installed: `which gunicorn`

### Database Connection Issues

If you encounter database connection problems:

1. Verify the `DATABASE_URL` environment variable is set correctly
2. Check database server status
3. Run the database connection test: `python -c "from sqlalchemy import create_engine, text; engine = create_engine('$DATABASE_URL'); print(engine.execute(text('SELECT 1')).scalar())"`

### Memory or Resource Issues

If the application becomes unresponsive:

1. Check system resources: `free -m` and `df -h`
2. Consider clearing old session files: `rm -rf flask_session/*`
3. Restart the application with `./public_start.sh`

## Keeping the Application Running

For continuous operation:

1. Use the monitoring script: `./monitor_deploy.sh`
2. Consider setting up a cron job to run the monitoring script periodically
3. Configure the application to start automatically after system reboots

## Security Considerations

- Keep the secret key file (`.secret_key`) secure and with restricted permissions
- Use HTTPS for all production deployments
- Regularly rotate database credentials
- Set up proper firewall rules to restrict access to ports 8080 (app) and 5432 (database)

## Environment Variables

Required environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Automatically set by deployment scripts
- `FLASK_ENV`: Set to "production" for deployment
- `PORT`: Usually 8080 for production