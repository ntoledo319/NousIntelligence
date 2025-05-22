# NOUS Personal Assistant - Replit Deployment Guide

This guide explains how to deploy your NOUS Personal Assistant on Replit with continuous availability.

## Deployment Options

You have several options for deploying your NOUS Personal Assistant:

### Option 1: Quick Deployment (Recommended)

Run the Replit-optimized deployment script:

```bash
./replit_deploy.sh
```

This script:
- Sets up the necessary environment variables
- Generates a secure secret key
- Starts the application on port 8080

### Option 2: Alternative Deployment Methods

We've provided multiple deployment scripts to ensure your application runs correctly:

- `run_public.sh` - Basic deployment with minimal configuration
- `clean_start.sh` - Deployment with additional logging and error handling
- `replit_start.sh` - Optimized for Replit environment

Choose the one that works best for your specific needs.

## Continuous Operation

For continuous operation after deployment, Replit will automatically use the configuration in `.replit.toml` to keep your application running.

## Troubleshooting

If you encounter any issues:

1. Check the console logs for error messages
2. Verify the application is using port 8080
3. Ensure all required directories (static, templates, logs) exist
4. Try using a different deployment script if one is not working

## Access Your Application

Once deployed, your application will be available at:

- Local: http://localhost:8080
- Public: https://[your-repl-name].replit.app