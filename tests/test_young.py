"""Phase 5: reading aloud, big text, picture buttons and shorter stories for
the youngest players, and the grade and standards on the certificate."""
import os
from xml.etree import ElementTree

import pytest

import config
import curriculum
import pictures
import story
from engine import Game


# --- shorter stories --------------------------------------------------------
def test_young_grades_have_fewer_encounters_but_keep_boss_and_task():
    for grade, limit in config.ENCOUNTERS_BY_GRADE.items():
        g = Game("Kit", grade, seed=1)
        for r in g.regions:
            full = story.build_region(next(x for x in g.content.regions
                                           if x["key"] == r["key"]))["encounters"]
            kinds = [e["kind"] for e in r["encounters"]]
            assert len(kinds) <= max(limit, sum(k in ("boss", "task") for k in kinds))
            assert "boss" in kinds and ("task" in kinds) == any(e["kind"] == "task" for e in full)
            # kept in story order
            names = [e["name"] for e in full]
            idx = [names.index(e["name"]) for e in r["encounters"]]
            assert idx == sorted(idx)
            assert "riddle" in kinds and "fight" in kinds
        peak = g.regions[-1]
        assert any(e.get("hp") == "final" for e in peak["encounters"])


def test_grades_not_listed_keep_the_full_story():
    g = Game("Kit", "4", seed=1)
    assert [len(r["encounters"]) for r in g.regions] == [7] * 6


def test_shorten_rules():
    encs = [{"kind": k, "name": str(i)} for i, k in
            enumerate(["riddle", "riddle", "fight", "task", "riddle", "fight", "boss"])]
    assert [e["kind"] for e in story.shorten(encs, 4)] == ["riddle", "fight", "task", "boss"]
    assert [e["name"] for e in story.shorten(encs, 5)] == ["0", "1", "2", "3", "6"]
    assert story.shorten(encs, None) == encs and story.shorten(encs, 9) == encs
    assert [e["kind"] for e in story.shorten(encs, 1)] == ["task", "boss"]   # never lost


# --- no typed fractions in K-1 -----------------------------------------------
def test_k_and_1st_grade_never_type_fractions_or_decimals():
    for code in curriculum.NO_TYPED_FRACTIONS:
        for topic in curriculum.grade(code).topics.values():
            assert all(t.kind in ("number", "choice") for t in topic.templates), topic.id


def test_a_k_file_with_a_fraction_question_is_refused(tmp_path):
    text = (curriculum.CURRICULUM_DIR / "grade_k.toml").read_text(encoding="utf-8")
    line = '  text    = "{a} + {b} = ?"'
    assert line in text
    bad = tmp_path / "grade_k.toml"
    bad.write_text(text.replace(line, '  kind    = "decimal"\n' + line, 1), encoding="utf-8")
    with pytest.raises(curriculum.CurriculumError, match="do not type"):
        curriculum.load_grade(bad)


# --- reading aloud ------------------------------------------------------------
@pytest.mark.parametrize("text, said", [
    ("7 + ? = 10", "7 plus blank equals 10"),
    ("? + 4 = 10", "blank plus 4 equals 10"),
    ("9 − 3 = ?", "9 minus 3 equals blank"),
    ("How many now?", "How many now?"),
    ("It is 3:00. What time in one hour?", "It is 3 o'clock. What time in one hour?"),
    ("Half past 4 is 4:30.", "Half past 4 is 4 30."),
    ("6 × 7 = ?", "6 times 7 equals blank"),
    ("45 ? 30   Which sign goes in the middle?",
     "45 blank 30 Which sign goes in the middle?"),
])
def test_spoken_text(text, said):
    assert curriculum.spoken(text) == said


def test_spoken_reads_choices_the_text_does_not_name():
    assert curriculum.spoken("Which is bigger: 3 or 7?", ["3", "7"]) == "Which is bigger: 3 or 7?"
    assert curriculum.spoken("What shape is this?", ["circle", "square", "triangle"]) == \
        "What shape is this? Is it circle, square, or triangle?"
    assert curriculum.spoken("45 ? 30", ["<", ">", "="]).endswith(
        "Is it less than, greater than, or equal?")


def test_every_young_question_can_be_spoken():
    import random
    rng = random.Random(3)
    for code in config.READ_ALOUD_GRADES:
        for topic in curriculum.grade(code).topics.values():
            for level in range(1, 6):
                q = curriculum.generate(topic, level, rng)
                said = curriculum.spoken(q.text, q.choices if q.kind == "choice" else None)
                assert said and not any(s in said for s in "−×÷="), (topic.id, said)


# --- pictures on the buttons ------------------------------------------------
def test_choice_labels_and_pictures():
    assert pictures.choice_label("a bus") == "🚌 a bus"
    assert pictures.choice_label("cats") == "🐱 cats"
    assert pictures.choice_label("True") == "✅ True"
    assert pictures.choice_label("halves") == "halves"
    for text in ("3", "10", "triangle", "cube"):
        ElementTree.fromstring(pictures.for_choice(text))
    assert pictures.for_choice("11") is None and pictures.for_choice("more") is None
    # no matching game: the question's own picture would give the answer away
    assert pictures.for_choice("triangle", ("shape", "triangle")) is None


# --- certificate --------------------------------------------------------------
def test_practiced_standards_are_listed_once_in_file_order():
    g = Game("Kit", "K", seed=1)
    assert g.practiced_standards() == []
    t1, t2 = g.topics[0], g.topics[-1]
    g.stats[t2][1] = 2
    g.stats[t1][1] = 1
    assert g.practiced_standards() == [g.standard(t1), g.standard(t2)]
    assert all("standard" in row for row in g.summary())


# --- the screens --------------------------------------------------------------
st = pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

APP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")


def to_question(grade):
    at = AppTest.from_file(APP, default_timeout=30)
    at.query_params["grade"] = grade
    at.run()
    at.text_input[0].set_value("Kit")
    next(b for b in at.button if "Begin" in b.label).click().run()
    next(b for b in at.button if b.key == "q_0").click().run()
    next(b for b in at.button if b.label.startswith("Enter")).click().run()
    assert not at.exception and at.session_state["game"].phase == "question"
    return at


def htmls(at):
    return [e.proto.body for e in at.get("html")]


def test_kindergarten_question_has_read_aloud_and_big_text():
    at = to_question("K")
    g = at.session_state["game"]
    say = [h for h in htmls(at) if "speechSynthesis" in h]
    assert len(say) == 1 and '"auto": true' in say[0]
    assert any("class='question big'" in m.value for m in at.markdown)
    assert at.toggle(key="auto_read_K").value is True
    # the child switches reading off: the button stays, nothing is read by itself
    at.toggle(key="auto_read_K").set_value(False).run()
    say = [h for h in htmls(at) if "speechSynthesis" in h]
    assert len(say) == 1 and '"auto": false' in say[0]
    assert g.phase == "question"


def test_second_grade_has_the_button_but_does_not_read_by_itself():
    at = to_question("2")
    say = [h for h in htmls(at) if "speechSynthesis" in h]
    assert len(say) == 1 and '"auto": false' in say[0]
    assert not any("class='question big'" in m.value for m in at.markdown)


def test_fourth_grade_has_no_read_aloud():
    at = to_question("4")
    assert not any("speechSynthesis" in h for h in htmls(at))
