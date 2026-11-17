# LooksMapping Scraper

A web scraping toolkit for extracting restaurant data from LooksMapping.com. The saved rankings cover New York, Los Angeles, and San Francisco, with attractiveness, age, and gender scores.

## Overview

This project has several scrapers for LooksMapping.com. They look for restaurant names, neighborhoods, attractiveness scores, age scores, and gender scores. The saved rankings file includes New York, Los Angeles, and San Francisco.

## Features

- HTTP, requests-html, Playwright, and Selenium scripts aimed at LooksMapping.com
- Saved rankings for New York, Los Angeles, and San Francisco in `data/rankings_data.json`
- `neighborhood_analyzer.py` averages the three scores by neighborhood for rows in `data/restaurant_data.json`
- Several scripts write a built-in sample when they find no rows. That sample is not scraped data.

## Project Structure

```
├── README.md
├── requirements.txt
├── scrapers/
│   ├── basic_scraper.py
│   ├── comprehensive_map_scraper.py
│   ├── extract_data.py
│   ├── map_scraper.py
│   ├── neighborhood_analyzer.py
│   ├── pin_scraper.py
│   ├── playwright_scraper.py
│   ├── requests_html_scraper.py
│   ├── scraper.py
│   ├── selenium_scraper.py
│   ├── selenium_scraper_robust.py
│   └── simple_scraper.py
└── data/
    ├── LooksMapping.html
    ├── looksmapping_complete.html
    ├── looksmapping_initial.png
    ├── looksmapping_ny_selected.png
    ├── looksmapping_source.html
    ├── rankings_data.json
    ├── raw_looksmapping.html
    └── restaurant_data.json
```

## Installation

### Prerequisites

- Python 3.7 or higher
- Chrome browser (for Selenium-based scrapers)
- Internet connection

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Zu67/looks-mapping-project.git
   cd looks-mapping-project
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **ChromeDriver.** Only `scrapers/selenium_scraper_robust.py` downloads it through webdriver-manager. `scrapers/selenium_scraper.py` calls `webdriver.Chrome()` and expects a driver already available.

`numpy`, `python-dotenv`, `lxml`, `matplotlib`, `seaborn`, `pytest`, `black`, and `flake8` are listed in `requirements.txt` and are not imported by any script. `pandas` is imported by `neighborhood_analyzer.py`.

5. **Install Playwright browsers** (for Playwright scrapers):
   ```bash
   playwright install
   ```

## Usage

### Basic Scraping

```bash
python scrapers/basic_scraper.py
```

`scrapers/basic_scraper.py` requests `https://looksmapping.com` with a Macintosh Chrome 91 user agent. A successful response is saved to `data/raw_looksmapping.html` before extraction. It keeps New York from `const rankings` and drops a repeated name, then uses the field regex, which keeps duplicates. If both are empty it writes five rows: SoHo, the Upper East Side, the West Village, Tribeca, and Chelsea. A failed request returns an empty list and writes nothing. The docstring says that failure raises `RequestException`, but the function catches it. The completion line still says the scrape succeeded and found 0. BeautifulSoup is imported and not used.

The `data/restaurant_data.json` in this repository is the two-row fallback, Test Restaurant 1 in SoHo and Test Restaurant 2 on the Upper East Side. That pair is what `scrapers/comprehensive_map_scraper.py`, `scrapers/map_scraper.py`, and `scrapers/playwright_scraper.py` write when they find nothing. `scrapers/scraper.py` writes it only after the page loads and both extractors are empty. A failed request returns an empty list and writes nothing. `scrapers/simple_scraper.py` writes Test Restaurant in Downtown and Fancy Cafe in Uptown, with string scores. `scrapers/extract_data.py` writes those same two names with numeric scores, `lat`, and `long`.

`data/rankings_data.json` is a saved rankings object for New York, Los Angeles, and San Francisco. Each city has hot, age, and gender lists, with top and bottom entries.

### Playwright

```bash
python scrapers/comprehensive_map_scraper.py
```

