import os
import random
import sys
from fractions import Fraction

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config  # noqa: E402
from engine import Game  # noqa: E402
from questions import (ALL_TOPICS, fmt, generate, is_correct,  # noqa: E402
                       parse_answer, severity)


@pytest.mark.parametrize("topic", ALL_TOPICS)
@pytest.mark.parametrize("tier", [1, 2, 3, 4, 5])
def test_generators_are_well_formed(topic, tier):
    rng = random.Random(tier * 100 + len(topic))
    for _ in range(400):
        q = generate(topic, tier, rng)
        assert q.text and q.hint and q.explanation
        if q.kind == "choice":
            assert q.answer in q.choices and len(set(q.choices)) == 2
        else:
            assert isinstance(q.answer, Fraction) and q.answer > 0
            # the displayed answer must be accepted when typed back in
            assert is_correct(q, parse_answer(fmt(q.answer)))
            # the answer shown to the child appears in the worked explanation
            assert fmt(q.answer) in q.explanation or str(q.answer) in q.explanation
            if q.kind == "number":
                assert q.answer.denominator == 1


def test_parse_answer():
    assert parse_answer("42") == 42
    assert parse_answer(" 1,203 ") == 1203
    assert parse_answer("3/4") == Fraction(3, 4)
    assert parse_answer("6/8") == Fraction(3, 4)
    assert parse_answer("1 1/2") == Fraction(3, 2)
    assert parse_answer("12 feet") == 12
    assert parse_answer("2.5") == Fraction(5, 2)
    assert parse_answer("abc") is None
    assert parse_answer("") is None
    assert parse_answer("3/0") is None


def test_severity_scales_with_error():
    q = generate("multiplication", 4, random.Random(1))
    a = q.answer
    assert severity(q, a + 1) == "light"
    assert severity(q, a * Fraction(12, 10)) == "medium"
    assert severity(q, a * 3) == "heavy"


def play(game, answer_fn, max_steps=5000):
    for _ in range(max_steps):
        if game.phase == "region_intro":
            game.start_region()
        elif game.phase == "question":
            assert game.submit(answer_fn(game))
        elif game.phase == "feedback":
            game.advance()
        elif game.phase == "region_done":
            game.next_region()
        elif game.phase == "defeat":
            game.retry_region()
        elif game.phase == "victory":
            return
    raise AssertionError("game did not finish")


def right(game):
    return fmt(game.question.answer)


def wrong(game):
    q = game.question
    if q.kind == "choice":
        return next(c for c in q.choices if c != q.answer)
    return fmt(q.answer * 5 + 7)


def test_perfect_player_wins_and_climbs_tiers():
    g = Game("Ada", seed=3)
    play(g, right)
    assert g.phase == "victory" and g.defeats == 0 and g.hp > 0
    assert all(s[0] == s[1] for s in g.stats.values())
    assert max(g.best_tiers.values()) == config.MAX_TIER
    assert g.xp > 2000


def test_tier_moves_up_after_a_run_of_right_answers():
    g = Game("Bo", seed=1)
    g.start_region()
    topic = g.question.topic
    start = g.tiers[topic]
    while g.stats[topic][1] < config.UP_AFTER:
        if g.phase == "question":
            g.submit(right(g))
        else:
            g.advance()
    assert g.tiers[topic] == start + 1

    g = Game("Cy", seed=1)
    g.start_region()
    topic = g.question.topic
    g.submit(wrong(g))                 # first miss: hint + retry
    assert g.phase == "question" and g.enc["attempt"] == 1
    g.submit(wrong(g))                 # retry does not count twice
    assert g.stats[topic] == [0, 1]


def test_actions_ignore_clicks_in_the_wrong_phase():
    g = Game("Hal", seed=6)
    g.next_region()
    g.retry_region()
    assert g.region_idx == 0 and g.phase == "region_intro" and g.defeats == 0
    g.start_region()
    count = g.qcount
    g.start_region()
    g.advance()
    assert g.qcount == count and g.phase == "question"
    assert g.submit("9" * 5000) is False and g.phase == "question"


def test_a_hit_is_never_paid_twice_after_a_defeat():
    g = Game("Ida", seed=8)
    g.start_region()
    totals = []
    for _ in range(4):
        while not (g.phase == "question" and g.enc["kind"] == "fight"):
            if g.phase == "question":
                g.submit(right(g))
            else:
                g.advance()
        g.submit(right(g))             # land one hit ...
        g.advance()
        while g.phase != "defeat":     # ... then lose on purpose
            if g.phase == "question":
                g.submit(wrong(g))
            else:
                g.advance()
        totals.append(g.xp)
        g.retry_region()
    assert len(set(totals)) == 1


def test_struggling_player_is_defeated_then_eased():
    g = Game("Di", seed=5)
    g.start_region()
    for _ in range(200):
        if g.phase == "question":
            g.submit(wrong(g))
        elif g.phase == "feedback":
            g.advance()
        elif g.phase == "defeat":
            break
    assert g.phase == "defeat" and g.hp == 0
    assert min(g.tiers.values()) == config.MIN_TIER
    g.retry_region()
    assert g.hp == config.MAX_HP and g.phase == "question"


def test_mixed_player_always_finishes():
    for seed in range(15):
        g = Game("Eve", seed=seed)
        coin = random.Random(seed)
        play(g, lambda game: right(game) if coin.random() < 0.6 else wrong(game))
        assert g.phase == "victory"


def test_low_hp_brings_a_healer():
    g = Game("Flo", seed=2)
    g.start_region()
    seen = False
    coin = random.Random(9)
    for _ in range(3000):
        if g.phase == "question":
            if g.enc["potion"]:
                seen = True
                before = g.hp
                g.submit(right(g))
                assert g.hp > before
                break
            foe = g.enc["kind"] in ("fight", "boss")
            g.submit(wrong(g) if foe and coin.random() < 0.7 else right(g))
        elif g.phase == "feedback":
            g.advance()
        elif g.phase == "region_done":
            g.next_region()
        elif g.phase == "defeat":
            g.retry_region()
        elif g.phase == "region_intro":
            g.start_region()
        else:
            break
    assert seen


def test_replaying_a_region_pays_no_xp_twice_and_softens_hits():
    g = Game("Gus", seed=4)
    g.start_region()
    g.submit(right(g))
    g.advance()                                # clear the first riddle
    xp_after_first = g.xp
    hits = []
    while g.phase != "defeat":
        if g.phase == "question":
            g.submit(wrong(g))
            if g.feedback.damage:
                hits.append(g.feedback.damage)
        else:
            g.advance()
    g.retry_region()
    g.submit(right(g))
    assert g.feedback.replay and g.xp == xp_after_first
    g.advance()
    while not (g.phase == "question" and g.enc["kind"] == "fight"):
        if g.phase == "question":
            g.submit(right(g))
        else:
            g.advance()
    g.submit(wrong(g))
    assert g.feedback.damage < max(hits)
