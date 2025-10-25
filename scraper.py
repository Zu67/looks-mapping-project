import requests
from bs4 import BeautifulSoup
import re
import json
from collections import defaultdict
import time

def scrape_looksmapping(city="New York"):
    print(f"Scraping Looksmapping data for {city}...")
    
    # URL of the website
    url = "https://looksmapping.com"
    
    # Send a request to the website
    print(f"Requesting {url}")
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to retrieve the website: Status code {response.status_code}")
        return
    
    print(f"Successfully retrieved website. Content length: {len(response.text)}")
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, "html.parser")
    
    # The data might be loaded dynamically with JavaScript
    # We need to look for JavaScript variables or API calls that contain the data
    
    # Look for script tags that might contain the data
    scripts = soup.find_all("script")
    print(f"Found {len(scripts)} script tags")
    
    # Try to find data in the page
    restaurant_data = []
    
    # Look for elements with onclick attributes containing flyToLocation
    elements_with_onclick = soup.find_all(lambda tag: tag.has_attr("onclick") and "flyToLocation(" in tag["onclick"])
    print(f"Found {len(elements_with_onclick)} elements with flyToLocation in onclick attribute")
    
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
                print(f"Extracted data: {data}")
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
                print(f"Problematic JSON string: {json_str}")
    
    print(f"Total restaurants found: {len(restaurant_data)}")
    
    # If we didn't find any data, the website might be using AJAX to load data
    if not restaurant_data:
        print("No data found in the HTML. The website might be loading data dynamically.")
        print("You might need to use a browser automation tool like Selenium to capture the data.")
        return
    
    # Group restaurants by neighborhood
    by_hood = defaultdict(list)
    for r in restaurant_data:
        hood = r.get("hood", "Unknown")
        by_hood[hood].append(r)
    
    # Print results
    for hood, places in by_hood.items():
        print(f"\nNeighborhood: {hood}")
        for p in places:
            name = p.get("name", "Unknown")
            hot = p.get("attractive_score", "N/A")
            gender = p.get("gender_score", "N/A")
            age = p.get("age_score", "N/A")
            print(f"  {name}: Hot {hot}, Gender {gender}, Age {age}")
        print("-" * 40)
    
    return by_hood

if __name__ == "__main__":
    # Try to scrape data for New York
    scrape_looksmapping("New York") 