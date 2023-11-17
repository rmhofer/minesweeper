import numpy as np
import json
import hashlib
import random

# Set the random seed
np.random.seed(1)
random.seed(1)

class Game:
    logging = True
    
    def __init__(self, length=None, width=None, num_mines=None, 
                 game_board=None, game_states=None, file_path=None):  
        
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
    
    def is_valid(self):
        # TODO function to check if a game or game state representation is valid
        pass
    
    def log(self, message):
        """ Log a message if logging is enabled """
        if Game.logging:
            print(message)
    
    def print_game(self):
        # Pretty pring: Prepare replacements for game_board and game_state
        '''
            0:      no mines nearby
            1-8:    number of mines nearby (do not replace)
            -1:     mine
        '''
        game_board_replacements = {'0': ' ', '-1': 'M'}
        
        '''
            0:      no mines nearby
            1-8:    number of mines nearby (do not replace)
            -1:     unseen
            -2:     mine
            -3:     flag placed
            -4:     safe (no mine)
            -5:     probe location
        '''
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
        # Generate a string representation of a board with replacements
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
        """ Recursively reveal cells starting from (x, y) """
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
            move can be one of [0, 1, 2]
            0: make a query
            1: place a flag
            2: place a 'safe' marker (only used by solver)
            Valid? Check if out of bounds or game has ended 
        """
        if (not self.gameplay_enabled):
            self.log("Error: Gampeplay disabled.")
            return False
        if not (0 <= x < self.length and 0 <= y < self.width):
            self.log("Error: Out of bounds")
            return False
        if action not in [0, 1, 2]:
            self.log("Error: Not a valid move")
            return False 
        
        if action == 0:
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
        
        if action == 1:
            # place/toggle a flag at (x, y)
            if self.current_game_state[x, y] >= 0:
                self.log("Error: Flags can only be placed on unseen squares")
                return False
            
            # toggle between -1 (no flag) and -3 (flag)
            self.current_game_state[x, y] = -4 - self.current_game_state[x, y]
            
            # check if all mines have been flagged
            if np.all((self.current_game_state == -4) == (self.game_board == -1)):
                self.gameplay_enabled = False
                self.log("Log: You won! :)")
        
        if action == 2:
            # mentally mark as no mine without querying position
            if self.current_game_state[x, y] != -1:
                self.log("Error: Only unseen squares can be marked as 'clear'")
                return False
            self.current_game_state[x, y] = -4
        
        # store this move and the corresponding game state
        self.game_states.append({
            "move" : (x, y, action), 
            "game_state" : np.copy(self.current_game_state)
        })
        return True

    def generate_game_hash(self):
        # TODO: generate a unique hash for each game
        pass
    
    def convert_to_serializable(self, obj):
        # Convert data to a serializable format
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: self.convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_to_serializable(item) for item in obj]
        else:
            return obj
    
    def generate_json(self, file_name):
        data = {
            "game_board": self.convert_to_serializable(self.game_board),
            "game_states": self.convert_to_serializable(self.game_states)
        }
        with open(file_name, 'w') as file:
            file.write(json.dumps(data)) # TODO: deal with JSON formatting
            
    def play(self):
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
    
    def simulate_gameplay(self, num_moves):
        for _ in range(num_moves):
            if not self.gameplay_enabled:
                break

            # Get locations that are not mines
            non_mine_locations = np.where(self.game_board != -1)

            # Randomly choose a non-mine location
            idx = random.randrange(len(non_mine_locations[0]))
            x, y = non_mine_locations[0][idx], non_mine_locations[1][idx]

            # Make a query on this location
            self.move(x, y, 0)  # Assuming 0 is the action for uncovering a cell

    def find_valid_probe(self):
        ''' returns a sqaure from the game state that is adjacent to a number'''
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

    def solve(self, max_steps=5):
        ''' Iteratively solve the Minesweeper game for a given number of steps. '''
        reasoning_steps_matrix = np.zeros(shape=self.current_game_state.shape) - 1
        reasoning_steps_matrix[self.current_game_state == -1] = 0
        
        for step in range(max_steps):
            flag_positions = []
            clear_positions = []
            for x in range(self.length):
                for y in range(self.width):
                    if self.current_game_state[x, y] > 0:
                        new_flag_positions, new_clear_positions = self.mark_adjacent_flags(self.current_game_state, x, y)
                        flag_positions += new_flag_positions
                        clear_positions += new_clear_positions
            # print("flag level", step + 1, list(set(flag_positions)))
            # print("clear level", step + 1, list(set(clear_positions)))
            
            for (x, y) in list(set(flag_positions)):
                self.move(x, y, 1)
                reasoning_steps_matrix[x, y] = step + 1
            
            for (x, y) in list(set(clear_positions)):
                self.move(x, y, 2)
                reasoning_steps_matrix[x, y] = step + 1
            # self.print_game()
        print(reasoning_steps_matrix)
        return reasoning_steps_matrix
        
    def mark_adjacent_flags(self, game_state, x, y):
        '''
        Marks unexplored squares adjacent to a numbered square with flags
        if the number of unexplored squares equals the number on the square minus adjacent flags.
        '''
        adjacent_unexplored = []
        new_flag_positions = []
        new_clear_positions = []
        adjacent_flags = 0
        
        # Check adjacent squares
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue  # Skip the current square

                nx, ny = x + dx, y + dy
                if 0 <= nx < game_state.shape[0] and 0 <= ny < game_state.shape[1]:
                    if game_state[nx, ny] == -1:
                        adjacent_unexplored.append((nx, ny))
                    elif game_state[nx, ny] == -3:
                        adjacent_flags += 1

        if (game_state[x, y] - adjacent_flags == 0):
            for nx, ny in adjacent_unexplored:
                new_clear_positions.append((nx, ny))
        
        # Mark with flags if conditions are met
        if len(adjacent_unexplored) == game_state[x, y] - adjacent_flags:
            for nx, ny in adjacent_unexplored:
                new_flag_positions.append((nx, ny))

        # remove duplicate positions (each flag should only be applied once)
        return new_flag_positions, new_clear_positions
    
# TESTING

# initialize from file 
# game = Game(file_path='./data/test.json')

# initialize from array
# game_board = [
#     [0,  1,  1,  1],
#     [0,  1, -1,  1],
#     [0,  2,  2,  2],
#     [0,  1, -1,  1]
# ]
# game_state = []
# game = Game(game_board=game_board, game_state=game_state)

# random initialization
# game = Game(length=10, width=10, num_mines=5)
# game.play()

# game = Game(length=5, width=5, num_mines=5)
# game.simulate_gameplay(3)
# game.print_game()
# game.solve()