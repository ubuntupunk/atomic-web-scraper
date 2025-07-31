"""
Atomic Scraper Tool - Next-Generation Intelligent Web Scraping

AI-powered scraping tool built on the atomic agents framework that provides
natural language interface and dynamic strategy generation for effortless data extraction.
"""

__version__ = "1.0.0"
__author__ = "Atomic Scraper Tool"

from .agents.scraper_planning_agent import AtomicScraperPlanningAgent
from .tools.atomic_scraper_tool import AtomicScraperTool
from .config.scraper_config import ScraperConfiguration

__all__ = [
    "AtomicScraperPlanningAgent",
    "AtomicScraperTool", 
    "ScraperConfiguration"
]