/* static/js/script.js */
$(document).ready(function() {
     // Load country names for autocomplete
     let countryList = [];
    
     $.getJSON('/countries', function(countries) {
         countryList = countries;
         
         // Initialize autocomplete with custom settings
         $('#country-input').autocomplete({
             source: countryList,
             minLength: 0,  // Show all options with 0 characters
             delay: 0,      // No delay in showing options
             autoFocus: false
         });
         
         // Show all options when input is clicked
         $('#country-input').on('click', function() {
             $(this).autocomplete('search', '');
         });
         
         // Close the list when clicking outside
         $(document).on('click', function(event) {
             if (!$(event.target).closest('#country-input').length) {
                 $('#country-input').autocomplete('close');
             }
         });
     });

    // Submit guess on button click
    $('#submit-guess').click(function() {
        submitGuess();
    });

    // Submit guess on Enter key
    $('#country-input').keypress(function(e) {
        if (e.which === 13) {
            submitGuess();
        }
    });

    // Start new game
    $('#new-game').click(function() {
        $.post('/new-game', function(data) {
            location.reload();
        });
    });

    // Load previous guesses (if any)
    loadPreviousGuesses();

    function submitGuess() {
        const country = $('#country-input').val().trim();
        if (!country) return;

        $.post('/guess', { country: country }, function(response) {
            $('#country-input').val('');

            if (response.error) {
                showError(response.error);
                return;
            }

            if (response.feedback) {
                displayGuessResult(response.feedback);
            }

            if (response.game_over) {
                showGameOver(response);
            }
        });
    }

    function displayGuessResult(feedback) {
        const guessCard = $('<div>').addClass('guess-card');
        
        // Create guess header
        const guessHeader = $('<div>').addClass('guess-header');
        guessHeader.append($('<span>').text(feedback.country));
        guessHeader.append($('<span>').text(`${feedback.guesses_remaining} guesses left`));
        guessCard.append(guessHeader);
        
        // Create guess details
        const guessDetails = $('<div>').addClass('guess-details');
        
        // Continent
        const continentItem = $('<div>').addClass('detail-item');
        continentItem.append($('<span>').text('Continent'));
        const continentValue = $('<span>').text(feedback.continent.value);
        if (feedback.continent.correct) {
            continentValue.css('color', 'var(--correct-color)');
        } else {
            continentValue.css('color', 'var(--different-color)');
        }
        continentItem.append(continentValue);
        guessDetails.append(continentItem);
        
        // GDP Rank
        const gdpItem = $('<div>').addClass('detail-item');
        gdpItem.append($('<span>').text('GDP Rank'));
        let directionSymbol = '';
        if (feedback.gdp_rank.direction === 'correct') {
            directionSymbol = ' ✓';
        } else if (feedback.gdp_rank.direction === 'higher') {
            directionSymbol = ' ↑ (Target is lower ranked)';
        } else {
            directionSymbol = ' ↓ (Target is higher ranked)';
        }
        gdpItem.append($('<span>').text(`${feedback.gdp_rank.value}${directionSymbol}`));
        guessDetails.append(gdpItem);
        
        // Exports Similarity
        const exportsItem = $('<div>').addClass('detail-item');
        exportsItem.append($('<div>').text('Export Similarity'));
        
        const exportsList = $('<div>').addClass('exports-list');
        Object.entries(feedback.exports_similarity).forEach(([product, similarity]) => {
            const exportItem = $('<div>').addClass('export-similarity-item');
            
            // Add color-coded indicator
            const indicator = $('<div>').addClass('similarity-indicator');
            indicator.addClass(similarity.replace(/\s+/g, '-'));
            exportItem.append(indicator);
            
            exportItem.append($('<span>').text(product));
            exportItem.append($('<span>').text(similarity));
            exportsList.append(exportItem);
        });
        
        exportsItem.append(exportsList);
        guessDetails.append(exportsItem);
        
        guessCard.append(guessDetails);
        $('#guesses-list').prepend(guessCard);
    }

    function showError(error) {
        // Simple error display - you could improve this with a toast notification
        alert(error);
    }

    function showGameOver(response) {
        // Create game over message
        const gameOver = $('<div>').addClass('game-over');
        
        if (response.won) {
            gameOver.append($('<h3>').text('Congratulations! You won!'));
        } else {
            gameOver.append($('<h3>').text(`Game Over! The correct country was: ${response.target_country}`));
        }
        
        const newGameBtn = $('<button>').attr('id', 'new-game').text('Play Again');
        newGameBtn.click(function() {
            $.post('/new-game', function(data) {
                location.reload();
            });
        });
        
        gameOver.append(newGameBtn);
        $('.guess-form').replaceWith(gameOver);
    }

    function loadPreviousGuesses() {
        // This would be handled by the server-side rendering in a real app
        // For a full SPA approach, you would fetch previous guesses via AJAX
    }
});