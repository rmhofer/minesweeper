document.addEventListener('keydown', function(event) {    
    var minePresent = false;
    var responseCorrect = false;
    var probePosition = null;

    // Get the row and column position of where the gameState array equals -5 (probe position)
    gameState.forEach((row, x) => {
        row.forEach((cell, y) => {
            if (cell === -5) {
                probePosition = { x, y };
                minePresent = gameBoard[x][y] === -1; // Check if the gameBoard array equals -1 at that position
            }
        });
    });

    if (event.key === 'q' || event.key === 'Q') {
        // User input: no mine present
        responseCorrect = !minePresent;
    } else if (event.key === 'p' || event.key === 'P') {
        // User input: mine present
        responseCorrect = minePresent;
    } else {
        return
    }

    // Loop over all gameBoard entries
    gameBoard.forEach((row, x) => {
        row.forEach((cell, y) => {
            const cellElement = document.getElementById(`cell-${x}-${y}`);
            // Check if the cell contains -1
            if (cell === -1) {
                cellElement.classList.add('mine'); // Add a 'mine' class to the cellElement
            }
            // If x, y equal probePosition then:
            if (probePosition && x === probePosition.x && y === probePosition.y) {
                cellElement.classList.remove('probe')
                cellElement.textContent = ' ';
                if (responseCorrect) {
                    cellElement.classList.add('green-background');
                    if (cell !== -1) { cellElement.classList.add('checkmark'); }
                } else {
                    cellElement.classList.add('red-background');
                    if (cell !== -1) { cellElement.classList.add('cross'); }
                }
            }
        });
    });

    setTimeout(loadNextTrial, 900); // ISI 500ms
});

var solutionShown = false;
function toggleSolved() {
    // game_state
    if (!solutionShown) {
        renderGameState(solvedGameState)
        solutionShown = true;
    } else {
        renderGameState(gameState)
        solutionShown = false;
    }  
}

function loadNextTrial() {
    window.location.href = '/experiment'; // Redirects the browser to the 'experiment' route
}