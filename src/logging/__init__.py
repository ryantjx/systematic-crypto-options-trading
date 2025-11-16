"""
Global logging package for systematic crypto options trading.

This package provides a centralized logging configuration for the entire project,
with support for console and file-based logging, configurable log levels, and
structured log formatting.
"""

from .logger import (
    get_logger,
    setup_logging,
    configure_logger,
    LogLevel,
)

__all__ = [
    "get_logger",
    "setup_logging",
    "configure_logger",
    "LogLevel",
]
