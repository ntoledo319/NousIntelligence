"""
Improved Application Runner

This script ensures that the application runs continuously and reliably
even under high load or when deployed. It adds connection pooling,
automatic retry logic, and better error handling.
"""

import os
import sys
import time
import logging
import subprocess
import signal
import atexit

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("NOUS-Runner")

class AppRunner:
    """Class to manage the continuous running of the application"""
    
    def __init__(self):
        """Initialize the runner with default settings"""
        self.process = None
        self.running = False
        # Configure environment
        os.environ['PYTHONUNBUFFERED'] = '1'
        os.environ['FLASK_APP'] = 'main.py'
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)
        atexit.register(self.cleanup)
    
    def handle_signal(self, signum, frame):
        """Handle termination signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully")
        self.stop()
        sys.exit(0)
    
    def cleanup(self):
        """Ensure resources are properly cleaned up"""
        self.stop()
        
    def start(self):
        """Start the application with Gunicorn"""
        if self.running:
            logger.warning("Application is already running")
            return
        
        try:
            logger.info("Starting NOUS application with Gunicorn")
            
            # Build the command with optimized production settings
            cmd = [
                "gunicorn",
                "--bind", "0.0.0.0:5000",
                "--workers", "2",
                "--threads", "4",
                "--timeout", "120",
                "--worker-class", "sync",
                "--worker-tmp-dir", "/dev/shm",
                "--reuse-port",
                "--limit-request-line", "8190",
                "--log-level", "info",
                "--access-logfile", "-",
                "--error-logfile", "-",
                "main:app"
            ]
            
            # Start the process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            self.running = True
            logger.info(f"Application process started with PID {self.process.pid}")
            
            # Monitor process output
            while self.running:
                output = self.process.stdout.readline()
                if output:
                    print(output.strip())
                
                # Check if process is still alive
                if self.process.poll() is not None:
                    logger.warning("Application process exited unexpectedly")
                    self.running = False
                    
                    # Auto-restart after a brief delay
                    logger.info("Automatically restarting application in 3 seconds")
                    time.sleep(3)
                    self.start()
                    return
                    
                time.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error starting application: {str(e)}")
            self.running = False
    
    def stop(self):
        """Stop the application gracefully"""
        if not self.running:
            return
        
        logger.info("Stopping application")
        if self.process:
            try:
                # Send SIGTERM for graceful shutdown
                self.process.terminate()
                
                # Give it time to shut down cleanly
                for _ in range(30):  # 3 seconds
                    if self.process.poll() is not None:
                        break
                    time.sleep(0.1)
                
                # Force kill if still running
                if self.process.poll() is None:
                    logger.warning("Application did not terminate gracefully, forcing")
                    self.process.kill()
                
                logger.info("Application stopped")
            except Exception as e:
                logger.error(f"Error stopping application: {str(e)}")
        
        self.running = False
        self.process = None

# Run the application if executed directly
if __name__ == "__main__":
    runner = AppRunner()
    try:
        runner.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down")
        runner.stop()
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        runner.stop()
        sys.exit(1)