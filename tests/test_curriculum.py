"""The curriculum engine and the content files."""
import os
import random
import sys
from fractions import Fraction

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import curriculum as cu  # noqa: E402
from curriculum import CurriculumError, evaluate, render  # noqa: E402
from questions import ALL_TOPICS, fmt, is_correct, parse_answer  # noqa: E402

GRADES = cu.load_all()


# --------------------------------------------------------------------------
# Content files
# --------------------------------------------------------------------------
def test_every_grade_file_loads_with_six_regions_and_full_level_coverage():
    assert list(GRADES) == [c for c in cu.GRADE_ORDER if c in GRADES]
    assert "4" in GRADES
    seen = set()
    for g in GRADES.values():
        assert [r["key"] for r in g.regions] == list(cu.REGION_KEYS)
        assert g.regions[-1]["final"] and g.regions[-1]["mix"]
        assert not any(r["final"] for r in g.regions[:-1])
        for r in g.regions:
            assert r["topics"] and all(t in g.topics for t in r["topics"])
            assert r["task_topic"] in g.topics
        for tid, topic in g.topics.items():
            assert tid not in seen, f"topic id {tid} appears in two grades"
            seen.add(tid)
            assert topic.label and topic.tip
            for level in cu.LEVELS:
                assert topic.for_level(level), f"{g.source}: {tid} level {level}"


def test_grade_4_keeps_the_old_topics_and_regions():
    import story
    g = GRADES["4"]
    assert list(g.topics) == ALL_TOPICS
    assert all(t.templates[0].generator == tid for tid, t in g.topics.items())
    for mine, old in zip(g.regions, story.REGIONS):
        assert mine["key"] == old["key"] and mine["name"] == old["name"]
        assert mine["gem"] == old["gem"] and mine["topics"] == old["topics"]
        task = next(e["task"] for e in old["encounters"] if e["kind"] == "task")
        assert mine["task"] == task


def test_check_all_finds_no_problems():
    assert cu.check_all(samples=60) == []


def test_generated_questions_are_well_formed():
    rng = random.Random(7)
    for g in GRADES.values():
        for topic in g.topics.values():
            for level in cu.LEVELS:
                for _ in range(20):
                    q = cu.generate(topic, level, rng)
                    assert q.topic == topic.id and q.tier == level
                    assert q.text and q.hint and q.explanation
                    if q.kind == "choice":
                        assert q.answer in q.choices
                        assert 2 <= len(q.choices) <= 4
                    else:
                        assert isinstance(q.answer, Fraction) and q.answer >= 0
                        shown = cu.show_answer(q)
                        assert is_correct(q, parse_answer(shown))
                        if q.kind == "decimal":
                            places = len(shown.partition(".")[2])
                            assert places <= g.decimal_places, (q.text, shown)
                        if q.kind == "number":
                            assert q.answer.denominator == 1


def test_a_broken_file_is_reported_clearly(tmp_path):
    def load(text):
        path = tmp_path / "grade_2.toml"
        path.write_text(text, encoding="utf-8")
        return cu.load_grade(path)

    regions = "".join(
        f'[[region]]\nkey="{k}"\nname="{k}"\ngem="g"\ntopics=["g2_a"]\n'
        + ('mix=true\nfinal=true\n' if k == "peak" else "")
        for k in cu.REGION_KEYS)
    good = (f'grade="2"\n{regions}[[topic]]\nid="g2_a"\nlabel="A"\ntip="t"\n'
            '[[topic.question]]\nvars={a="randint(1,9)"}\ntext="{a}?"\n'
            'answer="a"\nhint="h"\nexplain="{answer}"\n')
    g = load(good)
    assert list(g.topics) == ["g2_a"] and len(g.regions) == 6
    with pytest.raises(CurriculumError, match="level"):
        load(good.replace('vars=', 'levels=[1,2]\nvars='))
    with pytest.raises(CurriculumError, match="unknown key"):
        load(good.replace('hint="h"', 'hint="h"\nhnt="x"'))
    with pytest.raises(CurriculumError, match="regions"):
        load(good.replace('[[region]]\nkey="mines"', '[[region]]\nkey="docks"'))
    with pytest.raises(CurriculumError, match="unknown topics"):
        load(good.replace('topics=["g2_a"]', 'topics=["nope"]', 1))
    with pytest.raises(CurriculumError, match="generator"):
        load(good.replace('vars=', 'generator="nope"\nvars='))
    with pytest.raises(CurriculumError, match="finale"):
        load(good.replace('key="village"', 'key="village"\nfinal=true'))
    bad_math = good.replace('answer="a"', 'answer="a / 2"')
    assert cu.check_template(load(bad_math).topics["g2_a"].templates[0], "g2_a", 10)
    never = good.replace('vars={a="randint(1,9)"}', 'vars={a="randint(1,9)"}\nwhere="a > 20"')
    problems = cu.check_template(load(never).topics["g2_a"].templates[0], "g2_a", 5)
    assert problems and "where" in problems[0]


# --------------------------------------------------------------------------
# The evaluator
# --------------------------------------------------------------------------
@pytest.mark.parametrize("expr", [
    "__import__('os')", "().__class__", "lambda: 1", "open('x')", "2 ** 99999",
    "'abc'.upper()", "a.numerator", "[].append(1)", "x := 3", "print(1)",
    "eval('1')", "globals()", "(1).__class__.__bases__", "10 ** 20 * 10 ** 20",
    "'a' * 10 ** 9", "[0] * 10 ** 9", "range(10 ** 9)", "f'{a}'", "{1: 2}",
    "[x for x in [1]]", "randint(5, 1)", "a is b", "import os",
])
def test_the_evaluator_refuses_dangerous_or_unknown_things(expr):
    with pytest.raises(CurriculumError):
        evaluate(expr, {"a": 2, "b": 3}, random.Random(0))


