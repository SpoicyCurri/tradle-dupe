import plotly
import plotly.express
import json
import pandas
import os

class TradeTreemap:
    """Class for generating country export treemaps for the Tradle game"""
    
    def __init__(self, trade_data, game):
        """
        Initialize with a trade data to source the data
        
        Args:
            trade_data: Instance of TradeData
        """
        self.trade_data = trade_data
        self.target_country = game.target_country
    
        # Get export data from the trade data
        self.country_data = self.trade_data.get_country_data(self.target_country)
        
        # Create and return the treemap
        self.treemap_data, self.treemap_layout = self._create_treemap(self.country_data)
    
    def _prepare_data_for_treemap(self, country_data):
        """
        Transform trade data into a DataFrame suitable for a treemap
        
        Args:
            trade_data: Trade data from TradeDataManager
            
        Returns:
            Pandas DataFrame with categories, products, values, etc.
        """
        
        commodities = []
        values = []
        percentages = []
        
        # Process your trade data structure
        for commodity_name in country_data['exports'].keys():
            commodities.append(commodity_name)
            values.append(country_data['exports'].get(commodity_name, 0))
            percentages.append(country_data['export_percentages'].get(commodity_name, 0))
        
        return pandas.DataFrame({
            'commodity': commodities,
            'value': values,
            'percentage': percentages
        })
    
    def _create_treemap(self, country_data):
        """
        Create a treemap visualization from a prepared DataFrame
        
        Args:
            df: DataFrame with trade data
            
        Returns:
            JSON string of Plotly figure
        """
        # Transform the trade data into a format suitable for the treemap
        df = self._prepare_data_for_treemap(country_data)
        
        fig = plotly.express.treemap(
            df,
            path=['commodity'],
            values='value',
            color='percentage',
            color_continuous_scale='viridis_r',
            hover_data=['percentage']
        )
        
        fig.update_layout(
            margin=dict(t=50, l=25, r=25, b=25),
            font=dict(size=14)
        )
        
        self._save_png(fig)
        
        data_json = json.dumps(fig.data, cls=plotly.utils.PlotlyJSONEncoder)
        layout_json = json.dumps(fig.layout, cls=plotly.utils.PlotlyJSONEncoder)
        
        return data_json, layout_json
    
    def _save_png(self, figure):
        
        images_dir = os.path.join('app', 'static', 'images')
        
        if not os.path.exists(images_dir):
            os.mkdir(images_dir)
            
        figure.write_image(os.path.join(images_dir, "treemap.png"))
        