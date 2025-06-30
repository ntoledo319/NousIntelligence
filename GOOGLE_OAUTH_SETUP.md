# Google Cloud Console Redirect URI Configuration

## Required Redirect URIs

Add ALL of these redirect URIs to your Google Cloud Console OAuth 2.0 client:

### Replit Deployment URLs:
- https://nous.replit.app/auth/google/callback
- https://nous-assistant.replit.app/auth/google/callback
- https://workspace.replit.dev/auth/google/callback

### Common Replit Patterns:
- https://[YOUR-REPL-NAME].replit.app/auth/google/callback
- https://[YOUR-REPL-NAME].[YOUR-USERNAME].replit.app/auth/google/callback

### Development URLs (if testing locally):
- http://localhost:8080/auth/google/callback
- http://127.0.0.1:8080/auth/google/callback

## How to Configure:

1. Go to Google Cloud Console (https://console.cloud.google.com/)
2. Select your project
3. Navigate to "APIs & Services" > "Credentials"
4. Click on your OAuth 2.0 Client ID
5. In "Authorized redirect URIs" section, add ALL the URLs above
6. Save the changes

## Troubleshooting:

If OAuth still doesn't work after adding redirect URIs:
1. Wait 5-10 minutes for Google's changes to propagate
2. Clear your browser cache and cookies
3. Try the OAuth flow again
4. Check that GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are set in Replit Secrets

## Current Deployment:

To find your exact deployment URL:
1. Check the address bar when your app is running
2. Use that exact URL + "/auth/google/callback" as a redirect URI
