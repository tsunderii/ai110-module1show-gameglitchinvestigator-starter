# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

### Game Purpose

Glitchy Guesser is a number guessing game built with Streamlit. The player picks a difficulty (Easy: 1–20, Normal: 1–100, Hard: 1–200), then repeatedly guesses a secret number within a limited number of attempts. After each guess the game gives a hint (Too High / Too Low) and adjusts the score. Winning earlier earns more points; wrong guesses cost 5 points each.

### Bugs Found

| # | Location | Bug |
|---|----------|-----|
| 1 | `check_guess` | Hints were swapped — "Too High" said "Go HIGHER" and "Too Low" said "Go LOWER" |
| 2 | `update_score` | Win formula used `attempt_number + 1`, so a first-try win gave 70 points instead of 90 |
| 3 | `update_score` | "Too High" on even attempts added +5 points instead of subtracting |
| 4 | `get_range_for_difficulty` | Hard difficulty had range 1–50, which is easier than Normal's 1–100 |
| 5 | `app.py` (UI) | New game button hardcoded `randint(1, 100)` and didn't reset `score`, `status`, or `history` |
| 6 | `app.py` (UI) | Info text always showed "between 1 and 100" regardless of difficulty |
| 7 | `app.py` (UI) | Attempt counter incremented on invalid input, wasting an attempt for non-numeric guesses |
| 8 | `app.py` (UI) | Secret was converted to a string on even attempts, causing wrong lexicographic comparisons |

### Fixes Applied

1. **Swapped hints** — swapped the hint messages in `check_guess` so Too High → "Go LOWER" and Too Low → "Go HIGHER". Same fix applied to the `TypeError` fallback branch.
2. **Win score formula** — removed `+ 1` from `100 - 10 * (attempt_number + 1)` → `100 - 10 * attempt_number`. Also changed `attempts` to start at `0` so the first guess correctly passes `attempt_number = 1`.
3. **Too High always subtracts** — removed the `attempt_number % 2 == 0` branch that sometimes awarded +5 for a wrong guess.
4. **Hard difficulty range** — changed Hard from `1–50` to `1–200` so it is genuinely harder than Normal.
5. **New game button** — replaced hardcoded `randint(1, 100)` with `randint(low, high)` and added resets for `score`, `status`, and `history`.
6. **Dynamic info text** — replaced the hardcoded `"between 1 and 100"` string with `f"between {low} and {high}"`.
7. **Attempt counter on invalid input** — moved `st.session_state.attempts += 1` inside the `else` branch so it only increments on valid guesses.
8. **Secret type alternating** — removed the even/odd `str()` conversion; `secret` is always used as an integer.

### Pytest Results

All 16 tests pass after the fixes were applied. Run them yourself with:

```
python -m pytest test_app.py -v
```

Expected output:

```
============================= test session starts ==============================
platform darwin -- Python 3.13.12, pytest-9.0.2, pluggy-1.6.0
collected 16 items

test_app.py::test_check_guess_too_high_shows_go_lower PASSED             [  6%]
test_app.py::test_check_guess_too_low_shows_go_higher PASSED             [ 12%]
test_app.py::test_check_guess_correct PASSED                             [ 18%]
test_app.py::test_update_score_first_try_win PASSED                      [ 25%]
test_app.py::test_update_score_second_try_win PASSED                     [ 31%]
test_app.py::test_update_score_win_minimum_is_10 PASSED                  [ 37%]
test_app.py::test_update_score_too_high_always_subtracts PASSED          [ 43%]
test_app.py::test_update_score_too_high_odd_attempt_also_subtracts PASSED [ 50%]
test_app.py::test_update_score_too_low_subtracts PASSED                  [ 56%]
test_app.py::test_hard_range_larger_than_normal PASSED                   [ 62%]
test_app.py::test_difficulty_ranges PASSED                               [ 68%]
test_app.py::test_parse_guess_valid_integer PASSED                       [ 75%]
test_app.py::test_parse_guess_decimal_truncates PASSED                   [ 81%]
test_app.py::test_parse_guess_empty_string PASSED                        [ 87%]
test_app.py::test_parse_guess_none PASSED                                [ 93%]
test_app.py::test_parse_guess_non_numeric PASSED                         [100%]

============================== 16 passed in 0.01s ==============================
```

### How AI Helped Orchestrate the Changes

The AI assistant (Claude Code) was used throughout this investigation to identify, explain, and fix bugs across multiple files. Here is how it helped at each stage:

1. **Reading and understanding the code** — Claude read `app.py` in full and explained each function before suggesting any changes. It did not modify code it had not read first.

2. **Identifying bugs by reasoning about logic** — For each bug, Claude traced the data flow (e.g. following `attempt_number` from its initial value of `1` through the `+1` in the formula to explain why first-try gave `70`) rather than just guessing at fixes.

3. **Applying targeted edits across files** — Fixes spanned three files: `app.py` (logic functions and UI state), `README.md` (documentation), and the newly created `test_app.py`. Claude applied each change as a precise string replacement, leaving surrounding code untouched.

4. **Writing and running tests** — Claude created `test_app.py` with 16 tests grouped by bug, then ran `pytest` to confirm all passed. Because `app.py` cannot be imported outside Streamlit, Claude recognized this constraint and copied the pure functions into the test file — a standard workaround for Streamlit apps.

5. **Updating documentation** — After all fixes were verified, Claude updated this README to record the game's purpose, the full bug list, the fixes applied, and the test results, so the work is traceable.


