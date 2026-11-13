"""The Number Thief of Arithmos - a math text quest for 4th graders.

Run locally:  streamlit run app.py
"""
import datetime
import html

import streamlit as st

import config
import story
from engine import RANKS, Game, rank_for
from questions import TOPIC_LABELS

st.set_page_config(page_title=story.TITLE, page_icon="🐉", layout="centered")

CSS = """
<style>
.block-container {max-width: 760px; padding-top: 2.2rem;}
.hud {display:flex; gap:14px; align-items:center; flex-wrap:wrap;
      padding:10px 14px; border-radius:12px; margin-bottom:10px;
      background:rgba(128,128,128,.12); font-size:1rem;}
.hud .who {font-weight:700;}
.hud .bar {flex:1; min-width:140px; height:16px; border-radius:8px;
           background:rgba(128,128,128,.3); overflow:hidden;}
.hud .fill {height:100%; border-radius:8px;}
.npc {display:flex; gap:14px; align-items:flex-start; padding:14px 16px;
      border-radius:14px; background:rgba(120,100,220,.13); margin:8px 0;}
.npc.foe {background:rgba(220,90,70,.14);}
.npc .face {font-size:3rem; line-height:1;}
.npc .name {font-weight:700; font-size:1.05rem;}
.npc .hearts {letter-spacing:2px;}
.question {font-size:1.45rem; font-weight:600; line-height:1.4; padding:16px 18px;
           border-radius:14px; border:2px solid rgba(128,128,128,.45); margin:10px 0;}
.note {padding:10px 14px; border-radius:10px; margin:8px 0;
       background:rgba(128,128,128,.12);}
.cert {text-align:center; padding:26px 20px; border-radius:16px;
       border:4px double rgba(200,160,40,.9); background:rgba(230,190,60,.10);}
.cert h2 {margin:.2rem 0;}
.cert .big {font-size:2rem; font-weight:800;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def focus(selector):
    """Put the keyboard cursor on the answer box / Continue button."""
    st.session_state["_focus_n"] = st.session_state.get("_focus_n", 0) + 1
    st.html(
        f"""<script>
        // run {st.session_state["_focus_n"]}
        setTimeout(function() {{
          try {{
            // On touch screens, don't pop the keyboard up on every question.
            if (window.matchMedia('(pointer: coarse)').matches) return;
            const els = document.querySelectorAll('{selector}');
            if (els.length) els[els.length - 1].focus();
          }} catch (e) {{}}
        }}, 200);
        </script>""",
        unsafe_allow_javascript=True,
    )


def esc(text):
    return html.escape(str(text))


# ---------------------------------------------------------------------------
def title_screen():
    st.title("🐉 " + story.TITLE)
    st.markdown(story.PROLOGUE)
    with st.form("start"):
        name = st.text_input("What is your hero's name?", max_chars=20)
        go = st.form_submit_button("Begin the quest ⚔️", type="primary")
    if go:
        st.session_state.game = Game(name.strip() or "Hero")
        st.rerun()
    with st.expander("How to play"):
        st.markdown(
            "- **Friends** ask riddles. A right answer earns XP. If you miss, you get "
            "a hint and one more try.\n"
            "- **Monsters** fight! A right answer hits the monster. A wrong answer "
            "costs you HP: a close answer is only a scratch, a wild guess hurts a lot.\n"
            "- Get three in a row and the riddles get harder and are worth **more XP**.\n"
            "- Type fractions like `3/4`.")


def sidebar(g):
    with st.sidebar:
        st.markdown(f"### 🗺️ Quest map")
        for i, r in enumerate(g.regions):
            done = i < g.region_idx or g.phase == "victory"
            mark = "✅" if done else ("📍" if i == g.region_idx else "🔒")
            st.markdown(f"{mark} {r['emoji']} {r['name']}")
        st.markdown("### ⭐ Skill levels")
        for t in g.topics:
            st.markdown(f"{TOPIC_LABELS[t]}  \n{'⭐' * g.tiers[t]}{'☆' * (5 - g.tiers[t])}")
        if g.streak >= 3:
            st.markdown(f"🔥 Streak: **{g.streak}** in a row!")
        with st.expander("Teacher"):
            st.caption("Starts a brand new game for a new player.")
            if st.button("Restart game"):
                st.session_state.pop("celebrated", None)
                del st.session_state["game"]
                st.rerun()


def hud(g):
    pct = max(0, g.hp) / config.MAX_HP * 100
    color = "#2e9e5b" if pct >= 60 else "#e0a020" if pct >= config.LOW_HP else "#d64545"
    st.markdown(
        f"""<div class="hud">
        <span class="who">🧒 {esc(g.name)}</span>
        <span>🎖️ {esc(rank_for(g.xp))}</span>
        <span>✨ {g.xp} XP</span>
        <span>❤️ {g.hp}/{config.MAX_HP}</span>
        <div class="bar"><div class="fill" style="width:{pct}%;background:{color}"></div></div>
        </div>""",
        unsafe_allow_html=True,
    )


def npc_box(spec, line, enc=None):
    foe = spec["kind"] in ("fight", "boss")
    hearts = ""
    if foe and enc:
        hearts = ("<div class='hearts'>" + "💜" * enc["monster_hp"]
                  + "🖤" * (enc["monster_max"] - enc["monster_hp"]) + "</div>")
    label = {"fight": "Monster", "boss": "BOSS", "healer": "Healer"}.get(spec["kind"], "Friend")
    st.markdown(
        f"""<div class="npc {'foe' if foe else ''}">
        <div class="face">{spec['emoji']}</div>
        <div><div class="name">{esc(spec['name'])} <small>({label})</small></div>
        {hearts}<div>“{esc(line)}”</div></div></div>""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
