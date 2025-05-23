#!/bin/bash

# NOUS Personal Assistant - Public Deployment Setup
# This script prepares the application for production deployment

echo "===== NOUS Personal Assistant - Public Deployment Setup ====="
echo "Preparing application for production deployment..."

# Create necessary directories
mkdir -p static/css static/js templates flask_session logs

# Install required packages if needed
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Set environment variables for deployment
export FLASK_APP=main.py
export FLASK_ENV=production
export PUBLIC_ACCESS=true

# Make sure static files are available
if [ ! -f "static/css/main.css" ]; then
    echo "Creating main CSS file..."
    mkdir -p static/css
    cat > static/css/main.css << 'EOL'
/* Main Stylesheet for NOUS Personal Assistant */

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 0;
    background-color: #f7f9fc;
    color: #333;
}

header {
    background-color: #4a6fa5;
    color: white;
    text-align: center;
    padding: 1rem 0;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.container {
    max-width: 1100px;
    margin: 2rem auto;
    padding: 0 1rem;
}

h1 {
    color: #2c3e50;
    margin-bottom: 1rem;
}

footer {
    text-align: center;
    padding: 1rem 0;
    color: #888;
    font-size: 0.9rem;
    margin-top: 2rem;
}

.btn {
    display: inline-block;
    padding: 0.8rem 1.5rem;
    text-decoration: none;
    border-radius: 5px;
    font-weight: 600;
    transition: all 0.3s ease;
}

.btn-primary {
    background-color: #4a6fa5;
    color: white;
}

.btn-primary:hover {
    background-color: #3a5c8a;
    transform: translateY(-2px);
}
EOL
fi

# Create health check template if it doesn't exist
if [ ! -f "templates/health.html" ]; then
    echo "Creating health check template..."
    mkdir -p templates
    cat > templates/health.html << 'EOL'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NOUS Health Check</title>
    <link rel="stylesheet" href="/static/css/main.css">
    <style>
        .health-container {
            max-width: 600px;
            margin: 2rem auto;
            padding: 2rem;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }
        
        .health-status {
            display: inline-block;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: 600;
            background-color: #4ade80;
            color: #134e29;
        }
        
        .status-list {
            margin: 2rem 0;
            padding: 0;
            list-style: none;
        }
        
        .status-item {
            display: flex;
            justify-content: space-between;
            padding: 0.8rem;
            margin-bottom: 0.5rem;
            background-color: #f8f9fc;
            border-radius: 5px;
        }
        
        .status-label {
            font-weight: 500;
            color: #4b5563;
        }
        
        .status-value {
            font-weight: 600;
            color: #1f2937;
        }
    </style>
</head>
<body>
    <header>
        <h1>NOUS Personal Assistant</h1>
    </header>
    
    <div class="container">
        <div class="health-container">
            <h1>System Health</h1>
            <div class="health-status">Healthy</div>
            
            <ul class="status-list">
                <li class="status-item">
                    <span class="status-label">Version</span>
                    <span class="status-value">{{ version }}</span>
                </li>
                <li class="status-item">
                    <span class="status-label">Environment</span>
                    <span class="status-value">{{ environment }}</span>
                </li>
                <li class="status-item">
                    <span class="status-label">Timestamp</span>
                    <span class="status-value">{{ timestamp }}</span>
                </li>
            </ul>
            
            <a href="/" class="btn btn-primary">Return to Home</a>
        </div>
    </div>
    
    <footer>
        <p>&copy; 2025 NOUS Personal Assistant</p>
    </footer>
</body>
</html>
EOL
fi

# Ensure start script is executable
chmod +x public_start.sh
chmod +x start.sh

echo "Public deployment setup completed successfully!"
echo "Run ./public_start.sh to start the application"