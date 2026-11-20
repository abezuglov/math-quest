"""4th grade: times tables 2-10 and dividing with place value (NC.4.NBT.6:
up to three-digit dividends, one-digit divisors)."""
import os
import random
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import curriculum as cu  # noqa: E402
import pictures  # noqa: E402


def every_question(topic_id, n=80):
    rng = random.Random(3)
    topic = cu.grade("4").topics[topic_id]
    for tpl in topic.templates:
        for level in tpl.levels:
            for _ in range(n):
                yield level, cu.build(tpl, topic_id, level, rng)


def test_both_topics_are_on_the_map_and_added_at_the_end():
    g = cu.grade("4")
    assert list(g.topics)[-2:] == ["g4_times_table", "g4_div_place"]
    by_key = {r["key"]: r["topics"] for r in g.regions}
    assert "g4_times_table" in by_key["mines"]
    assert "g4_div_place" in by_key["docks"]


def test_times_table_facts_stay_within_2_to_10():
    for level, q in every_question("g4_times_table"):
        for a, b in re.findall(r"(\d+) × (\d+)", q.text):
            assert 2 <= int(a) <= 10 and 2 <= int(b) <= 10, q.text
        m = re.fullmatch(r"(\d+) × (\d+) = \?", q.text)
        if m and q.kind == "number":
            assert int(q.answer) == int(m[1]) * int(m[2])
            if level == 1:
                assert {2, 5, 10} & {int(m[1]), int(m[2])}, q.text


def test_division_uses_three_digit_dividends_and_one_digit_divisors():
    for _, q in every_question("g4_div_place"):
        for n, d in re.findall(r"(\d[\d,]*) ÷ (\d+)", q.text):
            assert int(n.replace(",", "")) <= 999 and 2 <= int(d) <= 9, q.text


def test_expanded_parts_add_up_and_each_divides_evenly():
    seen = 0
    for _, q in every_question("g4_div_place"):
        m = re.match(r"(\d+) = ([\d + ]+), and (\d) divides each part evenly", q.text)
        if not m:
            continue
        n, d = int(m[1]), int(m[3])
        parts = [int(x) for x in m[2].split(" + ")]
        assert sum(parts) == n and all(p % d == 0 for p in parts), q.text
        assert int(q.answer) * d == n
        seen += 1
    assert seen


def test_remainder_questions_are_consistent():
    for _, q in every_question("g4_div_place"):
        m = re.fullmatch(r"(\d+) ÷ (\d) = (\d+|\?) R (\d+|\?)", q.text)
        if not m:
            continue
        n, d = int(m[1]), int(m[2])
        quot = int(q.answer) if m[3] == "?" else int(m[3])
        rem = int(q.answer) if m[4] == "?" else int(m[4])
        assert quot * d + rem == n and 0 < rem < d, q.text


@pytest.mark.parametrize("n", [100, 104, 536, 999])
def test_place_chart_draws_one_disk_per_unit(n):
    svg = pictures.place_chart(n)
    assert svg.count("<circle") == sum(int(ch) for ch in str(n))
    assert "Hundreds" in svg and "Ones" in svg
