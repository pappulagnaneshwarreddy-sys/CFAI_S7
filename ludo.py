"""
╔══════════════════════════════════════════════════════╗
║               LUDO GAME — ADVANCED VERSION           ║
║   Features: AI Player, Difficulty, Stats, Rules      ║
╚══════════════════════════════════════════════════════╝
"""

import random
import time
import json
import os
from copy import deepcopy

# ─────────────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────────────

NUM_TOKENS      = 4
TRACK_LENGTH    = 52
HOME_COL_LEN    = 6
HOME_VALUE      = TRACK_LENGTH + HOME_COL_LEN   # 58  = reached home

SAFE_SQUARES    = {0, 8, 13, 21, 26, 34, 39, 47}

COLOR_START = {'Red': 0, 'Blue': 13, 'Green': 26, 'Yellow': 39}

# ANSI color codes (work in PyCharm terminal)
ANSI = {
    'Red'    : '\033[91m',
    'Blue'   : '\033[94m',
    'Green'  : '\033[92m',
    'Yellow' : '\033[93m',
    'Reset'  : '\033[0m',
    'Bold'   : '\033[1m',
    'Cyan'   : '\033[96m',
    'White'  : '\033[97m',
    'Gray'   : '\033[90m',
}

SYMBOLS = {'Red': 'R', 'Blue': 'B', 'Green': 'G', 'Yellow': 'Y'}

SAVE_FILE = "ludo_save.json"

# ─────────────────────────────────────────────────────
#  HELPER: colored text
# ─────────────────────────────────────────────────────

def col(text, color):
    """Wrap text in ANSI color for terminal output."""
    return f"{ANSI.get(color, '')}{text}{ANSI['Reset']}"

def bold(text):
    return f"{ANSI['Bold']}{text}{ANSI['Reset']}"

# ─────────────────────────────────────────────────────
#  TOKEN
# ─────────────────────────────────────────────────────

class Token:
    """
    Represents one token on the board.
    pos = -1      → in base (not yet entered)
    pos = 0..51   → on main track (relative to owner's start)
    pos = 52..57  → in home column (steps 1-6)
    pos = 58      → HOME (finished)
    """

    def __init__(self, color, tid):
        self.color = color
        self.tid   = tid      # 1-4
        self.pos   = -1

    # ── state properties ──────────────────────────────
    @property
    def in_base(self):     return self.pos == -1
    @property
    def in_home(self):     return self.pos == HOME_VALUE
    @property
    def on_track(self):    return 0 <= self.pos < TRACK_LENGTH
    @property
    def in_home_col(self): return TRACK_LENGTH <= self.pos < HOME_VALUE

    def global_pos(self, start):
        """Absolute board square (0-51) for collision checking."""
        if self.on_track:
            return (start + self.pos) % TRACK_LENGTH
        return None

    def label(self):
        """Short colored label for display."""
        sym = f"{SYMBOLS[self.color]}{self.tid}"
        return col(sym, self.color)

    def status(self):
        """Human-readable position string."""
        if self.in_base:      return col("BASE", 'Gray')
        if self.in_home:      return col("HOME✓", 'Green')
        if self.in_home_col:  return col(f"HC-{self.pos - TRACK_LENGTH}", 'Cyan')
        return f"T{self.pos:02d}"

    def to_dict(self):
        return {'color': self.color, 'tid': self.tid, 'pos': self.pos}

    @classmethod
    def from_dict(cls, d):
        t = cls(d['color'], d['tid'])
        t.pos = d['pos']
        return t

    def __repr__(self):
        return f"{self.label()}[{self.status()}]"


# ─────────────────────────────────────────────────────
#  PLAYER
# ─────────────────────────────────────────────────────