`scrapers/comprehensive_map_scraper.py` launches Chromium with `headless=False`, a 1280 by 800 viewport, and a Macintosh user agent. It tries four selectors for New York. A missing button is logged and the script continues. It then walks hot, age, and gender. A failure inside one mode is logged and that mode contributes no rows. The other modes still run. If the combined list is empty, the save writes the two-row fallback above, but the function still returns the empty list and the completion log says it found 0. An exception that escapes before that save, including a map that never appears, is logged and raised, and the file is left unchanged.

### Selenium

```bash
python scrapers/selenium_scraper.py
python scrapers/selenium_scraper_robust.py
```

`scrapers/selenium_scraper.py` calls `webdriver.Chrome()` and does not download a driver. `scrapers/selenium_scraper_robust.py` installs ChromeDriver through webdriver-manager.

### Data Analysis

After scraping, analyze the collected data:

```bash
python scrapers/neighborhood_analyzer.py
```

The script reads `data/restaurant_data.json` and keeps rows whose `hood` is in its Manhattan list. A missing file is logged and raised. An empty file, or a file whose neighborhoods are all outside that list, prints no tables, and the completion line says it processed 0 neighborhoods. It prints three tables. The headings include the `===` markers: "=== MANHATTAN NEIGHBORHOODS RANKED BY ATTRACTIVENESS ===", "=== MANHATTAN NEIGHBORHOODS RANKED BY YOUTH ===", and "=== MANHATTAN NEIGHBORHOODS RANKED BY FEMALE RATIO ===". Attractiveness and age put the highest average first. Gender puts the lowest average first, and the comment says a lower score means more female. Each printed row is the neighborhood, that average, and the restaurant count. A missing score is read as "0". A score that is present and null, or a value that cannot be converted to a number, becomes 0.0. Either one is included in the average, and the printed average is rounded to 2 decimal places. The DataFrame the function returns is sorted by restaurant count, highest first, not by those printed rankings. The file in the repository is the two-row fallback, one restaurant in each neighborhood, so every table lists the Upper East Side first and SoHo second: attractiveness 9.1 then 8.5, age 8.3 then 7.8, and gender 5.5 then 6.2. Hamilton Heights is in the New York section of `data/rankings_data.json` and is not in that Manhattan list, so a row with that hood would be dropped. A missing hood is read as an empty string and dropped the same way. The grouping step's `"Unknown"` default is not used for those rows. A JSON file that is an object, or a list of values that are not objects, raises `AttributeError`. The command logs `An error occurred during analysis` and raises it again. A missing file is logged twice: `Data file data/restaurant_data.json not found`, then that same outer line. The `StatisticsError` handler does not run, because an empty neighborhood is skipped before the average. `extract_restaurant_data()` is not called by this command. Calling it writes `[]` over `data/restaurant_data.json`.

## Scripts

Run these from the repository root. A failed network request is not the same as an empty extraction: some scripts write a sample only after the page loads and no rows are found.

