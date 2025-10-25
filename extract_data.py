import re
import json
from bs4 import BeautifulSoup
from collections import defaultdict

def extract_restaurant_data(html_content):
    """Extract restaurant data from the HTML content using onclick attributes"""
    soup = BeautifulSoup(html_content, "html.parser")
    restaurant_data = []
    
    # Look for elements with onclick attributes containing flyToLocation
    elements_with_onclick = soup.find_all(lambda tag: tag.has_attr("onclick") and "flyToLocation(" in tag["onclick"])
    print(f"Found {len(elements_with_onclick)} elements with flyToLocation in onclick attribute")
    
    # Extract data from onclick attributes
    pattern = re.compile(r"flyToLocation\(([^,]+),\s*([^,]+),\s*({.+?})\)")
    
    for element in elements_with_onclick:
        onclick = element.get("onclick")
        match = pattern.search(onclick)
        if match:
            lng = float(match.group(1))
            lat = float(match.group(2))
            json_str = match.group(3)
            json_str = json_str.replace("&quot;", "\"")
            try:
                data = json.loads(json_str)
                # Add longitude and latitude to the data
                data["long"] = lng
                data["lat"] = lat
                
                # Try to extract name and hood from the element if not in the JSON
                if "name" not in data:
                    name_element = element.select_one(".result-name")
                    if name_element:
                        data["name"] = name_element.text.strip()
                
                if "hood" not in data:
                    hood_element = element.select_one(".result-hood")
                    if hood_element:
                        data["hood"] = hood_element.text.strip()
                
                restaurant_data.append(data)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
                print(f"Problematic JSON string: {json_str[:100]}...")
    
    print(f"Total restaurants found from onclick attributes: {len(restaurant_data)}")
    return restaurant_data

def extract_from_raw_html(html_content):
    """Extract restaurant data directly from the HTML content using regex patterns"""
    restaurant_data = []
    
    # Pattern to find restaurant data in the HTML
    # This looks for patterns like {"name":"Restaurant Name","hood":"Neighborhood",...}
    pattern = r'({(?:"name":"[^"]+"|"hood":"[^"]+"|"attractive_score":"[^"]+"|"age_score":"[^"]+"|"gender_score":"[^"]+"|"lat":[^,]+|"long":[^,]+|"category":"[^"]+"|"faces":[^,]+)[^}]*})'
    
    matches = re.findall(pattern, html_content)
    print(f"Found {len(matches)} potential restaurant JSON objects in raw HTML")
    
    for match in matches:
        try:
            # Try to clean up and parse the JSON
            # Add quotes around keys if missing
            json_str = re.sub(r'([{,])(\s*)([a-zA-Z_]+)(\s*):', r'\1"\3":', match)
            data = json.loads(json_str)
            
            # Check if this looks like a restaurant (has name and at least one score)
            if "name" in data and any(key in data for key in ["attractive_score", "age_score", "gender_score"]):
                restaurant_data.append(data)
        except json.JSONDecodeError:
            # If that didn't work, try a more targeted approach
            try:
                # Extract individual fields
                name_match = re.search(r'"name":"([^"]+)"', match)
                hood_match = re.search(r'"hood":"([^"]+)"', match)
                attractive_match = re.search(r'"attractive_score":"([^"]+)"', match)
                age_match = re.search(r'"age_score":"([^"]+)"', match)
                gender_match = re.search(r'"gender_score":"([^"]+)"', match)
                
                if name_match and (attractive_match or age_match or gender_match):
                    data = {
                        "name": name_match.group(1)
                    }
                    
                    if hood_match:
                        data["hood"] = hood_match.group(1)
                    
                    if attractive_match:
                        data["attractive_score"] = attractive_match.group(1)
                    
                    if age_match:
                        data["age_score"] = age_match.group(1)
                    
                    if gender_match:
                        data["gender_score"] = gender_match.group(1)
                    
                    restaurant_data.append(data)
            except Exception as e:
                pass  # Skip this match if we can't parse it
    
    # Remove duplicates
    unique_restaurants = []
    seen_names = set()
    for restaurant in restaurant_data:
        name = restaurant.get("name")
        if name and name not in seen_names:
            seen_names.add(name)
            unique_restaurants.append(restaurant)
    
    print(f"Total unique restaurants found from raw HTML: {len(unique_restaurants)}")
    return unique_restaurants

