function doTrial() {

    // set the trial to active
    isTrialActive = true;

    $.getJSON('/get_stimulus', function(data) {
        // Start the reaction time timer
        const startTime = Date.now();

        let useTimeoutForAdvance = false; // Set to false to require space bar press
        let gameState = data.game_state;
        let gameBoard = data.game_board;
        let gameStateSolved = data.game_state_solved;
        let interactionMode = data.interaction_mode;
        let isSolvedStateShown = false;
        let probePosition = null, minePresent = false;
        
        // advance the progress bar
        let trialID = data.trial_id
        let numStimuli = data.num_stimuli
        let progressPercent = (trialID / numStimuli) * 100
        document.getElementById('progress-bar').style.width = progressPercent + '%';

        // Show the prompt for the current trial
        $('#experiment-prompt').show();
        $('#next-trial-prompt').hide();

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
            if (isTrialActive && (e.key.toUpperCase() === 'Q' || e.key.toUpperCase() === 'P')) {

                // set the trial to inactive
                isTrialActive = false;

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

                // save data and handle trial completion if successful
                $.ajax({
                    url: '/send_response',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify(trial_data),
                    success: handleTrialCompletion,
                    dataType: 'json'
                });
            }
        };

        function handleTrialCompletion() {
            if (useTimeoutForAdvance) {
                // Automatic advancement after timeout
                setTimeout(advanceTrialOrEndExperiment, 1000); // 1-second delay
            } else {
                // Manual advancement on space bar press
                $(document).off('keypress').on('keypress', function(event) {
                    if (event.key === ' ') {
                        $(document).off('keypress');
                        advanceTrialOrEndExperiment();
                    }
                });
        
                // Show the prompt for advancing to the next trial
                $('#experiment-prompt').hide();
                $('#next-trial-prompt').show();
            }
        }

        function advanceTrialOrEndExperiment() {
            console.log(numStimuli, trialID);
            if (numStimuli - trialID === 1) {
                // Experiment is complete, redirect to the experiment completion route
                window.location.href = '/survey';
            } else {
                // Start the next trial after a delay
                doTrial();
            }
        }

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

// Declare isTrialActive in the global scope
let isTrialActive = true;

$(document).ready(function() {
    // automatically load the first stimulus when the page is loaded
    // TODO: what if the page is refreshed after the last stimulus?
    doTrial();
});