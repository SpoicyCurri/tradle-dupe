import random
import json
from difflib import get_close_matches

class TradleGame:
    def __init__(self, data_file='country_trade_data.json'):
        """Initialize the game with trade data."""
        try:
            with open(data_file, 'r') as f:
                self.country_data = json.load(f)
        except FileNotFoundError:
            # If no data file is found, use sample data
            self.country_data = self._generate_sample_data()
        
        self.countries = list(self.country_data.keys())
        self.target_country = None
        self.guesses_made = []
        self.max_guesses = 6
        self.game_over = False
        self.won = False
    
    def _generate_sample_data(self):
        """Generate sample trade data for demo purposes."""
        return {
            "United States": {
                "exports": {
                    "Machinery": 25.4,
                    "Electronics": 18.2,
                    "Vehicles": 14.7,
                    "Chemicals": 11.0,
                    "Food Products": 8.3
                },
                "continent": "North America",
                "gdp_rank": 1
            },
            "Germany": {
                "exports": {
                    "Vehicles": 23.1,
                    "Machinery": 18.7,
                    "Chemicals": 15.2,
                    "Electronics": 12.5,
                    "Pharmaceuticals": 10.8
                },
                "continent": "Europe",
                "gdp_rank": 4
            },
            "Japan": {
                "exports": {
                    "Vehicles": 20.5,
                    "Electronics": 18.3,
                    "Machinery": 15.6,
                    "Chemicals": 10.2,
                    "Metals": 8.7
                },
                "continent": "Asia",
                "gdp_rank": 3
            },
            "China": {
                "exports": {
                    "Electronics": 24.1,
                    "Machinery": 20.8,
                    "Textiles": 12.5,
                    "Metals": 10.1,
                    "Furniture": 7.5
                },
                "continent": "Asia",
                "gdp_rank": 2
            },
            "Brazil": {
                "exports": {
                    "Agricultural Products": 23.6,
                    "Minerals": 18.9,
                    "Food Products": 15.4,
                    "Metals": 12.1,
                    "Machinery": 6.8
                },
                "continent": "South America",
                "gdp_rank": 9
            }
        }
    
    def start_new_game(self):
        """Start a new game by selecting a random target country."""
        self.target_country = random.choice(self.countries)
        self.guesses_made = []
        self.game_over = False
        self.won = False
        return self._get_target_exports()
    
    def _get_target_exports(self):
        """Return the export data for the target country."""
        return self.country_data[self.target_country]["exports"]
    
    def make_guess(self, guess):
        """Process a player's guess."""
        if self.game_over:
            return {"error": "Game is already over. Start a new game."}
        
        if len(self.guesses_made) >= self.max_guesses:
            self.game_over = True
            return {
                "message": f"Game over! You've used all {self.max_guesses} guesses. The correct country was {self.target_country}.",
                "game_over": True
            }
        
        # Handle close matches and case insensitivity
        close_matches = get_close_matches(guess, self.countries, n=1, cutoff=0.8)
        if guess.lower() in [country.lower() for country in self.countries]:
            matched_country = next(country for country in self.countries if country.lower() == guess.lower())
            guess = matched_country
        elif close_matches:
            guess = close_matches[0]
        
        if guess not in self.countries:
            return {"error": f"'{guess}' is not in our database. Try another country."}
        
        if guess in self.guesses_made:
            return {"error": f"You've already guessed {guess}. Try another country."}
        
        self.guesses_made.append(guess)
        
        if guess == self.target_country:
            self.game_over = True
            self.won = True
            return {
                "message": f"Congratulations! You guessed correctly in {len(self.guesses_made)} tries!",
                "game_over": True,
                "won": True
            }
        
        # Generate feedback for the guess
        feedback = self._generate_feedback(guess)
        
        if len(self.guesses_made) >= self.max_guesses:
            self.game_over = True
            feedback["message"] = f"Game over! You've used all {self.max_guesses} guesses. The correct country was {self.target_country}."
            feedback["game_over"] = True
        
        return feedback
    
    def _generate_feedback(self, guess):
        """Generate feedback comparing the guess to the target country."""
        guess_data = self.country_data[guess]
        target_data = self.country_data[self.target_country]
        
        feedback = {
            "continent": {
                "value": guess_data["continent"],
                "correct": guess_data["continent"] == target_data["continent"]
            },
            "gdp_rank": {
                "value": guess_data["gdp_rank"],
                "direction": "correct" if guess_data["gdp_rank"] == target_data["gdp_rank"] else 
                            ("higher" if guess_data["gdp_rank"] < target_data["gdp_rank"] else "lower")
            },
            "exports_similarity": self._compare_exports(guess_data["exports"], target_data["exports"]),
            "guesses_remaining": self.max_guesses - len(self.guesses_made)
        }
        
        return feedback
    
    def _compare_exports(self, guess_exports, target_exports):
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

# Example usage
def play_game():
    game = TradleGame()
    exports = game.start_new_game()
    
    print("Welcome to Tradle!")
    print("I'm thinking of a country with the following export profile:")
    for product, percentage in exports.items():
        print(f"  {product}: {percentage}%")
    
    while not game.game_over:
        guess = input("\nGuess a country: ")
        result = game.make_guess(guess)
        
        if "error" in result:
            print(result["error"])
            continue
        
        if "message" in result:
            print(result["message"])
        
        if not result.get("game_over", False):
            print(f"\nFeedback for {guess}:")
            print(f"Continent: {result['continent']['value']} - {'✓' if result['continent']['correct'] else '✗'}")
            
            gdp_direction = result['gdp_rank']['direction']
            direction_symbol = "=" if gdp_direction == "correct" else ("↑" if gdp_direction == "higher" else "↓")
            print(f"GDP Rank: {result['gdp_rank']['value']} {direction_symbol}")
            
            print("Export Similarity:")
            for product, similarity in result['exports_similarity'].items():
                symbol = "🟢" if similarity == "very similar" else ("🟡" if similarity == "similar" else "🔴")
                print(f"  {product}: {symbol} {similarity}")
            
            print(f"\nGuesses remaining: {result['guesses_remaining']}")

if __name__ == "__main__":
    play_game()