def region_intro(g):
    r = g.region
    st.header(f"{r['emoji']} Region {g.region_idx + 1}: {r['name']}")
    st.markdown(r["intro"])
    st.markdown(f"<div class='note'>💎 Win back the <b>{esc(r['gem'])}</b>. "
                f"Your health is restored to full.</div>", unsafe_allow_html=True)
    st.button(f"Enter {r['name']} ➡️", type="primary", on_click=g.start_region)
    focus('button[kind="primary"]')


def question_screen(g):
    enc, q = g.enc, g.question
    spec = enc["spec"]
    r = g.region
    st.caption(f"{r['emoji']} {r['name']}  ·  {TOPIC_LABELS[q.topic]}  ·  "
               f"Level {q.tier} riddle")
    foe = enc["kind"] in ("fight", "boss")
    if enc["asked"] == 1:
        line = spec["intro"]
    else:
        line = "You won't get the next one!" if foe else spec["intro"]
    npc_box(spec, line, enc)
    if enc["potion"]:
        st.markdown("<div class='note'>🧪 <b>Potion riddle!</b> Answer right to "
                    "win back some health.</div>", unsafe_allow_html=True)

    fb = g.feedback
    if enc["attempt"] == 1 and fb is not None:
        st.markdown(f"<div class='note'>🤔 <b>{esc(fb.your_answer)}</b> is not quite right. "
                    f"<br>💡 <b>Hint:</b> {esc(q.hint)}<br>"
                    f"Try once more for half the XP.</div>", unsafe_allow_html=True)
        if fb.sage_tip:
            st.markdown(f"<div class='note'>🦉 <b>{story.SAGE_NAME} whispers:</b> "
                        f"{esc(fb.sage_tip)}</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='question'>{esc(q.text)}</div>", unsafe_allow_html=True)

    if q.kind == "choice":
        cols = st.columns(len(q.choices))
        for col, choice in zip(cols, q.choices):
            col.button(choice, key=f"c_{g.qcount}_{enc['attempt']}_{choice}",
                       width="stretch", on_click=g.submit, args=(choice,))
    else:
        label = ("Your answer (type a fraction like 3/4)" if q.kind == "fraction"
                 else "Your answer")
        with st.form(f"f_{g.qcount}_{enc['attempt']}", clear_on_submit=True):
            raw = st.text_input(label, key=f"a_{g.qcount}_{enc['attempt']}",
                                max_chars=20)
            sent = st.form_submit_button("Attack! ⚔️" if foe else "Answer ✅",
                                         type="primary")
        if sent:
            g.submit(raw)
            st.rerun()
        focus('input[type="text"]')
    if g.input_error:
        st.warning(g.input_error)
    if foe:
        st.caption("Tip: if you are not sure, estimate! A close answer costs "
                   "much less health than a wild guess.")


