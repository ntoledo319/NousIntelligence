# NOUS Personal Assistant - Deployment Steps

## How to Deploy Your App Publicly

Follow these steps to make your app publicly accessible (no Replit login) while preserving your internal Google authentication:

### Step 1: Prepare Your App
- Make sure your `app.py` and other files are working correctly
- Verify that Google authentication is properly configured in your app

### Step 2: Run the Public Access Deployment Script
```bash
./deploy_public_access.sh
```

### Step 3: Deploy in Replit
1. Click the **Deploy** button in the Replit interface
2. In the deployment settings:
   - Set to "Public"
   - Turn ON "Allow public access without login"
   - Set the Run command to `bash deploy_public_access.sh`
3. Click "Deploy" to finalize

### Step 4: Verify Public Access
- Open your app's URL in an incognito/private browser window
- Confirm you can access the app without being prompted to log in to Replit
- Your app's Google authentication should still work normally

## Important Configuration Files
- `public_replit.toml`: Contains the configuration to make your app publicly accessible
- `deploy_public_access.sh`: Script that applies the public access configuration

## Troubleshooting
If you're still seeing a Replit login page, try these steps:

1. Manually update the .replit file before deploying:
   ```bash
   cp public_replit.toml .replit
   ```

2. In the Replit deployment settings, make sure:
   - "Allow public access without login" is turned ON
   - The correct deployment script is being used

3. Check your app's deployment logs for any errors