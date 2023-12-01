# Usage Examples

This document provides practical examples of using the LooksMapping Scraper.

## Basic Usage

### Simple HTTP Scraping

```python
from scrapers import HttpScraper
from utils.config import load_config

# Load configuration
config = load_config()

# Create scraper
scraper = HttpScraper(config)

# Scrape data
restaurants = scraper.scrape()

# Save results
scraper.save_data(restaurants, "restaurants.json")
print(f"Scraped {len(restaurants)} restaurants")
```

### Selenium Scraping with Custom Options

```python
from scrapers import SeleniumScraper
from utils.config import Config

# Create custom configuration
config = Config()
config.scraper_headless = False  # Show browser
config.scraper_timeout = 60     # Increase timeout

# Create scraper
scraper = SeleniumScraper(config)

# Check availability
if scraper.is_available():
    restaurants = scraper.scrape()
    print(f"Found {len(restaurants)} restaurants")
else:
    print("Selenium scraper not available")
```

### Playwright Scraping with Map Interaction

```python
from scrapers import PlaywrightScraper
import asyncio

async def scrape_with_playwright():
    scraper = PlaywrightScraper()
    
    if scraper.is_available():
        restaurants = scraper.scrape()
        return restaurants
    else:
        print("Playwright not available")
        return []

# Run async scraping
restaurants = asyncio.run(scrape_with_playwright())
```

## Data Analysis

### Basic Neighborhood Analysis

```python
from analyzers import NeighborhoodAnalyzer
from utils.config import load_config

# Load configuration
config = load_config()

# Create analyzer
analyzer = NeighborhoodAnalyzer(config)

# Load restaurant data
restaurants = analyzer.load_restaurant_data("restaurant_data.json")

# Analyze neighborhoods
df = analyzer.analyze_neighborhoods(restaurants)

# Get top neighborhoods by attractiveness
top_neighborhoods = analyzer.get_top_neighborhoods(df, "avg_attractive", 5)
print("Top 5 neighborhoods by attractiveness:")
print(top_neighborhoods[["neighborhood", "avg_attractive", "restaurant_count"]])
```

### Advanced Analysis with Statistics

```python
from analyzers import NeighborhoodAnalyzer
import pandas as pd

analyzer = NeighborhoodAnalyzer()

# Load and analyze data
restaurants = analyzer.load_restaurant_data("data.json")
df = analyzer.analyze_neighborhoods(restaurants)

# Generate summary statistics
summary = analyzer.generate_summary_statistics(df)
print("Dataset Summary:")
for key, value in summary.items():
    print(f"{key}: {value}")

# Calculate correlation matrix
correlation_matrix = analyzer.calculate_correlation_matrix(df)
print("\nCorrelation Matrix:")
print(correlation_matrix)

# Create visualization data
viz_data = analyzer.create_visualization_data(df)
print(f"\nVisualization data for {len(viz_data['neighborhoods'])} neighborhoods")
```

## Data Processing

### Cleaning and Validating Data

```python
from utils.helpers import (
    clean_restaurant_data,
    validate_restaurant_data,
    deduplicate_restaurants,
    filter_manhattan_restaurants
)

# Raw restaurant data
raw_restaurants = [
    {"name": "  Test Restaurant  ", "hood": "  SoHo  ", "attractive_score": "8.5"},
    {"name": "Another Restaurant", "hood": "Brooklyn", "attractive_score": "7.2"},
    {"name": "Test Restaurant", "hood": "SoHo", "attractive_score": "8.5"}  # Duplicate
]

# Clean data
cleaned_restaurants = [clean_restaurant_data(r) for r in raw_restaurants]

# Validate data
valid_restaurants = [r for r in cleaned_restaurants if validate_restaurant_data(r)]

# Filter Manhattan restaurants
manhattan_restaurants = filter_manhattan_restaurants(valid_restaurants)

# Remove duplicates
unique_restaurants = deduplicate_restaurants(manhattan_restaurants)

print(f"Processed {len(unique_restaurants)} unique Manhattan restaurants")
```

### Working with Restaurant Models

```python
from models import Restaurant, RestaurantData

# Create restaurant data
restaurant_data = RestaurantData(
    name="Test Restaurant",
    hood="SoHo",
    attractive_score=8.5,
    age_score=7.2,
    gender_score=6.8
)

# Create restaurant instance
restaurant = Restaurant(restaurant_data)

# Check properties
print(f"Name: {restaurant.name}")
print(f"Neighborhood: {restaurant.neighborhood}")
print(f"Attractiveness: {restaurant.attractiveness_rating}")

# Check if in Manhattan
if restaurant.is_manhattan():
    print("Restaurant is in Manhattan")

# Check if has complete scores
if restaurant.has_complete_scores():
    print("Restaurant has all demographic scores")

# Get demographic summary
summary = restaurant.get_demographic_summary()
print("Demographic Summary:")
for key, value in summary.items():
    print(f"  {key}: {value}")
```

## Configuration Management

### Custom Configuration

