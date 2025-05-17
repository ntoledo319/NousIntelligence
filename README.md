# NOUS Personal Assistant

NOUS is a comprehensive personal assistant application designed to help manage tasks, track health, monitor weather, maintain budgets, and much more. The application integrates with various services like Google, Spotify, and AI providers to deliver a personalized experience.

## Features

- **Task Management**: Integration with Google services for calendar, tasks, and notes
- **Health Tracking**: Monitor appointments, medications, and pain forecasts
- **Weather Integration**: Get weather forecasts and track weather-based health impacts
- **Budget Management**: Track expenses, budgets, and financial planning
- **Travel Planning**: Plan trips, manage itineraries, and track travel documents
- **Shopping Lists**: Create and manage shopping lists and recurring items
- **Voice Interactions**: Process voice commands and provide voice responses
- **AI-Powered Assistance**: Natural language processing for commands and questions

## Architecture

The application follows a modern, modular architecture with clear separation of concerns:

- **Factory Pattern**: Uses an application factory to configure and initialize the app
- **Repository Pattern**: Abstracts database access through repositories
- **Service Layer**: Encapsulates business logic in service components
- **Blueprints**: Organizes routes into logical blueprint modules
- **API Versioning**: Structured API endpoints with versioning

### Directory Structure

```
├── app_factory.py        # Application factory
├── auth/                 # Authentication providers
├── config.py             # Configuration classes
├── main.py               # Main entry point
├── migrations/           # Database migrations
├── models.py             # SQLAlchemy models
├── repositories/         # Repository pattern implementations
├── routes/               # Route blueprints
│   ├── api/              # API endpoints
│   │   └── v1/           # API version 1
│   └── view/             # View/page routes
├── services/             # Business logic services
├── static/               # Static assets
├── templates/            # HTML templates
└── utils/                # Utility functions
```

## Setup and Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Set up environment variables (see `.env.example`)
6. Initialize the database: `flask db upgrade`
7. Run the application: `python main.py`

## API Documentation

The API is organized into versioned endpoints:

- `/api/v1/settings` - User settings management
- `/api/v1/weather` - Weather data and location management

For detailed API documentation, visit `/api/documentation` after starting the server.

## Integrations

NOUS integrates with several third-party services:

- **Google OAuth**: Authentication and access to Google services
- **Spotify API**: Music integration and health-related music recommendations
- **OpenAI/OpenRouter**: AI capabilities for natural language processing
- **Weather APIs**: Local weather information and forecasting

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)