from enum import IntEnum
import itertools as it
import random

import numpy as np
from scipy.linalg import lu

debug = False


def bp():
    if debug:
        breakpoint()


def P(*a):
    if debug:
        print(*a)


class BoardState(IntEnum):
    unknown = -1
    given = 0
    proved_mine = 1
    proved_clear = 2


class MineSweeper:
    def __init__(self, board, x, y, n_mines, discount=0.99):
        self.board = board.copy()
        H = board.shape[0]
        W = board.shape[1]
        self.H = H
        self.W = W

        self.x = x
        self.y = y
        self.n_mines = n_mines

        self.unknown = BoardState.unknown
        self.given = BoardState.given
        self.proved_mine = BoardState.proved_mine
        self.proved_clear = BoardState.proved_clear

        action = ["flag", "clear"]
        for i in range(H):
            for j in range(W):
                if board[i, j] > 0:
                    # action.append(f"1_{i}-{j}")
                    action.append([(i, j)])

        for (i, j), (k, l) in it.product(
            it.product(range(H), range(W)), it.product(range(H), range(W))
        ):
            if (i, j) == (k, l):
                continue
            if board[i, j] <= 0 or board[k, l] <= 0:
                continue
            if abs(i - k) + abs(j - l) > 3:
                continue

            # action.append(f"2_{i}-{j}_{k}-{l}")
            action.append([(i, j), (k, l)])

        self.actions = action
        self.discount = discount

    def solve_one(self, state, cell):
        x, y = cell[0]
        mini_board = state[
            max(x - 1, 0) : min(x + 2, self.H), max(y - 1, 0) : min(y + 2, self.W)
        ]
        count = self.board[x, y]

        n_mines = count - (mini_board == self.proved_mine).sum()
        if n_mines == 0:
            new_val = self.proved_clear.value
        elif n_mines == (mini_board == self.unknown).sum():
            new_val = self.proved_mine.value
        else:
            return
            yield

        for i, j in it.product((x - 1, x, x + 1), (y - 1, y, y + 1)):
            if (i, j) == (x, y):
                continue
            if i < 0 or i >= self.H or j < 0 or j >= self.W:
                continue

            if state[i, j] == self.unknown:
                yield i, j, new_val

    def linear_equations(self, state, cells):
        unknowns = {}  # cell -> column index
        A = np.zeros((len(cells), len(cells) * 8))
        b = np.zeros(len(cells))

        n_unknowns = 0
        for idx, (x, y) in enumerate(cells):
            count = self.board[x, y]
            for i, j in it.product((x - 1, x, x + 1), (y - 1, y, y + 1)):
                if (i, j) == (x, y):
                    continue
                if i < 0 or i >= self.H or j < 0 or j >= self.W:
                    continue

                if state[i, j] == self.unknown:
                    unknown_idx = unknowns.setdefault((i, j), n_unknowns)
                    A[idx, unknown_idx] = 1
                    n_unknowns += 1 if unknown_idx == n_unknowns else 0

                if state[i, j] == self.proved_mine:
                    count -= 1

            b[idx] = count

        A = A[:, :n_unknowns]
        return A, b, unknowns

    # def solve_multiple(self, state, cells):
    #     unknowns = {}
    #     A = np.zeros((len(cells), len(cells) * 8))
    #     b = np.zeros(len(cells))

    #     n_unknowns = 0
    #     for idx, (x, y) in enumerate(cells):
    #         count = self.board[x, y]
    #         for i, j in it.product((x - 1, x, x + 1), (y - 1, y, y + 1)):
    #             if (i, j) == (x, y):
    #                 continue
    #             if i < 0 or i >= self.H or j < 0 or j >= self.W:
    #                 continue

    #             if state[i, j] == self.unknown:
    #                 unknown_idx = unknowns.setdefault((i, j), n_unknowns)
    #                 A[idx, unknown_idx] = 1
    #                 n_unknowns += 1 if unknown_idx == n_unknowns else 0

    #             if state[i, j] == self.proved_mine:
    #                 count -= 1

    #         b[idx] = count

    #     A = A[:, :n_unknowns]

    #     x = np.linalg.lstsq(A, b, rcond=None)[0]
    #     for (i, j), unknown_idx in unknowns.items():
    #         if np.isclose(x[unknown_idx], 0):
    #             yield i, j, self.proved_clear.value
    #         if np.isclose(x[unknown_idx], 1):
    #             yield i, j, self.proved_mine.value

    # def solve_multiple_bp(self, state, cells):
    #     import cvxopt

    #     A, b, unknowns = self.linear_equations(state, cells)

    #     n = A.shape[1]

    #     c = cvxopt.matrix(np.ones(n))
    #     G = cvxopt.matrix(np.concatenate([np.eye(n), -np.eye(n)]))
    #     h = cvxopt.matrix(np.concatenate([np.ones(n), np.zeros(n)]))
    #     sol = cvxopt.solvers.lp(c, G, h, cvxopt.matrix(A), cvxopt.matrix(b))
    #     x = sol["x"]

    #     for (i, j), unknown_idx in unknowns.items():
    #         if np.isclose(x[unknown_idx], 0):
    #             yield i, j, self.proved_clear.value
    #         if np.isclose(x[unknown_idx], 1):
    #             yield i, j, self.proved_mine.value

    def solve_multiple_rref(self, state, cells):
        A, b, unknowns = self.linear_equations(state, cells)
        P("A, b", A, b)

        *_, U = lu(np.concatenate([A, b[:, None]], axis=1))
        P("U", U)

        proved = np.ones(A.shape[1]) * self.unknown.value
        for i, row in reversed(list(enumerate(U[:, :-1]))):
            orig_row = row.copy()
            P("original row", row)
            mask = proved != self.unknown.value
            target = U[i, -1] - (proved[mask] @ row[mask])
            row = row[~mask]
            ub = (row > 0).sum()
            lb = -(row < 0).sum()
            P("bounds", ub, lb)
            P("new row", row)
            P("target", U[i, -1], "adjusted target", target)

            if ub == target:
                for k in np.where(orig_row != 0)[0]:
                    if mask[k]:
                        continue
                    proved[k] = 1 if orig_row[k] == 1 else 0

            if lb == target:
                for k in np.where(orig_row != 0)[0]:
                    if mask[k]:
                        continue
                    proved[k] = 1 if orig_row[k] == -1 else 0

            P("proved", proved)

        for (i, j), unknown_idx in unknowns.items():
            p = proved[unknown_idx]
            if np.isclose(p, 1):
                yield i, j, self.proved_mine.value
            elif np.isclose(p, 0):
                yield i, j, self.proved_clear.value

    def p_mine(self, s, x, y):
        if s[x, y] == self.proved_mine:
            return 1.0
        elif s[x, y] == self.proved_clear:
            return 0.0

        return (self.n_mines - (s == self.proved_mine).sum()) / (
            s == self.unknown
        ).sum()

    def tr(self, s, a):
        if a == "flag":
            return [s], [0], 10 * self.p_mine(s, self.x, self.y), True
        if a == "clear":
            return [s], [0], 10 * (1 - self.p_mine(s, self.x, self.y)), True

        solver = self.solve_one
        if len(a) > 1:
            solver = self.solve_multiple_rref

        snew = s.copy()
        for move in solver(s, a):
            x, y, v = move
            snew[x, y] = v

        return [snew], [1], -0.5 * 2 ** len(a), False

    def traverse(self, s):
        states = [s]

        names = {self.hash(s)}
        stack = [s]

        while len(stack) > 0:
            s = stack.pop()
            P(s)
            for a in range(2, len(self.actions)):
                P("trying ", self.actions[a])
                snew, _, _, done = self.tr(s, self.actions[a])
                if self.hash(snew[0]) not in names:
                    names.add(self.hash(snew[0]))
                    stack.append(snew[0])
                    states.append(snew[0])

        return states

    def board_to_state(self, board):
        s = np.array(board).copy()
        s[s != -1] = self.given.value
        return s

    def hash(self, s):
        return str(s)


