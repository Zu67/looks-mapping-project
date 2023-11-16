"""
Base scraper class for LooksMapping Scraper.

This module provides the abstract base class that all scrapers must implement,
ensuring consistent interface and behavior across different scraping methods.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Abstract base class for all scrapers.
    
    This class defines the common interface that all scrapers must implement,
    ensuring consistency across different scraping methods.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the scraper with optional configuration.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape restaurant data from LooksMapping.com.
        
        Returns:
            List[Dict[str, Any]]: List of restaurant dictionaries with extracted data
            
        Raises:
            ScrapingError: If scraping fails
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the scraper is available and properly configured.
        
        Returns:
            bool: True if scraper is available, False otherwise
        """
        pass
    
    def validate_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate and clean scraped data.
        
        Args:
            data: Raw scraped data
            
        Returns:
            List[Dict[str, Any]]: Validated and cleaned data
        """
        if not data:
            self.logger.warning("No data found during scraping")
            return []
        
        validated_data = []
        for item in data:
            if self._is_valid_restaurant(item):
                validated_data.append(self._clean_restaurant_data(item))
            else:
                self.logger.warning(f"Invalid restaurant data: {item}")
        
        self.logger.info(f"Validated {len(validated_data)} restaurants from {len(data)} raw items")
        return validated_data
    
    def _is_valid_restaurant(self, data: Dict[str, Any]) -> bool:
        """
        Check if restaurant data is valid.
        
        Args:
            data: Restaurant data dictionary
            
        Returns:
            bool: True if data is valid, False otherwise
        """
        required_fields = ["name"]
        return all(field in data and data[field] for field in required_fields)
    
    def _clean_restaurant_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and normalize restaurant data.
        
        Args:
            data: Raw restaurant data
            
        Returns:
            Dict[str, Any]: Cleaned restaurant data
        """
        cleaned = {}
        
        # Clean string fields
        string_fields = ["name", "hood", "cuisine", "score", "reviewers"]
        for field in string_fields:
            if field in data:
                cleaned[field] = str(data[field]).strip()
        
        # Clean numeric fields
        numeric_fields = ["attractive_score", "age_score", "gender_score", "lat", "long"]
        for field in numeric_fields:
            if field in data:
                try:
                    cleaned[field] = float(data[field])
                except (ValueError, TypeError):
                    cleaned[field] = 0.0
        
        return cleaned


class ScrapingError(Exception):
    """Exception raised when scraping fails."""
    pass
