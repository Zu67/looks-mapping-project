"""
Tests for neighborhood analyzer.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from analyzers.neighborhood_analyzer import NeighborhoodAnalyzer
from utils.config import Config


class TestNeighborhoodAnalyzer:
    """Test cases for NeighborhoodAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config()
        self.analyzer = NeighborhoodAnalyzer(self.config)
        
        # Sample restaurant data
        self.sample_restaurants = [
            {
                "name": "Restaurant 1",
                "hood": "SoHo",
                "attractive_score": 8.5,
                "age_score": 7.2,
                "gender_score": 6.8
            },
            {
                "name": "Restaurant 2",
                "hood": "SoHo",
                "attractive_score": 9.1,
                "age_score": 6.5,
                "gender_score": 7.2
            },
            {
                "name": "Restaurant 3",
                "hood": "Upper East Side",
                "attractive_score": 8.9,
                "age_score": 8.3,
                "gender_score": 5.5
            }
        ]
    
    def test_initialization(self):
        """Test analyzer initialization."""
        assert self.analyzer.config == self.config
        assert self.analyzer.logger is not None
    
    def test_analyze_neighborhoods(self):
        """Test neighborhood analysis."""
        df = self.analyzer.analyze_neighborhoods(self.sample_restaurants)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2  # SoHo and Upper East Side
        assert "neighborhood" in df.columns
        assert "avg_attractive" in df.columns
        assert "restaurant_count" in df.columns
    
    def test_calculate_neighborhood_statistics(self):
        """Test neighborhood statistics calculation."""
        neighborhoods = {
            "SoHo": self.sample_restaurants[:2],
            "Upper East Side": self.sample_restaurants[2:]
        }
        
        stats = self.analyzer._calculate_neighborhood_statistics(neighborhoods)
        
        assert len(stats) == 2
        assert all("neighborhood" in stat for stat in stats)
        assert all("avg_attractive" in stat for stat in stats)
        assert all("restaurant_count" in stat for stat in stats)
    
    def test_create_analysis_dataframe(self):
        """Test DataFrame creation."""
        stats = [
            {
                "neighborhood": "SoHo",
                "restaurant_count": 2,
                "avg_attractive": 8.8,
                "avg_age": 6.85,
                "avg_gender": 7.0
            }
        ]
        
        df = self.analyzer._create_analysis_dataframe(stats)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert df.iloc[0]["neighborhood"] == "SoHo"
        assert df.iloc[0]["restaurant_count"] == 2
    
    def test_get_top_neighborhoods(self):
        """Test getting top neighborhoods."""
        df = self.analyzer.analyze_neighborhoods(self.sample_restaurants)
        top_neighborhoods = self.analyzer.get_top_neighborhoods(df, "avg_attractive", 1)
        
        assert len(top_neighborhoods) == 1
        assert "neighborhood" in top_neighborhoods.columns
        assert "avg_attractive" in top_neighborhoods.columns
    
    def test_calculate_correlation_matrix(self):
        """Test correlation matrix calculation."""
        df = self.analyzer.analyze_neighborhoods(self.sample_restaurants)
        correlation_matrix = self.analyzer.calculate_correlation_matrix(df)
        
        assert isinstance(correlation_matrix, pd.DataFrame)
        assert not correlation_matrix.empty
    
    def test_generate_summary_statistics(self):
        """Test summary statistics generation."""
        df = self.analyzer.analyze_neighborhoods(self.sample_restaurants)
        summary = self.analyzer.generate_summary_statistics(df)
        
        assert isinstance(summary, dict)
        assert "total_neighborhoods" in summary
        assert "total_restaurants" in summary
        assert "avg_restaurants_per_neighborhood" in summary
    
    def test_load_restaurant_data_success(self):
        """Test successful data loading."""
        test_data = [{"name": "Test Restaurant", "hood": "SoHo"}]
        
        with patch('builtins.open', Mock()) as mock_open:
            with patch('json.load', return_value=test_data):
                restaurants = self.analyzer.load_restaurant_data("test.json")
                
                assert restaurants == test_data
                mock_open.assert_called_once_with("test.json", 'r', encoding='utf-8')
    
    def test_load_restaurant_data_file_not_found(self):
        """Test data loading when file not found."""
        with patch('builtins.open', side_effect=FileNotFoundError):
            restaurants = self.analyzer.load_restaurant_data("nonexistent.json")
            
            assert restaurants == []
    
    def test_save_analysis_json(self):
        """Test saving analysis as JSON."""
        df = self.analyzer.analyze_neighborhoods(self.sample_restaurants)
        
        with patch('builtins.open', Mock()) as mock_open:
            self.analyzer.save_analysis(df, "test.json")
            
            mock_open.assert_called_once()
    
    def test_save_analysis_csv(self):
        """Test saving analysis as CSV."""
        df = self.analyzer.analyze_neighborhoods(self.sample_restaurants)
        
        with patch('builtins.open', Mock()) as mock_open:
            self.analyzer.save_analysis(df, "test.csv")
            
            mock_open.assert_called_once()
    
    def test_create_visualization_data(self):
        """Test visualization data creation."""
        df = self.analyzer.analyze_neighborhoods(self.sample_restaurants)
        viz_data = self.analyzer.create_visualization_data(df)
        
        assert isinstance(viz_data, dict)
        assert "neighborhoods" in viz_data
        assert "attractiveness" in viz_data
        assert "summary" in viz_data