class Grid:
    def __init__(self, H, W):
        self.H = H
        self.W = W

        self.goal = (H - 1, W - 1)

        self.actions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
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
        return random.choices(
            range(len(mdp.actions)), np.exp(0.1 * Q[s]) / np.exp(0.1 * Q[s]).sum()
        )[0]
        # return random.choices(range(len(mdp.actions) - 2), np.exp(0.1 * Q[s][2:]) / np.exp(0.1 * Q[s][2:]).sum())[0]

    def backup(history, Q, N, G):
        for s, a, reward in reversed(history):
            s = mdp.hash(s)
            N[s][a] += 1
            Q[s][a] += (reward + mdp.discount * G - Q[s][a]) / N[s][a]
            G = reward + mdp.discount * G

    for _ in range(max_iter):
        s = root
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
            G += (mdp.discount**i) * reward

            if i == 0:
                history.append((s, a, reward))

            s = random.choice(ns)
            i += 1

        s, a, reward = history.pop(-1)
        Q[mdp.hash(s)][a] = G
        N[mdp.hash(s)][a] = 1
        backup(history, Q, N, G)

    return Q, N


def vi(mdp, states, rtol=1e-3):
    V = {mdp.hash(s): 0 for s in states}
    delta = 1
    while delta > rtol:
        delta = 0
        for s in states:
            v_old = V[mdp.hash(s)]
            V[mdp.hash(s)] = max(
                [
                    sum(
                        p[0] * (r + mdp.discount * V[mdp.hash(snew[0])])
                        if not done
                        else r
                        for snew, p, r, done in [mdp.tr(s, a)]
                    )
                    for a in mdp.actions
                ]
            )
            delta = max(delta, abs(V[mdp.hash(s)] - v_old))

    Q = {}
    for s in states:
        actions = np.zeros(len(mdp.actions))
        Q[mdp.hash(s)] = actions
        for i, a in enumerate(mdp.actions):
            snew, ps, r, done = mdp.tr(s, a)
            actions[i] = sum(
                (p * r + mdp.discount * V[mdp.hash(snew)] if not done else r)
                for snew, p in zip(snew, ps)
            )

    return Q, V


