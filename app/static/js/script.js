// In game.js
document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const countryInput = document.getElementById('country-input');
    const submitGuessButton = document.getElementById('submit-guess');
    const resultMessage = document.getElementById('result-message');
    const countryDropdown = document.getElementById('country-dropdown');

    // Function to add a new result row
    function addResultRow(result) {
        const tbody = document.getElementById('guesses-body');
        const row = document.createElement('tr');
        
        // Create cells for each piece of data
        const guessCell = document.createElement('td');
        guessCell.textContent = result.guess;
        
        const correctCell = document.createElement('td');
        correctCell.textContent = result.correct ? '✓' : '✗';
        correctCell.classList.add(result.correct ? 'correct' : 'incorrect');
        
        const distanceCell = document.createElement('td');
        distanceCell.textContent = result.distance + ' km';
        
        const directionCell = document.createElement('td');
        directionCell.textContent = result.direction;

        
        // Add all cells to the row
        row.appendChild(guessCell);
        row.appendChild(correctCell);
        row.appendChild(distanceCell);
        row.appendChild(directionCell);
        
        // Add the row to the table
        tbody.appendChild(row);
    }
    
    // Add event listener to the guess button
    submitGuessButton.addEventListener('click', submitGuess);
    
    // Also submit when pressing Enter in the input field
    countryInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            submitGuess();
        }
    });
    
    // Show dropdown when input is clicked
    countryInput.addEventListener('click', function() {
        showAllCountries();
    });
    
    // Show filtered countries when typing
    countryInput.addEventListener('input', function() {
        filterCountries();
    });
    
    // Hide dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (e.target !== countryInput && e.target !== countryDropdown) {
            countryDropdown.innerHTML = '';
            countryDropdown.style.display = 'none';
        }
    });

    // Add logic to load chart
    Plotly.newPlot('exports-treemap', treemap_data, treemap_layout);
    
    // Hide loading indicator once chart is loaded
    document.getElementById('chart-loading').style.display = 'none';

    function submitGuess() {
        const country = countryInput.value.trim();
        
        if (!country) {
            return; // Don't submit empty guesses
        }
        
        // Show loading state
        submitGuessButton.disabled = true;
        
        // Send the guess to the server
        fetch('/api/guess', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ guess: country })
        })
        .then(response => response.json())
        .then(result => {
            // Add the result to the table
            addResultRow(result);
            
            // Clear the form input
            document.getElementById('guess-input').value = '';
            
            // If the guess was correct, show a winning message
            if (result.correct) {
                alert('Congratulations! You guessed correctly!');
                // Or show a more sophisticated winning message
            }
        })
        .catch(error => console.error('Error submitting guess:', error))
        .finally(() => {
            // Re-enable button
            submitGuessButton.disabled = false;
        });
    }
        
    // Show all countries in the dropdown
    function showAllCountries() {
        countryDropdown.innerHTML = '';

        // Fetch countries from server
        fetch('/api/countries')
            .then(response => response.json())
            .then(data => {
                countries = data;
            })
            .catch(error => console.error('Error fetching countries:', error));
        
        countries.forEach(country => {
            const item = document.createElement('div');
            item.className = 'dropdown-item';
            item.textContent = country;
            item.addEventListener('click', function() {
                countryInput.value = country;
                countryDropdown.innerHTML = '';
                countryDropdown.style.display = 'none';
            });
            countryDropdown.appendChild(item);
        });
        
        countryDropdown.style.display = 'block';
    }
    
    // Filter countries based on input
    function filterCountries() {
        const input = countryInput.value.toLowerCase();
        
        countryDropdown.innerHTML = '';
        
        const filteredCountries = countries.filter(country => 
            country.toLowerCase().includes(input)
        );
        
        if (filteredCountries.length > 0) {
            filteredCountries.forEach(country => {
                const item = document.createElement('div');
                item.className = 'dropdown-item';
                item.textContent = country;
                item.addEventListener('click', function() {
                    countryInput.value = country;
                    countryDropdown.innerHTML = '';
                    countryDropdown.style.display = 'none';
                });
                countryDropdown.appendChild(item);
            });
            countryDropdown.style.display = 'block';
        } else {
            countryDropdown.style.display = 'none';
        }
    }
});


document.getElementById('guess-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    
    fetch('/submit_guess', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(result => {
        // Add the result to the table
        addResultRow(result);
        
        // Clear the form input
        document.getElementById('guess-input').value = '';
        
        // If the guess was correct, show a winning message or something
        if (result.correct) {
            alert('Congratulations! You guessed correctly!');
            // Or show a more sophisticated winning message
        }
    })
    .catch(error => console.error('Error submitting guess:', error));
});