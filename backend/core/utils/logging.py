"""
Elegant logging system for Faker Agent.

This module provides a sophisticated yet clean logging solution that:
1. Ensures all important logs are output exactly once
2. Captures initialization and configuration information
3. Maintains code cleanliness and elegance
4. Prevents duplicate log entries
"""
import logging
import sys
from typing import Optional, Set, Dict, Any
from datetime import datetime

from backend.config.settings import settings

class ElegantLogger:
    """Elegant logger that ensures each important message is logged exactly once."""
    
    def __init__(self):
        self._logged_messages: Set[str] = set()
        self._initialization_messages: Dict[str, str] = {}
        self._startup_sequence: list = []
        self._logging_initialized = False
        
    def configure_logging(self):
        """Configure logging system exactly once with elegant setup."""
        if self._logging_initialized:
            return
            
        # Clear any existing configuration
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Create elegant formatter
        formatter = logging.Formatter(
            fmt=settings.LOG_FORMAT,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler with elegant output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        
        # Configure root logger
        root_logger.setLevel(getattr(logging, settings.LOG_LEVEL, logging.INFO))
        root_logger.addHandler(console_handler)
        
        self._logging_initialized = True
        
        # Log system startup
        self.log_system_startup()
    
    def log_system_startup(self):
        """Log system startup information elegantly."""
        startup_logger = logging.getLogger('system.startup')
        startup_logger.info("=" * 60)
        startup_logger.info("Faker Agent Backend Starting")
        startup_logger.info("=" * 60)
        startup_logger.info(f"Log Level: {settings.LOG_LEVEL}")
        startup_logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        startup_logger.info("-" * 60)
    
    def log_initialization(self, component: str, details: str, **kwargs):
        """
        Log component initialization with details.
        Ensures each component is logged exactly once.
        """
        message_key = f"init_{component}"
        if message_key in self._logged_messages:
            return
            
        logger = logging.getLogger(component)
        
        # Build elegant message
        message_parts = [f"Initialized {component}"]
        if details:
            message_parts.append(details)
        if kwargs:
            details_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
            message_parts.append(details_str)
            
        full_message = " - ".join(message_parts)
        logger.info(full_message)
        
        self._logged_messages.add(message_key)
        self._initialization_messages[component] = full_message
    
    def log_configuration(self, config_type: str, config_data: Dict[str, Any]):
        """Log configuration information elegantly."""
        message_key = f"config_{config_type}"
        if message_key in self._logged_messages:
            return
            
        logger = logging.getLogger(f'config.{config_type}')
        logger.info(f"Configuration: {config_type}")
        
        for key, value in config_data.items():
            # Mask sensitive information
            if any(sensitive in key.lower() for sensitive in ['key', 'secret', 'password', 'token']):
                value = "***" if value else "None"
            logger.info(f"  {key}: {value}")
        
        self._logged_messages.add(message_key)
    
    def log_startup_phase(self, phase: str, message: str):
        """Log startup phase information."""
        message_key = f"startup_{phase}"
        if message_key in self._logged_messages:
            return
            
        startup_logger = logging.getLogger('system.startup')
        startup_logger.info(f"[{phase}] {message}")
        self._logged_messages.add(message_key)
        self._startup_sequence.append((phase, message))
    
    def log_shutdown(self):
        """Log system shutdown information elegantly."""
        shutdown_logger = logging.getLogger('system.shutdown')
        shutdown_logger.info("-" * 60)
        shutdown_logger.info("Faker Agent Backend Shutting Down")
        shutdown_logger.info("-" * 60)
        
        # Log initialization summary
        if self._initialization_messages:
            shutdown_logger.info("Initialization Summary:")
            for component, message in self._initialization_messages.items():
                shutdown_logger.info(f"  ✓ {message}")
        
        # Log startup sequence
        if self._startup_sequence:
            shutdown_logger.info("Startup Sequence:")
            for phase, message in self._startup_sequence:
                shutdown_logger.info(f"  {phase}: {message}")
        
        shutdown_logger.info("=" * 60)

# Global elegant logger instance
_elegant_logger = ElegantLogger()

def setup_logging():
    """Setup elegant logging system."""
    _elegant_logger.configure_logging()

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)

def log_initialization(component: str, details: str = "", **kwargs):
    """Log component initialization elegantly."""
    _elegant_logger.log_initialization(component, details, **kwargs)

def log_configuration(config_type: str, config_data: dict):
    """Log configuration information elegantly."""
    _elegant_logger.log_configuration(config_type, config_data)

def log_startup_phase(phase: str, message: str):
    """Log startup phase information."""
    _elegant_logger.log_startup_phase(phase, message)

def log_shutdown():
    """Log system shutdown elegantly."""
    _elegant_logger.log_shutdown()