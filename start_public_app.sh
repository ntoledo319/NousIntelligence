#!/bin/bash

echo "Starting NOUS Personal Assistant (Public Deployment)..."

# Create necessary directories
mkdir -p flask_session logs static templates

# Ensure we have a basic index template
if [ ! -f "templates/index.html" ]; then
  mkdir -p templates
  cat > templates/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NOUS Personal Assistant</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }
        .container {
            width: 80%;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background-color: #2c3e50;
            color: white;
            padding: 2rem 0;
            text-align: center;
            margin-bottom: 30px;
        }
        h1 {
            margin: 0;
            font-size: 2.5rem;
        }
        .tagline {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        .card {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            padding: 25px;
            margin-bottom: 25px;
        }
        h2 {
            color: #2c3e50;
            margin-top: 0;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 10px;
        }
        .feature-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        .feature-item {
            background-color: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 15px;
            border-radius: 4px;
        }
        footer {
            text-align: center;
            margin-top: 50px;
            padding: 20px 0;
            color: #7f8c8d;
            font-size: 0.9rem;
            border-top: 1px solid #eee;
        }
        .api-endpoint {
            font-family: monospace;
            background-color: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>NOUS Personal Assistant</h1>
            <p class="tagline">Your intelligent companion for daily tasks</p>
        </div>
    </header>
    
    <div class="container">
        <div class="card">
            <h2>Welcome to NOUS</h2>
            <p>NOUS is an advanced AI-powered personal assistant web application designed to provide seamless multi-modal interactions and reliable system management. Our platform helps you manage tasks, analyze data, and access information with ease.</p>
        </div>
        
        <div class="card">
            <h2>Key Features</h2>
            <div class="feature-list">
                <div class="feature-item">
                    <h3>Task Management</h3>
                    <p>Organize your tasks efficiently with intelligent prioritization and reminders.</p>
                </div>
                <div class="feature-item">
                    <h3>Data Analysis</h3>
                    <p>Visualize and understand your data with powerful analytical tools.</p>
                </div>
                <div class="feature-item">
                    <h3>Information Processing</h3>
                    <p>Find and summarize information from various sources quickly.</p>
                </div>
                <div class="feature-item">
                    <h3>Reliable Deployment</h3>
                    <p>Built with comprehensive deployment verification and monitoring.</p>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>API Access</h2>
            <p>Developers can access our API through these endpoints:</p>
            <ul>
                <li><span class="api-endpoint">/api/info</span> - Get information about the API</li>
                <li><span class="api-endpoint">/health</span> - Check the system health status</li>
            </ul>
        </div>
    </div>
    
    <footer>
        <div class="container">
            <p>&copy; 2025 NOUS Personal Assistant | Powered by Advanced AI Technology</p>
        </div>
    </footer>
</body>
</html>
EOF
fi

# Create error pages
mkdir -p templates/errors
if [ ! -f "templates/errors/404.html" ]; then
  cat > templates/errors/404.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Not Found - NOUS Personal Assistant</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            text-align: center;
            padding: 50px 20px;
            background-color: #f5f7fa;
        }
        .error-container {
            max-width: 600px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1 {
            color: #e74c3c;
            font-size: 3rem;
            margin-bottom: 10px;
        }
        .error-code {
            font-size: 1.5rem;
            color: #7f8c8d;
            margin-bottom: 20px;
        }
        .back-link {
            display: inline-block;
            margin-top: 20px;
            color: #3498db;
            text-decoration: none;
        }
        .back-link:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="error-container">
        <h1>Page Not Found</h1>
        <div class="error-code">Error 404</div>
        <p>The page you are looking for might have been removed, had its name changed, or is temporarily unavailable.</p>
        <a href="/" class="back-link">← Return to Homepage</a>
    </div>
</body>
</html>
EOF

  cat > templates/errors/500.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Server Error - NOUS Personal Assistant</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            text-align: center;
            padding: 50px 20px;
            background-color: #f5f7fa;
        }
        .error-container {
            max-width: 600px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1 {
            color: #e74c3c;
            font-size: 3rem;
            margin-bottom: 10px;
        }
        .error-code {
            font-size: 1.5rem;
            color: #7f8c8d;
            margin-bottom: 20px;
        }
        .back-link {
            display: inline-block;
            margin-top: 20px;
            color: #3498db;
            text-decoration: none;
        }
        .back-link:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="error-container">
        <h1>Server Error</h1>
        <div class="error-code">Error 500</div>
        <p>Sorry, something went wrong on our end. We're working on fixing the issue.</p>
        <p>Please try again later.</p>
        <a href="/" class="back-link">← Return to Homepage</a>
    </div>
</body>
</html>
EOF
fi

# Set environment variables
export FLASK_APP=public_app.py
export FLASK_ENV=production
export PORT=8080

# Run the public app
python public_app.py