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

`scrapers/basic_scraper.py` requests `https://looksmapping.com` with a Macintosh Chrome 91 user agent. A successful response is saved to `data/raw_looksmapping.html` before extraction. It keeps New York from `const rankings`, then uses the field regex. If both are empty it writes five rows: SoHo, the Upper East Side, the West Village, Tribeca, and Chelsea. A failed request writes nothing. BeautifulSoup is imported and not used.

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

The script reads `data/restaurant_data.json` and keeps rows whose `hood` is in its Manhattan list. It prints three tables. The headings are "MANHATTAN NEIGHBORHOODS RANKED BY ATTRACTIVENESS", "MANHATTAN NEIGHBORHOODS RANKED BY YOUTH", and "MANHATTAN NEIGHBORHOODS RANKED BY FEMALE RATIO". Attractiveness and age put the highest average first. Gender puts the lowest average first, and the comment says a lower score means more female. Each printed row is the neighborhood, that average, and the restaurant count. A missing score is read as "0". A value that cannot be converted to a number becomes 0.0. Either one is included in the average, and the printed average is rounded to 2 decimal places. The file in the repository is the two-row fallback, one restaurant in each neighborhood, so every table lists the Upper East Side first and SoHo second: attractiveness 9.1 then 8.5, age 8.3 then 7.8, and gender 5.5 then 6.2. Hamilton Heights is in the New York section of `data/rankings_data.json` and is not in that Manhattan list, so a row with that hood would be dropped.

## Scripts

Run these from the repository root. A failed network request is not the same as an empty extraction: some scripts write a sample only after the page loads and no rows are found.

