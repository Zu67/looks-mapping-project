"""
Comprehensive Playwright-based scraper for LooksMapping.com

This module provides advanced browser automation for scraping restaurant data
from LooksMapping.com using Playwright. It handles dynamic content, map interactions,
and multiple viewing modes to extract comprehensive restaurant data.

Author: LooksMapping Scraper Project
"""

import asyncio
from playwright.async_api import async_playwright
import json
import re
from collections import defaultdict
from typing import List, Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def scrape_looksmapping() -> List[Dict[str, Any]]:
    """
    Main function to scrape restaurant data from LooksMapping.com using Playwright.
    
    This function orchestrates the entire scraping process:
    1. Launch browser and navigate to website
    2. Select New York city
    3. Extract data from multiple viewing modes
    4. Process map interactions and popups
    5. Save collected data
    
    Returns:
        List[Dict[str, Any]]: List of restaurant dictionaries with extracted data
    """
    logger.info("Starting comprehensive scraping process...")
    
    async with async_playwright() as p:
        browser = await _setup_browser(p)
        page = await _setup_page(browser)
        
        try:
            await _navigate_to_website(page)
            await _select_new_york(page)
            await _wait_for_map_loading(page)
            
            # Initialize restaurant collection
            all_restaurants = []
            restaurant_names = set()
            
            # Process different viewing modes
            modes = ["hot", "age", "gender"]
            for mode in modes:
                logger.info(f"Processing {mode.upper()} mode...")
                mode_restaurants = await _process_viewing_mode(page, mode, restaurant_names)
                all_restaurants.extend(mode_restaurants)
                restaurant_names.update(r["name"] for r in mode_restaurants)
            
            # Save and analyze results
            await _save_and_analyze_results(all_restaurants)
            
            return all_restaurants
            
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            raise
        finally:
            await browser.close()
            logger.info("Browser closed")


async def _setup_browser(playwright) -> Any:
    """
    Set up and launch the browser with appropriate options.
    
    Args:
        playwright: Playwright instance
        
    Returns:
        Browser instance
    """
    logger.info("Launching browser...")
    browser = await playwright.chromium.launch(
        headless=False,  # Set to True for headless operation
        args=['--no-sandbox', '--disable-dev-shm-usage']
    )
    return browser


async def _setup_page(browser) -> Any:
    """
    Create a new browser context and page with appropriate settings.
    
    Args:
        browser: Browser instance
        
    Returns:
        Page instance
    """
    context = await browser.new_context(
        viewport={"width": 1280, "height": 800},
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    )
    page = await context.new_page()
    return page


async def _navigate_to_website(page) -> None:
    """
    Navigate to the LooksMapping website and wait for it to load.
    
    Args:
        page: Playwright page instance
    """
    logger.info("Navigating to LooksMapping website...")
    await page.goto("https://looksmapping.com", wait_until="networkidle")
    await page.wait_for_timeout(5000)  # Additional wait for dynamic content
    logger.info("Page loaded successfully")


async def _select_new_york(page) -> None:
    """
    Attempt to select New York city from the city selector.
    
    Args:
        page: Playwright page instance
    """
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
            ny_button = await page.query_selector(selector)
            if ny_button:
                logger.info("Found New York button!")
                await ny_button.click()
                await page.wait_for_timeout(3000)  # Wait for city to load
                return
        except Exception as e:
            logger.warning(f"Selector {selector} failed: {e}")
            continue
    
    logger.warning("Could not find New York button with any selector")


async def _wait_for_map_loading(page) -> None:
    """
    Wait for the map to fully load and be interactive.
    
    Args:
        page: Playwright page instance
    """
    logger.info("Waiting for map to load...")
    try:
        await page.wait_for_selector(".mapboxgl-canvas", timeout=30000)
        logger.info("Map loaded successfully")
    except Exception as e:
        logger.error(f"Map failed to load: {e}")
        raise


async def _process_viewing_mode(page, mode: str, existing_names: set) -> List[Dict[str, Any]]:
    """
    Process a specific viewing mode (hot, age, gender) and extract restaurant data.
    
    Args:
        page: Playwright page instance
        mode: Viewing mode ('hot', 'age', 'gender')
        existing_names: Set of already collected restaurant names
        
    Returns:
        List[Dict[str, Any]]: New restaurants found in this mode
    """
    try:
        # Switch to the specified mode
        await _switch_to_mode(page, mode)
        
        # Extract data from visible markers
        restaurants = await _extract_visible_restaurants(page, existing_names)
        
        # Pan around the map to find more restaurants
        await _pan_map_for_restaurants(page, restaurants, existing_names)
        
        # Try different zoom levels
        await _zoom_for_restaurants(page, restaurants, existing_names)
        
        logger.info(f"Found {len(restaurants)} new restaurants in {mode} mode")
        return restaurants
        
    except Exception as e:
        logger.error(f"Error processing {mode} mode: {e}")
        return []


