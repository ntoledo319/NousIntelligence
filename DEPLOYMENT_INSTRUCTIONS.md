# NOUS Personal Assistant - Deployment Instructions

## Overview
This document provides instructions for deploying the NOUS Personal Assistant application on Replit.

## Quick Deployment Steps

1. **Update your Replit configuration**
   - In the Replit interface, go to the "Tools" menu and select "Secrets"
   - Make sure you have a `SESSION_SECRET` set (a random secure string)
   - If needed, add `DATABASE_URL` if you want database functionality

2. **Configure the run command**
   - In the Replit interface, use the "Run" button settings
   - Set the run command to: `bash run_public.sh`
   - This will use our public deployment script that creates the necessary files and starts the server

3. **Run the application**
   - Click the "Run" button in the Replit interface
   - Wait for the application to start (you should see "Starting NOUS Personal Assistant (Public Version)...")
   - The app will be available on port 8080

4. **Make your app public**
   - In the Replit interface, go to the "Share" button at the top-right
   - Enable "Public" to make your app accessible to everyone
   - Your app will be available at: `https://[your-repl-name].[your-username].repl.co`

## Alternative Deployment Options

### Using the reliable minimal version
If you prefer a simpler deployment with fewer features:
```
bash run_reliable.sh
```

### Using the full-featured version with database support
If you need database functionality and all advanced features:
```
bash flask_app.sh
```

## Troubleshooting

If you encounter any issues with deployment:

1. Check the logs for error messages
2. Verify that all required directories are created (flask_session, logs, templates, static)
3. Try restarting the Replit instance
4. If you're still having issues, try using one of the alternative deployment scripts

## Post-Deployment

After deploying your app:

1. Test it by navigating to the public URL
2. Check the `/health` endpoint to verify the application is functioning correctly
3. Visit the `/api/info` endpoint to see API information