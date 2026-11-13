"""Random math question generators, one per topic, five difficulty tiers each."""
from __future__ import annotations

import math
import random
import re
from dataclasses import dataclass, field
from fractions import Fraction

import config

ALL_TOPICS = [
    "addition",
    "subtraction",
    "multiplication",
    "division",
    "fractions",
    "area_perimeter",
    "two_step",
]

TOPIC_LABELS = {
    "addition": "Addition",
    "subtraction": "Subtraction",
    "multiplication": "Multiplication",
    "division": "Division",
    "fractions": "Fractions",
    "area_perimeter": "Area & Perimeter",
    "two_step": "Two-Step Problems",
}

TOPIC_TIPS = {
    "addition": "Line up the place values. Add the biggest parts first "
                "(thousands, hundreds, tens), then the ones.",
    "subtraction": "Take away one place value at a time: first the hundreds, "
                   "then the tens, then the ones. Check by adding back.",
    "multiplication": "Break a big number into tens and ones, multiply each "
                      "part, then add the two results together.",
    "division": "Division undoes multiplication. Ask yourself: "
                "'what number times the divisor gives me this total?'",
    "fractions": "The bottom number says how many equal pieces make a whole. "
                 "The top number says how many pieces you have.",
    "area_perimeter": "Perimeter is the walk AROUND the shape: add all the sides. "
                      "Area is the space INSIDE: length times width.",
    "two_step": "Do one step at a time. Write down the answer to the first "
                "step, then use it for the second step.",
}

ITEMS = ["gold coins", "apples", "lanterns", "seashells", "acorns", "marbles"]
UNITS = ["feet", "meters"]


@dataclass
class Question:
    topic: str
    tier: int
    text: str
    answer: object            # Fraction for typed answers, str for choices
    hint: str
    explanation: str
    kind: str = "number"      # "number" | "fraction" | "choice"
    choices: list = field(default_factory=list)


# --------------------------------------------------------------------------
# Answer handling
# --------------------------------------------------------------------------
def parse_answer(raw: str):
    """Turn what a child typed into a Fraction, or None if it is not a number.

    Accepts 42, 1,203, 3.5, 3/4, 1 1/2 and trailing units like '12 feet'.
    """
    if raw is None or len(raw) > 30 or not raw.isascii():
        return None
    s = raw.strip().lower()
    s = re.sub(r"(?<=\d),(?=\d{3}(?!\d))", "", s)   # 1,203 -> 1203 (but not 1,2)
    s = re.sub(r"[a-z$%]+\.?", " ", s).strip()
    s = re.sub(r"\s+", " ", s)
    m = re.fullmatch(r"(\d+) (\d+) ?/ ?(\d+)", s)
    if m:
        w, n, d = (int(x) for x in m.groups())
        return Fraction(w) + Fraction(n, d) if d else None
    m = re.fullmatch(r"(-?\d+) ?/ ?(\d+)", s)
    if m:
        n, d = int(m.group(1)), int(m.group(2))
        return Fraction(n, d) if d else None
    if re.fullmatch(r"-?\d+(\.\d+)?", s):
        try:
            return Fraction(s)
        except ValueError:
            return None
    return None


def is_correct(q: Question, value) -> bool:
    return value == q.answer


def severity(q: Question, value) -> str:
    """How far off a wrong answer is: 'light', 'medium' or 'heavy'."""
    if q.kind == "choice":
        return "medium"
    correct = q.answer
    diff = abs(value - correct)
    rel = diff / abs(correct) if correct else diff
    whole = correct.denominator == 1 and value.denominator == 1
    if rel <= config.LIGHT_WITHIN or (whole and diff <= 1):
        return "light"
    if rel <= config.MEDIUM_WITHIN or (whole and diff <= 2):
        return "medium"
    return "heavy"


def fmt(value) -> str:
    """Show an answer the way a 4th grader would write it."""
    if isinstance(value, str):
        return value
    value = Fraction(value)
    if value < 0:
        return "-" + fmt(-value)
    if value.denominator == 1:
        return f"{value.numerator:,}"
    whole, rest = divmod(value.numerator, value.denominator)
    if whole:
        return f"{whole} {rest}/{value.denominator}"
    return f"{rest}/{value.denominator}"


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def _p(text, answer, hint, expl, kind="number", choices=None):
    return dict(text=text, answer=answer, hint=hint, explanation=expl,
                kind=kind, choices=list(choices or []))


