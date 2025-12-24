# Google OAuth Setup Guide

## Overview

This application uses Google OAuth 2.0 for secure user authentication. This guide explains how to configure OAuth for your deployment.

## Prerequisites

1. A Google Cloud Platform account
2. Your application deployed and accessible via HTTPS (required for production)

## Google Cloud Console Configuration

### Step 1: Create OAuth 2.0 Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select or create a project
3. Navigate to **APIs & Services** > **Credentials**
4. Click **Create Credentials** > **OAuth 2.0 Client ID**
5. Select **Web application** as the application type
6. Configure the following:

#### Authorized JavaScript Origins

Add your deployment URL(s):

```
https://your-domain.com
https://nousintelligence.onrender.com  (for Render)
http://localhost:8080                    (for local development)
```

#### Authorized Redirect URIs

**CRITICAL**: Add this exact callback URL:

```
https://your-domain.com/callback/google
https://nousintelligence.onrender.com/callback/google  (for Render)
http://localhost:8080/callback/google                   (for local development)
```

⚠️ **Important**: The redirect URI must be EXACTLY `/callback/google` - no variations!

### Step 2: Get Your Credentials

After creating the OAuth client, you'll receive:

- **Client ID**: Something like `123456789-abc123.apps.googleusercontent.com`
- **Client Secret**: Something like `GOCSPX-abc123xyz789`

## Environment Configuration

### Required Environment Variables

Set these in your deployment environment (Render, Replit, etc.):

```bash
# Required for OAuth
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-client-secret-here

# Required for sessions
SESSION_SECRET=your-long-random-secret-key-here

# Optional: Explicit redirect URI override
OAUTH_REDIRECT_URI=https://your-domain.com/callback/google

# Optional: Base URL override
BASE_URL=https://your-domain.com
```

### Generating a Secure SESSION_SECRET

```bash
# Linux/Mac
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Or
openssl rand -base64 32
```

### Local Development (.env file)

Create a `.env` file in the project root:

```bash
# OAuth Credentials
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-secret

# Session Secret (generate with: openssl rand -base64 32)
SESSION_SECRET=your-long-random-secret-here

# Database
DATABASE_URL=postgresql://localhost/nous_db

# Optional: Force specific callback URI
OAUTH_REDIRECT_URI=http://localhost:8080/callback/google
```

## Deployment-Specific Configuration

### Render

Render automatically sets these environment variables:

- `RENDER=true`
- `RENDER_EXTERNAL_URL` (e.g., `https://your-app.onrender.com`)
- `RENDER_EXTERNAL_HOSTNAME`

**You only need to set**:

1. `GOOGLE_CLIENT_ID`
2. `GOOGLE_CLIENT_SECRET`
3. `SESSION_SECRET`

The OAuth callback URI will be automatically detected.

### Replit

Replit sets:

- `REPL_URL` or `REPLIT_DOMAIN`

**You only need to set**:

1. `GOOGLE_CLIENT_ID`
2. `GOOGLE_CLIENT_SECRET`
3. `SESSION_SECRET`

### Other Platforms

If deploying elsewhere, set all environment variables including `BASE_URL` or `OAUTH_REDIRECT_URI`.

## OAuth Flow

### How It Works

1. **User clicks "Sign in with Google"**
   - Redirects to `/auth/google`
   - Generates secure CSRF token (state parameter)
   - Redirects to Google authorization page

2. **User authorizes on Google**
   - Google validates credentials
   - Redirects back to `/callback/google` with authorization code

3. **Token Exchange**
   - Application exchanges authorization code for access token
   - Validates CSRF state token
   - Fetches user info from Google

4. **User Creation/Login**
   - Creates or updates user in database
   - Encrypts and stores OAuth tokens
   - Logs user in and redirects to dashboard

### Security Features

✅ **CSRF Protection**: HMAC-signed state tokens with client fingerprinting
✅ **Token Encryption**: OAuth tokens encrypted at rest using Fernet
✅ **State Expiration**: OAuth state expires after 10 minutes
✅ **Client Fingerprinting**: IP address and User-Agent validation
✅ **Secure Redirects**: Only relative URLs allowed for post-auth redirects
✅ **Token Refresh**: Automatic token refresh when expired

