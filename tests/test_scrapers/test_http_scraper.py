"""
Tests for HTTP scraper.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from scrapers.http_scraper import HttpScraper
from utils.config import Config


class TestHttpScraper:
    """Test cases for HttpScraper class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config()
        self.scraper = HttpScraper(self.config)
    
    def test_initialization(self):
        """Test scraper initialization."""
        assert self.scraper.config == self.config
        assert self.scraper.base_url == "https://looksmapping.com"
        assert self.scraper.session is not None
    
    def test_is_available(self):
        """Test availability check."""
        assert self.scraper.is_available() is True
    
    @patch('requests.Session.get')
    def test_fetch_website_success(self, mock_get):
        """Test successful website fetching."""
        # Mock response
        mock_response = Mock()
        mock_response.text = "<html><body>Test content</body></html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        response = self.scraper._fetch_website()
        
        assert response is not None
        assert response.text == "<html><body>Test content</body></html>"
        mock_get.assert_called_once()
    
    @patch('requests.Session.get')
    def test_fetch_website_failure(self, mock_get):
        """Test website fetching failure."""
        mock_get.side_effect = Exception("Network error")
        
        response = self.scraper._fetch_website()
        
        assert response is None
    
    def test_extract_from_rankings_object(self):
        """Test extraction from rankings object."""
        html_content = """
        <script>
        const rankings = {
            "ny": {
                "attractive": {
                    "1": [{"name": "Test Restaurant", "hood": "SoHo", "attractive_score": "8.5"}]
                }
            }
        };
        </script>
        """
        soup = BeautifulSoup(html_content, "html.parser")
        
        restaurants = self.scraper._extract_from_rankings_object(soup)
        
        assert len(restaurants) == 1
        assert restaurants[0]["name"] == "Test Restaurant"
        assert restaurants[0]["hood"] == "SoHo"
        assert restaurants[0]["attractive_score"] == "8.5"
    
    def test_extract_with_pattern_matching(self):
        """Test pattern matching extraction."""
        html_content = '''
        <div>{"name":"Test Restaurant","hood":"SoHo","attractive_score":"8.5","age_score":"7.2","gender_score":"6.8"}</div>
        '''
        
        restaurants = self.scraper._extract_with_pattern_matching(html_content)
        
        assert len(restaurants) == 1
        assert restaurants[0]["name"] == "Test Restaurant"
        assert restaurants[0]["hood"] == "SoHo"
        assert restaurants[0]["attractive_score"] == "8.5"
    
    def test_create_test_dataset(self):
        """Test test dataset creation."""
        restaurants = self.scraper._create_test_dataset()
        
        assert len(restaurants) == 3
        assert all("name" in r for r in restaurants)
        assert all("hood" in r for r in restaurants)
    
    @patch('requests.Session.get')
    def test_scrape_success(self, mock_get):
        """Test successful scraping."""
        # Mock response with rankings data
        mock_response = Mock()
        mock_response.text = """
        <script>
        const rankings = {
            "ny": {
                "attractive": {
                    "1": [{"name": "Test Restaurant", "hood": "SoHo", "attractive_score": "8.5"}]
                }
            }
        };
        </script>
        """
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        restaurants = self.scraper.scrape()
        
        assert len(restaurants) == 1
        assert restaurants[0]["name"] == "Test Restaurant"
    
    @patch('requests.Session.get')
    def test_scrape_failure(self, mock_get):
        """Test scraping failure."""
        mock_get.side_effect = Exception("Network error")
        
        with pytest.raises(Exception):
            self.scraper.scrape()
    
    def test_validate_data(self):
        """Test data validation."""
        valid_data = [{"name": "Test Restaurant", "hood": "SoHo"}]
        invalid_data = [{"name": "", "hood": "SoHo"}]  # Empty name
        
        validated_valid = self.scraper.validate_data(valid_data)
        validated_invalid = self.scraper.validate_data(invalid_data)
        
        assert len(validated_valid) == 1
        assert len(validated_invalid) == 0
    
    def test_save_data(self):
        """Test data saving."""
        restaurants = [{"name": "Test Restaurant", "hood": "SoHo"}]
        
        with patch('builtins.open', Mock()) as mock_open:
            output_path = self.scraper.save_data(restaurants, "test.json")
            
            assert output_path == "test.json"
            mock_open.assert_called_once()
