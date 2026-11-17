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

4. **Install browser drivers** (for Selenium):
   ```bash
   # Chrome driver will be automatically managed
   ```

5. **Install Playwright browsers** (for Playwright scrapers):
   ```bash
   playwright install
   ```

## Usage

### Basic Scraping

```bash
python scrapers/basic_scraper.py
```

`scrapers/basic_scraper.py` requests `https://looksmapping.com`. It looks for a `const rankings = {...}` object and keeps the New York entries, then tries a regex on `name`, `hood`, and the three scores. BeautifulSoup is imported and not used. If the page loads and both extractors return nothing, it writes five fallback rows, Test Restaurant 1 through Test Restaurant 5, to `data/restaurant_data.json`. If the request fails, it prints the error and does not write a file.

The `data/restaurant_data.json` in this repository is the two-row fallback, Test Restaurant 1 in SoHo and Test Restaurant 2 on the Upper East Side. That pair is what `scrapers/comprehensive_map_scraper.py`, `scrapers/map_scraper.py`, `scrapers/playwright_scraper.py`, and `scrapers/scraper.py` write when they find nothing. `scrapers/simple_scraper.py` uses a different pair, Test Restaurant and Fancy Cafe.

`data/rankings_data.json` is a saved rankings object for New York, Los Angeles, and San Francisco. Each city has hot, age, and gender lists, with top and bottom entries.

### Playwright

```bash
python scrapers/comprehensive_map_scraper.py
```

`scrapers/comprehensive_map_scraper.py` launches Chromium with `headless=False`, selects New York, and walks the hot, age, and gender modes. If that finds no restaurants, it writes the two-row fallback above.

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

The script reads `data/restaurant_data.json` and keeps rows whose `hood` is in its Manhattan list. It prints three tables: attractiveness with the highest average first, age with the highest average first under the heading "ranked by youth", and gender with the lowest average first under "ranked by female ratio". The code comment says a lower gender score means more female. The file in the repository is the two-row fallback, so that report is SoHo and the Upper East Side from the sample.

## Scripts

Run these from the repository root. A failed network request is not the same as an empty extraction: some scripts write a sample only after the page loads and no rows are found.

| Script | What it does |
| --- | --- |
| `scrapers/basic_scraper.py` | Requests the homepage. Reads a `const rankings` object and keeps New York, then a field regex. Writes five Test Restaurant rows only when the page loaded and both extractors are empty. A failed request writes nothing. BeautifulSoup is imported and unused. |
| `scrapers/simple_scraper.py` | Requests the homepage and parses script tags with BeautifulSoup. Keeps New York from `const rankings`, then the same field regex. The sample is Test Restaurant in Downtown and Fancy Cafe in Uptown. Also writes `data/looksmapping.html`. A failed request writes nothing. |
| `scrapers/scraper.py` | Requests the homepage. The `city` argument is only logged. BeautifulSoup looks for `flyToLocation` onclick JSON, then a script containing `restaurants`. The sample is Test Restaurant 1 in SoHo and Test Restaurant 2 on the Upper East Side. A failed request writes nothing. |
| `scrapers/extract_data.py` | Does not fetch. Reads `data/LooksMapping.html`. Tries onclick JSON, then New York rows from a rankings object, then raw HTML when fewer than 10 rows were found. If still empty, writes Test Restaurant and Fancy Cafe with numeric scores, `lat`, and `long`. |
| `scrapers/requests_html_scraper.py` | Renders the homepage and reads `div` elements whose onclick contains `flyToLocation`. Writes `data/restaurant_data.json` and `data/looksmapping_complete.html`, including an empty list. |
| `scrapers/playwright_scraper.py` | Visible Chromium. Saves `data/looksmapping_initial.png`, `data/looksmapping_ny_selected.png`, and `data/looksmapping_source.html`. When it finds `const rankings`, it writes that object to `data/rankings_data.json` and keeps New York. Otherwise it uses the field regex. The empty case writes the two-row SoHo / Upper East Side sample. |
| `scrapers/map_scraper.py` | Visible Chromium and the same two screenshots. Clicks up to 30 `.mapboxgl-marker` pins. If those yield nothing, it reads New York from `const rankings` and saves `data/looksmapping_source.html`. The empty case writes the two-row sample. |
| `scrapers/comprehensive_map_scraper.py` | Visible Chromium, New York, and the hot, age, and gender modes. The empty case writes the two-row sample. |
| `scrapers/pin_scraper.py` | Visible Chromium, New York, and the hot, age, and gender modes. Clicks map markers and reads popups. Writes `data/restaurant_data_progress.json` during the run, and `data/restaurant_data.json` only when at least one row was found. |
| `scrapers/selenium_scraper.py` | Chrome through `webdriver.Chrome()`, New York, then hot, age, and gender. Writes `data/restaurant_data.json` even when the list is empty, plus `data/looksmapping_complete.html`. An exception before that save writes nothing. |
| `scrapers/selenium_scraper_robust.py` | ChromeDriver through webdriver-manager, New York, and hot, age, and gender. Writes `data/restaurant_data.json`, including an empty list, and `data/looksmapping_complete.html` when the loop finishes. |
| `scrapers/neighborhood_analyzer.py` | Does not scrape. Reads `data/restaurant_data.json`, keeps its Manhattan list, and prints attractiveness and age highest-first. The gender table is lowest-first, and the comment says a lower score means more female. |

## Data Structure

`data/restaurant_data.json` currently holds the fallback sample. Each row has `name`, `hood`, `attractive_score`, `gender_score`, and `age_score`.

`data/rankings_data.json` is grouped by city (`ny`, `la`, `sf`), then by `hot`, `age`, and `gender`. Each of those has `top` and `bottom` lists. An entry has `name`, `hood`, `category`, `attractive_score`, `age_score`, `gender_score`, `faces`, `lat`, and `long`.

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

`scrapers/neighborhood_analyzer.py` groups the rows in `data/restaurant_data.json` by neighborhood and prints three tables. Attractiveness and age are sorted with the highest average first. Gender is sorted with the lowest average first. It only keeps neighborhoods in its Manhattan list.

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
