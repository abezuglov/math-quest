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
            assert q.answer in q.choices
            assert 2 <= len(set(q.choices)) == len(q.choices) <= 4
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


import tasks  # noqa: E402
import pictures  # noqa: E402
import story  # noqa: E402
from xml.etree import ElementTree  # noqa: E402


def task_right(task):
    d = task.data
    return {"coins": lambda: d["answer"], "multiples": lambda: d["answer"],
            "share": lambda: (d["each"], d["left"]), "shade": lambda: d["answer"],
            "garden": lambda: (d["length"], d["width"]),
            "ledger": lambda: d["answer"]}[task.kind]()


def task_wrong(task):
    d = task.data
    return {"coins": lambda: d["bags"][:1] if sorted(d["bags"][:1]) != d["answer"] else d["bags"][:4],
            "multiples": lambda: d["numbers"], "share": lambda: (d["each"] + 1, 0),
            "shade": lambda: d["answer"] + 1, "garden": lambda: (d["length"], d["width"] + 1),
            "ledger": lambda: (d["answer"] + 1) % len(d["lines"])}[task.kind]()


def auto(g, pick=None):
    """Do the next thing on any screen that is not a typed question."""
    ph = g.phase
    if ph == "map":
        i = pick if pick is not None else next(
            i for i in range(len(g.regions)) if g.status(i) == "open")
        g.choose_region(i)
    elif ph == "region_intro":
        g.start_region()
    elif ph == "task":
        g.submit_task(task_right(g.task))
    elif ph == "feedback":
        g.advance()
    elif ph == "region_done":
        g.next_region()
    elif ph == "story":
        g.continue_story()
    elif ph == "defeat":
        g.retry_region()
    elif ph == "trial_done":
        g.leave_trial()


def enter(g, i=0):
    """Walk from the map into the first question of region i."""
    g.choose_region(i)
    g.start_region()


def play(game, answer_fn, max_steps=8000):
    for _ in range(max_steps):
        if game.phase == "question":
            assert game.submit(answer_fn(game))
        elif game.phase == "victory":
            return
        else:
            auto(game)
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
    # one pass through the story spreads the answers over every topic, so the
    # busiest topics climb at least two levels above the start
    assert max(g.best_tiers.values()) >= min(config.MAX_TIER, config.START_TIER + 2)
    assert g.xp > 2000
    assert g.all_done and g.beats_seen == len(story.BEATS)


def test_tier_moves_up_after_a_run_of_right_answers():
    g = Game("Bo", seed=1)
    enter(g)
    topic = g.question.topic
    start = g.tiers[topic]
    while g.stats[topic][1] < config.UP_AFTER:
        if g.phase == "question":
            g.submit(right(g))
        else:
            auto(g)
    assert g.tiers[topic] == start + 1

    g = Game("Cy", seed=1)
    enter(g)
    topic = g.question.topic
    g.submit(wrong(g))                 # first miss: hint + retry
    assert g.phase == "question" and g.enc["attempt"] == 1
    g.submit(wrong(g))                 # retry does not count twice
    assert g.stats[topic] == [0, 1]


def test_actions_ignore_clicks_in_the_wrong_phase():
    g = Game("Hal", seed=6)
    g.next_region()
    g.retry_region()
    g.start_region()
    g.continue_story()
    g.leave_trial()
    g.show_certificate()
    assert g.phase == "map" and g.defeats == 0 and not g.done
    g.choose_region(5)                 # Dragon's Peak is locked at the start
    g.choose_region(99)
    assert g.phase == "map"
    enter(g)
    count = g.qcount
    g.start_region()
    g.choose_region(2)
    g.advance()
    assert g.qcount == count and g.phase == "question" and g.region_idx == 0
    assert g.submit("9" * 5000) is False and g.phase == "question"
    assert g.submit_task([1]) is False


