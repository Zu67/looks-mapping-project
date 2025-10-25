import asyncio
from playwright.async_api import async_playwright
import json
import re
from collections import defaultdict
import time

async def scrape_looksmapping():
    print("Starting scraping process...")
    
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
        print("Page should be fully loaded now")
        
        # Take a screenshot of the initial page
        print("Taking initial screenshot...")
        await page.screenshot(path="looksmapping_initial.png")
        
        # Try to find and click on New York
        print("Looking for New York button...")
        try:
            # Try different selectors for the New York button
            selectors = [
                "text=New York",
                "span:has-text('New York')",
                ".city-selector span:has-text('New York')",
                "//span[contains(text(), 'New York')]"
            ]
            
            for selector in selectors:
                print(f"Trying to find New York button with selector: {selector}")
                ny_button = await page.query_selector(selector)
                if ny_button:
                    print("Found New York button!")
                    await ny_button.click()
                    print("Clicked New York button")
                    await page.wait_for_timeout(3000)  # 3 seconds
                    break
            else:
                print("Could not find New York button with any selector")
        except Exception as e:
            print(f"Error selecting New York: {e}")
        
        # Take another screenshot after selecting New York
        await page.screenshot(path="looksmapping_ny_selected.png")
        
        # Wait for the map to load
        print("Waiting for map to load...")
        await page.wait_for_selector(".mapboxgl-canvas", timeout=30000)
        print("Map loaded!")
        
        # Click on map markers to get restaurant data
        print("Looking for map markers...")
        
        # First, try to find markers on the map
        markers = await page.query_selector_all(".mapboxgl-marker")
        print(f"Found {len(markers)} map markers")
        
        all_restaurants = []
        
        if markers:
            print("Clicking on markers to get restaurant data...")
            for i, marker in enumerate(markers[:30]):  # Limit to first 30 markers to avoid taking too long
                try:
                    print(f"Clicking on marker {i+1}/{len(markers)}")
                    await marker.click()
                    await page.wait_for_timeout(1000)  # Wait for popup to appear
                    
                    # Check if popup appeared
                    popup = await page.query_selector(".mapboxgl-popup")
                    if popup:
                        print("Popup appeared!")
                        
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
                        
                        all_restaurants.append(restaurant)
                        print(f"Added restaurant: {name}")
                        
                        # Close the popup
                        close_button = await popup.query_selector(".mapboxgl-popup-close-button")
                        if close_button:
                            await close_button.click()
                            await page.wait_for_timeout(500)  # Wait for popup to close
                    else:
                        print("No popup appeared after clicking marker")
                
                except Exception as e:
                    print(f"Error processing marker {i+1}: {e}")
                    continue
        
        # If we didn't get any restaurants from markers, try to extract from the page source
        if not all_restaurants:
            print("No restaurants found from markers, trying to extract from page source...")
            content = await page.content()
            
            # Save the page source for inspection
            with open("looksmapping_source.html", "w", encoding="utf-8") as f:
                f.write(content)
            
            # Look for restaurant data in the JavaScript
            rankings_pattern = re.compile(r'const\s+rankings\s*=\s*({.*?});', re.DOTALL)
            rankings_match = rankings_pattern.search(content)
            
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
                                    if "name" in restaurant and not any(r.get("name") == restaurant["name"] for r in all_restaurants):
                                        all_restaurants.append(restaurant)
                    
                    print(f"Extracted {len(all_restaurants)} unique restaurants from rankings data")
                except json.JSONDecodeError as e:
                    print(f"Error parsing rankings JSON: {e}")
        
        # Save the data
        if all_restaurants:
            with open("restaurant_data.json", "w") as f:
                json.dump(all_restaurants, f, indent=2)
            
            print(f"Saved {len(all_restaurants)} restaurants to restaurant_data.json")
            
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
            
            # Create a minimal dataset for testing
            print("Creating minimal test dataset...")
            test_data = [
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
                }
            ]
            with open("restaurant_data.json", "w") as f:
                json.dump(test_data, f, indent=2)
            print("Created test dataset with 2 restaurants")
        
        # Wait a bit before closing
        print("Waiting 5 seconds before closing browser...")
        await page.wait_for_timeout(5000)
        
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