def _place_parts(n):
    """345 -> [300, 40, 5]"""
    parts, place = [], 1
    while n:
        digit = n % 10
        if digit:
            parts.append(digit * place)
        n //= 10
        place *= 10
    return parts[::-1]


def _add_steps(a, b):
    total, out = a, []
    for part in _place_parts(b):
        out.append(f"{total:,} + {part:,} = {total + part:,}")
        total += part
    return ", then ".join(out)


def _sub_steps(a, b):
    total, out = a, []
    for part in _place_parts(b):
        out.append(f"{total:,} − {part:,} = {total - part:,}")
        total -= part
    return ", then ".join(out)


def _mul_steps(a, b):
    """Explain a x b by splitting a into place parts."""
    parts = _place_parts(a)
    if len(parts) == 1:
        return f"{a:,} × {b:,} = {a * b:,}"
    pieces = [f"{p:,} × {b:,} = {p * b:,}" for p in parts]
    total = " + ".join(f"{p * b:,}" for p in parts)
    return f"Split {a:,} into {' + '.join(f'{p:,}' for p in parts)}. " \
           f"{', and '.join(pieces)}. Add them: {total} = {a * b:,}"


def _div_steps(n, d):
    """Explain n / d (exact) by taking out easy groups (partial quotients)."""
    q = n // d
    parts = _place_parts(q)
    if len(parts) == 1:
        return f"{d} × {q} = {n:,}, so {n:,} ÷ {d} = {q}"
    left, out = n, []
    for part in parts:
        left -= d * part
        out.append(f"{d} × {part:,} = {d * part:,} (left: {left:,})")
    return (f"Take out easy groups of {d}. {'. '.join(out)}. Add the groups: "
            f"{' + '.join(f'{part:,}' for part in parts)} = {q:,}, "
            f"so {n:,} ÷ {d} = {q:,}")


# --------------------------------------------------------------------------
# Generators
# --------------------------------------------------------------------------
def _addition(t, rng):
    if t >= 5 and rng.random() < 0.5:
        a, b = rng.randint(1200, 4999), rng.randint(1200, 4999)
        s = a + b
        return _p(f"Fill in the missing number:   ? + {a:,} = {s:,}", b,
                  "Work backwards: subtract the number you know from the total.",
                  f"The missing number is {s:,} − {a:,} = {b:,}.")
    lo_a, hi_a, lo_b, hi_b = {1: (11, 49, 11, 49), 2: (25, 99, 25, 99),
                              3: (100, 899, 100, 899),
                              4: (1000, 8999, 250, 4999),
                              5: (10000, 50000, 1000, 9999)}[t]
    a, b = rng.randint(lo_a, hi_a), rng.randint(lo_b, hi_b)
    item = rng.choice(ITEMS)
    text = rng.choice([
        f"What is {a:,} + {b:,}?",
        f"A trader has {a:,} {item} and gets {b:,} more. "
        f"How many {item} does the trader have now?",
    ])
    return _p(text, a + b,
              "Add the biggest place values first, then the smaller ones.",
              f"{_add_steps(a, b)}. The answer is {a + b:,}.")


def _subtraction(t, rng):
    if t >= 5 and rng.random() < 0.5:
        b, ans = rng.randint(150, 899), rng.randint(300, 999)
        return _p(f"Fill in the missing number:   ? − {b:,} = {ans:,}", ans + b,
                  "Work backwards: add the two numbers you know.",
                  f"The missing number is {ans:,} + {b:,} = {ans + b:,}.")
    if t == 1:
        a = rng.randint(30, 99); b = rng.randint(5, 29)
    elif t == 2:
        a = rng.randint(100, 500); b = rng.randint(15, 99)
    elif t == 3:
        a = rng.randint(400, 999); b = rng.randint(101, a - 50)
    elif t == 4:
        a = rng.choice([rng.randint(2, 9) * 1000, rng.randint(1500, 9999)])
        b = rng.randint(125, 999)
    else:
        a = rng.randint(10000, 50000); b = rng.randint(1200, 9500)
    item = rng.choice(ITEMS)
    text = rng.choice([
        f"What is {a:,} − {b:,}?",
        f"A storehouse holds {a:,} {item}. The Number Thief takes {b:,}. "
        f"How many {item} are left?",
    ])
    return _p(text, a - b,
              "Take away one place value at a time. You can check by adding back.",
              f"{_sub_steps(a, b)}. The answer is {a - b:,}.")


