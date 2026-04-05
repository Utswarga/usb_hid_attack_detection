"""
Structured logging module for the USB HID Attack Detection System.
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from core.config import LOG_FILE, LOG_FORMAT, LOG_LEVEL


class StructuredLoggerFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON with additional context."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields if present
        if hasattr(record, "event_data"):
            log_data["event_data"] = record.event_data

        return json.dumps(log_data)


class StructuredLogger:
    """Provides structured logging functionality."""

    def __init__(self, name: str):
        """
        Initialize the structured logger.

        Args:
            name: Logger name (typically module name)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, LOG_LEVEL))

        # File handler with JSON formatting
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(StructuredLoggerFormatter())
        self.logger.addHandler(file_handler)

        # Console handler with standard formatting
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(LOG_FORMAT)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

    def log_event(
        self,
        level: str,
        message: str,
        event_data: Dict[str, Any] = None,
    ) -> None:
        """
        Log a structured event.

        Args:
            level: Log level (INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            event_data: Dictionary of event-specific data
        """
        record = self.logger.makeRecord(
            name=self.logger.name,
            level=getattr(logging, level),
            fn="",
            lno=0,
            msg=message,
            args=(),
            exc_info=None,
        )
        record.event_data = event_data or {}
        self.logger.handle(record)

    def info(self, message: str, event_data: Dict[str, Any] = None) -> None:
        """Log info level message."""
        self.log_event("INFO", message, event_data)

    def warning(self, message: str, event_data: Dict[str, Any] = None) -> None:
        """Log warning level message."""
        self.log_event("WARNING", message, event_data)

    def error(self, message: str, event_data: Dict[str, Any] = None) -> None:
        """Log error level message."""
        self.log_event("ERROR", message, event_data)

    def critical(self, message: str, event_data: Dict[str, Any] = None) -> None:
        """Log critical level message."""
        self.log_event("CRITICAL", message, event_data)


# Module-level logger instance
logger = StructuredLogger(__name__)