## Troubleshooting

### Error: "redirect_uri_mismatch"

**Problem**: The callback URI doesn't match what's configured in Google Console.

**Solution**:

1. Check Google Console > Credentials > Your OAuth Client
2. Ensure `/callback/google` is in "Authorized redirect URIs"
3. Check application logs for the actual redirect URI being used:
   ```
   Using redirect URI: https://your-actual-domain.com/callback/google
   ```
4. Add that EXACT URL to Google Console

### Error: "OAuth not configured"

**Problem**: Missing environment variables.

**Solution**:

```bash
# Verify environment variables are set
echo $GOOGLE_CLIENT_ID
echo $GOOGLE_CLIENT_SECRET
echo $SESSION_SECRET
```

All three must have values. Restart your application after setting them.

### Error: "State validation failed"

**Problem**: CSRF token mismatch or expired.

**Causes**:

- User took too long (>10 minutes) between auth start and callback
- Session storage issues
- Multiple tabs attempting OAuth simultaneously
- SESSION_SECRET changed during OAuth flow

**Solution**: Have user try signing in again (don't reuse the callback URL).

### Error: "Token decryption failed"

**Problem**: Cannot decrypt stored OAuth tokens.

**Causes**:

- SESSION_SECRET was changed after tokens were encrypted
- Token corruption in database

**Solution**:

1. User must sign in again (triggers new token exchange)
2. Check SESSION_SECRET hasn't changed
3. Consider adding `TOKEN_ENCRYPTION_KEY` environment variable for separate encryption key

## Testing OAuth Locally

### Setup

1. Configure `http://localhost:8080/callback/google` in Google Console
2. Set environment variables in `.env`
3. Run the application:
   ```bash
   python3 app.py
   ```

### Test Flow

1. Navigate to `http://localhost:8080/auth/login`
2. Click "Sign in with Google"
3. Authorize on Google (may need to add localhost to allowed test users)
4. Should redirect back and log you in

### Debug Logging

Check logs for:

```
Initiating OAuth with redirect URI: http://localhost:8080/callback/google
OAuth state generated and stored securely
Google OAuth callback received at /callback/google
OAuth state validation: success
Token exchange successful
User user@gmail.com logged in successfully
```

## Security Best Practices

1. **Never commit credentials** - Use environment variables
2. **Use HTTPS in production** - Required by Google OAuth
3. **Rotate secrets regularly** - Change SESSION_SECRET periodically
4. **Monitor failed auth attempts** - Check logs for CSRF warnings
5. **Keep dependencies updated** - Especially `authlib` and `cryptography`
6. **Validate redirect URLs** - Application only allows relative redirects post-auth
7. **Use separate encryption key** - Set `TOKEN_ENCRYPTION_KEY` separate from `SESSION_SECRET`

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_CLIENT_ID` | Yes | None | OAuth client ID from Google Console |
| `GOOGLE_CLIENT_SECRET` | Yes | None | OAuth client secret from Google Console |
| `SESSION_SECRET` | Yes | None | Secret key for session encryption (32+ chars) |
| `OAUTH_REDIRECT_URI` | No | Auto-detected | Override callback URI |
| `BASE_URL` | No | Auto-detected | Base URL of your application |
| `TOKEN_ENCRYPTION_KEY` | No | Uses `SESSION_SECRET` | Separate key for token encryption |
| `DATABASE_URL` | Yes | None | PostgreSQL connection string |

## Support

If you encounter issues:

1. Check application logs for detailed error messages
2. Verify all environment variables are set correctly
3. Confirm Google Console redirect URI matches exactly
4. Test with a fresh incognito/private browsing window
5. Check the [Google OAuth documentation](https://developers.google.com/identity/protocols/oauth2)

## Migration from Old Implementation

If migrating from the old OAuth implementation:

1. Users will need to sign in again (old tokens won't work)
2. Update Google Console to use `/callback/google` (not `/auth/google/callback`)
3. Remove any hardcoded URLs from environment
4. Set new environment variables as documented above
5. Test thoroughly in staging before deploying to production
