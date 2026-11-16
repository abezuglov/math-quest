# The Number Thief of Arithmos

A math text quest for **Kindergarten to 5th grade** (ages 5-11). A trickster
dragon has stolen the numbers from the kingdom of Arithmos, and the player wins
them back region by region by answering riddles and beating monsters with math.

Every grade has its own kingdom map, built from that grade's Common Core
topics. The math lives in plain text files (`curriculum/grade_k.toml` ...
`curriculum/grade_5.toml`), so a teacher can change it without touching Python
(see [How to change the content](#how-to-change-the-content)).

## Run it on your computer

You need Python 3.11 or newer.

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
   Under **Advanced settings**, pick Python 3.11 or newer.
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
is kept in a short **hero code** (like `4000-14J9-4J94-G000-6YB0`) that holds the
grade, the gems won, the level of every skill and the XP:

- The code is shown on the map and in the side panel. The child writes it down
  and types it on the first screen next time (no need to pick the grade again:
  the first character of the code is the grade).
- The code is also kept in the page address, so refreshing the tab does not
  lose the hero.
- Share the plain link with the class, without the `?hero=...` part. A link
  that includes a code starts everyone as that hero.

### Hero-code rules for teachers

- The first character is the grade (`K`, `1` ... `5`). Codes differ in length
  between grades because each grade has a different number of skills.
- Old 12-character codes from the first, 4th-grade-only version still work and
  load as 4th grade.
- A code stores one level per topic **in the order of the grade file**. So once
  children have codes, **never reorder or delete topics** in a grade file.
  Switch a topic off with `enabled = false` instead (its level stays in the
  code), and add new topics only at the **end** of the file (old codes start the
  new topic at the starting level).
- Changing a question, a hint, a tip or a region name never breaks a code.

At the end the child sees a certificate (name, grade, rank, XP, accuracy, the
highest level per skill and the Common Core codes practiced) to show the
teacher. Ctrl+P prints it. The right/asked counts
on it cover the current sitting only. The code is not secret-proof: a determined
child could guess a code that unlocks more, so treat the certificate as
encouragement, not as a grade.

## How the game works

Each grade's map has six regions. The last one, Dragon's Peak, has its own
topic and then mixes everything.

| Grade | Regions (main math) |
|---|---|
| Kindergarten | Counting Meadow (count to 20, number after), Compare Caves (more, fewer, same), Adding Harbor (add within 10, make 10), Take-Away Woods (subtract within 10), Shape Castle (shapes, longer/heavier), Dragon's Peak (teen numbers) |
| 1st grade | Sum Village (add and subtract within 20, word problems, true or false), Tens Mines (tens and ones, compare, 10 more/less), Measure Docks (length, time to the half hour), Graph Forest (tally and picture graphs), Shape Castle (halves and fourths), Dragon's Peak (add within 100) |
| 2nd grade | Market Village (within 100, money), Place Value Mines (to 1000, compare, skip-count), Array Docks (arrays, within 1000), Measure Forest (length, time to 5 minutes), Castle of Charts (graphs, shapes), Dragon's Peak (two-step problems) |
| 3rd grade | Market Village (within 1000, rounding), Multiplication Mines (facts, × multiples of 10), Division Docks (division, bar graphs), Fraction Forest (fractions, equivalent fractions), Castle Builders (area, perimeter, shapes, time, mass, volume), Dragon's Peak (two-step problems) |
| 4th grade | Market Village (add, subtract, place value to 1,000,000), Multiplication Mines (multiplication, factors and primes), Division Docks (division, remainders, conversions), Fraction Forest (fractions, decimals), Castle Builders (area, perimeter, angles, lines), Dragon's Peak (two-step problems) |
| 5th grade | Market Village (decimals to thousandths, decimal operations), Multiplication Mines (powers of ten, multi-digit ×), Division Docks (2-digit divisors, conversions), Fraction Forest (add, multiply and divide fractions), Castle Builders (volume, coordinate plane), Dragon's Peak (expressions) |

The home screen is a **map**. The child picks any region in any order; Dragon's
Peak opens when the other gems are won. Each region can be played two ways:

- **Quest:** the full story. 3 friendly riddles, 2 monster fights, one hands-on
  task and a boss. Kindergarten and 1st grade get shorter quests (4 and 5
  encounters, set in `config.py`), and a region whose grade file lists no
  hands-on task has none.
- **Speed trial:** 5 quick riddles, 4 right wins the gem. For a child who already
  knows the topic, and the default way to revisit a region whose gem is won
  ("Quick practice"). A trial used to skip a quest asks level 3 riddles or harder.
  Anything played in a region whose gem is already won pays half XP.
  Dragon's Peak must be played as a full quest once.

**For the youngest:** in K-2 every question has a 🔊 "Read it to me" button
(K and 1st read each new question aloud by themselves; the child can switch
this off in the side panel). K and 1st also get bigger text, picture answer
buttons and no typed fractions.

**Hands-on tasks** (one per region in grades 3-5; younger grades get fewer):
pick coin bags that make an exact price, catch the multiples, share crates
among boats with a slider, shade an equal fraction, build a garden with a given
area and fence, and find the wrong sum in the Great Ledger (K and 1st get a
gentler ledger with sums within 20). A miss gives a hint and a second try.

**Pictures:** dots, fraction bars, pies, rectangles, arrays, clocks, coins,
number lines, shapes, tally charts, bar graphs, cubes and a coordinate grid are
drawn on the questions that need them.

**Worksheet-style questions** in 4th grade (modelled on homework, Lesson 5.6):
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

**Numbers and switches** are in `config.py`: which grades the title screen
offers (`GRADES`), one fixed grade for the whole app (`DEFAULT_GRADE`),
read-aloud and big text for the youngest, quest length per grade, the lowest,
highest and starting level, times tables up to 10 or 12, the speed-trial length
and pass mark, and the health, damage and XP numbers. Save the file and restart
the app.

### How to change the content

The questions live in `curriculum/grade_k.toml` ... `curriculum/grade_5.toml`,
one file per grade. Each file lists its six regions and its topics. Each topic
has a few question templates with random numbers, an answer, a hint and an
explanation. Without touching Python a teacher can:

- switch a topic off with `enabled = false`,
- change the wording, the numbers, a hint or the sage's tip,
- add a question template, or a new topic at the end of the file.

**[`curriculum/FORMAT.md`](curriculum/FORMAT.md)** explains the format with
worked examples. After editing, check the files:

```
python curriculum.py
```

It makes many sample questions from every template and lists anything broken
(a typo, a wrong kind of answer, a choice question with no right choice...).
The content files cannot run code: the game reads the small expressions in
them with its own safe calculator. Read the hero-code rules above before
reordering or deleting anything.

## Files

- `app.py` - the screens (Streamlit)
- `engine.py` - rules: XP, health, damage, adaptive levels, map, trials, hero codes
- `curriculum/` - the math content, one TOML file per grade, and `FORMAT.md`
- `curriculum.py` - reads the grade files and turns templates into questions
  (`python curriculum.py` checks them)
- `questions.py` - the original 4th-grade generators and answer checking
- `tasks.py` - the hands-on tasks
- `pictures.py` - the drawings (map, scenes, math figures)
- `story.py` - regions, characters, dialogue and story pages
- `config.py` - teacher settings
- `tests/` - run with `pytest tests`