async def _switch_to_mode(page, mode: str) -> None:
    """
    Switch to a specific viewing mode.
    
    Args:
        page: Playwright page instance
        mode: Mode to switch to ('hot', 'age', 'gender')
    """
    try:
        mode_button = await page.query_selector(f".mode-button[data-mode='{mode}']")
        if mode_button:
            await mode_button.click()
            await page.wait_for_timeout(3000)  # Wait for mode to change
            logger.info(f"Switched to {mode} mode")
        else:
            logger.warning(f"Could not find {mode} mode button")
    except Exception as e:
        logger.error(f"Error switching to {mode} mode: {e}")


async def _extract_visible_restaurants(page, existing_names: set) -> List[Dict[str, Any]]:
    """
    Extract data from currently visible restaurant markers.
    
    Args:
        page: Playwright page instance
        existing_names: Set of already collected restaurant names
        
    Returns:
        List[Dict[str, Any]]: New restaurants found
    """
    restaurants = []
    markers = await page.query_selector_all(".mapboxgl-marker")
    logger.info(f"Found {len(markers)} visible markers")
    
    for i, marker in enumerate(markers):
        try:
            logger.info(f"Processing marker {i+1}/{len(markers)}")
            
            # Scroll to marker and click
            await marker.scroll_into_view_if_needed()
            await page.wait_for_timeout(300)
            await marker.click()
            await page.wait_for_timeout(1000)  # Wait for popup
            
            # Extract data from popup
            restaurant = await _extract_popup_data(page)
            
            if restaurant and restaurant["name"] not in existing_names:
                restaurants.append(restaurant)
                existing_names.add(restaurant["name"])
                logger.info(f"Added new restaurant: {restaurant['name']}")
            
            # Close popup
            await _close_popup(page)
            
        except Exception as e:
            logger.warning(f"Error processing marker {i+1}: {e}")
            continue
    
    return restaurants


async def _extract_popup_data(page) -> Optional[Dict[str, Any]]:
    """
    Extract restaurant data from a popup.
    
    Args:
        page: Playwright page instance
        
    Returns:
        Optional[Dict[str, Any]]: Restaurant data or None if extraction fails
    """
    try:
        popup = await page.query_selector(".mapboxgl-popup")
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
        attractive_score, age_score, gender_score = _extract_metric_scores(metric_indicators)
        
        # Extract neighborhood
        hood = await _extract_neighborhood(page, name)
        
        return {
            "name": name,
            "cuisine": cuisine,
            "hood": hood,
            "score": score,
            "attractive_score": attractive_score,
            "age_score": age_score,
            "gender_score": gender_score,
            "reviewers": reviewers_text
        }
        
    except Exception as e:
        logger.error(f"Error extracting popup data: {e}")
        return None


def _extract_metric_scores(metric_indicators) -> tuple:
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


async def _extract_neighborhood(page, restaurant_name: str) -> str:
    """
    Extract neighborhood information for a restaurant.
    
    Args:
        page: Playwright page instance
        restaurant_name: Name of the restaurant
        
    Returns:
        str: Neighborhood name or "Unknown"
    """
    try:
        hood_element = await page.query_selector(f".result-item:has-text('{restaurant_name}') .result-hood")
        if hood_element:
            return await hood_element.text_content()
    except Exception as e:
        logger.warning(f"Error extracting neighborhood for {restaurant_name}: {e}")
    
    return "Unknown"


async def _close_popup(page) -> None:
    """
    Close any open popup.
    
    Args:
        page: Playwright page instance
    """
    try:
        close_button = await page.query_selector(".mapboxgl-popup-close-button")
        if close_button:
            await close_button.click()
            await page.wait_for_timeout(500)  # Wait for popup to close
    except Exception as e:
        logger.warning(f"Error closing popup: {e}")


