from flask import render_template, jsonify, request, g, session, redirect, url_for
from app import app, BONUS_AMOUNT, PROLIFIC_COMPLETION_URL
from database import save_trial_data, save_exit_data
from game_logic import Game
from game_solver import Solver
import os
import json
import numpy as np
import random



@app.context_processor
def inject_query_string():
    # make querystring universally available to all routes
    g.query_string = request.query_string.decode('utf-8')
    return dict(query_string=g.query_string)


@app.route('/clear_session')
def clear_session():
    session.clear()  # Clears all data from the session
    return 'Session cleared!'


@app.route('/')
def index():
    session.clear()  # Clears all data from the session
    query_string = request.query_string.decode('utf-8')
    # query_string needs to be attached here because of a redirect
    return redirect(url_for('render_page', page_name='consent') + '?' + query_string)


@app.route('/<page_name>')
def render_page(page_name):
    # generic render function for a list of subpages
    valid_pages = ['consent', 'instructions', 'survey']
    
    # Context data for specific pages
    page_contexts = {
        'consent' : {},
        'instructions': {'bonus_amount': BONUS_AMOUNT},
        'survey': {'bonus_amount': session.get('bonus', 0), 'process_percent' : 100},
        # ... add other pages and their contexts as needed
    }
    
    if page_name in valid_pages:
        # Get the context for the page, default to an empty dict if not found
        context = page_contexts.get(page_name, {})
        return render_template(f'{page_name}.html', **context)
    else:
        return "Page not found", 404


@app.route('/experiment')
def experiment():
    # Parse information passed as part of the URL
    params = request.args
    session['prolific_id'] = params.get('PID', 'default_id')
    debug_mode_arg_value = params.get('debug', 'false')
    session['debug'] = debug_mode_arg_value.lower() in ['true', '1', 'yes']

    # set up stimuli - retrieve or initialize
    if 'stimuli' in session:
        stimuli = session['stimuli']
    else:
        # Reading stimuli from stimuli.json if they exist
        if os.path.exists('./stimuli/stimuli_5_5_6.json'):
            with open('./stimuli/stimuli_5_5_6.json', 'r') as file:
                stimuli = json.load(file)
        else:
            # Fallback to generating random stimuli
            stimuli = None

        # Store the loaded stimuli in the session
        session['stimuli'] = stimuli[:6]  # Assuming you want to store only the first 5
        
        # initialize probe types and randomize
        probe_types = ["naive_easy_probe",
                       "naive_hard_probe",
                       "non_naive_probe"] * (len(stimuli)//3)
        random.shuffle(probe_types)
        session["probe_types"] = probe_types[:len(stimuli)]
        
    # retrieve or initialize other experiment variables
    session['trial_id'] = session.get('trial_id', 0)
    
    # redirect to survey if experiment has already ended
    if (len(stimuli) == session['trial_id']): 
        query_string = request.query_string.decode('utf-8')
        return redirect(url_for('render_page', page_name='survey') + '?' + query_string)
    else:
        # render the experiment template
        return render_template('experiment.html')


@app.route('/get_stimulus', methods=['GET'])
def get_stimulus():
    # get information from session variables
    stimuli = session.get('stimuli')
    trial_id = session.get('trial_id')
    probe = None
    
    if stimuli is not None:
        # load stimulus from file
        game_state_unsolved = np.array(stimuli[trial_id]['game_state'])
        game_board = np.array(stimuli[trial_id]['game_board'])
        game = Game(game_board=game_board,
             game_states=[{"move":0, "game_state":game_state_unsolved}])
        probe_types = session.get('probe_types')
        probe_type = probe_types[trial_id]
        probe = stimuli[trial_id][probe_type]
    else:
        # randomly create a new stimulus
        game = Game(length=10, width=10, num_mines=12)
        game.make_random_move(num_moves=4)

    if not probe: 
        # define a solver to create a random probe
        solver = Solver(solver_type='naive')
        probe = solver.sample_probe(game.current_game_state)
        
        # store a copy of the current game state
        game_state_copy = game.current_game_state.copy()
        
        # engage the solver (this will alter the game state)
        solver.solve(game)
        game.current_game_state = game_state_copy
        game_state_solved = game.current_game_state.tolist()
    else:
        game_state_solved = stimuli[trial_id]["solution"]

    # mark probe location
    game.current_game_state[probe[0]][probe[1]] = -5  # Use -5 to represent probe location
    
    # save game in session object (for interactive gameplay)
    session['game'] = game.serialize()
    
    # pass game varialbes as lists for rendering
    game_state_unsolved = game.current_game_state.tolist()
    game_board = game.game_board.tolist()
    
    # re-initialize session variable to store user actions
    session['user_actions'] = []
    
    # return the data as json (convert numpy arrays to lists if neccesary)
    return jsonify(game_state=game_state_unsolved, 
                   game_state_solved=game_state_solved, 
                   game_board=game_board, 
                   interaction_mode='exploratory',  # Possible values: 'disabled', 'standard', 'exploratory'
                   trial_id=trial_id,
                   num_stimuli=len(stimuli)
                   )


@app.route('/game', methods=['GET', 'POST'])
def game():
    # Initialize game with settings
    game = Game(length=request.form.get('length', 10, type=int), 
                width=request.form.get('width', 10, type=int), 
                num_mines=request.form.get('mines', 12, type=int))

    # re-initialize session variable to store user actions
    session['user_actions'] = []
    
    # serialize and store in session variable
    session['game'] = game.serialize()
    return render_template('game.html', 
                           game_state=game.current_game_state.tolist(), 
                           length=game.length,
                           width=game.width,
                           num_mines=game.num_mines,
                           interaction_mode='standard') # Possible values: 'disabled', 'standard', 'exploratory'


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
    
    # serialize and store information in session variables
    session['game'] = game.serialize()
    user_actions = session.get('user_actions')
    user_actions.append((x, y, action))
    session['user_actions'] = user_actions
    return jsonify({'result': result, 'game_state': new_game_state})


@app.route('/send_response', methods=['POST'])
def send_response():
    prolific_id = session.get('prolific_id', 'default_id')
    
    # retrieve trial-related data
    trial_data = request.json
    trial_data['trial_id'] = session.get('trial_id', 0)
    user_actions = session.get('user_actions')
    trial_data['user_actions'] = user_actions
    
    # update bonus
    bonus = session.get('bonus', 0) # Default to 0 if 'bonus' is not in session
    bonus += round(trial_data['response_correct'] * BONUS_AMOUNT, 4)
    session['bonus'] = bonus
    
    # save bonus
    try:
        save_trial_data(prolific_id, trial_data)
    except Exception as e:
        print(f"Error saving trial data: {e}")
        return jsonify(success=False, message="Failed to save trial data.")
    
    # incrementing trial variable
    session['trial_id'] = trial_data['trial_id'] + 1
    
    return jsonify(success=True)


@app.route('/submit_survey', methods=['POST'])
def submit_survey():
    # Extract form data
    form_data = request.form

    # Call function to save data to the database
    save_exit_data(form_data)

    # Clear the session
    session.clear()

    # Redirect to Prolific completion URL upon successful data saving
    return redirect(PROLIFIC_COMPLETION_URL)
