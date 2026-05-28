# ─────────────────────────────────────────────────────
# CO2 : BFS, DFS, UCS, A*, Greedy Search,
#       Heuristics, Memory-Bounded Search,
#       Graph and Puzzle Search
# ─────────────────────────────────────────────────────

import random
from copy import deepcopy
from queue import PriorityQueue
from collections import deque

TRACK_LENGTH = 52
HOME_VALUE = 58

SAFE_SQUARES = {0, 8, 13, 21, 26, 34, 39, 47}

COLOR_START = {
    'Red': 0,
    'Blue': 13,
    'Green': 26,
    'Yellow': 39
}

# ─────────────────────────────────────────────────────
# TOKEN CLASS
# ─────────────────────────────────────────────────────

class Token:

    def __init__(self, color, tid):
        self.color = color
        self.tid = tid
        self.pos = -1

    @property
    def in_base(self):
        return self.pos == -1

    @property
    def in_home(self):
        return self.pos == HOME_VALUE

    @property
    def on_track(self):
        return 0 <= self.pos < TRACK_LENGTH

    def global_pos(self, start):
        if self.on_track:
            return (start + self.pos) % TRACK_LENGTH
        return None


# ─────────────────────────────────────────────────────
# PLAYER CLASS
# ─────────────────────────────────────────────────────

class Player:

    def __init__(self, color):
        self.color = color
        self.start = COLOR_START[color]
        self.tokens = [Token(color, i + 1) for i in range(4)]


# ─────────────────────────────────────────────────────
# HEURISTIC FUNCTION
# Used in Greedy and A*
# ─────────────────────────────────────────────────────

def heuristic(token):

    # Distance remaining to reach HOME
    if token.in_base:
        return HOME_VALUE

    return HOME_VALUE - token.pos


# ─────────────────────────────────────────────────────
# APPLY MOVE
# State transition
# ─────────────────────────────────────────────────────

def apply_move(token, dice):

    if token.in_base and dice == 6:
        token.pos = 0

    elif token.pos + dice <= HOME_VALUE:
        token.pos += dice


# ─────────────────────────────────────────────────────
# BFS SEARCH
# Breadth First Search
# ─────────────────────────────────────────────────────

def bfs_search(start_pos):

    queue = deque()
    visited = set()

    queue.append(start_pos)
    visited.add(start_pos)

    while queue:

        current = queue.popleft()

        print("BFS Visiting:", current)

        if current == HOME_VALUE:
            return True

        for dice in range(1, 7):

            next_pos = current + dice

            if next_pos <= HOME_VALUE and next_pos not in visited:
                queue.append(next_pos)
                visited.add(next_pos)

    return False


# ─────────────────────────────────────────────────────
# DFS SEARCH
# Depth First Search
# ─────────────────────────────────────────────────────

def dfs_search(position, visited):

    print("DFS Visiting:", position)

    if position == HOME_VALUE:
        return True

    visited.add(position)

    for dice in range(1, 7):

        next_pos = position + dice

        if next_pos <= HOME_VALUE and next_pos not in visited:

            if dfs_search(next_pos, visited):
                return True

    return False


# ─────────────────────────────────────────────────────
# UCS SEARCH
# Uniform Cost Search
# ─────────────────────────────────────────────────────

def uniform_cost_search(start_pos):

    pq = PriorityQueue()

    pq.put((0, start_pos))

    visited = set()

    while not pq.empty():

        cost, current = pq.get()

        if current in visited:
            continue

        visited.add(current)

        print("UCS Visiting:", current, "Cost:", cost)

        if current == HOME_VALUE:
            return True

        for dice in range(1, 7):

            next_pos = current + dice

            if next_pos <= HOME_VALUE:
                pq.put((cost + 1, next_pos))

    return False


# ─────────────────────────────────────────────────────
# GREEDY SEARCH
# Uses only heuristic h(n)
# ─────────────────────────────────────────────────────

def greedy_search(token):

    current = deepcopy(token)

    while not current.in_home:

        best_dice = None
        best_score = float('inf')

        for dice in range(1, 7):

            temp = deepcopy(current)

            apply_move(temp, dice)

            score = heuristic(temp)

            if score < best_score:
                best_score = score
                best_dice = dice

        apply_move(current, best_dice)

        print("Greedy Move:", best_dice,
              "Position:", current.pos)

    return True


# ─────────────────────────────────────────────────────
# A* SEARCH
# f(n) = g(n) + h(n)
# ─────────────────────────────────────────────────────

def a_star_search(start_pos):

    pq = PriorityQueue()

    pq.put((0, 0, start_pos))

    visited = set()

    while not pq.empty():

        f, g, current = pq.get()

        if current in visited:
            continue

        visited.add(current)

        print("A* Visiting:", current,
              "g =", g,
              "h =", HOME_VALUE - current)

        if current == HOME_VALUE:
            return True

        for dice in range(1, 7):

            next_pos = current + dice

            if next_pos <= HOME_VALUE:

                new_g = g + 1
                new_h = HOME_VALUE - next_pos
                new_f = new_g + new_h

                pq.put((new_f, new_g, next_pos))

    return False


# ─────────────────────────────────────────────────────
# MEMORY-BOUNDED SEARCH IDEA
# Simple depth limit
# ─────────────────────────────────────────────────────

def depth_limited_search(position, depth):

    if position == HOME_VALUE:
        return True

    if depth == 0:
        return False

    for dice in range(1, 7):

        next_pos = position + dice

        if next_pos <= HOME_VALUE:

            if depth_limited_search(next_pos, depth - 1):
                return True

    return False


# ─────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────

player = Player("Red")

token = player.tokens[0]

print("\n--- BFS ---")
bfs_search(0)

print("\n--- DFS ---")
dfs_search(0, set())

print("\n--- UCS ---")
uniform_cost_search(0)

print("\n--- Greedy Search ---")
greedy_search(token)

print("\n--- A* Search ---")
a_star_search(0)

print("\n--- Memory-Bounded Search ---")
result = depth_limited_search(0, 10)

print("Depth Limited Result:", result)