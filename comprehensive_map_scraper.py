import asyncio
from playwright.async_api import async_playwright
import json
import re
from collections import defaultdict
import time
import random

async def scrape_looksmapping():
    print("Starting comprehensive scraping process...")
    
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
        
        # Function to process visible markers
        async def process_visible_markers():
            nonlocal all_restaurants, restaurant_names
            
            markers = await page.query_selector_all(".mapboxgl-marker")
            print(f"Found {len(markers)} visible markers")
            
            for i, marker in enumerate(markers):
                try:
                    print(f"Clicking on marker {i+1}/{len(markers)}")
                    
                    # Scroll to the marker if needed
                    await marker.scroll_into_view_if_needed()
                    await page.wait_for_timeout(300)
                    
                    # Click the marker
                    await marker.click()
                    await page.wait_for_timeout(1000)  # Wait for popup to appear
                    
                    # Extract data from popup
                    restaurant = await extract_popup_data()
                    
                    if restaurant and restaurant["name"] not in restaurant_names:
                        all_restaurants.append(restaurant)
                        restaurant_names.add(restaurant["name"])
                        print(f"Added new restaurant: {restaurant['name']}")
                except Exception as e:
                    print(f"Error processing marker {i+1}: {e}")
                    continue
        
        # Process restaurants in different modes
        modes = ["hot", "age", "gender"]
        
        for mode in modes:
            try:
                print(f"\nSwitching to {mode.upper()} mode...")
                mode_button = await page.query_selector(f".mode-button[data-mode='{mode}']")
                if mode_button:
                    await mode_button.click()
                    await page.wait_for_timeout(3000)  # Wait for mode to change
                
                # Process initial markers
                await process_visible_markers()
                
                # Pan around the map to different areas of Manhattan
                print(f"\nPanning around the map in {mode.upper()} mode...")
                
                # Define several points to pan to (covering different Manhattan neighborhoods)
                pan_points = [
                    {"x": 400, "y": 300},   # Center
                    {"x": 200, "y": 200},   # Upper West
                    {"x": 600, "y": 200},   # Upper East
                    {"x": 200, "y": 400},   # Lower West
                    {"x": 600, "y": 400},   # Lower East
                    {"x": 400, "y": 100},   # Upper
                    {"x": 400, "y": 500}    # Lower
                ]
                
                for point in pan_points:
                    print(f"Panning to new area: x={point['x']}, y={point['y']}")
                    
                    # Click and drag on the map to pan
                    map_canvas = await page.query_selector(".mapboxgl-canvas")
                    if map_canvas:
                        # Start from center
                        center_x = 400
                        center_y = 300
                        
                        # Calculate drag distance
                        drag_x = center_x - point["x"]
                        drag_y = center_y - point["y"]
                        
                        # Perform the drag
                        await page.mouse.move(center_x, center_y)
                        await page.mouse.down()
                        await page.mouse.move(center_x + drag_x, center_y + drag_y, steps=10)
                        await page.mouse.up()
                        
                        # Wait for map to settle
                        await page.wait_for_timeout(2000)
                        
                        # Process markers in this area
                        await process_visible_markers()
                
                # Try different zoom levels
                print(f"\nTrying different zoom levels in {mode.upper()} mode...")
                zoom_levels = [2, 1, 0, -1]  # Relative zoom levels
                
                for zoom in zoom_levels:
                    print(f"Changing zoom level: {zoom}")
                    
                    # Use mouse wheel to zoom
                    map_canvas = await page.query_selector(".mapboxgl-canvas")
                    if map_canvas:
                        # Get the center of the map
                        bounds = await map_canvas.bounding_box()
                        center_x = bounds["x"] + bounds["width"] / 2
                        center_y = bounds["y"] + bounds["height"] / 2
                        
                        # Zoom in or out
                        delta = -100 if zoom > 0 else 100  # Negative delta zooms in, positive zooms out
                        for _ in range(abs(zoom)):
                            await page.mouse.move(center_x, center_y)
                            await page.mouse.wheel(0, delta)
                            await page.wait_for_timeout(1000)  # Wait for zoom to complete
                        
                        # Process markers at this zoom level
                        await process_visible_markers()
                
                print(f"Completed processing in {mode.upper()} mode. Total restaurants so far: {len(all_restaurants)}")
                
            except Exception as e:
                print(f"Error processing {mode} mode: {e}")
        
        # Save the data
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