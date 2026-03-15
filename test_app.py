# test_app.py
# Tests for the bug fixes made in app.py.
# Now imports directly from logic_utils.py since all pure functions were
# refactored there. No more function copying needed.

from logic_utils import (
    check_guess,
    get_range_for_difficulty,
    parse_guess,
    update_score,
)


# ── Bug 1: check_guess hints were swapped ──────────────────────────────────
# Before fix: "Too High" showed "Go HIGHER" and "Too Low" showed "Go LOWER"

def test_check_guess_too_high_shows_go_lower():
    """Guess above secret → Too High with Go LOWER hint."""
    outcome, message = check_guess(80, 50)
    assert outcome == "Too High"
    assert "LOWER" in message


def test_check_guess_too_low_shows_go_higher():
    """Guess below secret → Too Low with Go HIGHER hint."""
    outcome, message = check_guess(20, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message


def test_check_guess_correct():
    """Exact match → Win."""
    outcome, _ = check_guess(42, 42)
    assert outcome == "Win"


# ── Bug 2: update_score formula had +1, first-try gave 70 instead of 90 ───
# Before fix: points = 100 - 10 * (attempt_number + 1)
# Also: Too High on even attempts added +5 instead of subtracting

def test_update_score_first_try_win():
    """Winning on attempt 1 awards 90 points (100 - 10*1)."""
    assert update_score(0, "Win", 1) == 90


def test_update_score_second_try_win():
    """Winning on attempt 2 awards 80 points (100 - 10*2)."""
    assert update_score(0, "Win", 2) == 80


def test_update_score_win_minimum_is_10():
    """Points floor at 10 even on very late attempts."""
    assert update_score(0, "Win", 15) == 10


def test_update_score_too_high_always_subtracts():
    """Too High always subtracts 5 — never adds (even attempt)."""
    assert update_score(50, "Too High", 2) == 45


def test_update_score_too_high_odd_attempt_also_subtracts():
    """Too High on an odd attempt also subtracts 5."""
    assert update_score(50, "Too High", 3) == 45


def test_update_score_too_low_subtracts():
    """Too Low always subtracts 5."""
    assert update_score(50, "Too Low", 3) == 45


# ── Bug 3: Hard difficulty range was 1-50 (easier than Normal's 1-100) ────

def test_hard_range_larger_than_normal():
    """Hard range must be larger (harder) than Normal."""
    _, normal_high = get_range_for_difficulty("Normal")
    _, hard_high = get_range_for_difficulty("Hard")
    assert hard_high > normal_high


def test_difficulty_ranges():
    assert get_range_for_difficulty("Easy") == (1, 20)
    assert get_range_for_difficulty("Normal") == (1, 100)
    assert get_range_for_difficulty("Hard") == (1, 200)


# ── parse_guess: input validation ─────────────────────────────────────────

def test_parse_guess_valid_integer():
    ok, value, err = parse_guess("42")
    assert ok is True and value == 42 and err is None


def test_parse_guess_decimal_truncates():
    ok, value, _ = parse_guess("3.7")
    assert ok is True and value == 3


def test_parse_guess_empty_string():
    ok, value, _ = parse_guess("")
    assert ok is False and value is None


def test_parse_guess_none():
    ok, _, _ = parse_guess(None)
    assert ok is False


def test_parse_guess_non_numeric():
    ok, _, err = parse_guess("abc")
    assert ok is False and "not a number" in err.lower()
