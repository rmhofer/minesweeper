from flask import Flask, render_template, jsonify, request
from game import Game
import json

app = Flask(__name__)

# Default values
length = 10
width = 10
num_mines = 10

@app.route('/', methods=['GET', 'POST'])
def home():
    # free gameplay
    global game, length, width, num_mines
    if request.method == 'POST':
        # Use form values if available, otherwise default
        length = int(request.form.get('length', length))
        width = int(request.form.get('width', width))
        num_mines = int(request.form.get('mines', num_mines))
    game = Game(length=length, width=width, num_mines=num_mines)
    return render_template('free_play.html', game_state=game.current_game_state.tolist(), game_object=game, interaction_enabled=True)

@app.route('/move', methods=['POST'])
def move():
    # helper function to make a move in free gameplay
    global game
    data = request.json
    x, y, action = data['x'], data['y'], data['action']
    result = game.move(x, y, action) # returns True or False
    return jsonify({'result': result, 'state': game.current_game_state.tolist()})

@app.route('/experiment')
def experiment():
    # 'is there a mine?' experiment
    global game
    
    # create a new game and simulate a number of rounds
    game = Game(length=length, width=width, num_mines=num_mines)
    game.simulate_gameplay(num_moves=4)
    
    # find an unseen square that's adjacent to a number
    probe = game.find_valid_probe()
    
    current_game_state = game.current_game_state.tolist()
    current_game_state[probe[0]][probe[1]] = -4 # use -4 to represent probe location
    return render_template('experiment.html', 
                           game_state=current_game_state, 
                           game_board=game.game_board.tolist(), 
                           interaction_enabled=False)

if __name__ == '__main__':
    app.run(debug=True)
