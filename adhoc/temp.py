from flask import Flask, render_template, request, jsonify, session
import random
import json
import os
from difflib import get_close_matches

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

MAX_GUESSES = 6

def start_new_game():
    """Initialize a new game session."""
    target_country = random.choice(COUNTRIES)
    session['target_country'] = target_country
    session['guesses_made'] = []
    session['game_over'] = False
    session['won'] = False
    return COUNTRY_DATA[target_country]["exports"]

def compare_exports(guess_exports, target_exports):
    """Compare the export profiles between two countries."""
    similarity = {}
    for product, percentage in guess_exports.items():
        if product in target_exports:
            target_percentage = target_exports[product]
            diff = abs(percentage - target_percentage)
            if diff < 2:
                similarity[product] = "very similar"
            elif diff < 5:
                similarity[product] = "similar"
            else:
                similarity[product] = "different"
        else:
            similarity[product] = "not in target"
    
    return similarity

def generate_feedback(guess):
    """Generate feedback comparing the guess to the target country."""
    guess_data = COUNTRY_DATA[guess]
    target_data = COUNTRY_DATA[session['target_country']]
    
    feedback = {
        "country": guess,
        "continent": {
            "value": guess_data["continent"],
            "correct": guess_data["continent"] == target_data["continent"]
        },
        "gdp_rank": {
            "value": guess_data["gdp_rank"],
            "direction": "correct" if guess_data["gdp_rank"] == target_data["gdp_rank"] else 
                        ("higher" if guess_data["gdp_rank"] < target_data["gdp_rank"] else "lower")
        },
        "exports_similarity": compare_exports(guess_data["exports"], target_data["exports"]),
        "guesses_remaining": MAX_GUESSES - len(session['guesses_made'])
    }
    
    return feedback

# @app.route('/')
def index():
    """Main game page."""
    if 'target_country' not in session:
        exports = start_new_game()
    else:
        exports = COUNTRY_DATA[session['target_country']]["exports"]
    
    return render_template('index.html', 
                          exports=exports, 
                          guesses=session.get('guesses_made', []),
                          game_over=session.get('game_over', False),
                          won=session.get('won', False),
                          max_guesses=MAX_GUESSES)

# @app.route('/guess', methods=['POST'])
def make_guess():
    """Process a player's guess."""
    if session.get('game_over', False):
        return jsonify({
            "error": "Game is already over. Start a new game."
        })
    
    guess = request.form.get('country', '').strip()
    
    # Handle close matches and case insensitivity
    close_matches = get_close_matches(guess, COUNTRIES, n=1, cutoff=0.8)
    if guess.lower() in [country.lower() for country in COUNTRIES]:
        matched_country = next(country for country in COUNTRIES if country.lower() == guess.lower())
        guess = matched_country
    elif close_matches:
        guess = close_matches[0]
    
    if guess not in COUNTRIES:
        return jsonify({
            "error": f"'{guess}' is not in our database. Try another country."
        })
    
    if guess in session.get('guesses_made', []):
        return jsonify({
            "error": f"You've already guessed {guess}. Try another country."
        })
    
    guesses_made = session.get('guesses_made', [])
    guesses_made.append(guess)
    session['guesses_made'] = guesses_made
    
    if guess == session['target_country']:
        session['game_over'] = True
        session['won'] = True
        return jsonify({
            "message": f"Congratulations! You guessed correctly in {len(guesses_made)} tries!",
            "game_over": True,
            "won": True,
            "target_country": session['target_country'],
            "feedback": generate_feedback(guess)
        })
    
    feedback = generate_feedback(guess)
    
    if len(guesses_made) >= MAX_GUESSES:
        session['game_over'] = True
        return jsonify({
            "message": f"Game over! You've used all {MAX_GUESSES} guesses. The correct country was {session['target_country']}.",
            "game_over": True,
            "target_country": session['target_country'],
            "feedback": feedback
        })
    
    return jsonify({
        "feedback": feedback
    })

# @app.route('/new-game', methods=['POST'])
def new_game():
    """Start a new game."""
    exports = start_new_game()
    return jsonify({
        "exports": exports,
        "message": "New game started!"
    })
    
#  {% comment %} <div class="game-board">
#             <div class="exports-panel">
#                 <h2>Export Profile</h2>
#                 <div class="export-items">
#                     {% for product, percentage in exports.items() %}
#                     <div class="export-item">
#                         <span class="product">{{ product }}</span>
#                         <span class="percentage">{{ percentage }}%</span>
#                     </div>
#                     {% endfor %}
#                 </div>
#             </div>

#             <div class="guesses-panel">
#                 <h2>Guesses</h2>
#                 <p>You have {{ max_guesses - guesses|length }} guesses remaining</p>
                
#                 {% if not game_over %}
#                 <div class="guess-form">
#                     <input type="text" id="country-input" placeholder="Enter a country name">
#                     <button id="submit-guess">Guess</button>
#                 </div>
#                 {% endif %}

#                 <div class="guesses-container" id="guesses-list">
#                     <!-- Guesses will be added here via JavaScript -->
#                 </div>
                
#                 {% if game_over %}
#                 <div class="game-over">
#                     {% if won %}
#                     <h3>Congratulations! You won!</h3>
#                     {% else %}
#                     <h3>Game Over! The correct country was: {{ session['target_country'] }}</h3>
#                     {% endif %}
#                     <button id="new-game">Play Again</button>
#                 </div>
#                 {% endif %}
#             </div>
#         </div> {% endcomment %}