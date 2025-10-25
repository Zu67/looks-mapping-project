"""
Neighborhood Analysis Module for LooksMapping Data

This module provides statistical analysis of Manhattan neighborhoods based on
restaurant data scraped from LooksMapping.com. It calculates averages for
attractiveness, age demographics, and gender ratios by neighborhood.

Author: LooksMapping Scraper Project
"""

import json
from collections import defaultdict
import statistics
import pandas as pd
from typing import List, Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def analyze_manhattan_neighborhoods(data_file: str = 'restaurant_data.json') -> pd.DataFrame:
    """
    Analyze Manhattan neighborhoods based on restaurant data.
    
    This function loads restaurant data and calculates statistical averages
    for each Manhattan neighborhood across different metrics:
    - Attractiveness scores
    - Age demographics
    - Gender ratios
    
    Args:
        data_file: Path to the JSON file containing restaurant data
        
    Returns:
        pd.DataFrame: DataFrame with neighborhood statistics
        
    Raises:
        FileNotFoundError: If the data file doesn't exist
        json.JSONDecodeError: If the data file is not valid JSON
    """
    logger.info("Starting Manhattan neighborhood analysis...")
    
    # Load restaurant data
    restaurants = _load_restaurant_data(data_file)
    
    # Filter for Manhattan neighborhoods
    manhattan_restaurants = _filter_manhattan_restaurants(restaurants)
    
    # Group restaurants by neighborhood
    neighborhoods = _group_restaurants_by_neighborhood(manhattan_restaurants)
    
    # Calculate statistics for each neighborhood
    neighborhood_stats = _calculate_neighborhood_statistics(neighborhoods)
    
    # Create DataFrame and generate reports
    df = _create_analysis_dataframe(neighborhood_stats)
    _generate_analysis_reports(df)
    
    logger.info("Neighborhood analysis completed")
    return df


def _load_restaurant_data(data_file: str) -> List[Dict[str, Any]]:
    """
    Load restaurant data from JSON file.
    
    Args:
        data_file: Path to the JSON file
        
    Returns:
        List[Dict[str, Any]]: List of restaurant dictionaries
    """
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded {len(data)} restaurants from {data_file}")
        return data
    except FileNotFoundError:
        logger.error(f"Data file {data_file} not found")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {data_file}: {e}")
        raise