class Node:
    def __init__(self, state, value):
        self.state = state
        self.children = {}
        self.data = {}
        self.value = value


def tree(mdp, s, Q, V):
    root = Node(s, V[mdp.hash(s)])
    stack = [root]
    nodes = {mdp.hash(root.state): root}
    while stack:
        node = stack.pop()
        m = Q[mdp.hash(node.state)].max()
        for i, a in enumerate(mdp.actions):
            if Q[mdp.hash(node.state)][i] < m:
                continue

            snew, _, r, done = mdp.tr(node.state, a)
            snew = snew[0]
            if done:
                continue

            if mdp.hash(snew) in nodes:
                child = nodes[mdp.hash(snew)]
            else:
                child = Node(snew, V[mdp.hash(snew)])
                nodes[mdp.hash(snew)] = child
                stack.append(child)

            node.children[i] = child
            node.data[i] = (a, r)

    return root


if __name__ == "__main__":
    # g = Grid(4, 4)
    board = np.array(
        [
            [1, 1, 1, 1, 1],
            [1, -1, -1, -1, -1],
        ]
    )
    board = np.array([[1, 2, 1], [-1, -1, -1]])

    s = board.copy()
    s[s != -1] = 0

    # m = MineSweeper(board, 1, 4, 2)
    m = MineSweeper(board, 1, 2, 2)
    states = m.traverse(s)
    Q, V = vi(m, states)
    # Q, N = mcts(m, s, max_iter=500)
    # print(Q[m.hash(s)])
