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

- [x] Describe the game's purpose.
  - Game Glitch Investigator is a Streamlit number-guessing game: the player picks a difficulty, repeatedly guesses a secret number within that difficulty's range, and gets "Too High"/"Too Low" hints and a running score until they either guess correctly or run out of attempts.
- [x] Detail which bugs you found.
   - Game stuck after attempting to start a new game.
   - On guess higher than actual, the app says keep going higher
   - Changing difficulty updated the displayed range but never regenerated the secret, so it could fall outside the new valid range.
   - The guess prompt always said "between 1 and 100" even on Easy/Hard difficulties, where the real range is different.
   - Incorrect guesses required clicking Submit twice before the attempts count and history reflected the update.
   - `pytest` failed with `ModuleNotFoundError: No module named 'logic_utils'` because the project had no root-level `conftest.py`.
- [x] Explain what fixes you applied.
  - Moved `check_guess`, `parse_guess`, `update_score`, and `get_range_for_difficulty` out of `app.py` and into `logic_utils.py`.
  - Corrected the backwards hint wording in `check_guess` (too high now says go lower, too low now says go higher).
  - Replaced the hardcoded "1 and 100" guess prompt with the actual `low`/`high` for the selected difficulty.
  - Made "New Game" reset `status`, `history`, and `score` (not just `attempts`/`secret`), and generate the new secret from the difficulty's `low`/`high` range, so the game can actually restart.
  - Added a difficulty-change check that regenerates the secret and resets game state whenever the difficulty selector changes.
  - Added a root-level `conftest.py` so `pytest` can resolve `logic_utils` regardless of how it's invoked.
  - Added regression tests in `tests/test_game_logic.py` covering each of the fixes above.

## 📸 Demo Walkthrough

Describe your fixed game in numbered steps so a reader can follow along without watching a video:

1. Difficulty is set to "Normal" (range 1-100, 8 attempts allowed). The secret number is 57, visible in the Developer Debug Info panel.
2. User enters a guess of `50`. The game correctly responds "Too Low — 📈 Go HIGHER!" (attempt 1).
3. User enters a guess of `75`. The game correctly responds "Too High — 📉 Go LOWER!" (attempt 2).
4. User enters a guess of `65`. Still too high — "📉 Go LOWER!" (attempt 3).
5. User enters a guess of `55`. Now too low — "📈 Go HIGHER!" (attempt 4).
6. User enters a guess of `57` - a match. The game announces "You won! The secret was 57. Final score: 30" and shows the balloons animation (attempt 5 of 8 used).
7. The "Attempts left" counter and Developer Debug Info panel update immediately after each guess, with no need to click Submit twice.
8. User clicks "New Game." The secret, attempts, score, and history all reset and a new round starts right away; the game no longer gets stuck on the "Game over" screen.

**Screenshot** *(optional)*: <!-- Insert a screenshot of your fixed, winning game here -->

## 🧪 Test Results

```
ai110-module1show-gameglitchinvestigator-starter % pytest
=============================================================================== test session starts ===============================================================================
platform darwin -- Python 3.13.15, pytest-9.1.1, pluggy-1.6.0
rootdir: ***/CodePath-Coding-Workspace/ai110-module1show-gameglitchinvestigator-starter
plugins: anyio-4.15.1
collected 12 items                                                                                                                                                                

tests/test_game_logic.py ............                                                                                                                                       [100%]

=============================================================================== 12 passed in 0.72s ================================================================================
```

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]