def _multiplication(t, rng):
    top = config.TIMES_TABLE_MAX
    if t == 1:
        a, b = rng.choice([2, 5, 10]), rng.randint(1, 10)
    elif t == 2:
        a, b = rng.randint(2, 10), rng.randint(2, 10)
    elif t == 3:
        a, b = rng.randint(6, top), rng.randint(6, top)
        if rng.random() < 0.3:
            return _p(f"Fill in the missing number:   {a} × ? = {a * b}", b,
                      f"Count by {a}s until you reach {a * b}.",
                      f"{a} × {b} = {a * b}, so the missing number is {b}.")
    elif t == 4:
        a, b = rng.randint(12, 99), rng.randint(3, 9)
    else:
        if rng.random() < 0.5:
            a, b = rng.randint(101, 999), rng.randint(3, 9)
            return _p(f"What is {a} × {b}?", a * b,
                      f"Split {a} into hundreds, tens and ones. "
                      f"Multiply each part by {b}, then add.",
                      _mul_steps(a, b) + ".")
        a, b = rng.randint(11, 40), rng.randint(11, 30)
        return _p(f"What is {a} × {b}?", a * b,
                  f"Split {b} into tens and ones, multiply each part by {a}, then add.",
                  _mul_steps(b, a) + ".")
    if t <= 3:
        if rng.random() < 0.5:
            a, b = b, a
        item = rng.choice(ITEMS)
        text = rng.choice([
            f"What is {a} × {b}?",
            f"There are {a} carts with {b} {item} in each. How many {item} in all?",
        ])
        return _p(text, a * b,
                  f"Count by {max(a, b)}s, {min(a, b)} times.",
                  f"{a} × {b} = {a * b}.")
    return _p(f"What is {a} × {b}?", a * b,
              f"Split {a} into tens and ones, multiply each part by {b}, then add.",
              _mul_steps(a, b) + ".")


def _remainder_q(n, d, item, rng):
    q, rem = divmod(n, d)
    hint = f"Find the biggest multiple of {d} that fits in {n:,}."
    if rng.random() < 0.5:
        return _p(f"{n:,} {item} are packed into boxes of {d}. "
                  f"How many {item} are LEFT OVER?", rem, hint,
                  f"{d} × {q} = {d * q:,}. That leaves {n:,} − {d * q:,} = {rem} left over.")
    return _p(f"{n:,} {item} are packed into boxes of {d}. "
              f"How many FULL boxes are there?", q, hint,
              f"{d} × {q} = {d * q:,}, and {d} × {q + 1} = {d * (q + 1):,} is too big. "
              f"So there are {q} full boxes (with {rem} left over).")


def _division(t, rng):
    top = config.TIMES_TABLE_MAX
    item = rng.choice(ITEMS)
    if t == 1:
        d, q = rng.choice([2, 5, 10]), rng.randint(1, 10)
    elif t == 2:
        d, q = rng.randint(2, 10), rng.randint(2, 10)
    elif t == 3:
        if rng.random() < 0.5:
            d, q = rng.randint(6, top), rng.randint(6, top)
        else:
            d = rng.randint(3, 9)
            return _remainder_q(d * rng.randint(4, 11) + rng.randint(1, d - 1),
                                d, item, rng)
    elif t == 4:
        d = rng.randint(3, 9)
        if rng.random() < 0.3:
            return _remainder_q(d * rng.randint(12, 30) + rng.randint(1, d - 1),
                                d, item, rng)
        q = rng.randint(12, 40)
    else:
        pick = rng.random()
        if pick < 0.25:
            d, q = rng.randint(4, top), rng.randint(11, 25)
            return _p(f"Fill in the missing number:   ? ÷ {d} = {q}", d * q,
                      "Work backwards: multiply the two numbers you know.",
                      f"The missing number is {q} × {d} = {d * q}.")
        d = rng.randint(3, 9)
        if pick < 0.5:
            return _remainder_q(d * rng.randint(40, 150) + rng.randint(1, d - 1),
                                d, item, rng)
        q = rng.randint(101, 450)
    n = d * q
    text = rng.choice([
        f"What is {n:,} ÷ {d}?",
        f"{n:,} {item} are shared equally among {d} villagers. "
        f"How many does each villager get?",
    ])
    if q >= 100:
        hint = (f"Take out easy groups of {d}. Start with hundreds: "
                f"how many hundreds of {d}s fit in {n:,}?")
    elif q > 12:
        hint = (f"Take out easy groups of {d}. Start with tens: {d} × 10 = {d * 10}. "
                f"How many tens fit in {n:,}?")
    else:
        hint = f"Think: {d} times what number makes {n:,}?"
    return _p(text, q, hint, _div_steps(n, d) + ".")


