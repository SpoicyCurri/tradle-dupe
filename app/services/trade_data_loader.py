import pandas as pd
import os
import json
import logging
from collections import defaultdict

class TradeDataLoader:
    """
    Loads and processes trade data from CSV into a game-friendly format for Tradle
    """
    def __init__(self, csv_path, country_metadata_path=None):
        """
        Initialize the data loader
        
        Parameters:
        - csv_path: Path to the CSV file with trade data
        - country_metadata_path: Optional path to JSON with country metadata (coordinates, etc.)
        """
        self.csv_path = csv_path
        self.country_metadata_path = country_metadata_path
        self.logger = logging.getLogger(__name__)
        self.raw_data = None
        self.country_metadata = None
        self.countries_data = {}
        
    def load_data(self):
        """Load trade data from CSV and process it"""
        try:
            self.logger.info(f"Loading trade data from {self.csv_path}")
            self.raw_data = pd.read_csv(self.csv_path, encoding_errors='ignore')
            
            # Load country metadata if available
            if self.country_metadata_path and os.path.exists(self.country_metadata_path):
                self.country_metadata = pd.read_csv(self.country_metadata_path)
                self.raw_data = self.raw_data.merge(self.country_metadata, left_on="reporterISO", right_on="country_iso")
                
            self.process_data()
        except Exception as e:
            self.logger.error(f"Error loading trade data: {str(e)}")
            raise
            
    def process_data(self):
        """Transform raw CSV data into game-friendly format specifically for your data structure"""
        # Initialize data structure
        processed_data = defaultdict(lambda: {
            'exports': {},
            'coordinates': {'lat': 0, 'lng': 0},
            'region': '',
            'subregion': '',
            'country_iso': '',
            'country_code': ''
        })
        
        # Process each row in the data
        for _, row in self.raw_data.iterrows():
            country_iso = row['reporterISO']
            country_name = row['reporterDesc']
            country_code = row['reporterCode']
            commodity_name = row['cmdDesc']
            value = row['fobvalue'] if not pd.isna(row['fobvalue']) else row['primaryValue']
            coordinates = row['latlng']
            region = row['region']
            subregion = row['subregion']
            
            # Skip rows with missing essential data
            if pd.isna(country_name) or pd.isna(commodity_name) or pd.isna(value):
                continue
            
            # Process coordinates
            # Remove brackets and split by comma
            coordinates = coordinates.strip('[]').split(',')
            # Convert each string to float
            coordinates = [float(coord.strip()) for coord in coordinates]
            
            # Add country info
            processed_data[country_name]['iso'] = country_iso
            processed_data[country_name]['country_code'] = country_code
            processed_data[country_name]['continent'] = region
            processed_data[country_name]['subregion'] = subregion
            processed_data[country_name]['coordinates'] = {'lat': coordinates[0], 'lng': coordinates[1]}
            
            # Add or update export value for this product
            if commodity_name in processed_data[country_name]['exports']:
                processed_data[country_name]['exports'][commodity_name] += value
            else:
                processed_data[country_name]['exports'][commodity_name] = value
        
        # Post-processing: calculate top products and percentages
        for country, data in processed_data.items():
            # Sort exports by value (descending)
            data['exports'] = dict(sorted(
                data['exports'].items(), 
                key=lambda x: x[1], 
                reverse=True
            ))
            
            # Calculate total export values
            total_exports = sum(data['exports'].values())
            
            # Calculate percentages for each product
            if total_exports > 0:
                data['export_percentages'] = {
                    commodity_name: (value / total_exports * 100) 
                    for commodity_name, value in data['exports'].items()
                }
            
            # Get top 5 products for display
            data['top_exports'] = list(data['exports'].keys())[:5] if data['exports'] else []
            
            # Add total values
            data['total_exports'] = total_exports
        
        self.countries_data = dict(processed_data)
        self.logger.info(f"Processed {len(self.countries_data)} countries")
    
    def save_processed_data(self, output_path):
        """Save processed data to JSON file for faster loading"""
        with open(output_path, 'w') as f:
            json.dump(self.countries_data, f)
        self.logger.info(f"Saved processed data to {output_path}")
    
    def load_processed_data(self, input_path):
        """Load pre-processed data from JSON file"""
        if os.path.exists(input_path):
            with open(input_path, 'r') as f:
                self.countries_data = json.load(f)
            self.logger.info(f"Loaded pre-processed data from {input_path}")
            return True
        return False
