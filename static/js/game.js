function query(x, y) {
    // make a query on left click
    makeMove(x, y, 0);
}

function flag(event, x, y) {
    // place/toggle a flag on right click
    event.preventDefault(); // Prevent the default context menu
    makeMove(x, y, 1);
}

function makeMove(x, y, action) {
    // interact with the game to perform the corresponding action
    fetch('/move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({x: x, y: y, action: action}),
    })
    .then(response => response.json())
    .then(data => {
        renderGameState(data.state, [x, y, action]);
    })
    .catch(error => console.error('Error:', error));
}

function renderGameState(gameState, move=null) {
    // call to render the game according to the contents of current_game_state
    gameState.forEach((row, x) => {
        row.forEach((cell, y) => {
            const cellElement = document.getElementById(`cell-${x}-${y}`);
            // remove all text except numbers 1 through 8
            cellElement.textContent = cell > 0 ? cell : ' ';
            
            // reset class styling
            cellElement.className = ''; 
        
            // add styling based on whether cell has been revealed
            cellElement.classList.add(cell >= 0 ? 'revealed' : 'unrevealed');

            // add number styling to the revealed cells
            if (cell >= 1 && cell <= 8) {
                cellElement.classList.add(`number-${cell}`);
            } else {
                cellElement.classList.add(`number-0`);
            }

            // add styling for bombs
            if (cell == -2) {
                cellElement.classList.add(`mine`);
                cellElement.classList.add(`revealed`);
            }

            // add styling for flags
            if (cell == -3) {
                cellElement.classList.add(`flag`);
            }

            // add styling for probe (if present)
            if (cell == -4) {
                cellElement.textContent = 'X'
                cellElement.classList.add('black-font-color');
            }

            // add styling for probe (if present)
            if (cell == -5) {
                cellElement.textContent = '?'
                cellElement.classList.add(`probe`);
            }

            // make the background red if a mine was revealed
            if (move && x === move[0] && y === move[1] && cell == -2) {
                cellElement.classList.add('red-background');
            }
        });
    });
}

// When the DOM is fully loaded, initialize the game
document.addEventListener('DOMContentLoaded', function() {
    // Convert the initial game state from Flask to a JavaScript array
    let initialState = JSON.parse(document.getElementById('initialState').textContent);
    renderGameState(initialState);
});