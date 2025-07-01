# Secure Configuration Template
# Use this template to ensure all environment variables are properly configured

# Required Environment Variables:
# SESSION_SECRET - Must be 32+ characters
# DATABASE_URL - PostgreSQL connection string
# GOOGLE_CLIENT_ID - OAuth client ID
# GOOGLE_CLIENT_SECRET - OAuth client secret

import os

def validate_required_env_vars():
    required_vars = [
        'SESSION_SECRET',
        'DATABASE_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {missing_vars}")
    
    # Validate SESSION_SECRET length
    secret_key = os.environ.get('SESSION_SECRET', '')
    if len(secret_key) < 32:
        raise ValueError("SESSION_SECRET must be at least 32 characters long")
    
    return True

# Call validation on import
validate_required_env_vars()
