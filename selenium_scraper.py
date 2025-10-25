"""
Selenium-based scraper for LooksMapping.com

This module provides browser automation for scraping restaurant data
from LooksMapping.com using Selenium WebDriver. It handles dynamic content
and extracts data from multiple viewing modes.

Author: LooksMapping Scraper Project
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
import re
from collections import defaultdict
from typing import List, Dict, Any, Set
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def scrape_with_selenium() -> List[Dict[str, Any]]:
    """
    Scrape restaurant data from LooksMapping.com using Selenium WebDriver.
    
    This function:
    1. Launches a Chrome browser
    2. Navigates to the website
    3. Selects New York city
    4. Extracts data from multiple viewing modes
    5. Saves results to JSON file
    
    Returns:
        List[Dict[str, Any]]: List of restaurant dictionaries with extracted data
    """
    driver = None
    try:
        driver = _setup_webdriver()
        _navigate_to_website(driver)
        _select_new_york(driver)
        _wait_for_restaurant_elements(driver)
        
        # Extract initial restaurant data
        restaurants = _extract_restaurant_data(driver)
        logger.info(f"Successfully extracted data for {len(restaurants)} restaurants")
        
        # Extract data from different viewing modes
        restaurants = _extract_from_viewing_modes(driver, restaurants)
        
        # Save and analyze results
        _save_and_analyze_results(restaurants, driver)
        
        return restaurants
        
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        raise
    finally:
        if driver:
            driver.quit()
            logger.info("WebDriver closed")


def _setup_webdriver() -> webdriver.Chrome:
    """
    Set up and configure the Chrome WebDriver.
    
    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance
    """
    logger.info("Setting up Chrome WebDriver...")
    
    chrome_options = Options()
    # Uncomment the line below if you want to run headless
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    
    return driver


def _navigate_to_website(driver: webdriver.Chrome) -> None:
    """
    Navigate to the LooksMapping website and wait for it to load.
    
    Args:
        driver: Chrome WebDriver instance
    """
    logger.info("Navigating to LooksMapping website...")
    driver.get("https://looksmapping.com")
    
    # Wait for the page to fully load
    logger.info("Waiting for page to load...")
    time.sleep(5)  # Initial wait for dynamic content


def _select_new_york(driver: webdriver.Chrome) -> None:
    """
    Select New York city from the city selector.
    
    Args:
        driver: Chrome WebDriver instance
    """
    try:
        ny_link = driver.find_element(By.XPATH, "//span[contains(text(), 'New York')]")
        if "city-active" not in ny_link.get_attribute("class"):
            logger.info("Clicking on New York...")
            ny_link.click()
            time.sleep(3)  # Wait for the city to load
        else:
            logger.info("New York is already selected")
    except NoSuchElementException:
        logger.warning("Could not find New York button")
    except Exception as e:
        logger.error(f"Error selecting New York: {e}")


def _wait_for_restaurant_elements(driver: webdriver.Chrome) -> None:
    """
    Wait for restaurant elements to appear on the page.
    
    Args:
        driver: Chrome WebDriver instance
    """
    logger.info("Waiting for restaurant elements...")
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[onclick*='flyToLocation']"))
        )
        logger.info("Restaurant elements found")
    except TimeoutException:
        logger.warning("Restaurant elements did not appear within timeout")


def _extract_restaurant_data(driver: webdriver.Chrome) -> List[Dict[str, Any]]:
    """
    Extract restaurant data from the current page state.
    
    Args:
        driver: Chrome WebDriver instance
        
    Returns:
        List[Dict[str, Any]]: List of restaurant dictionaries
    """
    logger.info("Finding restaurant elements...")
    restaurant_elements = driver.find_elements(By.CSS_SELECTOR, "div[onclick*='flyToLocation']")
    logger.info(f"Found {len(restaurant_elements)} restaurant elements")
    
    restaurants = []
    for element in restaurant_elements:
        try:
            restaurant_data = _extract_element_data(element)
            if restaurant_data:
                restaurants.append(restaurant_data)
        except Exception as e:
            logger.warning(f"Error extracting data from element: {e}")
    
    return restaurants


def _extract_element_data(element) -> Dict[str, Any]:
    """
    Extract restaurant data from a single element.
    
    Args:
        element: WebElement containing restaurant data
        
    Returns:
        Dict[str, Any]: Restaurant data dictionary or None if extraction fails
    """
    try:
        onclick = element.get_attribute("onclick")
        if not onclick or "flyToLocation" not in onclick:
            return None
        
        # Extract coordinates and JSON data from onclick attribute
        match = re.search(r'flyToLocation\(([^,]+),\s*([^,]+),\s*({.+?})\)', onclick)
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
        data["name"] = _extract_name_from_element(element, data)
        data["hood"] = _extract_neighborhood_from_element(element, data)
        
        return data
        
    except (json.JSONDecodeError, ValueError, AttributeError) as e:
        logger.warning(f"Error parsing element data: {e}")
        return None


def _extract_name_from_element(element, data: Dict[str, Any]) -> str:
    """
    Extract restaurant name from element or existing data.
    
    Args:
        element: WebElement containing restaurant data
        data: Existing restaurant data dictionary
        
    Returns:
        str: Restaurant name
    """
    if "name" in data:
        return data["name"]
    
    try:
        name_element = element.find_element(By.CSS_SELECTOR, ".result-name")
        return name_element.text
    except NoSuchElementException:
        return "Unknown"


def _extract_neighborhood_from_element(element, data: Dict[str, Any]) -> str:
    """
    Extract neighborhood from element or existing data.
    
    Args:
        element: WebElement containing restaurant data
        data: Existing restaurant data dictionary
        
    Returns:
        str: Neighborhood name
    """
    if "hood" in data:
        return data["hood"]
    
    try:
        hood_element = element.find_element(By.CSS_SELECTOR, ".result-hood")
        return hood_element.text
    except NoSuchElementException:
        return "Unknown"


def _extract_from_viewing_modes(driver: webdriver.Chrome, existing_restaurants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extract restaurant data from different viewing modes.
    
    Args:
        driver: Chrome WebDriver instance
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
            _switch_to_mode(driver, mode)
            
            # Get new restaurant elements
            new_elements = driver.find_elements(By.CSS_SELECTOR, "div[onclick*='flyToLocation']")
            logger.info(f"Found {len(new_elements)} restaurant elements in {mode} mode")
            
            # Extract data from new elements
            for element in new_elements:
                try:
                    restaurant_data = _extract_element_data(element)
                    if restaurant_data and restaurant_data.get("name") not in existing_names:
                        restaurants.append(restaurant_data)
                        existing_names.add(restaurant_data["name"])
                except Exception as e:
                    logger.warning(f"Error extracting data from element in {mode} mode: {e}")
                    
        except Exception as e:
            logger.error(f"Error switching to {mode} mode: {e}")
    
    logger.info(f"Total unique restaurants found: {len(restaurants)}")
    return restaurants


def _switch_to_mode(driver: webdriver.Chrome, mode: str) -> None:
    """
    Switch to a specific viewing mode.
    
    Args:
        driver: Chrome WebDriver instance
        mode: Mode to switch to ('hot', 'age', 'gender')
    """
    try:
        mode_button = driver.find_element(By.CSS_SELECTOR, f".mode-button[data-mode='{mode}']")
        mode_button.click()
        time.sleep(2)  # Wait for the mode to change
    except NoSuchElementException:
        logger.warning(f"Could not find {mode} mode button")
    except Exception as e:
        logger.error(f"Error switching to {mode} mode: {e}")


def _save_and_analyze_results(restaurants: List[Dict[str, Any]], driver: webdriver.Chrome) -> None:
    """
    Save restaurant data and perform basic analysis.
    
    Args:
        restaurants: List of restaurant dictionaries
        driver: Chrome WebDriver instance
    """
    # Save the data to JSON file
    with open("restaurant_data.json", "w", encoding="utf-8") as f:
        json.dump(restaurants, f, indent=2, ensure_ascii=False)
    
    logger.info("Data saved to restaurant_data.json")
    
    # Group restaurants by neighborhood
    by_hood = defaultdict(list)
    for restaurant in restaurants:
        hood = restaurant.get("hood", "Unknown")
        by_hood[hood].append(restaurant)
    
    logger.info("Neighborhoods found:")
    for hood, places in sorted(by_hood.items()):
        logger.info(f"  {hood}: {len(places)} restaurants")
    
    # Save the full HTML for reference
    try:
        with open("looksmapping_complete.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        logger.info("Complete HTML saved to looksmapping_complete.html")
    except Exception as e:
        logger.warning(f"Error saving HTML: {e}")


if __name__ == "__main__":
    """Main execution block for command-line usage."""
    try:
        logger.info("Starting Selenium scraper...")
        restaurants = scrape_with_selenium()
        logger.info(f"Scraping completed successfully. Found {len(restaurants)} restaurants.")
    except Exception as e:
        logger.error(f"An error occurred during scraping: {e}")
        raise
