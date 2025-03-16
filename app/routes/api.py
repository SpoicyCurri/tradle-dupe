from flask import Blueprint, jsonify, request

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/countries')
def get_countries():
    """Get list of all countries for autocomplete"""
    from flask import current_app
    return jsonify(current_app.trade_data.get_countries_list())

@api_bp.route('/guess', methods=['POST'])
def check_guess():
    from flask import current_app
    
    data = request.get_json()
    guess = data.get('guess')
    
    if not guess:
        return jsonify({'error': 'No guess provided'}), 400
        
    try:
        result = current_app.game.check_guess(guess)
        print(result)
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
