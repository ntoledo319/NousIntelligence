from app import app
import logging
import routes  # Import routes to register authentication routes
from utils.key_config import validate_keys

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Validate API keys on startup
validate_keys()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
