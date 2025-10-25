from requests_html import HTMLSession
import json
import re
from collections import defaultdict
import time

def scrape_with_requests_html():
    # Create an HTML session
    session = HTMLSession()
    
    # Navigate to the website
    print("Fetching the website...")
    r = session.get("https://looksmapping.com")
    
    # Render the JavaScript (this is what makes it different from regular requests)
    print("Rendering JavaScript (this may take a minute)...")
    r.html.render(sleep=5, timeout=30)  # Increase timeout if needed
    
    # Find all restaurant elements
    print("Finding restaurant elements...")
    restaurant_elements = r.html.find("div[onclick*='flyToLocation']")
    print(f"Found {len(restaurant_elements)} restaurant elements")
    
    # Extract data from each restaurant element
    restaurants = []
    for element in restaurant_elements:
        try:
            onclick = element.attrs.get("onclick", "")
            if onclick and "flyToLocation" in onclick:
                # Extract the restaurant data from the onclick attribute
                match = re.search(r'flyToLocation\(([^,]+),\s*([^,]+),\s*({.+?})\)', onclick)
                if match:
                    lng = float(match.group(1))
                    lat = float(match.group(2))
                    json_str = match.group(3)
                    # Replace &quot; with actual quotes
                    json_str = json_str.replace("&quot;", "\"")
                    data = json.loads(json_str)
                    
                    # Add coordinates
                    data["long"] = lng
                    data["lat"] = lat
                    
                    # Try to get name and neighborhood if not in the JSON
                    if "name" not in data:
                        name_element = element.find(".result-name", first=True)
                        if name_element:
                            data["name"] = name_element.text
                    
                    if "hood" not in data:
                        hood_element = element.find(".result-hood", first=True)
                        if hood_element:
                            data["hood"] = hood_element.text
                    
                    restaurants.append(data)
        except Exception as e:
            print(f"Error extracting data from element: {e}")
    
    print(f"Successfully extracted data for {len(restaurants)} restaurants")
    
    # Save the data
    with open("restaurant_data.json", "w") as f:
        json.dump(restaurants, f, indent=2)
    
    print("Data saved to restaurant_data.json")
    
    # Group restaurants by neighborhood
    by_hood = defaultdict(list)
    for r in restaurants:
        hood = r.get("hood", "Unknown")
        by_hood[hood].append(r)
    
    print("\nNeighborhoods found:")
    for hood, places in sorted(by_hood.items()):
        print(f"  {hood}: {len(places)} restaurants")
    
    # Also save the full HTML for reference
    with open("looksmapping_complete.html", "w", encoding="utf-8") as f:
        f.write(r.html.html)
    
    print("Complete HTML saved to looksmapping_complete.html")

if __name__ == "__main__":
    scrape_with_requests_html() 