def _fractions(t, rng):
    if t == 1:
        if rng.random() < 0.5:
            n = rng.choice([4, 6, 8, 10])
            k = rng.randint(1, n - 1)
            return _p(f"A pie is cut into {n} equal slices. "
                      f"{k} {'slice is' if k == 1 else 'slices are'} eaten. "
                      f"What fraction of the pie was eaten?", Fraction(k, n),
                      "Top number: slices eaten. Bottom number: slices in the whole pie.",
                      f"{k} out of {n} slices: the fraction is {k}/{n}"
                      + (f" (which is the same as {fmt(Fraction(k, n))})."
                         if fmt(Fraction(k, n)) != f"{k}/{n}" else "."),
                      kind="fraction")
        d = rng.choice([4, 5, 6, 8, 10])
        a, b = rng.sample(range(1, d), 2)
        big = max(a, b)
        return _p("Which fraction is bigger?", f"{big}/{d}",
                  "The pieces are the same size. Which one has more pieces?",
                  f"Both are cut into {d} pieces, and {big} pieces is more than "
                  f"{min(a, b)} pieces. So {big}/{d} is bigger.",
                  kind="choice", choices=[f"{a}/{d}", f"{b}/{d}"])
    if t == 2:
        if rng.random() < 0.5:
            n, d = rng.choice([(1, 2), (1, 3), (2, 3), (1, 4), (3, 4), (1, 5), (2, 5)])
            m = rng.randint(2, 5)
            return _p(f"Fill in the missing number:   {n}/{d} = ?/{d * m}", n * m,
                      f"The bottom was multiplied by {m}. Do the same to the top.",
                      f"{d} × {m} = {d * m}, so multiply the top by {m} too: "
                      f"{n} × {m} = {n * m}. So {n}/{d} = {n * m}/{d * m}.")
        n = rng.choice([1, 1, 2, 3])
        d1, d2 = rng.sample([d for d in (3, 4, 5, 6, 8, 10) if d > n], 2)
        small_d = min(d1, d2)
        return _p("Which fraction is bigger?", f"{n}/{small_d}",
                  "Cutting a pie into MORE pieces makes each piece smaller.",
                  f"Pieces of size 1/{small_d} are bigger than pieces of size "
                  f"1/{max(d1, d2)}, so {n}/{small_d} is bigger.",
                  kind="choice", choices=[f"{n}/{d1}", f"{n}/{d2}"])
    if t == 3:
        d = rng.choice([5, 6, 8, 10, 12])
        if rng.random() < 0.5:
            a = rng.randint(1, d - 2)
            b = rng.randint(1, d - 1 - a)
            ans = Fraction(a + b, d)
            return _p(f"What is {a}/{d} + {b}/{d}?", ans,
                      "The pieces are the same size, so just add the top numbers.",
                      f"{a} + {b} = {a + b}, so the answer is {a + b}/{d}"
                      + (f" (which is the same as {fmt(ans)})." if fmt(ans) != f"{a + b}/{d}" else "."),
                      kind="fraction")
        a = rng.randint(2, d - 1)
        b = rng.randint(1, a - 1)
        ans = Fraction(a - b, d)
        return _p(f"What is {a}/{d} − {b}/{d}?", ans,
                  "The pieces are the same size, so just subtract the top numbers.",
                  f"{a} − {b} = {a - b}, so the answer is {a - b}/{d}"
                  + (f" (which is the same as {fmt(ans)})." if fmt(ans) != f"{a - b}/{d}" else "."),
                  kind="fraction")
    if t == 4:
        if rng.random() < 0.5:
            d = rng.choice([2, 3, 4, 5, 6, 8])
            n = rng.randint(1, d - 1)
            each = rng.randint(2, 9)
            whole = d * each
            return _p(f"What is {n}/{d} of {whole}?", n * each,
                      f"First split {whole} into {d} equal groups.",
                      f"{whole} ÷ {d} = {each} in each group. "
                      f"Take {n} of the groups: {n} × {each} = {n * each}.")
        pool = [(1, 2), (1, 3), (2, 3), (1, 4), (3, 4), (2, 5), (3, 5), (1, 6), (5, 6),
                (3, 8), (5, 8), (7, 8), (3, 10), (7, 10), (5, 12), (7, 12)]
        while True:
            (a, b), (c, d) = rng.sample(pool, 2)
            low = math.lcm(b, d)
            if b != d and low <= 12 and Fraction(a, b) != Fraction(c, d):
                break
        big = f"{a}/{b}" if Fraction(a, b) > Fraction(c, d) else f"{c}/{d}"
        return _p("Which fraction is bigger?", big,
                  f"Change the fractions so both have {low} as the bottom number.",
                  f"Use {low} as the bottom number: {a}/{b} = {a * low // b}/{low} and "
                  f"{c}/{d} = {c * low // d}/{low}. So {big} is bigger.",
                  kind="choice", choices=[f"{a}/{b}", f"{c}/{d}"])
    # tier 5
    pick = rng.randint(1, 3)
    if pick == 1:
        d1 = rng.choice([2, 3, 4, 5])
        m = rng.choice([2, 3])
        d2 = d1 * m
        a = rng.randint(1, d1 - 1)
        b = rng.randint(1, d2 - 1 - a * m) if d2 - 1 - a * m >= 1 else 1
        ans = Fraction(a, d1) + Fraction(b, d2)
        return _p(f"What is {a}/{d1} + {b}/{d2}?", ans,
                  f"Change {a}/{d1} so its bottom number is {d2}.",
                  f"{a}/{d1} = {a * m}/{d2}. Then {a * m}/{d2} + {b}/{d2} = "
                  f"{a * m + b}/{d2}"
                  + (f" (which is the same as {fmt(ans)})." if fmt(ans) != f"{a * m + b}/{d2}" else "."),
                  kind="fraction")
    if pick == 2:
        d = rng.choice([3, 4, 5, 8])
        n = rng.randint(1, d - 1)
        k = rng.randint(2, 6)
        ans = Fraction(k * n, d)
        return _p(f"What is {k} × {n}/{d}?", ans,
                  f"It means {n}/{d} added {k} times. Multiply the top number by {k}.",
                  f"{k} × {n} = {k * n}, so the answer is {k * n}/{d}"
                  + (f" (which is the same as {fmt(ans)})." if fmt(ans) != f"{k * n}/{d}" else "."),
                  kind="fraction")
    d = rng.choice([4, 5, 6, 8])
    a, b = rng.randint(1, d - 1), rng.randint(1, d - 1)
    w1, w2 = rng.randint(1, 4), rng.randint(1, 4)
    ans = w1 + w2 + Fraction(a + b, d)
    extra = ""
    if a + b >= d:
        extra = (f" {a + b}/{d} is a whole or more: it equals "
                 f"{fmt(Fraction(a + b, d))}, so add that to {w1 + w2}.")
    return _p(f"What is {w1} {a}/{d} + {w2} {b}/{d}?", ans,
              "Add the whole numbers first, then add the fractions. "
              "If the fraction part is bigger than 1, trade it for another whole.",
              f"Wholes: {w1} + {w2} = {w1 + w2}. Fractions: {a}/{d} + {b}/{d} = "
              f"{a + b}/{d}.{extra} Together that is {fmt(ans)}.",
              kind="fraction")


