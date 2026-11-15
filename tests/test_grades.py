"""Grades: content files wired into the game, regions, tasks and ranks."""
import os
import random
import sys
from fractions import Fraction

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config  # noqa: E402
import curriculum  # noqa: E402
import story  # noqa: E402
import tasks  # noqa: E402
from engine import RANKS, Game  # noqa: E402
from questions import Question  # noqa: E402
from test_game import auto, enter, play, right  # noqa: E402

GRADES = list(curriculum.load_all())


def test_game_takes_its_topics_and_regions_from_the_grade_file():
    g = Game("Ada", "4", seed=1)
    assert g.grade == "4" and g.content.code == "4"
    assert g.topics == list(curriculum.grade("4").topics)
    assert g.label("fractions") == "Fractions" and "piece" in g.tip("fractions")
    assert g.standard("addition") == "4.NBT.B.4"
    assert [r["key"] for r in g.regions] == list(curriculum.REGION_KEYS)
    assert Game("Ada", grade=4).grade == "4"
    with pytest.raises(KeyError):
        Game("Ada", "9")


def test_region_overrides_and_missing_tasks():
    lux = Game("Bo", "4").regions[1]["encounters"][1]
    assert lux["name"] == "Lampkeeper Lux" and "multiply" in lux["intro"]
    assert "multiply" not in story.REGION_BY_KEY["mines"]["encounters"][1]["intro"]

    spec = {"key": "mines", "name": "Counting Caves", "gem": "Gem of Dots",
            "topics": ["k_count"], "mix": False, "final": False, "task": None,
            "task_topic": "k_count", "task_levels": [1, 2], "intro": "Dark!",
            "encounter": [{"slot": 0, "name": "Mole", "emoji": "🐹"},
                          {"slot": 99, "name": "nobody"}]}
    r = story.build_region(spec)
    assert r["name"] == "Counting Caves" and r["gem"] == "Gem of Dots"
    assert r["intro"] == "Dark!" and r["outro"] == story.REGION_BY_KEY["mines"]["outro"]
    assert r["emoji"] == "⛏️" and r["topics"] == ["k_count"]
    assert [e["kind"] for e in r["encounters"]] == ["riddle", "riddle", "fight", "riddle",
                                                     "fight", "boss"]
    assert r["encounters"][0]["name"] == "Mole" and r["encounters"][0]["emoji"] == "🐹"
    assert r["encounters"][0]["intro"] == story.REGION_BY_KEY["mines"]["encounters"][0]["intro"]
    # the shared story is not changed by building a region
    assert story.REGION_BY_KEY["mines"]["encounters"][0]["name"] == "Digger Dot"
    with_task = story.build_region({**spec, "task": "coins"})
    task = next(e for e in with_task["encounters"] if e["kind"] == "task")
    assert task["task"] == "coins" and task["name"] == "The Echo Cave"


def test_a_task_counts_for_the_regions_task_topic_and_respects_task_levels(monkeypatch):
    g = Game("Cy", "4", seed=15)
    region = g.regions[0]
    monkeypatch.setitem(region, "task_topic", "subtraction")
    monkeypatch.setitem(region, "task_levels", [1, 1])
    g.tiers["subtraction"] = 4
    enter(g)
    while g.phase != "task":
        g.submit(right(g)) if g.phase == "question" else auto(g)
    assert g.task.topic == "subtraction" and g.task.tier == 1
    asked = g.stats["subtraction"][1]
    g.submit_task(g.task.data["answer"])
    assert g.stats["subtraction"][1] == asked + 1


def test_the_gentle_ledger_stays_within_20():
    rng = random.Random(3)
    for tier in (1, 2, 3, 4, 5):
        for _ in range(100):
            t = tasks.generate("ledger", tier, rng, topic="k_add", gentle=True)
            assert t.topic == "k_add" and len(t.data["lines"]) == 3
            for text, shown in t.data["lines"]:
                truth = eval(text.replace("−", "-"))
                assert 0 < truth <= 20
                assert shown == truth or shown == truth + 10
            assert tasks.check(t, t.data["answer"])
    hard = tasks.generate("ledger", 3, random.Random(1))
    assert hard.topic == "two_step" and len(hard.data["lines"]) == 4


@pytest.mark.parametrize("grade", GRADES)
def test_a_perfect_player_reaches_the_top_rank_in_every_grade(grade):
    g = Game("Dee", grade, seed=21)
    play(g, right)
    assert g.phase == "victory" and g.rank == RANKS[-1][1], (grade, g.xp, g.rank_scale)


