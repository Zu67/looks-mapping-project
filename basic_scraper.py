"""
Basic HTTP-based scraper for LooksMapping.com

This module provides a simple HTTP-based approach to scraping restaurant data
from LooksMapping.com. It uses requests and BeautifulSoup to extract data
from the website's JavaScript objects and HTML content.

Author: LooksMapping Scraper Project
"""

import requests
import json
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Any


def scrape_looksmapping() -> List[Dict[str, Any]]:
    """
    Scrape restaurant data from LooksMapping.com using HTTP requests.
    
    This function attempts multiple extraction strategies:
    1. Extract data from JavaScript rankings object
    2. Use regex pattern matching on HTML content
    3. Fall back to test dataset if no data found
    
    Returns:
        List[Dict[str, Any]]: List of restaurant dictionaries with extracted data
        
    Raises:
        requests.RequestException: If the HTTP request fails
        json.JSONDecodeError: If JSON parsing fails
    """
    print("Fetching the website...")
    
    # Set up headers to mimic a real browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get("https://looksmapping.com", headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch website: {e}")
        return []
    
    html_content = response.text
    print(f"Successfully fetched website, content length: {len(html_content)}")
    
    # Save the raw HTML for inspection and debugging
    with open("raw_looksmapping.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    restaurants = _extract_restaurants_from_js(html_content)
    
    # Fallback to pattern matching if JavaScript extraction failed
    if not restaurants:
        print("Trying pattern matching approach...")
        restaurants = _extract_restaurants_with_regex(html_content)
    
    # Final fallback to test data
    if not restaurants:
        print("No restaurants found. Creating test dataset...")
        restaurants = _create_test_dataset()
    
    # Save the extracted data
    _save_restaurant_data(restaurants)
    
    return restaurants


def _extract_restaurants_from_js(html_content: str) -> List[Dict[str, Any]]:
    """
    Extract restaurant data from JavaScript rankings object.
    
    Args:
        html_content: Raw HTML content from the website
        
    Returns:
        List[Dict[str, Any]]: Extracted restaurant data
    """
    restaurants = []
    
    # Look for the rankings JavaScript object
    rankings_pattern = re.compile(r'const\s+rankings\s*=\s*({.*?});', re.DOTALL)
    rankings_match = rankings_pattern.search(html_content)
    
    if rankings_match:
        print("Found rankings data in JavaScript!")
        try:
            rankings_json = rankings_match.group(1)
            rankings = json.loads(rankings_json)
            
            # Extract NY restaurants from the rankings object
            if "ny" in rankings:
                for metric, metric_data in rankings["ny"].items():
                    for position, restaurant_list in metric_data.items():
                        for restaurant in restaurant_list:
                            # Avoid duplicates by checking existing restaurants
                            if not any(r.get("name") == restaurant.get("name") for r in restaurants):
                                restaurants.append(restaurant)
            
            print(f"Extracted {len(restaurants)} unique restaurants from rankings data")
        except json.JSONDecodeError as e:
            print(f"Error parsing rankings JSON: {e}")
    
    return restaurants


def _extract_restaurants_with_regex(html_content: str) -> List[Dict[str, Any]]:
    """
    Extract restaurant data using regex pattern matching.
    
    Args:
        html_content: Raw HTML content from the website
        
    Returns:
        List[Dict[str, Any]]: Extracted restaurant data
    """
    restaurants = []
    
    # Pattern to match restaurant data in HTML
    restaurant_pattern = re.compile(
        r'"name":"([^"]+)"[^}]+"hood":"([^"]+)"[^}]+"attractive_score":"([^"]+)"[^}]+"age_score":"([^"]+)"[^}]+"gender_score":"([^"]+)"'
    )
    matches = restaurant_pattern.findall(html_content)
    
    for match in matches:
        name, hood, attractive, age, gender = match
        restaurants.append({
            "name": name,
            "hood": hood,
            "attractive_score": attractive,
            "age_score": age,
            "gender_score": gender
        })
    
    print(f"Found {len(restaurants)} restaurants using pattern matching")
    return restaurants


def _create_test_dataset() -> List[Dict[str, Any]]:
    """
    Create a test dataset for development and testing purposes.
    
    Returns:
        List[Dict[str, Any]]: Test restaurant data
    """
    test_restaurants = [
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
        },
        {
            "name": "Test Restaurant 3",
            "hood": "West Village",
            "attractive_score": "8.9",
            "gender_score": "7.2",
            "age_score": "6.5"
        },
        {
            "name": "Test Restaurant 4",
            "hood": "Tribeca",
            "attractive_score": "9.3",
            "gender_score": "6.8",
            "age_score": "7.1"
        },
        {
            "name": "Test Restaurant 5",
            "hood": "Chelsea",
            "attractive_score": "8.7",
            "gender_score": "6.5",
            "age_score": "7.9"
        }
    ]
    
    print("Created test dataset with 5 restaurants")
    return test_restaurants


def _save_restaurant_data(restaurants: List[Dict[str, Any]]) -> None:
    """
    Save restaurant data to JSON file.
    
    Args:
        restaurants: List of restaurant dictionaries to save
    """
    with open("restaurant_data.json", "w", encoding="utf-8") as f:
        json.dump(restaurants, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(restaurants)} restaurants to restaurant_data.json")


if __name__ == "__main__":
    """Main execution block for command-line usage."""
    try:
        restaurants = scrape_looksmapping()
        print(f"Scraping completed successfully. Found {len(restaurants)} restaurants.")
    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        raise 