# Implementation prompt: Math Quest for grades K–5

Paste the line below into a new Claude Code session in this repo:

> Read `docs/IMPLEMENTATION_PROMPT.md` and carry it out phase by phase. Run
> `pytest tests` after every phase and commit when it is green.

---

## Goal

Turn "The Number Thief of Arithmos" (a 4th-grade Streamlit math quest) into a
game that covers the **whole elementary math program, Kindergarten to 5th
grade**, where:

1. **The math content lives in text files**, one per grade
   (`curriculum/grade_k.toml` … `curriculum/grade_5.toml`). A teacher can add,
   change or switch off a topic or a question without touching Python.
2. **A question engine** (`curriculum.py`) turns the question *templates* in
   those files into real questions with random numbers.
3. **The child (or the teacher's link) picks the grade.** Each grade has its own
   link (`?grade=2`). With no grade in the link, the title screen asks for one.
   The hero code remembers the grade.

The game rules stay as they are (map, quests, speed trials, fights, adaptive
levels 1–5, XP, hero codes, certificate). Only the content and the grade layer
are new.

## What already exists (do not rewrite)

- `engine.py`: game rules. `questions.py`: hand-written 4th-grade generators.
  `tasks.py`: hands-on tasks. `pictures.py`: SVG drawings. `story.py`: regions
  and dialogue. `app.py`: the screens. `config.py`: teacher settings.
- `tests/`: 87 tests, all passing. **They must keep passing** (update them only
  where the change is intended, such as `Game("x")` getting a grade argument).
- **`curriculum.py` is already written** (the foundation of this plan). Read it
  first. It has:
  - a safe expression evaluator (`evaluate`): no `eval`, no imports, no
    attributes, only whitelisted functions (`randint`, `choice`, `sample`,
    `coin`, `name`, `item`, `frac`, `dec`, `gcd`, `lcm`, `round_to`, `digit`,
    `word`, `ordinal`, `plural`, `money`, `dec_text`, `join`, …). `/` gives an
    exact `Fraction`. `L` is the current level (1–5).
  - text templates: `{expr}` in `text`/`hint`/`explain`, with styles
    `{x|plain}` (no commas), `{x|word}`, `{x|money}`, `{x|dec}`,
    `{x|ordinal}`. `{answer}` is available in `explain`.
  - `load_grade`, `load_all`, `grade(code)`, `generate(topic, level, rng)`,
    `build`, `show_answer(q)` (prints decimals as `3.25`), and
    `check_template` / `check_all` (generate many samples, report broken
    content). `python curriculum.py` checks every file.
  - kinds: `number`, `fraction`, `decimal`, `choice`.
  - `generator = "multiplication"` in a template calls the old hand-written
    generator from `questions.py`, so 4th grade keeps its current questions.

  It was smoke-tested but has no test file yet and no grade files yet. Fix
  anything in it you find broken; keep its design.

## Content file format (implement exactly this; document it in `curriculum/FORMAT.md`)

```toml
grade = "2"                  # K, 1, 2, 3, 4 or 5
name  = "2nd grade"
title = "The Number Thief of Arithmos"     # optional

[[region]]                   # exactly 6 regions; the last one is the finale
key    = "village"           # map spot + scene picture: village | mines | docks | forest | castle | peak
name   = "Market Village"
gem    = "Gem of Sums"
topics = ["g2_add100", "g2_sub100"]
intro  = "..."               # optional: falls back to story.py for that key
outro  = "..."               # optional
task   = "coins"             # optional hands-on task (tasks.py kind); omit for none
task_topic = "g2_money"      # topic whose level/stats the task uses
# mix = true / final = true on the peak region, as in story.py

[[topic]]
id       = "g2_add100"       # lowercase, unique across ALL grades, start with grade prefix
label    = "Adding within 100"
standard = "2.NBT.B.5"       # Common Core code, for the teacher
tip      = "Add the tens first, then the ones."   # the sage's tip
enabled  = true              # teacher switch (default true)

  [[topic.question]]
  levels  = [1, 2]           # default: all of 1–5. Every level 1–5 must be covered.
  weight  = 1                # how often, relative to the others at that level
  kind    = "number"         # number | fraction | decimal | choice
  vars    = { a = "randint(10, 20 * L)", b = "randint(1, 9)" }   # in order; later vars may use earlier ones
  where   = "(a % 10) + b >= 10"        # optional: re-roll until true
  text    = "{name()} has {a} {item()}. ..."    # careful: call name()/item() ONCE in vars, not in text
  answer  = "a + b"
  hint    = "Make a ten first."
  explain = "{a} + {b} = {answer}."
  choices = ["'<'", "'>'", "'='"]      # choice kind: expressions; the answer must be one of them
  shuffle = false            # keep choice order (use for < > = and Yes/No)
  picture = ["array", "1", "a"]        # optional: pictures.for_question kind + expressions
```

Level meaning inside one grade: **1 = start of the year / easiest, 3 = grade
standard, 5 = stretch**. The adaptive rules already move the child between
levels.

## Phases

### Phase 1 — Engine tests and the 4th-grade file

1. `tests/test_curriculum.py`:
   - every grade file loads; topic ids are unique across grades; every topic
     covers levels 1–5; every region lists known topics; 6 regions, last one
     final.
   - `check_all(samples=60)` returns `[]` (this is the safety net that catches
     wrong math or typos in any content file; keep it fast, < 20 s).
   - the evaluator refuses `__import__('os')`, `().__class__`, `lambda: 1`,
     `open('x')`, `2 ** 99999`, and attribute access.
   - render styles, `number_word`, `fmt_decimal`, `fmt_money`, `round_to`.
2. `curriculum/grade_4.toml`: topic ids **exactly** the old `ALL_TOPICS`
   (`addition`, `subtraction`, `multiplication`, `division`, `fractions`,
   `area_perimeter`, `two_step`), each using `generator = "<same name>"`, and
   6 regions copied from `story.REGIONS` (same keys, names, gems, tasks). This
   keeps old hero codes and the old tests valid.
3. `curriculum/FORMAT.md`: the format above, written for a teacher, with three
   worked examples (number, fraction, choice) and "how to check your file:
   `python curriculum.py`".

### Phase 2 — Wire grades into the game

1. `Game(name, grade="4", seed=None)`. Topics, labels, tips and regions come
   from `curriculum.grade(grade)`. Questions come from `curriculum.generate`.
   Keep `questions.py` as the home of the legacy generators and of
   `parse_answer`, `fmt`, `severity`.
2. Regions: build the region dicts from the grade file. Encounters (riddle /
   fight / task / boss characters and lines) come from `story.py` by region
   `key`; move topic-specific words in those lines ("multiply", "fractions")
   into the region's optional overrides, or make the shared lines topic-neutral.
   Add an optional `[[region.encounter]]` override in TOML for name/emoji/
   intro/win per encounter. If a region has no `task`, drop the task encounter.
3. `config.TOPICS` is replaced by the `enabled` flag in the TOML files; keep
   `config.py` for numbers (HP, XP, tiers…), and add `DEFAULT_GRADE = None`
   (None = ask) and `GRADES = ["K", "1", "2", "3", "4", "5"]` (which grades are
   offered).
4. Feedback and the answer shown after a miss use `curriculum.show_answer(q)`
   (decimals print as `0.75`, not `3/4`). The input error message mentions
   decimals for decimal questions.
5. Hands-on tasks: a region's task uses the level of `task_topic`. Tasks that do
   not fit young grades are simply not listed in those grade files. Add a
   gentler level for `ledger` (sums within 20) so K–1 can still finish the story
   on the Great Ledger page; use it when the grade is K or 1.
6. Ranks scale by grade or by XP earned in that grade; keep them reachable in
   every grade (test: a perfect player reaches the top rank in each grade).

### Phase 3 — Grade choice, links and hero codes

1. URL: `?grade=K|1|2|3|4|5`. Title screen: if no grade in the URL and
   `DEFAULT_GRADE` is None, show 6 big buttons ("Kindergarten", "1st grade", …)
   before the name box. The chosen grade is written into the URL with the hero.
   Map header shows the grade; the sidebar has "Change grade" (asks for
   confirmation, starts a new hero for that grade, the old code stays valid).
2. README: one link per grade for the teacher to share, e.g.
   `https://<app>.streamlit.app/?grade=3`.
3. Hero code **v2**: first character is the grade (`K,1,2,3,4,5`), then base-32
   payload holding: region gems (6 bits), level of every topic of that grade in
   file order (3 bits each), XP (17 bits), story pages (2 bits), check value.
   Length grows with the number of topics; group in 4s with dashes.
   **Old 12-character codes (no grade prefix) must still load as 4th grade**
   (keep a test with a code made by the current code). Topics switched off keep
   their level in the code, like today. Adding a topic at the END of a grade
   file must not break old codes of that grade (decode missing trailing topics
   as the start level; store the topic count in the code). Document: never
   reorder or delete topics in a file once children have codes — switch them off.

### Phase 4 — Content for every grade

Write the other five grade files. Aim for **8–12 topics per grade, 3–6
templates per topic**, word problems mixed with bare sums, everyday kid themes
(market, animals, school, sports). Respect reading level: **K and 1st: at most
about 10 words per question, numbers before words, pictures whenever possible.**
Follow Common Core; the topic list below is the plan (ids and regions may be
adjusted, standards are the checklist):

**Kindergarten** (`grade_k.toml`)
- village "Counting Meadow": count objects to 20 (dots picture); number after /
  before; count on from a number.
- mines: compare numbers / groups (more, fewer, same — choice).
- docks: add within 10 (story + bare), make 10 (`7 + ? = 10`).
- forest: subtract within 10.
- castle: shapes (sides, corners; flat vs solid; choice), compare length/weight
  (longer, heavier — choice).
- peak (mix): teen numbers as 10 + ones, plus everything.

**1st grade**
- add & subtract within 20 (strategies: make ten, doubles; missing addend);
  word problems with all three unknown positions; true/false equations
  (`6 = 6 + 0` — choice).
- place value: tens and ones to 120; compare 2-digit numbers (`<`, `>`, `=`);
  10 more / 10 less; add within 100 (2-digit + 1-digit, + multiples of 10).
- measurement: order 3 lengths; tell time to the hour and half hour (clock
  picture, choice).
- data: read a tally/picture graph (how many more?).
- geometry: halves and fourths of a shape (choice).

**2nd grade**
- add & subtract within 100 fluently, within 1000 with regrouping; two-step
  word problems within 100.
- place value to 1000: hundreds/tens/ones, expanded form, number words,
  compare 3-digit numbers, skip-count by 5, 10, 100; 10/100 more or less.
- even and odd (choice); arrays and repeated addition (array picture).
- measurement: inches/feet, cm/meters, estimate lengths, length word problems,
  number line.
- money: coins and bills, `$` and `¢` (coin picture; `money` style).
- time to the nearest 5 minutes, a.m./p.m.
- picture and bar graphs; shapes (angles, faces); partition into halves,
  thirds, fourths.

**3rd grade**
- multiplication & division within 100 (facts, arrays, equal groups, unknown
  factor, properties); two-step word problems with all four operations;
  patterns in the times table.
- rounding to the nearest 10 and 100; add & subtract within 1000; multiply by
  multiples of 10 (`6 × 70`).
- fractions: unit fractions, fractions on a number line (picture), equivalent
  fractions, whole numbers as fractions, compare same numerator or same
  denominator.
- time to the minute and elapsed time; mass (g, kg) and liquid volume (L);
  scaled bar graphs.
- area (count squares, length × width, add rectangles) and perimeter;
  quadrilaterals (choice).

**4th grade** (keep the existing generators, then ADD topics at the end):
place value to 1,000,000 and rounding any place; factors, multiples, prime or
composite; decimals as tenths/hundredths (`0.62 = 62/100`), compare decimals;
measurement conversions (ft↔in, kg↔g, hours↔minutes); angles (degrees, adding
angles); lines and symmetry.

**5th grade**
- place value: powers of ten, multiplying/dividing by 10, 100, 1000; decimals to
  thousandths (read, expanded form, compare, round).
- operations: multi-digit multiplication; division with 2-digit divisors;
  add, subtract, multiply, divide decimals to hundredths.
- fractions: add & subtract unlike denominators (including mixed numbers);
  multiply fraction × whole and fraction × fraction; fraction as division
  (`3 ÷ 4 = 3/4`); divide unit fraction by whole and whole by unit fraction.
- volume of rectangular prisms (`l × w × h`, cube picture), unit conversions
  within one system.
- expressions with parentheses (order of operations), numeric patterns;
  coordinate plane, first quadrant (grid picture).

New pictures go in `pictures.py` and `pictures.for_question` (each needs an SVG
validity test like the existing ones): `clock(h, m)`, `coins(list)`,
`number_line(lo, hi, marks)`, `shape(name)`, `tally(counts)`, `bar_graph(...)`,
`cubes(l, w, h)`, `grid_point(x, y)`. Keep them simple, readable at phone width.

**Math checks for content** (beyond `check_all`): each template's answer must
be exactly one value; a choice question must have exactly one right choice;
no negative numbers below 6th grade; no answers that need rounding unless the
question asks for rounding; money and decimal answers must have at most 2
decimal places (5th grade: 3).

### Phase 5 — Kid-friendliness for the youngest

1. 🔊 "Read it to me" button on every question for grades K–2 (browser
   `speechSynthesis` via `st.html`, reading the question text; on by default
   for K and 1st, a setting in `config.py`).
2. K–1: bigger question text, choice buttons with pictures where possible,
   fewer encounters per region (config: `ENCOUNTERS_BY_GRADE`), and no typing
   of fractions.
3. Certificate shows the grade and the Common Core codes of the topics practiced.

### Phase 6 — Finish

- README: grades, per-grade links, "how to change the content" pointing to
  `curriculum/FORMAT.md`, and the hero-code rules for teachers.
- Update `.roborev.toml` review guidelines: grades K–5 (ages 5–11) instead of
  "4th graders", and "check each question against its grade's reading level".
- `test_app.py`: play one full game through the UI for grade K and grade 5 as
  well as grade 4; picking a grade from the title screen; `?grade=` links.

## Rules for the whole job

- Keep it simple: plain Python + Streamlit + TOML (`tomllib` is built in, so no
  new dependency). No database, no accounts, no framework.
- Content files must never be able to run code: only the evaluator in
  `curriculum.py` reads expressions.
- Wrong math is the worst bug. Every new template must pass `check_all`, and
  for tricky ones (rounding, remainders, money) add a targeted test.
- Commit after every phase with a clear message. Do not touch `.roborev.toml`
  until phase 6, and leave the user's uncommitted `.gitignore` change alone.
