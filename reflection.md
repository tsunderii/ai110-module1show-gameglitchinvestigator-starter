# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the secret number kept changing" or "the hints were backwards").

When I first started, I noticed immediately that the hints were inaccurate and giving the opposite outcome. For example, when I guessed 3, it kept telling me to guess lower until I guessed until 0, andit kept telling me to go lower when I expected it to tell me to go higher because the guessing range did not include negative numbers. Another bug that I noticed was that the new game button didn't work after finishing a game. When I guessed the number correctly and clicked the button to start a new game, I was unable to start a new game and it instead continued the previous game unless I reloaded the page entirely.
---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

One misleading AI suggestion was that the code was “production-ready,” even though the guessing hints are wrong.The AI tool I used was Claude to explain a reason for why I was getting an error in a specific section that I thought correlated with a problem area (Ex. The hint function). For instance, I mentioned how I noticed the incorrect hint was being displayed and asked it to explain why specifically it was wrong and what was wrong with the code "The labels ("Too High" / "Too Low") are correct, but the emoji hints are swapped." Experimeting with Copilot as well, it was able to produce similar sentiments, saying that the labels are correct but the actual outputted response was flipped. These descriptions fit the experience that I had when testing out the app, confirming their suggestions. 
---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

I decided whether or not a bug was really fixed by doing tests, specifically aiming to test the bugs that I had noticed before. For example, I tested a case where the secret number was 50 and entered guesses like 70 and 30; previously the game labeled the guess correctly as “Too High” or “Too Low” but displayed the wrong hint direction. AI helped suggest test cases such as checking both comparison branches and edge cases (correct guess, high guess, low guess), but I confirmed the results by manually running the game and inputting numbers myself. Additionally,
I had AI help me design a Pytest because I was not sure how to code a test file -- It created a new file called test_app.py which then has the issues that I had listed plus how it intends to solve them, elaborating and showing how to build a test.
---

## 4. What did you learn about Streamlit and state?

- In your own words, explain why the secret number kept changing in the original app.
- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
- What change did you make that finally gave the game a stable secret number?

The secret number kept changing in the original app because Streamlit used to rerun it's entire script whenever the user interacted with the app -- generating a new secret number instead of keeping the original one. Explaining this to someone whose never used it before, I would describe session state memory like footprints in the sand, and then a new sesseion state as a wave running over all the footprints, leaving the sand with no prints in it afterwards. Consulting Claude, the fix was storing the secret number in st.session_state.secret and only creating it if it did not already exist, which keeps the number stable during the game.
---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
