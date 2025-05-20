# NOUS - Personal Assistant Application

NOUS is a modern web-based personal assistant application built with Flask. It helps you organize your life, track important information, and manage tasks efficiently.

## Features

- **User Authentication**: Secure login with email/password or Google OAuth
- **Task Management**: Create, update, and track tasks with priorities and due dates
- **Settings Management**: Customize your experience with themes and preferences
- **Dashboard**: Get a quick overview of your most important information
- **Responsive Design**: Works well on desktop and mobile devices

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A modern web browser

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/nous.git
   cd nous
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   # For development
   export FLASK_ENV=development
   export SECRET_KEY=your_secret_key
   
   # For Google OAuth (optional)
   export GOOGLE_CLIENT_ID=your_google_client_id
   export GOOGLE_CLIENT_SECRET=your_google_client_secret
   export GOOGLE_REDIRECT_URI=http://localhost:8080/auth/google/callback
   ```

5. Initialize the database:
   ```bash
   flask init-db  # This command is added by the app
   ```

6. Run the application:
   ```bash
   python app.py
   # or
   flask run
   ```

7. Access the application:
   Open your browser and navigate to `http://localhost:8080`

## Development

### Project Structure

- **app.py**: Main application entry point
- **app_factory.py**: Application factory for Flask app creation
- **models.py**: SQLAlchemy database models
- **auth/**: Authentication related files
- **routes/**: Route blueprints for different features
- **templates/**: Jinja2 HTML templates
- **static/**: Static files (CSS, JS, images)
- **utils/**: Utility functions and helpers

### Key Components

- **Flask**: Web framework
- **SQLAlchemy**: ORM for database operations
- **Flask-Login**: User session management
- **Bootstrap 5**: Frontend framework
- **JavaScript**: Client-side interactions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [Bootstrap](https://getbootstrap.com/)
- [Font Awesome](https://fontawesome.com/)
- [Google OAuth](https://developers.google.com/identity/protocols/oauth2)