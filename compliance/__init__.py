"""
Compliance module for ethical web scraping.

This module provides tools for respecting website policies, rate limiting,
and maintaining compliance with web scraping best practices.
"""

from .robots_parser import RobotsParser
from .rate_limiter import RateLimiter, RateLimitConfig, RespectfulCrawler
from .privacy_compliance import (
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