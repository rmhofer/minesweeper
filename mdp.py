import itertools as it
import random

import numpy as np

from game_solver import Solver


class MineSweeper:
    def __init__(self, board, x, y, n_mines):
        self.board = board.copy()
        H = board.shape[0]
        W = board.shape[1]

        self.x = x
        self.y = y
        self.n_mines = n_mines

        self.solver = Solver("naive")

        # 0 - given free, -1 - unknown, 1 - proved mine, 2 - proved safe
        # states = []
        # for assignment in it.product(*([[-1, 1, 2]] * n_mines)):
        #     for m in it.combinations([(i, j) for i in range(H) for j in range(W) if board[i, j] == -1], n_mines):
        #         s = np.zeros((H, W))
        #         for idx, (i, j) in enumerate(m):
        #             s[i, j] = assignment[idx]
        #         states.append(s)

        action = ["flag", "clear"]
        for i in range(H):
            for j in range(W):
                if board[i, j] > 0:
                    action.append(f"think-{i}-{j}")

        self.actions = action
        self.discount = 0.99

    def p_mine(self, s, x, y):
        if s[x, y] == 1:
            return 1.0
        elif s[x, y] == 0:
            return 0.0

        return (self.n_mines - (s == 1).sum()) / (s == -1).sum()

    def reward(self, s, a):
        if a == "flag":
            return 10 * self.p_mine(s, self.x, self.y)
        elif a == "clear":
            return 10 * (1 - self.p_mine(s, self.x, self.y))

        return -1

    def score(self, s, a, snew):
        if a in ("flag", "stop"):
            return 0.0

        snew = self.tr(s, a)[0]
        return 1.0 if np.all(snew == s) else 0.0

    def tr(self, s, a):
        if a == "flag":
            return [-1], [1], 10 * self.p_mine(s, self.x, self.y), True
        if a == "clear":
            return [-1], [1], 10 * (1 - self.p_mine(s, self.x, self.y)), True

        cell = [int(l) for l in a.split("-")[1:]]

        board = self.board.copy()
        # force observed state to match things that we've already proved
        board[s == 1] = -3
        board[s == 2] = -4

        snew = s.copy()
        for move in self.solver.deduce_moves_from_cell(board, cell[0], cell[1]):
            x, y, a = move
            if a == 1:  # deduced that x, y is mine
                snew[x, y] = 1
            elif a == 2:  # deduced that x, y is clear
                snew[x, y] = 2

        return [snew], [1], -0.5, False

    def hash(self, s):
        return str(s)


class Grid:
    def __init__(self, H, W):
        self.H = H
        self.W = W

        self.goal = (H - 1, W - 1)

        self.actions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # right, left, up, down
        self.discount = 0.95

    def tr(self, s, a):
        snew = [
            (np.clip(s[0] + a[0], 0, self.H - 1), np.clip(s[1] + a[1], 0, self.W - 1))
        ]

        if snew[0] == self.goal:
            return snew, [1], 1, True
        else:
            return snew, [1], -1, False

    def hash(self, s):
        return s


def mcts(mdp, root, max_iter=10, max_depth=10):
    Q = {}
    N = {}

    def uct(mdp, s, Q, N):
        s = mdp.hash(s)
        return np.argmax(Q[s] + np.sqrt(2 * np.log(N[s].sum()) / N[s]))

    def softmax(mdp, s, Q):
        s = mdp.hash(s)
        return random.choices(range(len(mdp.actions)), np.exp(0.1 * Q[s]) / np.exp(0.1 * Q[s]).sum())[0]

    def backup(history, Q, N, G):
        for s, a, reward in reversed(history):
            s = mdp.hash(s)
            N[s][a] += 1
            Q[s][a] += (reward + mdp.discount * G - Q[s][a]) / N[s][a]
            G = reward + mdp.discount * G

    for _ in range(max_iter):
        # breakpoint()
        s = root
        # selection
        done = False
        history = []

        while N.get(mdp.hash(s), None) is not None:
            # a = uct(mdp, s, Q, N)
            a = softmax(mdp, s, Q)
            # a = random.choice(range(len(mdp.actions)))
            ns, ps, reward, done = mdp.tr(s, mdp.actions[a])
            history.append((s, a, reward))

            if done:
                break

            s = random.choices(ns, ps)[0]

        # breakpoint()
        if done:
            backup(history, Q, N, 0)
            continue

        Q[mdp.hash(s)] = np.zeros(len(mdp.actions))
        N[mdp.hash(s)] = np.zeros(len(mdp.actions))

        G = 0
        i = 0

        while not done and i < max_depth:
            a = random.choice(range(len(mdp.actions)))
            ns, ps, reward, done = mdp.tr(s, mdp.actions[a])
            G += (mdp.discount ** (i - 1)) * reward

            if i == 0:
                history.append((s, a, reward))

            s = random.choice(ns)
            i += 1

        # breakpoint()

        s, a, reward = history.pop(-1)
        Q[mdp.hash(s)][a] = G
        N[mdp.hash(s)][a] = 1
        backup(history, Q, N, G)

    return Q


if __name__ == "__main__":
    # g = Grid(4, 4)
    game_board = np.array(
        [
            [1, 1, 1, 1, 1],
            [1, -1, -1, -1, -1],
        ]
    )

    s = game_board.copy()
    s[s != -1] = 0

    m = MineSweeper(game_board, 1, 4, 2)
    Q = mcts(m, s)
