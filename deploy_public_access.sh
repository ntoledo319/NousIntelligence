#!/bin/bash

# NOUS Personal Assistant - Public Access Deployment Script
# This script configures the app to be publicly accessible (no Replit login)
# while preserving the app's internal Google authentication

echo "======= NOUS Public Access Deployment ======="
echo "Starting deployment at $(date)"

# Create required directories and logs
mkdir -p logs static templates instance flask_session uploads
LOGFILE="logs/public_access_deployment_$(date +%Y%m%d).log"
echo "Public access deployment started at $(date)" > "$LOGFILE"

# Apply public access configuration
echo "Applying public access configuration..."
cp public_replit.toml replit.toml
echo "$(date): Public access configuration applied" >> "$LOGFILE"

# Ensure permissions are correct
chmod +x deploy.sh
chmod +x public_start.sh
chmod +x health_check.sh
echo "$(date): Permissions updated" >> "$LOGFILE"

# Run the standard deployment script
echo "Running main deployment script..."
bash deploy.sh

echo "======= Public Access Deployment Complete ======="
echo "Your app should now be publicly accessible without requiring Replit login"
echo "The internal Google authentication in your app is preserved"
echo "Deployment completed at $(date)" >> "$LOGFILE"