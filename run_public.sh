#!/bin/bash

echo "Starting NOUS Personal Assistant (Public Version)..."

# Create necessary directories
mkdir -p logs flask_session static templates

# Make sure we have a basic template if one doesn't exist
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
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            text-align: center;
            margin-bottom: 30px;
        }
        h1 {
            color: #2c3e50;
        }
        .container {
            background-color: #f9f9f9;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .feature {
            margin-bottom: 20px;
            padding: 15px;
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        footer {
            margin-top: 30px;
            text-align: center;
            font-size: 0.9em;
            color: #7f8c8d;
        }
    </style>
</head>
<body>
    <header>
        <h1>NOUS Personal Assistant</h1>
        <p>Your intelligent companion for daily tasks</p>
    </header>
    
    <div class="container">
        <div class="feature">
            <h2>Welcome!</h2>
            <p>NOUS Personal Assistant is running and ready to help you. This is the public deployment of our advanced AI-powered assistant.</p>
        </div>
        
        <div class="feature">
            <h2>Key Features</h2>
            <ul>
                <li>Intelligent Task Management</li>
                <li>Data Analysis & Visualization</li>
                <li>Information Retrieval & Summarization</li>
                <li>Personalized Recommendations</li>
            </ul>
        </div>
        
        <div class="feature">
            <h2>API Access</h2>
            <p>Developers can access our API at <code>/api/info</code> for integration purposes.</p>
        </div>
    </div>
    
    <footer>
        <p>&copy; 2025 NOUS Personal Assistant | Powered by Advanced AI Technology</p>
    </footer>
</body>
</html>
EOF
fi

# Make sure we have a static folder with CSS
mkdir -p static/css
if [ ! -f "static/css/style.css" ]; then
  cat > static/css/style.css << 'EOF'
/* NOUS Personal Assistant Styles */
body {
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f5f7fa;
}
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}
header {
    background-color: #2c3e50;
    color: white;
    padding: 1rem 0;
    text-align: center;
}
footer {
    margin-top: 2rem;
    padding: 1rem 0;
    text-align: center;
    font-size: 0.9rem;
    color: #7f8c8d;
}
EOF
fi

# Run the public version of the app
python public_nous.py