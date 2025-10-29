# LooksMapping Scraper

A comprehensive web scraping toolkit for extracting restaurant data from LooksMapping.com, focusing on Manhattan restaurants with demographic metrics.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Features

- **Multiple Scraping Methods**: HTTP requests, Selenium WebDriver, and Playwright automation
- **Comprehensive Data Extraction**: Restaurant names, neighborhoods, attractiveness scores, age demographics, gender ratios
- **Neighborhood Analysis**: Statistical analysis of Manhattan neighborhoods by various metrics
- **Robust Error Handling**: Multiple fallback strategies for data extraction
- **CLI Interface**: Easy-to-use command-line tools for scraping and analysis
- **Type Safety**: Full type hints with mypy strict mode
- **Testing**: Comprehensive test coverage with pytest

## Requirements

- Python 3.8 or higher
- Chrome browser (for Selenium and Playwright scrapers)
- Internet connection

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/looksmapping-scraper.git
cd looksmapping-scraper
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install production dependencies
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### 4. Install Browser Dependencies

```bash
# Install Playwright browsers
playwright install

# Chrome driver is automatically managed by webdriver-manager
```

## Quick Start

### Basic Scraping

```bash
# Scrape using HTTP requests (fastest)
python scripts/scrape.py --method http

# Scrape using Selenium (handles dynamic content)
python scripts/scrape.py --method selenium --headless

# Scrape using Playwright (most comprehensive)
python scripts/scrape.py --method playwright
```

### Data Analysis

```bash
# Analyze scraped data
python scripts/analyze.py --input restaurant_data.json

# Get top neighborhoods by attractiveness
python scripts/analyze.py --input data.json --top 5 --metric avg_attractive

# Show correlation analysis
python scripts/analyze.py --input data.json --correlation --summary
```

## 📊 Data Structure

The scraped data is saved in JSON format with the following structure:

```json
[
  {
    "name": "Restaurant Name",
    "hood": "Neighborhood",
    "attractive_score": 8.5,
    "age_score": 7.2,
    "gender_score": 6.8,
    "cuisine": "Italian",
    "score": "8.5/10",
    "reviewers": "150 reviewers",
    "lat": 40.7589,
    "long": -73.9851,
    "source": "looksmapping.com",
    "scraped_at": "2023-11-30T10:00:00Z"
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
- **source**: Data source
- **scraped_at**: Timestamp of scraping

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env
```

Key configuration options:

```env
# Scraping Configuration
SCRAPER_TIMEOUT=30
SCRAPER_HEADLESS=true
SCRAPER_MAX_RETRIES=3
SCRAPER_DELAY=1.0

# Browser Configuration
BROWSER_WIDTH=1280
BROWSER_HEIGHT=800

# Data Configuration
DATA_OUTPUT_DIR=./data
DATA_FORMAT=json
```

### Command Line Options

```bash
# Scraping options
python scripts/scrape.py --method http --output data.json --format json

# Analysis options
python scripts/analyze.py --input data.json --output analysis.json --top 10
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
make test

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_scrapers/test_http_scraper.py -v
```

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Type checking
make type-check

# Run all quality checks
make pre-commit
```

## 📈 Analysis Features

### Neighborhood Rankings

The analyzer provides comprehensive neighborhood analysis:

- **Attractiveness Rankings**: Neighborhoods ranked by average attractiveness
- **Age Demographics**: Areas with younger vs. older demographics
- **Gender Ratios**: Neighborhoods with different gender distributions
- **Statistical Analysis**: Mean, median, standard deviation calculations
- **Correlation Analysis**: Relationships between different metrics

### Example Analysis Output

```
=== TOP 10 NEIGHBORHOODS BY ATTRACTIVENESS ===
neighborhood        avg_attractive  restaurant_count
SoHo                9.2            15
Upper East Side     8.9            12
West Village        8.7            18
Tribeca             8.5            8
Chelsea             8.3            10
```

## 🏗️ Architecture

### Project Structure

```
LooksMappingScraper/
├── src/
│   ├── scrapers/          # Scraping implementations
│   ├── analyzers/         # Data analysis tools
│   ├── models/           # Data models
│   └── utils/            # Utility functions
├── tests/                # Test suite
├── scripts/              # CLI scripts
├── docs/                 # Documentation
└── data/                 # Output data
```

### Scraping Methods

1. **HTTP Scraper** (`HttpScraper`)
   - Fast and lightweight
   - Uses requests and BeautifulSoup
   - Limited to static content

2. **Selenium Scraper** (`SeleniumScraper`)
   - Handles dynamic content
   - Uses Chrome WebDriver
   - Good for JavaScript-heavy sites

3. **Playwright Scraper** (`PlaywrightScraper`)
   - Most comprehensive
   - Advanced browser automation
   - Map interaction and popup handling

## Troubleshooting

### Common Issues

1. **"ChromeDriver not found"**
   ```bash
   # The project uses webdriver-manager to auto-download drivers
   pip install webdriver-manager
   ```

2. **"Playwright browsers not installed"**
   ```bash
   playwright install
   ```

3. **"No restaurants found"**
   - Check if the website structure has changed
   - Try different scraping methods
   - Verify internet connection

4. **"Timeout errors"**
   - Increase timeout values in configuration
   - Check if the website is accessible

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Set headless=False to see browser actions
python scripts/scrape.py --method selenium --verbose
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Run quality checks: `make pre-commit`
6. Commit your changes: `git commit -m "feat: add new feature"`
7. Push to the branch: `git push origin feature-name`
8. Submit a pull request

### Development Setup

```bash
# Complete development setup
make dev-setup

# Run CI pipeline locally
make ci
```


## Legal Notice

This project is for educational and research purposes. Please respect the website's terms of service and robots.txt file. Use reasonable delays between requests to avoid overloading the server.



## Changelog

- **v0.1.0** (2023-12-03): Initial release
  - HTTP, Selenium, and Playwright scrapers
  - Neighborhood analysis tools
  - CLI interface
  - Comprehensive testing suite
  - Full documentation

## 🙏 Acknowledgments

- [LooksMapping.com](https://looksmapping.com) for providing the data source
- [Playwright](https://playwright.dev/) for advanced browser automation
- [Selenium](https://selenium.dev/) for WebDriver automation
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
