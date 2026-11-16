# Writing the math content (for teachers)

All the math in the game lives in this folder, one plain text file per grade:

| File | Grade |
|---|---|
| `grade_k.toml` | Kindergarten |
| `grade_1.toml` … `grade_5.toml` | 1st to 5th grade |

You can open these files in any text editor (Notepad works). Nothing in them
can run code: the game reads the small expressions inside with its own tiny
calculator, which only knows numbers, the operators `+ - * / // % **`, lists,
comparisons and the helper functions listed at the end of this page.

After every change: **check your file** with

```
python curriculum.py
```

It makes hundreds of questions from every template and prints `PROBLEM:` lines
for anything broken (a typo in a name, an answer that is not a whole number, a
choice question whose answer is not one of the choices, a `where` that is never
true…). No `PROBLEM:` lines means the file is good. The same check runs in the
tests (`pytest tests`).

## The shape of a file

```toml
grade = "2"                  # K, 1, 2, 3, 4 or 5
name  = "2nd grade"
title = "The Number Thief of Arithmos"     # optional

[[region]]                   # exactly 6 regions; the last one is the finale
key    = "village"           # map spot + picture: village | mines | docks | forest | castle | peak
name   = "Market Village"
gem    = "Gem of Sums"
topics = ["g2_add100", "g2_sub100"]
intro  = "..."               # optional: falls back to the story for that key
outro  = "..."               # optional
task   = "coins"             # optional hands-on task; leave it out for none
task_topic = "g2_money"      # topic whose level and stats the task uses
# mix = true / final = true on the peak region (the finale)

[[topic]]
id       = "g2_add100"       # lowercase, unique across ALL grades, start with the grade prefix
label    = "Adding within 100"
standard = "2.NBT.B.5"       # Common Core code, for the certificate
tip      = "Add the tens first, then the ones."   # what the sage says after two misses
enabled  = true              # teacher switch (default true)

  [[topic.question]]
  levels  = [1, 2]           # default: all of 1-5. Every level 1-5 must be covered.
  weight  = 1                # how often, relative to the other templates at that level
  kind    = "number"         # number | fraction | decimal | choice
  vars    = { a = "randint(10, 20 * L)", b = "randint(1, 9)" }   # in order; later vars may use earlier ones
  where   = "(a % 10) + b >= 10"        # optional: roll the dice again until this is true
  text    = "{who} has {a} {what}. ..."
  answer  = "a + b"
  hint    = "Make a ten first."
  explain = "{a} + {b} = {answer}."
  choices = ["'<'", "'>'", "'='"]      # choice kind only: expressions; the answer must be one of them
  shuffle = false            # keep the choice order (use for < > = and Yes/No)
  picture = ["array", "1", "a"]        # optional: a drawing (see Pictures)
```

### Regions

Each grade has **six regions**, one for each map spot: `village`, `mines`,
`docks`, `forest`, `castle` and `peak`, in that order. The last region is the
finale: give it `mix = true` (fights and trials there mix every topic of the
grade) and `final = true` (it opens when the other five gems are won).

- `topics`: the topic ids asked in this region.
- `task`: an optional hands-on task: `coins` (pick coin bags that make a price),
  `multiples` (catch the multiples), `share` (crates on boats), `shade`
  (shade a fraction), `garden` (build a rectangle), `ledger` (find the wrong
  sum). `task_topic` says which topic's level the task is made at and which
  topic's stats it counts for. `task_levels = [1, 3]` caps the task at those
  levels for grades where the full task is too hard. Leave `task` out for no
  task in that region.
- `intro`, `outro`, `memory`: the region's story text. If left out, the 4th-grade
  story for that map spot is used.
- The characters (friends, monsters, boss) come from the story for that map
  spot. To rename one or change its lines, add an override:

  ```toml
  [[region.encounter]]
  slot  = 0            # which encounter in the region: 0 = the first
  name  = "Counting Cow"
  emoji = "🐄"
  intro = "Moo! How many apples do you see?"
  win   = "Moo-velous!"
  ```
  Any field you leave out keeps the original.

