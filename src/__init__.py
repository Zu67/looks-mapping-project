"""
LooksMapping Scraper

A comprehensive web scraping toolkit for extracting restaurant data from LooksMapping.com,
focusing on Manhattan restaurants with demographic and attractiveness metrics.
"""

__version__ = "0.1.0"
__author__ = "LooksMapping Scraper Team"
__email__ = "team@looksmapping.dev"

from .scrapers import HttpScraper, SeleniumScraper, PlaywrightScraper
from .analyzers import NeighborhoodAnalyzer
from .models import Restaurant

__all__ = [
    "HttpScraper",
    "SeleniumScraper", 
    "PlaywrightScraper",
    "NeighborhoodAnalyzer",
    "Restaurant",
]
