# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2023-12-03

### Added
- Initial release of LooksMapping Scraper
- HTTP-based scraper using requests and BeautifulSoup
- Selenium WebDriver scraper for dynamic content
- Playwright scraper with advanced browser automation
- Neighborhood analysis tools with statistical calculations
- Command-line interface for scraping and analysis
- Comprehensive test suite with pytest
- Full type hints with mypy strict mode
- GitHub Actions CI/CD pipeline
- Complete documentation with examples
- Configuration management with environment variables
- Data validation and cleaning utilities
- Multiple output formats (JSON, CSV)
- Manhattan neighborhood filtering
- Correlation analysis and summary statistics
- Robust error handling and retry mechanisms
- Browser automation with map interaction
- Data deduplication and validation
- Performance optimizations
- Security scanning and code quality checks

### Features
- **Multiple Scraping Methods**: HTTP, Selenium, and Playwright
- **Comprehensive Data Extraction**: Restaurant names, neighborhoods, scores
- **Statistical Analysis**: Neighborhood rankings and correlations
- **CLI Tools**: Easy-to-use command-line interface
- **Type Safety**: Full type hints and mypy compliance
- **Testing**: Comprehensive test coverage
- **CI/CD**: Automated testing and deployment
- **Documentation**: Complete API docs and examples

### Technical Details
- Python 3.8+ support
- Modern packaging with pyproject.toml
- Environment-based configuration
- Async support for Playwright
- Mock-based testing
- Code quality tools (black, flake8, mypy)
- Security scanning (safety, bandit)
- Coverage reporting
- Pre-commit hooks
