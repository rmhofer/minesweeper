function reveal(x, y) {
    // reveal a square on left click
    processUserInteraction(x, y, 0);
}

function toggleFlag(event, x, y) {
    // place/toggle a flag on right click
    event.preventDefault(); // Prevent the default context menu
    processUserInteraction(x, y, 1);
}

function toggleMarkSafe(x, y) {
    // place/toggle a safe mark on right click
    processUserInteraction(x, y, 2);
}

function processUserInteraction(x, y, action) {
    // interact with the game to perform the corresponding action
    $.ajax({
        url: '/move',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({x: x, y: y, action: action}),
        success: function(data) {
            if (data.result) {
                // only update game state if the move is valid
                renderGameState(data.game_state, [x, y, action]);
            }
        },
        error: function(error) {
            console.error('Error:', error);
        }
    });
}

function renderGameBoard(gameState, interactionMode) {
    if (!gameState) return;
    
    let htmlContent = '<table>';
    for (let row = 0; row < gameState.length; row++) {
        htmlContent += '<tr>';
        for (let col = 0; col < gameState[row].length; col++) {
            // Add interaction attributes depending on interaction mode
            let interactionAttributes = '';
            if (interactionMode == 'standard') {
                interactionAttributes = ` onclick="reveal(${row}, ${col})" oncontextmenu="toggleFlag(event, ${row}, ${col})"`;
            } else if (interactionMode == 'exploratory') {
                interactionAttributes = ` onclick="toggleMarkSafe(${row}, ${col})" oncontextmenu="toggleFlag(event, ${row}, ${col})"`;
            } else {
                // no user interaction possible
            }

            htmlContent += `<td id="cell-${row}-${col}"${interactionAttributes}></td>`;
        }
        htmlContent += '</tr>';
    }
    htmlContent += '</table>';

    document.getElementById('gameBoardContainer').innerHTML = htmlContent;
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

            // add styling for safe squares
            if (cell == -4) {
                // cellElement.textContent = 'X'
                cellElement.classList.add('safe');
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
    // Check if the 'gameState' element exists
    var gameStateElement = document.getElementById('gameState');
    
    if (gameStateElement) {
        // Convert the initial game state from Flask to a JavaScript array
        gameState = JSON.parse(gameStateElement.textContent);
        renderGameBoard(gameState, true);
        renderGameState(gameState);
    }
});