class Player:
    """
    Holds 4 tokens and player metadata.
    is_human = True  → waits for keyboard input
    is_human = False → AI picks automatically
    difficulty       → 'easy' | 'medium' | 'hard'
    """

    def __init__(self, color, is_human=True, difficulty='hard'):
        self.color      = color
        self.is_human   = is_human
        self.difficulty = difficulty
        self.tokens     = [Token(color, i + 1) for i in range(NUM_TOKENS)]
        self.start      = COLOR_START[color]
        # ── statistics ──
        self.stat_captures   = 0
        self.stat_dice_rolls = 0
        self.stat_sixes      = 0
        self.stat_turns      = 0
        self.rolls_without_six = 0

    @property
    def all_home(self):
        return all(t.in_home for t in self.tokens)

    def movable_tokens(self, dice):
        """Return tokens that have a legal move for this dice value."""
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

    def colored_name(self):
        return col(bold(self.color), self.color)

    def to_dict(self):
        return {
            'color': self.color, 'is_human': self.is_human,
            'difficulty': self.difficulty,
            'tokens': [t.to_dict() for t in self.tokens],
            'stat_captures': self.stat_captures,
            'stat_dice_rolls': self.stat_dice_rolls,
            'stat_sixes': self.stat_sixes,
            'stat_turns': self.stat_turns,
        }

    @classmethod
    def from_dict(cls, d):
        p = cls(d['color'], d['is_human'], d['difficulty'])
        p.tokens         = [Token.from_dict(td) for td in d['tokens']]
        p.stat_captures  = d.get('stat_captures', 0)
        p.stat_dice_rolls= d.get('stat_dice_rolls', 0)
        p.stat_sixes     = d.get('stat_sixes', 0)
        p.stat_turns     = d.get('stat_turns', 0)
        return p


# ─────────────────────────────────────────────────────
#  BOARD LOGIC
# ─────────────────────────────────────────────────────

def tokens_at_global(players, gsq):
    """All (player, token) pairs occupying a given global track square."""
    result = []
    for p in players:
        for t in p.tokens:
            if t.on_track and t.global_pos(p.start) == gsq:
                result.append((p, t))
    return result


def is_blocked(players, gsq, color):
    """
    Block rule: two same-color tokens on same square = block.
    Enemy tokens cannot land there.
    """
    same = [t for p in players for t in p.tokens
            if p.color != color and t.on_track and t.global_pos(p.start) == gsq]
    # count how many same-color tokens from any one opponent are on gsq
    from collections import Counter
    cnt = Counter()
    for p in players:
        if p.color == color:
            continue
        for t in p.tokens:
            if t.on_track and t.global_pos(p.start) == gsq:
                cnt[p.color] += 1
    return any(v >= 2 for v in cnt.values())


def apply_move(player, token, dice, players, history):
    """
    Move token, handle captures, record history event.
    Returns list of captured (player, token) tuples.
    """
    captured = []

    if token.in_base and dice == 6:
        token.pos = 0
        history.append(f"{player.color} brought Token {token.tid} out of base")
    else:
        token.pos += dice
        history.append(f"{player.color} moved Token {token.tid} → pos {token.pos}")

    # capture check (only on main track, non-safe squares)
    if token.on_track:
        gsq = token.global_pos(player.start)
        if gsq not in SAFE_SQUARES and not is_blocked(players, gsq, player.color):
            for op, ot in tokens_at_global(players, gsq):
                if op.color != player.color:
                    ot.pos = -1
                    captured.append((op, ot))
                    op.stat_captures -= 1   # they lost a token (for reference)
                    history.append(
                        f"{player.color} CAPTURED {op.color}'s Token {ot.tid}!"
                    )

    if token.in_home:
        history.append(f"{player.color} Token {token.tid} reached HOME!")

    return captured


# ─────────────────────────────────────────────────────
#  AI — HEURISTIC SCORING
# ─────────────────────────────────────────────────────