| Script | What it does |
| --- | --- |
| `scrapers/basic_scraper.py` | Requests the homepage with a Macintosh Chrome 91 user agent and a 30 second timeout. A successful response is saved to `data/raw_looksmapping.html` before extraction. It reads `const rankings`, keeps New York, and drops a repeated name. Two rows with no name count as the same name, so only the first is kept. A rankings position that cannot be read as a list of objects raises before the field regex. The HTML file stays, and `data/restaurant_data.json` is not written. If that is empty, the field regex requires `name`, `hood`, `attractive_score`, `age_score`, then `gender_score`, and it keeps duplicates. If that is also empty, it writes five rows: Test Restaurant 1 in SoHo, 2 on the Upper East Side, 3 in the West Village, 4 in Tribeca, and 5 in Chelsea. A failed request returns an empty list and writes nothing. The completion line still says the scrape succeeded and found 0. BeautifulSoup is imported and unused. |
| `scrapers/simple_scraper.py` | Requests the homepage with a Windows Chrome 91 user agent and a 30 second timeout. BeautifulSoup reads script tags. It keeps New York from the first `const rankings` that parses, drops a repeated name, and stops. Two rows with no name count as the same name, so only the first is kept. A script whose contents are not one string is skipped. A JSON error in one script lets it try the next script. A rankings position that cannot be read as a list of objects raises before the field regex. Neither output file is written, and the main block logs the error and re-raises it. The field regex runs only when the rankings list is empty, and it keeps duplicates. The sample is Test Restaurant in Downtown and Fancy Cafe in Uptown, and those scores are the strings `"8"`, `"6"`, `"7"` and `"9"`, `"5"`, `"8"`. A successful fetch also writes `data/looksmapping.html`, including when the sample is used. A failed request returns an empty list and writes nothing. The completion line still says the scrape succeeded and found 0. |
| `scrapers/scraper.py` | Requests the homepage with a 30 second timeout and no user agent. The `city` argument is only logged. The onclick pattern keeps the JSON object, turns `&quot;` into a quote, stops at the first `}`, and drops the two coordinate numbers. A repeated name is kept. If that list is empty, every script whose text is one string and contains `restaurants` in any case is tried. The regex still requires the lowercase key `"restaurants"`, and it is greedy from the first `{` to the last `}`. Each parsed object that has a `restaurants` value is appended, with no city filter. A string value is stored one character per row. A value that is not iterable raises before the sample is written. The main block logs that error and re-raises it, and no file is written. The two-row sample is written only when the page loads and both extractors are empty. A failed request returns an empty list, does not write the sample, and the completion log says it found 0. |
| `scrapers/extract_data.py` | Does not fetch. Reads `data/LooksMapping.html`. A missing file prints the error and a traceback, writes nothing, and still exits 0. Onclick JSON keeps `flyToLocation(lng, lat, json)` and adds `long` and `lat`, including a repeated name. The JSON pattern stops at the first `}`. A coordinate that is not a number raises `ValueError` before the other extractors run, and that error is caught by the same handler as a missing file, so nothing is written. A `name` key that is present and null is kept on that onclick row, and it does not block a later row because the seen set stores only a truthy name. The rankings search is not the same as the other scripts: it requires `const rankings = {...}; // This will contain`, or `updateRankingsDisplay();` immediately before `const rankings`. It keeps New York and drops a repeated name, and the merge also skips a name already taken from the onclick rows. Raw HTML runs only when fewer than 10 rows were found. If still empty, it writes Test Restaurant and Fancy Cafe with numeric scores, `lat`, and `long`. |
| `scrapers/requests_html_scraper.py` | Renders the homepage with a 5 second sleep and a 30 second timeout, then parses `flyToLocation(lng, lat, json)` from `div[onclick*='flyToLocation']`. It writes `data/restaurant_data.json`, including an empty list, and then prints the neighborhoods. The neighborhood loop reuses the name `r`. When at least one row was saved, `r` is the last restaurant dict, so `r.html.html` raises `AttributeError` after the JSON file and the neighborhood report. That error is not caught. `data/looksmapping_complete.html` is written only when the list is empty, because the loop did not rebind `r`. A failed request writes nothing. |
| `scrapers/playwright_scraper.py` | Visible Chromium, 1280 by 800. If Playwright is not installed, it exits 1 before opening a browser. It looks for `div.result-item`, then `.result-list .result-item`, then `[onclick*='flyToLocation']`, then `.result-name`. The first selector that matches is counted and then ignored. It saves the two screenshots, then always saves `data/looksmapping_source.html`. When it finds `const rankings`, it writes that raw text to `data/rankings_data.json` before parsing it, and that path drops a repeated name. A parse error leaves that file and falls through to the field regex. The regex requires `name`, `hood`, `attractive_score`, `age_score`, then `gender_score`, in that order, and it keeps duplicates. The two-row sample is written only when both are empty. A rankings object with no `ny` key still leaves `data/rankings_data.json` in place and then uses the field regex. If a position value is not a list, `len` raises `TypeError`, which is not caught, so the 10 second wait is skipped. Otherwise it waits 10 seconds before closing the browser. |
| `scrapers/map_scraper.py` | Visible Chromium, 1280 by 800, and the same two screenshots. It clicks New York whenever a selector matches, without checking whether that city is already selected. It clicks at most the first 30 `.mapboxgl-marker` pins. The click log's denominator is the full marker count, not 30. A name that contains a single quote makes the neighborhood selector raise, and that row is not saved. A click that raises, or a marker with no popup, adds no row and the loop continues. A popup is kept even when the name repeats. A score of `N/10` keeps N, including a decimal, and no match becomes `"0"`. Each of the first three metric bars uses an integer `left: N%`, divided by 10, rounded to 1 decimal, and stored as a string. A missing bar stays `"0"`. If those clicks yield nothing, it saves `data/looksmapping_source.html` and reads New York from `const rankings`, dropping a repeated name. A rankings JSON error, or both sources empty, writes the two-row sample. After either save it waits 5 seconds. If Playwright is not installed, it exits 1 before opening a browser. |
| `scrapers/comprehensive_map_scraper.py` | Visible Chromium, 1280 by 800. New York, then hot, age, and gender. A missing New York button is logged and the script continues. A failure inside one mode returns no rows for that mode and the other modes still run. In each mode it clicks every `.mapboxgl-marker`, skips a name it already saved, drags the map to seven fixed points, and wheel-zooms by 2, 1, 0, and -1. Every drag starts at screen 400, 300, not at the canvas center. The first point is also 400, 300, so that drag has zero length. A positive zoom wheels in by 100 once per step, and a negative zoom wheels out by 100 once per step. A zoom of 0 moves the wheel zero times. A pan or zoom error is logged and that step continues. An empty combined list writes the two-row sample, while the function still returns the empty list. An exception before that save writes nothing and is raised. |
| `scrapers/pin_scraper.py` | Visible Chromium, 1280 by 800. It clicks New York only when the button's class does not contain `city-active`. A missing class is caught and the script continues. If `.mapboxgl-canvas` never appears, the 30 second wait raises and nothing is written. Then hot, age, and gender. A mode error is printed and the next mode runs. It uses the first selector that finds pins: `.mapboxgl-marker`, that marker's `svg`, that marker's `div`, then two style selectors. Pins are clicked in batches of 50. A score of `N/10` keeps N, including a decimal, and no match becomes `"0"`. Each of the first three metric bars uses an integer `left: N%`, divided by 10, rounded to 1 decimal, and stored as a string. A name already saved is skipped. `data/restaurant_data_progress.json` is rewritten when the unique-name count is a multiple of 10, and again after every batch of pins that were found, even when that batch added nothing and even when the list is still empty. `data/restaurant_data.json` is written only when at least one row was found. A missing name is stored as "Unknown", and only the first one is kept. The scroll call passes the pin's viewport x and y to `window.scrollTo`. If Playwright is not installed, the script prints the install lines and exits 1 before opening a browser. A raised canvas wait skips the final "Script completed" line. |
| `scrapers/selenium_scraper.py` | Visible Chrome through `webdriver.Chrome()`. Headless is commented out. A missing New York button is logged and the script continues. If `div[onclick*='flyToLocation']` does not appear within 20 seconds, that timeout is logged and the script continues. It parses `flyToLocation(lng, lat, json)` once for the page's current mode, without dropping repeated names, then again for hot, age, and gender, skipping a name already saved. `&quot;` is replaced with a quote before parsing. The JSON pattern stops at the first `}`. A `name` or `hood` key that is present and null is kept. A missing name uses the `.result-name` text, or "Unknown". It writes `data/restaurant_data.json` even when the list is empty, then `data/looksmapping_complete.html`. An HTML save error is logged and the JSON file stays. An exception before the JSON save writes nothing and is raised. The browser is closed either way. |
| `scrapers/selenium_scraper_robust.py` | Visible Chrome, 1920 by 1080, with ChromeDriver from webdriver-manager. A missing Selenium install exits 1 before the driver starts. A driver-setup failure exits 1. It clicks New York when the class does not contain `city-active`. A New York error is printed and the script continues. It reads `div.result-item` text, keeping `Hot:`, `Age:`, and `Gender:` numbers, or `"0"` when a label is missing, and stores the mode on each row. The name and neighborhood are stripped. A blank name is kept once. An element missing `.result-name`, `.result-hood`, or `.result-scores` is skipped. A mode that finds no `div.result-item` within 20 seconds adds no rows. Names are unique across modes. After the mode loop it writes `data/restaurant_data.json`, including an empty list, and then `data/looksmapping_complete.html`. An error during the HTML write leaves the JSON file in place and the function returns an empty list. An error before the JSON write returns an empty list and writes nothing. The command does not check that return value, so those failures still exit 0. |
| `scrapers/neighborhood_analyzer.py` | Does not scrape when run as a script. Reads `data/restaurant_data.json`, keeps its Manhattan list, and prints attractiveness and age highest-first. The gender table is lowest-first, and the comment says a lower score means more female. A missing score is read as "0". A null score, or a value that cannot be converted to a number, becomes 0.0. Either one is included, and the printed average is rounded to 2 decimal places. The returned DataFrame is sorted by restaurant count, highest first. A missing file is raised. An empty result prints no tables and the completion line says it processed 0 neighborhoods. `extract_restaurant_data()` is not called by the script. Calling it writes `[]` over `data/restaurant_data.json`. |

