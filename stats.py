"""Usage stats for The Number Thief of Arithmos (for the teacher, not the class).

Run:  streamlit run stats.py

It reads the same database as the game (see usage.py). To read the stats of
the online game, give it the same address: put `usage_db = "..."` in
.streamlit/secrets.toml, or set the environment variable MATHQUEST_USAGE_DB.
It can also be deployed as a second Streamlit Cloud app (main file stats.py);
then add `stats_password = "..."` to its secrets so only you can open it.
"""
import datetime
import hmac
import json

import pandas as pd
import streamlit as st

import curriculum
import usage

st.set_page_config(page_title="Math Quest usage", page_icon="📊", layout="wide")


def password_ok():
    try:
        secret = st.secrets.get("stats_password")
    except Exception:
        secret = None
    if not secret:
        return True
    typed = st.text_input("Password", type="password")
    if typed and hmac.compare_digest(typed, str(secret)):
        return True
    if typed:
        st.error("Wrong password.")
    return False


@st.cache_data(ttl=60, show_spinner="Loading the events...")
def load(url):
    df = usage.load(url)
    extra = pd.json_normalize([json.loads(d) if d else {} for d in df["data"]])
    extra.index = df.index
    return df.drop(columns=["data"]).join(extra.drop(columns=[c for c in extra
                                                             if c in df], errors="ignore"))


def names():
    """grade -> ({region key: name}, {topic key: label})"""
    out = {}
    for code, g in curriculum.load_all().items():
        out[code] = ({r["key"]: r["name"] for r in g.regions},
                     {k: t.label for k, t in g.topics.items()})
    return out


def col(df, name, default=None):
    return df[name] if name in df else pd.Series(default, index=df.index)


def gorder(code):
    """K, 1, 2 ... 5, then anything else."""
    return "K12345".find(code) if code in "K12345" else 9


def by_grade(index):
    """Sort (grade, ...) index tuples in grade order, keeping file order inside."""
    return sorted(index, key=lambda ix: (gorder(ix[0]), ix[1:]))


def minutes(s):
    return (s / 60).round(1)


