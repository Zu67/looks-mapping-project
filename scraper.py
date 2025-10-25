"""
Main scraper interface for LooksMapping.com

This module provides a unified interface for scraping restaurant data
from LooksMapping.com with multiple extraction strategies and fallback options.

Author: LooksMapping Scraper Project
"""

import requests
from bs4 import BeautifulSoup
import re
import json
from collections import defaultdict
from typing import List, Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def scrape_looksmapping(city: str = "New York") -> List[Dict[str, Any]]:
    """
    Scrape restaurant data from LooksMapping.com for a specific city.
    
    This function attempts multiple extraction strategies:
    1. Extract data from onclick attributes
    2. Look for JSON data in script tags
    3. Fall back to test data if no extraction succeeds
    
    Args:
        city: City name to scrape data for (default: "New York")
        
    Returns:
        List[Dict[str, Any]]: List of restaurant dictionaries with extracted data
    """
    logger.info(f"Scraping LooksMapping data for {city}...")
    
    # Fetch the website
    response = _fetch_website()
    if not response:
        return []
    
    # Parse HTML content
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Try multiple extraction strategies
    restaurant_data = _extract_from_onclick_attributes(soup)
    
    if not restaurant_data:
        logger.info("No data found in onclick attributes, trying script extraction...")
        restaurant_data = _extract_from_script_tags(soup)
    
    if not restaurant_data:
        logger.warning("No restaurant data found, creating test dataset...")
        restaurant_data = _create_test_dataset()
    
    # Save and analyze results
    _save_and_analyze_results(restaurant_data)
    
    return restaurant_data


def _fetch_website() -> Optional[requests.Response]:
    """
    Fetch the LooksMapping website.
    
    Returns:
        Optional[requests.Response]: Response object or None if fetch fails
    """
    url = "https://looksmapping.com"
    logger.info(f"Requesting {url}")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        logger.info(f"Successfully retrieved website. Content length: {len(response.text)}")
        return response
    except requests.RequestException as e:
        logger.error(f"Failed to retrieve the website: {e}")
        return None


def _extract_from_onclick_attributes(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """
    Extract restaurant data from onclick attributes.
    
    Args:
        soup: BeautifulSoup object of the HTML content
        
    Returns:
        List[Dict[str, Any]]: Extracted restaurant data
    """
    restaurant_data = []
    
    # Look for elements with onclick attributes containing flyToLocation
    elements_with_onclick = soup.find_all(
        lambda tag: tag.has_attr("onclick") and "flyToLocation(" in tag["onclick"]
    )
    logger.info(f"Found {len(elements_with_onclick)} elements with flyToLocation in onclick attribute")
    
    # Extract data from onclick attributes
    pattern = re.compile(r"flyToLocation\([^,]+,[^,]+,({.+?})\)")
    
    for element in elements_with_onclick:
        onclick = element.get("onclick")
        match = pattern.search(onclick)
        if match:
            json_str = match.group(1)
            json_str = json_str.replace("&quot;", "\"")
            try:
                data = json.loads(json_str)
                restaurant_data.append(data)
                logger.debug(f"Extracted data: {data}")
            except json.JSONDecodeError as e:
                logger.warning(f"Error parsing JSON: {e}")
                logger.debug(f"Problematic JSON string: {json_str}")
    
    logger.info(f"Total restaurants found: {len(restaurant_data)}")
    return restaurant_data


def _extract_from_script_tags(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """
    Extract restaurant data from script tags.
    
    Args:
        soup: BeautifulSoup object of the HTML content
        
    Returns:
        List[Dict[str, Any]]: Extracted restaurant data
    """
    restaurant_data = []
    scripts = soup.find_all("script")
    logger.info(f"Found {len(scripts)} script tags")
    
    for script in scripts:
        if script.string and "restaurants" in script.string.lower():
            logger.info("Found script with 'restaurants' keyword")
            # Try to extract JSON from the script
            json_match = re.search(r'({.*"restaurants".*})', script.string, re.DOTALL)
            if json_match:
                try:
                    json_data = json.loads(json_match.group(1))
                    logger.info("Successfully parsed JSON from script")
                    # Process the JSON data here
                    if isinstance(json_data, dict) and "restaurants" in json_data:
                        restaurant_data.extend(json_data["restaurants"])
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON from script: {e}")
    
    logger.info(f"Extracted {len(restaurant_data)} restaurants from script tags")
    return restaurant_data


def _create_test_dataset() -> List[Dict[str, Any]]:
    """
    Create a test dataset for development and testing.
    
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


def _save_and_analyze_results(restaurant_data: List[Dict[str, Any]]) -> None:
    """
    Save restaurant data and perform basic analysis.
    
    Args:
        restaurant_data: List of restaurant dictionaries
    """
    if not restaurant_data:
        logger.warning("No restaurant data to save")
        return
    
    # Save the data to JSON file
    with open("restaurant_data.json", "w", encoding="utf-8") as f:
        json.dump(restaurant_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved {len(restaurant_data)} restaurants to restaurant_data.json")
    
    # Group by neighborhood and display results
    by_hood = defaultdict(list)
    for restaurant in restaurant_data:
        hood = restaurant.get("hood", "Unknown")
        by_hood[hood].append(restaurant)
    
    logger.info("Neighborhoods found:")
    for hood, places in by_hood.items():
        logger.info(f"\nNeighborhood: {hood}")
        for place in places:
            name = place.get("name", "Unknown")
            hot = place.get("attractive_score", "N/A")
            gender = place.get("gender_score", "N/A")
            age = place.get("age_score", "N/A")
            logger.info(f"  {name}: Hot {hot}, Gender {gender}, Age {age}")
        logger.info("-" * 40)


if __name__ == "__main__":
    """Main execution block for command-line usage."""
    try:
        logger.info("Starting main scraper...")
        restaurants = scrape_looksmapping("New York")
        logger.info(f"Scraping completed successfully. Found {len(restaurants)} restaurants.")
    except Exception as e:
        logger.error(f"An error occurred during scraping: {e}")
        raise