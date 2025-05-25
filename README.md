# NOUS Personal Assistant

NOUS is an advanced AI-powered personal assistant web application that leverages cutting-edge technologies to provide intelligent, adaptive, and user-friendly interactions.

## Features

- **Public Access**: Accessible to everyone without requiring Replit login
- **Secure Authentication**: Maintains Google authentication for protected routes
- **Modern UI**: Beautiful responsive design across all pages
- **Intelligent Task Management**: Smart organization and prioritization of tasks
- **Health Monitoring**: Track and analyze health metrics
- **Weather Forecasting**: Get accurate weather predictions with smart recommendations

## Deployment Instructions

### Using the Deploy Button

The easiest way to deploy NOUS is using the Replit deploy button:

1. Click the **Deploy** button in your Replit interface
2. Wait for the deployment process to complete
3. Your application will be available at your deployment URL (shown after deployment)

The deploy button automatically:
- Sets up the required environment
- Starts the application server
- Makes it publicly accessible without requiring Replit login
- Maintains Google authentication for protected routes

### Manual Deployment

If you prefer to deploy manually, follow these steps:

1. Ensure all dependencies are installed
2. Run `python main.py` or `python deployment.py`
3. The application will be available at port 8080

## Accessing the Application

After deployment, your NOUS Personal Assistant will be accessible at:
- Your deployment URL (when using the deploy button)
- `http://localhost:8080` (when running locally)

No Replit login is required to access the application, but protected routes still use Google authentication.

## Login Information

For demo purposes, you can use:
- Email: demo@example.com
- Password: demo123

## Application Structure

- `app_public_final.py`: Main application with public access configuration
- `run_nous.py`: Application runner
- `deployment.py`: Deployment helper script
- `main.py`: Entry point for deployment
- `templates/`: HTML templates for all pages
- `static/`: Static assets (CSS, JS, images)

## Getting Help

If you encounter any issues with deployment or using the application, please check:
- The application logs for error messages
- That all required directories exist
- That the port (8080) is available

## License

© 2025 NOUS Personal Assistant. All rights reserved.