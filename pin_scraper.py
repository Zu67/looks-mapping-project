import asyncio
from playwright.async_api import async_playwright
import json
import re
from collections import defaultdict
import time

async def scrape_looksmapping():
    print("Starting pin scraping process...")
    
    async with async_playwright() as p:
        # Launch the browser
        print("Launching browser...")
        browser = await p.chromium.launch(headless=False)
        
        # Create a new context and page
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()
        
        # Navigate to the website
        print("Navigating to LooksMapping website...")
        await page.goto("https://looksmapping.com")
        print("Page loaded!")
        
        # Wait for the page to load
        print("Waiting for page to fully load...")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(5000)  # 5 seconds
        
        # Make sure New York is selected
        print("Making sure New York is selected...")
        try:
            ny_button = await page.query_selector("text=New York")
            if ny_button:
                class_attr = await ny_button.get_attribute("class")
                if "city-active" not in class_attr:
                    print("Clicking on New York...")
                    await ny_button.click()
                    await page.wait_for_timeout(3000)  # 3 seconds
        except Exception as e:
            print(f"Error selecting New York: {e}")
        
        # Wait for the map to load
        print("Waiting for map to load...")
        await page.wait_for_selector(".mapboxgl-canvas", timeout=30000)
        print("Map loaded!")
        
        # Initialize restaurant collection
        all_restaurants = []
        restaurant_names = set()  # To track unique restaurants
        
        # Function to extract data from a popup
        async def extract_popup_data():
            popup = await page.query_selector(".mapboxgl-popup")
            if not popup:
                return None
            
            try:
                # Extract restaurant data from popup
                name_element = await popup.query_selector("strong")
                cuisine_element = await popup.query_selector(".popup-info")
                score_element = await popup.query_selector(".popup-score")
                reviewers_element = await popup.query_selector("div[style*='text-align: center']")
                
                # Extract metric indicators
                metric_indicators = await popup.query_selector_all(".metric-indicator")
                
                name = await name_element.text_content() if name_element else "Unknown"
                cuisine = await cuisine_element.text_content() if cuisine_element else "Unknown"
                score_text = await score_element.text_content() if score_element else "0/10"
                reviewers_text = await reviewers_element.text_content() if reviewers_element else "0 reviewers"
                
                # Extract score
                score_match = re.search(r'(\d+(\.\d+)?)/10', score_text)
                score = score_match.group(1) if score_match else "0"
                
                # Extract metrics
                attractive_score = "0"
                age_score = "0"
                gender_score = "0"
                
                if len(metric_indicators) >= 3:
                    # Extract percentages from style attribute
                    for j, indicator in enumerate(metric_indicators[:3]):
                        style = await indicator.get_attribute("style")
                        percent_match = re.search(r'left:\s*(\d+)%', style)
                        if percent_match:
                            percent = int(percent_match.group(1))
                            # Convert percentage to score out of 10
                            metric_score = str(round(percent / 10, 1))
                            
                            if j == 0:
                                attractive_score = metric_score
                            elif j == 1:
                                age_score = metric_score
                            elif j == 2:
                                gender_score = metric_score
                
                # Extract neighborhood from the results list if available
                hood = "Unknown"
                hood_element = await page.query_selector(f".result-item:has-text('{name}') .result-hood")
                if hood_element:
                    hood = await hood_element.text_content()
                
                # Create restaurant object
                restaurant = {
                    "name": name,
                    "cuisine": cuisine,
                    "hood": hood,
                    "score": score,
                    "attractive_score": attractive_score,
                    "age_score": age_score,
                    "gender_score": gender_score,
                    "reviewers": reviewers_text
                }
                
                return restaurant
            except Exception as e:
                print(f"Error extracting popup data: {e}")
                return None
            finally:
                # Close the popup
                close_button = await popup.query_selector(".mapboxgl-popup-close-button")
                if close_button:
                    await close_button.click()
                    await page.wait_for_timeout(500)  # Wait for popup to close
        
        # Process restaurants in different modes
        modes = ["hot", "age", "gender"]
        
        for mode in modes:
            try:
                print(f"\nSwitching to {mode.upper()} mode...")
                mode_button = await page.query_selector(f".mode-button[data-mode='{mode}']")
                if mode_button:
                    await mode_button.click()
                    await page.wait_for_timeout(3000)  # Wait for mode to change
                
                # Find all the map pins - these are the actual markers we need to click
                print(f"Finding map pins in {mode.upper()} mode...")
                
                # The pins are likely SVG markers or divs with specific classes
                pin_selectors = [
                    ".mapboxgl-marker",
                    ".mapboxgl-marker svg",
                    ".mapboxgl-marker div",
                    "div[style*='background-image'][style*='marker']",
                    "div[style*='position: absolute'][style*='transform']"
                ]
                
                pins = []
                for selector in pin_selectors:
                    pins = await page.query_selector_all(selector)
                    if pins:
                        print(f"Found {len(pins)} pins with selector: {selector}")
                        break
                
                if not pins:
                    print(f"No pins found in {mode.upper()} mode with any selector")
                    continue
                
                print(f"Processing {len(pins)} pins in {mode.upper()} mode...")
                
                # Process pins in batches to avoid overwhelming the page
                batch_size = 50
                for i in range(0, len(pins), batch_size):
                    batch = pins[i:i+batch_size]
                    print(f"Processing batch {i//batch_size + 1}/{(len(pins) + batch_size - 1)//batch_size}")
                    
                    for j, pin in enumerate(batch):
                        try:
                            print(f"Clicking pin {i+j+1}/{len(pins)}")
                            
                            # Get pin position for scrolling
                            bounding_box = await pin.bounding_box()
                            if not bounding_box:
                                print("Could not get bounding box for pin, skipping")
                                continue
                            
                            # Scroll to the pin
                            await page.evaluate("""
                                (x, y) => {
                                    window.scrollTo(x, y);
                                }
                            """, bounding_box["x"], bounding_box["y"])
                            await page.wait_for_timeout(300)
                            
                            # Click the pin
                            await pin.click()
                            await page.wait_for_timeout(1000)  # Wait for popup to appear
                            
                            # Extract data from popup
                            restaurant = await extract_popup_data()
                            
                            if restaurant and restaurant["name"] not in restaurant_names:
                                all_restaurants.append(restaurant)
                                restaurant_names.add(restaurant["name"])
                                print(f"Added new restaurant: {restaurant['name']}")
                                
                                # Save progress after every 10 new restaurants
                                if len(all_restaurants) % 10 == 0:
                                    with open("restaurant_data_progress.json", "w") as f:
                                        json.dump(all_restaurants, f, indent=2)
                                    print(f"Progress saved: {len(all_restaurants)} restaurants")
                        except Exception as e:
                            print(f"Error processing pin {i+j+1}: {e}")
                            continue
                    
                    # Save progress after each batch
                    with open("restaurant_data_progress.json", "w") as f:
                        json.dump(all_restaurants, f, indent=2)
                    print(f"Batch complete. Total restaurants so far: {len(all_restaurants)}")
                
                print(f"Completed processing in {mode.upper()} mode. Total restaurants: {len(all_restaurants)}")
                
            except Exception as e:
                print(f"Error processing {mode} mode: {e}")
        
        # Save the final data
        if all_restaurants:
            with open("restaurant_data.json", "w") as f:
                json.dump(all_restaurants, f, indent=2)
            
            print(f"\nSaved {len(all_restaurants)} restaurants to restaurant_data.json")
            
            # Group restaurants by neighborhood
            by_hood = defaultdict(list)
            for r in all_restaurants:
                hood = r.get("hood", "Unknown")
                by_hood[hood].append(r)
            
            print("\nNeighborhoods found:")
            for hood, places in sorted(by_hood.items()):
                print(f"  {hood}: {len(places)} restaurants")
        else:
            print("No restaurants found")
        
        # Close the browser
        print("Closing browser...")
        await browser.close()
        print("Browser closed")

if __name__ == "__main__":
    print("Script started")
    # Check if we have playwright installed
    try:
        import playwright
        print("Playwright is installed. Starting scraper...")
    except ImportError:
        print("Playwright is not installed. Please install it with: pip install playwright")
        print("Then run: playwright install")
        exit(1)
    
    # Run the scraper
    asyncio.run(scrape_looksmapping())
    print("Script completed") 