def feedback_screen(g):
    fb, enc = g.feedback, g.enc
    spec = enc["spec"]
    foe = enc["kind"] in ("fight", "boss")
    if fb.correct:
        gain = "(XP already earned here)" if fb.replay else f"+{fb.xp} XP"
        if foe:
            st.success(f"⚔️ Direct hit! **{fb.answer_text}** is right.  {gain}")
        else:
            st.success(f"✅ Correct! **{fb.answer_text}** is right.  {gain}")
        if fb.heal:
            st.info(f"🧪 The potion restores {fb.heal} health.")
        if fb.encounter_over:
            npc_box(spec, spec["win"], enc)
            if fb.bonus:
                st.info(f"🏆 {spec['name']} is defeated! Bonus +{fb.bonus} XP")
        else:
            npc_box(spec, "Ouch! That one stung.", enc)
        if g.streak >= 3:
            st.caption(f"🔥 {g.streak} in a row! Streak bonus included.")
    else:
        if foe:
            words = {"light": "So close! Only a scratch.",
                     "medium": "Not quite. That hit hurt a bit.",
                     "heavy": "That guess was far off, and the hit was hard!"}[fb.severity]
            st.error(f"💥 {words}  −{fb.damage} health")
        else:
            st.error("❌ Not this time.")
        st.markdown(
            f"<div class='note'>You answered <b>{esc(fb.your_answer)}</b>. "
            f"The right answer is <b>{esc(fb.answer_text)}</b>.<br>"
            f"📖 {esc(fb.explanation)}</div>", unsafe_allow_html=True)
        if fb.sage_tip:
            st.markdown(f"<div class='note'>🦉 <b>{story.SAGE_NAME} appears:</b> "
                        f"{esc(fb.sage_tip)}</div>", unsafe_allow_html=True)

    topic = TOPIC_LABELS[fb.topic]
    if fb.tier_change > 0:
        st.info(f"📈 You're on a roll! {topic} riddles get tougher now, "
                f"and they are worth more XP.")
    elif fb.tier_change < 0:
        st.info(f"🌱 Let's practice with slightly easier {topic} riddles for a bit.")
    if fb.rank_up:
        st.success(f"🎖️ New rank: **{fb.rank_up}**!")
        st.balloons()

    st.button("Continue ➡️", type="primary", on_click=g.advance)
    focus('button[kind="primary"]')


def region_done(g):
    r = g.region
    st.header(f"💎 {r['gem']} recovered!")
    st.markdown(r["outro"])
    label = "See your certificate 📜" if g.is_last_region else "Travel onward 🗺️"
    st.button(label, type="primary", on_click=g.next_region)
    focus('button[kind="primary"]')


def defeat_screen(g):
    r = g.region
    st.header("😵 Out of energy!")
    st.markdown(
        f"Pip the Firefly carries you safely back to the start of **{r['name']}**. "
        f"Every hero needs more than one try. Your XP is safe, the riddles will be a "
        f"little gentler, and Pip's **glow-shield** will soften the monsters' hits. "
        f"(Parts you already beat here won't give XP a second time.)")
    st.button("Try again 💪", type="primary", on_click=g.retry_region)
    focus('button[kind="primary"]')


def victory_screen(g):
    if not st.session_state.get("celebrated"):
        st.balloons()
        st.session_state.celebrated = True
    rows = ""
    for row in g.summary():
        acc = f"{row['accuracy']}%" if row["accuracy"] is not None else "–"
        rows += (f"<tr><td style='text-align:left'>{TOPIC_LABELS[row['topic']]}</td>"
                 f"<td>{row['right']} / {row['asked']}</td><td>{acc}</td>"
                 f"<td>{'⭐' * row['tier']}</td></tr>")
    right = sum(s[0] for s in g.stats.values())
    asked = sum(s[1] for s in g.stats.values())
    st.markdown(
        f"""<div class="cert">
        <div>📜 Kingdom of Arithmos · Certificate of Heroism</div>
        <h2>{esc(g.name)}</h2>
        <div>returned the stolen numbers and earned the rank of</div>
        <div class="big">🎖️ {esc(rank_for(g.xp))}</div>
        <div>✨ {g.xp} XP · {right} of {asked} first tries right ·
             best streak {g.best_streak} · {datetime.date.today():%B %d, %Y}</div>
        <table style="margin:14px auto 0; border-collapse:collapse;">
        <tr><th style='text-align:left'>Skill</th><th>Right</th><th>Accuracy</th>
            <th>Highest level</th></tr>
        {rows}
        </table></div>""",
        unsafe_allow_html=True,
    )
    st.caption("Show this screen to your teacher! (Teachers: Ctrl+P prints it.)")
    if st.button("Play again 🔁"):
        del st.session_state["game"]
        st.session_state.pop("celebrated", None)
        st.rerun()


SCREENS = {
    "region_intro": region_intro,
    "question": question_screen,
    "feedback": feedback_screen,
    "region_done": region_done,
    "defeat": defeat_screen,
    "victory": victory_screen,
}


def main():
    if not any(config.TOPICS.values()):
        st.error("No math topics are turned on. Teacher: set at least one topic "
                 "to True in config.py.")
        st.stop()
    if "game" not in st.session_state:
        title_screen()
        return
    g = st.session_state.game
    sidebar(g)
    hud(g)
    SCREENS[g.phase](g)


main()
