"""
Core module for the atomic scraper tool.

Contains base interfaces, abstract classes, and core functionality.
"""

# Import only exceptions and error handler for now to avoid circular dependencies
from .exceptions import (
    ScrapingError, NetworkError, ParsingError, ValidationError,
    ConfigurationError, RateLimitError, QualityError
)
from .error_handler import ErrorHandler, ErrorContext, RetryConfig, RetryStrategy, ErrorSeverity

__all__ = [
    "ScrapingError",
    "NetworkError",
    "ParsingError",
    "ValidationError",
    "ConfigurationError",
    "RateLimitError",
    "QualityError",
    "ErrorHandler",
    "ErrorContext",
    "RetryConfig",
    "RetryStrategy",
    "ErrorSeverity"
]