```python
from utils.config import Config
import os

# Set environment variables
os.environ["SCRAPER_HEADLESS"] = "false"
os.environ["SCRAPER_TIMEOUT"] = "60"
os.environ["BROWSER_WIDTH"] = "1920"
os.environ["BROWSER_HEIGHT"] = "1080"

# Load configuration
config = Config()

# Access configuration values
print(f"Headless mode: {config.scraper_headless}")
print(f"Timeout: {config.scraper_timeout}")
print(f"Browser size: {config.browser_width}x{config.browser_height}")

# Get browser options
browser_options = config.get_browser_options()
print(f"Browser options: {browser_options}")
```

### Configuration from File

```python
from utils.config import load_config

# Load from specific config file
config = load_config("custom.env")

# Access configuration
print(f"Data output directory: {config.data_output_dir}")
print(f"Log level: {config.log_level}")
```

## Error Handling

### Robust Scraping with Fallbacks

```python
from scrapers import HttpScraper, SeleniumScraper, PlaywrightScraper
from scrapers.base import ScrapingError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def scrape_with_fallbacks():
    """Try different scrapers in order of preference."""
    scrapers = [
        ("HTTP", HttpScraper()),
        ("Selenium", SeleniumScraper()),
        ("Playwright", PlaywrightScraper())
    ]
    
    for name, scraper in scrapers:
        try:
            if scraper.is_available():
                print(f"Trying {name} scraper...")
                restaurants = scraper.scrape()
                print(f"{name} scraper succeeded with {len(restaurants)} restaurants")
                return restaurants
            else:
                print(f"{name} scraper not available")
        except ScrapingError as e:
            print(f"{name} scraper failed: {e}")
            continue
        except Exception as e:
            print(f"{name} scraper error: {e}")
            continue
    
    print("All scrapers failed")
    return []

# Run scraping with fallbacks
restaurants = scrape_with_fallbacks()
```

### Data Validation and Error Recovery

```python
from utils.helpers import validate_restaurant_data, clean_restaurant_data
import json

def process_restaurant_data(raw_data):
    """Process and validate restaurant data."""
    processed_data = []
    errors = []
    
    for i, restaurant in enumerate(raw_data):
        try:
            # Clean the data
            cleaned = clean_restaurant_data(restaurant)
            
            # Validate the data
            if validate_restaurant_data(cleaned):
                processed_data.append(cleaned)
            else:
                errors.append(f"Invalid data at index {i}: {restaurant}")
        except Exception as e:
            errors.append(f"Error processing index {i}: {e}")
    
    if errors:
        print(f"Found {len(errors)} errors:")
        for error in errors:
            print(f"  - {error}")
    
    return processed_data

# Example usage
raw_restaurants = [
    {"name": "Valid Restaurant", "hood": "SoHo", "attractive_score": 8.5},
    {"name": "", "hood": "SoHo"},  # Invalid: empty name
    {"name": "Another Restaurant", "attractive_score": "invalid"}  # Invalid: non-numeric score
]

processed = process_restaurant_data(raw_restaurants)
print(f"Processed {len(processed)} valid restaurants")
```

## Command Line Usage

### Scraping Examples

```bash
# Basic HTTP scraping
python scripts/scrape.py --method http

# Selenium scraping with custom options
python scripts/scrape.py --method selenium --headless --timeout 60

# Playwright scraping with output file
python scripts/scrape.py --method playwright --output data/restaurants.json

# Scraping with deduplication
python scripts/scrape.py --method http --deduplicate --format json
```

### Analysis Examples

```bash
# Basic analysis
python scripts/analyze.py --input restaurant_data.json

# Top neighborhoods by attractiveness
python scripts/analyze.py --input data.json --top 5 --metric avg_attractive

# Analysis with correlation and summary
python scripts/analyze.py --input data.json --correlation --summary

# Save analysis results
python scripts/analyze.py --input data.json --output analysis.json --format json
```

### Development and Testing

```bash
# Run tests
make test

# Format code
make format

# Run linting
make lint

# Type checking
make type-check

# Complete development setup
make dev-setup
```

## Integration Examples

### Flask Web Application

```python
from flask import Flask, jsonify, request
from scrapers import HttpScraper
from analyzers import NeighborhoodAnalyzer

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape_restaurants():
    """Scrape restaurant data via API."""
    try:
        scraper = HttpScraper()
        restaurants = scraper.scrape()
        return jsonify({"success": True, "count": len(restaurants), "data": restaurants})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze_neighborhoods():
    """Analyze neighborhood data via API."""
    try:
        data = request.json
        analyzer = NeighborhoodAnalyzer()
        df = analyzer.analyze_neighborhoods(data['restaurants'])
        return jsonify({"success": True, "analysis": df.to_dict('records')})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

### Scheduled Scraping

```python
import schedule
import time
from scrapers import HttpScraper
from datetime import datetime

def daily_scrape():
    """Perform daily scraping."""
    print(f"Starting daily scrape at {datetime.now()}")
    
    scraper = HttpScraper()
    restaurants = scraper.scrape()
    
    # Save with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"restaurants_{timestamp}.json"
    scraper.save_data(restaurants, filename)
    
    print(f"Daily scrape completed: {len(restaurants)} restaurants saved to {filename}")

# Schedule daily scraping at 6 AM
schedule.every().day.at("06:00").do(daily_scrape)

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(60)
```
