
#!/bin/bash

echo "$(date +'[%Y-%m-%d %H:%M:%S]') Running NOUS health check"

# Create logs directory if it doesn't exist
mkdir -p logs
LOGFILE="logs/health_check.log"

# Check if the application is running
if curl -s http://localhost:${PORT:-8080}/health >/dev/null; then
    echo "$(date +'[%Y-%m-%d %H:%M:%S]') Health check passed" | tee -a $LOGFILE
    exit 0
else
    echo "$(date +'[%Y-%m-%d %H:%M:%S]') Health check failed - attempting restart" | tee -a $LOGFILE
    
    # Restart the application
    bash public_start.sh &
    
    # Wait a moment and check again
    sleep 5
    if curl -s http://localhost:${PORT:-8080}/health >/dev/null; then
        echo "$(date +'[%Y-%m-%d %H:%M:%S]') Application successfully restarted" | tee -a $LOGFILE
        exit 0
    else
        echo "$(date +'[%Y-%m-%d %H:%M:%S]') Failed to restart application" | tee -a $LOGFILE
        exit 1
    fi
fi
