"""
Playwright-based scraper for LooksMapping.com

This module provides advanced browser automation for scraping restaurant data
from LooksMapping.com using Playwright. It handles complex interactions,
map navigation, and popup management.
"""

import asyncio
import json
import re
from typing import List, Dict, Any, Optional
import logging
from collections import defaultdict

from playwright.async_api import async_playwright, Browser, Page, BrowserContext

from .base import BaseScraper, ScrapingError
from ..utils.helpers import clean_restaurant_data, validate_restaurant_data, deduplicate_restaurants
from ..utils.config import Config

logger = logging.getLogger(__name__)


class PlaywrightScraper(BaseScraper):
    """
    Playwright-based scraper for LooksMapping.com.
    
    This scraper uses Playwright for advanced browser automation, including
    map interactions, popup handling, and comprehensive data extraction.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize Playwright scraper.
        
        Args:
            config: Optional configuration instance
        """
        super().__init__(config)
        self.base_url = "https://looksmapping.com"
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    def is_available(self) -> bool:
        """
        Check if Playwright scraper is available.
        
        Returns:
            bool: True if Playwright is installed and browsers are available
        """
        try:
            # Try to import playwright and check if browsers are installed
            import playwright
            return True
        except ImportError:
            logger.warning("Playwright is not installed")
            return False
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape restaurant data from LooksMapping.com using Playwright.
        
        Returns:
            List[Dict[str, Any]]: List of restaurant dictionaries
            
        Raises:
            ScrapingError: If scraping fails
        """
        try:
            logger.info("Starting Playwright scraping...")
            
            # Run async scraping
            restaurants = asyncio.run(self._async_scrape())
            
            # Validate and clean data
            validated_restaurants = self.validate_data(restaurants)
            
            logger.info(f"Playwright scraping completed. Found {len(validated_restaurants)} restaurants")
            return validated_restaurants
            
        except Exception as e:
            logger.error(f"Playwright scraping failed: {e}")
            raise ScrapingError(f"Playwright scraping failed: {e}")
    
    async def _async_scrape(self) -> List[Dict[str, Any]]:
        """
        Async scraping implementation.
        
        Returns:
            List[Dict[str, Any]]: List of restaurant dictionaries
        """
        async with async_playwright() as p:
            try:
                # Set up browser
                await self._setup_browser(p)
                
                # Navigate to website
                await self._navigate_to_website()
                
                # Select New York city
                await self._select_new_york()
                
                # Wait for map to load
                await self._wait_for_map_loading()
                
                # Initialize restaurant collection
                all_restaurants = []
                restaurant_names = set()
                
                # Process different viewing modes
                modes = ["hot", "age", "gender"]
                for mode in modes:
                    logger.info(f"Processing {mode.upper()} mode...")
                    mode_restaurants = await self._process_viewing_mode(mode, restaurant_names)
                    all_restaurants.extend(mode_restaurants)
                    restaurant_names.update(r["name"] for r in mode_restaurants)
                
                # Remove duplicates
                unique_restaurants = deduplicate_restaurants(all_restaurants)
                
                return unique_restaurants
                
            except Exception as e:
                logger.error(f"Async scraping failed: {e}")
                raise
            finally:
                await self._cleanup()
    
    async def _setup_browser(self, playwright) -> None:
        """
        Set up Playwright browser with appropriate options.
        
        Args:
            playwright: Playwright instance
        """
        try:
            logger.info("Launching browser...")
            
            # Configure browser options
            browser_options = {
                "headless": self.config.scraper_headless if self.config else True,
                "args": ['--no-sandbox', '--disable-dev-shm-usage']
            }
            
            self.browser = await playwright.chromium.launch(**browser_options)
            
            # Create context with viewport settings
            context_options = {
                "viewport": {
                    "width": self.config.browser_width if self.config else 1280,
                    "height": self.config.browser_height if self.config else 800
                },
                "user_agent": self.config.browser_user_agent if self.config else None
            }
            
            self.context = await self.browser.new_context(**context_options)
            self.page = await self.context.new_page()
            
            logger.info("Browser setup complete")
            
        except Exception as e:
            logger.error(f"Failed to setup browser: {e}")
            raise ScrapingError(f"Browser setup failed: {e}")
    
    async def _navigate_to_website(self) -> None:
        """Navigate to the LooksMapping website."""
        try:
            logger.info("Navigating to LooksMapping website...")
            await self.page.goto(self.base_url, wait_until="networkidle")
            await self.page.wait_for_timeout(5000)  # Additional wait for dynamic content
            logger.info("Page loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to navigate to website: {e}")
            raise ScrapingError(f"Navigation failed: {e}")
    
    async def _select_new_york(self) -> None:
        """Attempt to select New York city from the city selector."""
        try:
            logger.info("Looking for New York button...")
            
            # Try different selectors for the New York button
            selectors = [
                "text=New York",
                "span:has-text('New York')",
                ".city-selector span:has-text('New York')",
                "//span[contains(text(), 'New York')]"
            ]
            
            for selector in selectors:
                try:
                    logger.info(f"Trying selector: {selector}")
                    ny_button = await self.page.query_selector(selector)
                    if ny_button:
                        logger.info("Found New York button!")
                        await ny_button.click()
                        await self.page.wait_for_timeout(3000)  # Wait for city to load
                        return
                except Exception as e:
                    logger.warning(f"Selector {selector} failed: {e}")
                    continue
            
            logger.warning("Could not find New York button with any selector")
            
        except Exception as e:
            logger.warning(f"Error selecting New York: {e}")
    
    async def _wait_for_map_loading(self) -> None:
        """Wait for the map to fully load and be interactive."""
        try:
            logger.info("Waiting for map to load...")
            await self.page.wait_for_selector(".mapboxgl-canvas", timeout=30000)
            logger.info("Map loaded successfully")
        except Exception as e:
            logger.error(f"Map failed to load: {e}")
            raise ScrapingError(f"Map loading failed: {e}")
    
    async def _process_viewing_mode(self, mode: str, existing_names: set) -> List[Dict[str, Any]]:
        """
        Process a specific viewing mode and extract restaurant data.
        
        Args:
            mode: Viewing mode ('hot', 'age', 'gender')
            existing_names: Set of already collected restaurant names
            
        Returns:
            List[Dict[str, Any]]: New restaurants found in this mode
        """
        try:
            # Switch to the specified mode
            await self._switch_to_mode(mode)
            
            # Extract data from visible markers
            restaurants = await self._extract_visible_restaurants(existing_names)
            
            # Pan around the map to find more restaurants
            await self._pan_map_for_restaurants(restaurants, existing_names)
            
            # Try different zoom levels
            await self._zoom_for_restaurants(restaurants, existing_names)
            
            logger.info(f"Found {len(restaurants)} new restaurants in {mode} mode")
            return restaurants
            
        except Exception as e:
            logger.error(f"Error processing {mode} mode: {e}")
            return []
    
    async def _switch_to_mode(self, mode: str) -> None:
        """
        Switch to a specific viewing mode.
        
        Args:
            mode: Mode to switch to ('hot', 'age', 'gender')
        """
        try:
            mode_button = await self.page.query_selector(f".mode-button[data-mode='{mode}']")
            if mode_button:
                await mode_button.click()
                await self.page.wait_for_timeout(3000)  # Wait for mode to change
                logger.info(f"Switched to {mode} mode")
            else:
                logger.warning(f"Could not find {mode} mode button")
        except Exception as e:
            logger.error(f"Error switching to {mode} mode: {e}")
    
    async def _extract_visible_restaurants(self, existing_names: set) -> List[Dict[str, Any]]:
        """
        Extract data from currently visible restaurant markers.
        
        Args:
            existing_names: Set of already collected restaurant names
            
        Returns:
            List[Dict[str, Any]]: New restaurants found
        """
        restaurants = []
        markers = await self.page.query_selector_all(".mapboxgl-marker")
        logger.info(f"Found {len(markers)} visible markers")
        
        for i, marker in enumerate(markers):
            try:
                logger.info(f"Processing marker {i+1}/{len(markers)}")
                
                # Scroll to marker and click
                await marker.scroll_into_view_if_needed()
                await self.page.wait_for_timeout(300)
                await marker.click()
                await self.page.wait_for_timeout(1000)  # Wait for popup
                
                # Extract data from popup
                restaurant = await self._extract_popup_data()
                
                if restaurant and restaurant["name"] not in existing_names:
                    restaurants.append(restaurant)
                    existing_names.add(restaurant["name"])
                    logger.info(f"Added new restaurant: {restaurant['name']}")
                
                # Close popup
                await self._close_popup()
                
            except Exception as e:
                logger.warning(f"Error processing marker {i+1}: {e}")
                continue
        
        return restaurants
    
    async def _extract_popup_data(self) -> Optional[Dict[str, Any]]:
        """
        Extract restaurant data from a popup.
        
        Returns:
            Optional[Dict[str, Any]]: Restaurant data or None if extraction fails
        """
        try:
            popup = await self.page.query_selector(".mapboxgl-popup")
            if not popup:
                return None
            
            # Extract basic information
            name_element = await popup.query_selector("strong")
            cuisine_element = await popup.query_selector(".popup-info")
            score_element = await popup.query_selector(".popup-score")
            reviewers_element = await popup.query_selector("div[style*='text-align: center']")
            
            # Extract metric indicators
            metric_indicators = await popup.query_selector_all(".metric-indicator")
            
            # Get text content
            name = await name_element.text_content() if name_element else "Unknown"
            cuisine = await cuisine_element.text_content() if cuisine_element else "Unknown"
            score_text = await score_element.text_content() if score_element else "0/10"
            reviewers_text = await reviewers_element.text_content() if reviewers_element else "0 reviewers"
            
            # Extract numeric score
            score_match = re.search(r'(\d+(\.\d+)?)/10', score_text)
            score = score_match.group(1) if score_match else "0"
            
            # Extract metric scores from indicators
            attractive_score, age_score, gender_score = await self._extract_metric_scores(metric_indicators)
            
            # Extract neighborhood
            hood = await self._extract_neighborhood(name)
            
            restaurant_data = {
                "name": name,
                "cuisine": cuisine,
                "hood": hood,
                "score": score,
                "attractive_score": attractive_score,
                "age_score": age_score,
                "gender_score": gender_score,
                "reviewers": reviewers_text
            }
            
            return clean_restaurant_data(restaurant_data)
            
        except Exception as e:
            logger.error(f"Error extracting popup data: {e}")
            return None
    
    async def _extract_metric_scores(self, metric_indicators) -> tuple[str, str, str]:
        """
        Extract metric scores from indicator elements.
        
        Args:
            metric_indicators: List of metric indicator elements
            
        Returns:
            tuple: (attractive_score, age_score, gender_score)
        """
        attractive_score = "0"
        age_score = "0"
        gender_score = "0"
        
        if len(metric_indicators) >= 3:
            for i, indicator in enumerate(metric_indicators[:3]):
                try:
                    style = await indicator.get_attribute("style")
                    percent_match = re.search(r'left:\s*(\d+)%', style)
                    if percent_match:
                        percent = int(percent_match.group(1))
                        metric_score = str(round(percent / 10, 1))
                        
                        if i == 0:
                            attractive_score = metric_score
                        elif i == 1:
                            age_score = metric_score
                        elif i == 2:
                            gender_score = metric_score
                except Exception as e:
                    logger.warning(f"Error extracting metric {i}: {e}")
        
        return attractive_score, age_score, gender_score
    
    async def _extract_neighborhood(self, restaurant_name: str) -> str:
        """
        Extract neighborhood information for a restaurant.
        
        Args:
            restaurant_name: Name of the restaurant
            
        Returns:
            str: Neighborhood name or "Unknown"
        """
        try:
            hood_element = await self.page.query_selector(f".result-item:has-text('{restaurant_name}') .result-hood")
            if hood_element:
                return await hood_element.text_content()
        except Exception as e:
            logger.warning(f"Error extracting neighborhood for {restaurant_name}: {e}")
        
        return "Unknown"
    
    async def _close_popup(self) -> None:
        """Close any open popup."""
        try:
            close_button = await self.page.query_selector(".mapboxgl-popup-close-button")
            if close_button:
                await close_button.click()
                await self.page.wait_for_timeout(500)  # Wait for popup to close
        except Exception as e:
            logger.warning(f"Error closing popup: {e}")
    
    async def _pan_map_for_restaurants(self, restaurants: List[Dict], existing_names: set) -> None:
        """
        Pan around the map to find more restaurants.
        
        Args:
            restaurants: Current list of restaurants
            existing_names: Set of existing restaurant names
        """
        logger.info("Panning around the map to find more restaurants...")
        
        # Define pan points covering different Manhattan areas
        pan_points = [
            {"x": 400, "y": 300},   # Center
            {"x": 200, "y": 200},   # Upper West
            {"x": 600, "y": 200},   # Upper East
            {"x": 200, "y": 400},   # Lower West
            {"x": 600, "y": 400},   # Lower East
            {"x": 400, "y": 100},   # Upper
            {"x": 400, "y": 500}    # Lower
        ]
        
        for point in pan_points:
            try:
                logger.info(f"Panning to area: x={point['x']}, y={point['y']}")
                await self._pan_to_point(point)
                await self.page.wait_for_timeout(2000)  # Wait for map to settle
                
                # Extract restaurants in this area
                new_restaurants = await self._extract_visible_restaurants(existing_names)
                restaurants.extend(new_restaurants)
                
            except Exception as e:
                logger.warning(f"Error panning to point {point}: {e}")
    
    async def _pan_to_point(self, point: Dict[str, int]) -> None:
        """
        Pan the map to a specific point.
        
        Args:
            point: Dictionary with 'x' and 'y' coordinates
        """
        map_canvas = await self.page.query_selector(".mapboxgl-canvas")
        if not map_canvas:
            return
        
        # Start from center and drag to target point
        center_x, center_y = 400, 300
        drag_x = center_x - point["x"]
        drag_y = center_y - point["y"]
        
        await self.page.mouse.move(center_x, center_y)
        await self.page.mouse.down()
        await self.page.mouse.move(center_x + drag_x, center_y + drag_y, steps=10)
        await self.page.mouse.up()
    
    async def _zoom_for_restaurants(self, restaurants: List[Dict], existing_names: set) -> None:
        """
        Try different zoom levels to find more restaurants.
        
        Args:
            restaurants: Current list of restaurants
            existing_names: Set of existing restaurant names
        """
        logger.info("Trying different zoom levels...")
        
        zoom_levels = [2, 1, 0, -1]  # Relative zoom levels
        
        for zoom in zoom_levels:
            try:
                logger.info(f"Changing zoom level: {zoom}")
                await self._zoom_map(zoom)
                await self.page.wait_for_timeout(2000)  # Wait for zoom to complete
                
                # Extract restaurants at this zoom level
                new_restaurants = await self._extract_visible_restaurants(existing_names)
                restaurants.extend(new_restaurants)
                
            except Exception as e:
                logger.warning(f"Error zooming to level {zoom}: {e}")
    
    async def _zoom_map(self, zoom_level: int) -> None:
        """
        Zoom the map to a specific level.
        
        Args:
            zoom_level: Zoom level (positive = zoom in, negative = zoom out)
        """
        map_canvas = await self.page.query_selector(".mapboxgl-canvas")
        if not map_canvas:
            return
        
        # Get map center
        bounds = await map_canvas.bounding_box()
        center_x = bounds["x"] + bounds["width"] / 2
        center_y = bounds["y"] + bounds["height"] / 2
        
        # Perform zoom
        delta = -100 if zoom_level > 0 else 100
        for _ in range(abs(zoom_level)):
            await self.page.mouse.move(center_x, center_y)
            await self.page.mouse.wheel(0, delta)
            await self.page.wait_for_timeout(1000)
    
    async def _cleanup(self) -> None:
        """Clean up browser resources."""
        try:
            if self.browser:
                await self.browser.close()
                logger.info("Browser closed")
        except Exception as e:
            logger.warning(f"Error closing browser: {e}")
        finally:
            self.browser = None
            self.context = None
            self.page = None
    
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
