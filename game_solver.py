import numpy as np
from game import Game
import itertools
import random

class Solver:
    def __init__(self, solver_type='naive'):
        """
        Initialize the Solver with a specific solving strategy.

        Parameters:
        - solver_type (str): Type of solver to use. Currently, only 'naive' is implemented.
        """
        self.solver_type = solver_type
    
    def sample_probe(self, game_state):
        candidate_squares = self.get_unexplored_adjacent_to_number(game_state)
        # Randomly select one of these locations
        if candidate_squares:
            return random.choice(candidate_squares)
        else:
            return None
        
    def solve(self, game, max_steps=10, **kwargs):
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
        A naive approach to solving the Minesweeper game, focusing on simple, direct deductions, followed by contradiction testing for more complex situations.

        !Note that the solver will make changes to the game state representation!
        
        Parameters:
        - max_steps (int): Maximum number of steps for the naive solver.
        - **kwargs: Additional keyword arguments for customizing the solver's behavior.
        """        
        # keeps track of how many steps required for each undecided square
        reasoning_steps_matrix = np.zeros(shape=game.current_game_state.shape).astype(np.int) - 1
        reasoning_steps_matrix[game.current_game_state == -1] = 0
        
        for step in range(max_steps):
            moves = []
            for (x, y) in self.get_numbered_squares(game.current_game_state):
                # find simple direct deductions
                moves += self.deduce_moves_from_cell(game.current_game_state, x, y)

            contradiction_found = False
            if not moves:  # If no moves found by naive approach, try contradiction
                for (x, y) in self.get_unexplored_adjacent_to_number(game.current_game_state):
                    if self.test_contradiction(game.current_game_state, game, x, y):
                        contradiction_found = True
                        reasoning_steps_matrix[x, y] = step + 1
                        break  # Break if a contradiction is found and resolved
            
            # mark flag and clear positions
            for (x, y, action) in list(set(moves)):
                game.move(x, y, action)
                reasoning_steps_matrix[x, y] = step + 1

            # Termination condition
            if not moves and not contradiction_found:
                print(f'No further deductions possible. Terminating after {step+1} steps.\nDeduction steps:')
                print(game.board_to_string(reasoning_steps_matrix, replace={'-1' : ' '}))
                break
        
            
        return reasoning_steps_matrix

    def get_numbered_squares(self, game_state, x=None, y=None, max_distance=1):
        """
        Retrieve coordinates of squares with numbers, optionally limited to those within a certain distance from a given point if (x, y) is provided.

        Returns:
        - List of tuples: Coordinates of the squares in game_state that meet the criteria.
        """
        return [(ix, iy) for ix, iy in np.ndindex(game_state.shape)
                if game_state[ix, iy] > 0 and (x is None or y is None or max_distance is None 
                or (abs(ix - x) <= max_distance and abs(iy - y) <= max_distance))]

    def get_adjacent_squares(self, game_state, x, y):
        """Gather coordinates of all squares adjacent to a specified square."""
        adjacent_squares = []
        for dx, dy in itertools.product([-1, 0, 1], repeat=2):
            if dx == 0 and dy == 0: continue  # Skip the current square itself
            nx, ny = x + dx, y + dy
            if 0 <= nx < game_state.shape[0] and 0 <= ny < game_state.shape[1]:
                adjacent_squares.append((nx, ny))
        return adjacent_squares
    
    def get_adjacent_unexplored(self, game_state, x, y):
        """Count the number of adjacent squares that are unexplored (marked with -1) around a given square."""
        return [(nx, ny) for nx, ny in self.get_adjacent_squares(game_state, x, y) if game_state[nx, ny] == -1]

    def get_unexplored_adjacent_to_number(self, game_state):
        """
        Retrieve coordinates of unexplored squares that are adjacent to a numbered square.
        Useful for decision-making in game strategies.
        """
        rows, cols = game_state.shape
        locations = []

        for i in range(rows):
            for j in range(cols):
                if game_state[i, j] == -1:  # Check only unexplored squares
                    adjacent_squares = self.get_adjacent_squares(game_state, i, j)
                    if any(game_state[nx, ny] in range(1, 9) for nx, ny in adjacent_squares):
                        locations.append((i, j))

        return locations
    
    def count_unaccounted_mines(self, game_state, x, y):
        """
        Count the number of mines in adjacend cells that have not been accounted for by flags
        """
        adjacent_squares = self.get_adjacent_squares(game_state, x, y)
        num_adjacent_flags = sum(1 for nx, ny in adjacent_squares if game_state[nx, ny] == -3)
        return game_state[x, y] - num_adjacent_flags      
        
    def deduce_moves_from_cell(self, game_state, x, y):
        """
        Deduces potential moves (flagging or clearing) based on the number of adjacent mines indicated by the cell.
        """
        proposed_moves = []

        # compute the number of unaccounted mines and get unexplored squares
        adjacent_unexplored = self.get_adjacent_unexplored(game_state, x, y)
        num_unaccounted_mines = self.count_unaccounted_mines(game_state, x, y) 
        
        if num_unaccounted_mines == 0:
            action = 2  # Clear action
        elif num_unaccounted_mines == len(adjacent_unexplored):
            action = 1  # Flag action
        else:
            return proposed_moves  # No definitive action

        for nx, ny in adjacent_unexplored:
            proposed_moves.append((nx, ny, action))

        return proposed_moves

    def test_contradiction(self, game_state, game, x, y, max_distance=None):
        """
        Test if placing a flag at (x, y) leads to a contradiction with adjacent numbers.
        To do this, check which new implications follow from the flag for all squares around (x, y)
        that are at most max_distance squares away, and see if this leads to a contradiction.
        
        !Currently only search depth of 1!
        """
        game_state_copy = game_state.copy()
        game_state_copy[x, y] = -3  # Temporarily place a flag
        contradiction_found = False
        
        # Iterate over all numbered squares within max_distance (if specified) or all numbered squares
        for (nx, ny) in self.get_numbered_squares(game_state_copy, x=x, y=y, max_distance=max_distance or 1):
            # Deduce legal moves based on the current state
            moves = self.deduce_moves_from_cell(game_state_copy, nx, ny)

            # Perform proposed moves and check for contradictions
            for (mx, my, action) in moves:
                if action == 1:
                    game_state_copy[mx, my] = -3
                elif action == 2:
                    game_state_copy[mx, my] = -4
                
                # check if the current move leads to a contradiction in adjacent squares
                for (px, py) in self.get_numbered_squares(game_state_copy, x=mx, y=my):
                    num_unaccounted_mines = self.count_unaccounted_mines(game_state_copy, px, py) 
                    num_adjacent_unexplored = len(self.get_adjacent_unexplored(game_state_copy, px, py))
                    # Check if the move leads to a contradiction
                    if num_unaccounted_mines > num_adjacent_unexplored:
                        contradiction_found = True
                        break

                if contradiction_found:
                    break
            
            if contradiction_found:
                break
        
        if contradiction_found:
            game.move(x, y, 2)  # Mark original square as clear if contradiction is found
        
        return contradiction_found
    
    

if __name__ == '__main__':        
    # Set the random seed
    np.random.seed(1)
    random.seed(1)
    
    # TESTING
    # game = Game(length=10, width=10, num_mines=10)
    # game.make_random_move(3)
    # game.print_game()
    
    game_board = [
        [0,  0,  0,  0,  0,  0,  0,  0],
        [0,  0,  0,  0,  0,  0,  0,  0],
        [0,  0,  0,  0,  0,  0,  0,  0],
        [0,  0,  0,  1,  1,  1,  0,  0],
        [1,  1,  2,  2, -1,  2,  1,  1],
        [1, -1,  3, -1,  2,  2, -1,  1],
        [1,  2, -1,  2,  1,  1,  1,  1],
        [0,  1,  1,  1,  0,  0,  0,  0],
    ]
    game_states = []
    
    game = Game(game_board=game_board, game_states=game_states)
    game.move(0, 0, 0)
    game.move(5, 2, 0)
    game.print_game()
    
    # solve game
    naive_solver = Solver('naive')
    naive_solver.solve(game)
    game.print_game()
