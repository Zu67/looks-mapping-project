# API Documentation

This document provides detailed API documentation for the LooksMapping Scraper.

## Core Classes

### BaseScraper

Abstract base class for all scrapers.

```python
from scrapers import BaseScraper

class MyScraper(BaseScraper):
    def scrape(self) -> List[Dict[str, Any]]:
        # Implementation
        pass
    
    def is_available(self) -> bool:
        # Check if scraper is available
        return True
```

### HttpScraper

HTTP-based scraper using requests and BeautifulSoup.

```python
from scrapers import HttpScraper
from utils.config import Config

config = Config()
scraper = HttpScraper(config)

# Check availability
if scraper.is_available():
    restaurants = scraper.scrape()
    scraper.save_data(restaurants, "output.json")
```

### SeleniumScraper

Selenium WebDriver-based scraper.

```python
from scrapers import SeleniumScraper

scraper = SeleniumScraper(config)

# Scrape with browser automation
restaurants = scraper.scrape()
```

### PlaywrightScraper

Playwright-based scraper with advanced automation.

```python
from scrapers import PlaywrightScraper

scraper = PlaywrightScraper(config)

# Comprehensive scraping with map interaction
restaurants = scraper.scrape()
```

## Analysis Classes

### NeighborhoodAnalyzer

Statistical analysis of neighborhood data.

```python
from analyzers import NeighborhoodAnalyzer

analyzer = NeighborhoodAnalyzer(config)

# Load and analyze data
restaurants = analyzer.load_restaurant_data("data.json")
df = analyzer.analyze_neighborhoods(restaurants)

# Get top neighborhoods
top_neighborhoods = analyzer.get_top_neighborhoods(df, "avg_attractive", 10)

# Generate summary statistics
summary = analyzer.generate_summary_statistics(df)
```

## Data Models

### RestaurantData

Data class representing restaurant information.

```python
from models import RestaurantData

# Create restaurant data
restaurant = RestaurantData(
    name="Test Restaurant",
    hood="SoHo",
    attractive_score=8.5,
    age_score=7.2,
    gender_score=6.8
)

# Convert to dictionary
data_dict = restaurant.to_dict()

# Convert to JSON
json_str = restaurant.to_json()
```

### Restaurant

Enhanced restaurant class with analysis methods.

```python
from models import Restaurant

restaurant = Restaurant(restaurant_data)

# Check if in Manhattan
if restaurant.is_manhattan():
    print("Restaurant is in Manhattan")

# Check if has complete scores
if restaurant.has_complete_scores():
    print("Restaurant has all demographic scores")

# Get demographic summary
summary = restaurant.get_demographic_summary()
```

## Utility Functions

### Configuration

```python
from utils.config import load_config

# Load configuration from environment
config = load_config()

# Access configuration values
timeout = config.scraper_timeout
headless = config.scraper_headless
```

### Helpers

```python
from utils.helpers import (
    clean_string,
    safe_float,
    validate_restaurant_data,
    is_manhattan_neighborhood,
    deduplicate_restaurants
)

# Clean string data
cleaned = clean_string("  Test Restaurant  ")

# Safe float conversion
score = safe_float("8.5", default=0.0)

# Validate restaurant data
is_valid = validate_restaurant_data(restaurant_dict)

# Check Manhattan neighborhood
is_manhattan = is_manhattan_neighborhood("SoHo")

# Remove duplicates
unique_restaurants = deduplicate_restaurants(restaurants)
```

## Error Handling

### ScrapingError

Custom exception for scraping failures.

```python
from scrapers.base import ScrapingError

try:
    restaurants = scraper.scrape()
except ScrapingError as e:
    print(f"Scraping failed: {e}")
```

## Examples

### Complete Scraping Workflow

```python
from scrapers import HttpScraper, SeleniumScraper, PlaywrightScraper
from analyzers import NeighborhoodAnalyzer
from utils.config import load_config

# Load configuration
config = load_config()

# Try different scrapers
scrapers = [
    HttpScraper(config),
    SeleniumScraper(config),
    PlaywrightScraper(config)
]

restaurants = []
for scraper in scrapers:
    if scraper.is_available():
        try:
            restaurants = scraper.scrape()
            break
        except Exception as e:
            print(f"Scraper {scraper.__class__.__name__} failed: {e}")
            continue

# Analyze data
if restaurants:
    analyzer = NeighborhoodAnalyzer(config)
    df = analyzer.analyze_neighborhoods(restaurants)
    
    # Save results
    analyzer.save_analysis(df, "analysis.json")
```

### Custom Scraper Implementation

```python
from scrapers.base import BaseScraper
from typing import List, Dict, Any

class CustomScraper(BaseScraper):
    def scrape(self) -> List[Dict[str, Any]]:
        # Custom scraping logic
        restaurants = []
        
        # Your scraping implementation here
        
        return self.validate_data(restaurants)
    
    def is_available(self) -> bool:
        # Check if your scraper is available
        return True
```