def test_a_hit_is_never_paid_twice_after_a_defeat():
    g = Game("Ida", seed=8)
    enter(g)
    totals = []
    for _ in range(4):
        while not (g.phase == "question" and g.enc["kind"] == "fight"):
            if g.phase == "question":
                g.submit(right(g))
            else:
                auto(g)
        g.submit(right(g))             # land one hit ...
        g.advance()
        while g.phase != "defeat":     # ... then lose on purpose
            if g.phase == "question":
                g.submit(wrong(g))
            else:
                auto(g)
        totals.append(g.xp)
        g.retry_region()
    assert len(set(totals)) == 1


def test_leaving_and_coming_back_pays_no_xp_twice():
    g = Game("Jo", seed=8)
    enter(g)
    g.submit(right(g))
    xp = g.xp
    g.advance()
    g.leave_region()
    assert g.phase == "map" and g.xp == xp
    enter(g)
    g.submit(right(g))
    assert g.feedback.replay and g.xp == xp


def test_struggling_player_is_defeated_then_eased():
    g = Game("Di", seed=5)
    enter(g)
    for _ in range(200):
        if g.phase == "question":
            g.submit(wrong(g))
        elif g.phase == "defeat":
            break
        else:
            auto(g)
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
    enter(g)
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
        elif g.phase == "victory":
            break
        else:
            auto(g)
    assert seen


def test_replaying_a_region_pays_no_xp_twice_and_softens_hits():
    g = Game("Gus", seed=4)
    enter(g)
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
            auto(g)
    g.retry_region()
    g.submit(right(g))
    assert g.feedback.replay and g.xp == xp_after_first
    g.advance()
    while not (g.phase == "question" and g.enc["kind"] == "fight"):
        if g.phase == "question":
            g.submit(right(g))
        else:
            auto(g)
    g.submit(wrong(g))
    assert g.feedback.damage < max(hits)


# --------------------------------------------------------------------------
# Map, speed trials, story pages, hero codes
# --------------------------------------------------------------------------
def run_trial(g, i, n_right):
    g.choose_region(i, "trial")
    assert g.phase == "question" and g.enc["kind"] == "trial"
    for k in range(g.enc["total"]):
        g.submit(right(g) if k < n_right else wrong(g))
        assert g.phase == "feedback"       # a trial never gives a second try
        g.advance()
    assert g.phase == "trial_done"


def test_regions_can_be_played_in_any_order_and_the_peak_opens_last():
    g = Game("Kai", seed=11)
    assert [g.status(i) for i in range(6)] == ["open"] * 5 + ["locked"]
    for n, i in enumerate([3, 0, 4, 2, 1]):
        assert g.status(5) == "locked"
        while not (g.phase in ("map", "story") and g.status(i) == "done"):
            if g.phase == "question":
                g.submit(right(g))
            else:
                auto(g, pick=i)
        # story pages come after the 1st, 3rd and 5th gem, whatever the order
        assert (g.phase == "story") == (n + 1 in (1, 3, 5))
        while g.phase == "story":
            g.continue_story()
    assert g.status(5) == "open" and g.beats_seen == 3
    assert not g.can_trial(5)              # the finale must be played in full once
    g.choose_region(5, "trial")
    assert g.phase == "map"
    play(g, right)
    assert g.phase == "victory" and g.all_done
    g.back_to_map()
    assert g.phase == "map" and g.can_trial(5)
    g.show_certificate()
    assert g.phase == "victory"


def test_speed_trial_wins_a_gem_only_with_enough_right_answers():
    g = Game("Lu", seed=12)
    run_trial(g, 1, 3)
    assert not g.trial_result["passed"] and g.status(1) == "open"
    g.retry_trial()
    assert g.phase == "question" and g.enc["asked"] == 1
    for k in range(5):
        assert g.question.tier >= 3        # skipping a quest must be earned
        g.submit(right(g))
        g.advance()
    res = g.trial_result
    assert res["passed"] and res["new_gem"] and res["bonus"] == config.BOSS_BONUS
    assert g.status(1) == "done"
    xp = g.xp
    g.leave_trial()
    assert g.phase == "story"              # first gem: the scorched note
    g.continue_story()
    run_trial(g, 1, 5)                     # quick practice on a region already won
    assert g.trial_result["passed"] and not g.trial_result["new_gem"]
    assert g.trial_result["bonus"] == 0 and g.xp > xp
    g.leave_trial()
    assert g.phase == "map" and len(g.done) == 1


