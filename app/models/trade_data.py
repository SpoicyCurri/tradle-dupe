# app/models/trade_data.py

import os
from app.services.trade_data_loader import TradeDataLoader

class TradeData:
    def __init__(self, app=None):
        self.app = app
        self.data_loader = None
        
        if app is not None:
            self.init_app(app)
            
    def init_app(self, app):
        """Initialize with Flask app config"""
        self.app = app
        
        csv_path = app.config['TRADE_DATA_PATH']
        metadata_path = app.config.get('COUNTRY_METADATA_PATH')
        processed_path = app.config.get('PROCESSED_DATA_PATH')
        
        force_data_reload = app.config['FORCE_DATA_RELOAD']
        
        # Initialize data loader
        self.data_loader = TradeDataLoader(
            csv_path=csv_path,
            country_metadata_path=metadata_path
        )
        
        # If we have a path for processed data, try to load it
        if processed_path and os.path.exists(processed_path) and not force_data_reload:
            self.data_loader.load_processed_data(processed_path)
        else:
            self.data_loader.load_data()
            self.data_loader.save_processed_data(processed_path)
        
    def get_countries_list(self):
        """Return a sorted list of all countries"""
        return sorted(list(self.data_loader.countries_data.keys()))
    
    def get_country_data(self, country_name):
        """Get data for a specific country"""
        return self.data_loader.countries_data.get(country_name)
    
    def get_all_countries_data(self):
        """Return the complete processed dataset"""
        return self.data_loader.countries_data
        
    # Game-specific methods
    def compare_countries(self, guess, target):
        """Compare two countries for game logic"""
        # Implementation of comparison logic
        # ...
    