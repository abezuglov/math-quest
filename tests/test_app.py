"""Smoke test: drive the real Streamlit screens through a whole game."""
import os

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

from questions import fmt  # noqa: E402

APP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
SIDE = ("Restart game", "⬅️ Back to the map", "Play again from the beginning 🔁")


def click(at, pred):
    next(b for b in at.button if pred(b)).click().run()


def set_task(at, g, good):
    """Work the controls of a hands-on task, right or wrong."""
    d, key = g.task.data, f"task_{g.qcount}"
    kind = g.task.kind
    if kind in ("coins", "multiples"):
        pool = d["bags"] if kind == "coins" else d["numbers"]
        at.button_group(key=key).set_value(list(d["answer"]) if good else list(pool))
    elif kind == "share":
        at.slider(key=key).set_value(d["each"] if good else d["each"] + 1)
        at.number_input(key=key + "_left").set_value(d["left"])
    elif kind == "shade":
        at.slider(key=key).set_value(d["answer"] if good else d["answer"] - 1)
    elif kind == "garden":
        at.slider(key=key + "_l").set_value(d["length"] if good else d["width"])
        at.slider(key=key + "_w").set_value(d["width"])
    else:
        n = len(d["lines"])
        at.radio(key=key).set_value(d["answer"] if good else (d["answer"] + 1) % n)


def test_full_playthrough_through_the_ui():
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception
    at.text_input[0].set_value("Testy <b>")
    click(at, lambda b: "Begin" in b.label)
    g = at.session_state["game"]
    assert g.phase == "map"
    seen, kinds = set(), set()
    turn = 0
    for _ in range(900):
        assert not at.exception, at.exception
        seen.add(g.phase)
        if g.phase == "victory":
            break
        if g.phase == "map":
            assert at.query_params["hero"] in (g.to_code(), [g.to_code()])
            i = next(i for i in range(len(g.regions)) if g.status(i) == "open")
            # try (and fail) one speed trial on the way, then play full quests
            trial = i == 1 and "trial_done" not in seen
            click(at, lambda b: b.key == (f"t_{i}" if trial else f"q_{i}"))
        elif g.phase == "question":
            turn += 1
            q = g.question
            miss = turn % 4 == 0 or g.enc["kind"] == "trial"    # every 4th one wrong
            if q.kind == "choice":
                want = next(c for c in q.choices if (c != q.answer) == miss)
                click(at, lambda b: b.label == want)
            else:
                at.text_input[0].set_value("1" if miss else fmt(q.answer))
                click(at, lambda b: "⚔️" in b.label or "✅" in b.label)
        elif g.phase == "task":
            kinds.add(g.task.kind)
            if g.task.kind == "ledger" and g.enc["attempt"] == 0:
                click(at, lambda b: (b.key or "").startswith("task_go_"))   # nothing picked
                assert at.session_state["game"].phase == "task"
            set_task(at, g, good=g.enc["attempt"] == 1 or g.task.kind in ("coins", "ledger"))
            at.run()
            assert not at.exception, at.exception
            click(at, lambda b: (b.key or "").startswith("task_go_"))
        else:
            click(at, lambda b: b.label not in SIDE)
        g = at.session_state["game"]
    assert g.phase == "victory"
    assert {"map", "region_intro", "question", "task", "feedback", "region_done",
            "trial_done", "story"} <= seen
    assert kinds == {"coins", "multiples", "share", "shade", "garden", "ledger"}
    cert = next(m.value for m in at.markdown if "Certificate of Heroism" in m.value)
    assert "Testy &lt;b&gt;" in cert

    # after the certificate: back to the map, then quick practice on a won region
    click(at, lambda b: "Back to the map" in b.label and b.label not in SIDE)
    g = at.session_state["game"]
    assert g.phase == "map" and g.all_done
    click(at, lambda b: b.key == "t_0")
    g = at.session_state["game"]
    assert g.phase == "question" and g.enc["kind"] == "trial"
    assert not at.exception


def test_hero_comes_back_from_the_address_or_a_typed_code():
    at = AppTest.from_file(APP, default_timeout=30).run()
    at.text_input[0].set_value("Zed")
    click(at, lambda b: "Begin" in b.label)
    click(at, lambda b: b.key == "q_0")
    click(at, lambda b: b.key == "intro_leave")
    g = at.session_state["game"]
    g.done.update({"village", "mines"})
    g.xp = 345
    code = g.to_code()

    again = AppTest.from_file(APP, default_timeout=30)
    again.query_params["hero"] = code
    again.query_params["name"] = "Zed"
    again.run()
    assert not again.exception
    h = again.session_state["game"]
    assert h.name == "Zed" and h.xp == 345 and h.done == {"village", "mines"}

    typed = AppTest.from_file(APP, default_timeout=30).run()
    typed.text_input(key="resume_name").set_value("Zed")
    typed.text_input(key="resume_code").set_value("nonsense")
    click(typed, lambda b: "Continue my quest" in b.label)
    assert "game" not in typed.session_state and typed.warning
    typed.text_input(key="resume_code").set_value(code.lower())
    click(typed, lambda b: "Continue my quest" in b.label)
    assert typed.session_state["game"].done == {"village", "mines"}

    broken = AppTest.from_file(APP, default_timeout=30)
    broken.query_params["hero"] = "XXXX-XXXX-XXXX"
    broken.run()
    assert not broken.exception and "game" not in broken.session_state
