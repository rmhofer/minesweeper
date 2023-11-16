// game.js
// function tied to an event listener that updates the game state when a cell is clicked
function cellLeftClicked(x, y) {
    // Handle left click logic
    query(x, y, 0);
    // Add your left click handling code here
}

function cellRightClicked(event, x, y) {
    event.preventDefault(); // Prevent the default context menu
    query(x, y, 1);
}

function query(x, y, action) {
    fetch('/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({x: x, y: y, action: action}),
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.result); // You can use this for additional logic or notifications
        updateGameBoard(data.state);
    })
    .catch(error => console.error('Error:', error));
}

function updateGameBoard(gameState) {
    gameState.forEach((row, x) => {
        row.forEach((cell, y) => {
            const cellElement = document.getElementById(`cell-${x}-${y}`);
            // remove all text except numbers 1 through 8
            cellElement.textContent = cell > 0 ? cell : ' ';
            
            // reset class styling
            cellElement.className = ''; 
        
            // add styling based on whether cell has been revealed
            cellElement.classList.add(cell >= 0 ? 'revealed' : 'unrevealed');

            // add styling to the revealed cells (numbers including 0)
            if (cell >= 1 && cell <= 8) {
                cellElement.classList.add(`number-${cell}`);
            } else {
                cellElement.classList.add(`number-0`);
            }

            // add styling for bombs
            if (cell == -2) {
                cellElement.classList.add(`bomb`);
            }

            // add styling for flags
            if (cell == -3) {
                cellElement.classList.add(`flag`);
            }
        });
    });
}

// Function to initialize the game with the initial state from the server
function initializeGame(initialState) {
    updateGameBoard(initialState);
}

// When the DOM is fully loaded, initialize the game
document.addEventListener('DOMContentLoaded', function() {
    // Convert the initial game state from Flask to a JavaScript array
    let initialState = JSON.parse(document.getElementById('initialState').textContent);
    initializeGame(initialState);
});