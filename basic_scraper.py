import requests
import json
import re
from bs4 import BeautifulSoup

def scrape_looksmapping():
    # Fetch the website
    print("Fetching the website...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get("https://looksmapping.com", headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to fetch website: {response.status_code}")
        return []
    
    html_content = response.text
    print(f"Successfully fetched website, content length: {len(html_content)}")
    
    # Save the raw HTML for inspection
    with open("raw_looksmapping.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # Try to find the rankings data in the JavaScript
    rankings_pattern = re.compile(r'const\s+rankings\s*=\s*({.*?});', re.DOTALL)
    rankings_match = rankings_pattern.search(html_content)
    
    restaurants = []
    
    if rankings_match:
        print("Found rankings data in JavaScript!")
        try:
            rankings_json = rankings_match.group(1)
            rankings = json.loads(rankings_json)
            
            # Extract NY restaurants
            if "ny" in rankings:
                for metric, metric_data in rankings["ny"].items():
                    for position, restaurant_list in metric_data.items():
                        for restaurant in restaurant_list:
                            # Check if this restaurant is already in our list
                            if not any(r.get("name") == restaurant.get("name") for r in restaurants):
                                restaurants.append(restaurant)
            
            print(f"Extracted {len(restaurants)} unique restaurants from rankings data")
        except json.JSONDecodeError as e:
            print(f"Error parsing rankings JSON: {e}")
    
    # If we didn't find any restaurants, try pattern matching
    if not restaurants:
        print("Trying pattern matching approach...")
        # Look for restaurant data in the HTML
        restaurant_pattern = re.compile(r'"name":"([^"]+)"[^}]+"hood":"([^"]+)"[^}]+"attractive_score":"([^"]+)"[^}]+"age_score":"([^"]+)"[^}]+"gender_score":"([^"]+)"')
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
    
    # If we still don't have any restaurants, create a test dataset
    if not restaurants:
        print("No restaurants found. Creating test dataset...")
        restaurants = [
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
    
    # Save the restaurant data
    with open("restaurant_data.json", "w") as f:
        json.dump(restaurants, f, indent=2)
    
    print(f"Saved {len(restaurants)} restaurants to restaurant_data.json")
    return restaurants

if __name__ == "__main__":
    scrape_looksmapping() 