"""Smoke test: drive the real Streamlit screens through a whole game."""
import os

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

from questions import fmt  # noqa: E402

APP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")


def test_full_playthrough_through_the_ui():
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception
    at.text_input[0].set_value("Testy <b>")
    at.button[0].click().run()
    g = at.session_state["game"]
    seen = set()
    turn = 0
    for _ in range(600):
        assert not at.exception, at.exception
        seen.add(g.phase)
        if g.phase == "victory":
            break
        if g.phase == "question":
            turn += 1
            q = g.question
            miss = turn % 4 == 0          # get every 4th one wrong
            if q.kind == "choice":
                want = next(c for c in q.choices if (c != q.answer) == miss)
                next(b for b in at.button if b.label == want).click().run()
            else:
                at.text_input[0].set_value("1" if miss else fmt(q.answer))
                next(b for b in at.button if "⚔️" in b.label or "✅" in b.label).click().run()
        else:
            next(b for b in at.button if b.label != "Restart game").click().run()
        g = at.session_state["game"]
    assert g.phase == "victory"
    assert {"region_intro", "question", "feedback", "region_done"} <= seen
    cert = next(m.value for m in at.markdown if "Certificate of Heroism" in m.value)
    assert "Testy &lt;b&gt;" in cert