def _area_perimeter(t, rng):
    u = rng.choice(UNITS)
    place = rng.choice(["garden", "castle floor", "courtyard", "banner", "stable"])
    if t <= 2:
        lo, hi = (2, 6) if t == 1 else (3, 12)
        w = rng.randint(lo, hi - 1)
        l = rng.randint(w + 1, hi + (3 if t == 1 else 0))
        if rng.random() < 0.5:
            return _p(f"A rectangular {place} is {l} {u} long and {w} {u} wide. "
                      f"What is its PERIMETER (the distance all the way around), in {u}?",
                      2 * (l + w),
                      "Add all four sides: two long sides and two short sides.",
                      f"{l} + {w} + {l} + {w} = {2 * (l + w)} {u}.")
        return _p(f"A rectangular {place} is {l} {u} long and {w} {u} wide. "
                  f"What is its AREA (the space inside), in square {u}?", l * w,
                  "Area of a rectangle = length × width.",
                  f"{l} × {w} = {l * w} square {u}.")
    if t == 3:
        if rng.random() < 0.5:
            s = rng.randint(3, 12)
            return _p(f"A square {place} has a perimeter of {4 * s} {u}. "
                      f"How long is ONE side?", s,
                      "A square has 4 equal sides.",
                      f"{4 * s} ÷ 4 = {s} {u} for each side.")
        w = rng.randint(3, 9)
        l = rng.randint(w + 1, 12)
        return _p(f"A rectangular {place} has an area of {l * w} square {u}. "
                  f"It is {w} {u} wide. How long is it?", l,
                  f"Area = length × width. What times {w} makes {l * w}?",
                  f"{l * w} ÷ {w} = {l} {u}.")
    if t == 4:
        if rng.random() < 0.5:
            w = rng.randint(3, 10)
            l = rng.randint(w + 1, 16)
            per = 2 * (l + w)
            return _p(f"A rectangular {place} has a perimeter of {per} {u}. "
                      f"It is {l} {u} long. How wide is it?", w,
                      "Take away the two long sides, then split what is left in half.",
                      f"Two long sides: {l} + {l} = {2 * l}. Left over: {per} − {2 * l} = "
                      f"{2 * w}. Half of that is {w} {u}.")
        a, b, c, d = rng.randint(3, 9), rng.randint(2, 6), rng.randint(2, 6), rng.randint(2, 5)
        return _p(f"A castle hall is made of two rectangles joined together. "
                  f"One is {a} by {b} {u}. The other is {c} by {d} {u}. "
                  f"What is the TOTAL area, in square {u}?", a * b + c * d,
                  "Find the area of each rectangle, then add them.",
                  f"{a} × {b} = {a * b} and {c} × {d} = {c * d}. "
                  f"{a * b} + {c * d} = {a * b + c * d} square {u}.")
    pick = rng.randint(1, 3)
    if pick == 1:
        w = rng.randint(3, 9)
        l = rng.randint(w + 1, 14)
        per = 2 * (l + w)
        return _p(f"A rectangular {place} has a perimeter of {per} {u} and is "
                  f"{l} {u} long. What is its AREA, in square {u}?", l * w,
                  "First find the width from the perimeter. Then area = length × width.",
                  f"Two long sides use {2 * l}. {per} − {2 * l} = {2 * w}, so the width "
                  f"is {w}. Area: {l} × {w} = {l * w} square {u}.")
    if pick == 2:
        s = rng.randint(4, 10)
        return _p(f"A square {place} has an area of {s * s} square {u}. "
                  f"What is its PERIMETER, in {u}?", 4 * s,
                  "What number times itself makes the area? That is the side.",
                  f"{s} × {s} = {s * s}, so each side is {s}. Perimeter: 4 × {s} = {4 * s} {u}.")
    w = rng.randint(3, 9)
    l = rng.randint(w + 1, 12)
    cost = rng.randint(2, 5)
    per = 2 * (l + w)
    return _p(f"A rectangular {place} is {l} {u} long and {w} {u} wide. A fence "
              f"around it costs {cost} coins for each "
              f"{ {'feet': 'foot', 'meters': 'meter'}[u] }. "
              f"How many coins does the whole fence cost?", per * cost,
              "First find the perimeter. Then multiply by the cost.",
              f"Perimeter: {l} + {w} + {l} + {w} = {per}. Cost: {per} × {cost} = {per * cost} coins.")