def main():
    st.title("📊 Math Quest: who plays, how far they get, where they get stuck")
    if not password_ok():
        return
    url = usage.db_url()
    if url is None:
        st.warning("Usage stats are switched off (USAGE_TRACKING / USAGE_DB in "
                   "config.py, or MATHQUEST_USAGE_DB).")
        return
    try:
        df = load(url)
    except Exception as e:
        st.error(f"Could not read the usage database: {e}")
        return
    if df.empty:
        st.info("No games played yet. Play a few riddles in the game and come back.")
        return
    label = names()

    # --- filters ----------------------------------------------------------
    c1, c2, c3 = st.columns([1, 2, 1])
    days = c1.selectbox("Period", [7, 30, 90, 365, None], index=1,
                        format_func=lambda d: f"Last {d} days" if d else "All time")
    grades = sorted(df["grade"].dropna().unique(), key=gorder)
    pick = c2.multiselect("Grades", grades, default=grades,
                          format_func=lambda g: curriculum.grade(g).name
                          if g in label else g)
    if c3.button("🔄 Reload"):
        load.clear()
        st.rerun()
    if days:
        since = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=days)
        df = df[df["ts"] >= since]
    df = df[df["grade"].isin(pick)]
    if df.empty:
        st.info("Nothing in this period for these grades.")
        return

    ans = df[df["event"] == "answer"]
    first = ans[ans["attempt"] == 1]
    visits = df.groupby("visit").agg(grade=("grade", "first"), start=("ts", "min"),
                                     end=("ts", "max"), gems=("gems", "max"),
                                     answers=("event", lambda e: (e == "answer").sum()))
    visits["minutes"] = (visits["end"] - visits["start"]).dt.total_seconds() / 60
    starts = df[df["event"] == "start"]
    how = starts.groupby("visit")["how"].first() if "how" in starts else pd.Series()
    wins = df[df["event"] == "victory"]

    k = st.columns(5)
    k[0].metric("Visits", f"{len(visits):,}",
                help="One hero in one browser tab. A refresh is the same visit.")
    k[1].metric("Played at least one riddle", f"{(visits['answers'] > 0).sum():,}")
    k[2].metric("First-try accuracy", f"{first['correct'].mean():.0%}" if len(first) else "–")
    k[3].metric("Median visit", f"{visits['minutes'].median():.0f} min")
    k[4].metric("Finished the game", f"{wins['visit'].nunique():,}")

    # --- who plays --------------------------------------------------------
    st.header("Who plays")
    left, right = st.columns(2)
    per_day = visits.groupby(visits["start"].dt.date).size().rename("Visits")
    left.subheader("Visits per day")
    left.bar_chart(per_day, y_label="Visits", x_label="")
    right.subheader("By grade")
    g = visits.groupby("grade").agg(
        Visits=("gems", "size"),
        **{"Median minutes": ("minutes", "median"),
           "Median gems at the end": ("gems", "median"),
           "Median answers": ("answers", "median")})
    g["New heroes"] = how[how == "new"].groupby(visits["grade"]).size()
    g["Came back with a code"] = how[how == "code"].groupby(visits["grade"]).size()
    g["Finished"] = wins.groupby("grade")["visit"].nunique()
    g = g.fillna(0).loc[sorted(g.index, key=gorder)]
    g.index = [curriculum.grade(x).name if x in label else x for x in g.index]
    right.dataframe(g.round(1), width="stretch")

    # --- how far they get ---------------------------------------------------
    st.header("How far they get")
    st.caption("Per region: how many visits went in, how many won the gem, how many "
               "walked out without it, and how many times the hero ran out of health.")
    ev = df[df["region"].notna()]

    def per_region(e):
        n = lambda name: e[e["event"] == name]["visit"].nunique()   # noqa: E731
        won_q = e[e["event"] == "region_won"]
        trials = e[e["event"] == "trial_done"]
        passed = trials[col(trials, "passed", False).fillna(False).astype(bool)]
        tried = e[e["event"] == "region_start"]["visit"].nunique()
        won = pd.concat([won_q["visit"], passed["visit"]]).nunique()
        return pd.Series({
            "Visits that entered": tried,
            "Won the gem": won,
            "Win rate": 100 * won / tried if tried else None,
            "Won by quest": won_q["visit"].nunique(),
            "Won by speed trial": passed["visit"].nunique(),
            "Trials failed": len(trials) - len(passed),
            "Left without winning": n("region_left"),
            "Defeats": (e["event"] == "defeat").sum(),
            "Median minutes to win (quest)": minutes(won_q["seconds"].median()),
        })

    table = ev.groupby(["grade", "region"]).apply(per_region, include_groups=False)
    order = {(gr, r["key"]): i for gr in label for i, r
             in enumerate(curriculum.grade(gr).regions)}
    table = table.loc[sorted(table.index, key=lambda ix: (gorder(ix[0]),
                                                         order.get(ix, 99)))]
    table.index = [f"{gr} · {label.get(gr, ({}, {}))[0].get(r, r)}"
                   for gr, r in table.index]
    st.dataframe(table, width="stretch", height=min(36 * len(table) + 40, 1300),
                 column_config={"Win rate": st.column_config.ProgressColumn(
                     format="%.0f%%", min_value=0, max_value=100)})

    st.subheader("Gems won by the end of the visit")
    gem_dist = visits.groupby("gems").size().rename("Visits")
    gem_dist.index = gem_dist.index.astype(int).astype(str)
    st.bar_chart(gem_dist, y_label="Visits", x_label="Gems")

    # --- where they get stuck ---------------------------------------------
    st.header("Where they get stuck")
    st.caption("Per skill, first tries only (the hinted second try is not counted). "
               "Lowest accuracy first. A **level down** happens after two misses in "
               "a row; the sage then gives a tip.")
    if len(first):
        grp = first.groupby(["grade", "topic"])
        skills = pd.DataFrame({
            "Answers": grp.size(),
            "First-try accuracy": 100 * grp["correct"].mean(),
            "Median seconds": grp["seconds"].median().round(0),
            "Average level": grp["tier"].mean().round(1),
            "Levels up": grp["change"].apply(lambda c: (c == 1).sum()),
            "Levels down": grp["change"].apply(lambda c: (c == -1).sum()),
        })
        lost = df[df["event"] == "defeat"].groupby(["grade", "topic"]).size()
        skills["Defeats on it"] = lost.reindex(skills.index).fillna(0).astype(int)
        quit_ = df[df["event"] == "region_left"].groupby(["grade", "topic"]).size()
        skills["Walked out on it"] = quit_.reindex(skills.index).fillna(0).astype(int)
        skills = skills.sort_values("First-try accuracy")
        skills.index = [f"{gr} · {label.get(gr, ({}, {}))[1].get(t, t)}"
                        for gr, t in skills.index]
        st.dataframe(skills, width="stretch", column_config={
            "First-try accuracy": st.column_config.ProgressColumn(
                format="%.0f%%", min_value=0, max_value=100)})

        st.subheader("Accuracy by skill and level")
        st.caption("First tries. Blank: never asked at that level.")
        pivot = first.pivot_table(index=["grade", "topic"], columns="tier",
                                  values="correct", aggfunc="mean")
        counts = first.pivot_table(index=["grade", "topic"], columns="tier",
                                   values="correct", aggfunc="size")
        shown = pivot.map(lambda v: "" if pd.isna(v) else f"{v:.0%}")
        shown = shown.where(counts.isna(), shown + counts.map(
            lambda c: "" if pd.isna(c) else f"  (n={int(c)})"))
        shown.columns = [f"Level {int(c)}" for c in shown.columns]
        shown = shown.loc[by_grade(shown.index)]
        shown.index = [f"{gr} · {label.get(gr, ({}, {}))[1].get(t, t)}"
                       for gr, t in shown.index]
        st.dataframe(shown, width="stretch")

    st.subheader("Where visits end")
    st.caption("The last thing that happened in each visit that played at least one "
               "riddle and did not finish the game. Visits that went quiet in "
               "the middle of a region are where children gave up.")
    last = df.sort_values("ts").groupby("visit").tail(1)
    last = last[~last["visit"].isin(wins["visit"])
                & last["visit"].isin(visits.index[visits["answers"] > 0])]
    if len(last):
        what = {"answer": "answering a riddle", "region_left": "left a region",
                "region_won": "just won a gem", "trial_done": "finished a speed trial",
                "defeat": "ran out of health", "region_retry": "retrying after a defeat",
                "region_start": "just entered a region", "start": "on the map"}
        where = last.apply(lambda r: (
            f"{r['grade']} · {label.get(r['grade'], ({}, {}))[0].get(r['region'], '–')}"
            if isinstance(r["region"], str) else f"{r['grade']} · map"), axis=1)
        ends = (pd.DataFrame({"Where": where, "Doing": last["event"].map(what)
                              .fillna(last["event"])})
                .value_counts().rename("Visits").reset_index())
        st.dataframe(ends, width="stretch", hide_index=True)

    # --- the actual misses ------------------------------------------------
    st.header("Wrong answers")
    misses = ans[ans["correct"] == False]   # noqa: E712
    if len(misses):
        opts = by_grade(set(zip(misses["grade"], misses["topic"])))
        sel = st.selectbox("Skill", opts, format_func=lambda o: (
            f"{o[0]} · {label.get(o[0], ({}, {}))[1].get(o[1], o[1])}"))
        m = misses[(misses["grade"] == sel[0]) & (misses["topic"] == sel[1])]
        st.dataframe(
            m.sort_values("ts", ascending=False)[
                ["ts", "tier", "attempt", "question", "given", "expected", "seconds"]
            ].rename(columns={"ts": "When", "tier": "Level", "attempt": "Try",
                              "question": "Question", "given": "Answered",
                              "expected": "Right answer", "seconds": "Seconds"}),
            width="stretch", hide_index=True,
            column_config={"When": st.column_config.DatetimeColumn(
                format="YYYY-MM-DD HH:mm")})
    else:
        st.caption("No wrong answers yet.")

    st.download_button("⬇️ Download all events (CSV)", df.to_csv(index=False),
                       file_name=f"math-quest-usage-{datetime.date.today()}.csv",
                       mime="text/csv")


main()
