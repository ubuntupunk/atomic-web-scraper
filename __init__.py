"""
Website Scraper Tool - A conversational AI agent for intelligent web scraping.

Built on the atomic agents framework, this tool provides a chat interface for users
to specify scraping criteria and automatically determines the best scraping strategy.
"""

__version__ = "0.1.0"
__author__ = "Website Scraper Tool"

from .agents.scraper_planning_agent import ScraperPlanningAgent
from .tools.website_scraper_tool import WebsiteScraperTool
from .config.scraper_config import ScraperConfiguration

__all__ = [
    "ScraperPlanningAgent",
    "WebsiteScraperTool", 
    "ScraperConfiguration"
]