def _two_step(t, rng):
    item = rng.choice(ITEMS)
    if t == 1:
        a, b = rng.randint(10, 40), rng.randint(5, 30)
        c = rng.randint(3, a + b - 2)
        return _p(f"Mira had {a} {item}. She found {b} more, then gave away {c}. "
                  f"How many {item} does she have now?", a + b - c,
                  "Step 1: add what she found. Step 2: subtract what she gave away.",
                  f"{a} + {b} = {a + b}, then {a + b} − {c} = {a + b - c}.")
    if t == 2:
        a, b, c = rng.randint(3, 9), rng.randint(4, 10), rng.randint(3, 20)
        return _p(f"A baker fills {a} trays with {b} buns each, and bakes {c} extra "
                  f"buns. How many buns in all?", a * b + c,
                  "Step 1: multiply trays by buns. Step 2: add the extras.",
                  f"{a} × {b} = {a * b}, then {a * b} + {c} = {a * b + c}.")
    if t == 3:
        if rng.random() < 0.5:
            a, b = rng.randint(4, 9), rng.randint(6, 12)
            c = rng.randint(5, a * b - 5)
            return _p(f"A knight has {a} bags with {b} {item} in each. "
                      f"He gives away {c} of them. How many are left?", a * b - c,
                      "Step 1: multiply to find the total. Step 2: subtract what he gave away.",
                      f"{a} × {b} = {a * b}, then {a * b} − {c} = {a * b - c}.")
        a, b, c = rng.randint(3, 12), rng.randint(3, 12), rng.randint(3, 8)
        return _p(f"{a} girls and {b} boys each get {c} stickers. "
                  f"How many stickers are handed out?", (a + b) * c,
                  "Step 1: add to find how many children. Step 2: multiply by the stickers.",
                  f"{a} + {b} = {a + b} children, then {a + b} × {c} = {(a + b) * c}.")
    if t == 4:
        if rng.random() < 0.5:
            c, a, k = rng.randint(2, 6), rng.randint(2, 6), rng.randint(2, 6)
            b = c * k
            return _p(f"There are {a} crates with {b} candles in each. The candles "
                      f"are shared equally among {c} towers. "
                      f"How many candles does each tower get?", a * k,
                      "Step 1: multiply to find all the candles. Step 2: divide by the towers.",
                      f"{a} × {b} = {a * b} candles, then {a * b} ÷ {c} = {a * k}.")
        a, b, c, k = rng.randint(2, 6), rng.randint(3, 9), rng.randint(2, 6), rng.randint(3, 10)
        total = a * b + c * k
        return _p(f"Tom has {total} coins. He buys {a} toys that cost {b} coins each, "
                  f"then shares the rest equally among {c} friends. "
                  f"How many coins does each friend get?", k,
                  "Find the cost of the toys, subtract it, then divide what is left.",
                  f"Toys: {a} × {b} = {a * b}. Left: {total} − {a * b} = {c * k}. "
                  f"Each friend: {c * k} ÷ {c} = {k}.")
    if rng.random() < 0.5:
        while True:
            d, m = rng.randint(3, 8), rng.randint(6, 15)
            a, b = rng.randint(3, 9), rng.randint(4, 9)
            c = d * m - a * b
            if c > 0:
                break
        return _p(f"{a} knights each carry {b} arrows. They find {c} more arrows, "
                  f"then split ALL the arrows equally into {d} wagons. "
                  f"How many arrows go in each wagon?", m,
                  "Three steps: multiply, then add, then divide.",
                  f"{a} × {b} = {a * b}. {a * b} + {c} = {d * m}. {d * m} ÷ {d} = {m}.")
    while True:
        n, d = rng.randint(30, 99), rng.randint(4, 9)
        if n % d:
            break
    cost = rng.randint(2, 6)
    boats = n // d + 1
    return _p(f"{n} travelers must cross a lake. Each boat holds {d} travelers and "
              f"costs {cost} coins. Nobody can be left behind! "
              f"How many coins do all the boats cost?", boats * cost,
              "Find how many boats are needed. Leftover travelers still need a boat!",
              f"{d} × {n // d} = {d * (n // d)}, so {n // d} boats leave {n % d} "
              f"travelers behind. They need {boats} boats. {boats} × {cost} = "
              f"{boats * cost} coins.")


_GENERATORS = {
    "addition": _addition,
    "subtraction": _subtraction,
    "multiplication": _multiplication,
    "division": _division,
    "fractions": _fractions,
    "area_perimeter": _area_perimeter,
    "two_step": _two_step,
}


def generate(topic: str, tier: int, rng: random.Random | None = None) -> Question:
    rng = rng or random
    tier = max(1, min(5, tier))
    d = _GENERATORS[topic](tier, rng)
    if not isinstance(d["answer"], str):
        d["answer"] = Fraction(d["answer"])
    return Question(topic=topic, tier=tier, **d)
