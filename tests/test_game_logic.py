import os

from streamlit.testing.v1 import AppTest

from logic_utils import check_guess, get_range_for_difficulty

APP_PATH = os.path.join(os.path.dirname(__file__), "..", "app.py")


def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result[0] == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result[0] == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result[0] == "Too Low"


# --- Bug: hint wording was backwards (a guess above the secret told the
# player to go higher, and vice versa). ---------------------------------------

def test_guess_too_high_says_go_lower():
    _, message = check_guess(60, 50)
    assert "LOWER" in message.upper()


def test_guess_too_low_says_go_higher():
    _, message = check_guess(40, 50)
    assert "HIGHER" in message.upper()


# --- Bug: the on-screen range was hardcoded to 1-100 regardless of
# difficulty. -----------------------------------------------------------------

def test_range_for_easy():
    assert get_range_for_difficulty("Easy") == (1, 20)


def test_range_for_normal():
    assert get_range_for_difficulty("Normal") == (1, 100)


def test_range_for_hard():
    assert get_range_for_difficulty("Hard") == (1, 50)


# --- Bug: clicking "New Game" reset attempts/secret but not `status`, so a
# won or lost game immediately re-triggered the game-over screen and never
# actually restarted. ----------------------------------------------------------

def test_new_game_resets_status_after_win():
    at = AppTest.from_file(APP_PATH)
    at.run()

    secret = at.session_state["secret"]
    at.text_input[0].set_value(str(secret)).run()
    at.button[0].click().run()  # Submit Guess
    assert at.session_state["status"] == "won"

    at.button[1].click().run()  # New Game
    assert at.session_state["status"] == "playing"
    assert at.session_state["attempts"] == 0
    assert at.session_state["history"] == []


# --- Bug: switching difficulty updated the displayed range but never
# regenerated the secret, so it could fall outside the new valid range. -------

def test_changing_difficulty_regenerates_secret_in_range():
    at = AppTest.from_file(APP_PATH)
    at.run()

    at.selectbox[0].set_value("Easy").run()

    low, high = get_range_for_difficulty("Easy")
    assert low <= at.session_state["secret"] <= high


# --- Bug: the "Attempts left" info and debug panel were rendered before the
# guess was processed, so they showed stale state until the next rerun. ------

def test_attempt_and_history_update_on_first_click():
    at = AppTest.from_file(APP_PATH)
    at.run()

    secret = at.session_state["secret"]
    wrong_guess = secret + 1 if secret < 100 else secret - 1

    at.text_input[0].set_value(str(wrong_guess)).run()
    at.button[0].click().run()  # Submit Guess

    assert at.session_state["attempts"] == 1
    assert wrong_guess in at.session_state["history"]
    assert "Attempts left: 7" in at.info[0].value


# --- Bug: once the game was won/lost, `st.stop()` fired before the debug
# panel was ever rendered, so any further interaction (e.g. toggling "Show
# hint") made it vanish. -------------------------------------------------------

def test_debug_info_persists_after_win_and_further_interaction():
    at = AppTest.from_file(APP_PATH)
    at.run()

    secret = at.session_state["secret"]
    at.text_input[0].set_value(str(secret)).run()
    at.button[0].click().run()  # Submit Guess -> win
    assert at.session_state["status"] == "won"
    assert [e.label for e in at.expander] == ["Developer Debug Info"]

    at.checkbox[0].set_value(False).run()  # toggle "Show hint"
    assert [e.label for e in at.expander] == ["Developer Debug Info"]
