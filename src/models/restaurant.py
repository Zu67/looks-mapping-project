"""
Restaurant data models for LooksMapping Scraper.

This module defines the data structures used to represent restaurant information
extracted from LooksMapping.com.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import json


@dataclass
class RestaurantData:
    """
    Data class representing restaurant information from LooksMapping.com.
    
    This class encapsulates all the data fields that can be extracted
    from the website for a single restaurant.
    """
    
    # Basic Information
    name: str
    hood: Optional[str] = None
    cuisine: Optional[str] = None
    
    # Demographic Scores (0-10 scale)
    attractive_score: Optional[float] = None
    age_score: Optional[float] = None
    gender_score: Optional[float] = None
    
    # Additional Metrics
    score: Optional[str] = None
    reviewers: Optional[str] = None
    
    # Geographic Information
    lat: Optional[float] = None
    long: Optional[float] = None
    
    # Metadata
    source: str = "looksmapping.com"
    scraped_at: Optional[str] = None
    
    def __post_init__(self):
        """Validate and clean data after initialization."""
        if not self.name or not self.name.strip():
            raise ValueError("Restaurant name cannot be empty")
        
        # Clean string fields
        self.name = self.name.strip()
        if self.hood:
            self.hood = self.hood.strip()
        if self.cuisine:
            self.cuisine = self.cuisine.strip()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "hood": self.hood,
            "cuisine": self.cuisine,
            "attractive_score": self.attractive_score,
            "age_score": self.age_score,
            "gender_score": self.gender_score,
            "score": self.score,
            "reviewers": self.reviewers,
            "lat": self.lat,
            "long": self.long,
            "source": self.source,
            "scraped_at": self.scraped_at,
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RestaurantData":
        """Create instance from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> "RestaurantData":
        """Create instance from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


@dataclass
class Restaurant:
    """
    Enhanced restaurant class with additional functionality.
    
    This class extends RestaurantData with methods for analysis
    and comparison operations.
    """
    
    data: RestaurantData
    
    def __post_init__(self):
        """Initialize with RestaurantData if needed."""
        if not isinstance(self.data, RestaurantData):
            self.data = RestaurantData(**self.data) if isinstance(self.data, dict) else self.data
    
    @property
    def name(self) -> str:
        """Get restaurant name."""
        return self.data.name
    
    @property
    def neighborhood(self) -> Optional[str]:
        """Get neighborhood name."""
        return self.data.hood
    
    @property
    def attractiveness_rating(self) -> Optional[float]:
        """Get attractiveness score."""
        return self.data.attractive_score
    
    @property
    def age_demographic(self) -> Optional[float]:
        """Get age demographic score."""
        return self.data.age_score
    
    @property
    def gender_ratio(self) -> Optional[float]:
        """Get gender ratio score."""
        return self.data.gender_score
    
    def is_manhattan(self) -> bool:
        """Check if restaurant is in Manhattan."""
        if not self.data.hood:
            return False
        
        manhattan_neighborhoods = {
            "Midtown East", "Midtown West", "Hell's Kitchen", "Chelsea", 
            "Flatiron District", "Gramercy", "Murray Hill", "Kips Bay",
            "East Village", "West Village", "Greenwich Village", "SoHo", 
            "NoHo", "Tribeca", "Financial District", "Lower East Side",
            "Chinatown", "Little Italy", "Upper East Side", "Upper West Side",
            "Harlem", "East Harlem", "Washington Heights", "Inwood", "NoMad",
            "Koreatown", "Nolita", "Battery Park City", "Morningside Heights",
            "Central Park South", "Theater District", "Garment District"
        }
        
        return self.data.hood in manhattan_neighborhoods
    
    def has_complete_scores(self) -> bool:
        """Check if restaurant has all demographic scores."""
        return all([
            self.data.attractive_score is not None,
            self.data.age_score is not None,
            self.data.gender_score is not None
        ])
    
    def get_demographic_summary(self) -> Dict[str, Any]:
        """Get summary of demographic data."""
        return {
            "name": self.data.name,
            "neighborhood": self.data.hood,
            "attractiveness": self.data.attractive_score,
            "age_demographic": self.data.age_score,
            "gender_ratio": self.data.gender_score,
            "has_complete_data": self.has_complete_scores(),
            "is_manhattan": self.is_manhattan(),
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return self.data.to_dict()
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.data.to_json()
