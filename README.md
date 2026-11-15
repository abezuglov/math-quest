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

### One link per grade

The game covers Kindergarten to 5th grade. Add `?grade=` to the app's address
to send a class straight to its grade (no grade buttons):

| Grade | Link to share |
|---|---|
| Kindergarten | `https://<your-app>.streamlit.app/?grade=K` |
| 1st grade | `https://<your-app>.streamlit.app/?grade=1` |
| 2nd grade | `https://<your-app>.streamlit.app/?grade=2` |
| 3rd grade | `https://<your-app>.streamlit.app/?grade=3` |
| 4th grade | `https://<your-app>.streamlit.app/?grade=4` |
| 5th grade | `https://<your-app>.streamlit.app/?grade=5` |

Without `?grade=`, the first screen asks the child to pick a grade. A hero
code remembers its grade, and the side panel has **Change grade** (starts a
new hero in the new grade; the old code stays valid).

Each child's browser is its own separate game. There are no accounts. Progress
is kept in a short **hero code** (like `400R-6J8N-80NJ-KXFQ`) that holds the
grade, the gems won, the level of every skill and the XP:

- The code is shown on the map and in the side panel. The child writes it down
  and types it on the first screen next time.
- The code is also kept in the page address, so refreshing the tab does not
  lose the hero.
- Share the plain link with the class, without the `?hero=...` part. A link
  that includes a code starts everyone as that hero.

At the end the child sees a certificate (name, rank, XP, accuracy and highest
level per skill) to show the teacher. Ctrl+P prints it. The right/asked counts
on it cover the current sitting only. The code is not secret-proof: a determined
child could guess a code that unlocks more, so treat the certificate as
encouragement, not as a grade.

## How the game works

| Region | Math |
|---|---|
| 1. Market Village | addition, subtraction |
| 2. Multiplication Mines | multiplication |
| 3. Division Docks | division, remainders |
| 4. Fraction Forest | fractions |
| 5. Castle Builders | area, perimeter |
| 6. Dragon's Peak | two-step problems, then everything mixed |

The home screen is a **map**. The child picks any region in any order; Dragon's
Peak opens when the other gems are won. Each region can be played two ways:

- **Quest:** the full story. 3 friendly riddles, 2 monster fights, one hands-on
  task and a boss.
- **Speed trial:** 5 quick riddles, 4 right wins the gem. For a child who already
  knows the topic, and the default way to revisit a region whose gem is won
  ("Quick practice"). A trial used to skip a quest asks level 3 riddles or harder.
  Anything played in a region whose gem is already won pays half XP.
  Dragon's Peak must be played as a full quest once.

**Hands-on tasks** (one per region): pick coin bags that make an exact price,
catch the multiples, share crates among boats with a slider, shade an equal
fraction, build a garden with a given area and fence, and find the wrong sum in
the Great Ledger. A miss gives a hint and a second try.

**Pictures:** fraction bars, a pie, rectangles and dot arrays are drawn on the
easier questions.

**Worksheet-style questions** (modelled on 4th-grade homework, Lesson 5.6):
estimating a 2-digit × 2-digit product by rounding to tens, 2-digit × 2-digit
word problems (including money), picking the right product from four answers,
finding a digit the Number Thief smudged in a worked multiplication, "twice as
many" comparisons, reading a dot array as a division equation, "is there
enough?" problems, subtracting across zeros (like 296,004 − 99,238) and
4-digit additions past 10,000.

**Story:** besides each region's own scenes, three story pages appear after the
1st gem, the 3rd gem and the last gem before the Peak, in whatever order the
regions are played.

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
highest level allowed, the starting level, times tables up to 10 or 12, the
speed-trial length and pass mark, and the health, damage and XP numbers. Save
the file and restart the app.

## Files

- `app.py` - the screens (Streamlit)
- `engine.py` - rules: XP, health, damage, adaptive levels, map, trials, hero codes
- `questions.py` - the question generators, one per topic, five levels each
- `tasks.py` - the hands-on tasks
- `pictures.py` - the drawings (map, scenes, math figures)
- `story.py` - regions, characters, dialogue and story pages
- `config.py` - teacher settings
- `tests/` - run with `pytest tests`
