"""
NOUS Personal Assistant - Main Entry Point for Deployment

This file serves as the main entry point for the application
when using the deploy button. It imports and runs the deployment script.
"""
import os
import sys

if __name__ == "__main__":
    # Run the deployment script
    from deployment import setup_deployment, run_application
    
    # Setup deployment environment
    if setup_deployment():
        # Run the application
        run_application()
    else:
        print("Failed to set up deployment environment")
        sys.exit(1)