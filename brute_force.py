from game_logic import Game
from game_solver import Solver
import numpy as np
import random
import itertools
import copy

class BruteForceSolver(Solver):
    def __init__(self, game):
        super().__init__(solver_type='brute_force')
        self.game = game

    def solve(self, max_steps=10):
        # Run naive solver first 
        super().solve(self.game, max_steps)

        #self.game.print_game()
        candidate_cells = self.get_candidate_cells()
        remaining_mines = self.game.num_mines - self.get_flagged_mines_count()

        all_combinations = itertools.combinations(candidate_cells, remaining_mines)

        # Filter combinations for those consistent with the current game state
        consistent_combinations = self.filter_consistent_combinations(all_combinations)


        # Deduce mines and safe cells based on consistent combinations
        self.make_deductions(consistent_combinations)

    def get_candidate_cells(self):
        candidate_cells = []
        for x in range(self.game.length):
            for y in range(self.game.width):
                if ((not self.game.is_cell_revealed(x, y))
                     and (not self.game.is_cell_flagged(x, y)) 
                     and not self.game.is_cell_safe(x, y)):
                    candidate_cells.append((x, y))
        return candidate_cells

    def get_flagged_mines_count(self):
        flagged_count = 0
        for x in range(self.game.length):
            for y in range(self.game.width):
                if self.game.is_cell_flagged(x, y):
                    flagged_count += 1
        return flagged_count


    def filter_consistent_combinations(self, combinations):
        consistent_combinations = []
        for combination in combinations:
            if self.is_combination_consistent(combination):
                consistent_combinations.append(combination)
        return consistent_combinations

    def is_combination_consistent(self, combination):
        for x in range(self.game.length):
            for y in range(self.game.width):
                if self.game.is_cell_revealed(x, y):
                    num = self.game.current_game_state[x, y]
                    if num != self.count_adjacent_mines(x, y, combination):
                        return False
        return True

    def count_adjacent_mines(self, x, y, combination):
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if (dx, dy) != (0, 0) and (x + dx, y + dy) in combination:
                    count += 1
        return count

    def make_deductions(self, consistent_combinations):
        if not consistent_combinations:
            return  

        candidate_cells = self.get_candidate_cells()
        for cell in candidate_cells:

            if all(cell in combination for combination in consistent_combinations):
                # If the cell is a mine in all combinations, flag it as a mine
                self.game.toggle_flag(cell[0], cell[1])
            elif all(cell not in combination for combination in consistent_combinations):
                # If the cell is safe in all combinations, mark safe
                self.game.mark_safe(cell[0], cell[1])



if __name__ == "__main__":
    # TESTING
    #np.random.seed(3)
    #random.seed(1)
    game = Game(length=4, width=4, num_mines=6)
    # game_board = [
    #     [ 0, 1,-1,-1, 1, 0],
    #     [ 1, 2, 2, 2, 2, 1],
    #     [-1, 2, 0, 0, 2,-1],
    #     [-1, 2, 0, 0, 2,-1],
    #     [ 1, 2, 2, 2, 2, 1],
    #     [ 0, 1,-1,-1, 1, 0],
    # ]

    game_states = []
    # game_state = [#
    #     [-1,-1,-1,-1,-1,-1],
    #     [-1, 2, 2, 2, 2,-1],
    #     [-1, 2,-1,-1, 2,-1],
    #     [-1, 2,-1,-1, 2,-1],
    #     [-1, 2, 2, 2, 2,-1],
    #     [-1,-1,-1,-1,-1,-1],
    # ]

    #game = Game(game_board=game_board, game_states=game_states)


    game.make_random_move(5)
    game.print_game()

    naive_solver = Solver()
    reasoning_steps_matrix = copy.deepcopy(naive_solver.solve(game))
    game.print_game()


    bf_solver = BruteForceSolver(game)
    bf_solver.solve()


    game.print_game()
    print(reasoning_steps_matrix)
