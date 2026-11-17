# LooksMapping Scraper

A web scraping toolkit for extracting restaurant data from LooksMapping.com. The saved rankings cover New York, Los Angeles, and San Francisco, with attractiveness, age, and gender scores.

## Overview

This project has several scrapers for LooksMapping.com. They look for restaurant names, neighborhoods, attractiveness scores, age scores, and gender scores. The saved rankings file includes New York, Los Angeles, and San Francisco.

## Features

- **Multiple Scraping Methods**: Basic HTTP requests, Selenium WebDriver, and Playwright automation
- **Comprehensive Data Extraction**: Restaurant names, neighborhoods, attractiveness scores, age demographics, gender ratios
- **Neighborhood Analysis**: `neighborhood_analyzer.py` averages the three scores by neighborhood for rows in `data/restaurant_data.json`
- **Robust Error Handling**: Multiple fallback strategies for data extraction
- **Data Export**: JSON output with structured restaurant data

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

The script reads `data/restaurant_data.json`, keeps rows whose `hood` is in its Manhattan list, and prints average attractiveness, age, and gender scores by neighborhood. The file in the repository is the two-row fallback, so that report is SoHo and the Upper East Side from the sample.

## Scraping Methods

### 1. Basic HTTP Scraper (`scrapers/basic_scraper.py`)
- **Method**: HTTP requests, then a regex for a JavaScript `rankings` object and a second regex for restaurant fields. BeautifulSoup is imported and not used.
- **Pros**: No browser required
- **Cons**: Only reads what is in the first HTML response, and only keeps New York from the rankings object
- **Use Case**: A fetch that does not run the map interface

### 2. Playwright Scraper (`scrapers/comprehensive_map_scraper.py`)
- **Method**: Full browser automation with Playwright
- **Pros**: Handles dynamic content, can interact with complex interfaces
- **Cons**: Slower, requires browser installation
- **Use Case**: Comprehensive data extraction with map interaction

### 3. Selenium Scraper (`scrapers/selenium_scraper.py`)
- **Method**: WebDriver automation with Selenium
- **Pros**: Mature ecosystem, good debugging tools
- **Cons**: Calls `webdriver.Chrome()` with no driver manager, so ChromeDriver has to be on the path
- **Use Case**: A visible Chrome session that selects New York and reads the hot, age, and gender modes

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

`scrapers/neighborhood_analyzer.py` groups the rows in `data/restaurant_data.json` by neighborhood and prints three tables: average `attractive_score`, average `age_score`, and average `gender_score`. It only keeps neighborhoods in its Manhattan list.

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
