"""
Base data models for the website scraper tool.

Contains core Pydantic models for scraping operations and results.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class ScrapingStrategy(BaseModel):
    """Strategy configuration for scraping operations."""
    
    scrape_type: str = Field(..., description="Type of scraping: 'list', 'detail', 'search', 'sitemap'")
    target_selectors: List[str] = Field(..., description="CSS selectors for target content")
    pagination_strategy: Optional[str] = Field(None, description="Pagination handling strategy")
    content_filters: List[str] = Field(default_factory=list, description="Content filtering rules")
    extraction_rules: Dict[str, str] = Field(default_factory=dict, description="Field extraction rules")
    max_pages: int = Field(10, ge=1, description="Maximum pages to scrape")
    request_delay: float = Field(1.0, ge=0.1, description="Delay between requests")


class ScrapedItem(BaseModel):
    """Individual scraped item with quality tracking."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique item identifier")
    source_url: str = Field(..., description="URL where item was scraped from")
    scraped_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when scraped")
    data: Dict[str, Any] = Field(..., description="Extracted data fields")
    quality_score: float = Field(..., ge=0.0, le=100.0, description="Quality score (0-100)")
    extraction_issues: List[str] = Field(default_factory=list, description="Issues encountered during extraction")
    schema_version: str = Field("1.0", description="Schema version used for extraction")


class ScrapingResult(BaseModel):
    """Complete result of a scraping operation."""
    
    items: List[ScrapedItem] = Field(..., description="List of scraped items")
    total_items_found: int = Field(..., ge=0, description="Total items found on pages")
    total_items_scraped: int = Field(..., ge=0, description="Total items successfully scraped")
    average_quality_score: float = Field(..., ge=0.0, le=100.0, description="Average quality score")
    scraping_summary: str = Field(..., description="Human-readable summary of results")
    strategy_used: ScrapingStrategy = Field(..., description="Strategy used for scraping")
    errors: List[str] = Field(default_factory=list, description="Errors encountered during scraping")
    execution_time: float = Field(..., ge=0.0, description="Total execution time in seconds")
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_items_found == 0:
            return 0.0
        return (self.total_items_scraped / self.total_items_found) * 100.0