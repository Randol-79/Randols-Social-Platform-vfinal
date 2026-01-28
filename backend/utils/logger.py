"""
Structured logging for Randol's Agentic Marketing Platform
Provides consistent logging across all agents and services
"""

import logging
import sys
import os
from datetime import datetime
from typing import Optional, Any, Dict
import json

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra_data'):
            log_data['data'] = record.extra_data
            
        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Build message
        message = f"{color}[{timestamp}] [{record.levelname}] [{record.name}]{reset} {record.getMessage()}"
        
        # Add exception if present
        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"
            
        return message


class AgentLogger:
    """Custom logger for agents with additional context"""
    
    def __init__(self, name: str, logger: logging.Logger):
        self.name = name
        self.logger = logger
        self.context: Dict[str, Any] = {}
        
    def set_context(self, **kwargs):
        """Set persistent context for all log messages"""
        self.context.update(kwargs)
        
    def clear_context(self):
        """Clear persistent context"""
        self.context = {}
        
    def _log_with_context(self, level: int, message: str, extra_data: Optional[Dict] = None):
        """Log message with context"""
        data = {**self.context}
        if extra_data:
            data.update(extra_data)
            
        record = self.logger.makeRecord(
            self.name, level, '', 0, message, (), None
        )
        if data:
            record.extra_data = data
        self.logger.handle(record)
        
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log_with_context(logging.DEBUG, message, kwargs if kwargs else None)
        
    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log_with_context(logging.INFO, message, kwargs if kwargs else None)
        
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._log_with_context(logging.WARNING, message, kwargs if kwargs else None)
        
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log error message"""
        if exception:
            kwargs['exception'] = str(exception)
        self._log_with_context(logging.ERROR, message, kwargs if kwargs else None)
        
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self._log_with_context(logging.CRITICAL, message, kwargs if kwargs else None)
        
    def agent_action(self, action: str, details: Optional[Dict] = None):
        """Log agent-specific action"""
        message = f"Agent Action: {action}"
        data = {'action': action}
        if details:
            data['details'] = details
        self._log_with_context(logging.INFO, message, data)
        
    def content_event(self, event_type: str, content_id: str, **kwargs):
        """Log content-related event"""
        message = f"Content Event: {event_type} - {content_id}"
        data = {
            'event_type': event_type,
            'content_id': content_id,
            **kwargs
        }
        self._log_with_context(logging.INFO, message, data)


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_to_file: bool = True,
    json_format: bool = False
) -> AgentLogger:
    """
    Setup and return a configured logger
    
    Args:
        name: Logger name (usually agent or module name)
        level: Logging level
        log_to_file: Whether to log to file
        json_format: Whether to use JSON formatting
        
    Returns:
        Configured AgentLogger instance
    """
    
    # Create base logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers = []
    
    # Determine environment
    is_production = os.environ.get('FLASK_ENV') == 'production'
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    if is_production or json_format:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(ColoredFormatter())
    
    logger.addHandler(console_handler)
    
    # File handler (if enabled)
    if log_to_file:
        log_dir = os.environ.get('LOG_DIR', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Daily rotating log file
        log_file = os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(JSONFormatter())
        
        logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return AgentLogger(name, logger)


def get_logger(name: str) -> AgentLogger:
    """Get or create a logger by name"""
    return setup_logger(name)


# Pre-configured loggers for common use
api_logger = setup_logger('api')
agent_logger = setup_logger('agents')
content_logger = setup_logger('content')
analytics_logger = setup_logger('analytics')


class LogContext:
    """Context manager for temporary logging context"""
    
    def __init__(self, logger: AgentLogger, **kwargs):
        self.logger = logger
        self.context = kwargs
        self.previous_context = {}
        
    def __enter__(self):
        self.previous_context = self.logger.context.copy()
        self.logger.set_context(**self.context)
        return self.logger
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.context = self.previous_context
        return False


# Performance logging decorator
def log_performance(logger: AgentLogger):
    """Decorator to log function performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            logger.debug(f"Starting {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                logger.info(
                    f"Completed {func.__name__}",
                    duration_seconds=duration,
                    status='success'
                )
                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                logger.error(
                    f"Failed {func.__name__}",
                    exception=e,
                    duration_seconds=duration,
                    status='failed'
                )
                raise
                
        return wrapper
    return decorator
