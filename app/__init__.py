# __init__.py
from flask import Flask

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Get configurations
    from app.config.config import config_by_name
    app.config.from_object(config_by_name[config_name])
    
    # Register blueprints
    from app.routes.api import api_bp
    from app.routes.views import views_bp
    app.register_blueprint(api_bp)
    app.register_blueprint(views_bp)
    
    # Initialize data
    from app.models.trade_data import TradeData
    from app.services.game_logic import TradleGame
    from app.services.trade_charts import TradeTreemap

    app.trade_data = TradeData(app)
    app.game = TradleGame(app.trade_data, app.config['MAX_GUESSES'])
    app.treemap = TradeTreemap(app.trade_data, app.game)
    
    return app