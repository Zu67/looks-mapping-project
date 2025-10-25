import asyncio
from playwright.async_api import async_playwright
import json
import re
from collections import defaultdict
import time

async def scrape_looksmapping():
    print("Starting scraping process...")
    
    async with async_playwright() as p:
        # Launch the browser - explicitly set headless=False to see the browser
        print("Launching browser...")
        browser = await p.chromium.launch(headless=False)
        
        # Create a new context and page with larger viewport
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
        print("Screenshot saved to looksmapping_initial.png")
        
        # Print the title of the page to confirm we're on the right page
        title = await page.title()
        print(f"Page title: {title}")
        
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
        print("Screenshot saved to looksmapping_ny_selected.png")
        
        # Try to extract data from the page
        print("Extracting data from page...")
        
        # Look for restaurant elements
        print("Looking for restaurant elements...")
        selectors = [
            "div.result-item",
            ".result-list .result-item",
            "[onclick*='flyToLocation']",
            ".result-name"
        ]
        
        for selector in selectors:
            print(f"Trying selector: {selector}")
            elements = await page.query_selector_all(selector)
            if elements:
                print(f"Found {len(elements)} elements with selector {selector}")
                break
        else:
            print("Could not find any restaurant elements with any selector")
        
        # Try to extract data from the page source
        print("Extracting data from page source...")
        content = await page.content()
        print(f"Page source length: {len(content)}")
        
        # Save the page source for inspection
        with open("looksmapping_source.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("Page source saved to looksmapping_source.html")
        
        # Look for restaurant data in the JavaScript
        print("Looking for rankings data in JavaScript...")
        rankings_pattern = re.compile(r'const\s+rankings\s*=\s*({.*?});', re.DOTALL)
        rankings_match = rankings_pattern.search(content)
        
        all_restaurants = []
        
        if rankings_match:
            print("Found rankings data in JavaScript!")
            try:
                rankings_json = rankings_match.group(1)
                with open("rankings_data.json", "w") as f:
                    f.write(rankings_json)
                print("Rankings data saved to rankings_data.json")
                
                rankings = json.loads(rankings_json)
                
                # Extract NY restaurants
                if "ny" in rankings:
                    print("Found NY data in rankings!")
                    for metric, metric_data in rankings["ny"].items():
                        print(f"Processing metric: {metric}")
                        for position, restaurant_list in metric_data.items():
                            print(f"Position {position}: {len(restaurant_list)} restaurants")
                            for restaurant in restaurant_list:
                                # Check if this restaurant is already in our list
                                if "name" in restaurant and not any(r.get("name") == restaurant["name"] for r in all_restaurants):
                                    all_restaurants.append(restaurant)
                
                print(f"Extracted {len(all_restaurants)} unique restaurants from rankings data")
            except json.JSONDecodeError as e:
                print(f"Error parsing rankings JSON: {e}")
        else:
            print("No rankings data found in JavaScript")
        
        # If we didn't find any restaurants, try pattern matching
        if not all_restaurants:
            print("Trying pattern matching approach...")
            # Look for restaurant data in the HTML
            restaurant_pattern = re.compile(r'"name":"([^"]+)"[^}]+"hood":"([^"]+)"[^}]+"attractive_score":"([^"]+)"[^}]+"age_score":"([^"]+)"[^}]+"gender_score":"([^"]+)"')
            matches = restaurant_pattern.findall(content)
            
            for match in matches:
                name, hood, attractive, age, gender = match
                restaurant = {
                    "name": name,
                    "hood": hood,
                    "attractive_score": attractive,
                    "age_score": age,
                    "gender_score": gender
                }
                all_restaurants.append(restaurant)
            
            print(f"Found {len(all_restaurants)} restaurants using pattern matching")
        
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
        
        # Wait a bit before closing to see what's happening
        print("Waiting 10 seconds before closing browser...")
        await page.wait_for_timeout(10000)  # 10 seconds
        
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