def _filter_manhattan_restaurants(restaurants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter restaurants to include only Manhattan neighborhoods.
    
    Args:
        restaurants: List of restaurant dictionaries
        
    Returns:
        List[Dict[str, Any]]: Filtered list of Manhattan restaurants
    """
    # Define Manhattan neighborhoods
    manhattan_neighborhoods = {
        "Midtown East", "Midtown West", "Hell's Kitchen", "Chelsea", "Flatiron District",
        "Gramercy", "Murray Hill", "Kips Bay", "East Village", "West Village", "Greenwich Village",
        "SoHo", "NoHo", "Tribeca", "Financial District", "Lower East Side", "Chinatown",
        "Little Italy", "Upper East Side", "Upper West Side", "Harlem", "East Harlem",
        "Washington Heights", "Inwood", "NoMad", "Koreatown", "Nolita", "Battery Park City",
        "Morningside Heights", "Central Park South", "Theater District", "Garment District"
    }
    
    manhattan_restaurants = []
    for restaurant in restaurants:
        hood = restaurant.get("hood", "")
        if hood in manhattan_neighborhoods:
            manhattan_restaurants.append(restaurant)
    
    logger.info(f"Filtered to {len(manhattan_restaurants)} Manhattan restaurants")
    return manhattan_restaurants


def _group_restaurants_by_neighborhood(restaurants: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group restaurants by neighborhood.
    
    Args:
        restaurants: List of restaurant dictionaries
        
    Returns:
        Dict[str, List[Dict[str, Any]]]: Dictionary mapping neighborhoods to restaurant lists
    """
    neighborhoods = defaultdict(list)
    
    for restaurant in restaurants:
        hood = restaurant.get("hood", "Unknown")
        neighborhoods[hood].append({
            "name": restaurant.get("name", "Unknown"),
            "attractive_score": _safe_float(restaurant.get("attractive_score", "0")),
            "age_score": _safe_float(restaurant.get("age_score", "0")),
            "gender_score": _safe_float(restaurant.get("gender_score", "0")),
            "category": restaurant.get("category", "Unknown")
        })
    
    logger.info(f"Grouped restaurants into {len(neighborhoods)} neighborhoods")
    return dict(neighborhoods)


def _safe_float(value: Any) -> float:
    """
    Safely convert a value to float, handling string inputs.
    
    Args:
        value: Value to convert to float
        
    Returns:
        float: Converted float value or 0.0 if conversion fails
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def _calculate_neighborhood_statistics(neighborhoods: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Calculate statistical averages for each neighborhood.
    
    Args:
        neighborhoods: Dictionary mapping neighborhoods to restaurant lists
        
    Returns:
        List[Dict[str, Any]]: List of neighborhood statistics
    """
    neighborhood_stats = []
    
    for hood, restaurants in neighborhoods.items():
        if not restaurants:  # Skip empty neighborhoods
            continue
        
        try:
            # Calculate averages
            avg_attractive = statistics.mean([r["attractive_score"] for r in restaurants])
            avg_age = statistics.mean([r["age_score"] for r in restaurants])
            avg_gender = statistics.mean([r["gender_score"] for r in restaurants])
            
            # Store the stats
            neighborhood_stats.append({
                "neighborhood": hood,
                "restaurant_count": len(restaurants),
                "avg_attractive": round(avg_attractive, 2),
                "avg_age": round(avg_age, 2),
                "avg_gender": round(avg_gender, 2)
            })
            
        except statistics.StatisticsError as e:
            logger.warning(f"Error calculating statistics for {hood}: {e}")
            continue
    
    logger.info(f"Calculated statistics for {len(neighborhood_stats)} neighborhoods")
    return neighborhood_stats


def _create_analysis_dataframe(neighborhood_stats: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Create a pandas DataFrame from neighborhood statistics.
    
    Args:
        neighborhood_stats: List of neighborhood statistics
        
    Returns:
        pd.DataFrame: DataFrame with neighborhood statistics
    """
    df = pd.DataFrame(neighborhood_stats)
    
    if df.empty:
        logger.warning("No neighborhood statistics to display")
        return df
    
    # Sort by different metrics for analysis
    df = df.sort_values("restaurant_count", ascending=False)
    
    return df


def _generate_analysis_reports(df: pd.DataFrame) -> None:
    """
    Generate and display analysis reports.
    
    Args:
        df: DataFrame with neighborhood statistics
    """
    if df.empty:
        logger.warning("No data available for analysis")
        return
    
    # Sort by different metrics
    hottest_neighborhoods = df.sort_values("avg_attractive", ascending=False)
    youngest_neighborhoods = df.sort_values("avg_age", ascending=False)
    most_female_neighborhoods = df.sort_values("avg_gender", ascending=True)  # Lower = more female
    
    # Display results
    logger.info("\n=== MANHATTAN NEIGHBORHOODS RANKED BY ATTRACTIVENESS ===")
    print("\n=== MANHATTAN NEIGHBORHOODS RANKED BY ATTRACTIVENESS ===")
    print(hottest_neighborhoods[["neighborhood", "avg_attractive", "restaurant_count"]].to_string(index=False))
    
    logger.info("\n=== MANHATTAN NEIGHBORHOODS RANKED BY YOUTH ===")
    print("\n=== MANHATTAN NEIGHBORHOODS RANKED BY YOUTH ===")
    print(youngest_neighborhoods[["neighborhood", "avg_age", "restaurant_count"]].to_string(index=False))
    
    logger.info("\n=== MANHATTAN NEIGHBORHOODS RANKED BY FEMALE RATIO ===")
    print("\n=== MANHATTAN NEIGHBORHOODS RANKED BY FEMALE RATIO ===")
    print(most_female_neighborhoods[["neighborhood", "avg_gender", "restaurant_count"]].to_string(index=False))


def extract_restaurant_data() -> List[Dict[str, Any]]:
    """
    Extract restaurant data from the website or file.
    
    This function is a placeholder for data extraction functionality.
    In a real implementation, this would extract data from the website
    or load it from a file.
    
    Returns:
        List[Dict[str, Any]]: List of restaurant dictionaries
    """
    logger.info("Extracting restaurant data...")
    
    # This is a placeholder implementation
    # In practice, you would:
    # 1. Parse the HTML to extract the 'rankings' JavaScript object
    # 2. Convert it to a Python data structure
    # 3. Extract all restaurant data
    
    restaurants = []
    
    # Save to a JSON file for later use
    with open('restaurant_data.json', 'w', encoding='utf-8') as f:
        json.dump(restaurants, f, indent=2, ensure_ascii=False)
    
    logger.info("Restaurant data extraction completed")
    return restaurants


if __name__ == "__main__":
    """Main execution block for command-line usage."""
    try:
        logger.info("Starting neighborhood analysis...")
        df = analyze_manhattan_neighborhoods()
        logger.info(f"Analysis completed. Processed {len(df)} neighborhoods.")
    except Exception as e:
        logger.error(f"An error occurred during analysis: {e}")
        raise 