"""
Data models module for the website scraper tool.

Contains Pydantic models for data validation and serialization.
"""

from .base_models import ScrapedItem, ScrapingResult, ScrapingStrategy
from .schema_models import SchemaRecipe, FieldDefinition
from .extraction_models import ExtractedContent, ExtractionRule

__all__ = [
    "ScrapedItem",
    "ScrapingResult", 
    "ScrapingStrategy",
    "SchemaRecipe",
    "FieldDefinition",
    "ExtractedContent",
    "ExtractionRule"
]