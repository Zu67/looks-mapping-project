from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import re
import os
import sys

def setup_driver():
    """Set up and return a Chrome WebDriver with the correct version"""
    try:
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Use webdriver-manager to get the correct ChromeDriver version
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        sys.exit(1)

def extract_restaurant_data(driver, mode="hot"):
    """Extract restaurant data from the current page"""
    restaurants = []
    
    # Wait for restaurant elements to appear
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.result-item"))
        )
        
        # Get all restaurant elements
        restaurant_elements = driver.find_elements(By.CSS_SELECTOR, "div.result-item")
        print(f"Found {len(restaurant_elements)} restaurant elements in {mode} mode")
        
        # Extract data from each restaurant element
        for element in restaurant_elements:
            try:
                # Get restaurant name
                name_element = element.find_element(By.CSS_SELECTOR, ".result-name")
                name = name_element.text.strip()
                
                # Get neighborhood
                hood_element = element.find_element(By.CSS_SELECTOR, ".result-hood")
                hood = hood_element.text.strip()
                
                # Get scores
                scores_element = element.find_element(By.CSS_SELECTOR, ".result-scores")
                scores_text = scores_element.text
                
                # Parse scores
                attractive_score = "0"
                age_score = "0"
                gender_score = "0"
                
                # Extract scores using regex
                attractive_match = re.search(r'Hot:\s*(\d+(\.\d+)?)', scores_text)
                if attractive_match:
                    attractive_score = attractive_match.group(1)
                
                age_match = re.search(r'Age:\s*(\d+(\.\d+)?)', scores_text)
                if age_match:
                    age_score = age_match.group(1)
                
                gender_match = re.search(r'Gender:\s*(\d+(\.\d+)?)', scores_text)
                if gender_match:
                    gender_score = gender_match.group(1)
                
                # Create restaurant object
                restaurant = {
                    "name": name,
                    "hood": hood,
                    "attractive_score": attractive_score,
                    "age_score": age_score,
                    "gender_score": gender_score,
                    "mode": mode
                }
                
                restaurants.append(restaurant)
                
            except Exception as e:
                print(f"Error extracting data from restaurant element: {e}")
                continue
    
    except Exception as e:
        print(f"Error waiting for restaurant elements: {e}")
    
    return restaurants

def scrape_looksmapping():
    """Scrape restaurant data from LooksMapping website"""
    driver = None
    try:
        print("Setting up Chrome driver...")
        driver = setup_driver()
        
        print("Navigating to LooksMapping website...")
        driver.get("https://looksmapping.com")
        
        # Wait for the page to load
        time.sleep(5)
        
        # Make sure we're looking at New York data
        try:
            # Check if we need to select New York
            ny_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'New York')]"))
            )
            
            # Check if New York is already selected
            if "city-active" not in ny_button.get_attribute("class"):
                print("Clicking on New York...")
                ny_button.click()
                time.sleep(3)
        except Exception as e:
            print(f"Error selecting New York: {e}")
        
        # Extract data for each mode
        all_restaurants = []
        modes = ["hot", "age", "gender"]
        
        for mode in modes:
            try:
                print(f"Switching to {mode} mode...")
                mode_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, f".mode-button[data-mode='{mode}']"))
                )
                mode_button.click()
                time.sleep(3)
                
                # Extract restaurant data
                restaurants = extract_restaurant_data(driver, mode)
                
                # Add to our list, avoiding duplicates
                existing_names = {r["name"] for r in all_restaurants}
                for restaurant in restaurants:
                    if restaurant["name"] not in existing_names:
                        all_restaurants.append(restaurant)
                        existing_names.add(restaurant["name"])
                
                print(f"Total unique restaurants so far: {len(all_restaurants)}")
                
            except Exception as e:
                print(f"Error processing {mode} mode: {e}")
        
        # Save the data
        with open("restaurant_data.json", "w") as f:
            json.dump(all_restaurants, f, indent=2)
        
        print(f"Saved {len(all_restaurants)} restaurants to restaurant_data.json")
        
        # Save the page source for reference
        with open("looksmapping_complete.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        
        return all_restaurants
        
    except Exception as e:
        print(f"Error scraping LooksMapping: {e}")
        return []
        
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    # Check if we have selenium installed
    try:
        import selenium
        print("Selenium is installed. Starting scraper...")
    except ImportError:
        print("Selenium is not installed. Please install it with: pip install selenium webdriver-manager")
        sys.exit(1)
    
    # Run the scraper
    scrape_looksmapping() 