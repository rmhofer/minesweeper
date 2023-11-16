import numpy as np

# Set the random seed
# np.random.seed(0)

class Game:
    logging = True
    
    def __init__(self, length, width, num_mines):    
        # game variables
        self.length = length
        self.width = width
        self.num_mines = num_mines
        self.gameover = False
        
        # game state is what the user 'sees'
        # information about revealed (number), unseen (-1), bomb (-2), flag (-3)
        self.game_state = np.full((length, width), -1)
        
        # location of mines: 1 if mine and 0 otherwise
        self.mine_matrix = self.initialize_mine_matrix()
        
        # location of flags: 1 if flag and 0 otherwise
        self.flag_matrix = np.full((length, width), 0)
        
        # information about adjacent mines (number) and mines (-1)
        self.adjacent_mines_matrix = self.compute_adjacent_mines()
        
    
    def log(self, message):
        """ Log a message if logging is enabled """
        if Game.logging:
            print(message)
        
    def initialize_mine_matrix(self):
        # Create the mine vector and shuffle it
        mine_vector = np.array([1] * self.num_mines + [0] * (self.length * self.width - self.num_mines))
        np.random.shuffle(mine_vector)

        # Reshape the vector into a matrix
        mine_matrix = mine_vector.reshape((self.length, self.width))
        return mine_matrix

    def compute_adjacent_mines(self):
        length, width = self.mine_matrix.shape
        adjacent_mines_matrix = np.zeros((length, width), dtype=int)

        # Directions to shift: (dx, dy)
        shifts = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dx, dy in shifts:
            # Shift the matrix
            shifted_matrix = np.roll(self.mine_matrix, shift=(dx, dy), axis=(0, 1))

            # Set wrapped rows and/or columns to zero
            if dx == -1:
                shifted_matrix[-1, :] = 0
            elif dx == 1:
                shifted_matrix[0, :] = 0

            if dy == -1:
                shifted_matrix[:, -1] = 0
            elif dy == 1:
                shifted_matrix[:, 0] = 0

            # Add to the adjacent mines matrix
            adjacent_mines_matrix += shifted_matrix

        # Set cells with mines to -1
        adjacent_mines_matrix[self.mine_matrix == 1] = -1

        return adjacent_mines_matrix

    def pretty_print(self, matrix):
        for row in matrix:
            print(" ".join(str(int(x)) if x >= 0 else "*" for x in row))
        print()

    def display_board(self):
        print("\nAdjacent Mines Matrix:")
        self.pretty_print(self.adjacent_mines_matrix)
        print("\nGame state:")
        self.pretty_print(self.game_state)

    def reveal(self, x, y):
        """ Recursively reveal cells starting from (x, y) """
        if self.game_state[x, y] != -1 or self.mine_matrix[x, y] == 1:
            return

        self.game_state[x, y] = self.adjacent_mines_matrix[x, y]
        if self.adjacent_mines_matrix[x, y] == 0:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.length and 0 <= ny < self.width:
                        self.reveal(nx, ny)
    
    def valid(self, x, y):
        """ Check if out of bounds or game has ended """
        if (self.gameover):
            self.log("The game is already over.")
            return False
        
        if not (0 <= x < self.length and 0 <= y < self.width):
            self.log("Error: Out of bounds")
            return False
        return True 
    
    def query(self, x, y):
        """ Query position (x, y) """
        if not self.valid(x, y): return
        
        if self.game_state[x, y] == -3: 
            self.log("Error: Must unflag first.")
            return
        
        if self.mine_matrix[x, y] == 1:
            self.log("Bomb! Gameover")
            self.gameover = True
            
            # update gamestate (-2) to reveal all mines
            for i in range(self.length):
                for j in range(self.width):
                    if self.mine_matrix[i, j] == 1:
                        self.game_state[i, j] = -2
            return

        # reveal (x, y) and adjacent empty squares
        self.reveal(x, y)
        self.log("Revealed")
        self.pretty_print(self.game_state)
        return

    def flag(self, x, y):        
        """ Place a flag at position (x, y) """
        if not self.valid(x, y): return
        
        if self.game_state[x, y] >= 0:
            self.log("Error: Cannot place a flag here")
            return
        
        # toggle value between -1 (no flag) and -3 (flag)
        self.game_state[x, y] = -4 - self.game_state[x, y]
        # toggle flag at (x, y)
        self.flag_matrix[x, y] ^= 1
        self.log("Flag updated")

        if (np.array_equal(self.flag_matrix, self.mine_matrix)):
            self.gameover = True
            self.log("Congratulations, you won!")
        return
            
# game = Game(length=10, width=10, num_mines=20)
# game.display_board()
# game.query(0, 0)