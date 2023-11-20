from flask import render_template, jsonify, request, session
from app import app
from database import save_trial_data
from game_logic import Game
from game_solver import Solver
import os
import json


@app.route('/game', methods=['GET', 'POST'])
def game():
    # Initialize game with settings
    game = Game(length=request.form.get('length', 10, type=int), 
                width=request.form.get('width', 10, type=int), 
                num_mines=request.form.get('mines', 12, type=int))

    # serialize and store in session variable
    session['game'] = game.serialize()
    return render_template('free_play.html', 
                           game_state=game.current_game_state.tolist(), 
                           length=game.length,
                           width=game.width,
                           num_mines=game.num_mines,
                           interaction_enabled=True)

@app.route('/move', methods=['POST'])
def move():
    data = request.json
    
    # reinitialize game
    serialized_game = session.get('game')
    game = Game.deserialize(serialized_game)
    
    # carry out move
    x, y, action = data['x'], data['y'], data['action']
    result = game.move(x, y, action)
    new_game_state = game.current_game_state.tolist()
    
    # serialize and store in session variable
    session['game'] = game.serialize()
    return jsonify({'result': result, 'game_state': new_game_state})

@app.route('/experiment')
def experiment():    
    # Parse information passed as part of the URL
    prolific_id = request.args.get('PID', 'default_id')
    session['prolific_id'] = prolific_id

    # reading stimuli from stimuli.json if they exist
    if os.path.exists('./stimuli.json'):
        with open('./stimuli.json', 'r') as file:
            stimuli = json.load(file)
    else:
        # Fallback to generating random stimuli
        stimuli = None
    session['stimuli'] = stimuli
    
    # initialize other experiment variables
    session['trial_id'] = 0
    return render_template('experiment.html')

@app.route('/get_stimulus', methods=['GET'])
def get_stimulus():
    prolific_id = session.get('prolific_id', 'default_id')
    stimuli = session.get('stimuli')
    trial_id = session.get('trial_id', 0)

    probe = None
    
    if stimuli is not None:
        # load stimulus from file (UNTESTED)
        game_state_unsolved = stimuli[trial_id]['game_state']
        game_board = stimuli[trial_id]['game_board']
        game = Game(game_board=game_board, game_state=game_state_unsolved)
        probe = stimuli[trial_id]['probe']
    else:
        # randomly create a new stimulus
        game = Game(length=10, width=10, num_mines=12)
        game.make_random_move(num_moves=4)
    
    # define a solver to create a random probe
    solver = Solver(solver_type='naive')
    if not probe: 
        probe = solver.sample_probe(game.current_game_state)

    # store the current game state
    game_state_unsolved = game.current_game_state.tolist()
    
    # engage the solver to solve
    solver.solve(game)
    
    # prepare game state and solved game state
    game_state_unsolved[probe[0]][probe[1]] = -5  # Use -5 to represent probe location
    game_state_solved = game.current_game_state.tolist()
    game_board = game.game_board.tolist()
        
    # incrementing trial variable
    session['trial_id'] = trial_id + 1
    
    # return the data as json (convert numpy arrays to lists if neccesary)
    return jsonify(game_state=game_state_unsolved, game_state_solved=game_state_solved, game_board=game_board, interaction_enabled=False)

@app.route('/send_response', methods=['POST'])
def send_response():
    trial_data = request.json
    prolific_id = session.get('prolific_id', 'default_id')
    trial_id = session.get('trial_id', 0)
    
    try:
        save_trial_data(trial_data, trial_id, prolific_id)
    except Exception as e:
        print(f"Error saving trial data: {e}")
        return jsonify(success=False, message="Failed to save trial data.")
    
    return jsonify(success=True)