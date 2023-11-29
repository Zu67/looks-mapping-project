"""
Tests for Selenium scraper.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from scrapers.selenium_scraper import SeleniumScraper
from utils.config import Config


class TestSeleniumScraper:
    """Test cases for SeleniumScraper class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config()
        self.scraper = SeleniumScraper(self.config)
    
    def test_initialization(self):
        """Test scraper initialization."""
        assert self.scraper.config == self.config
        assert self.scraper.base_url == "https://looksmapping.com"
        assert self.scraper.driver is None
    
    @patch('webdriver_manager.chrome.ChromeDriverManager')
    @patch('selenium.webdriver.Chrome')
    def test_is_available_success(self, mock_chrome, mock_manager):
        """Test availability check when Chrome driver is available."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_manager.return_value.install.return_value = "/path/to/chromedriver"
        
        assert self.scraper.is_available() is True
    
    @patch('webdriver_manager.chrome.ChromeDriverManager')
    def test_is_available_failure(self, mock_manager):
        """Test availability check when Chrome driver is not available."""
        mock_manager.side_effect = Exception("Driver not found")
        
        assert self.scraper.is_available() is False
    
    @patch('selenium.webdriver.Chrome')
    @patch('webdriver_manager.chrome.ChromeDriverManager')
    def test_setup_webdriver(self, mock_manager, mock_chrome):
        """Test WebDriver setup."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_manager.return_value.install.return_value = "/path/to/chromedriver"
        
        self.scraper._setup_webdriver()
        
        assert self.scraper.driver == mock_driver
        mock_chrome.assert_called_once()
    
    @patch('selenium.webdriver.Chrome')
    @patch('webdriver_manager.chrome.ChromeDriverManager')
    def test_navigate_to_website(self, mock_manager, mock_chrome):
        """Test website navigation."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_manager.return_value.install.return_value = "/path/to/chromedriver"
        
        self.scraper.driver = mock_driver
        self.scraper._navigate_to_website()
        
        mock_driver.get.assert_called_once_with("https://looksmapping.com")
    
    @patch('selenium.webdriver.Chrome')
    @patch('webdriver_manager.chrome.ChromeDriverManager')
    def test_select_new_york_success(self, mock_manager, mock_chrome):
        """Test successful New York selection."""
        mock_driver = Mock()
        mock_element = Mock()
        mock_element.is_displayed.return_value = True
        mock_element.is_enabled.return_value = True
        mock_driver.find_element.return_value = mock_element
        mock_chrome.return_value = mock_driver
        mock_manager.return_value.install.return_value = "/path/to/chromedriver"
        
        self.scraper.driver = mock_driver
        self.scraper._select_new_york()
        
        mock_element.click.assert_called_once()
    
    @patch('selenium.webdriver.Chrome')
    @patch('webdriver_manager.chrome.ChromeDriverManager')
    def test_extract_element_data(self, mock_manager, mock_chrome):
        """Test element data extraction."""
        mock_driver = Mock()
        mock_element = Mock()
        mock_element.get_attribute.return_value = 'flyToLocation(-73.9851, 40.7589, {"name":"Test Restaurant","hood":"SoHo"})'
        mock_chrome.return_value = mock_driver
        mock_manager.return_value.install.return_value = "/path/to/chromedriver"
        
        self.scraper.driver = mock_driver
        restaurant_data = self.scraper._extract_element_data(mock_element)
        
        assert restaurant_data is not None
        assert restaurant_data["name"] == "Test Restaurant"
        assert restaurant_data["hood"] == "SoHo"
        assert restaurant_data["long"] == -73.9851
        assert restaurant_data["lat"] == 40.7589
    
    @patch('selenium.webdriver.Chrome')
    @patch('webdriver_manager.chrome.ChromeDriverManager')
    def test_extract_element_data_invalid(self, mock_manager, mock_chrome):
        """Test element data extraction with invalid data."""
        mock_driver = Mock()
        mock_element = Mock()
        mock_element.get_attribute.return_value = 'invalid_onclick'
        mock_chrome.return_value = mock_driver
        mock_manager.return_value.install.return_value = "/path/to/chromedriver"
        
        self.scraper.driver = mock_driver
        restaurant_data = self.scraper._extract_element_data(mock_element)
        
        assert restaurant_data is None
    
    @patch('selenium.webdriver.Chrome')
    @patch('webdriver_manager.chrome.ChromeDriverManager')
    def test_cleanup(self, mock_manager, mock_chrome):
        """Test cleanup functionality."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_manager.return_value.install.return_value = "/path/to/chromedriver"
        
        self.scraper.driver = mock_driver
        self.scraper._cleanup()
        
        mock_driver.quit.assert_called_once()
        assert self.scraper.driver is None
