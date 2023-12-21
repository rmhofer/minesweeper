function startTrial() {

    $.getJSON('/get_stimulus', function(data) {
        // Start the reaction time timer
        const startTime = Date.now();

        let gameState = data.game_state;
        let gameBoard = data.game_board;
        let gameStateSolved = data.game_state_solved;
        let interactionMode = data.interaction_mode;
        let isSolvedStateShown = false;
        let probePosition = null, minePresent = false;
        
        // advance the progress bar
        let progressPercent = data.progress_percent
        document.getElementById('progress-bar').style.width = progressPercent + '%';

        // render the game board and game state
        renderGameBoard(gameState, interactionMode);
        renderGameState(gameState);

        // find the probe position and check if a mine is present
        $.each(gameState, function(x, row) {
            $.each(row, function(y, cell) {
                if (cell === -5) {
                    probePosition = { x, y };
                    minePresent = gameBoard[x][y] === -1;
                }
            });
        });

        // bind the keypress event
        $(document).on('keypress', handleKeypress);

        // define the keypress handler
        function handleKeypress(e) {
            if (e.key.toUpperCase() === 'Q' || e.key.toUpperCase() === 'P') {
                // Unbind the keypress event to prevent further responses in this trial
                $(document).off('keypress');
                
                let userResponse = e.key.toUpperCase() === 'P';
                let responseCorrect = minePresent === userResponse;
                
                // Calculate reaction time
                const reactionTime = Date.now() - startTime;

                // Record trial data
                let trial_data = {
                    'trial_id': null, // override later
                    'game_board': gameBoard, 
                    'game_state': gameState, 
                    'probe_position': probePosition,
                    'mine_present': minePresent,
                    'user_response': userResponse,
                    'response_correct': responseCorrect,
                    'total_reaction_time': reactionTime,
                };
                
                // feedback: update game board representation
                //  TODO
                $.each(gameBoard, function(x, row) {
                    $.each(row, function(y, cell) {
                        let cellElement = $(`#cell-${x}-${y}`);
                        
                        // show a mine if the cell contains -1 (mine)
                        if (cell === -1) {
                            cellElement.addClass('mine');
                        }
                        
                        // give visual feedback at the probe location
                        if (x === probePosition.x && y === probePosition.y) {
                            cellElement.text(' ').removeClass('probe')
                                .addClass(responseCorrect ? 'green-background' : 'red-background')
                                .addClass(cell !== -1 ? (responseCorrect ? 'checkmark' : 'cross') : '');
                        }
                    });
                });

                // start the next trial (TODO: or end experiment when no more trials)
                $.ajax({
                    url: '/send_response',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify(trial_data),
                    success: function(response) {
                        // console.log(response);
                        setTimeout(startTrial, 1000); // Inter-Stimulus Interval (ISI)
                    },
                    dataType: 'json'
                });
            }
        };

        // add event listener to the button with id #toggle
        function toggleSolve() {
            if (isSolvedStateShown) {
                renderGameState(gameState);
            } else {
                renderGameState(gameStateSolved);
            }
            isSolvedStateShown = !isSolvedStateShown;
        }

        // Bind toggleSolve to the button
        document.getElementById('toggleSolveButton')?.addEventListener('click', toggleSolve);
    });
}

$(document).ready(function() {
    // automatically load the first stimulus when the page is loaded
    startTrial();
});