def score_move(player, token, dice, players):
    """
    Evaluate a potential move and return a numeric score.
    Higher = better move.

    Scoring table:
      Reach HOME           +1000
      Enter home column    +200
      Capture opponent     +150  each
      Land on safe square  +80
      Progress on track    +2 × steps
      Exit base            +60
      Danger (enemy nearby)+(-40)
    """
    # simulate on a copy
    sim_players = deepcopy(players)
    sim_player  = next(p for p in sim_players if p.color == player.color)
    sim_token   = sim_player.tokens[token.tid - 1]

    dummy_history = []
    captured = apply_move(sim_player, sim_token, dice, sim_players, dummy_history)

    score = 0

    # 1. Reached home
    if sim_token.in_home:
        score += 1000

    # 2. Progress
    if not sim_token.in_base:
        score += sim_token.pos * 2

    # 3. Captures
    score += len(captured) * 150

    # 4. Safe square bonus
    if sim_token.on_track:
        gsq = sim_token.global_pos(sim_player.start)
        if gsq in SAFE_SQUARES:
            score += 80

    # 5. Exited base
    if token.in_base and dice == 6:
        score += 60

    # 6. In home column (near finish)
    if sim_token.in_home_col:
        score += 200

    # 7. Danger penalty — enemy within 1-6 steps behind
    if sim_token.on_track:
        gsq = sim_token.global_pos(sim_player.start)
        if gsq not in SAFE_SQUARES:
            for op in sim_players:
                if op.color == sim_player.color:
                    continue
                for ot in op.tokens:
                    if ot.on_track:
                        eg = ot.global_pos(op.start)
                        diff = (gsq - eg) % TRACK_LENGTH
                        if 1 <= diff <= 6:
                            score -= 40

    return score


def ai_choose_token(player, movable, dice, players, difficulty):
    """
    AI move selection based on difficulty level.

    Easy   → random choice
    Medium → prefer captures and safe squares (no deep look-ahead)
    Hard   → full heuristic scoring (score_move)
    """
    if difficulty == 'easy':
        return random.choice(movable)

    if difficulty == 'medium':
        # Quick priority: capture > safe > anything
        for t in movable:
            if t.on_track:
                new_gsq = (player.start + t.pos + dice) % TRACK_LENGTH
                if new_gsq not in SAFE_SQUARES:
                    occupied = tokens_at_global(players, new_gsq)
                    if any(p.color != player.color for p, _ in occupied):
                        return t  # capture!
        for t in movable:
            if t.on_track:
                new_pos = t.pos + dice
                if new_pos < TRACK_LENGTH:
                    new_gsq = (player.start + new_pos) % TRACK_LENGTH
                    if new_gsq in SAFE_SQUARES:
                        return t  # safe
        return random.choice(movable)

    # hard: full heuristic
    scores = [score_move(player, t, dice, players) for t in movable]
    best_idx = scores.index(max(scores))
    return movable[best_idx]


# ─────────────────────────────────────────────────────
#  BOARD DISPLAY
# ─────────────────────────────────────────────────────

def print_board(players):
    """
    ASCII board display showing all token positions.

    ┌─────────────────────────────────────────────────────┐
    │  RED     R1[T05]  R2[BASE]  R3[HOME✓] R4[HC-2]    │
    │  BLUE    B1[T18]  B2[T31]  B3[BASE]  B4[BASE]     │
    └─────────────────────────────────────────────────────┘
    """
    print()
    width = 60
    print(col("┌" + "─" * width + "┐", 'Gray'))

    for p in players:
        done  = sum(1 for t in p.tokens if t.in_home)
        bar   = "█" * done + "░" * (NUM_TOKENS - done)
        toks  = "  ".join(
            f"{t.label()}[{t.status()}]" for t in p.tokens
        )
        ptype = "Human" if p.is_human else f"AI({p.difficulty})"
        line  = f"  {col(f'{p.color:7s}', p.color)} [{bar}] {done}/4  {toks}  {col(ptype,'Gray')}"
        print(col("│", 'Gray') + line)

    print(col("└" + "─" * width + "┘", 'Gray'))


def print_history(history, last_n=5):
    """Print the last N moves from turn history."""
    print(col("\n  ── Recent Moves ──", 'Gray'))
    for entry in history[-last_n:]:
        print(col(f"   • {entry}", 'Gray'))


# ─────────────────────────────────────────────────────
#  GAME STATISTICS
# ─────────────────────────────────────────────────────

def print_statistics(players, total_turns):
    """Display end-of-game statistics table."""
    print()
    print(bold(col("╔══════ GAME STATISTICS ══════╗", 'Cyan')))
    print(col(f"  Total Turns Played : {total_turns}", 'White'))
    print(col("  ─────────────────────────────", 'Gray'))
    print(f"  {'Player':<10} {'Captures':>9} {'Dice Rolls':>11} {'Sixes':>6} {'Finished':>9}")
    print(col("  ─────────────────────────────────────────", 'Gray'))
    for p in players:
        fin = sum(1 for t in p.tokens if t.in_home)
        row = (f"  {p.color:<10} {p.stat_captures:>9} "
               f"{p.stat_dice_rolls:>11} {p.stat_sixes:>6} {fin:>9}/4")
        print(col(row, p.color))
    print(bold(col("╚═════════════════════════════╝", 'Cyan')))


