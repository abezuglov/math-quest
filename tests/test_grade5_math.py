"""5th grade: re-check the tricky answers from the question text alone.

check_all() makes sure every answer is well formed. These tests go further for
the templates where a wrong formula would still look fine (rounding,
remainders, money, mixed numbers): they read the numbers back out of the text
and work the answer out a second, independent way."""
import math
import os
import random
import re
import sys
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import curriculum as cu  # noqa: E402

GRADE = cu.grade("5")


def _num(s):
    return Decimal(s.replace(",", ""))


def _round(m):
    places = {"whole number": "1", "tenth": "0.1", "hundredth": "0.01"}[m[2]]
    return Fraction(_num(m[1]).quantize(Decimal(places), rounding=ROUND_HALF_UP))


def _mixed(w, n, d):
    return int(w) + Fraction(int(n), int(d))


CHECKS = {
    "rounding": (r"Round ([\d.,]+) to the nearest (whole number|tenth|hundredth)\.", _round),
    "full cartons": (r"([\d,]+) eggs are packed in cartons of (\d+)\.",
                     lambda m: int(_num(m[1])) // int(m[2])),
    "vans needed": (r"([\d,]+) people go on a trip\. Each van holds (\d+) people\.",
                    lambda m: math.ceil(int(_num(m[1])) / int(m[2]))),
    "change from $20": (r"book for \$([\d.]+) and a pen for \$([\d.]+), and pays with a \$20 bill",
                        lambda m: Fraction(Decimal(20) - _num(m[1]) - _num(m[2]))),
    "mixed subtraction": (r"^(\d+) (\d+)/(\d+) − (\d+) (\d+)/(\d+) = \?$",
                          lambda m: _mixed(*m.groups()[:3]) - _mixed(*m.groups()[3:])),
    "mixed addition": (r"^(\d+) (\d+)/(\d+) \+ (\d+) (\d+)/(\d+) = \?$",
                       lambda m: _mixed(*m.groups()[:3]) + _mixed(*m.groups()[3:])),
    "decimal ÷ power of ten": (r"^([\d.,]+) ÷ (10|100|1,000) = \?$",
                               lambda m: Fraction(_num(m[1]) / _num(m[2]))),
    "decimal × decimal": (r"^(\d\.\d+) × (\d+\.\d+) = \?$",
                          lambda m: Fraction(_num(m[1]) * _num(m[2]))),
}


def test_tricky_answers_match_an_independent_calculation():
    rng = random.Random(5)
    seen = dict.fromkeys(CHECKS, 0)
    for topic in GRADE.topics.values():
        for tpl in topic.templates:
            for level in tpl.levels:
                for _ in range(80):
                    q = cu.build(tpl, topic.id, level, rng)
                    for name, (pattern, solve) in CHECKS.items():
                        m = re.search(pattern, q.text)
                        if m:
                            seen[name] += 1
                            assert q.answer == solve(m), (name, q.text, q.answer)
    assert all(seen.values()), seen       # every check found its questions


def test_decimal_answers_stay_within_thousandths_and_are_never_negative():
    rng = random.Random(9)
    for topic in GRADE.topics.values():
        for tpl in topic.templates:
            if tpl.kind not in ("decimal", "fraction", "number"):
                continue
            for level in tpl.levels:
                for _ in range(40):
                    q = cu.build(tpl, topic.id, level, rng)
                    assert q.answer >= 0, q.text
                    if tpl.kind == "decimal":
                        assert (q.answer * 1000).denominator == 1, (q.text, q.answer)


def test_every_choice_question_has_exactly_one_right_answer():
    rng = random.Random(2)
    for topic in GRADE.topics.values():
        for tpl in topic.templates:
            if tpl.kind != "choice":
                continue
            for level in tpl.levels:
                for _ in range(60):
                    q = cu.build(tpl, topic.id, level, rng)
                    assert q.choices.count(q.answer) == 1, (q.text, q.choices)