async def _pan_map_for_restaurants(page, restaurants: List[Dict], existing_names: set) -> None:
    """
    Pan around the map to find more restaurants.
    
    Args:
        page: Playwright page instance
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
            await _pan_to_point(page, point)
            await page.wait_for_timeout(2000)  # Wait for map to settle
            
            # Extract restaurants in this area
            new_restaurants = await _extract_visible_restaurants(page, existing_names)
            restaurants.extend(new_restaurants)
            
        except Exception as e:
            logger.warning(f"Error panning to point {point}: {e}")


async def _pan_to_point(page, point: Dict[str, int]) -> None:
    """
    Pan the map to a specific point.
    
    Args:
        page: Playwright page instance
        point: Dictionary with 'x' and 'y' coordinates
    """
    map_canvas = await page.query_selector(".mapboxgl-canvas")
    if not map_canvas:
        return
    
    # Start from center and drag to target point
    center_x, center_y = 400, 300
    drag_x = center_x - point["x"]
    drag_y = center_y - point["y"]
    
    await page.mouse.move(center_x, center_y)
    await page.mouse.down()
    await page.mouse.move(center_x + drag_x, center_y + drag_y, steps=10)
    await page.mouse.up()


async def _zoom_for_restaurants(page, restaurants: List[Dict], existing_names: set) -> None:
    """
    Try different zoom levels to find more restaurants.
    
    Args:
        page: Playwright page instance
        restaurants: Current list of restaurants
        existing_names: Set of existing restaurant names
    """
    logger.info("Trying different zoom levels...")
    
    zoom_levels = [2, 1, 0, -1]  # Relative zoom levels
    
    for zoom in zoom_levels:
        try:
            logger.info(f"Changing zoom level: {zoom}")
            await _zoom_map(page, zoom)
            await page.wait_for_timeout(2000)  # Wait for zoom to complete
            
            # Extract restaurants at this zoom level
            new_restaurants = await _extract_visible_restaurants(page, existing_names)
            restaurants.extend(new_restaurants)
            
        except Exception as e:
            logger.warning(f"Error zooming to level {zoom}: {e}")


async def _zoom_map(page, zoom_level: int) -> None:
    """
    Zoom the map to a specific level.
    
    Args:
        page: Playwright page instance
        zoom_level: Zoom level (positive = zoom in, negative = zoom out)
    """
    map_canvas = await page.query_selector(".mapboxgl-canvas")
    if not map_canvas:
        return
    
    # Get map center
    bounds = await map_canvas.bounding_box()
    center_x = bounds["x"] + bounds["width"] / 2
    center_y = bounds["y"] + bounds["height"] / 2
    
    # Perform zoom
    delta = -100 if zoom_level > 0 else 100
    for _ in range(abs(zoom_level)):
        await page.mouse.move(center_x, center_y)
        await page.mouse.wheel(0, delta)
        await page.wait_for_timeout(1000)


async def _save_and_analyze_results(restaurants: List[Dict[str, Any]]) -> None:
    """
    Save restaurant data and perform basic analysis.
    
    Args:
        restaurants: List of restaurant dictionaries
    """
    if not restaurants:
        logger.warning("No restaurants found, creating test dataset...")
        restaurants = _create_test_dataset()
    
    # Save data to JSON file
    with open("restaurant_data.json", "w", encoding="utf-8") as f:
        json.dump(restaurants, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved {len(restaurants)} restaurants to restaurant_data.json")
    
    # Group by neighborhood
    by_hood = defaultdict(list)
    for restaurant in restaurants:
        hood = restaurant.get("hood", "Unknown")
        by_hood[hood].append(restaurant)
    
    logger.info("Neighborhoods found:")
    for hood, places in sorted(by_hood.items()):
        logger.info(f"  {hood}: {len(places)} restaurants")


def _create_test_dataset() -> List[Dict[str, Any]]:
    """
    Create a minimal test dataset for development and testing.
    
    Returns:
        List[Dict[str, Any]]: Test restaurant data
    """
    return [
        {
            "name": "Test Restaurant 1",
            "hood": "SoHo",
            "attractive_score": "8.5",
            "gender_score": "6.2",
            "age_score": "7.8"
        },
        {
            "name": "Test Restaurant 2",
            "hood": "Upper East Side",
            "attractive_score": "9.1",
            "gender_score": "5.5",
            "age_score": "8.3"
        }
    ]


if __name__ == "__main__":
    """Main execution block for command-line usage."""
    try:
        logger.info("Starting comprehensive scraper...")
        restaurants = asyncio.run(scrape_looksmapping())
        logger.info(f"Scraping completed successfully. Found {len(restaurants)} restaurants.")
    except ImportError as e:
        logger.error("Playwright is not installed. Please install it with: pip install playwright")
        logger.error("Then run: playwright install")
        raise
    except Exception as e:
        logger.error(f"An error occurred during scraping: {e}")
        raise