### Topics

- `id` must be lowercase letters, digits and `_`, start with the grade
  (`k_`, `g1_`, `g2_` …) and be unique across every grade file.
- **Never reorder or delete a topic once children have hero codes for that
  grade.** The hero code stores one skill level per topic *in file order*.
  Add new topics at the END of the file, and switch off a topic you no longer
  want with `enabled = false` (its level stays in the code).
- Every topic must have at least one template for each level 1 to 5.

**Levels** inside one grade: **1 = start of the year / easiest, 3 = the grade
standard, 5 = a stretch.** The game moves each child up a level after three
right answers in a row and down after two misses.

### Templates (`[[topic.question]]`)

- `vars` are rolled in the order written. `L` is the current level (1-5), so
  `randint(1, 4 * L)` grows with the level.
- `where` is checked after the vars are rolled; if false, everything is rolled
  again (up to 300 tries, then the checker complains: make your `where` easier
  to satisfy).
- `answer` is an expression. For `kind = "number"` it must come out a whole
  number; `"fraction"` allows fractions (`/` always gives an exact fraction:
  `3 / 4` is three quarters, not 0.75); `"decimal"` shows the answer as a
  decimal (`0.75`); `"choice"` shows buttons and the answer must equal one of
  the `choices` exactly.
- `text`, `hint` and `explain` are templates: anything in `{braces}` is an
  expression and is replaced by its value. `{answer}` works in `explain`.
  Add a **style** after `|`:

  | Style | Example | Shows |
  |---|---|---|
  | (none) | `{n}` | `1,234` or `3/4` |
  | `plain` | `{n\|plain}` | `1234` (no comma) |
  | `word` | `{n\|word}` | `one thousand two hundred thirty-four` |
  | `money` | `{n\|money}` | `$3.25` |
  | `dec` | `{n\|dec}` | `0.75` |
  | `ordinal` | `{n\|ordinal}` | `3rd` |

- **Call `name()` and `item()` once, in `vars`**, not in the text: each call
  picks a new random name, so `{name()} ... {name()}` would be two people.
- A `choice` question gets 2 to 4 choices, all different. With `shuffle = false`
  the buttons keep the order written (use it for `< > =` or `Yes / No`).
- `generator = "multiplication"` (4th grade only) uses a hand-written question
  maker from `questions.py` instead of a template. Such a question needs
  nothing else.

### Keep the math right

The checker makes 60 questions from each template at each level and refuses:
a non-whole answer in a `number` question, a negative answer, a choice answer
that is not one of the choices, and anything that crashes. It cannot know
whether `a - b` is what the story asks for, so **read a few generated questions
yourself**: run `python -c "import curriculum, random; print(curriculum.generate(curriculum.grade('2').topics['g2_add100'], 3).text)"`.

Rules of thumb:

- One right answer only. A `where` clause is the usual fix (`where = "a != b"`).
- No negative numbers before 6th grade: `where = "a > b"` before `a - b`.
- Money and decimal answers: at most 2 decimal places (3 in 5th grade).
- K and 1st grade: at most about 10 words in a question, numbers before words,
  and a picture whenever possible. These grades never type a fraction or a
  decimal: the file is refused if it has a `fraction` or `decimal` question
  (ask "What part is it?" as a `choice` question instead).
- In K–2 a 🔊 button reads the question aloud. Write `?` for the missing
  number (`7 + ? = 10`): the voice says "blank". Choice answers that the
  question text does not already name are read out at the end.
- In K and 1st grade, choice buttons get a small picture when they can:
  animal and object names get an emoji, numbers up to 10 get counting dots
  and shape names get the shape (only when the question has no picture of
  its own). The grades and the number of encounters per region are set in
  `config.py`.

## Worked examples

**1. A number question with a picture (2nd grade, arrays)**

