#!/usr/bin/env python3
"""
Main scraping script for LooksMapping Scraper.

This script provides a command-line interface for scraping restaurant data
from LooksMapping.com using different scraping methods.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scrapers import HttpScraper, SeleniumScraper, PlaywrightScraper
from utils.config import load_config
from utils.helpers import deduplicate_restaurants

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function for the scraping script."""
    parser = argparse.ArgumentParser(
        description="Scrape restaurant data from LooksMapping.com",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/scrape.py --method http
  python scripts/scrape.py --method selenium --headless
  python scripts/scrape.py --method playwright --output data/restaurants.json
        """
    )
    
    # Scraping method
    parser.add_argument(
        "--method",
        choices=["http", "selenium", "playwright"],
        default="http",
        help="Scraping method to use (default: http)"
    )
    
    # Output options
    parser.add_argument(
        "--output", "-o",
        default="restaurant_data.json",
        help="Output file path (default: restaurant_data.json)"
    )
    
    # Browser options
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)"
    )
    
    # Data options
    parser.add_argument(
        "--deduplicate",
        action="store_true",
        help="Remove duplicate restaurants"
    )
    
    parser.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Output format (default: json)"
    )
    
    # Logging options
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress output except errors"
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    
    try:
        # Load configuration
        config = load_config()
        
        # Override config with command line arguments
        if args.headless:
            config.scraper_headless = True
        if args.timeout:
            config.scraper_timeout = args.timeout
        
        # Create scraper instance
        scraper = create_scraper(args.method, config)
        
        if not scraper.is_available():
            logger.error(f"Scraper {args.method} is not available")
            sys.exit(1)
        
        # Perform scraping
        logger.info(f"Starting scraping with {args.method} method...")
        restaurants = scraper.scrape()
        
        if not restaurants:
            logger.warning("No restaurants found")
            sys.exit(1)
        
        # Deduplicate if requested
        if args.deduplicate:
            original_count = len(restaurants)
            restaurants = deduplicate_restaurants(restaurants)
            logger.info(f"Removed {original_count - len(restaurants)} duplicate restaurants")
        
        # Save results
        output_path = save_results(restaurants, args.output, args.format)
        
        logger.info(f"Scraping completed successfully!")
        logger.info(f"Found {len(restaurants)} restaurants")
        logger.info(f"Results saved to {output_path}")
        
        # Print summary
        print_summary(restaurants)
        
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        sys.exit(1)


def create_scraper(method: str, config) -> Optional[object]:
    """
    Create scraper instance based on method.
    
    Args:
        method: Scraping method name
        config: Configuration instance
        
    Returns:
        Scraper instance or None if method not supported
    """
    if method == "http":
        return HttpScraper(config)
    elif method == "selenium":
        return SeleniumScraper(config)
    elif method == "playwright":
        return PlaywrightScraper(config)
    else:
        logger.error(f"Unsupported scraping method: {method}")
        return None


def save_results(restaurants: list, output_path: str, format_type: str) -> str:
    """
    Save scraping results to file.
    
    Args:
        restaurants: List of restaurant dictionaries
        output_path: Output file path
        format_type: Output format (json or csv)
        
    Returns:
        str: Path to saved file
    """
    try:
        if format_type == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(restaurants, f, indent=2, ensure_ascii=False)
        elif format_type == "csv":
            import pandas as pd
            df = pd.DataFrame(restaurants)
            df.to_csv(output_path, index=False)
        
        logger.info(f"Results saved to {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to save results: {e}")
        raise


def print_summary(restaurants: list) -> None:
    """
    Print summary of scraping results.
    
    Args:
        restaurants: List of restaurant dictionaries
    """
    if not restaurants:
        return
    
    # Count by neighborhood
    neighborhoods = {}
    for restaurant in restaurants:
        hood = restaurant.get("hood", "Unknown")
        neighborhoods[hood] = neighborhoods.get(hood, 0) + 1
    
    print(f"\n=== SCRAPING SUMMARY ===")
    print(f"Total restaurants: {len(restaurants)}")
    print(f"Neighborhoods found: {len(neighborhoods)}")
    
    # Show top neighborhoods
    top_neighborhoods = sorted(neighborhoods.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f"\nTop neighborhoods:")
    for hood, count in top_neighborhoods:
        print(f"  {hood}: {count} restaurants")
    
    # Show score ranges
    attractive_scores = [r.get("attractive_score", 0) for r in restaurants if r.get("attractive_score")]
    if attractive_scores:
        print(f"\nAttractiveness scores:")
        print(f"  Range: {min(attractive_scores):.1f} - {max(attractive_scores):.1f}")
        print(f"  Average: {sum(attractive_scores) / len(attractive_scores):.1f}")


if __name__ == "__main__":
    main()
