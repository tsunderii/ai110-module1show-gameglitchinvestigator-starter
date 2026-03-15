import json
import os
import random
import streamlit as st

# FEATURE: High Score tracker and Guess History visualizer
# Agent planned and implemented both features in one pass:
#   - load_high_scores / save_high_score persist best scores per difficulty to highscores.json
#   - Guess History sidebar renders a bar chart showing how far each guess was from the secret

HIGH_SCORES_FILE = "highscores.json"

def load_high_scores():
    """Load high scores from disk. Returns a dict keyed by difficulty."""
    if os.path.exists(HIGH_SCORES_FILE):
        with open(HIGH_SCORES_FILE, "r") as f:
            return json.load(f)
    return {}

def save_high_score(difficulty: str, score: int):
    """Save score if it beats the existing high score for this difficulty."""
    scores = load_high_scores()
    if score > scores.get(difficulty, 0):
        scores[difficulty] = score
        with open(HIGH_SCORES_FILE, "w") as f:
            json.dump(scores, f)

def get_range_for_difficulty(difficulty: str):
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    # FIX: Hard was 1-50 (easier than Normal). AI identified the range was backwards;
    # collaborated to change it to 1-200 so Hard is genuinely harder than Normal.
    if difficulty == "Hard":
        return 1, 200
    return 1, 100


def parse_guess(raw: str):
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    if guess == secret:
        return "Win", "🎉 Correct!"

    # FIX: Hints were swapped — "Too High" said "Go HIGHER" and vice versa.
    # AI traced the mismatch between outcome label and hint text; swapped both
    # branches here and in the TypeError fallback below.
    try:
        if guess > secret:
            return "Too High", "📉 Go LOWER!"
        else:
            return "Too Low", "📈 Go HIGHER!"
    except TypeError:
        g = str(guess)
        if g == secret:
            return "Win", "🎉 Correct!"
        if g > secret:
            return "Too High", "📉 Go LOWER!"
        return "Too Low", "📈 Go HIGHER!"

def update_score(current_score: int, outcome: str, attempt_number: int):
    if outcome == "Win":
        # FIX: Formula had `attempt_number + 1`, making first-try give 70 instead of 90.
        # AI traced attempt_number=1 on first guess through the old formula to find the off-by-one;
        # removed the +1 so first try correctly awards 90 points.
        points = 100 - 10 * attempt_number
        if points < 10:
            points = 10
        return current_score + points

    # FIX: "Too High" on even attempts added +5 instead of subtracting.
    # AI spotted the stray `attempt_number % 2 == 0` branch that rewarded wrong guesses;
    # removed it so both wrong outcomes always subtract 5.
    if outcome == "Too High":
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

# FEATURE: Show high scores per difficulty in the sidebar
# Agent added this block to display persisted best scores next to the settings.
st.sidebar.divider()
st.sidebar.header("🏆 High Scores")
high_scores = load_high_scores()
for diff in ["Easy", "Normal", "Hard"]:
    best = high_scores.get(diff, 0)
    st.sidebar.caption(f"{diff}: {best}")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

# FIX: attempts was initialised to 1, causing the first guess to pass attempt_number=2.
# AI caught this while tracing the score bug; changed to 0 so the first valid guess gives attempt_number=1.
if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

st.subheader("Make a guess")

# FIX: Info text hardcoded "between 1 and 100" regardless of difficulty.
# AI noticed the f-string used a literal instead of the low/high variables; updated to use them.
st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

# FIX: New game button used hardcoded randint(1,100) and didn't reset score, status, or history.
# AI identified all missing resets and replaced the hardcoded range with randint(low, high).
if new_game:
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(low, high)
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append(raw_guess)
        st.error(err)
    else:
        # FIX: attempts incremented before parse_guess, so invalid input wasted an attempt.
        # AI moved the increment inside the else branch so only valid guesses count.
        st.session_state.attempts += 1
        st.session_state.history.append(guess_int)
        # FIX: secret was cast to str on even attempts, causing wrong lexicographic comparisons.
        # AI traced the alternating int/str type bug and removed the conversion so secret is always an integer.
        secret = st.session_state.secret

        outcome, message = check_guess(guess_int, secret)

        if show_hint:
            st.warning(message)

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            # FEATURE: Save high score on win; agent added this call so every win
            # is compared against the persisted best for this difficulty.
            save_high_score(difficulty, st.session_state.score)
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

# FEATURE: Guess History visualizer
# Agent designed this section to render a bar chart in the sidebar showing
# how far each valid guess was from the secret, so the player can see their
# progression at a glance. Only shown once at least one valid guess exists.
valid_guesses = [g for g in st.session_state.history if isinstance(g, int)]
if valid_guesses:
    st.divider()
    st.subheader("📊 Guess History")
    secret = st.session_state.secret
    data = {
        "Guess": valid_guesses,
        "Distance from secret": [abs(g - secret) for g in valid_guesses],
    }
    st.bar_chart(data, x="Guess", y="Distance from secret")
    st.caption("Lower bar = closer to the secret number.")

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
