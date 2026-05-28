# ─────────────────────────────────────────────────────
# CO4 : Utility Functions, Minimax,
#       Alpha-Beta Pruning,
#       Evaluation Functions,
#       Iterative Deepening,
#       Expectimax,
#       Rationality and Policy Selection,
#       Multi-Agent Reasoning
# ─────────────────────────────────────────────────────

import random
from copy import deepcopy

TRACK_LENGTH = 52
HOME_VALUE = 58

COLOR_START = {
    'Red': 0,
    'Blue': 13,
    'Green': 26,
    'Yellow': 39
}

SAFE_SQUARES = {0, 8, 13, 21, 26, 34, 39, 47}

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


# ─────────────────────────────────────────────────────
# PLAYER CLASS
# Multi-Agent Reasoning
# ─────────────────────────────────────────────────────

class Player:

    def __init__(self, color):

        self.color = color
        self.start = COLOR_START[color]

        self.tokens = [Token(color, i + 1) for i in range(4)]

    @property
    def all_home(self):
        return all(t.in_home for t in self.tokens)


# ─────────────────────────────────────────────────────
# UTILITY FUNCTION
# Measures desirability of state
# ─────────────────────────────────────────────────────

def utility_function(player):

    utility = 0

    for token in player.tokens:

        if token.in_home:
            utility += 100

        elif token.in_base:
            utility -= 20

        else:
            utility += token.pos

    return utility


# ─────────────────────────────────────────────────────
# EVALUATION FUNCTION
# Heuristic evaluation
# ─────────────────────────────────────────────────────

def evaluation_function(player):

    score = 0

    for token in player.tokens:

        if token.in_home:
            score += 200

        elif token.on_track:
            score += token.pos * 2

        elif token.in_base:
            score -= 10

    return score


# ─────────────────────────────────────────────────────
# APPLY MOVE
# ─────────────────────────────────────────────────────

def apply_move(token, dice):

    if token.in_base and dice == 6:
        token.pos = 0

    elif not token.in_base:

        if token.pos + dice <= HOME_VALUE:
            token.pos += dice


# ─────────────────────────────────────────────────────
# GENERATE POSSIBLE MOVES
# ─────────────────────────────────────────────────────

def generate_moves(player):

    moves = []

    for token in player.tokens:

        for dice in range(1, 7):

            if token.in_base and dice == 6:
                moves.append((token, dice))

            elif not token.in_base:

                if token.pos + dice <= HOME_VALUE:
                    moves.append((token, dice))

    return moves


# ─────────────────────────────────────────────────────
# MINIMAX ALGORITHM
# ─────────────────────────────────────────────────────

def minimax(player, depth, maximizing_player):

    if depth == 0 or player.all_home:
        return evaluation_function(player)

    if maximizing_player:

        max_eval = float('-inf')

        for token, dice in generate_moves(player):

            temp_player = deepcopy(player)

            temp_token = temp_player.tokens[token.tid - 1]

            apply_move(temp_token, dice)

            eval_score = minimax(
                temp_player,
                depth - 1,
                False
            )

            max_eval = max(max_eval, eval_score)

        return max_eval

    else:

        min_eval = float('inf')

        for token, dice in generate_moves(player):

            temp_player = deepcopy(player)

            temp_token = temp_player.tokens[token.tid - 1]

            apply_move(temp_token, dice)

            eval_score = minimax(
                temp_player,
                depth - 1,
                True
            )

            min_eval = min(min_eval, eval_score)

        return min_eval


# ─────────────────────────────────────────────────────
# ALPHA-BETA PRUNING
# ─────────────────────────────────────────────────────

def alpha_beta(player,
               depth,
               alpha,
               beta,
               maximizing_player):

    if depth == 0 or player.all_home:
        return evaluation_function(player)

    if maximizing_player:

        value = float('-inf')

        for token, dice in generate_moves(player):

            temp_player = deepcopy(player)

            temp_token = temp_player.tokens[token.tid - 1]

            apply_move(temp_token, dice)

            value = max(
                value,
                alpha_beta(
                    temp_player,
                    depth - 1,
                    alpha,
                    beta,
                    False
                )
            )

            alpha = max(alpha, value)

            if alpha >= beta:
                break

        return value

    else:

        value = float('inf')

        for token, dice in generate_moves(player):

            temp_player = deepcopy(player)

            temp_token = temp_player.tokens[token.tid - 1]

            apply_move(temp_token, dice)

            value = min(
                value,
                alpha_beta(
                    temp_player,
                    depth - 1,
                    alpha,
                    beta,
                    True
                )
            )

            beta = min(beta, value)

            if alpha >= beta:
                break

        return value


# ─────────────────────────────────────────────────────
# ITERATIVE DEEPENING
# ─────────────────────────────────────────────────────

def iterative_deepening(player, max_depth):

    best_score = None

    for depth in range(1, max_depth + 1):

        score = minimax(player, depth, True)

        print("Depth", depth, "Score =", score)

        best_score = score

    return best_score


# ─────────────────────────────────────────────────────
# EXPECTIMAX
# Handles stochastic dice rolls
# ─────────────────────────────────────────────────────

def expectimax(player, depth):

    if depth == 0:
        return evaluation_function(player)

    expected_value = 0

    for dice in range(1, 7):

        probability = 1 / 6

        best_score = float('-inf')

        for token in player.tokens:

            temp_player = deepcopy(player)

            temp_token = temp_player.tokens[token.tid - 1]

            apply_move(temp_token, dice)

            score = evaluation_function(temp_player)

            best_score = max(best_score, score)

        expected_value += probability * best_score

    return expected_value


# ─────────────────────────────────────────────────────
# RATIONAL POLICY SELECTION
# Select best action
# ─────────────────────────────────────────────────────

def select_best_policy(player):

    best_move = None
    best_score = float('-inf')

    for token, dice in generate_moves(player):

        temp_player = deepcopy(player)

        temp_token = temp_player.tokens[token.tid - 1]

        apply_move(temp_token, dice)

        score = evaluation_function(temp_player)

        if score > best_score:

            best_score = score
            best_move = (token.tid, dice)

    return best_move


# ─────────────────────────────────────────────────────
# MULTI-AGENT REASONING
# Compare utilities of players
# ─────────────────────────────────────────────────────

def compare_players(players):

    print("\nPlayer Utilities")

    for player in players:

        utility = utility_function(player)

        print(player.color, "Utility =", utility)


# ─────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────

players = [
    Player("Red"),
    Player("Blue")
]

player = players[0]

# Initialize sample positions
player.tokens[0].pos = 10
player.tokens[1].pos = 20
player.tokens[2].pos = 35

# Utility Function
print("Utility Function:",
      utility_function(player))

# Evaluation Function
print("Evaluation Function:",
      evaluation_function(player))

# Minimax
print("\nMinimax Result:",
      minimax(player, 2, True))

# Alpha-Beta Pruning
print("\nAlpha-Beta Result:",
      alpha_beta(
          player,
          2,
          float('-inf'),
          float('inf'),
          True
      ))

# Iterative Deepening
print("\nIterative Deepening")
iterative_deepening(player, 3)

# Expectimax
print("\nExpectimax Result:",
      expectimax(player, 2))

# Rational Policy Selection
best_policy = select_best_policy(player)

print("\nBest Policy:")
print("Move Token", best_policy[0],
      "with Dice", best_policy[1])

# Multi-Agent Reasoning
compare_players(players)