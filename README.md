# NOUS Personal Assistant

An advanced AI-powered personal assistant web application with robust multi-modal interaction capabilities and intelligent system management.

## Project Structure

The application has been consolidated into a cleaner, more maintainable structure:

- **main.py**: Primary entry point that creates and runs the Flask application
- **app_factory.py**: Application factory for creating and configuring the Flask app
- **config.py**: Configuration classes for different environments (development, testing, production)
- **routes/**: Directory containing route blueprints organized by feature
- **models/**: Directory containing database models organized by domain
- **templates/**: Jinja2 HTML templates with a base template structure
- **static/**: Static files including CSS, JavaScript, and images
- **utils/**: Utility functions and helper modules

## Running the Application

To start the application:

```bash
# Run with the unified start script
./start.sh

# OR run with Python directly
python main.py
```

## Development

### Local Setup

1. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Key Features

- Advanced AI assistance with task management
- Health monitoring and data analysis
- Secure authentication and user profiles
- Multi-modal interaction capabilities

## Configuration

The application uses environment variables for configuration:
- `FLASK_ENV`: Set to "development", "testing", or "production" (default)
- `SECRET_KEY` or `SESSION_SECRET`: Secret key for session security
- `DATABASE_URL`: Database connection URL

## Database

The application uses SQLAlchemy with PostgreSQL. To initialize or update the database schema:

```bash
python run_migrations.py
```