## Data Structure

`data/restaurant_data.json` currently holds the fallback sample. Each row has `name`, `hood`, `attractive_score`, `gender_score`, and `age_score`.

`data/rankings_data.json` is a saved rankings extract, not the two-row sample. It is grouped by city (`ny`, `la`, `sf`), then by `hot`, `age`, and `gender`. Each of those has `top` and `bottom` lists, and every list has 5 rows, so the file has 90 rows and 88 different names. Hop Won Express is in the New York hot bottom list and the New York gender bottom list. City Lunch Restaurant is in the San Francisco age bottom list and the San Francisco gender bottom list. Each pair is the same record twice. Hop Won Express is Midtown East, Chinese restaurant, scores `"1.0"`, `"4.8"`, and `"3.1"`, 95 faces, latitude 40.7532541, longitude -73.9739666. City Lunch Restaurant is Hunters Point, Traditional American restaurant, scores `"4.5"`, `"1.2"`, and `"2.8"`, 54 faces, latitude 37.725809, longitude -122.3868195. An entry has `name`, `hood`, `category`, `attractive_score`, `age_score`, `gender_score`, `faces`, `lat`, and `long`. The three scores are strings, `faces` is an integer, and `lat` and `long` are numbers. `hood` is null on 12 Los Angeles rows and on no New York or San Francisco row. Those rows are Mariscos El Levanton on the hot top list, Lupita's, Mediterranean Delight, McDonald's, and Jack in the Box on the hot bottom list, Steak Corral Restaurants, El Sabroso grill, Bruce's Prime Rib And Spirits, and R&J Sea & Soul on the age bottom list, Le Coco and The Blue Hole Restaurant Belizean Caribbean Cuisine on the gender top list, and Capo on the gender bottom list. Every hot top row has `attractive_score` `"10.0"`, and every hot bottom row has `"1.0"`. That is 15 rows at each end. New York and San Francisco age top rows are also all `"10.0"`. Los Angeles age top is not: Manas Indian Cuisine is `"9.4"`, Mayura Indian Restaurant, Backyard Bowls, and Lemonade are `"8.9"`, and AFURI Ramen Culver City is `"8.5"`. Los Angeles age bottom is all `"1.0"`. New York age bottom is `"1.0"`, `"1.0"`, `"1.2"`, `"1.3"`, and `"1.7"`. San Francisco age bottom is `"1.0"`, `"1.0"`, `"1.2"`, `"1.2"`, and `"1.4"`. No gender list is all `"10.0"` or all `"1.0"`. New York gender top is `"9.2"`, `"8.6"`, `"8.5"`, `"8.2"`, and `"8.2"`: Big Apple Brunch, Pietro Nolita, Kanü Bar|Grill, STK Steakhouse Downtown NYC, and Lighthouse Fish Market. New York gender bottom is `"2.3"`, `"2.5"`, `"3.1"`, `"3.1"`, and `"3.1"`: Lahori Kabab, Big Arc Chicken, Hop Won Express, Subway, and Nica Trattoria. Los Angeles gender top starts at `"8.5"` on Le Coco, whose `hood` is null, and its bottom starts at `"3.3"` on Hamburger Habit. San Francisco gender top starts at `"7.6"` on Jolene’s Bar and Restaurant, and its bottom starts at `"2.5"` on both Gold Club and Hi Tops San Francisco. New York's hot top rows are Ubani Midtown, Shinn WEST, KYU NYC, Aroy Dee Thai Kitchen, and Top Thai 55 Carmine. `gender_score` runs from `"2.3"` on Lahori Kabab in Kips Bay to `"9.2"` on Big Apple Brunch in Hell's Kitchen. `faces` runs from 50 to 277. The 50s are Shinn WEST, Mykonian House, and Mediterranean Delight. The 277 is Hi Tops San Francisco in The Castro. The 90 rows sum to 10123 faces. The `category` field has 51 different values, and 33 of them appear once. `Restaurant` appears 9 times, `Mexican restaurant` 5, and `Thai restaurant`, `Chinese restaurant`, `Italian restaurant`, `Seafood restaurant`, and `Indian restaurant` 4 each. Only `Restaurant`, `Chinese restaurant`, and `Seafood restaurant` appear in all three cities. Fourteen categories appear only in New York, 11 only in Los Angeles, and 13 only in San Francisco.

