"""
Core module for the website scraper tool.

Contains base interfaces, abstract classes, and core functionality.
"""

from .interfaces import BaseExtractor, BaseAnalyzer, BaseGenerator
from .exceptions import ScrapingError, NetworkError, ParsingError, ValidationError

__all__ = [
    "BaseExtractor",
    "BaseAnalyzer", 
    "BaseGenerator",
    "ScrapingError",
    "NetworkError",
    "ParsingError",
    "ValidationError"
]