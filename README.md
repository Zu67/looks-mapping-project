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
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── basic_scraper.py                   # Simple HTTP-based scraper
├── comprehensive_map_scraper.py        # Advanced Playwright-based scraper
├── selenium_scraper.py                # Selenium WebDriver scraper
├── selenium_scraper_robust.py         # Enhanced Selenium scraper
├── simple_scraper.py                  # Minimal scraper implementation
├── playwright_scraper.py              # Playwright automation scraper
├── requests_html_scraper.py           # Requests-HTML based scraper
├── neighborhood_analyzer.py           # Data analysis and statistics
├── extract_data.py                    # Data extraction utilities
├── map_scraper.py                     # Map-specific scraping logic
├── pin_scraper.py                     # Pin-based data extraction
├── scraper.py                         # Main scraper interface
└── restaurant_data.json               # Output data file
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
python basic_scraper.py
```

This will:
- Fetch the LooksMapping website
- Extract restaurant data from JavaScript objects
- Save results to `restaurant_data.json`

### Advanced Scraping with Playwright

For comprehensive data extraction with browser automation:

```bash
python comprehensive_map_scraper.py
```

This will:
- Launch a browser and navigate to the website
- Interact with the map interface
- Extract data from multiple viewing modes (hot, age, gender)
- Collect comprehensive restaurant data

### Selenium-based Scraping

For traditional browser automation:

```bash
python selenium_scraper.py
```

### Data Analysis

After scraping, analyze the collected data:

```bash
python neighborhood_analyzer.py
```

This will provide statistical analysis of Manhattan neighborhoods.

## Scraping Methods

### 1. Basic HTTP Scraper (`basic_scraper.py`)
- **Method**: HTTP requests with BeautifulSoup parsing
- **Pros**: Fast, lightweight, no browser required
- **Cons**: Limited to static content, may miss dynamic data
- **Use Case**: Quick data extraction when JavaScript execution isn't needed

### 2. Playwright Scraper (`comprehensive_map_scraper.py`)
- **Method**: Full browser automation with Playwright
- **Pros**: Handles dynamic content, can interact with complex interfaces
- **Cons**: Slower, requires browser installation
- **Use Case**: Comprehensive data extraction with map interaction

### 3. Selenium Scraper (`selenium_scraper.py`)
- **Method**: WebDriver automation with Selenium
- **Pros**: Mature ecosystem, good debugging tools
- **Cons**: Requires driver management, slower than Playwright
- **Use Case**: When you need Selenium-specific features

## Data Structure

The scraped data is saved in `restaurant_data.json` with the following structure:

```json
[
  {
    "name": "Restaurant Name",
    "hood": "Neighborhood",
    "attractive_score": "8.5",
    "age_score": "7.2",
    "gender_score": "6.8",
    "cuisine": "Italian",
    "score": "8.5",
    "reviewers": "150 reviewers",
    "lat": 40.7589,
    "long": -73.9851
  }
]
```

### Field Descriptions

- **name**: Restaurant name
- **hood**: Manhattan neighborhood
- **attractive_score**: Attractiveness rating (0-10)
- **age_score**: Age demographic score (0-10)
- **gender_score**: Gender ratio score (0-10, lower = more female)
- **cuisine**: Restaurant cuisine type
- **score**: Overall rating
- **reviewers**: Number of reviewers
- **lat/long**: Geographic coordinates

## Configuration

### Browser Settings

For headless operation, modify the browser launch options:

```python
# In comprehensive_map_scraper.py
browser = await p.chromium.launch(headless=True)  # Set to True for headless

# In selenium_scraper.py
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

The `neighborhood_analyzer.py` script provides statistical analysis:

- **Attractiveness Rankings**: Neighborhoods ranked by average attractiveness
- **Age Demographics**: Areas with younger vs. older demographics  
- **Gender Ratios**: Neighborhoods with different gender distributions

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

## Changelog

- **v1.0**: Initial release with basic scraping functionality
- **v1.1**: Added Playwright-based comprehensive scraper
- **v1.2**: Enhanced error handling and data analysis
- **v1.3**: Added neighborhood analysis and statistical reporting
