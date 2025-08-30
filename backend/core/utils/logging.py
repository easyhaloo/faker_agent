"""
Centralized logging module for the Faker Agent.

This module provides a configurable logging system with:
- Standardized log format
- Multiple handlers (console, file)
- Rotation options for log files
- Log level configuration
- Color-coded console output (optional)
"""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Dict, List, Optional, Union

from backend.config.settings import settings


class ColoredFormatter(logging.Formatter):
    """Logging formatter with colored output for console."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[41m',  # Red background
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        """Format log records with colors."""
        # Save the original format
        log_fmt = self._style._fmt
        
        # Add color codes based on the log level
        if record.levelname in self.COLORS:
            self._style._fmt = f"{self.COLORS[record.levelname]}{log_fmt}{self.COLORS['RESET']}"
            
        # Format the record
        result = logging.Formatter.format(self, record)
        
        # Restore the original format
        self._style._fmt = log_fmt
        
        return result


def get_logger(
    name: Optional[str] = None,
    level: Optional[Union[str, int]] = None,
    use_colors: bool = True,
    log_to_file: bool = True,
    log_to_console: bool = True,
    log_dir: Optional[str] = None,
    file_name: str = "application.log",  # Default to a single application log file
    rotation_type: str = "size",
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5,
    format_string: Optional[str] = None,
) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name, typically __name__. If None, a default root logger will be used
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_colors: Whether to use colored output for console handler
        log_to_file: Whether to log to a file
        log_to_console: Whether to log to console
        log_dir: Directory for log files
        file_name: Log file name (default: application.log - single log file for all modules)
        rotation_type: 'size' or 'time' based rotation
        max_bytes: Maximum size in bytes before rotating (for size rotation)
        backup_count: Number of backup files to keep
        format_string: Custom log format string
        
    Returns:
        Configured logger instance
    """
    # Get log level from settings if not specified
    if level is None:
        level = getattr(logging, settings.LOG_LEVEL, logging.INFO)
    elif isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
        
    # Get format string from settings if not specified
    if format_string is None:
        format_string = settings.LOG_FORMAT
        
    # Create logger
    if name is None:
        # Use the root logger if no name is provided
        logger = logging.getLogger()
    else:
        logger = logging.getLogger(name)
        
    logger.setLevel(level)
    
    # Avoid adding handlers if they already exist - except when a custom file is requested
    # This allows having multiple loggers with different file destinations
    if logger.handlers and file_name == "application.log":
        return logger
        
    # Remove existing handlers if we're configuring a logger with a custom file
    if logger.handlers and file_name != "application.log":
        for handler in logger.handlers[:]:
            if isinstance(handler, (RotatingFileHandler, TimedRotatingFileHandler)):
                logger.removeHandler(handler)
        
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        if use_colors:
            console_formatter = ColoredFormatter(format_string)
        else:
            console_formatter = logging.Formatter(format_string)
            
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
    # File handler
    if log_to_file:
        # Create log directory if it doesn't exist
        if log_dir is None:
            log_dir = os.path.join(Path.cwd(), "logs")
            
        os.makedirs(log_dir, exist_ok=True)
        
        # Use the specified file_name (defaults to application.log)
        log_file_path = os.path.join(log_dir, file_name)
        
        # Create file handler based on rotation type
        if rotation_type.lower() == "time":
            file_handler = TimedRotatingFileHandler(
                log_file_path,
                when="midnight",
                interval=1,
                backupCount=backup_count,
                encoding="utf-8"
            )
        else:  # Default to size-based rotation
            file_handler = RotatingFileHandler(
                log_file_path,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8"
            )
            
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(format_string)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
    return logger


def configure_root_logger(
    level: Optional[Union[str, int]] = None,
    use_colors: bool = True,
    log_to_file: bool = True,
    log_to_console: bool = True,
    log_dir: Optional[str] = None,
    file_name: str = "application.log",  # Default to a single application log file
    rotation_type: str = "size",
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5,
    format_string: Optional[str] = None,
) -> None:
    """
    Configure the root logger for the entire application.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_colors: Whether to use colored output for console handler
        log_to_file: Whether to log to a file
        log_to_console: Whether to log to console
        log_dir: Directory for log files
        file_name: Log file name (default: application.log - single log file for all modules)
        rotation_type: 'size' or 'time' based rotation
        max_bytes: Maximum size in bytes before rotating (for size rotation)
        backup_count: Number of backup files to keep
        format_string: Custom log format string
    """
    # Reset root logger handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    # Configure with the same function
    get_logger(
        None,  # Use None to get the root logger
        level=level,
        use_colors=use_colors,
        log_to_file=log_to_file,
        log_to_console=log_to_console,
        log_dir=log_dir,
        file_name=file_name,
        rotation_type=rotation_type,
        max_bytes=max_bytes,
        backup_count=backup_count,
        format_string=format_string
    )
    
    # Set this as the root logger
    logging.basicConfig(handlers=root_logger.handlers, level=level)