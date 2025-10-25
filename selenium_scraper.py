from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import re
from collections import defaultdict

def scrape_with_selenium():
    # Set up Chrome options
    chrome_options = Options()
    # Uncomment the line below if you want to run headless
    # chrome_options.add_argument("--headless")
    
    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to the website
        driver.get("https://looksmapping.com")
        
        # Wait for the page to fully load
        print("Waiting for page to load...")
        time.sleep(5)  # Initial wait
        
        # Select New York if it's not already selected
        try:
            ny_link = driver.find_element(By.XPATH, "//span[contains(text(), 'New York')]")
            if "city-active" not in ny_link.get_attribute("class"):
                print("Clicking on New York...")
                ny_link.click()
                time.sleep(3)  # Wait for the city to load
        except Exception as e:
            print(f"Error selecting New York: {e}")
        
        # Wait for restaurant elements to appear
        print("Waiting for restaurant elements...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[onclick*='flyToLocation']"))
        )
        
        # Get all restaurant elements
        print("Finding restaurant elements...")
        restaurant_elements = driver.find_elements(By.CSS_SELECTOR, "div[onclick*='flyToLocation']")
        print(f"Found {len(restaurant_elements)} restaurant elements")
        
        # Extract data from each restaurant element
        restaurants = []
        for element in restaurant_elements:
            try:
                onclick = element.get_attribute("onclick")
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
                            try:
                                name_element = element.find_element(By.CSS_SELECTOR, ".result-name")
                                data["name"] = name_element.text
                            except:
                                pass
                        
                        if "hood" not in data:
                            try:
                                hood_element = element.find_element(By.CSS_SELECTOR, ".result-hood")
                                data["hood"] = hood_element.text
                            except:
                                pass
                        
                        restaurants.append(data)
            except Exception as e:
                print(f"Error extracting data from element: {e}")
        
        print(f"Successfully extracted data for {len(restaurants)} restaurants")
        
        # Try to get more data by clicking on different modes
        modes = ["hot", "age", "gender"]
        for mode in modes:
            try:
                print(f"Switching to {mode} mode...")
                mode_button = driver.find_element(By.CSS_SELECTOR, f".mode-button[data-mode='{mode}']")
                mode_button.click()
                time.sleep(2)  # Wait for the mode to change
                
                # Get new restaurant elements
                new_elements = driver.find_elements(By.CSS_SELECTOR, "div[onclick*='flyToLocation']")
                print(f"Found {len(new_elements)} restaurant elements in {mode} mode")
                
                # Extract data from new elements
                existing_names = {r.get("name") for r in restaurants if "name" in r}
                for element in new_elements:
                    try:
                        onclick = element.get_attribute("onclick")
                        if onclick and "flyToLocation" in onclick:
                            match = re.search(r'flyToLocation\(([^,]+),\s*([^,]+),\s*({.+?})\)', onclick)
                            if match:
                                lng = float(match.group(1))
                                lat = float(match.group(2))
                                json_str = match.group(3)
                                json_str = json_str.replace("&quot;", "\"")
                                data = json.loads(json_str)
                                
                                # Add coordinates
                                data["long"] = lng
                                data["lat"] = lat
                                
                                # Try to get name and neighborhood if not in the JSON
                                if "name" not in data:
                                    try:
                                        name_element = element.find_element(By.CSS_SELECTOR, ".result-name")
                                        data["name"] = name_element.text
                                    except:
                                        pass
                                
                                if "hood" not in data:
                                    try:
                                        hood_element = element.find_element(By.CSS_SELECTOR, ".result-hood")
                                        data["hood"] = hood_element.text
                                    except:
                                        pass
                                
                                # Only add if it's a new restaurant
                                if "name" in data and data["name"] not in existing_names:
                                    restaurants.append(data)
                                    existing_names.add(data["name"])
                    except Exception as e:
                        print(f"Error extracting data from element in {mode} mode: {e}")
            except Exception as e:
                print(f"Error switching to {mode} mode: {e}")
        
        print(f"Total unique restaurants found: {len(restaurants)}")
        
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
            f.write(driver.page_source)
        
        print("Complete HTML saved to looksmapping_complete.html")
        
    finally:
        # Close the driver
        driver.quit()

if __name__ == "__main__":
    scrape_with_selenium()
