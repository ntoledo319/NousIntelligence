"""
Production Logging Configuration
Implements structured logging with JSON formatting for production deployment
"""

import os
import sys
import logging
from pythonjsonlogger import jsonlogger


class ProductionFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter for production logs.

    Adds context-specific fields and ensures consistent log structure.
    """

    def add_fields(self, log_record, record, message_dict):
        """Add custom fields to log records"""
        super().add_fields(log_record, record, message_dict)

        # Add standard fields
        log_record['timestamp'] = record.created
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno

        # Add environment context
        log_record['environment'] = os.environ.get('FLASK_ENV', 'production')
        log_record['app'] = 'nous-intelligence'

        # Add request context if available
        try:
            from flask import g, request, has_request_context

            if has_request_context():
                log_record['request_id'] = getattr(g, 'request_id', None)
                log_record['path'] = request.path
                log_record['method'] = request.method
                log_record['remote_addr'] = request.remote_addr
        except (ImportError, RuntimeError):
            pass


def init_production_logging(app=None, log_level=None):
    """
    Initialize production-ready structured logging.

    Args:
        app: Flask application instance (optional)
        log_level: Logging level (defaults to INFO)

    Returns:
        logging.Logger: Configured root logger
    """
    # Determine log level
    if log_level is None:
        log_level_str = os.environ.get('LOG_LEVEL', 'INFO').upper()
        log_level = getattr(logging, log_level_str, logging.INFO)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create console handler with JSON formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # JSON formatter for structured logging
    formatter = ProductionFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s',
        rename_fields={
            'timestamp': '@timestamp',
            'level': '@level',
            'logger': '@logger',
        }
    )
    console_handler.setFormatter(formatter)

    # Add handler to root logger
    root_logger.addHandler(console_handler)

    # Set levels for third-party loggers to reduce noise
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

    # Log initialization
    logger = logging.getLogger(__name__)
    logger.info(
        "Production logging initialized",
        extra={
            'log_level': logging.getLevelName(log_level),
            'handlers': [h.__class__.__name__ for h in root_logger.handlers]
        }
    )

    return root_logger


def get_logger(name):
    """
    Get a logger instance with production configuration.

    Args:
        name: Logger name (typically __name__)

    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)


def log_error(logger, error, context=None):
    """
    Log an error with structured context.

    Args:
        logger: Logger instance
        error: Exception or error message
        context: Additional context dictionary
    """
    error_data = {
        'error_type': type(error).__name__ if isinstance(error, Exception) else 'Error',
        'error_message': str(error),
    }

    if context:
        error_data.update(context)

    if isinstance(error, Exception):
        logger.error(
            f"Error occurred: {error}",
            exc_info=True,
            extra=error_data
        )
    else:
        logger.error(
            str(error),
            extra=error_data
        )


def log_request(logger, request, response=None, duration=None):
    """
    Log HTTP request/response with structured data.

    Args:
        logger: Logger instance
        request: Flask request object
        response: Flask response object (optional)
        duration: Request duration in seconds (optional)
    """
    request_data = {
        'method': request.method,
        'path': request.path,
        'remote_addr': request.remote_addr,
        'user_agent': request.user_agent.string if request.user_agent else None,
    }

    if response:
        request_data['status_code'] = response.status_code
        request_data['content_length'] = response.content_length

    if duration is not None:
        request_data['duration'] = duration

    logger.info(
        f"{request.method} {request.path} - {response.status_code if response else 'pending'}",
        extra=request_data
    )


def log_metric(logger, metric_name, value, tags=None):
    """
    Log a metric for monitoring and analytics.

    Args:
        logger: Logger instance
        metric_name: Name of the metric
        value: Metric value
        tags: Dictionary of tags for categorization
    """
    metric_data = {
        'metric_name': metric_name,
        'metric_value': value,
        'metric_type': type(value).__name__,
    }

    if tags:
        metric_data['tags'] = tags

    logger.info(
        f"Metric: {metric_name}={value}",
        extra=metric_data
    )
