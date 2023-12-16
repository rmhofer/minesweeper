from flask import render_template, jsonify, request, session
from app import app
from database import save_trial_data
from game_logic import Game
from game_solver import Solver
import os
import json
import numpy as np
import random


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
    if os.path.exists('./stimuli/stimuli_5_5_6.json'):
        with open('./stimuli/stimuli_5_5_6.json', 'r') as file:
            stimuli = json.load(file)
    else:
        # Fallback to generating random stimuli
        stimuli = None
    session['stimuli'] = stimuli

    # initialize other experiment variables
    session['trial_id'] = 0
    probe_types = ["naive_easy_probe",
                   "naive_hard_probe",
                   "non_naive_probe"]*(len(stimuli)//3)

    random.shuffle(probe_types)
    session["probe_types"] = probe_types[:len(stimuli)]


    return render_template('experiment.html')

@app.route('/get_stimulus', methods=['GET'])
def get_stimulus():
    prolific_id = session.get('prolific_id', 'default_id')
    stimuli = session.get('stimuli')
    trial_id = session.get('trial_id', 0)
    probe_types = session.get('probe_types')
    probe_type = probe_types[trial_id]

    probe = None

    if stimuli is not None:
        # load stimulus from file (UNTESTED)
        game_state_unsolved = np.array(stimuli[trial_id]['game_state'])
        game_board = np.array(stimuli[trial_id]['game_board'])
        game = Game(game_board=game_board,
             game_states=[{"move":0, "game_state":game_state_unsolved}])
        probe = stimuli[trial_id][probe_type]
    
    else:
        # randomly create a new stimulus
        game = Game(length=10, width=10, num_mines=12)
        game.make_random_move(num_moves=4)

    game_state_unsolved = game.current_game_state.tolist()

    # define a solver to create a random probe
    if not probe: 
        solver = Solver(solver_type='naive')
        probe = solver.sample_probe(game.current_game_state)
        solver.solve(game)
        game_state_solved = game.current_game_state.tolist()
    else:
        game_state_solved = stimuli[trial_id]["solution"]



    # store the current game state
    
    # engage the solver to solve
    
    # prepare game state and solved game state
    game_state_unsolved[probe[0]][probe[1]] = -5  # Use -5 to represent probe location
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