from flask import Flask, render_template, jsonify, request
from game import Game

app = Flask(__name__)

# Default values
length = 10
width = 10
mines = 10

@app.route('/', methods=['GET', 'POST'])
def home():
    global game, length, width, mines
    if request.method == 'POST':
        # Use form values if available, otherwise default
        length = int(request.form.get('length', length))
        width = int(request.form.get('width', width))
        mines = int(request.form.get('mines', mines))
        game = Game(length, width, mines)
    else:
        # If GET request or no form data, use defaults
        game = Game(length, width, mines)
    
    return render_template('game.html', game_state=game.game_state.tolist(), game=game)

@app.route('/query', methods=['POST'])
def query():
    global game
    data = request.json
    x, y = data['x'], data['y']
    result = game.query(x, y) if data['action'] == 0 else game.flag(x, y)
    return jsonify({'result': result, 'state': game.game_state.tolist()})

if __name__ == '__main__':
    app.run(debug=True)