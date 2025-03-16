import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_for_development_only')
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    
    # Data settings
    TRADE_DATA_PATH = os.path.join('app', STATIC_FOLDER, 'data', 'tradedata_uncomtrade.csv')
    COUNTRY_METADATA_PATH = os.path.join('app', STATIC_FOLDER, 'data', 'country_metadata.csv')
    PROCESSED_DATA_PATH = os.path.join('app', STATIC_FOLDER, 'data', 'trade_data.json')
    FORCE_DATA_RELOAD = os.environ.get('FORCE_DATA_RELOAD', True)
    
    # Game settings
    MAX_GUESSES = 6
    DAILY_RESET = True
    DAILY_RESET_TIME = "00:00:00"  # UTC time for daily country reset
    
    # API settings
    JSON_SORT_KEYS = False  # Preserve the order of JSON keys in responses
    
    # Rate limiting to prevent abuse
    RATELIMIT_DEFAULT = "100 per day;30 per hour;5 per minute"


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    EXPLAIN_TEMPLATE_LOADING = True  # Helpful for debugging template issues
    TEMPLATES_AUTO_RELOAD = True
    

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False  # Disable CSRF during testing
    TRADE_DATA_PATH = os.path.join('tests', 'test_data', 'test_trade_data.csv')
    

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # In production, use environment variables for sensitive data
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Session security settings for production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # Error logging config
    LOG_LEVEL = "ERROR"
    

# Configuration dictionary to easily select config class
config_by_name = {
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'prod': ProductionConfig,
    'default': DevelopmentConfig
}