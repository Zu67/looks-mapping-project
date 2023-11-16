"""
Scrapers module for LooksMapping Scraper.

This module contains all scraping implementations for extracting restaurant data
from LooksMapping.com using different approaches.
"""

from .base import BaseScraper
from .http_scraper import HttpScraper
from .selenium_scraper import SeleniumScraper
from .playwright_scraper import PlaywrightScraper

__all__ = [
    "BaseScraper",
    "HttpScraper",
    "SeleniumScraper", 
    "PlaywrightScraper",
]
