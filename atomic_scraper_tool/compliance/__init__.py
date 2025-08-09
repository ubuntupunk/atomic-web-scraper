"""
Compliance module for ethical web scraping.

This module provides tools for respecting website policies, rate limiting,
and maintaining compliance with web scraping best practices.
"""

from atomic_scraper_tool.robots_parser import RobotsParser
from atomic_scraper_tool.rate_limiter import RateLimiter, RateLimitConfig, RespectfulCrawler
from atomic_scraper_tool.privacy_compliance import (
    PrivacyComplianceChecker,
    PrivacyComplianceConfig,
    DataCategory,
    RetentionPolicy,
    DataCollectionRule
)

__all__ = [
    'RobotsParser',
    'RateLimiter',
    'RateLimitConfig',
    'RespectfulCrawler',
    'PrivacyComplianceChecker',
    'PrivacyComplianceConfig',
    'DataCategory',
    'RetentionPolicy',
    'DataCollectionRule'
]