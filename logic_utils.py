"""
logic_utils.py
--------------
Pure game-logic helpers for Glitchy Guesser.

All functions in this module are side-effect-free (except the persistence
helpers) and have no dependency on Streamlit, making them straightforward to
unit-test in isolation.

Agent contribution: Claude Code extracted these functions from app.py, added
PEP 257-compliant docstrings with Args/Returns/Examples sections, applied PEP 8
formatting throughout, and added full type annotations for static analysis.
"""

import json
import os


HIGH_SCORES_FILE = "highscores.json"


# ---------------------------------------------------------------------------
# Difficulty helpers
# ---------------------------------------------------------------------------

def get_range_for_difficulty(difficulty: str) -> tuple[int, int]:
    """Return the (low, high) guess range for the given difficulty level.

    Args:
        difficulty: One of ``"Easy"``, ``"Normal"``, or ``"Hard"``.

    Returns:
        A tuple ``(low, high)`` representing the inclusive guess range.
        Defaults to ``(1, 100)`` for unrecognised difficulty strings.

    Examples:
        >>> get_range_for_difficulty("Easy")
        (1, 20)
        >>> get_range_for_difficulty("Hard")
        (1, 200)
    """
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        # FIX: Hard was 1-50 (easier than Normal). AI identified the range was
        # backwards; changed to 1-200 so Hard is genuinely harder than Normal.
        return 1, 200
    return 1, 100


# ---------------------------------------------------------------------------
# Input parsing
# ---------------------------------------------------------------------------

def parse_guess(raw: str) -> tuple[bool, int | None, str | None]:
    """Parse and validate a raw text guess from the user.

    Accepts whole numbers and decimal strings (the decimal portion is
    truncated, e.g. ``"3.7"`` becomes ``3``).

    Args:
        raw: The raw string typed by the user. May be ``None`` or empty.

    Returns:
        A 3-tuple ``(ok, value, error)``:

        - ``ok`` (bool): ``True`` if parsing succeeded.
        - ``value`` (int | None): The parsed integer, or ``None`` on failure.
        - ``error`` (str | None): A human-readable error message, or ``None``
          on success.

    Examples:
        >>> parse_guess("42")
        (True, 42, None)
        >>> parse_guess("abc")
        (False, None, 'That is not a number.')
    """
    if raw is None or raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


# ---------------------------------------------------------------------------
# Guess evaluation
# ---------------------------------------------------------------------------

def check_guess(guess: int, secret: int) -> tuple[str, str]:
    """Compare a player's guess against the secret number.

    Args:
        guess: The player's integer guess.
        secret: The secret integer the player is trying to find.

    Returns:
        A 2-tuple ``(outcome, message)``:

        - ``outcome``: One of ``"Win"``, ``"Too High"``, or ``"Too Low"``.
        - ``message``: A short emoji-decorated hint string for the player.

    Examples:
        >>> check_guess(50, 50)
        ('Win', '🎉 Correct!')
        >>> check_guess(80, 50)
        ('Too High', '📉 Go LOWER!')
        >>> check_guess(20, 50)
        ('Too Low', '📈 Go HIGHER!')
    """
    if guess == secret:
        return "Win", "🎉 Correct!"

    # FIX: Hints were swapped — "Too High" said "Go HIGHER" and vice versa.
    # AI traced the mismatch between outcome label and hint text; swapped both
    # branches here and in the TypeError fallback below.
    try:
        if guess > secret:
            return "Too High", "📉 Go LOWER!"
        return "Too Low", "📈 Go HIGHER!"
    except TypeError:
        g = str(guess)
        if g == secret:
            return "Win", "🎉 Correct!"
        if g > secret:
            return "Too High", "📉 Go LOWER!"
        return "Too Low", "📈 Go HIGHER!"


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def update_score(current_score: int, outcome: str, attempt_number: int) -> int:
    """Calculate the new score after a guess outcome.

    Win points decrease with each attempt (minimum 10). Wrong guesses each
    deduct 5 points regardless of attempt number.

    Args:
        current_score: The player's score before this guess.
        outcome: One of ``"Win"``, ``"Too High"``, or ``"Too Low"``.
        attempt_number: The 1-based index of the current attempt.

    Returns:
        The updated integer score.

    Examples:
        >>> update_score(0, "Win", 1)
        90
        >>> update_score(50, "Too High", 2)
        45
        >>> update_score(50, "Too Low", 3)
        45
    """
    if outcome == "Win":
        # FIX: Formula had `attempt_number + 1`, making first-try give 70
        # instead of 90. AI traced the off-by-one and removed the +1.
        points = 100 - 10 * attempt_number
        if points < 10:
            points = 10
        return current_score + points

    # FIX: "Too High" on even attempts used to add +5 instead of subtracting.
    # AI removed the stray % 2 branch; both wrong outcomes now always subtract 5.
    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    return current_score


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def load_high_scores() -> dict[str, int]:
    """Load the persisted high-score table from disk.

    Reads ``highscores.json`` from the current working directory. Returns an
    empty dict if the file does not exist yet.

    Returns:
        A dict mapping difficulty name (str) to best score (int).

    Examples:
        >>> scores = load_high_scores()
        >>> isinstance(scores, dict)
        True
    """
    if os.path.exists(HIGH_SCORES_FILE):
        with open(HIGH_SCORES_FILE, "r") as f:
            return json.load(f)
    return {}


def save_high_score(difficulty: str, score: int) -> None:
    """Persist a score if it beats the current high score for the difficulty.

    Reads the existing table, updates the entry for *difficulty* only when
    *score* is strictly greater than the stored value, then writes back to disk.

    Args:
        difficulty: The difficulty level string (e.g. ``"Normal"``).
        score: The score achieved at the end of the game.

    Returns:
        None

    Examples:
        >>> save_high_score("Easy", 90)  # saves if 90 > current best
    """
    scores = load_high_scores()
    if score > scores.get(difficulty, 0):
        scores[difficulty] = score
        with open(HIGH_SCORES_FILE, "w") as f:
            json.dump(scores, f)