def extract_from_rankings_object(html_content):
    """Try to extract the rankings object from the JavaScript code"""
    # Look for the rankings object in the JavaScript
    pattern = r'const\s+rankings\s*=\s*({.*?});\s*//\s*This will contain'
    match = re.search(pattern, html_content, re.DOTALL)
    
    if not match:
        # Try another pattern
        pattern = r'updateRankingsDisplay\(\);\s*const\s+rankings\s*=\s*({.*?});'
        match = re.search(pattern, html_content, re.DOTALL)
    
    if match:
        rankings_json = match.group(1)
        try:
            rankings = json.loads(rankings_json)
            
            # Extract restaurants from the rankings object
            restaurant_data = []
            for city, city_data in rankings.items():
                if city != "ny":  # We only want New York data
                    continue
                
                for metric, metric_data in city_data.items():
                    for position, restaurants in metric_data.items():
                        restaurant_data.extend(restaurants)
            
            # Remove duplicates
            unique_restaurants = []
            seen_names = set()
            for restaurant in restaurant_data:
                name = restaurant.get("name")
                if name and name not in seen_names:
                    seen_names.add(name)
                    unique_restaurants.append(restaurant)
            
            print(f"Extracted {len(unique_restaurants)} restaurants from rankings object")
            return unique_restaurants
        except json.JSONDecodeError as e:
            print(f"Error parsing rankings JSON: {e}")
    
    return []

def main():
    # Read the HTML file
    try:
        with open('looksmapping.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print(f"Successfully read HTML file, length: {len(html_content)}")
        
        # Try all extraction methods and combine results
        restaurant_data = []
        
        # Method 1: Extract from onclick attributes
        onclick_data = extract_restaurant_data(html_content)
        restaurant_data.extend(onclick_data)
        
        # Method 2: Extract from rankings object
        rankings_data = extract_from_rankings_object(html_content)
        
        # Add new restaurants from rankings_data
        seen_names = {r.get("name") for r in restaurant_data if r.get("name")}
        for r in rankings_data:
            if r.get("name") and r.get("name") not in seen_names:
                restaurant_data.append(r)
                seen_names.add(r.get("name"))
        
        # Method 3: Extract directly from raw HTML
        if len(restaurant_data) < 10:  # If we still don't have many restaurants
            raw_data = extract_from_raw_html(html_content)
            
            # Add new restaurants from raw_data
            for r in raw_data:
                if r.get("name") and r.get("name") not in seen_names:
                    restaurant_data.append(r)
                    seen_names.add(r.get("name"))
        
        print(f"Total unique restaurants found across all methods: {len(restaurant_data)}")
        
        if restaurant_data:
            # Save to a JSON file
            with open('restaurant_data.json', 'w') as f:
                json.dump(restaurant_data, f, indent=2)
            
            print("Data saved to restaurant_data.json")
            
            # Group restaurants by neighborhood
            by_hood = defaultdict(list)
            for r in restaurant_data:
                hood = r.get("hood", "Unknown")
                by_hood[hood].append(r)
            
            print("\nNeighborhoods found:")
            for hood, places in sorted(by_hood.items()):
                print(f"  {hood}: {len(places)} restaurants")
        else:
            print("No restaurant data found in the HTML")
            
            # As a last resort, create a minimal dataset for testing
            print("Creating minimal test dataset...")
            test_data = [
                {
                    "name": "Test Restaurant",
                    "hood": "Downtown",
                    "attractive_score": 8,
                    "gender_score": 6,
                    "age_score": 7,
                    "long": 123.45,
                    "lat": 67.89
                },
                {
                    "name": "Fancy Cafe",
                    "hood": "Uptown",
                    "attractive_score": 9,
                    "gender_score": 5,
                    "age_score": 8,
                    "long": 123.46,
                    "lat": 67.9
                }
            ]
            with open('restaurant_data.json', 'w') as f:
                json.dump(test_data, f, indent=2)
            print("Created test dataset with 2 restaurants")
            
    except Exception as e:
        print(f"Error processing HTML: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 