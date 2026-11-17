"""Usage stats: the game's events, and writing them to a database."""
import pytest

import usage
from engine import Game


def answer_right(g):
    q = g.question
    g.submit(q.choices[q.choices.index(str(q.answer))] if q.kind == "choice"
             else str(q.answer))


def test_events_name_no_child_and_cover_a_quest():
    g = Game("Secret Name", "3", seed=1)
    ticks = iter(range(0, 10000, 7))
    g._clock = lambda: next(ticks)
    g.choose_region(0)
    g.start_region()
    while g.phase in ("question", "task", "feedback"):
        if g.phase == "question":
            answer_right(g)
        elif g.phase == "task":
            g.submit_task(g.task.data.get("answer"))
            if g.phase == "task":            # no simple answer key: give up the task
                g.submit_task(None)
        else:
            g.advance()
    names = [e["event"] for e in g.events]
    assert names[0] == "region_start" and "answer" in names
    assert names[-1] == "region_won"
    won = g.events[-1]
    assert won["region"] == g.regions[0]["key"] and won["mode"] == "quest"
    assert won["seconds"] > 0 and won["gems"] == 1
    ans = next(e for e in g.events if e["event"] == "answer" and not e["task"])
    assert ans["correct"] and ans["attempt"] == 1 and ans["seconds"] == 7
    assert ans["topic"] in g.topics and 1 <= ans["tier"] <= 5
    assert "Secret Name" not in repr(g.events)


def test_leaving_and_trials_are_logged():
    g = Game("x", "4", seed=2)
    g.choose_region(1)
    g.start_region()
    g.leave_region()
    left = g.events[-1]
    assert left["event"] == "region_left" and left["stage"] == "question"
    assert left["topic"]
    g.choose_region(0, mode="trial")
    assert g.events[-1]["event"] == "region_start" and g.events[-1]["mode"] == "trial"
    while g.phase != "trial_done":
        if g.phase == "question":
            answer_right(g)
        else:
            g.advance()
    done = g.events[-1]
    assert done["event"] == "trial_done" and done["passed"] and done["right"] == 5


def test_rows_are_written_to_the_database(tmp_path, monkeypatch):
    pytest.importorskip("sqlalchemy")
    pytest.importorskip("pandas")
    monkeypatch.setenv("MATHQUEST_USAGE_DB", f"sqlite:///{tmp_path / 'u.db'}")
    g = Game("x", "K", seed=3)
    g.choose_region(0)
    g.start_region()
    answer_right(g)
    usage.record("a" * 32, g.grade, [{"event": "start", "how": "new"}] + g.events)
    usage.recorder().flush()
    df = usage.load()
    assert list(df["event"][:3]) == ["start", "region_start", "answer"]
    row = df.iloc[2]
    assert row["grade"] == "K" and row["visit"] == "a" * 32 and bool(row["correct"])
    assert '"question"' in row["data"]


def test_switched_off_and_broken_databases_never_raise(monkeypatch):
    monkeypatch.setenv("MATHQUEST_USAGE_DB", "off")
    assert usage.db_url() is None
    usage.record("v", "4", [{"event": "start"}])
    monkeypatch.setenv("MATHQUEST_USAGE_DB", "nonsense://nowhere")
    usage.record("v", "4", [{"event": "start"}])     # logged, not raised


def test_postgres_addresses_use_psycopg3():
    assert usage.normalize("postgres://u:p@h/db") == "postgresql+psycopg://u:p@h/db"
    assert usage.normalize("postgresql://u:p@h/db") == "postgresql+psycopg://u:p@h/db"
    assert usage.normalize("sqlite:///usage.db").endswith("/usage.db")
    assert usage.normalize("sqlite:///usage.db") != "sqlite:///usage.db"
