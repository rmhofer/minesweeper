function startTrial() {

    $.getJSON('/get_stimulus', function(data) {
        // Start the reaction time timer
        const startTime = Date.now();

        let game_state = data.game_state;
        let game_state_solved = data.game_state_solved;
        let isSolvedStateShown = false;
        let probePosition = null, minePresent = false;
        
        // render the game board and game state
        renderGameBoard(game_state);
        renderGameState(game_state);

        // find the probe position and check if a mine is present
        $.each(game_state, function(x, row) {
            $.each(row, function(y, cell) {
                if (cell === -5) {
                    probePosition = { x, y };
                    minePresent = data.game_board[x][y] === -1;
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
                    'trial_id': null,
                    'game_board': data.game_board, 
                    'game_state': game_state, 
                    'probe_position': probePosition,
                    'mine_present': minePresent,
                    'user_response': userResponse,  // Corrected the spelling
                    'response_correct': responseCorrect,
                    'reaction_time': reactionTime,
                };
                
                // update game board representation
                $.each(data.game_board, function(x, row) {
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

                // start the next trial (TODO: or end experiment)
                $.ajax({
                    url: '/send_response',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify(trial_data),
                    success: function(response) {
                        setTimeout(startTrial, 900); // Inter-Stimulus Interval (ISI)
                    },
                    dataType: 'json'
                });
            }
        };

        // add event listener to the button with id #toggle
        function toggleSolve() {
            if (isSolvedStateShown) {
                renderGameState(game_state);
            } else {
                renderGameState(game_state_solved);
            }
            isSolvedStateShown = !isSolvedStateShown;
        }

        // Bind toggleSolve to the button
        document.getElementById('toggleSolveButton').onclick = toggleSolve;
    });
}

$(document).ready(function() {
    startTrial();
});