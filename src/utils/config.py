"""
Configuration management for LooksMapping Scraper.

This module handles loading and managing configuration settings
from environment variables and configuration files.
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


class Config:
    """
    Configuration class for LooksMapping Scraper.
    
    This class manages all configuration settings, loading them from
    environment variables with sensible defaults.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Optional path to configuration file
        """
        # Load environment variables
        if config_file:
            load_dotenv(config_file)
        else:
            load_dotenv()
        
        # Scraping Configuration
        self.scraper_timeout = int(os.getenv("SCRAPER_TIMEOUT", "30"))
        self.scraper_headless = os.getenv("SCRAPER_HEADLESS", "true").lower() == "true"
        self.scraper_max_retries = int(os.getenv("SCRAPER_MAX_RETRIES", "3"))
        self.scraper_delay = float(os.getenv("SCRAPER_DELAY", "1.0"))
        
        # Browser Configuration
        self.browser_width = int(os.getenv("BROWSER_WIDTH", "1280"))
        self.browser_height = int(os.getenv("BROWSER_HEIGHT", "800"))
        self.browser_user_agent = os.getenv(
            "BROWSER_USER_AGENT",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        
        # Data Configuration
        self.data_output_dir = os.getenv("DATA_OUTPUT_DIR", "./data")
        self.data_format = os.getenv("DATA_FORMAT", "json")
        self.data_include_html = os.getenv("DATA_INCLUDE_HTML", "false").lower() == "true"
        
        # Logging Configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_format = os.getenv(
            "LOG_FORMAT",
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.log_file = os.getenv("LOG_FILE", "scraper.log")
        
        # Analysis Configuration
        self.analysis_include_stats = os.getenv("ANALYSIS_INCLUDE_STATS", "true").lower() == "true"
        self.analysis_output_format = os.getenv("ANALYSIS_OUTPUT_FORMAT", "both")
        self.analysis_neighborhood_filter = os.getenv("ANALYSIS_NEIGHBORHOOD_FILTER", "manhattan")
        
        # Development Configuration
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
        self.mock_data = os.getenv("MOCK_DATA", "false").lower() == "true"
        
        # Ensure data directory exists
        os.makedirs(self.data_output_dir, exist_ok=True)
    
    def get_browser_options(self) -> Dict[str, Any]:
        """Get browser configuration options."""
        return {
            "headless": self.scraper_headless,
            "width": self.browser_width,
            "height": self.browser_height,
            "user_agent": self.browser_user_agent,
        }
    
    def get_scraper_options(self) -> Dict[str, Any]:
        """Get scraper configuration options."""
        return {
            "timeout": self.scraper_timeout,
            "max_retries": self.scraper_max_retries,
            "delay": self.scraper_delay,
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return {
            "level": self.log_level,
            "format": self.log_format,
            "file": self.log_file,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "scraper_timeout": self.scraper_timeout,
            "scraper_headless": self.scraper_headless,
            "scraper_max_retries": self.scraper_max_retries,
            "scraper_delay": self.scraper_delay,
            "browser_width": self.browser_width,
            "browser_height": self.browser_height,
            "browser_user_agent": self.browser_user_agent,
            "data_output_dir": self.data_output_dir,
            "data_format": self.data_format,
            "data_include_html": self.data_include_html,
            "log_level": self.log_level,
            "log_format": self.log_format,
            "log_file": self.log_file,
            "analysis_include_stats": self.analysis_include_stats,
            "analysis_output_format": self.analysis_output_format,
            "analysis_neighborhood_filter": self.analysis_neighborhood_filter,
            "debug": self.debug,
            "test_mode": self.test_mode,
            "mock_data": self.mock_data,
        }


def load_config(config_file: Optional[str] = None) -> Config:
    """
    Load configuration from environment variables.
    
    Args:
        config_file: Optional path to configuration file
        
    Returns:
        Config: Loaded configuration instance
    """
    return Config(config_file)
