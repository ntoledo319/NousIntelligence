from app import create_app

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    # Development server - use gunicorn for production
    app.run(
        host='0.0.0.0', 
        port=8080, 
        debug=False  # Set via environment for security
    )
