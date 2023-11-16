"""
Helper utilities for LooksMapping Scraper.

This module contains utility functions for data cleaning, validation,
and common operations used across the scraper.
"""

import re
from typing import Any, Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)


def clean_string(value: Any) -> str:
    """
    Clean and normalize string values.
    
    Args:
        value: Value to clean
        
    Returns:
        str: Cleaned string value
    """
    if value is None:
        return ""
    
    # Convert to string and strip whitespace
    cleaned = str(value).strip()
    
    # Remove extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    return cleaned


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert a value to float.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        float: Converted float value or default
    """
    if value is None:
        return default
    
    try:
        return float(value)
    except (ValueError, TypeError):
        logger.warning(f"Could not convert '{value}' to float, using default {default}")
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert a value to integer.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        int: Converted integer value or default
    """
    if value is None:
        return default
    
    try:
        return int(value)
    except (ValueError, TypeError):
        logger.warning(f"Could not convert '{value}' to int, using default {default}")
        return default


def validate_restaurant_data(data: Dict[str, Any]) -> bool:
    """
    Validate restaurant data structure.
    
    Args:
        data: Restaurant data dictionary
        
    Returns:
        bool: True if data is valid, False otherwise
    """
    if not isinstance(data, dict):
        logger.warning("Restaurant data must be a dictionary")
        return False
    
    # Check for required fields
    required_fields = ["name"]
    for field in required_fields:
        if field not in data or not data[field]:
            logger.warning(f"Missing required field: {field}")
            return False
    
    # Validate string fields
    string_fields = ["name", "hood", "cuisine", "score", "reviewers"]
    for field in string_fields:
        if field in data and data[field] is not None:
            if not isinstance(data[field], str):
                logger.warning(f"Field '{field}' should be a string")
                return False
    
    # Validate numeric fields
    numeric_fields = ["attractive_score", "age_score", "gender_score", "lat", "long"]
    for field in numeric_fields:
        if field in data and data[field] is not None:
            try:
                float(data[field])
            except (ValueError, TypeError):
                logger.warning(f"Field '{field}' should be numeric")
                return False
    
    return True


def clean_restaurant_data(data: Dict[str, Any]) -> Dict[str, Any]:
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
            cleaned[field] = clean_string(data[field])
    
    # Clean numeric fields
    numeric_fields = ["attractive_score", "age_score", "gender_score", "lat", "long"]
    for field in numeric_fields:
        if field in data:
            cleaned[field] = safe_float(data[field])
    
    # Add metadata
    cleaned["source"] = "looksmapping.com"
    
    return cleaned


def extract_coordinates(data: Dict[str, Any]) -> tuple[Optional[float], Optional[float]]:
    """
    Extract latitude and longitude from restaurant data.
    
    Args:
        data: Restaurant data dictionary
        
    Returns:
        tuple: (latitude, longitude) or (None, None) if not found
    """
    lat = data.get("lat") or data.get("latitude")
    lng = data.get("long") or data.get("longitude") or data.get("lng")
    
    if lat is not None and lng is not None:
        return safe_float(lat), safe_float(lng)
    
    return None, None


def is_manhattan_neighborhood(neighborhood: str) -> bool:
    """
    Check if a neighborhood is in Manhattan.
    
    Args:
        neighborhood: Neighborhood name
        
    Returns:
        bool: True if neighborhood is in Manhattan
    """
    if not neighborhood:
        return False
    
    manhattan_neighborhoods = {
        "midtown east", "midtown west", "hell's kitchen", "chelsea",
        "flatiron district", "gramercy", "murray hill", "kips bay",
        "east village", "west village", "greenwich village", "soho",
        "noho", "tribeca", "financial district", "lower east side",
        "chinatown", "little italy", "upper east side", "upper west side",
        "harlem", "east harlem", "washington heights", "inwood", "nomad",
        "koreatown", "nolita", "battery park city", "morningside heights",
        "central park south", "theater district", "garment district"
    }
    
    return neighborhood.lower().strip() in manhattan_neighborhoods


def group_by_neighborhood(restaurants: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group restaurants by neighborhood.
    
    Args:
        restaurants: List of restaurant dictionaries
        
    Returns:
        Dict[str, List[Dict[str, Any]]]: Restaurants grouped by neighborhood
    """
    groups = {}
    
    for restaurant in restaurants:
        hood = restaurant.get("hood", "Unknown")
        if hood not in groups:
            groups[hood] = []
        groups[hood].append(restaurant)
    
    return groups


def filter_manhattan_restaurants(restaurants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter restaurants to include only Manhattan neighborhoods.
    
    Args:
        restaurants: List of restaurant dictionaries
        
    Returns:
        List[Dict[str, Any]]: Filtered list of Manhattan restaurants
    """
    return [
        restaurant for restaurant in restaurants
        if is_manhattan_neighborhood(restaurant.get("hood", ""))
    ]


def deduplicate_restaurants(restaurants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove duplicate restaurants based on name.
    
    Args:
        restaurants: List of restaurant dictionaries
        
    Returns:
        List[Dict[str, Any]]: List with duplicates removed
    """
    seen_names = set()
    unique_restaurants = []
    
    for restaurant in restaurants:
        name = restaurant.get("name", "").strip().lower()
        if name and name not in seen_names:
            seen_names.add(name)
            unique_restaurants.append(restaurant)
    
    return unique_restaurants