`data/LooksMapping.html`, `data/looksmapping_complete.html`, `data/looksmapping_source.html`, and `data/raw_looksmapping.html` are saved copies of the page. Each one contains a `const rankings` assignment, and that object is the same as `data/rankings_data.json`. `LooksMapping.html` has that assignment five times. The other three files have it once. `mapboxgl.accessToken` is the word `REDACTED` in each of them. `LooksMapping.html` has that assignment five times. The other three files have it once. Each file credits walzr.com. The saved script sets `initialCity` to `ny`. New York is centered at longitude -73.99500657647957 and latitude 40.73653166523988, zoom 12.905477962190917. Los Angeles is -118.49352211180002, 34.01429982135038, zoom 13.8828812294801. San Francisco is -122.4136541280476, 37.78464407695378, zoom 13.727669036468848. Measured from those centers by straight-line distance in degrees, the closest saved place in New York is KYU NYC in NoHo, 0.010912 degrees away, and the farthest is Kanü Bar|Grill in Hamilton Heights, 0.103824. In Los Angeles the closest is Backyard Bowls in Mid-City, 0.005542, and the farthest is El Sabroso grill, whose hood is null, 0.455041. In San Francisco the closest is Ararat Kebab & Gyros in the Tenderloin, 0.001690, and the farthest is Cypress Grill in Lakeshore, 0.100048. Those six distances are rounded to 6 decimal places. The file has 88 distinct places. By that same distance, each one is closer to its own city's center than to either of the other two. A city link whose text is not exactly `New York` or `Los Angeles` is treated as San Francisco. `flyToLocation` flies to zoom 16 over 1000 milliseconds, then waits another 1000 milliseconds. A viewport 768 pixels wide or narrower fills a modal. A wider viewport opens a Mapbox popup. Each pan button moves the center by 0.01 degree, and the center button flies back to that city's saved center and zoom. `LooksMapping.html` repeats this script five times. The closest city is the straight-line distance in degrees, not miles. An equal distance keeps the later city in the order New York, San Francisco, Los Angeles. The first `switchCity` call passes `false`, so that move has duration 0, and `initialLoadComplete` is still false, so it does not refresh the markers. Marker color uses the current mode. The score is clamped to 1 through 10 before the color is chosen, and a score of 5.5 or below is on the low side of white. The popup badge still prints `attractive_score`, including in the age and gender modes. The category line removes the first ` restaurant`, so `Southern restaurant (US)` is shown as `Southern (US)`. The rankings panel is separate from the map pins. Hot titles are "Top 5 hot" and "Top 5 not". Age titles are "Top 5 young" and "Top 5 old". Gender titles are "Top 5 female" and "Top 5 male". The second title uses the `bottom` list. That panel prints the score for the current mode, and a null `hood` is shown as an empty string. The pins are fetched from `/places_ny.geojson.gz`, `/places_la.geojson.gz`, and `/places_sf.geojson.gz`. Those files are not in this repository. A failed fetch logs the error and draws no pins. A successful load is cached, and every `moveend` calls that load again. A pin click within 300 milliseconds of a map move is ignored. Search matches the lowercased name, keeps the first 10 matches in file order, and prints `attractive_score`. An empty query clears the list. It runs from the search button and from Enter. The document title is LooksMapping, and the page loads Mapbox GL JS v2.15.0. The Mapbox logo is hidden. The viewport meta includes `user-scalable=no`. The zoom slider is 153 pixels: the top is zoom 18 and the bottom is zoom 0. Dragging clamps the handle to that range. The zoom listener does not clamp, so a zoom above 18 places the handle above the track.

