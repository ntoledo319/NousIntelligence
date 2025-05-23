
#!/bin/bash
# NOUS Health Monitoring Script

# Setup logging
mkdir -p logs
LOG_FILE="logs/health_check_$(date +%Y%m%d).log"

log_message() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_message "Running health check"

# Check if application is running
PORT=${PORT:-8080}
if ! curl -s http://localhost:$PORT/health > /dev/null; then
  log_message "Health check failed, attempting restart"
  
  # Kill any existing processes on the port
  fuser -k $PORT/tcp 2>/dev/null || true
  
  # Start the application
  log_message "Restarting application"
  ./public_start.sh &
  
  # Wait and verify
  sleep 5
  if curl -s http://localhost:$PORT/health > /dev/null; then
    log_message "Application successfully restarted"
  else
    log_message "Failed to restart application"
  fi
else
  log_message "Health check passed"
fi

# Check system resources
DISK_SPACE=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_SPACE" -gt 85 ]; then
  log_message "Disk space alert: ${DISK_SPACE}% used"
  
  # Clean up old logs
  find logs -name "*.log" -type f -mtime +7 -delete
fi
