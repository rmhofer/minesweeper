import numpy as np
from game import Game
import itertools
from copy import deepcopy

class Solver:
    def __init__(self, solver_type='naive'):
        """
        Initialize the Solver with a specific solving strategy.

        Parameters:
        - solver_type (str): Type of solver to use. Currently, only 'naive' is implemented.
        """
        self.solver_type = solver_type
    
    def solve(self, game, max_steps=5, **kwargs):
        """
        Iteratively solve the Minesweeper game for a given number of steps.
        Delegates to the specified solver method based on the solver type.

        Parameters:
        - max_steps (int): Maximum number of steps to attempt in solving the game.
        """
        if self.solver_type == 'naive':
            return self.naive_solver(game, max_steps, **kwargs)
        else:
            raise NotImplementedError(f"Solver type '{self.solver_type}' is not implemented.")

    def naive_solver(self, game, max_steps, **kwargs):
        """
        A naive approach to solving the Minesweeper game, focusing on simple, direct deductions.

        !Note that the solver might make changes to the game state representation!
        
        Parameters:
        - max_steps (int): Maximum number of steps for the naive solver.
        - **kwargs: Additional keyword arguments for customizing the solver's behavior.
        """        
        # keep track of how many reasoning steps are necessary to decide
        reasoning_steps_matrix = np.zeros(shape=game.current_game_state.shape) - 1
        reasoning_steps_matrix[game.current_game_state == -1] = 0
        
        for step in range(max_steps):
            moves = []
            clear_positions = []
            for x, y in itertools.product(range(game.length), range(game.width)):
                
                # squares with n > 0 (n adjacent mines)
                if game.current_game_state[x, y] > 0:
                    
                    # deductive reasoning step
                    # check if any adjacent squares can be marked 'mine' or 'clear'
                    # and propose corresponding 'flag' or 'clear' moves
                    moves += self.check_adjacent(game.current_game_state, x, y)

                    # TODO: UNTESTED proof by contradiction (currently not working)
                    # moves += self.test_contradiction(game.current_game_state, x, y)

            # mark flag and clear positions
            for (x, y, action) in list(set(moves)):
                game.move(x, y, action)
                reasoning_steps_matrix[x, y] = step + 1

        return reasoning_steps_matrix
        
    def check_adjacent(self, game_state, x, y):
        '''
        Performs deduction based on the number of unaccounted mines and squares marked with flags or marked as clear
        '''
        adjacent_unexplored = []
        num_adjacent_flags = 0
        proposed_moves = []
        
        # Count the number of adjacent unexplored and flagged squares
        for dx, dy in itertools.product([-1, 0, 1], repeat=2):
            if dx == 0 and dy == 0:
                continue  # Skip the current square
            
            nx, ny = x + dx, y + dy
            
            # check if new x and y are within bounds of the game board
            if 0 <= nx < game_state.shape[0] and 0 <= ny < game_state.shape[1]:
                # unexplored square
                if game_state[nx, ny] == -1:
                    adjacent_unexplored.append((nx, ny))
                # flagged square
                elif game_state[nx, ny] == -3:
                    num_adjacent_flags += 1

        # compute the number of unaccounted mines
        num_unaccounted_mines = game_state[x, y] - num_adjacent_flags
        
        if num_unaccounted_mines == 0:
            # No unaccounted mines left, mark remaining unexplored squares as 'clear'
            action = 2
        elif num_unaccounted_mines == len(adjacent_unexplored):
            # Number of unaccounted mines equals number of unexplored adjacent squares, mark those with a flag
            action = 1
        else:
            # No definitive action can be taken
            return proposed_moves

        for nx, ny in adjacent_unexplored:
            proposed_moves.append((nx, ny, action))

        return proposed_moves

    def test_contradiction(self, game_state, x, y):
        """
        Test if placing a flag at (x, y) leads to a contradiction with adjacent numbers.
        """
        # Temporarily place a flag
        game_state[x, y] = -2

        for dx, dy in itertools.product([-1, 0, 1], repeat=2):
            nx, ny = x + dx, y + dy
            if 0 <= nx < game_state.shape[0] and 0 <= ny < game_state.shape[1]:
                # Check adjacent squares that are revealed and have a number
                if 0 <= game_state[nx, ny] <= 8:
                    if not self.is_valid_configuration(game_state, nx, ny):
                        # contradiction found
                        
                        # Revert the flag placement
                        game_state[x, y] = -1
                        # Mark the square as 'clear'
                        return [(x, y, 2)]
        return []

    def is_valid_configuration(self, game_state, x, y):
        """
        Check if the configuration around (x, y) is valid based on Minesweeper rules.
        """
        count_flags = 0
        count_unexplored = 0
        for dx, dy in itertools.product([-1, 0, 1], repeat=2):
            nx, ny = x + dx, y + dy
            if 0 <= nx < game_state.shape[0] and 0 <= ny < game_state.shape[1]:
                if game_state[nx, ny] == -2:  # Flag
                    count_flags += 1
                elif game_state[nx, ny] == -1:  # Unexplored
                    count_unexplored += 1

        # The number of flags plus unexplored squares should not be less than the number on the square
        return count_flags + count_unexplored >= game_state[x, y]
    
    
if __name__ == '__main__':        
    # TESTING
    game = Game(length=10, width=10, num_mines=10)
    game.make_random_move(3)
    game.print_game()
    
    # solve game
    naive_solver = Solver('naive')
    naive_solver.solve(game)
    game.print_game()