```toml
[[topic]]
id       = "g2_arrays"
label    = "Arrays"
standard = "2.OA.C.4"
tip      = "Count one row, then add that number once for every row."

  [[topic.question]]
  levels  = [1, 2, 3]
  vars    = { r = "randint(2, 3 + L)", c = "randint(2, 5)" }
  text    = "How many dots are there?"
  answer  = "r * c"
  hint    = "Count the dots in one row. Then count the rows."
  explain = "{r} rows of {c} dots: {join([c] * r, ' + ')} = {answer}."
  picture = ["array", "r", "c"]
```

**2. A fraction question (3rd grade)**

```toml
[[topic]]
id       = "g3_unit_fractions"
label    = "Fractions of a whole"
standard = "3.NF.A.1"
tip      = "The bottom number tells how many equal parts make the whole."

  [[topic.question]]
  kind    = "fraction"
  vars    = { d = "choice([2, 3, 4, 6, 8])", k = "randint(1, d - 1)" }
  text    = "A pie is cut into {d} equal slices. {k} {'slice is' if k == 1 else 'slices are'} eaten. What fraction of the pie is eaten?"
  answer  = "k / d"
  hint    = "Top: slices eaten. Bottom: slices in the whole pie."
  explain = "{k} out of {d} slices is {k}/{d}."
  picture = ["pie", "k", "d"]
```

(The child may type `2/4` for a pie with 2 of 4 slices eaten: equal fractions
are accepted.)

**3. A choice question (1st grade, comparing)**

```toml
[[topic]]
id       = "g1_compare"
label    = "Comparing numbers"
standard = "1.NBT.B.3"
tip      = "Look at the tens first. More tens means a bigger number."

  [[topic.question]]
  kind    = "choice"
  vars    = { a = "randint(10, 20 * L)", b = "randint(10, 20 * L)" }
  text    = "{a} ? {b}   Which sign goes in the middle?"
  answer  = "compare(a, b)"
  choices = ["'<'", "'>'", "'='"]
  shuffle = false
  hint    = "Which number has more tens?"
  explain = "{a} {answer} {b}."
```

## Pictures

`picture = ["kind", "expr", "expr", ...]`: the first entry is the kind of
drawing, the rest are expressions for its numbers.

| Kind | Arguments | Draws |
|---|---|---|
| `array` | rows, cols | rows of dots |
| `pie` | eaten, slices | a pie with some slices eaten |
| `bars` | list of [top, bottom] pairs | fraction bars |
| `rect` | length, width, top label, side label | a rectangle |
| `dots` | n | up to 20 counting dots (K) |
| `clock` | hour, minute | an analog clock |
| `coins` | list of cent values | coins and bills |
| `number_line` | low, high, marked value | a number line with one point |
| `shape` | name | a flat or solid shape |
| `tally` | list of counts | tally marks |
| `bar_graph` | list of labels, list of counts | a bar graph |
| `cubes` | length, width, height | a box of unit cubes |
| `grid_point` | x, y | a point on a grid (first quadrant) |

## Functions you may use in expressions

Random (use the game's dice):
`randint(lo, hi)`, `randstep(lo, hi, step)` (multiples of step from lo to hi),
`choice(list)`, `sample(list, k)`, `shuffled(list)`, `coin()` (true half the
time), `name()`, `names(k)`, `item()`.

Numbers: `+ - * / // % **`, `min max abs sum len int round_to(n, place)
digit(n, place) gcd lcm frac(n, d) dec("0.25") num(x) den(x) factors(n)
is_prime(n) range(a, b) sorted(list) reversed(list) count(list, x)
index(list, x) different(a, b, c)`.

Words: `word(n)` (`twelve`), `ordinal(n)` (`3rd`), `plural(n, "apple")`
(`3 apples`), `money(x)` (`$3.25`), `dec_text(x)` (`0.75`), `plain(n)`
(`1234`), `expanded(n)` (`300 + 40 + 5`), `time(h, m)` (`3:05`),
`compare(a, b)` (`<`, `>` or `=`), `yesno(ok)` (`Yes` / `No`), `str(x)`,
`join(list, ", ")`.

Also `x if test else y`, `and`, `or`, `not`, lists `[a, b, c]`, `list[i]` and
`'text'` in quotes. Decimal numbers like `0.25` are read exactly (as 1/4).
