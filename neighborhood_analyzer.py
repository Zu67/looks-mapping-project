import json
from collections import defaultdict
import statistics
import pandas as pd

def analyze_manhattan_neighborhoods():
    # Load the data from the rankings object we found in the HTML
    # This is a simplified version - in reality, you'd extract this from the website
    # or use the data you've already scraped
    
    # For this example, I'll use the NY data from the rankings object
    with open('restaurant_data.json', 'r') as f:
        data = json.load(f)
    
    # Filter for Manhattan neighborhoods only
    # This is a list of Manhattan neighborhoods - you may need to adjust this
    manhattan_neighborhoods = [
        "Midtown East", "Midtown West", "Hell's Kitchen", "Chelsea", "Flatiron District",
        "Gramercy", "Murray Hill", "Kips Bay", "East Village", "West Village", "Greenwich Village",
        "SoHo", "NoHo", "Tribeca", "Financial District", "Lower East Side", "Chinatown",
        "Little Italy", "Upper East Side", "Upper West Side", "Harlem", "East Harlem",
        "Washington Heights", "Inwood", "NoMad", "Koreatown", "Nolita", "Battery Park City",
        "Morningside Heights", "Central Park South", "Theater District", "Garment District"
    ]
    
    # Create a dictionary to store restaurant data by neighborhood
    neighborhoods = defaultdict(list)
    
    # Process all restaurants
    for restaurant in data:
        hood = restaurant.get("hood")
        
        # Skip if no neighborhood or not in Manhattan
        if not hood or hood not in manhattan_neighborhoods:
            continue
            
        # Add restaurant data to the appropriate neighborhood
        neighborhoods[hood].append({
            "name": restaurant.get("name"),
            "attractive_score": float(restaurant.get("attractive_score", 0)),
            "age_score": float(restaurant.get("age_score", 0)),
            "gender_score": float(restaurant.get("gender_score", 0)),
            "category": restaurant.get("category", "Unknown")
        })
    
    # Calculate averages for each neighborhood
    neighborhood_stats = []
    
    for hood, restaurants in neighborhoods.items():
        if not restaurants:  # Skip empty neighborhoods
            continue
            
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
    
    # Create a DataFrame for easier analysis
    df = pd.DataFrame(neighborhood_stats)
    
    # Sort by different metrics
    hottest_neighborhoods = df.sort_values("avg_attractive", ascending=False)
    youngest_neighborhoods = df.sort_values("avg_age", ascending=False)
    most_female_neighborhoods = df.sort_values("avg_gender", ascending=True)  # Lower gender score = more female
    
    # Print the results
    print("\n=== MANHATTAN NEIGHBORHOODS RANKED BY ATTRACTIVENESS ===")
    print(hottest_neighborhoods[["neighborhood", "avg_attractive", "restaurant_count"]].to_string(index=False))
    
    print("\n=== MANHATTAN NEIGHBORHOODS RANKED BY YOUTH ===")
    print(youngest_neighborhoods[["neighborhood", "avg_age", "restaurant_count"]].to_string(index=False))
    
    print("\n=== MANHATTAN NEIGHBORHOODS RANKED BY FEMALE RATIO ===")
    print(most_female_neighborhoods[["neighborhood", "avg_gender", "restaurant_count"]].to_string(index=False))
    
    # Return the dataframe for further analysis if needed
    return df

def extract_restaurant_data():
    """
    This function would extract the restaurant data from the website or a file.
    For this example, we'll create a simplified version based on the data we saw.
    """
    # In a real implementation, you would:
    # 1. Parse the HTML to extract the 'rankings' JavaScript object
    # 2. Convert it to a Python data structure
    # 3. Extract all restaurant data
    
    # For now, we'll create a placeholder that you would replace with actual data
    restaurants = []
    
    # Here you would add code to extract all restaurants from the NY data
    # For example, by parsing the HTML and extracting the 'rankings.ny' object
    
    # Save to a JSON file for later use
    with open('restaurant_data.json', 'w') as f:
        json.dump(restaurants, f)
    
    return restaurants

if __name__ == "__main__":
    # First extract the data (you'd only need to do this once)
    # extract_restaurant_data()
    
    # Then analyze the neighborhoods
    analyze_manhattan_neighborhoods() 