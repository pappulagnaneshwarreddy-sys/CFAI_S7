# ─────────────────────────────────────────────────────
# CO1 : Agent Model (PEAS), Environment Types,
#       Problem Formulation, Knowledge Representation,
#       Python Essentials for AI Algorithms
# ─────────────────────────────────────────────────────

import random
from copy import deepcopy

# ─────────────────────────────────────────────────────
# KNOWLEDGE REPRESENTATION
# Using dictionaries and sets
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
# Represents state of a token
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
# AGENT MODEL (PEAS)
# ─────────────────────────────────────────────────────

class Player:

    def __init__(self, color, is_human=True):
        self.color = color
        self.is_human = is_human
        self.start = COLOR_START[color]

        # List data structure
        self.tokens = [Token(color, i + 1) for i in range(4)]

    # Goal test
    @property
    def all_home(self):
        return all(t.in_home for t in self.tokens)

    # Action generation
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
# PROBLEM FORMULATION
# State, Action, Transition
# ─────────────────────────────────────────────────────

def apply_move(player, token, dice):

    # Transition model

    if token.in_base and dice == 6:
        token.pos = 0

    else:
        token.pos += dice


# ─────────────────────────────────────────────────────
# ENVIRONMENT TYPE
# Stochastic environment using dice
# ─────────────────────────────────────────────────────

def roll_dice():
    return random.randint(1, 6)


# ─────────────────────────────────────────────────────
# AI AGENT
# ─────────────────────────────────────────────────────

def ai_choose_token(player, movable_tokens):

    # Simple AI: random action selection
    return random.choice(movable_tokens)


# ─────────────────────────────────────────────────────
# MAIN EXECUTION
# ─────────────────────────────────────────────────────

player = Player("Red", is_human=False)

dice = roll_dice()

print("Dice =", dice)

movable = player.movable_tokens(dice)

if movable:

    chosen_token = ai_choose_token(player, movable)

    # Deep copy for simulation
    simulation_player = deepcopy(player)

    apply_move(player, chosen_token, dice)

    print("Moved Token:", chosen_token.tid)
    print("New Position:", chosen_token.pos)

else:
    print("No valid moves")