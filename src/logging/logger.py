"""
Centralized logging configuration for the systematic crypto options trading framework.

This module provides utilities for setting up and managing loggers across the entire
project. It supports both console and file-based logging with configurable formats,
log levels, and handlers.

Example usage:
    >>> from src.logging import get_logger, setup_logging
    >>> 
    >>> # Setup global logging configuration
    >>> setup_logging(level="INFO", log_file="data/logs/app.log")
    >>> 
    >>> # Get a logger for your module
    >>> logger = get_logger(__name__)
    >>> logger.info("Starting data collection")
    >>> logger.debug("Debug information")
    >>> logger.error("An error occurred", exc_info=True)
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Union
from enum import Enum


class LogLevel(str, Enum):
    """Enumeration of available log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        """Format log record with color if outputting to console."""
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']
        
        # Add color to level name
        record.levelname = f"{log_color}{record.levelname}{reset_color}"
        
        return super().format(record)


def setup_logging(
    level: Union[str, LogLevel] = LogLevel.INFO,
    log_file: Optional[Union[str, Path]] = None,
    log_dir: Optional[Union[str, Path]] = None,
    console: bool = True,
    colored: bool = True,
    format_string: Optional[str] = None,
    date_format: Optional[str] = None,
) -> None:
    """
    Configure global logging settings for the application.
    
    This function sets up the root logger with console and/or file handlers,
    configures formatting, and sets the logging level. It should typically be
    called once at the start of the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file. If provided, file logging will be enabled
        log_dir: Directory for log files. If provided with log_file, creates
                the directory if it doesn't exist
        console: Whether to enable console logging (default: True)
        colored: Whether to use colored output for console (default: True)
        format_string: Custom format string for log messages
        date_format: Custom date format string
    
    Example:
        >>> setup_logging(
        ...     level="DEBUG",
        ...     log_file="data/logs/trading.log",
        ...     console=True,
        ...     colored=True
        ... )
    """
    # Convert string to LogLevel if needed
    if isinstance(level, str):
        level = LogLevel(level.upper())
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.value))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Default format strings
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    if date_format is None:
        date_format = "%Y-%m-%d %H:%M:%S"
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.value))
        
        if colored and sys.stdout.isatty():
            console_formatter = ColoredFormatter(format_string, datefmt=date_format)
        else:
            console_formatter = logging.Formatter(format_string, datefmt=date_format)
        
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # File handler
    if log_file is not None:
        log_path = Path(log_file)
        
        # Create log directory if specified or use log_file's parent
        if log_dir is not None:
            log_path = Path(log_dir) / log_path.name
        
        # Create parent directory if it doesn't exist
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
        file_handler.setLevel(getattr(logging, level.value))
        
        # File logs should not be colored
        file_formatter = logging.Formatter(format_string, datefmt=date_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        root_logger.info(f"Logging to file: {log_path}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the specified module.
    
    This function returns a logger with the given name, which will inherit
    the configuration from the root logger set up by setup_logging().
    
    Args:
        name: Name of the logger, typically __name__ from the calling module
    
    Returns:
        Logger instance
    
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing data...")
    """
    return logging.getLogger(name)


def configure_logger(
    name: str,
    level: Optional[Union[str, LogLevel]] = None,
    handlers: Optional[list] = None,
) -> logging.Logger:
    """
    Configure a specific logger with custom settings.
    
    This allows for fine-grained control over individual loggers, separate from
    the global configuration. Useful when you need different logging behavior
    for specific modules.
    
    Args:
        name: Name of the logger
        level: Logging level for this specific logger
        handlers: List of custom handlers to attach to this logger
    
    Returns:
        Configured logger instance
    
    Example:
        >>> # Create a logger with custom file handler
        >>> file_handler = logging.FileHandler('data/logs/strategy.log')
        >>> strategy_logger = configure_logger(
        ...     'strategy.volatility_arb',
        ...     level='DEBUG',
        ...     handlers=[file_handler]
        ... )
    """
    logger = logging.getLogger(name)
    
    if level is not None:
        if isinstance(level, str):
            level = LogLevel(level.upper())
        logger.setLevel(getattr(logging, level.value))
    
    if handlers is not None:
        # Clear existing handlers for this logger
        logger.handlers.clear()
        for handler in handlers:
            logger.addHandler(handler)
    
    return logger


# Set up a default configuration if logging hasn't been configured yet
if not logging.getLogger().handlers:
    setup_logging(level=LogLevel.INFO, console=True, colored=True)
