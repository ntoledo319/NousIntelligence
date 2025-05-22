// Simple HTTP server to help redirect to our Flask app
const http = require('http');
const fs = require('fs');

// Create HTML content with auto-redirect
const html = `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0;url=http://localhost:5000">
    <title>NOUS Personal Assistant</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            text-align: center;
            padding: 50px;
            background-color: #f8f9fa;
        }
        h1 {
            color: #4a6fa5;
        }
        .loading {
            margin: 30px auto;
            width: 50px;
            height: 50px;
            border: 5px solid rgba(74, 111, 165, 0.3);
            border-radius: 50%;
            border-top-color: #4a6fa5;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <h1>NOUS Personal Assistant</h1>
    <div class="loading"></div>
    <p>Redirecting to your application...</p>
    <p>If you are not redirected automatically, <a href="http://localhost:5000">click here</a>.</p>
</body>
</html>
`;

// Create a server
const server = http.createServer((req, res) => {
    res.writeHead(200, {'Content-Type': 'text/html'});
    res.end(html);
});

// Start listening on port 8080
server.listen(8080, () => {
    console.log('Redirection server running on port 8080');
    
    // Start the Flask app on port 5000
    const { exec } = require('child_process');
    exec('python main.py', (error, stdout, stderr) => {
        if (error) {
            console.error(`Error starting Flask app: ${error.message}`);
            return;
        }
        if (stderr) {
            console.error(`Flask stderr: ${stderr}`);
            return;
        }
        console.log(`Flask stdout: ${stdout}`);
    });
});