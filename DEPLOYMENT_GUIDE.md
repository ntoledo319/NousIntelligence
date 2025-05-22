# NOUS Personal Assistant - Continuous Deployment Guide

This guide provides step-by-step instructions to ensure your NOUS Personal Assistant runs continuously on Replit.

## Setting Up Continuous Operation

### Option 1: Using Replit's Run Button

1. Click the **Run** button at the top of your Replit workspace.
2. Replit will automatically use your `.replit` configuration to run the application.
3. The application will continue running as long as your Replit is active.

### Option 2: Using Deployment Scripts

We've provided several deployment scripts to help you run your application:

- **`replit_deploy.sh`** (Recommended): Optimized for Replit with proper environment setup.
- **`run_public.sh`**: Simple script for quickly running the public version.
- **`clean_start.sh`**: Enhanced script with better error handling.

To use any of these scripts:
```bash
# Example:
./replit_deploy.sh
```

### Option 3: Manual Startup

If you prefer to start the application manually:
```bash
# Start with Python directly
python replit_app.py

# Or use gunicorn for production (if installed)
gunicorn 'nous_public:app' --bind '0.0.0.0:8080'
```

## Keeping Your App Running Continuously

To ensure your app runs continuously (even when you're not using the editor):

1. Go to the **Tools** panel in your Replit workspace
2. Select **Deployments**
3. Click "Deploy" to deploy your application
4. Your app will now run continuously on its own URL

For more persistent operation, consider upgrading to Replit's Deployment service, which provides continuous uptime.

## File Structure

- **`nous_public.py`**: The main application file (public version, no login required)
- **`replit_app.py`**: Replit-specific entry point
- **`static/`**: Static files (CSS, JS, images)
- **`templates/`**: HTML templates
- **`logs/`**: Application logs

## Troubleshooting

If you encounter any issues:

1. Check the console for error messages
2. Verify port 8080 is being used 
3. Try restarting the Replit environment
4. If one script doesn't work, try an alternative deployment script