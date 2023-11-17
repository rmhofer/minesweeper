import numpy as np
import json
import random

# Set the random seed
np.random.seed(1)
random.seed(1)

class Game:
    logging = True
    
    def __init__(self, length=None, width=None, num_mines=None, 
                 game_board=None, game_states=None, file_path=None):  
        """
        Initialize a new instance of the Game class.

        The Game object represents a minesweeper-like game with a board of specified dimensions 
        (length x width) and a certain number of mines (num_mines) distributed across the board.

        The game state reflects the current visible state of the game to the player or an agent.
        It includes an array, game_states, which records the history of all game states 
        and the moves that led to those states. Each game state provides insight into the board's 
        current state, such as revealed cells, flagged mines, and yet-to-be-revealed cells.
            
        example game_board          example game_state
        -----------------------		-----------------------
        |                 1 1 |		|                 1 * |
        | 1 1             1 M |		| 1 1             1 F |
        | M 1             1 1 |		| F 1             1 1 |
        | 1 1                 |		| 1 1                 |
        |     1 1 1     1 1 1 |		|     1 1 1     1 1 1 |
        |     1 M 1 1 1 3 M 2 |		|     1 F 1 1 1 3 F * |
        |     1 2 2 2 M 3 M 2 |		|     1 * * * * * * * |
        |   1 1 2 M 2 2 3 2 1 |		|   1 1 * * * * * * 1 |
        | 1 2 M 3 2 3 2 M 1   |		| 1 2 F * * * * * * * |
        | M 2 1 2 M 2 M 2 1   |		| * * * * * * * * * * |
        -----------------------		-----------------------
        
        Initialize a Game instance in one of three ways:
        1. From a JSON file, rebuilding the game state from saved data.
        2. Using provided game board and states, useful for testing specific scenarios.
        3. Creating a new game with specified length, width, and number of mines.
        """
        if file_path is not None:
            # Initialize from a JSON file
            with open(file_path, 'r') as file:
                data = json.load(file)
            self.game_board = np.array(data['game_board'])
            self.game_states = [{'move' : game_round['move'], 'game_state' : np.asarray(game_round['game_state'])} for game_round in data['game_states']] # parse into numpy array data structure
            self.length, self.width = self.game_board.shape
            self.num_mines = np.sum(self.game_board == -1)
            self.log("game initialized from file")
        elif game_board is not None and game_states is not None:
            # Initialize with provided game board and states
            self.game_board = np.array(game_board)
            self.game_states = game_states
            self.length, self.width = self.game_board.shape
            self.num_mines = np.sum(self.game_board == -1)
            self.log("game initialized from user input")
        elif length is not None and width is not None and num_mines is not None:
            # Initialize a new game
            self.length = length
            self.width = width
            self.num_mines = num_mines
            self.game_board = self.initialize_game_board()
            self.game_states = []
            self.log("game randomly initialized from user input")
        else:
            raise ValueError("Invalid arguments for game initialization")
        
        # retrieve last game state if available, or initialize
        self.current_game_state = np.asarray(self.game_states[-1]["game_state"]) if len(self.game_states) > 0 else np.full((self.length, self.width), -1)
        self.gameplay_enabled = True
        
        # show the game board and current game state
        self.print_game()
    
    def has_unique_solution(self):
        """
        Placeholder for a function to check if the current game configuration has a unique solution.
        Currently not implemented.
        """
        pass
    
    def is_valid_game(self):
        """
        Placeholder for a function to verify the validity of a game.
        It should check for errors in the game board setup or state representation.
        Currently not implemented.
        """
        pass
    
    def log(self, message):
        """ Print a log message if logging is enabled in the Game class. """
        if Game.logging:
            print(message)
    
    def print_game(self):
        """
        Pretty print the current game board and game state side by side.
        Uses custom replacements to visually represent different elements of the game.
        """
        # 0:      no mines nearby
        # 1-8:    number of mines nearby (do not replace)
        # -1:     mine
        game_board_replacements = {'0': ' ', '-1': 'M'}
        
        # 0:      no mines nearby
        # 1-8:    number of mines nearby (do not replace)
        # -1:     unseen
        # -2:     mine
        # -3:     flag placed
        # -4:     safe (no mine)
        # -5:     probe location
        game_state_replacements = {'0': ' ', '-1': '*', '-2': '*', '-3': 'F', '-4': 'X', '-5': 'P'}

        # Convert game_board and current game_state to string with replacements
        game_board_str = self.board_to_string(self.game_board, game_board_replacements)
        game_state_str = self.board_to_string(self.current_game_state, game_state_replacements)

        # Split the string representations into lines for side-by-side printing
        game_board_lines = game_board_str.split('\n')
        game_state_lines = game_state_str.split('\n')

        # Print the game board and game state side by side
        for board_line, state_line in zip(game_board_lines, game_state_lines):
            print(board_line + '\t\t' + state_line)
    
    def board_to_string(self, board, replace):
        """
        Convert a game board to a string representation.
        Takes a board (either game board or game state) and a dictionary of replacements
        for better visualization.
        """
        border = '-' * (2 * self.width + 3)
        board_str = border + '\n'
        for row in board:
            row_str = '|'
            for cell in row:
                cell_str = str(cell)
                for key, value in replace.items():
                    cell_str = cell_str.replace(key, value)
                row_str += ' ' + cell_str
            row_str += ' |\n'
            board_str += row_str
        board_str += border
        return board_str

    def initialize_game_board(self):
        """
        Initialize a new game board with mines placed randomly.
        Also calculates and populates the board with numbers indicating adjacent mines.
        """
        # Create the mine vector [1 if mine and 0 otherwise] and shuffle it
        mine_vector = np.array([1] * self.num_mines + [0] * (self.length * self.width - self.num_mines))
        np.random.shuffle(mine_vector)

        # Reshape the vector into a matrix
        mine_matrix = mine_vector.reshape((self.length, self.width))
        
        self.game_board = np.zeros(mine_matrix.shape, dtype=int)

        # Directions to shift: (dx, dy)
        shifts = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dx, dy in shifts:
            # Shift the matrix
            shifted_matrix = np.roll(mine_matrix, shift=(dx, dy), axis=(0, 1))

            # Set wrapped rows and/or columns to zero
            if dx == -1: shifted_matrix[-1, :] = 0
            elif dx == 1: shifted_matrix[0, :] = 0
            if dy == -1: shifted_matrix[:, -1] = 0
            elif dy == 1: shifted_matrix[:, 0] = 0

            # Add to the adjacent mines matrix
            self.game_board += shifted_matrix

        # Set cells with mines to -1
        self.game_board[mine_matrix == 1] = -1
        return self.game_board

    def reveal(self, x, y):
        """
        Recursively reveal cells starting from the specified location (x, y).
        Reveals adjacent cells if the revealed cell is empty (has no adjacent mines).
        """
        if self.current_game_state[x, y] != -1 or self.game_board[x, y] == -1:
            return

        self.current_game_state[x, y] = self.game_board[x, y]
        # check all adjacent cells if cell is empty
        if self.game_board[x, y] == 0:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.length and 0 <= ny < self.width:
                        self.reveal(nx, ny)
    
    def move(self, x, y, action):
        """ 
        Process a player's move based on the action at the coordinates (x, y).
        The action can be: 
        0 - query (reveal the cell), 
        1 - place or remove a flag, 
        2 - mark as safe (used by solvers).
        Validates the move and updates the game state accordingly.
        """
        if not self.is_move_valid(x, y, action):
            return False

        if action == 0:
            self.query_position(x, y)
        elif action == 1:
            self.toggle_flag(x, y)
        elif action == 2:
            self.mark_safe(x, y)

        # store this move and the corresponding game state
        self.game_states.append({
            "move" : (x, y, action), 
            "game_state" : np.copy(self.current_game_state)
        })
        return True
    
    def is_move_valid(self, x, y, action):
        """ Validate the move. Check if it's within bounds, the game is ongoing, and the action is correct. """
        if (not self.gameplay_enabled):
            self.log("Error: Gampeplay disabled.")
            return False
        if not (0 <= x < self.length and 0 <= y < self.width):
            self.log("Error: Out of bounds")
            return False
        if action not in [0, 1, 2]:
            self.log("Error: Not a valid move")
            return False 
        return True
    
    def query_position(self, x, y):
        """ Handle querying a position on the board. """
        # query position (x, y)
        if self.current_game_state[x, y] == -3: 
            self.log("Error: Cannot reveal flagged square.")
            return False
    
        if self.game_board[x, y] == -1:
            # end game and reveal location of all mines
            self.log("Log: You clicked on a bomb! :(")
            self.gameplay_enabled = False
            self.current_game_state[self.game_board == -1] = -2
        else:
            # reveal (x, y) and adjacent empty squares
            self.reveal(x, y)

    def toggle_flag(self, x, y):
        """ Handle placing or removing a flag on the board. """
        if self.current_game_state[x, y] >= 0:
            self.log("Error: Flags can only be placed on unseen squares")
            return False
        
        # toggle between -1 (no flag) and -3 (flag)
        self.current_game_state[x, y] = -4 - self.current_game_state[x, y]
        
        # check if all mines have been flagged
        if np.all((self.current_game_state == -4) == (self.game_board == -1)):
            self.gameplay_enabled = False
            self.log("Log: You won! :)")
    
    def mark_safe(self, x, y):
        """ Mark a cell as safe without querying. """
        if self.current_game_state[x, y] != -1:
            self.log("Error: Only unseen squares can be marked as 'clear'")
            return False
        self.current_game_state[x, y] = -4
    
    def convert_to_serializable(self, obj):
        """
        Convert the game data to a format that is serializable in JSON.
        Handles conversion for numpy arrays, dictionaries, and lists.
        """
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: self.convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_to_serializable(item) for item in obj]
        else:
            return obj
    
    def generate_json(self, file_name):
        """
        Generate and save the current game state to a JSON file.
        Converts game data to a serializable format before writing to the file.
        """
        data = {
            "game_board": self.convert_to_serializable(self.game_board),
            "game_states": self.convert_to_serializable(self.game_states)
        }
        with open(file_name, 'w') as file:
            file.write(json.dumps(data)) # TODO: deal with JSON formatting
            
    def play(self):
        """
        The main game loop that handles player input and updates the game state.
        Allows the player to make moves, save the game, and displays the updated game state.
        Handles invalid inputs and termination conditions.
        """
        while self.gameplay_enabled:  # Continue playing until the game is over
            # Wait for user input
            user_input = input("Enter your move (format 'x y action', where action is 0 for uncover and 1 for flag): ")
            try:
                if user_input == 'save':
                    self.generate_json(file_name='test.json')
                    continue
                # Parse user input
                x, y, action = map(int, user_input.split())
                
                # Make a move
                if not self.move(x, y, action):
                    raise ValueError("Coordinates out of bounds")
                
                # Print the updated game representation
                self.print_game()
            except ValueError as e:
                print(f"Invalid input: {e}")
    
    def make_random_move(self, num_moves, avoid_mines=True):
        """
        Make a specified number of random moves, avoiding mines if specified.
        Useful for testing or simulating random gameplay.
        
        TODO: ensure that each move is unique
        """
        for _ in range(num_moves):
            if not self.gameplay_enabled:
                break

            if avoid_mines:
                # Get locations that are not mines
                locations_considered = np.where(self.game_board != -1)
            else:
                # Get all locations
                locations_considered = np.where(self.game_board < 9)
            
            # Randomly choose a non-mine location
            idx = random.randrange(len(locations_considered[0]))
            x, y = locations_considered[0][idx], locations_considered[1][idx]

            # Make a query on this location
            self.move(x, y, 0)  # Assuming 0 is the action for uncovering a cell

    def find_adjacent_to_number(self):
        """
        Find and return a random square in the game state that is adjacent to a revealed number.
        Useful for making informed decisions in game strategies.
        """
        # TODO: rename and refactor this
        rows, cols = self.current_game_state.shape
        valid_locations = []
    
        # Check adjacent cells
        def is_valid_location(r, c):
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    if dr == 0 and dc == 0:
                        continue
                    if 0 <= r + dr < rows and 0 <= c + dc < cols:
                        if self.current_game_state[r + dr, c + dc] in range(1, 9):
                            return True
            return False
        
        # Find all -1 locations with at least one adjacent number (1-8)
        for i in range(rows):
            for j in range(cols):
                if self.current_game_state[i, j] == -1 and is_valid_location(i, j):
                    valid_locations.append((i, j))
                    
        # Randomly select one of these locations
        if valid_locations:
            return random.choice(valid_locations)
        else:
            return None


if __name__ == '__main__':        
    # TESTING

    # initialize from file 
    game = Game(file_path='./data/test.json')

    # initialize from array
    game_board = [
        [0,  1,  1,  1],
        [0,  1, -1,  1],
        [0,  2,  2,  2],
        [0,  1, -1,  1]
    ]
    game_state = []
    game = Game(game_board=game_board, game_states=game_state)

    # random initialization
    game = Game(length=10, width=10, num_mines=5)
    game.play()