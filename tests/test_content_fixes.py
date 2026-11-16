"""Content checks for review findings: questions with more than one right
answer, wording that contradicts the picture, and off-grade numbers."""
import os
import random
import re
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import curriculum as cu  # noqa: E402
import story  # noqa: E402
from questions import fmt  # noqa: E402


def questions(grade, topic_id, pattern, n=150):
    """Questions of one topic whose text matches pattern, at every level."""
    rng = random.Random(1)
    topic = cu.grade(grade).topics[topic_id]
    out = []
    for tpl in topic.templates:
        for level in tpl.levels:
            for _ in range(n):
                q = cu.build(tpl, topic_id, level, rng)
                if re.search(pattern, q.text):
                    out.append(q)
    assert out, f"no {topic_id} question matches {pattern!r}"
    return out


def test_simplest_form_does_not_accept_the_unsimplified_fraction():
    for q in questions("3", "g3_equiv", r"simplest form"):
        a, b = map(int, re.search(r"Write (\d+)/(\d+)", q.text).groups())
        assert q.kind == "choice" and f"{a}/{b}" in q.choices, q.text
        assert q.answer == fmt(Fraction(a, b)) != f"{a}/{b}"
    for q in questions("4", "g4_decimals", r"simplest form"):
        k = round(Fraction(re.search(r"Write ([\d.]+)", q.text)[1]) * 100)
        assert q.kind == "choice" and f"{k}/100" in q.choices, q.text
        assert q.answer == fmt(Fraction(k, 100)) != f"{k}/100"


ALSO_CALLED = {"square": {"rectangle", "rhombus", "parallelogram"},
               "rectangle": {"parallelogram"}, "rhombus": {"parallelogram"}}


def test_shape_names_ask_for_the_best_name_when_two_fit():
    for q in questions("3", "g3_quads", r"this shape"):
        if ALSO_CALLED.get(q.answer, set()) & set(q.choices):
            assert "best" in q.text, (q.text, q.answer, q.choices)


def test_3rd_grade_mass_division_stays_within_100():
    for q in questions("3", "g3_mass", r"shared equally into"):
        assert int(q.text.split()[0]) <= 100, q.text


def test_kindergarten_wording_matches_the_story():
    for q in questions("K", "k_add", r"dots\. How many dots"):
        assert "blue" not in q.text, q.text   # dots up to 10 are all drawn red
    for q in questions("K", "k_sub", r"fly away"):
        assert "frogs" not in q.text, q.text
    for q in questions("K", "k_compare", r"fewer.*same"):
        assert "than" in q.text, q.text


def test_a_failing_picture_is_not_also_called_unknown():
    tpl = cu.grade("K").topics["k_add"].templates[0]
    bad = cu.Template(**{**tpl.__dict__, "picture": ["dots", "1", "2", "3", "4"]})
    problems = cu.check_template(bad, "k_add", samples=1)
    assert any("failed" in p for p in problems)
    assert not any("unknown picture" in p for p in problems)


def _places(s):
    return len(s.partition(".")[2])


def test_5th_grade_decimal_division_shows_the_answers_places():
    for q in questions("5", "g5_dec_ops", r"^[\d.]+ ÷ \d = \?$"):
        places = next(p for p in range(4) if (q.answer * 10 ** p).denominator == 1)
        assert _places(q.text.split()[0]) == places, q.text


def test_5th_grade_place_value_number_has_three_decimal_places():
    for q in questions("5", "g5_decimals", r"which digit is in the"):
        assert _places(re.search(r"In ([\d.]+),", q.text)[1]) == 3, q.text


FOURTH_GRADE_WORDS = re.compile(
    r"\btimes \w|in groups|shares|leftovers|split things|how far (around|is it)|perimeter|tiny parts"
    r"|bit\.\.\.|piece of|measure wrong", re.I)


def _lines(region):
    """Story text with the character names taken out (Times Bat may stay)."""
    names = [e["name"].removeprefix("The ") for e in region["encounters"]]
    for e in [region, *region["encounters"]]:
        for line in (e["intro"], e.get("outro") or e.get("win") or ""):
            for name in names:
                line = line.replace(name, "")
            yield line


def test_k_to_2_story_lines_do_not_name_4th_grade_topics():
    for g in ("K", "1", "2"):
        for spec in cu.grade(g).regions:
            for line in _lines(story.build_region(spec)):
                assert not FOURTH_GRADE_WORDS.search(line), (g, spec["key"], line)


def test_region_text_names_its_own_gem():
    gems = {r["gem"] for g in cu.load_all() for r in cu.grade(g).regions}
    for g in cu.load_all():
        for spec in cu.grade(g).regions:
            r = story.build_region(spec)
            for other in gems - {r["gem"]}:
                assert other not in r["intro"] + r["outro"], (g, r["key"], other)


def test_4th_grade_keeps_its_topic_lines():
    regions = {r["key"]: story.build_region(r) for r in cu.grade("4").regions}
    assert "Rocks times rocks" in regions["mines"]["encounters"][5]["intro"]
    assert "EIGHT SHARES" in regions["docks"]["encounters"][6]["intro"]
    assert "bit... by bit" in regions["forest"]["encounters"][6]["intro"]
    assert "area and perimeter" in regions["castle"]["intro"]


def test_the_shade_task_text_matches_the_nut_loaf_everywhere():
    for g in cu.load_all():
        for spec in cu.grade(g).regions:
            for e in story.build_region(spec)["encounters"]:
                if e.get("task") == "shade":
                    assert "nut loaf" in e["intro"] and "garden" not in e["intro"], (g, e)


def test_5th_grade_castle_intro_fits_its_topics():
    spec = next(r for r in cu.grade("5").regions if r["key"] == "castle")
    assert "perimeter" not in story.build_region(spec)["intro"]