def test_feedback_shows_decimals_as_decimals():
    g = Game("Eve", "4", seed=2)
    enter(g)
    g.question = Question("addition", 2, "What is 0.5 + 0.25?", Fraction(3, 4),
                          "h", "0.5 + 0.25 = 0.75", kind="decimal")
    assert not g.submit("abc") and "decimal like 0.75" in g.input_error
    assert g.submit("0.5")
    assert g.feedback.your_answer == "0.5" and g.feedback.answer_text == "0.75"
    g.question = Question("addition", 2, "Pick", "Yes", "h", "e", kind="choice",
                          choices=["Yes", "No"])
    g.enc["attempt"] = 0
    assert not g.submit("Maybe") and "Pick one of the choices" in g.input_error


def test_config_has_grade_settings_and_no_topic_switches():
    assert config.GRADES == ["K", "1", "2", "3", "4", "5"]
    assert config.DEFAULT_GRADE is None
    assert not hasattr(config, "TOPICS")


# --------------------------------------------------------------------------
# Hero codes v2
# --------------------------------------------------------------------------
from engine import decode_code, encode_code  # noqa: E402

# Made by the old 12-character encoder (before grades): village and mines won,
# 345 XP, levels addition 3, fractions 1, two_step 5, the rest 2, one story page.
OLD_CODE = "R6J8-N80N-JRDE"


def test_old_12_character_codes_still_load_as_4th_grade():
    g = Game.from_code("Zed", OLD_CODE)
    assert g is not None and g.grade == "4"
    assert g.done == {"village", "mines"} and g.xp == 345 and g.beats_seen == 1
    assert g.tiers == {"addition": 3, "subtraction": 2, "multiplication": 2,
                       "division": 2, "fractions": 1, "area_perimeter": 2, "two_step": 5}
    assert Game.from_code("Zed", OLD_CODE.lower().replace("-", "")).xp == 345
    # once saved again it becomes a v2 code with the grade in front
    assert g.to_code().startswith("4") and len(g.to_code()) == 19
    assert Game.from_code("Zed", g.to_code()).tiers == g.tiers


@pytest.mark.parametrize("grade", GRADES)
def test_codes_round_trip_in_every_grade(grade):
    g = Game("Fay", grade, seed=4)
    rng = random.Random(int(grade) if grade != "K" else 0)
    for t in g.topics:
        g.tiers[t] = rng.randint(1, 5)
    g.done = {r["key"] for r in g.regions[:3]}
    g.xp = 12345
    g.beats_seen = 2
    code = g.to_code()
    assert code[0] == grade and len(code.replace("-", "")) % 4 == 0
    assert len(code.replace("-", "")) >= 16
    assert all(ch in "0123456789ABCDEFGHJKMNPQRSTVWXYZ" for ch in code.replace("-", "")[1:])
    h = Game.from_code("Fay", code.lower().replace("-", " "))
    assert h.grade == grade and h.tiers == g.tiers and h.done == g.done
    assert h.xp == 12345 and h.beats_seen == 2
    bad = code[:-1] + ("0" if code[-1] != "0" else "1")
    assert Game.from_code("x", bad) is None


def test_adding_a_topic_at_the_end_keeps_old_codes_valid():
    topics = list(curriculum.grade("4").topics)
    gems = [True, False, True, False, False, False]
    short = encode_code("4", gems, [5, 4, 3, 2, 1], 999, 3)     # only 5 of the 7 topics
    assert decode_code(short) == ("4", gems, [5, 4, 3, 2, 1], 999, 3)
    g = Game.from_code("Gil", short)
    assert [g.tiers[t] for t in topics] == [5, 4, 3, 2, 1, config.START_TIER, config.START_TIER]
    assert g.done == {"village", "docks"} and g.xp == 999
    # more levels than topics (a topic was deleted, against the rules): the extras are dropped
    long = encode_code("4", gems, [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2], 5, 0)
    assert [Game.from_code("Gil", long).tiers[t] for t in topics] == [1, 2, 3, 4, 5, 1, 2]
    assert len(long.replace("-", "")) == 20 and len(short.replace("-", "")) == 16


def test_bad_codes_are_rejected_not_crashed():
    for junk in ("", "4", "9ABC-DEFG-HJKM-NPQR", "4ABC-DEFG-HJKM-NPQ", "4UUU-UUUU-UUUU-UUUU",
                 "4" * 40, "ABCD-1234", None):
        assert Game.from_code("x", junk) is None
    rng = random.Random(3)
    alphabet = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
    for _ in range(300):
        junk = rng.choice(GRADES) + "".join(rng.choice(alphabet) for _ in range(15))
        made = Game.from_code("x", junk)
        assert made is None or made.to_code().replace("-", "") == junk
    with pytest.raises(ValueError):
        encode_code("4", [True] * 6, [], 0, 0)
    with pytest.raises(ValueError):
        encode_code("4", [True] * 6, [1] * 32, 0, 0)
