"""
Tests for helper utilities.
"""

import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from utils.helpers import (
    clean_string,
    safe_float,
    safe_int,
    validate_restaurant_data,
    clean_restaurant_data,
    extract_coordinates,
    is_manhattan_neighborhood,
    group_by_neighborhood,
    filter_manhattan_restaurants,
    deduplicate_restaurants
)


class TestHelpers:
    """Test cases for helper functions."""
    
    def test_clean_string(self):
        """Test string cleaning."""
        assert clean_string("  test  ") == "test"
        assert clean_string("  test  string  ") == "test string"
        assert clean_string(None) == ""
        assert clean_string(123) == "123"
    
    def test_safe_float(self):
        """Test safe float conversion."""
        assert safe_float("8.5") == 8.5
        assert safe_float("invalid") == 0.0
        assert safe_float(None) == 0.0
        assert safe_float("8.5", 1.0) == 8.5
        assert safe_float("invalid", 1.0) == 1.0
    
    def test_safe_int(self):
        """Test safe integer conversion."""
        assert safe_int("8") == 8
        assert safe_int("8.5") == 8
        assert safe_int("invalid") == 0
        assert safe_int(None) == 0
        assert safe_int("invalid", 1) == 1
    
    def test_validate_restaurant_data_valid(self):
        """Test validation of valid restaurant data."""
        valid_data = {
            "name": "Test Restaurant",
            "hood": "SoHo",
            "attractive_score": 8.5
        }
        
        assert validate_restaurant_data(valid_data) is True
    
    def test_validate_restaurant_data_invalid(self):
        """Test validation of invalid restaurant data."""
        invalid_data = {
            "hood": "SoHo",
            "attractive_score": 8.5
            # Missing required 'name' field
        }
        
        assert validate_restaurant_data(invalid_data) is False
    
    def test_validate_restaurant_data_not_dict(self):
        """Test validation of non-dictionary data."""
        assert validate_restaurant_data("not a dict") is False
        assert validate_restaurant_data(None) is False
    
    def test_clean_restaurant_data(self):
        """Test restaurant data cleaning."""
        raw_data = {
            "name": "  Test Restaurant  ",
            "hood": "  SoHo  ",
            "attractive_score": "8.5",
            "age_score": "7.2"
        }
        
        cleaned = clean_restaurant_data(raw_data)
        
        assert cleaned["name"] == "Test Restaurant"
        assert cleaned["hood"] == "SoHo"
        assert cleaned["attractive_score"] == 8.5
        assert cleaned["age_score"] == 7.2
        assert cleaned["source"] == "looksmapping.com"
    
    def test_extract_coordinates(self):
        """Test coordinate extraction."""
        data_with_lat_long = {"lat": 40.7589, "long": -73.9851}
        lat, lng = extract_coordinates(data_with_lat_long)
        assert lat == 40.7589
        assert lng == -73.9851
        
        data_with_latitude_longitude = {"latitude": 40.7589, "longitude": -73.9851}
        lat, lng = extract_coordinates(data_with_latitude_longitude)
        assert lat == 40.7589
        assert lng == -73.9851
        
        data_with_lng = {"lat": 40.7589, "lng": -73.9851}
        lat, lng = extract_coordinates(data_with_lng)
        assert lat == 40.7589
        assert lng == -73.9851
        
        data_no_coords = {"name": "Test Restaurant"}
        lat, lng = extract_coordinates(data_no_coords)
        assert lat is None
        assert lng is None
    
    def test_is_manhattan_neighborhood(self):
        """Test Manhattan neighborhood detection."""
        assert is_manhattan_neighborhood("SoHo") is True
        assert is_manhattan_neighborhood("Upper East Side") is True
        assert is_manhattan_neighborhood("Brooklyn") is False
        assert is_manhattan_neighborhood("") is False
        assert is_manhattan_neighborhood(None) is False
    
    def test_group_by_neighborhood(self):
        """Test neighborhood grouping."""
        restaurants = [
            {"name": "Restaurant 1", "hood": "SoHo"},
            {"name": "Restaurant 2", "hood": "SoHo"},
            {"name": "Restaurant 3", "hood": "Upper East Side"}
        ]
        
        groups = group_by_neighborhood(restaurants)
        
        assert "SoHo" in groups
        assert "Upper East Side" in groups
        assert len(groups["SoHo"]) == 2
        assert len(groups["Upper East Side"]) == 1
    
    def test_filter_manhattan_restaurants(self):
        """Test Manhattan restaurant filtering."""
        restaurants = [
            {"name": "Restaurant 1", "hood": "SoHo"},
            {"name": "Restaurant 2", "hood": "Brooklyn"},
            {"name": "Restaurant 3", "hood": "Upper East Side"}
        ]
        
        manhattan_restaurants = filter_manhattan_restaurants(restaurants)
        
        assert len(manhattan_restaurants) == 2
        assert all(r["hood"] in ["SoHo", "Upper East Side"] for r in manhattan_restaurants)
    
    def test_deduplicate_restaurants(self):
        """Test restaurant deduplication."""
        restaurants = [
            {"name": "Restaurant 1", "hood": "SoHo"},
            {"name": "Restaurant 1", "hood": "SoHo"},  # Duplicate
            {"name": "Restaurant 2", "hood": "Upper East Side"},
            {"name": "restaurant 1", "hood": "SoHo"}  # Case-insensitive duplicate
        ]
        
        unique_restaurants = deduplicate_restaurants(restaurants)
        
        assert len(unique_restaurants) == 2
        names = [r["name"].lower() for r in unique_restaurants]
        assert "restaurant 1" in names
        assert "restaurant 2" in names