## Configuration

### Browser Settings

For headless operation, modify the browser launch options:

```python
# scrapers/comprehensive_map_scraper.py, inside _setup_browser
browser = await playwright.chromium.launch(
    headless=False,  # Set to True for headless operation
)

# scrapers/selenium_scraper.py, inside _setup_webdriver
# chrome_options.add_argument("--headless")
```

### Timeout Settings

Adjust wait times based on your internet connection:

```python
# Increase timeouts for slower connections
await page.wait_for_timeout(5000)  # 5 seconds
time.sleep(3)  # 3 seconds
```

## Troubleshooting

### Common Issues

1. **"ChromeDriver not found"**
   - `scrapers/selenium_scraper.py` calls `webdriver.Chrome()` and expects a driver already on the path
   - `scrapers/selenium_scraper_robust.py` downloads one with webdriver-manager

2. **"Playwright browsers not installed"**
   - Solution: Run `playwright install`

3. **"No restaurants found"**
   - Solution: Check if the website structure has changed
   - Try different scraping methods
   - Verify internet connection

4. **"Timeout errors"**
   - Solution: Increase timeout values in the code
   - Check if the website is accessible

### Debug Mode

Enable debug mode for detailed logging:

```python
# Set headless=False to see browser actions
browser = await p.chromium.launch(headless=False)
```

