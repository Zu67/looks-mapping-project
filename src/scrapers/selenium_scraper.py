"""
Selenium-based scraper for LooksMapping.com

This module provides browser automation for scraping restaurant data
from LooksMapping.com using Selenium WebDriver. It handles dynamic content
and can interact with JavaScript-rendered elements.
"""

import time
import json
import re
from typing import List, Dict, Any, Optional
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from .base import BaseScraper, ScrapingError
from ..utils.helpers import clean_restaurant_data, validate_restaurant_data
from ..utils.config import Config

logger = logging.getLogger(__name__)


class SeleniumScraper(BaseScraper):
    """
    Selenium-based scraper for LooksMapping.com.
    
    This scraper uses Selenium WebDriver to automate a browser and extract
    restaurant data. It can handle dynamic content and JavaScript interactions.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize Selenium scraper.
        
        Args:
            config: Optional configuration instance
        """
        super().__init__(config)
        self.driver: Optional[webdriver.Chrome] = None
        self.base_url = "https://looksmapping.com"
    
    def is_available(self) -> bool:
        """
        Check if Selenium scraper is available.
        
        Returns:
            bool: True if Chrome driver is available
        """
        try:
            # Try to create a temporary driver to test availability
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            service = Service(ChromeDriverManager().install())
            test_driver = webdriver.Chrome(service=service, options=options)
            test_driver.quit()
            return True
        except Exception as e:
            logger.warning(f"Selenium scraper not available: {e}")
            return False
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape restaurant data from LooksMapping.com using Selenium.
        
        Returns:
            List[Dict[str, Any]]: List of restaurant dictionaries
            
        Raises:
            ScrapingError: If scraping fails
        """
        try:
            logger.info("Starting Selenium scraping...")
            
            # Set up WebDriver
            self._setup_webdriver()
            
            # Navigate to website
            self._navigate_to_website()
            
            # Select New York city
            self._select_new_york()
            
            # Wait for content to load
            self._wait_for_content()
            
            # Extract restaurant data
            restaurants = self._extract_restaurant_data()
            
            # Try different viewing modes
            restaurants = self._extract_from_viewing_modes(restaurants)
            
            # Validate and clean data
            validated_restaurants = self.validate_data(restaurants)
            
            logger.info(f"Selenium scraping completed. Found {len(validated_restaurants)} restaurants")
            return validated_restaurants
            
        except Exception as e:
            logger.error(f"Selenium scraping failed: {e}")
            raise ScrapingError(f"Selenium scraping failed: {e}")
        finally:
            self._cleanup()
    
    def _setup_webdriver(self) -> None:
        """Set up Chrome WebDriver with appropriate options."""
        try:
            logger.info("Setting up Chrome WebDriver...")
            
            options = Options()
            
            # Configure browser options
            if self.config and self.config.scraper_headless:
                options.add_argument("--headless")
            
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")
            options.add_argument("--disable-javascript")
            
            # Set window size
            if self.config:
                options.add_argument(f"--window-size={self.config.browser_width},{self.config.browser_height}")
            
            # Set user agent
            if self.config:
                options.add_argument(f"--user-agent={self.config.browser_user_agent}")
            
            # Create WebDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.implicitly_wait(10)
            
            logger.info("Chrome WebDriver setup complete")
            
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {e}")
            raise ScrapingError(f"WebDriver setup failed: {e}")
    
    def _navigate_to_website(self) -> None:
        """Navigate to the LooksMapping website."""
        try:
            logger.info("Navigating to LooksMapping website...")
            self.driver.get(self.base_url)
            
            # Wait for page to load
            time.sleep(5)
            logger.info("Successfully navigated to website")
            
        except WebDriverException as e:
            logger.error(f"Failed to navigate to website: {e}")
            raise ScrapingError(f"Navigation failed: {e}")
    
    def _select_new_york(self) -> None:
        """Select New York city from the city selector."""
        try:
            logger.info("Looking for New York button...")
            
            # Try different selectors for the New York button
            selectors = [
                "//span[contains(text(), 'New York')]",
                "//button[contains(text(), 'New York')]",
                "//a[contains(text(), 'New York')]",
                "//div[contains(text(), 'New York')]"
            ]
            
            for selector in selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed() and element.is_enabled():
                        logger.info("Found New York button, clicking...")
                        element.click()
                        time.sleep(3)  # Wait for city to load
                        return
                except NoSuchElementException:
                    continue
            
            logger.warning("Could not find New York button with any selector")
            
        except Exception as e:
            logger.warning(f"Error selecting New York: {e}")
    
    def _wait_for_content(self) -> None:
        """Wait for restaurant content to load."""
        try:
            logger.info("Waiting for restaurant content...")
            
            # Wait for restaurant elements to appear
            wait = WebDriverWait(self.driver, 20)
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[onclick*='flyToLocation']"))
            )
            
            # Additional wait for dynamic content
            time.sleep(3)
            logger.info("Restaurant content loaded")
            
        except TimeoutException:
            logger.warning("Restaurant content did not load within timeout")
    
    def _extract_restaurant_data(self) -> List[Dict[str, Any]]:
        """
        Extract restaurant data from the current page.
        
        Returns:
            List[Dict[str, Any]]: List of restaurant dictionaries
        """
        restaurants = []
        
        try:
            logger.info("Finding restaurant elements...")
            elements = self.driver.find_elements(By.CSS_SELECTOR, "div[onclick*='flyToLocation']")
            logger.info(f"Found {len(elements)} restaurant elements")
            
            for i, element in enumerate(elements):
                try:
                    restaurant_data = self._extract_element_data(element)
                    if restaurant_data:
                        restaurants.append(restaurant_data)
                except Exception as e:
                    logger.warning(f"Error extracting data from element {i}: {e}")
            
        except Exception as e:
            logger.error(f"Error extracting restaurant data: {e}")
        
        return restaurants
    
    def _extract_element_data(self, element) -> Optional[Dict[str, Any]]:
        """
        Extract restaurant data from a single element.
        
        Args:
            element: WebElement containing restaurant data
            
        Returns:
            Optional[Dict[str, Any]]: Restaurant data or None if extraction fails
        """
        try:
            onclick = element.get_attribute("onclick")
            if not onclick or "flyToLocation" not in onclick:
                return None
            
            # Extract coordinates and JSON data from onclick attribute
            match = re.search(r'flyToLocation\(([^,]+,\s*([^,]+),\s*({.+?})\)', onclick)
            if not match:
                return None
            
            lng = float(match.group(1))
            lat = float(match.group(2))
            json_str = match.group(3)
            
            # Clean up JSON string
            json_str = json_str.replace("&quot;", "\"")
            data = json.loads(json_str)
            
            # Add coordinates
            data["long"] = lng
            data["lat"] = lat
            
            # Try to get name and neighborhood if not in the JSON
            data["name"] = self._extract_name_from_element(element, data)
            data["hood"] = self._extract_neighborhood_from_element(element, data)
            
            return clean_restaurant_data(data)
            
        except (json.JSONDecodeError, ValueError, AttributeError) as e:
            logger.warning(f"Error parsing element data: {e}")
            return None
    
    def _extract_name_from_element(self, element, data: Dict[str, Any]) -> str:
        """Extract restaurant name from element or existing data."""
        if "name" in data and data["name"]:
            return data["name"]
        
        try:
            name_element = element.find_element(By.CSS_SELECTOR, ".result-name")
            return name_element.text
        except NoSuchElementException:
            return "Unknown"
    
    def _extract_neighborhood_from_element(self, element, data: Dict[str, Any]) -> str:
        """Extract neighborhood from element or existing data."""
        if "hood" in data and data["hood"]:
            return data["hood"]
        
        try:
            hood_element = element.find_element(By.CSS_SELECTOR, ".result-hood")
            return hood_element.text
        except NoSuchElementException:
            return "Unknown"
    
    def _extract_from_viewing_modes(self, existing_restaurants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract restaurant data from different viewing modes.
        
        Args:
            existing_restaurants: List of already extracted restaurants
            
        Returns:
            List[Dict[str, Any]]: Updated list of restaurants
        """
        restaurants = existing_restaurants.copy()
        existing_names = {r.get("name") for r in restaurants if "name" in r}
        
        modes = ["hot", "age", "gender"]
        for mode in modes:
            try:
                logger.info(f"Switching to {mode} mode...")
                self._switch_to_mode(mode)
                
                # Get new restaurant elements
                elements = self.driver.find_elements(By.CSS_SELECTOR, "div[onclick*='flyToLocation']")
                logger.info(f"Found {len(elements)} restaurant elements in {mode} mode")
                
                # Extract data from new elements
                for element in elements:
                    try:
                        restaurant_data = self._extract_element_data(element)
                        if restaurant_data and restaurant_data.get("name") not in existing_names:
                            restaurants.append(restaurant_data)
                            existing_names.add(restaurant_data["name"])
                    except Exception as e:
                        logger.warning(f"Error extracting data from element in {mode} mode: {e}")
                        
            except Exception as e:
                logger.error(f"Error switching to {mode} mode: {e}")
        
        logger.info(f"Total unique restaurants found: {len(restaurants)}")
        return restaurants
    
    def _switch_to_mode(self, mode: str) -> None:
        """
        Switch to a specific viewing mode.
        
        Args:
            mode: Mode to switch to ('hot', 'age', 'gender')
        """
        try:
            mode_button = self.driver.find_element(By.CSS_SELECTOR, f".mode-button[data-mode='{mode}']")
            mode_button.click()
            time.sleep(2)  # Wait for the mode to change
        except NoSuchElementException:
            logger.warning(f"Could not find {mode} mode button")
        except Exception as e:
            logger.error(f"Error switching to {mode} mode: {e}")
    
    def _cleanup(self) -> None:
        """Clean up WebDriver resources."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed")
            except Exception as e:
                logger.warning(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None
    
    def save_data(self, restaurants: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """
        Save restaurant data to JSON file.
        
        Args:
            restaurants: List of restaurant dictionaries
            filename: Optional filename (defaults to restaurant_data.json)
            
        Returns:
            str: Path to saved file
        """
        if not filename:
            filename = "restaurant_data.json"
        
        output_path = f"{self.config.data_output_dir}/{filename}" if self.config else filename
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(restaurants, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(restaurants)} restaurants to {output_path}")
        return output_path
