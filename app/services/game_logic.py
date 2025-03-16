# app/services/game_logic.py

import random
import datetime
import hashlib
from math import radians, cos, sin, asin, sqrt

class TradleGame:
    def __init__(self, trade_data, max_guesses):
        """Initialize game with trade data"""
        self.trade_data = trade_data
        self.max_guesses = max_guesses
        
        # Get target country based on date (for daily challenge)
        self.target_country = self._get_daily_country()
        self.game_number = self._calculate_game_number()
        
    def _get_daily_country(self):
        """Get the daily target country based on current date"""
        # Get all countries
        countries = self.trade_data.get_countries_list()
        
        if not countries:
            raise ValueError("No countries available in trade data")
            
        # Use today's date as seed for random selection
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        
        # Create a consistent hash from the date
        seed = int(hashlib.md5(today.encode()).hexdigest(), 16) % 10000
        
        # Use the seed to select a country
        random.seed(seed)
        country = random.choice(countries)
        random.seed()  # Reset random seed
        
        return country
        
    def _calculate_game_number(self):
        """Calculate game number (days since launch)"""
        # Use a fixed start date (e.g., when you launched the game)
        start_date = datetime.datetime(2025, 3, 1)  # Example launch date
        today = datetime.datetime.now()
        delta = today - start_date
        return delta.days + 1
        
    def get_current_date_string(self):
        """Get formatted date string for display"""
        return datetime.datetime.now().strftime('%Y-%m-%d')
        
    def get_current_game_number(self):
        """Get current game number"""
        return self.game_number
        
    def check_guess(self, guess):
        """Process a guess and return results"""
        # Get data for both countries
        guess_data = self.trade_data.get_country_data(guess)
        target_data = self.trade_data.get_country_data(self.target_country)
        
        if not guess_data:
            raise ValueError(f"Unknown country: {guess}")
            
        # Check if correct
        is_correct = (guess == self.target_country)
        
        # Calculate distance
        distance = self._calculate_distance(
            guess_data['coordinates']['lat'], 
            guess_data['coordinates']['lng'],
            target_data['coordinates']['lat'], 
            target_data['coordinates']['lng']
        )
        
        # Calculate direction
        direction = self._calculate_direction(
            guess_data['coordinates']['lat'], 
            guess_data['coordinates']['lng'],
            target_data['coordinates']['lat'], 
            target_data['coordinates']['lng']
        )
        
        # Check export/import similarities
        common_exports = set(guess_data.get('top_exports', [])) & set(target_data.get('top_exports', []))
        
        # Check region matches
        region_match = guess_data.get('region', '') == target_data.get('region', '')
        subregion_match = guess_data.get('subregion', '') == target_data.get('subregion', '')
        
        # Prepare response
        result = {
            'guess': guess,
            'correct': is_correct,
            'distance': int(round(distance)),
            'direction': direction,
            'common_exports': list(common_exports),
            'region_match': region_match,
            'subregion_match': subregion_match
        }
            
        return result
        
    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points using Haversine formula"""
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers
        
        return c * r
        
    def _calculate_direction(self, lat1, lon1, lat2, lon2):
        """Calculate direction from point 1 to point 2"""
        # Calculate general direction
        lat_diff = lat2 - lat1
        lon_diff = lon2 - lon1
        
        # Determine cardinal direction
        if abs(lat_diff) < 0.001 and abs(lon_diff) < 0.001:
            return "same"
            
        directions = []
        if lat_diff > 0:
            directions.append("N")
        elif lat_diff < 0:
            directions.append("S")
            
        if lon_diff > 0:
            directions.append("E")
        elif lon_diff < 0:
            directions.append("W")
            
        return "".join(directions)
        
    def get_target_country(self):
        """Get target country (only for testing)"""
        return self.target_country
        
    def save_progress(self, data):
        """Save game progress"""
        # This would typically save to a database or session
        # For now, we just return success
        return True