## Data Analysis

`scrapers/neighborhood_analyzer.py` groups the rows in `data/restaurant_data.json` by neighborhood and prints three tables. Attractiveness and age are sorted with the highest average first. Gender is sorted with the lowest average first. Printed averages are rounded to 2 decimal places. It only keeps neighborhoods in its Manhattan list. Hamilton Heights is not on that list. The list has 32 names. Of the New York ranking neighborhoods, only Hamilton Heights is missing, so Kanü Bar|Grill is the only saved New York row it would drop. The 13 it would keep are East Harlem, East Village, the Financial District, Harlem, Hell's Kitchen, Kips Bay, the Lower East Side, Midtown East, Murray Hill, NoHo, Nolita, the Upper East Side, and the West Village. The other 19 names on the list do not appear in the rankings file: Battery Park City, Central Park South, Chelsea, Chinatown, the Flatiron District, the Garment District, Gramercy, Greenwich Village, Inwood, Koreatown, Little Italy, Midtown West, Morningside Heights, NoMad, SoHo, the Theater District, Tribeca, the Upper West Side, and Washington Heights. On the file in this repository, every table lists the Upper East Side before SoHo. The returned DataFrame is sorted by restaurant count. `extract_restaurant_data()` is separate from that command and writes an empty list over the JSON file.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Legal Notice

This project is for educational and research purposes. Please respect the website's terms of service and robots.txt file. Use reasonable delays between requests to avoid overloading the server.

## License

This repository does not include a license file.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the code comments
3. Open an issue on GitHub

## History

Zu67 committed the scrapers on 2025-10-25 ("Initial commit: LooksMapping scraper project") and the documentation the same day ("feat: Add comprehensive documentation and clean up codebase").
