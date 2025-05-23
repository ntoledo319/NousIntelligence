#!/usr/bin/env python
"""
NOUS Personal Assistant - Launch and Monitor Script

This script launches the NOUS Personal Assistant and monitors it for errors.
It provides detailed error reporting and ensures the application is running properly.
"""

import os
import sys
import time
import subprocess
import logging
import signal
import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('launch_monitor.log')
    ]
)

logger = logging.getLogger('nous_monitor')

class NOUSMonitor:
    """Monitor for NOUS Personal Assistant"""
    
    def __init__(self):
        """Initialize the monitor"""
        self.process = None
        self.logs_file = 'nous_app.log'
        self.error_logs_file = 'nous_error.log'
        self.restart_count = 0
        self.max_restarts = 3
        
    def setup_environment(self):
        """Setup environment variables for the application"""
        os.environ['PORT'] = '5000'
        os.environ['FLASK_ENV'] = 'development'
        os.environ['PUBLIC_ACCESS'] = 'true'
        os.environ['PYTHONUNBUFFERED'] = '1'
        os.environ['NOUS_MONITOR'] = 'true'
        
        # Create required directories
        os.makedirs('logs', exist_ok=True)
        os.makedirs('static', exist_ok=True)
        os.makedirs('static/css', exist_ok=True)
        os.makedirs('static/js', exist_ok=True)
        os.makedirs('templates', exist_ok=True)
        
        logger.info("Environment setup complete")
        
    def launch_app(self):
        """Launch the NOUS Personal Assistant"""
        logger.info("Launching NOUS Personal Assistant...")
        
        # Kill any existing Python processes
        try:
            subprocess.run(['pkill', 'python'], stderr=subprocess.PIPE)
            time.sleep(1)  # Give processes time to terminate
        except Exception as e:
            logger.warning(f"Failed to kill existing processes: {str(e)}")
        
        # Launch the application
        try:
            with open(self.logs_file, 'w') as log_file, open(self.error_logs_file, 'w') as error_log:
                self.process = subprocess.Popen(
                    ['python', 'main.py'],
                    stdout=log_file,
                    stderr=error_log,
                    env=os.environ,
                    start_new_session=True
                )
            
            logger.info(f"NOUS Personal Assistant launched with PID: {self.process.pid}")
            return True
        except Exception as e:
            logger.error(f"Failed to launch application: {str(e)}")
            return False
    
    def monitor_logs(self):
        """Monitor application logs for errors"""
        if not os.path.exists(self.error_logs_file):
            logger.warning(f"Error log file not found: {self.error_logs_file}")
            return False
        
        try:
            with open(self.error_logs_file, 'r') as error_log:
                error_content = error_log.read()
                
            if 'Error' in error_content or 'Exception' in error_content:
                logger.error("Errors detected in application logs:")
                
                for line in error_content.splitlines():
                    if 'Error' in line or 'Exception' in line:
                        logger.error(f"LOG ERROR: {line}")
                        
                return True  # Errors found
                
            return False  # No errors found
        except Exception as e:
            logger.error(f"Failed to monitor logs: {str(e)}")
            return False
    
    def check_app_status(self):
        """Check if the application is still running"""
        if self.process is None:
            logger.warning("Process not initialized")
            return False
            
        if self.process.poll() is not None:
            # Process has terminated
            return_code = self.process.returncode
            logger.error(f"Application terminated with return code: {return_code}")
            
            # Extract log tail
            if os.path.exists(self.logs_file):
                try:
                    with open(self.logs_file, 'r') as log_file:
                        log_tail = log_file.readlines()[-20:]  # Last 20 lines
                        logger.error("Last application log entries:")
                        for line in log_tail:
                            logger.error(f"LOG: {line.strip()}")
                except Exception as e:
                    logger.error(f"Failed to read log tail: {str(e)}")
            
            return False
        
        # Process is still running
        return True
    
    def check_port(self):
        """Check if the application port is accessible"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', 5000))
            sock.close()
            
            if result == 0:
                logger.info("Port 5000 is open and accessible")
                return True
            else:
                logger.warning(f"Port 5000 is not accessible (result: {result})")
                return False
        except Exception as e:
            logger.error(f"Failed to check port: {str(e)}")
            return False
    
    def request_index(self):
        """Make a request to the application index page"""
        try:
            import urllib.request
            response = urllib.request.urlopen('http://localhost:5000/')
            
            status_code = response.getcode()
            content = response.read().decode('utf-8')
            
            logger.info(f"Index page status code: {status_code}")
            
            if status_code == 200:
                if 'NOUS Personal Assistant' in content:
                    logger.info("Index page loaded successfully")
                    return True
                else:
                    logger.warning("Index page loaded but content is unexpected")
                    return False
            else:
                logger.warning(f"Index page returned non-200 status code: {status_code}")
                return False
        except Exception as e:
            logger.error(f"Failed to request index page: {str(e)}")
            return False
    
    def restart_app(self):
        """Restart the application if it has crashed"""
        if self.restart_count >= self.max_restarts:
            logger.error(f"Maximum restart limit ({self.max_restarts}) reached. Giving up.")
            return False
            
        logger.info("Restarting application...")
        self.restart_count += 1
        
        # Kill the current process if it's still running
        if self.process and self.process.poll() is None:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                time.sleep(2)  # Give process time to terminate
            except Exception as e:
                logger.warning(f"Failed to kill process: {str(e)}")
        
        # Launch the application again
        return self.launch_app()
    
    def run_monitor(self):
        """Run the monitoring loop"""
        logger.info("Starting NOUS Personal Assistant monitor")
        
        # Setup environment and launch application
        self.setup_environment()
        if not self.launch_app():
            logger.error("Failed to launch application. Exiting.")
            return False
        
        # Give the application time to start up
        time.sleep(5)
        
        # Check initial status
        if not self.check_app_status():
            logger.error("Application failed to start properly")
            self.monitor_logs()
            
            if self.restart_app():
                logger.info("Application restarted after initial failure")
                time.sleep(5)  # Give it time to start up again
            else:
                logger.error("Failed to restart application after initial failure")
                return False
        
        # Main monitoring loop
        monitoring_start = datetime.datetime.now()
        check_count = 0
        
        logger.info("Beginning monitoring loop...")
        
        try:
            while True:
                check_count += 1
                logger.info(f"Health check #{check_count} at {datetime.datetime.now().strftime('%H:%M:%S')}")
                
                # Run health checks
                app_running = self.check_app_status()
                port_accessible = self.check_port()
                has_errors = self.monitor_logs()
                
                # Try to access the index page
                if port_accessible:
                    index_accessible = self.request_index()
                else:
                    index_accessible = False
                
                # Log the health check results
                logger.info(f"Health check results: running={app_running}, port={port_accessible}, "
                           f"index={index_accessible}, errors={has_errors}")
                
                # Take action if needed
                if not app_running or not port_accessible or not index_accessible:
                    logger.warning("Application is not healthy, attempting restart")
                    if self.restart_app():
                        logger.info("Application restarted successfully")
                        time.sleep(5)  # Give it time to start up again
                    else:
                        logger.error("Failed to restart application")
                        return False
                
                # Sleep between checks
                time.sleep(20)
                
                # Break after a certain duration for safety
                monitoring_duration = (datetime.datetime.now() - monitoring_start).total_seconds()
                if monitoring_duration > 600:  # 10 minutes
                    logger.info(f"Monitoring completed after {monitoring_duration:.1f} seconds")
                    break
        
        except KeyboardInterrupt:
            logger.info("Monitoring interrupted by user")
        except Exception as e:
            logger.error(f"Monitoring error: {str(e)}")
        
        finally:
            # Clean up
            if self.process and self.process.poll() is None:
                try:
                    logger.info("Terminating application process")
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                except Exception as e:
                    logger.warning(f"Failed to terminate process: {str(e)}")
        
        logger.info("Monitoring complete")
        return True

if __name__ == "__main__":
    monitor = NOUSMonitor()
    monitor.run_monitor()