def test_hero_code_brings_back_gems_levels_and_xp():
    g = Game("Mia", seed=13)
    for i in (0, 2, 4):
        run_trial(g, i, 5)
        g.leave_trial()
        while g.phase == "story":
            g.continue_story()
    code = g.to_code()
    assert code[0] == "4" and len(code) % 5 == 4
    assert all(ch == "-" for ch in code[4::5])
    h = Game.from_code("Mia", code.lower().replace("-", " "))
    assert h is not None and h.done == g.done and h.xp == g.xp and h.tiers == g.tiers
    assert h.phase == "map" and h.beats_seen == 2      # old story pages are not replayed
    assert Game.from_code("x", "") is None
    assert Game.from_code("x", "ABCD-1234-EFG") is None
    assert Game.from_code("x", "UUUU-UUUU-UUUU") is None
    bad = code[:-1] + ("0" if code[-1] != "0" else "1")
    assert Game.from_code("x", bad) is None
    # random codes are rejected, or decode to exactly themselves; never a crash
    rng = random.Random(1)
    for _ in range(300):
        junk = "".join(rng.choice("0123456789ABCDEFGHJKMNPQRSTVWXYZ") for _ in range(12))
        made = Game.from_code("x", junk)
        assert made is None or made.to_code().replace("-", "") == junk


def test_a_full_hero_survives_the_code():
    g = Game("Ned", seed=14)
    play(g, right)
    h = Game.from_code("Ned", g.to_code())
    assert h.all_done and h.tiers == g.tiers and h.xp == g.xp
    assert h.beats_seen == len(story.BEATS)


def test_a_typo_in_the_code_is_almost_always_caught():
    g = Game("Pat", seed=16)
    run_trial(g, 0, 5)
    code = g.to_code().replace("-", "")
    rng = random.Random(2)
    slipped = 0
    for _ in range(4000):
        i = rng.randrange(len(code))
        ch = rng.choice([c for c in "0123456789ABCDEFGHJKMNPQRSTVWXYZ" if c != code[i]])
        slipped += Game.from_code("x", code[:i] + ch + code[i + 1:]) is not None
    assert slipped <= 4


def test_an_unread_story_page_and_switched_off_regions_survive_the_code(monkeypatch):
    g = Game("Quin", seed=17)
    run_trial(g, 0, 5)
    g.leave_trial()
    assert g.phase == "story"                  # the page is due but not read yet
    h = Game.from_code("Quin", g.to_code())
    assert h.phase == "story" and h.beats_seen == 0
    h.continue_story()
    assert h.phase == "map" and Game.from_code("Quin", h.to_code()).phase == "map"

    full = Game("Rae", seed=18)
    play(full, right)
    code = full.to_code()
    import curriculum
    for tid in ("fractions", "g4_decimals", "division", "g4_convert"):   # forest and docks
        monkeypatch.setattr(curriculum.grade("4").topics[tid], "enabled", False)
    small = Game.from_code("Rae", code)
    assert len(small.regions) == 4 and small.all_done
    assert small.to_code() == code             # nothing is lost while topics are off


def test_practice_in_a_won_region_pays_half_and_leaving_restores_health():
    g = Game("Sol", seed=19)
    run_trial(g, 0, 5)
    g.leave_trial()
    g.continue_story()
    g.choose_region(0, "trial")
    before = g.xp
    tier = g.question.tier
    g.submit(right(g))
    assert g.feedback.xp == (config.XP_BASE * tier + config.STREAK_BONUS) // 2
    assert g.xp == before + g.feedback.xp
    h = Game("Tam", seed=5)
    enter(h)
    while h.phase != "defeat":
        if h.phase == "question":
            h.submit(wrong(h))
        else:
            auto(h)
    h.leave_region()
    assert h.phase == "map" and h.hp == config.MAX_HP


