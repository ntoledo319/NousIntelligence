#!/bin/bash

echo "Starting NOUS Personal Assistant (Public-No-Auth Version)..."

# Create directories
mkdir -p templates static

# Create a simple index page
cat > templates/index.html << 'EOF'
<!DOCTYPE html>
<html>
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
            <p>NOUS is an advanced AI-powered personal assistant web application designed to provide seamless multi-modal interactions and reliable system management.</p>
            <p>This is a 100% public deployment that doesn't require login.</p>
        </div>
        
        <div class="card">
            <h2>Key Features</h2>
            <div class="feature-list">
                <div class="feature-item">
                    <h3>Task Management</h3>
                    <p>Organize your tasks efficiently with intelligent prioritization.</p>
                </div>
                <div class="feature-item">
                    <h3>Data Analysis</h3>
                    <p>Visualize and understand your data with powerful tools.</p>
                </div>
                <div class="feature-item">
                    <h3>Information Processing</h3>
                    <p>Find and summarize information from various sources.</p>
                </div>
            </div>
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

# Run the simplified app without authentication
PORT=8080 python nous_public.py