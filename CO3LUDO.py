# ─────────────────────────────────────────────────────
# CO3 : CSP Modeling, Backtracking,
#       Constraint Propagation,
#       CSP Heuristics (MRV, Degree, LCV),
#       Local Search for CSP,
#       Scheduling / Timetabling,
#       SAT Intuition, Explainability
# ─────────────────────────────────────────────────────

import random
from copy import deepcopy

# ─────────────────────────────────────────────────────
# CSP MODELING
# Variables = Tokens
# Domain = Possible Positions
# Constraints = Valid moves
# ─────────────────────────────────────────────────────

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

    # Constraint checking
    def movable_tokens(self, dice):

        result = []

        for t in self.tokens:

            if t.in_home:
                continue

            if t.in_base:
                if dice == 6:
                    result.append(t)

            else:
                if t.pos + dice <= HOME_VALUE:
                    result.append(t)

        return result


# ─────────────────────────────────────────────────────
# CONSTRAINT PROPAGATION
# Remove invalid moves automatically
# ─────────────────────────────────────────────────────

def constraint_propagation(player, dice):

    valid = []

    for token in player.tokens:

        if token.in_home:
            continue

        if token.in_base and dice != 6:
            continue

        if not token.in_base:
            if token.pos + dice > HOME_VALUE:
                continue

        valid.append(token)

    return valid


# ─────────────────────────────────────────────────────
# MRV HEURISTIC
# Minimum Remaining Values
# Choose token closest to HOME
# ─────────────────────────────────────────────────────

def mrv_heuristic(tokens):

    best = None
    best_remaining = float('inf')

    for t in tokens:

        if t.in_base:
            remaining = HOME_VALUE
        else:
            remaining = HOME_VALUE - t.pos

        if remaining < best_remaining:
            best_remaining = remaining
            best = t

    return best


# ─────────────────────────────────────────────────────
# DEGREE HEURISTIC
# Prefer token affecting more opponents
# ─────────────────────────────────────────────────────

def degree_heuristic(player, players):

    best = None
    highest_degree = -1

    for token in player.tokens:

        if token.in_base:
            continue

        degree = 0

        for op in players:

            if op.color == player.color:
                continue

            for ot in op.tokens:

                if ot.on_track:
                    diff = abs(token.pos - ot.pos)

                    if diff <= 6:
                        degree += 1

        if degree > highest_degree:
            highest_degree = degree
            best = token

    return best


# ─────────────────────────────────────────────────────
# LCV HEURISTIC
# Least Constraining Value
# ─────────────────────────────────────────────────────

def lcv_heuristic(player, dice):

    best_token = None
    least_conflict = float('inf')

    for token in player.tokens:

        if token.in_base and dice != 6:
            continue

        future_pos = 0 if token.in_base else token.pos + dice

        conflict = 0

        if future_pos in SAFE_SQUARES:
            conflict -= 1

        if future_pos > HOME_VALUE:
            conflict += 10

        if conflict < least_conflict:
            least_conflict = conflict
            best_token = token

    return best_token


# ─────────────────────────────────────────────────────
# BACKTRACKING SEARCH
# Recursive CSP solving
# ─────────────────────────────────────────────────────

def backtracking(position):

    print("Backtracking Position:", position)

    if position == HOME_VALUE:
        return True

    for dice in range(1, 7):

        next_pos = position + dice

        if next_pos <= HOME_VALUE:

            if backtracking(next_pos):
                return True

    return False


# ─────────────────────────────────────────────────────
# LOCAL SEARCH FOR CSP
# Hill-climbing style improvement
# ─────────────────────────────────────────────────────

def local_search(token):

    current = deepcopy(token)

    while not current.in_home:

        best_move = None
        best_score = -1

        for dice in range(1, 7):

            temp = deepcopy(current)

            if temp.in_base and dice == 6:
                temp.pos = 0

            elif not temp.in_base:
                temp.pos += dice

            score = temp.pos

            if score > best_score:
                best_score = score
                best_move = dice

        if current.in_base and best_move == 6:
            current.pos = 0
        else:
            current.pos += best_move

        print("Local Search Move:",
              best_move,
              "Position:",
              current.pos)

    return True


# ─────────────────────────────────────────────────────
# SCHEDULING / TIMETABLING
# Turn scheduling example
# ─────────────────────────────────────────────────────

def schedule_turns(players):

    print("\nTurn Schedule:")

    for i, player in enumerate(players):

        print("Turn", i + 1, "→", player.color)


# ─────────────────────────────────────────────────────
# SAT INTUITION
# Boolean constraint satisfaction
# ─────────────────────────────────────────────────────

def sat_check(token, dice):

    # TRUE if move is legal

    if token.in_base and dice != 6:
        return False

    if not token.in_base:

        if token.pos + dice > HOME_VALUE:
            return False

    return True


# ─────────────────────────────────────────────────────
# EXPLAINABILITY
# AI reasoning explanation
# ─────────────────────────────────────────────────────

def explain_move(token, dice):

    print("\nExplainable AI Decision")

    if token.in_base and dice == 6:
        print("Reason: Token can leave base")

    elif token.pos + dice <= HOME_VALUE:
        print("Reason: Safe valid movement")

    else:
        print("Reason: Invalid move")


# ─────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────

players = [
    Player("Red"),
    Player("Blue"),
    Player("Green")
]

player = players[0]

dice = random.randint(1, 6)

print("Dice =", dice)

# Constraint propagation
valid_tokens = constraint_propagation(player, dice)

print("\nValid Tokens:")

for t in valid_tokens:
    print("Token", t.tid)

# MRV
mrv_token = mrv_heuristic(player.tokens)

print("\nMRV Selected Token:", mrv_token.tid)

# Degree heuristic
degree_token = degree_heuristic(player, players)

if degree_token:
    print("Degree Heuristic Token:", degree_token.tid)

# LCV
lcv_token = lcv_heuristic(player, dice)

print("LCV Selected Token:", lcv_token.tid)

# Backtracking
print("\nBacktracking Search")
backtracking(0)

# Local Search
print("\nLocal Search")
local_search(player.tokens[0])

# Scheduling
schedule_turns(players)

# SAT intuition
print("\nSAT Check:",
      sat_check(player.tokens[0], dice))

# Explainability
explain_move(player.tokens[0], dice)