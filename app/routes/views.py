from flask import Blueprint, render_template, current_app

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def index():
    """Main game page"""
    print("loading page")    
    return render_template(
        'index.html',
        treemap_data=current_app.treemap.treemap_data, 
        treemap_layout=current_app.treemap.treemap_layout
        )
