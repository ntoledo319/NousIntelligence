from app import app
import logging
import routes  # Import routes to register authentication routes

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(host="0.0.0.0", port=5000, debug=True)
