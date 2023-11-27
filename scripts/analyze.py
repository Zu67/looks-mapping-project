#!/usr/bin/env python3
"""
Analysis script for LooksMapping Scraper.

This script provides a command-line interface for analyzing restaurant data
and generating neighborhood statistics.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analyzers import NeighborhoodAnalyzer
from utils.config import load_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function for the analysis script."""
    parser = argparse.ArgumentParser(
        description="Analyze restaurant data from LooksMapping.com",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/analyze.py --input restaurant_data.json
  python scripts/analyze.py --input data.json --output analysis.json --format json
  python scripts/analyze.py --input data.json --top 5 --metric avg_attractive
        """
    )
    
    # Input options
    parser.add_argument(
        "--input", "-i",
        default="restaurant_data.json",
        help="Input JSON file with restaurant data (default: restaurant_data.json)"
    )
    
    # Output options
    parser.add_argument(
        "--output", "-o",
        default="neighborhood_analysis.json",
        help="Output file for analysis results (default: neighborhood_analysis.json)"
    )
    
    parser.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Output format (default: json)"
    )
    
    # Analysis options
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Number of top neighborhoods to show (default: 10)"
    )
    
    parser.add_argument(
        "--metric",
        choices=["avg_attractive", "avg_age", "avg_gender", "restaurant_count"],
        default="avg_attractive",
        help="Metric to rank neighborhoods by (default: avg_attractive)"
    )
    
    parser.add_argument(
        "--correlation",
        action="store_true",
        help="Show correlation matrix between metrics"
    )
    
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show summary statistics"
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
        
        # Create analyzer
        analyzer = NeighborhoodAnalyzer(config)
        
        # Load restaurant data
        logger.info(f"Loading restaurant data from {args.input}...")
        restaurants = analyzer.load_restaurant_data(args.input)
        
        if not restaurants:
            logger.error("No restaurant data found")
            sys.exit(1)
        
        # Perform analysis
        logger.info("Performing neighborhood analysis...")
        df = analyzer.analyze_neighborhoods(restaurants)
        
        if df.empty:
            logger.warning("No neighborhoods found for analysis")
            sys.exit(1)
        
        # Show top neighborhoods
        top_neighborhoods = analyzer.get_top_neighborhoods(df, args.metric, args.top)
        print(f"\n=== TOP {args.top} NEIGHBORHOODS BY {args.metric.upper()} ===")
        print(top_neighborhoods[["neighborhood", args.metric, "restaurant_count"]].to_string(index=False))
        
        # Show correlation matrix if requested
        if args.correlation:
            correlation_matrix = analyzer.calculate_correlation_matrix(df)
            if not correlation_matrix.empty:
                print(f"\n=== CORRELATION MATRIX ===")
                print(correlation_matrix.to_string())
        
        # Show summary statistics if requested
        if args.summary:
            summary = analyzer.generate_summary_statistics(df)
            print(f"\n=== SUMMARY STATISTICS ===")
            for key, value in summary.items():
                print(f"{key}: {value}")
        
        # Save analysis results
        analyzer.save_analysis(df, args.output)
        
        logger.info(f"Analysis completed successfully!")
        logger.info(f"Results saved to {args.output}")
        
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