# ─────────────────────────────────────────────────────
#  SAVE / LOAD
# ─────────────────────────────────────────────────────

def save_game(players, current_idx, history, total_turns):
    data = {
        'players'     : [p.to_dict() for p in players],
        'current_idx' : current_idx,
        'history'     : history,
        'total_turns' : total_turns,
    }
    with open(SAVE_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(col(f"  Game saved to {SAVE_FILE}", 'Green'))


def load_game():
    if not os.path.exists(SAVE_FILE):
        print(col("  No save file found.", 'Gray'))
        return None
    with open(SAVE_FILE, 'r') as f:
        data = json.load(f)
    players     = [Player.from_dict(d) for d in data['players']]
    current_idx = data['current_idx']
    history     = data['history']
    total_turns = data['total_turns']
    print(col(f"  Game loaded from {SAVE_FILE}", 'Green'))
    return players, current_idx, history, total_turns


# ─────────────────────────────────────────────────────
#  TURN LOGIC
# ─────────────────────────────────────────────────────

def do_turn(player, players, history):
    """
    Execute one full turn for a player.
    Handles:
      • Triple-six rule (3 consecutive sixes → turn cancelled)
      • Extra turn on 6
      • Human input / AI selection
    Returns True if player gets an extra turn.
    """
    consecutive_sixes = 0

    while True:
        # Guarantee a 6 within first 5 rolls if all tokens are still in base
        all_in_base = all(t.in_base for t in player.tokens)
        if all_in_base and player.rolls_without_six >= 4:
            dice = 6
        else:
            dice = random.randint(1, 6)

        player.stat_dice_rolls += 1
        player.stat_turns      += 1

        if dice == 6:
            consecutive_sixes += 1
            player.stat_sixes += 1
            player.rolls_without_six = 0
        else:
            consecutive_sixes = 0
            player.rolls_without_six += 1

        print(f"\n  {player.colored_name()} rolled → {bold(col(str(dice), 'Yellow'))}", end="")

        # ── Triple-six rule ──────────────────────────
        if consecutive_sixes == 3:
            print(col("  ⚠  Three 6s in a row! Turn cancelled.", 'Yellow'))
            history.append(f"{player.color} rolled three 6s — turn cancelled")
            return False

        movable = player.movable_tokens(dice)

        if not movable:
            print(col("   No valid moves.", 'Gray'))
            if dice != 6:
                return False
            # rolled 6 but nothing to do (all in base, can't enter for some reason)
            return False

        # ── Choose token ─────────────────────────────
        if player.is_human:
            token = human_choose(player, movable, dice)
        else:
            time.sleep(0.5)   # small pause so AI doesn't fly through
            token = ai_choose_token(player, movable, dice, players, player.difficulty)
            print(col(f"   AI selects Token {token.tid}", 'Cyan'))

        captured = apply_move(player, token, dice, players, history)
        player.stat_captures += len(captured)

        # ── Report result ─────────────────────────────
        print(f"   Token {token.tid} → {token.status()}", end="")
        for op, ot in captured:
            print(f"\n   {col('💥 CAPTURED', 'Red')} {op.colored_name()}'s Token {ot.tid}! Sent to base.")

        if token.in_home:
            print(col(f"\n   ✅ Token {token.tid} reached HOME!", 'Green'))

        # ── Extra turn on 6 ──────────────────────────
        if dice == 6:
            print(col("   🎲 Rolled 6! Extra turn.", 'Yellow'))
            # Stay in while loop for extra turn
            continue

        print()
        return False   # normal end of turn


def human_choose(player, movable, dice):
    """Prompt human to pick a token. Always shows all 4 tokens; highlights movable ones."""
    movable_ids = {t.tid for t in movable}
    print(col(f"\n   Your tokens (dice={dice}):", 'White'))
    for t in player.tokens:
        if t.tid in movable_ids:
            tag = col("  can move", 'Green')
        else:
            tag = col("  blocked", 'Gray')
        print(f"     [Token {t.tid}]  {t.status()}{tag}")
    while True:
        try:
            c = int(input(col("   Choose token (1-4): ", 'White')))
            chosen = next((t for t in movable if t.tid == c), None)
            if chosen:
                return chosen
            if 1 <= c <= 4:
                print(col("   That token cannot move. Pick a movable token.", 'Yellow'))
            else:
                print("   Enter a number between 1 and 4.")
        except ValueError:
            print("   Enter a number between 1 and 4.")


# ─────────────────────────────────────────────────────
#  MENU
# ─────────────────────────────────────────────────────

def show_menu():
    print()
    print(bold(col("╔══════════════════════════════╗", 'Cyan')))
    print(bold(col("║        L U D O  GAME         ║", 'Cyan')))
    print(bold(col("╚══════════════════════════════╝", 'Cyan')))
    print(col("  1. Human vs AI", 'White'))
    print(col("  2. Exit", 'White'))
    print()
    while True:
        choice = input(col("  Select option (1-2): ", 'Yellow')).strip()
        if choice in ('1', '2'):
            return choice
        print("  Enter 1 or 2.")


def choose_difficulty():
    print(col("\n  AI Difficulty:", 'White'))
    print("    1. Easy   (random moves)")
    print("    2. Medium (safe + captures)")
    print("    3. Hard   (full heuristic)")
    while True:
        d = input(col("  Choose difficulty (1-3): ", 'Yellow')).strip()
        if d == '1': return 'easy'
        if d == '2': return 'medium'
        if d == '3': return 'hard'
        print("  Enter 1, 2, or 3.")


def setup_players(option):
    """
    Return list of Player objects.
    Option 1: Human (Red) vs AI opponents.
    """
    colors = ['Red', 'Blue', 'Green', 'Yellow']
    players = []

    print(col("\n  Human vs AI selected.", 'White'))
    diff = choose_difficulty()
    while True:
        try:
            n = int(input(col("  How many AI opponents? (1-3): ", 'Yellow')))
            if 1 <= n <= 3:
                break
            print("  Enter 1-3.")
        except ValueError:
            pass
    players.append(Player('Red', is_human=True))
    for i in range(n):
        players.append(Player(colors[i + 1], is_human=False, difficulty=diff))

    return players


# ─────────────────────────────────────────────────────
#  MAIN GAME LOOP
# ─────────────────────────────────────────────────────

def play_game(players, start_idx=0, history=None, total_turns=0):
    if history is None:
        history = []

    print()
    print(col("  Players in this game:", 'White'))
    for p in players:
        ptype = "Human" if p.is_human else f"AI [{p.difficulty}]"
        print(f"   {p.colored_name()} — {ptype}")

    current = start_idx
    winner  = None
    ranking = []   # players in finish order

    while not winner:
        player = players[current]
        print_board(players)
        if history:
            print_history(history)

        if player.is_human:
            input(col(f"\n  {player.colored_name()} — Press Enter to roll: ", 'White'))

        do_turn(player, players, history)
        total_turns += 1

        # Check if this player just finished
        if player.all_home and player not in ranking:
            ranking.append(player)
            print(col(f"\n  🏅 {player.colored_name()} finished in position #{len(ranking)}!", 'Yellow'))
            if len(ranking) == 1:
                winner = player   # first to finish wins

        if not do_turn.__doc__:  # always advance
            pass

        current = (current + 1) % len(players)

    # ── Game over ────────────────────────────────────
    print_board(players)
    print()
    print(bold(col("★" * 44, 'Yellow')))
    print(bold(col(f"   🏆  {winner.color} WINS THE GAME!  🏆", 'Yellow')))
    print(bold(col("★" * 44, 'Yellow')))
    print_statistics(players, total_turns)


# ─────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────

def main():
    while True:
        option = show_menu()

        if option == '2':
            print(col("\n  Goodbye! Thanks for playing Ludo.\n", 'Cyan'))
            break

        players = setup_players(option)
        play_game(players)

        again = input(col("\n  Play again? (y/n): ", 'Yellow')).strip().lower()
        if again != 'y':
            print(col("\n  Thanks for playing!\n", 'Cyan'))
            break


if __name__ == "__main__":
    main()