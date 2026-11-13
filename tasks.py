"""Hands-on tasks: one per region. Pure Python (no Streamlit).

Each task is something to DO (tap, slide, pick) instead of typing a number.
The screen in app.py reads `kind` and `data` to draw the controls, then sends
the child's value to `check`.

Value passed to check(), by kind:
  coins      list of the chosen bag numbers
  multiples  list of the chosen numbers
  share      (each, left_over)
  shade      number of shaded parts
  garden     (length, width)
  ledger     index of the line with the mistake
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from itertools import combinations

TASK_TOPIC = {
    "coins": "addition",
    "multiples": "multiplication",
    "share": "division",
    "shade": "fractions",
    "garden": "area_perimeter",
    "ledger": "two_step",
}


@dataclass
class Task:
    kind: str
    topic: str
    tier: int
    prompt: str
    hint: str
    solution: str            # shown after a miss: the answer in words
    explanation: str
    data: dict = field(default_factory=dict)


# --------------------------------------------------------------------------
def _coins(t, rng):
    lo, hi, step = {1: (5, 30, 5), 2: (11, 60, 1), 3: (25, 150, 5),
                    4: (40, 300, 1), 5: (120, 900, 1)}[t]
    n_bags = 5 if t <= 2 else 6
    while True:
        bags = sorted({rng.randrange(lo, hi + 1, step) for _ in range(n_bags)})
        if len(bags) != n_bags:
            continue
        size = rng.choice([2, 3]) if t >= 2 else 2
        chosen = sorted(rng.sample(bags, size))
        target = sum(chosen)
        # Only one set of bags may make the price, so the task has one answer.
        ways = [c for k in range(1, n_bags + 1) for c in combinations(bags, k)
                if sum(c) == target]
        if len(ways) == 1:
            break
    rng.shuffle(bags)
    plus = " + ".join(f"{c:,}" for c in chosen)
    return Task(
        "coins", "addition", t,
        f"Peddler Pim's price is exactly {target:,} coins. Tap the coin bags that "
        f"add up to {target:,}. No more, no less!",
        "Pick one bag, then work out how much is still missing. Is there a bag "
        "(or two) that makes up the rest? If not, start with a different bag.",
        "the bags " + ", ".join(f"{c:,}" for c in chosen[:-1]) + f" and {chosen[-1]:,}",
        f"{plus} = {target:,}.",
        {"bags": bags, "target": target, "answer": chosen})


def _multiples(t, rng):
    n = rng.choice({1: [2, 5, 10], 2: [3, 4, 5], 3: [6, 7, 8, 9],
                    4: [7, 8, 9, 11, 12], 5: [12, 15, 25]}[t])
    top = 12 if t <= 4 else 9
    good = sorted(rng.sample([n * k for k in range(2, top + 1)], 3 if t <= 2 else 4))
    bad = set()
    while len(bad) < 8 - len(good):
        x = n * rng.randint(2, top) + rng.randint(1, n - 1)
        if x % n:
            bad.add(x)
    numbers = good + sorted(bad)
    rng.shuffle(numbers)
    facts = ", ".join(f"{n} × {g // n} = {g}" for g in good)
    return Task(
        "multiples", "multiplication", t,
        f"The bats are hiding numbers! Tap every number that is a multiple of {n}.",
        f"Count by {n}s: {n}, {2 * n}, {3 * n}... Which bats do you land on?",
        ", ".join(str(g) for g in good),
        f"{facts}. The others are not multiples of {n}.",
        {"n": n, "numbers": numbers, "answer": good})


def _share(t, rng):
    d = rng.randint(2, 4) if t <= 2 else rng.randint(3, 6)
    q = {1: rng.randint(2, 5), 2: rng.randint(3, 8), 3: rng.randint(4, 9),
         4: rng.randint(6, 12), 5: rng.randint(8, 15)}[t]
    r = 0 if t == 1 else rng.randint(1, d - 1)
    n = d * q + r
    left = (f" and {r} left over" if r else " and nothing left over")
    return Task(
        "share", "division", t,
        f"Share {n} crates fairly among {d} boats. Every boat must get the same "
        f"number, and as many as possible. Move the slider, then count what is left.",
        f"Find the biggest multiple of {d} that fits in {n}.",
        f"{q} crates on each boat{left}",
        f"{d} × {q} = {d * q}. That leaves {n} − {d * q} = {r} left over."
        if r else f"{d} × {q} = {n}, so each boat gets {q} and nothing is left over.",
        {"n": n, "boats": d, "each": q, "left": r,
         "max_each": max(q + 4, 8)})


def _shade(t, rng):
    pool = {1: [(1, 2)], 2: [(1, 2), (1, 3), (1, 4)],
            3: [(1, 3), (2, 3), (1, 4), (3, 4)],
            4: [(2, 3), (3, 4), (2, 5), (3, 5)],
            5: [(2, 3), (3, 4), (2, 5), (3, 5), (5, 6)]}[t]
    a, b = rng.choice(pool)
    m = rng.choice([2, 3] if t <= 3 else [2, 3, 4])
    while b * m > 16:
        m -= 1
    parts = b * m
    return Task(
        "shade", "fractions", t,
        f"Hazel's recipe needs {a}/{b} of the nut loaf. But this loaf is cut "
        f"into {parts} equal pieces. Slide to shade the pieces that make {a}/{b}.",
        f"Look at the two bars. One piece of the top bar is as long as {m} pieces "
        f"of the bottom bar.",
        f"{a * m} pieces",
        f"{b} × {m} = {parts}, so multiply the top by {m} too: {a} × {m} = {a * m}. "
        f"So {a}/{b} = {a * m}/{parts}.",
        {"a": a, "b": b, "parts": parts, "answer": a * m})


def _garden(t, rng):
    hi = {1: 6, 2: 8, 3: 10, 4: 12, 5: 12}[t]
    while True:
        w = rng.randint(2, hi - 1)
        l = rng.randint(w + 1, hi)
        # At tiers 1-2 the area alone must be enough to find the answer.
        if t > 2 or sum(1 for x in range(1, hi + 1)
                        for y in range(1, x + 1) if x * y == l * w) == 1:
            break
    area, per = l * w, 2 * (l + w)
    if t <= 2:
        prompt = (f"Gwen wants a rectangular garden with an AREA of {area} square "
                  f"meters. Each side is at most {hi} meters. "
                  f"Move the sliders to build it.")
        hint = f"Area = length × width. Which two numbers multiply to make {area}?"
    else:
        prompt = (f"Gwen wants a rectangular garden with an AREA of {area} square "
                  f"meters and a fence (PERIMETER) of {per} meters. "
                  f"Move the sliders to build it.")
        hint = (f"Length + width must be half the fence: {per // 2}. "
                f"Which two numbers add to {per // 2} and multiply to {area}?")
    return Task(
        "garden", "area_perimeter", t, prompt, hint,
        f"{l} meters long and {w} meters wide",
        f"{l} × {w} = {area} square meters, and {l} + {w} + {l} + {w} = {per} meters.",
        {"area": area, "per": per, "length": l, "width": w, "max": hi,
         "need_per": t > 2})


def _ledger_line(t, rng):
    """One true line of the ledger: (text, correct_total)."""
    pick = rng.randint(1, 3)
    if t <= 2:
        a, b = rng.randint(12, 60), rng.randint(12, 39)
        if pick == 1:
            return f"{a} + {b}", a + b
        if pick == 2:
            return f"{a + b} − {b}", a
        x, y = rng.randint(2, 9), rng.randint(2, 9)
        return f"{x} × {y}", x * y
    if pick == 1:
        a, b = rng.randint(120, 890), rng.randint(105, 480)
        return f"{a} + {b}", a + b
    if pick == 2:
        x, y = rng.randint(6, 12), rng.randint(6, 12)
        return f"{x} × {y}", x * y
    x, y, c = rng.randint(3, 9), rng.randint(4, 9), rng.randint(11, 60)
    return f"{x} × {y} + {c}", x * y + c


def _ledger(t, rng):
    n_lines = 4 if t <= 3 else 5
    lines, seen = [], set()
    while len(lines) < n_lines:
        text, total = _ledger_line(t, rng)
        if text not in seen:
            seen.add(text)
            lines.append((text, total))
    bad = rng.randrange(n_lines)
    text, total = lines[bad]
    # The story says the royal gold came out ten coins short: the book says ten
    # more than there really was.
    wrong = total + 10
    shown = [(tx, wrong if i == bad else tot) for i, (tx, tot) in enumerate(lines)]
    return Task(
        "ledger", "two_step", t,
        "This is a page of the Great Ledger. One line was added up wrong, long "
        "ago. Check every line and tap the one with the mistake. "
        "You may use paper.",
        "Work out each line yourself, one at a time. Estimating first is a fast "
        "way to spot a line that looks odd.",
        f"line {bad + 1}",
        f"{text} = {total:,}, not {wrong:,}. The other lines are correct.",
        {"lines": shown, "answer": bad, "truth": total})


_MAKERS = {"coins": _coins, "multiples": _multiples, "share": _share,
           "shade": _shade, "garden": _garden, "ledger": _ledger}


def generate(kind: str, tier: int, rng: random.Random | None = None) -> Task:
    rng = rng or random
    return _MAKERS[kind](max(1, min(5, tier)), rng)


def check(task: Task, value) -> bool:
    d = task.data
    try:
        if task.kind in ("coins", "multiples"):
            return sorted(int(v) for v in value) == sorted(d["answer"])
        if task.kind == "share":
            each, left = value
            return int(each) == d["each"] and int(left) == d["left"]
        if task.kind == "shade":
            return int(value) == d["answer"]
        if task.kind == "garden":
            length, width = int(value[0]), int(value[1])   # either way round is fine
            return (length * width == d["area"]
                    and (not d["need_per"] or 2 * (length + width) == d["per"]))
        if task.kind == "ledger":
            return int(value) == d["answer"]
    except (TypeError, ValueError, IndexError):
        return False
    return False


def describe(task: Task, value) -> str:
    """The child's attempt in words, for the feedback screen."""
    try:
        if task.kind in ("coins", "multiples"):
            picked = sorted(int(v) for v in value)
            if not picked:
                return "nothing"
            text = ", ".join(f"{p:,}" for p in picked)
            if task.kind == "coins":
                text += f" (that makes {sum(picked):,})"
            return text
        if task.kind == "share":
            return f"{int(value[0])} on each boat and {int(value[1])} left over"
        if task.kind == "shade":
            return f"{int(value)} pieces"
        if task.kind == "garden":
            l, w = int(value[0]), int(value[1])
            return (f"{l} by {w} (area {l * w}, fence {2 * (l + w)})")
        if task.kind == "ledger":
            return f"line {int(value) + 1}"
    except (TypeError, ValueError, IndexError):
        pass
    return "that"