@pytest.mark.parametrize("kind", sorted(tasks.TASK_TOPIC))
@pytest.mark.parametrize("tier", [1, 2, 3, 4, 5])
def test_tasks_are_well_formed(kind, tier):
    rng = random.Random(tier * 31 + len(kind))
    for _ in range(300):
        t = tasks.generate(kind, tier, rng)
        assert t.prompt and t.hint and t.solution and t.explanation
        assert tasks.check(t, task_right(t))
        assert not tasks.check(t, task_wrong(t))
        assert not tasks.check(t, None) and not tasks.check(t, [])
        assert tasks.describe(t, task_right(t)) and tasks.describe(t, None)
        d = t.data
        if kind == "coins":
            assert sum(d["answer"]) == d["target"] and set(d["answer"]) <= set(d["bags"])
        if kind == "multiples":
            assert all((x % d["n"] == 0) == (x in d["answer"]) for x in d["numbers"])
        if kind == "share":
            assert d["boats"] * d["each"] + d["left"] == d["n"] and d["left"] < d["boats"]
            assert d["each"] <= d["max_each"]
        if kind == "shade":
            assert Fraction(d["answer"], d["parts"]) == Fraction(d["a"], d["b"])
        if kind == "garden":
            good = [(x, y) for x in range(1, d["max"] + 1) for y in range(1, d["max"] + 1)
                    if tasks.check(t, (x, y))]
            # one garden, and it may be laid out either way round
            assert good == sorted([(d["length"], d["width"]), (d["width"], d["length"])])
        if kind == "ledger":
            wrong_lines = [i for i, (text, total) in enumerate(d["lines"])
                           if eval(text.replace("×", "*").replace("−", "-")) != total]
            assert wrong_lines == [d["answer"]]


def test_task_gives_a_hint_then_shows_the_answer():
    g = Game("Oz", seed=15)
    enter(g)
    while g.phase != "task":
        if g.phase == "question":
            g.submit(right(g))
        else:
            g.advance()
    asked = g.stats["addition"][1]
    assert g.submit_task(task_wrong(g.task))
    assert g.phase == "task" and g.feedback.retry and g.enc["attempt"] == 1
    assert g.submit_task(task_wrong(g.task))
    assert g.phase == "feedback" and g.feedback.encounter_over and not g.feedback.correct
    assert g.stats["addition"][1] == asked + 1          # counted once
    g.advance()
    assert g.phase == "question" and g.enc_idx == 4


def test_pictures_are_valid_svg():
    def ok(svg):
        root = ElementTree.fromstring(svg)
        assert root.tag.endswith("svg")

    for r in story.REGIONS:
        ok(pictures.scene(r["key"]))
    for art in ("note", "nilla", "ledger", "finale"):
        ok(pictures.story_art(art))
    for beat in story.BEATS:
        ok(pictures.story_art(beat["art"]))
    for status in ("done", "open", "locked"):
        ok(pictures.kingdom_map([(r["key"], r["name"], status) for r in story.REGIONS]))
    ok(pictures.kingdom_map([("forest", "Fraction Forest", "open")]))
    rng = random.Random(5)
    drawn = set()
    for topic in ALL_TOPICS:
        for tier in range(1, 6):
            for _ in range(200):
                q = generate(topic, tier, rng)
                svg = pictures.for_question(q.picture)
                if q.picture:
                    drawn.add(q.picture[0])
                    ok(svg)
                else:
                    assert svg is None
    assert drawn == {"array", "bars", "pie", "rect", "vmul"}
    for n, boats, each in [(17, 3, 0), (17, 3, 5), (17, 3, 9), (95, 6, 15), (4, 2, 2)]:
        ok(pictures.share_fig(n, boats, each))
    for shaded in range(0, 13):
        ok(pictures.shade_bars(2, 3, 12, shaded))
    for l in range(1, 13):
        for w in range(1, 13):
            ok(pictures.rect_fig(l, w, f"{l} m", f"{w} m", True))
            ok(pictures.garden_fig(l, w, 12))
