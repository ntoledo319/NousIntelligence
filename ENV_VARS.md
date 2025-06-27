# NOUS Environment Variables

This file documents all environment variables used by the NOUS Personal Assistant application. Store these in Replit Secrets for production or in a local `.env` file for development.

## Core Application (Required)

These variables **must** be set for the application to function correctly.

| Variable             | Description                                          | Default Value                 | Example                          |
| -------------------- | ---------------------------------------------------- | ----------------------------- | -------------------------------- |
| `DATABASE_URL`       | The full connection string for the PostgreSQL database. | `sqlite:///nous.db`           | `postgresql://user:pass@host/db` |
| `SESSION_SECRET`     | A long, random string used to sign session cookies.  | `nous-unified-config-2025`    | `a_very_long_and_random_string`  |
| `GOOGLE_CLIENT_ID`   | The Client ID for your Google OAuth 2.0 application. | (none)                        | `12345.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET`| The Client Secret for your Google OAuth 2.0 application. | (none)                        | `GOCSPX-abc123`                  |

## Core Application (Optional)

These variables have default values but can be overridden for specific deployment needs.

| Variable         | Description                                     | Default Value |
| ---------------- | ----------------------------------------------- | ------------- |
| `PORT`           | The port on which the Flask server will listen. | `5000`        |
| `HOST`           | The host address to bind the server to.         | `0.0.0.0`     |
| `FLASK_ENV`      | The environment for Flask (`development` or `production`). | `production`  |
| `CORS_ORIGINS`   | Comma-separated list of allowed CORS origins.   | `*`           |
| `BASE_URL`       | The public base URL of the application.         | `''`          |

## AI & External Services (Optional)

These variables enable integrations with third-party services.

| Variable                | Description                                                | Required for         |
| ----------------------- | ---------------------------------------------------------- | -------------------- |
| `OPENROUTER_API_KEY`    | API key for OpenRouter.ai (primary AI provider).           | AI Chat              |
| `HUGGINGFACE_API_KEY`   | API key for Hugging Face (used for TTS/STT).               | Voice Features       |
| `GOOGLE_API_KEY`        | General Google API key for services like Maps.             | Google Integrations  |
| `SPOTIFY_CLIENT_ID`     | Client ID for the Spotify API.                             | Spotify Integration  |
| `SPOTIFY_CLIENT_SECRET` | Client Secret for the Spotify API.                         | Spotify Integration  |
| `WEATHER_API_KEY`       | API key for a weather service provider.                    | Weather Feature      |

```bash
# Google OAuth (REQUIRED)
GOOGLE_REDIRECT_URI=http://localhost:5000/callback/google

# External Services (Optional)
AMAZON_API_KEY=<amazon_key>

# Beta Configuration
ENABLE_BETA_MODE=true               # Enable beta features (default: true)
BETA_ACCESS_CODE=BETANOUS2025       # Beta access code
MAX_BETA_TESTERS=30                 # Maximum beta users

# Security & Performance
REDIS_URL=redis://localhost:6379/0  # Caching (optional)
``` 