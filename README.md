# LooksMapping Scraper

A comprehensive web scraping toolkit for extracting restaurant data from LooksMapping.com, focusing on Manhattan restaurants with attractiveness, age, and gender demographic scores.

## Overview

This project provides multiple scraping approaches to extract restaurant data from LooksMapping.com, a website that maps restaurants in New York City with demographic and attractiveness metrics. The scrapers collect data including restaurant names, neighborhoods, attractiveness scores, age demographics, and gender ratios.

## Features

- **Multiple Scraping Methods**: Basic HTTP requests, Selenium WebDriver, and Playwright automation
- **Comprehensive Data Extraction**: Restaurant names, neighborhoods, attractiveness scores, age demographics, gender ratios
- **Neighborhood Analysis**: Statistical analysis of Manhattan neighborhoods by various metrics
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

The simplest way to start scraping:

```bash
python scrapers/basic_scraper.py
```

This will:
- Fetch the LooksMapping website
- Extract restaurant data from JavaScript objects
- Save results to `data/restaurant_data.json`

If extraction finds nothing, the script writes its built-in fallback rows. The `data/restaurant_data.json` in this repository is that fallback: Test Restaurant 1 and Test Restaurant 2.

`data/rankings_data.json` is a saved rankings object for New York, Los Angeles, and San Francisco. Each city has hot, age, and gender lists, with top and bottom entries.

### Advanced Scraping with Playwright

For comprehensive data extraction with browser automation:

```bash
python scrapers/comprehensive_map_scraper.py
```

This will:
- Launch a browser and navigate to the website
- Interact with the map interface
- Extract data from multiple viewing modes (hot, age, gender)
- Collect comprehensive restaurant data

### Selenium-based Scraping

For traditional browser automation:

```bash
python scrapers/selenium_scraper.py
```

### Data Analysis

After scraping, analyze the collected data:

```bash
python scrapers/neighborhood_analyzer.py
```

The script reads `data/restaurant_data.json`, keeps rows whose `hood` is in its Manhattan list, and prints average attractiveness, age, and gender scores by neighborhood. The file in the repository is the two-row fallback, so that report is SoHo and the Upper East Side from the sample.

## Scraping Methods

### 1. Basic HTTP Scraper (`scrapers/basic_scraper.py`)
- **Method**: HTTP requests with BeautifulSoup parsing
- **Pros**: Fast, lightweight, no browser required
- **Cons**: Limited to static content, may miss dynamic data
- **Use Case**: Quick data extraction when JavaScript execution isn't needed

### 2. Playwright Scraper (`scrapers/comprehensive_map_scraper.py`)
- **Method**: Full browser automation with Playwright
- **Pros**: Handles dynamic content, can interact with complex interfaces
- **Cons**: Slower, requires browser installation
- **Use Case**: Comprehensive data extraction with map interaction

### 3. Selenium Scraper (`scrapers/selenium_scraper.py`)
- **Method**: WebDriver automation with Selenium
- **Pros**: Mature ecosystem, good debugging tools
- **Cons**: Requires driver management, slower than Playwright
- **Use Case**: When you need Selenium-specific features

## Data Structure

`data/restaurant_data.json` currently holds the fallback sample. Each row has `name`, `hood`, `attractive_score`, `gender_score`, and `age_score`.

`data/rankings_data.json` is grouped by city (`ny`, `la`, `sf`), then by `hot`, `age`, and `gender`. Each of those has `top` and `bottom` lists. An entry has `name`, `hood`, `category`, `attractive_score`, `age_score`, `gender_score`, `faces`, `lat`, and `long`.

## Configuration

### Browser Settings

For headless operation, modify the browser launch options:

```python
# In scrapers/comprehensive_map_scraper.py
browser = await p.chromium.launch(headless=True)  # Set to True for headless

# In scrapers/selenium_scraper.py
chrome_options.add_argument("--headless")  # Uncomment for headless
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
   - Solution: The project uses webdriver-manager to auto-download drivers

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

This project is open source. Please use responsibly and in accordance with the target website's terms of service.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the code comments
3. Open an issue on GitHub

## History

Zu67 committed the scrapers on 2025-10-25 ("Initial commit: LooksMapping scraper project") and the documentation the same day ("feat: Add comprehensive documentation and clean up codebase").
