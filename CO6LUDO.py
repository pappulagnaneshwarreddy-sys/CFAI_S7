# ─────────────────────────────────────────────────────
# CO6 : Combine Search + CSP +
#       Probabilistic Inference,
#       Decision Logic,
#       Hybrid Architectures,
#       Explainable Reasoning Traces,
#       Performance Engineering,
#       Failure Analysis,
#       Ethics / Limitations,
#       Readiness for ML / DL / NLP / GenAI
# ─────────────────────────────────────────────────────

import random
import time
from copy import deepcopy

# ─────────────────────────────────────────────────────
# GAME CONSTANTS
# ─────────────────────────────────────────────────────

TRACK_LENGTH = 52
HOME_VALUE = 58

SAFE_SQUARES = {0, 8, 13, 21, 26, 34, 39, 47}

COLOR_START = {
    "Red": 0,
    "Blue": 13
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


# ─────────────────────────────────────────────────────
# PLAYER CLASS
# ─────────────────────────────────────────────────────

class Player:

    def __init__(self, color):

        self.color = color
        self.start = COLOR_START[color]

        self.tokens = [Token(color, i + 1) for i in range(4)]

    # CSP constraint checking
    def movable_tokens(self, dice):

        valid = []

        for t in self.tokens:

            if t.in_home:
                continue

            if t.in_base:

                if dice == 6:
                    valid.append(t)

            else:

                if t.pos + dice <= HOME_VALUE:
                    valid.append(t)

        return valid


# ─────────────────────────────────────────────────────
# SEARCH + CSP + PROBABILITY
# HYBRID AI ARCHITECTURE
# ─────────────────────────────────────────────────────

def hybrid_ai_decision(player, dice):

    movable = player.movable_tokens(dice)

    if not movable:
        return None

    best_token = None
    best_score = float("-inf")

    for token in movable:

        score = evaluate_token(player, token, dice)

        if score > best_score:

            best_score = score
            best_token = token

    return best_token


# ─────────────────────────────────────────────────────
# SEARCH COMPONENT
# Heuristic evaluation
# ─────────────────────────────────────────────────────

def heuristic(token):

    if token.in_base:
        return -20

    return token.pos


# ─────────────────────────────────────────────────────
# PROBABILISTIC INFERENCE
# Expected success probability
# ─────────────────────────────────────────────────────

def probability_of_safety(position):

    if position in SAFE_SQUARES:
        return 0.95

    return 0.50


# ─────────────────────────────────────────────────────
# DECISION LOGIC
# Combines heuristic + probability
# ─────────────────────────────────────────────────────

def evaluate_token(player, token, dice):

    simulated = deepcopy(token)

    # Apply move

    if simulated.in_base and dice == 6:
        simulated.pos = 0

    elif not simulated.in_base:
        simulated.pos += dice

    # Search score
    heuristic_score = heuristic(simulated)

    # Probability score
    safety_probability = probability_of_safety(simulated.pos)

    final_score = heuristic_score + (safety_probability * 100)

    return final_score


# ─────────────────────────────────────────────────────
# EXPLAINABLE REASONING TRACE
# ─────────────────────────────────────────────────────

def explain_decision(token, dice):

    print("\nExplainable Reasoning Trace")

    print("Selected Token :", token.tid)

    print("Dice Value     :", dice)

    if token.in_base and dice == 6:
        print("Reason          : Token exits base")

    elif token.pos in SAFE_SQUARES:
        print("Reason          : Safe position")

    else:
        print("Reason          : Maximum heuristic score")


# ─────────────────────────────────────────────────────
# PERFORMANCE ENGINEERING
# Measure execution time
# ─────────────────────────────────────────────────────

def performance_test(player):

    start_time = time.time()

    for _ in range(1000):

        dice = random.randint(1, 6)

        hybrid_ai_decision(player, dice)

    end_time = time.time()

    total_time = end_time - start_time

    print("\nPerformance Test")

    print("Execution Time =", total_time, "seconds")


# ─────────────────────────────────────────────────────
# FAILURE ANALYSIS
# Analyze invalid states
# ─────────────────────────────────────────────────────

def failure_analysis(player, dice):

    movable = player.movable_tokens(dice)

    if not movable:

        print("\nFailure Analysis")

        print("No valid moves available")

        if dice != 6:

            print("Reason: Tokens stuck in base")

        else:

            print("Reason: Constraints prevent movement")


# ─────────────────────────────────────────────────────
# ETHICS / LIMITATIONS
# AI fairness and constraints
# ─────────────────────────────────────────────────────

def ethics_and_limitations():

    print("\nEthics and Limitations")

    print("- AI decisions depend on heuristics")

    print("- Random dice introduces uncertainty")

    print("- AI may not always select globally optimal move")

    print("- Limited search depth affects intelligence")

    print("- Bias may occur in evaluation function")


# ─────────────────────────────────────────────────────
# READINESS FOR ML / DL / NLP / GenAI
# Foundation concepts
# ─────────────────────────────────────────────────────

def ai_course_readiness():

    print("\nAI Course Readiness")

    print("- Search algorithms")

    print("- Constraint satisfaction")

    print("- Probabilistic reasoning")

    print("- Decision systems")

    print("- Hybrid AI architecture")

    print("- Explainable AI")

    print("- Performance optimization")


# ─────────────────────────────────────────────────────
# MAIN EXECUTION
# ─────────────────────────────────────────────────────

player = Player("Red")

dice = random.randint(1, 6)

print("Dice =", dice)

# Hybrid AI decision
selected_token = hybrid_ai_decision(player, dice)

if selected_token:

    print("\nHybrid AI Selected Token:",
          selected_token.tid)

    # Explainability
    explain_decision(selected_token, dice)

else:

    print("\nNo movable token")

# Performance Engineering
performance_test(player)

# Failure Analysis
failure_analysis(player, dice)

# Ethics / Limitations
ethics_and_limitations()

# Readiness for advanced AI
ai_course_readiness()