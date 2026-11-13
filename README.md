# The Number Thief of Arithmos

A math text quest for 4th graders. A trickster dragon has stolen the numbers from
the kingdom of Arithmos, and the player wins them back region by region by
answering riddles and beating monsters with math.

## Run it on your computer

```
python -m venv .venv
.venv\Scripts\activate          (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
```

The game opens in the browser at http://localhost:8501.

## Put it online for a class (free)

1. Create a GitHub repository and push this folder to it.
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **Create app**, pick the repository, and set the main file to `app.py`.
4. Click **Deploy**. Share the link it gives you with the class.

Each child's browser is its own separate game. There are no accounts and nothing
is saved: closing or refreshing the tab starts over. At the end the child sees a
certificate (name, rank, XP, accuracy and highest level per skill) to show the
teacher. Ctrl+P prints it.

## How the game works

| Region | Math |
|---|---|
| 1. Market Village | addition, subtraction |
| 2. Multiplication Mines | multiplication |
| 3. Division Docks | division, remainders |
| 4. Fraction Forest | fractions |
| 5. Castle Builders | area, perimeter |
| 6. Dragon's Peak | two-step problems, then everything mixed |

Each region has 3 friendly riddles, 2 monster fights and a boss.

- **Riddles:** a right answer earns XP. A miss gives a hint and one retry for half XP.
- **Fights:** a right answer hits the monster. A wrong answer costs health,
  depending on how far off it is: within 10% (or off by 1) costs 5, within 30%
  costs 12, further off costs 20. This rewards estimating over wild guessing.
- **Adaptive difficulty:** every topic has its own level from 1 to 5. Three
  right in a row moves that topic up, two wrong in a row moves it down. XP per
  answer is 10 x level, so harder questions pay more. (Moving up is slower than
  moving down on purpose: a symmetric rule settles children near 50% correct,
  this one settles them nearer 70-80%.)
- **Safety net:** below 30 health a healer offers an easier potion riddle. At 0
  health the region restarts with full health, an easier level, and a shield
  that softens later hits there. Parts of a region already beaten give no XP a
  second time, so replaying cannot be used to farm XP. After two misses in a row
  on a topic, a sage gives a strategy tip.

## Teacher settings

Everything adjustable is in `config.py`: which topics are on, the lowest and
highest level allowed, the starting level, times tables up to 10 or 12, and the
health, damage and XP numbers. Save the file and restart the app.

## Files

- `app.py` - the screens (Streamlit)
- `engine.py` - rules: XP, health, damage, adaptive levels, story progress
- `questions.py` - the question generators, one per topic, five levels each
- `story.py` - regions, characters and dialogue
- `config.py` - teacher settings
- `tests/` - run with `pytest tests`
