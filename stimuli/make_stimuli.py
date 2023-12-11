import sys
sys.path.append("..")

from game_logic import Game
from game_solver import Solver
from brute_force import BruteForceSolver
import numpy as np
import random
import itertools
import copy
import json


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)




def make_stimulus(length, width, num_mines):
    while True:
        # Until we've found a game that's solvable, keep going
        game = Game(length=length, width=width, num_mines=num_mines)
        game.make_random_move(length*width)

        naive_solver = Solver()
        naive_steps = copy.deepcopy(naive_solver.solve(game, use_contradiction=False))
        naive_solution = copy.deepcopy(game.current_game_state)


        BruteForceSolver(game).solve()
        if np.sum(game.current_game_state == -1) == 0:

            solution = copy.deepcopy(game.current_game_state)
            game.reset_state()

            return game,  naive_solution, naive_steps, solution


def make_solvable_games(n, length, width, num_mines, file_name):

    games = []

    while len(games) < n:

        game, naive_solution, naive_steps, solution =  make_stimulus(length, width, num_mines)

        # Only accept games that have some easy squares
        # Some squares that are harder but have an easy solution process
        # And some squares that don't have any trivial way to solve

        if ((np.sum((naive_steps==0)*1) > 0) and 
             (np.sum(naive_steps == 1)*1 > 0) and
             (np.sum((naive_steps > 2)*1) > 0)):

            non_naive_rows,non_naive_cols = np.where(naive_steps == 0)
            non_naive_cells = list(zip(non_naive_rows, non_naive_cols))
            non_naive_probe = non_naive_cells[np.random.randint(0,len(non_naive_cells))]

            naive_easy_rows,naive_easy_cols = np.where(naive_steps == 1)
            naive_easy_cells = list(zip(naive_easy_rows, naive_easy_cols))
            naive_easy_probe = naive_easy_cells[np.random.randint(0,len(naive_easy_cells))]
            naive_easy_steps = naive_steps[naive_easy_probe[0],naive_easy_probe[1]]


            naive_hard_rows,naive_hard_cols = np.where(naive_steps > 1)
            naive_hard_cells = list(zip(naive_hard_rows, naive_hard_cols))
            naive_hard_probe = naive_hard_cells[np.random.randint(0,len(naive_hard_cells))]
            naive_hard_steps = naive_steps[naive_hard_probe[0],naive_hard_probe[1]]

            game_dct = {
                "length": length,
                "width":width,
                "num_mines":num_mines,
                "game_board": game.game_board,
                "naive_solution": naive_solution,
                "naive_steps": naive_steps,
                "solution": solution,
                "non_naive_probe":non_naive_probe,
                "naive_easy_probe": naive_easy_probe,
                "naive_hard_probe": naive_hard_probe,
                "naive_easy_steps": naive_easy_steps,
                "naive_hard_steps": naive_hard_steps
            }



            game.print_game()
            # print(naive_steps)
            # print("naive hard steps", naive_hard_steps)
            # print("="*25)

            games.append(copy.deepcopy(game_dct))


    with open(file_name, 'w') as file:
        file.write(json.dumps(games, cls=NpEncoder)) 
    



if __name__ == "__main__":


    length, width, num_mines = 5,5,6
    make_solvable_games(25, length, width, num_mines, 
                        f"stimuli_{length}_{width}_{num_mines}.json")