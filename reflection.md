# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
  - At a glance it looked completely normal — a title, a difficulty picker in the sidebar, a text box to enter a guess, and a "Developer Debug Info" expander to look at the actual secret. It was when I actually tried to play a full round that I started noticing major bugs with the game.
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").
  - The hints were backwards — guessing too high recommended to "go higher" instead of "go lower."
  - The guess prompt always said "between 1 and 100," even when I picked Easy or Hard, which have different ranges.
  - After I won a round, clicking "New Game" didn't actually start a new game — it just kept showing the "you already won" message.
  - Submitting a wrong guess didn't update the attempts count or history until I clicked Submit a second time.


**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| Secret is 50, guess is 60 (Normal difficulty) | Hint says "Too High — go lower" | Hint says "Go HIGHER!" even though the guess was too high | None — silently wrong message text |
| Difficulty set to "Easy" | Prompt reads "Guess a number between 1 and 20" | Prompt still reads "Guess a number between 1 and 100" | None |
| Win a round, then click "New Game" | A new secret is picked and I can guess again | Screen immediately shows "You already won. Start a new game to play again." and blocks further guesses | None — the game just silently calls `st.stop()` |
| Submit one wrong guess | Attempts count and guess history update right away | Attempts count and history stay the same until I click Submit again | None |

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
  - Claude Code
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
  - When I reported that "New Game" didn't actually restart the game, Claude traced the bug to `app.py`'s `if new_game:` block: it reset `attempts` and `secret`, but never reset `status`. Since `status` stayed `"won"`/`"lost"`, the status-check block right below it immediately called `st.stop()` again on the very next rerun, so the game looked stuck even after clicking New Game. Claude's fix reset `status`, `history`, and `score` too, and also generated the new secret from `random.randint(low, high)` instead of a hardcoded `random.randint(1, 100)` (which had ignored the selected difficulty). I verified this was correct by manually running the app, winning a game, clicking New Game, and confirming I could make a fresh guess instead of seeing the game-over message again. I later locked this in with an automated test, `test_new_game_resets_status_after_win` in `tests/test_game_logic.py`, which uses Streamlit's `AppTest` to simulate winning and clicking New Game, then asserts `status == "playing"` and `attempts`/`history` are reset.
- Give one example of an AI suggestion you did not accept as written (including what the AI suggested, why you rejected or changed it, and how you verified your version). It does not have to be a suggestion that was wrong: over-engineered, out of scope, harder to read, or a poor fit for this codebase all count.
  - While fixing the bug where incorrect guesses needed a second click to show up in "Attempts left" and the debug history, Claude's fix used `st.empty()` placeholders so the display would reflect state right after a guess was processed. As part of that change, it split the original single `st.info("Guess a number between X and Y. Attempts left: N")` message into two separate pieces: a static `st.info()` for the range and a separate `st.caption()` for the attempts-left count. The staleness fix itself was correct, but I didn't ask for the message to be split into two lines, and I preferred the original single combined message. I asked Claude to merge it back into one `st.info(...)` box while keeping the placeholder fix. I verified this by rerunning the app and confirming a single info box now shows both the range and an up-to-date "Attempts left" count immediately after submitting a guess, with no stale text and no extra second line.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
  - I found each bug myself while actually using the app (for example: clicking New Game after winning and finding I couldn't play again). I traced the bug to wide potential root cause area, and then described the bug behavior to Claude. Claude was able to help pinpoint the exact root cause in the code and compose a fix. After each fix, I went back and reproduced the same scenario in the app again to confirm the bug no longer happened, rather than just trusting that the code change looked right. For the trickier state bugs, I also added an automated test afterward so the fix couldn't silently regress later.
- Describe at least one test you ran (manual or using pytest) and what it showed you about your code.
  - I ran `pytest tests -q` and initially got `ModuleNotFoundError: No module named 'logic_utils'`, even though `logic_utils.py` was sitting right there in the project root. I traced this with Claude's help: pytest's default import mode only adds the first parent directory *without* an `__init__.py` to `sys.path`, and since `tests/` has no `__init__.py`, pytest was adding `tests/` instead of the project root. Adding an empty `conftest.py` at the project root fixed it, because pytest always puts a conftest file's own directory on `sys.path`. Re-running `.venv/bin/pytest tests -q` afterward showed all 12 tests passing, which told me both the import issue and the underlying bug fixes (hint wording, difficulty range, New Game restart, difficulty-change secret regeneration) were actually working, not just "looked right" in the browser.
- Did AI help you design or understand any tests? How?
  - Yes. Claude introduced me to Streamlit's `streamlit.testing.v1.AppTest`, which can script the app end to end (set a text input, click a button, read `session_state`) without a real browser. It used this to write tests like `test_new_game_resets_status_after_win`, `test_changing_difficulty_regenerates_secret_in_range`, and `test_debug_info_persists_after_win_and_further_interaction`, each one directly simulating the exact click sequence that used to trigger the bug. It also explained the `sys.path`/`conftest.py` mechanics behind the `ModuleNotFoundError` instead of just handing me a fix, which is why I could describe the root cause above instead of just saying "it works now."

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
  - I'd tell them Streamlit doesn't work like a normal app where only the part you clicked updates. Every time you interact with anything — click a button, type in a box, check a checkbox — Streamlit throws away the screen and runs your whole script again from top to bottom. That's the "rerun." Normally that would mean losing all your data every single time (like the secret number resetting on every guess), which is exactly the bug I kept running into. `session_state` is the fix: it's just a dictionary that survives across reruns, so you can stash things like the secret number, the score, or how many attempts you've used, and they'll still be there the next time the script runs. The tricky part I learned the hard way is that *where* in the script you read from `session_state` matters — if you display something before you've updated it in that same run, you'll see last run's value instead of the current one.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
  - Thoroughly describing a bug's behavior and the expected behavior after the fix before letting the AI assistant plan or make any changes. Giving it the exact input, what I expected, and what actually happened let it pinpoint the real root cause instead of guessing, and I didn't have to re-explain myself halfway through a fix. It also kept the AI on track and less likely to wander off and change things I hadn't asked for. I want to continue this habit going forward.
- What is one thing you would do differently next time you work with AI on a coding task?
  - I'd push back sooner when a fix changes more than what I asked for. A couple of times the AI's fix was technically correct but also quietly changed something else (like how a message was displayed), and I didn't catch it until later. Next time, I'll review diffs more carefully right when they're made instead of after the fact.
- In one or two sentences, describe how this project changed the way you think about AI generated code.
  - I came in assuming AI-written code either works or throws an obvious error, but most of these bugs were silent logic mistakes that looked totally fine until I actually played the game. Now I think of AI output as a first draft that needs to be run and poked at, not something to trust just because it looks reasonable.
