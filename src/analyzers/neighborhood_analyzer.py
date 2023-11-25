"""
Neighborhood Analysis Module for LooksMapping Data

This module provides statistical analysis of Manhattan neighborhoods based on
restaurant data scraped from LooksMapping.com. It calculates averages for
attractiveness, age demographics, and gender ratios by neighborhood.
"""

import json
import statistics
from collections import defaultdict
from typing import List, Dict, Any, Optional, Tuple
import logging
import pandas as pd
import numpy as np

from ..utils.helpers import (
    is_manhattan_neighborhood, 
    group_by_neighborhood, 
    filter_manhattan_restaurants,
    safe_float
)
from ..utils.config import Config

logger = logging.getLogger(__name__)


class NeighborhoodAnalyzer:
    """
    Analyzer for Manhattan neighborhood restaurant data.
    
    This class provides comprehensive analysis of restaurant data by neighborhood,
    including statistical calculations, rankings, and data visualization.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize neighborhood analyzer.
        
        Args:
            config: Optional configuration instance
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def analyze_neighborhoods(self, restaurants: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Analyze Manhattan neighborhoods based on restaurant data.
        
        Args:
            restaurants: List of restaurant dictionaries
            
        Returns:
            pd.DataFrame: DataFrame with neighborhood statistics
        """
        self.logger.info("Starting Manhattan neighborhood analysis...")
        
        # Filter for Manhattan restaurants
        manhattan_restaurants = filter_manhattan_restaurants(restaurants)
        self.logger.info(f"Filtered to {len(manhattan_restaurants)} Manhattan restaurants")
        
        # Group restaurants by neighborhood
        neighborhoods = group_by_neighborhood(manhattan_restaurants)
        
        # Calculate statistics for each neighborhood
        neighborhood_stats = self._calculate_neighborhood_statistics(neighborhoods)
        
        # Create DataFrame and generate reports
        df = self._create_analysis_dataframe(neighborhood_stats)
        self._generate_analysis_reports(df)
        
        self.logger.info("Neighborhood analysis completed")
        return df
    
    def _calculate_neighborhood_statistics(self, neighborhoods: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Calculate statistical averages for each neighborhood.
        
        Args:
            neighborhoods: Dictionary mapping neighborhoods to restaurant lists
            
        Returns:
            List[Dict[str, Any]]: List of neighborhood statistics
        """
        neighborhood_stats = []
        
        for hood, restaurants in neighborhoods.items():
            if not restaurants:  # Skip empty neighborhoods
                continue
            
            try:
                # Extract scores
                attractive_scores = [safe_float(r.get("attractive_score", 0)) for r in restaurants]
                age_scores = [safe_float(r.get("age_score", 0)) for r in restaurants]
                gender_scores = [safe_float(r.get("gender_score", 0)) for r in restaurants]
                
                # Calculate averages
                avg_attractive = statistics.mean(attractive_scores) if attractive_scores else 0
                avg_age = statistics.mean(age_scores) if age_scores else 0
                avg_gender = statistics.mean(gender_scores) if gender_scores else 0
                
                # Calculate additional statistics
                median_attractive = statistics.median(attractive_scores) if attractive_scores else 0
                std_attractive = statistics.stdev(attractive_scores) if len(attractive_scores) > 1 else 0
                
                # Store the stats
                neighborhood_stats.append({
                    "neighborhood": hood,
                    "restaurant_count": len(restaurants),
                    "avg_attractive": round(avg_attractive, 2),
                    "avg_age": round(avg_age, 2),
                    "avg_gender": round(avg_gender, 2),
                    "median_attractive": round(median_attractive, 2),
                    "std_attractive": round(std_attractive, 2),
                    "attractive_scores": attractive_scores,
                    "age_scores": age_scores,
                    "gender_scores": gender_scores
                })
                
            except statistics.StatisticsError as e:
                self.logger.warning(f"Error calculating statistics for {hood}: {e}")
                continue
        
        self.logger.info(f"Calculated statistics for {len(neighborhood_stats)} neighborhoods")
        return neighborhood_stats
    
    def _create_analysis_dataframe(self, neighborhood_stats: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Create a pandas DataFrame from neighborhood statistics.
        
        Args:
            neighborhood_stats: List of neighborhood statistics
            
        Returns:
            pd.DataFrame: DataFrame with neighborhood statistics
        """
        df = pd.DataFrame(neighborhood_stats)
        
        if df.empty:
            self.logger.warning("No neighborhood statistics to display")
            return df
        
        # Sort by different metrics for analysis
        df = df.sort_values("restaurant_count", ascending=False)
        
        return df
    
    def _generate_analysis_reports(self, df: pd.DataFrame) -> None:
        """
        Generate and display analysis reports.
        
        Args:
            df: DataFrame with neighborhood statistics
        """
        if df.empty:
            self.logger.warning("No data available for analysis")
            return
        
        # Sort by different metrics
        hottest_neighborhoods = df.sort_values("avg_attractive", ascending=False)
        youngest_neighborhoods = df.sort_values("avg_age", ascending=False)
        most_female_neighborhoods = df.sort_values("avg_gender", ascending=True)  # Lower = more female
        
        # Display results
        self.logger.info("\n=== MANHATTAN NEIGHBORHOODS RANKED BY ATTRACTIVENESS ===")
        print("\n=== MANHATTAN NEIGHBORHOODS RANKED BY ATTRACTIVENESS ===")
        print(hottest_neighborhoods[["neighborhood", "avg_attractive", "restaurant_count"]].to_string(index=False))
        
        self.logger.info("\n=== MANHATTAN NEIGHBORHOODS RANKED BY YOUTH ===")
        print("\n=== MANHATTAN NEIGHBORHOODS RANKED BY YOUTH ===")
        print(youngest_neighborhoods[["neighborhood", "avg_age", "restaurant_count"]].to_string(index=False))
        
        self.logger.info("\n=== MANHATTAN NEIGHBORHOODS RANKED BY FEMALE RATIO ===")
        print("\n=== MANHATTAN NEIGHBORHOODS RANKED BY FEMALE RATIO ===")
        print(most_female_neighborhoods[["neighborhood", "avg_gender", "restaurant_count"]].to_string(index=False))
    
    def get_top_neighborhoods(self, df: pd.DataFrame, metric: str = "avg_attractive", top_n: int = 10) -> pd.DataFrame:
        """
        Get top neighborhoods by a specific metric.
        
        Args:
            df: DataFrame with neighborhood statistics
            metric: Metric to rank by
            top_n: Number of top neighborhoods to return
            
        Returns:
            pd.DataFrame: Top neighborhoods by metric
        """
        if df.empty:
            return df
        
        ascending = metric == "avg_gender"  # Lower gender score = more female
        return df.nlargest(top_n, metric) if not ascending else df.nsmallest(top_n, metric)
    
    def calculate_correlation_matrix(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate correlation matrix between different metrics.
        
        Args:
            df: DataFrame with neighborhood statistics
            
        Returns:
            pd.DataFrame: Correlation matrix
        """
        if df.empty:
            return pd.DataFrame()
        
        # Select numeric columns for correlation
        numeric_cols = ["avg_attractive", "avg_age", "avg_gender", "restaurant_count"]
        available_cols = [col for col in numeric_cols if col in df.columns]
        
        if len(available_cols) < 2:
            self.logger.warning("Not enough numeric columns for correlation analysis")
            return pd.DataFrame()
        
        return df[available_cols].corr()
    
    def generate_summary_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate summary statistics for the dataset.
        
        Args:
            df: DataFrame with neighborhood statistics
            
        Returns:
            Dict[str, Any]: Summary statistics
        """
        if df.empty:
            return {}
        
        summary = {
            "total_neighborhoods": len(df),
            "total_restaurants": df["restaurant_count"].sum(),
            "avg_restaurants_per_neighborhood": round(df["restaurant_count"].mean(), 2),
            "most_restaurants_neighborhood": df.loc[df["restaurant_count"].idxmax(), "neighborhood"],
            "highest_attractiveness": round(df["avg_attractive"].max(), 2),
            "lowest_attractiveness": round(df["avg_attractive"].min(), 2),
            "attractiveness_std": round(df["avg_attractive"].std(), 2)
        }
        
        return summary
    
    def save_analysis(self, df: pd.DataFrame, output_path: str) -> None:
        """
        Save analysis results to file.
        
        Args:
            df: DataFrame with analysis results
            output_path: Path to save the results
        """
        try:
            if output_path.endswith('.json'):
                df.to_json(output_path, orient='records', indent=2)
            elif output_path.endswith('.csv'):
                df.to_csv(output_path, index=False)
            else:
                # Default to JSON
                df.to_json(output_path + '.json', orient='records', indent=2)
            
            self.logger.info(f"Analysis results saved to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving analysis results: {e}")
    
    def load_restaurant_data(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load restaurant data from JSON file.
        
        Args:
            file_path: Path to JSON file containing restaurant data
            
        Returns:
            List[Dict[str, Any]]: List of restaurant dictionaries
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.info(f"Loaded {len(data)} restaurants from {file_path}")
            return data
            
        except FileNotFoundError:
            self.logger.error(f"Data file {file_path} not found")
            return []
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in {file_path}: {e}")
            return []
    
    def create_visualization_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Create data structure suitable for visualization.
        
        Args:
            df: DataFrame with neighborhood statistics
            
        Returns:
            Dict[str, Any]: Visualization data structure
        """
        if df.empty:
            return {}
        
        return {
            "neighborhoods": df["neighborhood"].tolist(),
            "attractiveness": df["avg_attractive"].tolist(),
            "age_demographics": df["avg_age"].tolist(),
            "gender_ratios": df["avg_gender"].tolist(),
            "restaurant_counts": df["restaurant_count"].tolist(),
            "summary": self.generate_summary_statistics(df)
        }