def test_the_evaluator_does_arithmetic_exactly():
    env = {"a": 7, "b": 2, "L": 3}
    assert evaluate("a + b * 3", env) == 13
    assert evaluate("a / b", env) == Fraction(7, 2)
    assert evaluate("a // b", env) == 3 and evaluate("a % b", env) == 1
    assert evaluate("0.25 + 0.5", env) == Fraction(3, 4)
    assert evaluate("2 ** 10", env) == 1024
    assert evaluate("a if b > 1 else 0", env) == 7
    assert evaluate("[a, b][1]", env) == 2
    assert evaluate("a > b and b > 1", env) is True
    assert evaluate("1 < b < a", env) is True
    assert evaluate("'<' if a < b else '>'", env) == ">"
    assert evaluate("gcd(12, 18) + lcm(4, 6)", env) == 18
    assert evaluate("digit(4372, 100)", env) == 3
    assert evaluate("compare(2, 5) + compare(5, 5) + compare(9, 5)", env) == "<=>"
    assert evaluate("factors(12)", env) == [1, 2, 3, 4, 6, 12]
    assert evaluate("is_prime(13) and not is_prime(15)", env) is True
    assert evaluate("expanded(305)", env) == "300 + 5"
    assert evaluate("time(3, 5)", env) == "3:05"
    assert evaluate("different(1, 2, 3) and not different(1, 2, 1)", env) is True
    assert evaluate("join([1, 2, 3], ' + ')", env) == "1 + 2 + 3"
    assert evaluate("plural(1, 'apple') + ', ' + plural(3, 'apple')", env) == "1 apple, 3 apples"
    assert evaluate(5, env) == 5 and evaluate(0.5, env) == Fraction(1, 2)
    rng = random.Random(1)
    assert all(1 <= evaluate("randint(1, L)", env, rng) <= 3 for _ in range(50))
    assert all(evaluate("randstep(5, 30, 5)", env, rng) % 5 == 0 for _ in range(50))
    assert evaluate("name()", env, rng) in cu.NAMES


def test_render_styles():
    funcs = cu._bind(random.Random(0))
    env = {"n": 1234, "f": Fraction(13, 4), "m": Fraction(325, 100), "k": 3,
           "s": "hi", "ok": True}
    assert render("{n} {n|plain} {k|ordinal} {s} {ok}", env, funcs) == "1,234 1234 3rd hi yes"
    assert render("{f} {f|dec} {m|money} {k|word}", env, funcs) == "3 1/4 3.25 $3.25 three"
    assert render("{n + k} and {'x' if k > 2 else 'y'}", env, funcs) == "1,237 and x"
    with pytest.raises(CurriculumError, match="style"):
        render("{n|nope}", env, funcs)
    with pytest.raises(CurriculumError):
        render("{zzz}", env, funcs)


def test_helpers():
    assert cu.number_word(0) == "zero"
    assert cu.number_word(12) == "twelve"
    assert cu.number_word(40) == "forty"
    assert cu.number_word(345) == "three hundred forty-five"
    assert cu.number_word(1000) == "one thousand"
    assert cu.number_word(21_017) == "twenty-one thousand seventeen"
    assert cu.fmt_decimal(Fraction(13, 4)) == "3.25"
    assert cu.fmt_decimal(Fraction(3, 10)) == "0.3"
    assert cu.fmt_decimal(7) == "7"
    assert cu.fmt_decimal(Fraction(1234567, 1000)) == "1,234.567"
    with pytest.raises(ValueError):
        cu.fmt_decimal(Fraction(1, 3))
    assert cu.fmt_money(Fraction(13, 4)) == "$3.25"
    assert cu.fmt_money(5) == "$5.00"
    assert cu.fmt_money(Fraction(1005, 100)) == "$10.05"
    assert cu.round_to(45, 10) == 50 and cu.round_to(44, 10) == 40
    assert cu.round_to(650, 100) == 700 and cu.round_to(649, 100) == 600
    assert cu.round_to(2500, 1000) == 3000
    assert cu.ordinal(1) == "1st" and cu.ordinal(12) == "12th" and cu.ordinal(23) == "23rd"


def test_show_answer_prints_decimals_as_decimals():
    from questions import Question
    q = Question("t", 1, "x", Fraction(3, 4), "h", "e", kind="decimal")
    assert cu.show_answer(q) == "0.75"
    q.kind = "fraction"
    assert cu.show_answer(q) == "3/4"
    q.kind = "decimal"
    q.answer = Fraction(1, 3)
    assert cu.show_answer(q) == "1/3"              # no short decimal: fall back
    assert cu.show_answer(q, Fraction(5, 2)) == "2.5"


def test_generate_uses_the_old_generators_for_4th_grade():
    import questions
    topic = GRADES["4"].topics["multiplication"]
    q = cu.generate(topic, 3, random.Random(5))
    old = questions.generate("multiplication", 3, random.Random(5))
    assert q.text == old.text and q.answer == old.answer and q.topic == "multiplication"
    assert fmt(q.answer) == fmt(old.answer)