| Script | What it does |
| --- | --- |
| `scrapers/basic_scraper.py` | Requests the homepage with a Macintosh Chrome 91 user agent and a 30 second timeout. A successful response is saved to `data/raw_looksmapping.html` before extraction. It reads `const rankings`, keeps New York, and drops a repeated name. If that is empty, the field regex requires `name`, `hood`, `attractive_score`, `age_score`, then `gender_score`. If that is also empty, it writes five rows: Test Restaurant 1 in SoHo, 2 on the Upper East Side, 3 in the West Village, 4 in Tribeca, and 5 in Chelsea. A failed request writes nothing. BeautifulSoup is imported and unused. |
| `scrapers/simple_scraper.py` | Requests the homepage with a Windows Chrome 91 user agent and a 30 second timeout. BeautifulSoup reads script tags. It keeps New York from `const rankings` and drops a repeated name, then uses the same field regex. The sample is Test Restaurant in Downtown and Fancy Cafe in Uptown, and those scores are the strings `"8"`, `"6"`, `"7"` and `"9"`, `"5"`, `"8"`. It also writes `data/looksmapping.html`. A failed request writes nothing. |
| `scrapers/scraper.py` | Requests the homepage with a 30 second timeout and no user agent. The `city` argument is only logged. The onclick pattern keeps the JSON object and drops the two coordinate numbers. If that list is empty, every script whose text contains `restaurants` is tried. The regex is greedy from the first `{` to the last `}`. Each parsed object that has a `restaurants` list is appended, with no city filter. The two-row sample is written only when the page loads and both extractors are empty. A failed request returns an empty list, does not write the sample, and the completion log says it found 0. |
| `scrapers/extract_data.py` | Does not fetch. Reads `data/LooksMapping.html`. A missing file writes nothing. Onclick JSON keeps `flyToLocation(lng, lat, json)` and adds `long` and `lat`. The rankings search is not the same as the other scripts: it requires `const rankings = {...}; // This will contain`, or `updateRankingsDisplay();` immediately before `const rankings`. It keeps New York and drops a repeated name. Raw HTML runs only when fewer than 10 rows were found. If still empty, it writes Test Restaurant and Fancy Cafe with numeric scores, `lat`, and `long`. |
| `scrapers/requests_html_scraper.py` | Renders the homepage with a 5 second sleep and a 30 second timeout, then parses `flyToLocation(lng, lat, json)` from `div[onclick*='flyToLocation']`. It writes `data/restaurant_data.json`, including an empty list, and then prints the neighborhoods. The neighborhood loop reuses the name `r`. When at least one row was saved, `r` is the last restaurant dict, so `r.html.html` raises `AttributeError` after the JSON file and the neighborhood report. That error is not caught. `data/looksmapping_complete.html` is written only when the list is empty, because the loop did not rebind `r`. A failed request writes nothing. |
| `scrapers/playwright_scraper.py` | Visible Chromium, 1280 by 800. If Playwright is not installed, it exits 1 before opening a browser. It looks for `div.result-item`, then `.result-list .result-item`, then `[onclick*='flyToLocation']`, then `.result-name`. The first selector that matches is counted and then ignored. It saves the two screenshots, then always saves `data/looksmapping_source.html`. When it finds `const rankings`, it writes that raw text to `data/rankings_data.json` before parsing it, and that path drops a repeated name. A parse error leaves that file and falls through to the field regex. The regex requires `name`, `hood`, `attractive_score`, `age_score`, then `gender_score`, in that order, and it keeps duplicates. The two-row sample is written only when both are empty. It waits 10 seconds before closing the browser. |
| `scrapers/map_scraper.py` | Visible Chromium, 1280 by 800, and the same two screenshots. It clicks at most the first 30 `.mapboxgl-marker` pins. A click that raises, or a marker with no popup, adds no row and the loop continues. A popup is kept even when the name repeats. A score of `N/10` keeps N, including a decimal, and no match becomes `"0"`. Each of the first three metric bars uses an integer `left: N%`, divided by 10, rounded to 1 decimal, and stored as a string. A missing bar stays `"0"`. If those clicks yield nothing, it saves `data/looksmapping_source.html` and reads New York from `const rankings`, dropping a repeated name. A rankings JSON error, or both sources empty, writes the two-row sample. After either save it waits 5 seconds. If Playwright is not installed, it exits 1 before opening a browser. |
| `scrapers/comprehensive_map_scraper.py` | Visible Chromium, 1280 by 800. New York, then hot, age, and gender. A missing New York button is logged and the script continues. A failure inside one mode returns no rows for that mode and the other modes still run. In each mode it clicks every `.mapboxgl-marker`, skips a name it already saved, drags the map to seven fixed points, and wheel-zooms by 2, 1, 0, and -1. A zoom of 0 moves the wheel zero times. A pan or zoom error is logged and that step continues. An empty combined list writes the two-row sample, while the function still returns the empty list. An exception before that save writes nothing and is raised. |
| `scrapers/pin_scraper.py` | Visible Chromium, 1280 by 800. It clicks New York only when the button's class does not contain `city-active`. A missing class is caught and the script continues. If `.mapboxgl-canvas` never appears, the 30 second wait raises and nothing is written. Then hot, age, and gender. A mode error is printed and the next mode runs. It uses the first selector that finds pins: `.mapboxgl-marker`, that marker's `svg`, that marker's `div`, then two style selectors. Pins are clicked in batches of 50. A score of `N/10` keeps N, including a decimal, and no match becomes `"0"`. Each of the first three metric bars uses an integer `left: N%`, divided by 10, rounded to 1 decimal, and stored as a string. A name already saved is skipped. `data/restaurant_data_progress.json` is rewritten when the unique-name count is a multiple of 10, and again after every batch of pins that were found, even when that batch added nothing and even when the list is still empty. `data/restaurant_data.json` is written only when at least one row was found. |
| `scrapers/selenium_scraper.py` | Visible Chrome through `webdriver.Chrome()`. Headless is commented out. A missing New York button is logged and the script continues. If `div[onclick*='flyToLocation']` does not appear within 20 seconds, that timeout is logged and the script continues. It parses `flyToLocation(lng, lat, json)` once for the page's current mode, without dropping repeated names, then again for hot, age, and gender, skipping a name already saved. It writes `data/restaurant_data.json` even when the list is empty, then `data/looksmapping_complete.html`. An HTML save error is logged and the JSON file stays. An exception before the JSON save writes nothing and is raised. The browser is closed either way. |
| `scrapers/selenium_scraper_robust.py` | Visible Chrome, 1920 by 1080, with ChromeDriver from webdriver-manager. A missing Selenium install exits 1 before the driver starts. A driver-setup failure exits 1. It clicks New York when the class does not contain `city-active`. A New York error is printed and the script continues. It reads `div.result-item` text, keeping `Hot:`, `Age:`, and `Gender:` numbers, or `"0"` when a label is missing, and stores the mode on each row. A mode that finds no `div.result-item` within 20 seconds adds no rows. Names are unique across modes. After the mode loop it writes `data/restaurant_data.json`, including an empty list, and then `data/looksmapping_complete.html`. An error during the HTML write leaves the JSON file in place and the function returns an empty list. An error before the JSON write returns an empty list and writes nothing. The command does not check that return value, so those failures still exit 0. |
| `scrapers/neighborhood_analyzer.py` | Does not scrape. Reads `data/restaurant_data.json`, keeps its Manhattan list, and prints attractiveness and age highest-first. The gender table is lowest-first, and the comment says a lower score means more female. A missing score is read as "0". A value that cannot be converted to a number becomes 0.0. Either one is included, and the printed average is rounded to 2 decimal places. |

## Data Structure

`data/restaurant_data.json` currently holds the fallback sample. Each row has `name`, `hood`, `attractive_score`, `gender_score`, and `age_score`.

`data/rankings_data.json` is a saved rankings extract, not the two-row sample. It is grouped by city (`ny`, `la`, `sf`), then by `hot`, `age`, and `gender`. Each of those has `top` and `bottom` lists. An entry has `name`, `hood`, `category`, `attractive_score`, `age_score`, `gender_score`, `faces`, `lat`, and `long`. `hood` is null on some Los Angeles and San Francisco rows.

`data/LooksMapping.html`, `data/looksmapping_complete.html`, `data/looksmapping_source.html`, and `data/raw_looksmapping.html` are saved copies of the page. `mapboxgl.accessToken` is the word `REDACTED` in each of them. `LooksMapping.html` has that assignment five times. The other three files have it once.

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

`scrapers/neighborhood_analyzer.py` groups the rows in `data/restaurant_data.json` by neighborhood and prints three tables. Attractiveness and age are sorted with the highest average first. Gender is sorted with the lowest average first. Printed averages are rounded to 2 decimal places. It only keeps neighborhoods in its Manhattan list. Hamilton Heights is not on that list. On the file in this repository, every table lists the Upper East Side before SoHo.

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
