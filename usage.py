"""Anonymous usage stats: how many play, how far they get, where they get stuck.

The game (engine.py) notes events such as "answer", "region_won" or "defeat".
The app hands them here with a random visit id and the grade, and a background
thread writes them to a database, so a slow or broken database never slows
down or stops the game. Nothing stored names the child: no hero name, no hero
code, no IP address.

Where the events go (the first one set wins):
  1. the environment variable MATHQUEST_USAGE_DB,
  2. `usage_db = "..."` in .streamlit/secrets.toml (or the Streamlit Cloud
     Secrets box),
  3. USAGE_DB in config.py (a local SQLite file by default).
Any SQLAlchemy address works, e.g. a free hosted Postgres:
  postgresql://user:password@host:5432/dbname
Set it to "off" (or USAGE_TRACKING = False in config.py) to collect nothing.

See the numbers with:  streamlit run stats.py
"""
from __future__ import annotations

import datetime
import json
import logging
import os
import queue
import threading
import time

import config

log = logging.getLogger(__name__)
HERE = os.path.dirname(os.path.abspath(__file__))

# Events get these as real columns (easy to query); everything else goes in `data`.
COLUMNS = ("region", "mode", "kind", "topic", "tier", "correct", "attempt", "seconds")


def db_url():
    """The database address, or None when usage stats are switched off."""
    if not getattr(config, "USAGE_TRACKING", True):
        return None
    url = os.environ.get("MATHQUEST_USAGE_DB")
    if url is None:
        try:
            import streamlit as st
            url = st.secrets.get("usage_db")
        except Exception:      # no secrets file: that is fine
            url = None
    if url is None:
        url = getattr(config, "USAGE_DB", None)
    url = str(url or "").strip()
    if url.lower() in ("", "off", "none", "false"):
        return None
    return normalize(url)


def normalize(url):
    """Hosted Postgres services hand out postgres:// addresses; use psycopg 3.
    A relative SQLite path is taken from the game's folder, not the shell's."""
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    if url.startswith("sqlite:///") and not url.startswith("sqlite:////"):
        path = url[len("sqlite:///"):]
        if path and path != ":memory:" and not os.path.isabs(path):
            return "sqlite:///" + os.path.join(HERE, path).replace("\\", "/")
    return url


def events_table(meta):
    from sqlalchemy import (Boolean, Column, DateTime, Float, Integer, String,
                            Table, Text)
    return Table(
        "events", meta,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("ts", DateTime(timezone=True), index=True),
        Column("visit", String(32), index=True),
        Column("grade", String(2)),
        Column("event", String(20), index=True),
        Column("region", String(40)),
        Column("mode", String(10)),
        Column("kind", String(10)),
        Column("topic", String(60)),
        Column("tier", Integer),
        Column("correct", Boolean),
        Column("attempt", Integer),
        Column("seconds", Float),
        Column("data", Text),
    )


def make_engine(url):
    from sqlalchemy import MetaData, create_engine
    engine = create_engine(url, pool_pre_ping=True)
    meta = MetaData()
    table = events_table(meta)
    meta.create_all(engine)
    return engine, table


def to_row(visit, grade, event, now=None):
    """One event dict from the game -> one database row."""
    event = dict(event)
    row = {"ts": now or datetime.datetime.now(datetime.timezone.utc),
           "visit": str(visit)[:32], "grade": str(grade)[:2],
           "event": str(event.pop("event", "?"))[:20]}
    for col in COLUMNS:
        row[col] = event.pop(col, None)
    for col, size in (("region", 40), ("mode", 10), ("kind", 10), ("topic", 60)):
        if row[col] is not None:
            row[col] = str(row[col])[:size]
    row["data"] = json.dumps(event, default=str) if event else None
    return row


class Recorder:
    """Writes rows to the database on a background thread."""

    def __init__(self, url):
        self.url = url
        self.queue = queue.Queue(maxsize=20000)
        self.thread = threading.Thread(target=self._run, name="usage-stats", daemon=True)
        self.thread.start()

    def put(self, rows):
        for row in rows:
            try:
                self.queue.put_nowait(row)
            except queue.Full:     # the database is down for long: drop, don't block
                return

    def _run(self):
        engine = table = None
        while True:
            batch = [self.queue.get()]
            while len(batch) < 500:
                try:
                    batch.append(self.queue.get_nowait())
                except queue.Empty:
                    break
            for attempt in range(3):
                try:
                    if engine is None:
                        engine, table = make_engine(self.url)
                    with engine.begin() as conn:
                        conn.execute(table.insert(), batch)
                    break
                except Exception as e:   # never let stats break anything
                    log.warning("usage stats: could not write %d events (%s)",
                                len(batch), e)
                    engine = None
                    time.sleep(2 * (attempt + 1))
            for _ in batch:
                self.queue.task_done()

    def flush(self, timeout=10.0):
        """Wait until everything queued is written (for tests and scripts)."""
        end = time.monotonic() + timeout
        while self.queue.unfinished_tasks and time.monotonic() < end:
            time.sleep(0.02)


_recorder = None
_recorder_url = None
_lock = threading.Lock()


def recorder():
    """The shared Recorder for the current address (None when switched off)."""
    global _recorder, _recorder_url
    url = db_url()
    if url is None:
        return None
    with _lock:
        if _recorder is None or _recorder_url != url:
            _recorder, _recorder_url = Recorder(url), url
        return _recorder


def record(visit, grade, events):
    """Queue the game's events. Never raises."""
    if not events:
        return
    try:
        rec = recorder()
        if rec is not None:
            now = datetime.datetime.now(datetime.timezone.utc)
            rec.put([to_row(visit, grade, e, now) for e in events])
    except Exception as e:
        log.warning("usage stats: %s", e)


def load(url=None):
    """All events as a pandas DataFrame (for stats.py)."""
    import pandas as pd
    from sqlalchemy import select
    engine, table = make_engine(url or db_url())
    with engine.connect() as conn:
        df = pd.read_sql(select(table), conn)
    df["ts"] = pd.to_datetime(df["ts"], utc=True)
    return df
