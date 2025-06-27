# NOUS Developer Guide

This guide provides instructions for setting up the NOUS development environment, understanding the architecture, and contributing to the project.

## Table of Contents
1. [Environment Setup](#environment-setup)
2. [Project Structure](#project-structure)
3. [Key Components & Feature Modules](#key-components-feature-modules)
4. [Running the Application](#running-the-application)
5. [Testing](#testing)
6. [Code Style Guide](#code-style-guide)
7. [Development Workflow](#development-workflow)

## Environment Setup

### Prerequisites
- A Replit account
- Access to the NOUS project on Replit

### Setting Up the Development Environment
The project is configured to run directly on Replit, which handles the environment and dependencies automatically.

1. **Open the project in Replit.**
2. **Set up environment variables (Secrets):**
   - In the Replit sidebar, go to the "Secrets" tool.
   - Add the necessary secrets as defined in `ENV_VARS.md`. Key variables include:
     - `DATABASE_URL`: The Replit Postgres connection string.
     - `SESSION_SECRET`: A long, random string for session security.
     - `GOOGLE_CLIENT_ID` & `GOOGLE_CLIENT_SECRET`: For Google OAuth.
     - `HUGGINGFACE_API_TOKEN`: For AI-powered features.
     - `OPENROUTER_API_KEY`: For the primary AI chat model.
     - `GEMINI_API_KEY`: For direct access to the Gemini API.
     - `OPENWEATHER_API_KEY`: For weather data.
     - `MAPS_API_KEY`: For Google Maps services.

The database is managed by Replit, and schema is created automatically on application startup.

## Project Structure
```
nous/
├── app.py                 # Main Flask application and app factory
├── main.py                # Application entry point
├── routes/                # Route blueprints for each feature
│   ├── api.py
│   ├── maps_routes.py
│   ├── image_routes.py
│   └── ...
├── utils/                 # Business logic and helper modules
│   ├── ai_service_manager.py
│   ├── gemini_helper.py
│   ├── huggingface_helper.py
│   └── ...
├── models/                # SQLAlchemy database models
├── templates/             # HTML templates
├── static/                # Static assets (CSS, JS, images)
├── tests/                 # Unit and integration tests
├── docs/                  # Project documentation
└── replit.toml            # Replit configuration file
```

## Key Components & Feature Modules

### Core Architecture
- **`app.py`**: Contains the `create_app` factory, which initializes the Flask app, loads configuration, and registers all blueprints.
- **`routes/`**: Contains all route blueprints, organized by feature including new analytics, search, notification, financial, and collaboration routes.
- **`models/`**: Database models organized into feature-specific files with 20+ models for comprehensive data management.
- **`utils/`**: Business logic services including new analytics, search, and notification services.
- **`utils/ai_service_manager.py`**: A key module that intelligently routes requests to different AI services (OpenAI, Gemini, OpenRouter, Hugging Face) for cost and performance optimization.

### New Feature Architecture (v2.0)

#### Analytics System
- **Models**: `models/analytics_models.py` - UserActivity, UserMetrics, UserInsight, UserGoal
- **Routes**: `routes/analytics_routes.py` - Dashboard, activity tracking, goal management, insights generation
- **Service**: `utils/analytics_service.py` - Data processing, pattern recognition, AI insight generation
- **Frontend**: Real-time dashboard with charts, goal tracking, and personalized recommendations

#### Global Search System
- **Routes**: `routes/search_routes.py` - Global search, suggestions, content indexing
- **Service**: `utils/search_service.py` - Real-time search, content ranking, suggestion engine
- **Frontend**: Instant search with `Ctrl+K` shortcut, real-time suggestions, category filtering

#### Notification System
- **Models**: Enhanced NotificationQueue in core models
- **Routes**: `routes/notification_routes.py` - Notification management, priority handling
- **Service**: `utils/notification_service.py` - Smart prioritization, multi-channel delivery
- **Frontend**: Notification center with priority indicators and action buttons

#### Financial Management
- **Models**: `models/financial_models.py` - BankAccount, Transaction, Budget, ExpenseCategory, FinancialGoal
- **Routes**: `routes/financial_routes.py` - Account management, transaction tracking, budget monitoring
- **Frontend**: Comprehensive financial dashboard with budget tracking and spending insights

#### Collaboration Features
- **Models**: `models/collaboration_models.py` - Family, FamilyMember, SharedTask, ActivityLog
- **Routes**: `routes/collaboration_routes.py` - Family management, shared task coordination
- **Frontend**: Family dashboard with member management and shared task tracking

#### Enhanced Health Tracking
- **Models**: `models/enhanced_health_models.py` - HealthMetric, HealthGoal, WellnessInsight, MoodEntry
- **Integration**: Enhanced health tracking with goal setting and AI-powered insights
- **Frontend**: Comprehensive wellness dashboard with progress tracking

### Progressive Web App Enhancements
- **Service Worker**: Offline functionality and intelligent caching
- **Mobile Optimization**: Touch-friendly interface with gesture support
- **Keyboard Shortcuts**: Comprehensive shortcut system for power users
- **Accessibility**: Full ARIA compliance and keyboard navigation
- **Real-time Updates**: Live data updates with polling mechanisms

### Voice Emotion Analysis
- **Description**: This feature analyzes an audio file to determine the emotion of the speaker.
- **How it works**:
  1. The user uploads an audio file via the `voice_routes.py` endpoint or uses the voice interface.
  2. The route calls `utils.emotion_detection.analyze_voice_audio`.
  3. This function uses `utils/huggingface_helper.py` to perform speech-to-text and `utils.emotion_detection.py` to perform direct audio-based emotion analysis, then combines the results.
- **Key Files**:
  - `routes/voice_routes.py`
  - `utils/emotion_detection.py`
  - `utils/huggingface_helper.py`
  - `templates/voice_interface.html`

### Mindfulness Voice Assistant
- **Description**: Provides users with pre-defined or AI-generated guided mindfulness exercises.
- **How it works**:
  1. The user interacts with the `voice_mindfulness_routes.py` endpoints.
  2. The routes call functions in `utils/voice_mindfulness.py` to fetch or generate exercises.
  3. The `text_to_speech` function from `utils/voice_interaction.py` is used to generate the audio.
  4. The `templates/voice_mindfulness/exercise.html` template plays the audio.
- **Key Files**:
  - `routes/voice_mindfulness_routes.py`
  - `utils/voice_mindfulness.py`
  - `utils/voice_interaction.py`
  - `templates/voice_mindfulness/exercise.html`

### Image Analysis & Gallery
- **Description**: Allows users to upload images for various types of analysis and view them in an organized gallery.
- **How it works**:
  1. The user uploads an image via `routes/image_routes.py`.
  2. The route calls functions in `utils/image_helper.py` to perform the analysis.
  3. The `image_helper.py` uses `utils/huggingface_helper.py` to interact with various Hugging Face models.
  4. The gallery route dynamically organizes images using the classification data.
- **Key Files**:
  - `routes/image_routes.py`
  - `utils/image_helper.py`
  - `utils/huggingface_helper.py`
  - `templates/image_gallery.html`
  - `templates/image_upload.html`
  - `templates/image_results.html`

### Maps & Navigation
- **Description**: Provides an interactive map with directions and search functionality.
- **How it works**:
  1. The `routes/maps_routes.py` provides the endpoints for the maps page.
  2. The frontend in `templates/maps.html` makes API calls to these endpoints.
  3. The routes call functions in `utils/maps_helper.py` to interact with the Google Maps API.
- **Key Files**:
  - `routes/maps_routes.py`
  - `utils/maps_helper.py`
  - `templates/maps.html`

### Weather Dashboard
- **Description**: Displays detailed weather information.
- **How it works**:
  1. The `routes/weather_routes.py` provides the endpoints for the weather dashboard.
  2. The route calls functions in `utils/weather_helper.py` to get data from the OpenWeatherMap API.
- **Key Files**:
  - `routes/weather_routes.py`
  - `utils/weather_helper.py`
  - `templates/weather.html`

### Task Management
- **Description**: Allows users to manage a to-do list and sync with Google Tasks.
- **How it works**:
  1. `routes/tasks_routes.py` provides endpoints for the tasks dashboard.
  2. The routes interact with the `Task` model in the database.
  3. The `/sync` route uses `utils/google_tasks_helper.py` to communicate with the Google Tasks API.
- **Key Files**:
  - `routes/tasks_routes.py`
  - `utils/google_tasks_helper.py`
  - `models/Task.py` (or equivalent)
  - `templates/tasks.html`

### Recovery Insights
- **Description**: A dashboard for tracking and visualizing recovery progress.
- **How it works**:
  1. `routes/recovery_routes.py` provides the endpoint for the insights dashboard.
  2. The route calls `utils/aa_helper.py` to get recovery statistics.
  3. It uses `utils/ai_helper.py` to generate personalized insights.
- **Key Files**:
  - `routes/recovery_routes.py`
  - `utils/aa_helper.py`
  - `templates/recovery_insights.html`

## Running the Application

Click the "Run" button at the top of the Replit interface. Replit will install dependencies and start the Flask development server.

## Testing

The project uses `pytest`. Tests are located in the `tests/` directory.

To run all tests, open the "Shell" tab in Replit and run:
```bash
pytest
```

## Code Style Guide

The project follows PEP 8 style guidelines with the following tools:

- **Black**: Code formatting
- **Flake8**: Linting
- **isort**: Import sorting

### Documentation Standards

- All modules should have a module-level docstring
- All public functions should have docstrings with parameter descriptions
- Use type hints for function parameters and return values

## Development Workflow

1.  **Create a feature branch**: `git checkout -b feature/your-feature-name`
2.  **Make changes and test**: Run `pytest` to ensure changes don't break existing functionality.
3.  **Commit changes**: Use descriptive commit messages.
4.  **Push changes and create a pull request**.

## Getting Help

If you encounter issues not covered here, please check existing GitHub issues or discuss with the team. 