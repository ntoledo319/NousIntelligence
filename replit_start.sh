#!/bin/bash

echo "Starting NOUS Personal Assistant (Replit Deployment)..."

# Create required directories
mkdir -p flask_session uploads logs instance static/error templates

# Set permissions
chmod -R 777 flask_session uploads logs instance

# Make sure we have a static error page
if [ ! -f "static/error/404.html" ]; then
    # Create a simple error page if none exists
    mkdir -p static/error
    cat > static/error/404.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Page Not Found</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        h1 { color: #333; }
    </style>
</head>
<body>
    <h1>Page Not Found</h1>
    <p>The page you are looking for does not exist.</p>
    <p><a href="/">Go to Homepage</a></p>
</body>
</html>
EOF
fi

# Create a simple index page if none exists
if [ ! -f "templates/index.html" ]; then
    mkdir -p templates
    cat > templates/index.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>NOUS Personal Assistant</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1 { color: #6f42c1; }
    </style>
</head>
<body>
    <div class="container">
        <h1>NOUS Personal Assistant</h1>
        <p>Welcome to your personal assistant application.</p>
        <p>The application is currently running.</p>
    </div>
</body>
</html>
EOF
fi

# Environment variables
export PORT=8080
export FLASK_ENV=production
export SECRET_KEY=$(cat .secret_key 2>/dev/null || echo "tempsecretkey")
export SESSION_SECRET=$SECRET_KEY
export PYTHONUNBUFFERED=1

# Start the application using Python directly for reliable deployment on Replit
echo "Starting web server on port 8080..."
exec python replit_server.py