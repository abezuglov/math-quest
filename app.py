"""The Number Thief of Arithmos - a math text quest for 4th graders.

Run locally:  streamlit run app.py
"""
import datetime
import html

import streamlit as st

import config
import curriculum
import pictures
import story
from engine import TRIAL_PASS, TRIAL_QUESTIONS, Game

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
.code {font-family:ui-monospace,Consolas,monospace; font-size:1.25rem; font-weight:700;
       letter-spacing:.08em;}
.ledger {font-family:ui-monospace,Consolas,monospace; font-size:1.2rem;}
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


def note(inner_html):
    st.markdown(f"<div class='note'>{inner_html}</div>", unsafe_allow_html=True)


def picture(svg, wide=False):
    if svg:
        st.image(svg, width="stretch" if wide else "content")


def new_game(game):
    st.session_state.game = game
    st.session_state.pop("celebrated", None)


def end_game():
    """Back to the title screen. A teacher's ?grade= link (the grade that was in
    the address when the page was first opened, before any hero) is kept, so the
    next child does not have to pick it again. A grade a child picked is not."""
    st.session_state.pop("celebrated", None)
    st.session_state.pop("game", None)
    st.session_state.pop("grade_pick", None)
    grade = st.session_state.get("link_grade")
    st.query_params.clear()
    if grade:
        st.query_params["grade"] = grade


def start_game(make):
    """Start a hero with make(), or show the teacher why it cannot start
    (every topic of that grade switched off). Returns what make() returns, or
    False when the grade cannot be played."""
    try:
        return make()
    except ValueError as e:
        st.error(f"This grade cannot be played: {e}. A teacher can switch a topic "
                 "back on with `enabled = true` in that file.")
        return False


def sync_url(g):
    """Keep the hero code in the page address, so a refresh does not lose the hero."""
    code = g.to_code()
    if (st.query_params.get("hero") != code or st.query_params.get("name") != g.name
            or st.query_params.get("grade") != g.grade):
        st.query_params["hero"] = code
        st.query_params["name"] = g.name
        st.query_params["grade"] = g.grade


def grades_offered():
    """The grades a child may pick: listed in config.py AND having a content file."""
    return [c for c in config.GRADES if c in curriculum.load_all()]


def grade_from_link():
    """The grade in the page address or in config.py, if valid."""
    for code in (st.query_params.get("grade"), config.DEFAULT_GRADE):
        code = str(code).strip().upper() if code else ""
        if code in grades_offered():
            return code
    return None


def grade_name(code):
    return curriculum.grade(code).name


# ---------------------------------------------------------------------------
def title_screen():
    st.title("🐉 " + story.TITLE)
    picture(pictures.scene("peak"), wide=True)
    st.markdown(story.PROLOGUE)
    fixed = grade_from_link()
    grade = fixed or st.session_state.get("grade_pick")
    if grade is None:
        st.markdown("### 🎓 Which grade are you in?")
        cols = st.columns(3)
        for i, code in enumerate(grades_offered()):
            if cols[i % 3].button(grade_name(code), key=f"grade_{code}", type="primary",
                                  width="stretch"):
                st.session_state.grade_pick = code
                st.rerun()
    else:
        st.markdown(f"🎓 **{grade_name(grade)}**")
        with st.form("start"):
            name = st.text_input("What is your hero's name?", max_chars=20)
            go = st.form_submit_button("Begin the quest ⚔️", type="primary")
        game = start_game(lambda: Game(name.strip() or "Hero", grade)) if go else None
        if game:
            new_game(game)
            st.rerun()
        if not fixed and st.button("Pick another grade", key="grade_again"):
            st.session_state.pop("grade_pick", None)
            st.rerun()
    with st.expander("🔑 I played before and have a hero code"):
        with st.form("resume"):
            old_name = st.text_input("Hero's name", max_chars=20, key="resume_name")
            code = st.text_input("Hero code (like 4ABC-DEFG-HJKM-NPQR)", max_chars=40,
                                 key="resume_code")
            back = st.form_submit_button("Continue my quest 🗺️")
        if back:
            game = start_game(lambda: Game.from_code(old_name.strip() or "Hero", code))
            if game is None:
                st.warning("That code does not look right. Check each letter and "
                           "number and try again.")
            elif game:
                new_game(game)
                st.rerun()
    with st.expander("How to play"):
        st.markdown(
            "- **The map:** pick any place to visit. Dragon's Peak opens when you "
            "have won the other gems.\n"
            "- **Quest:** the full story of a place, with friends, monsters and a boss.\n"
            f"- **Speed trial:** {TRIAL_QUESTIONS} quick riddles. Get {TRIAL_PASS} "
            "right and the gem is yours. Good for math you already know.\n"
            "- **Friends** ask riddles. A right answer earns XP. If you miss, you get "
            "a hint and one more try.\n"
            "- **Monsters** fight! A right answer hits the monster. A wrong answer "
            "costs you HP: a close answer is only a scratch, one that is far off "
            "hurts more.\n"
            "- Coming back to a place whose gem you already have is practice: it "
            "pays half XP.\n"
            "- Get three in a row and the riddles get harder and are worth **more XP**.\n"
            "- Type fractions like `3/4` and decimals like `0.75`.\n"
            "- Write down your **hero code** to carry on another day. Reloading "
            "the page takes you back to the map.")


def sidebar(g):
    with st.sidebar:
        st.markdown("### 🗺️ Quest map")
        here = g.phase not in ("map", "story", "victory")
        for i, r in enumerate(g.regions):
            status = g.status(i)
            mark = {"done": "💎", "open": "▫️", "locked": "🔒"}[status]
            if here and i == g.region_idx:
                mark = "📍"
            st.markdown(f"{mark} {r['emoji']} {r['name']}")
        if g.phase in ("region_intro", "question", "task", "feedback", "defeat"):
            st.button("⬅️ Back to the map", on_click=g.leave_region, key="side_leave",
                      help="Leave this place. You keep your XP.")
        st.markdown("### ⭐ Skill levels")
        for t in g.topics:
            st.markdown(f"{g.label(t)}  \n{'⭐' * g.tiers[t]}{'☆' * (5 - g.tiers[t])}")
        if g.streak >= 3:
            st.markdown(f"🔥 Streak: **{g.streak}** in a row!")
        st.markdown("### 🔑 Hero code")
        st.markdown(f"<span class='code'>{g.to_code()}</span>", unsafe_allow_html=True)
        st.caption("Write it down to carry on another day.")
        with st.expander("🎓 Change grade"):
            st.caption(f"Now playing **{grade_name(g.grade)}**. Changing the grade starts "
                       "a NEW hero in that grade. This hero's code above stays valid: "
                       "write it down to come back to it.")
            pick = st.selectbox("New grade", grades_offered(), index=None,
                                format_func=grade_name, key="side_grade",
                                placeholder="Pick a grade")
            sure = st.checkbox("Yes, start a new hero in that grade", key="side_grade_sure")
            if st.button("Change grade", disabled=not (sure and pick)):
                name = g.name
                st.session_state.pop("side_grade", None)
                st.session_state.pop("side_grade_sure", None)
                game = start_game(lambda: Game(name, pick))
                if game:
                    new_game(game)
                    st.rerun()
        with st.expander("Teacher"):
            st.caption("Starts a brand new game for a new player. "
                       "This hero's gems and XP are erased.")
            sure = st.checkbox("Yes, erase this hero", key="side_sure")
            if st.button("Restart game", disabled=not sure):
                st.session_state.pop("side_sure", None)
                end_game()
                st.rerun()


def hud(g):
    pct = max(0, g.hp) / config.MAX_HP * 100
    color = "#2e9e5b" if pct >= 60 else "#e0a020" if pct >= config.LOW_HP else "#d64545"
    st.markdown(
        f"""<div class="hud">
        <span class="who">🧒 {esc(g.name)}</span>
        <span>🎓 {esc(grade_name(g.grade))}</span>
        <span>🎖️ {esc(g.rank)}</span>
        <span>✨ {g.xp} XP</span>
        <span>💎 {len(g.done)}/{len(g.regions)}</span>
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
    label = {"fight": "Monster", "boss": "BOSS", "healer": "Healer",
             "task": "Hands-on task", "trial": "Speed trial"}.get(spec["kind"], "Friend")
    st.markdown(
        f"""<div class="npc {'foe' if foe else ''}">
        <div class="face">{spec['emoji']}</div>
        <div><div class="name">{esc(spec['name'])} <small>({label})</small></div>
        {hearts}<div>“{esc(line)}”</div></div></div>""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
def map_screen(g):
    places = [(r["key"], r["name"], g.status(i)) for i, r in enumerate(g.regions)]
    picture(pictures.kingdom_map(places), wide=True)
    if g.all_done:
        st.success("💎 Every gem is home! Arithmos is safe. You can still visit any "
                   "place for quick practice.")
        st.button("See your certificate 📜", type="primary", on_click=g.show_certificate)
    elif not g.done:
        st.markdown("**Where will you go first?** Want to practice as you go? Start "
                    f"a **quest**. Feeling sure? Try the **speed trial**: {TRIAL_PASS} "
                    f"right out of {TRIAL_QUESTIONS} wins the gem straight away. "
                    "There is no clock.")
    else:
        st.markdown("**Where to next, hero?**")
    for i, r in enumerate(g.regions):
        status = g.status(i)
        skills = ", ".join(g.label(t) for t in r["topics"] if t in g.topics)
        if r.get("mix"):
            skills = f"{skills}, then everything mixed" if skills else "Everything mixed"
        with st.container(border=True):
            left, right = st.columns([3, 2], vertical_alignment="center")
            gem = {"done": f"💎 {r['gem']} won", "open": "Gem not won yet",
                   "locked": "🔒 Win the other gems first"}[status]
            left.markdown(f"**{r['emoji']} {r['name']}**  \n{skills}  \n{gem}")
            if status == "done":
                right.button("Quick practice ⚡", key=f"t_{i}", type="primary",
                             help="5 riddles. Practice pays half XP.",
                             width="stretch", on_click=g.choose_region, args=(i, "trial"))
                right.button("Replay the story 📖", key=f"q_{i}", width="stretch",
                             on_click=g.choose_region, args=(i, "quest"))
            elif status == "open":
                right.button("Start quest ⚔️", key=f"q_{i}", type="primary",
                             width="stretch", on_click=g.choose_region, args=(i, "quest"))
                if g.can_trial(i):
                    right.button("Speed trial ⚡", key=f"t_{i}", width="stretch",
                                 on_click=g.choose_region, args=(i, "trial"))
    note(f"🔑 Your hero code: <span class='code'>{g.to_code()}</span><br>"
         "Write it down. Next time, type it on the first screen to get your gems, "
         "levels and XP back. (Reloading the page brings you back here, to the map.)")


def region_intro(g):
    r = g.region
    picture(pictures.scene(r["key"]), wide=True)
    st.header(f"{r['emoji']} {r['name']}")
    st.markdown(r["intro"])
    note(f"💎 Win back the <b>{esc(r['gem'])}</b>. Your health is restored to full.")
    st.button(f"Enter {r['name']} ➡️", type="primary", on_click=g.start_region)
    st.button("⬅️ Back to the map", on_click=g.leave_region, key="intro_leave")
    focus('button[kind="primary"]')


def question_screen(g):
    enc, q = g.enc, g.question
    spec = enc["spec"]
    r = g.region
    trial = enc["kind"] == "trial"
    if trial:
        st.caption(f"{r['emoji']} {r['name']}  ·  ⚡ Speed trial: riddle {enc['asked']} "
                   f"of {enc['total']}  ·  ✅ {enc['right']} right so far  ·  "
                   f"{g.label(q.topic)}, level {q.tier}")
    else:
        st.caption(f"{r['emoji']} {r['name']}  ·  {g.label(q.topic)}  ·  "
                   f"Level {q.tier} riddle")
    foe = enc["kind"] in ("fight", "boss")
    if trial:
        if enc["asked"] == 1:
            npc_box(spec, f"{enc['total']} riddles. Get {TRIAL_PASS} right"
                          + (" and the gem is yours. " if enc["prove"]
                             else " to keep your gem shining. ")
                          + "There is no clock, so take your time.")
    else:
        if enc["asked"] == 1:
            line = spec["intro"]
        else:
            line = "You won't get the next one!" if foe else spec["intro"]
        npc_box(spec, line, enc)
    if enc["potion"]:
        note("🧪 <b>Potion riddle!</b> Answer right to win back some health.")

    fb = g.feedback
    if enc["attempt"] == 1 and fb is not None:
        note(f"🤔 <b>{esc(fb.your_answer)}</b> is not quite right. "
             f"<br>💡 <b>Hint:</b> {esc(q.hint)}<br>Try once more for half the XP.")
        if fb.sage_tip:
            note(f"🦉 <b>{story.SAGE_NAME} whispers:</b> {esc(fb.sage_tip)}")

    st.markdown(f"<div class='question'>{esc(q.text)}</div>", unsafe_allow_html=True)
    picture(pictures.for_question(q.picture))

    if q.kind == "choice":
        cols = st.columns(len(q.choices))
        for col, choice in zip(cols, q.choices):
            col.button(choice, key=f"c_{g.qcount}_{enc['attempt']}_{choice}",
                       width="stretch", on_click=g.submit, args=(choice,))
    else:
        label = {"fraction": "Your answer (type a fraction like 3/4)",
                 "decimal": "Your answer (type a decimal like 0.75)"}.get(q.kind, "Your answer")
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
        st.caption("Tip: not sure? Estimate and give your best try. A closer "
                   "answer costs less health.")


def task_controls(g):
    """Draw the controls for a hands-on task. Returns (value, button label)."""
    task, d = g.task, g.task.data
    key = f"task_{g.qcount}"
    if task.kind == "coins":
        chosen = st.pills("Coin bags (tap to pick, tap again to put back)", d["bags"],
                          selection_mode="multi", format_func=lambda v: f"💰 {v:,}",
                          key=key)
        return list(chosen or []), "Pay ✅"
    if task.kind == "multiples":
        chosen = st.pills("Bats (tap to catch, tap again to let go)", d["numbers"],
                          selection_mode="multi", format_func=lambda v: f"🦇 {v}",
                          key=key)
        return list(chosen or []), "Catch them ✅"
    if task.kind == "share":
        each = st.slider("Crates on EACH boat", 0, d["max_each"], 0, key=key)
        picture(pictures.share_fig(d["n"], d["boats"], each))
        left = st.number_input("How many crates are left over on the dock?",
                               min_value=0, max_value=d["n"], value=0, step=1,
                               key=key + "_left")
        return (each, left), "Cast off ✅"
    if task.kind == "shade":
        shaded = st.slider("Pieces to shade", 0, d["parts"], 0, key=key)
        picture(pictures.shade_bars(d["a"], d["b"], d["parts"], shaded))
        return shaded, "Cut the loaf ✅"
    if task.kind == "garden":
        c1, c2 = st.columns(2)
        length = c1.slider("Length (meters)", 1, d["max"], 1, key=key + "_l")
        width = c2.slider("Width (meters)", 1, d["max"], 1, key=key + "_w")
        picture(pictures.garden_fig(length, width, d["max"]))
        st.caption("Each small square is 1 square meter.")
        return (length, width), "Build it ✅"
    lines = [f"Line {i + 1}:   {text} = {total:,}" for i, (text, total) in enumerate(d["lines"])]
    pick = st.radio("Which line has the mistake?", range(len(lines)),
                    format_func=lambda i: lines[i], index=None, key=key)
    return pick, "This line is wrong ✅"


def task_screen(g):
    enc, task = g.enc, g.task
    spec, r = enc["spec"], g.region
    st.caption(f"{r['emoji']} {r['name']}  ·  {g.label(task.topic)}  ·  "
               f"🖐️ Hands-on task, level {task.tier}")
    npc_box(spec, spec["intro"])
    fb = g.feedback
    if enc["attempt"] == 1 and fb is not None:
        note(f"🤔 You tried <b>{esc(fb.your_answer)}</b>. Not quite. "
             f"<br>💡 <b>Hint:</b> {esc(task.hint)}<br>Change it and try once more.")
    st.markdown(f"<div class='question'>{esc(task.prompt)}</div>", unsafe_allow_html=True)
    value, label = task_controls(g)
    if st.button(label, type="primary", key=f"task_go_{g.qcount}_{enc['attempt']}"):
        # Pressing the button before touching anything is not an answer.
        untouched = {"coins": value == [], "multiples": value == [],
                     "share": value == (0, 0), "shade": value == 0,
                     "garden": value == (1, 1), "ledger": value is None}[task.kind]
        if untouched:
            st.warning("Pick a line first." if task.kind == "ledger" else
                       "Tap or slide to make your answer first.")
        else:
            g.submit_task(value)
            st.rerun()


def feedback_screen(g):
    fb, enc = g.feedback, g.enc
    spec = enc["spec"]
    foe = enc["kind"] in ("fight", "boss")
    trial = enc["kind"] == "trial"
    if fb.correct:
        gain = "(XP already earned here)" if fb.replay else f"+{fb.xp} XP"
        if foe:
            st.success(f"⚔️ Direct hit! **{fb.answer_text}** is right.  {gain}")
        elif fb.is_task:
            st.success(f"✅ You did it! {gain}")
            note(f"📖 {esc(fb.explanation)}")
        else:
            st.success(f"✅ Correct! **{fb.answer_text}** is right.  {gain}")
        if fb.heal:
            st.info(f"🧪 The potion restores {fb.heal} health.")
        if trial:
            pass
        elif fb.encounter_over:
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
                     "heavy": "That one was a long way off, and the hit was hard."}[fb.severity]
            st.error(f"💥 {words}  −{fb.damage} health")
        else:
            st.error("❌ Not this time.")
        tried = "You tried" if fb.is_task else "You answered"
        note(f"{tried} <b>{esc(fb.your_answer)}</b>. "
             f"The right answer is <b>{esc(fb.answer_text)}</b>.<br>"
             f"📖 {esc(fb.explanation)}")
        if fb.sage_tip:
            note(f"🦉 <b>{story.SAGE_NAME} appears:</b> {esc(fb.sage_tip)}")
    if trial:
        st.caption(f"⚡ Speed trial: {enc['right']} right out of {enc['asked']} so far "
                   f"({enc['total']} riddles in all).")

    topic = g.label(fb.topic)
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
    if g.is_last_region:
        picture(pictures.story_art("finale"), wide=True)
    st.header(f"💎 {r['gem']} recovered!" if g.just_won else f"💎 {r['name']}: done again!")
    st.markdown(r["outro"])
    if r.get("memory"):
        note(f"🕯️ <b>A memory of the old days</b><br>{esc(r['memory'])}")
    label = "See your certificate 📜" if g.is_last_region else "Back to the map 🗺️"
    st.button(label, type="primary", on_click=g.next_region)
    focus('button[kind="primary"]')


def trial_done(g):
    r, res = g.region, g.trial_result
    score = f"**{res['right']} out of {res['total']}**"
    if res["passed"]:
        if res["new_gem"]:
            st.header(f"💎 {r['gem']} recovered!")
            st.markdown(f"⚡ {score} in the speed trial. You already know your way "
                        f"around {r['name']}, so the gem flies straight into your "
                        f"hand.  \n🏆 Bonus +{res['bonus']} XP")
        else:
            st.header("⚡ Speed trial passed!")
            st.markdown(f"{score}. The {r['gem']} shines a little brighter.")
        st.button("Back to the map 🗺️", type="primary", on_click=g.leave_trial)
        st.button("Another round ⚡", on_click=g.retry_trial)
    else:
        st.header("⚡ Not this time")
        st.markdown(f"{score}. You need {TRIAL_PASS} to pass. "
                    + ("So close! Try again, or take the **quest** to practice first."
                       if res["right"] == TRIAL_PASS - 1
                       else "No harm done: the full **quest** teaches this step by "
                            "step, with hints along the way."))
        st.button("Back to the map 🗺️", type="primary", on_click=g.leave_trial)
        st.button("Try the trial again ⚡", on_click=g.retry_trial)
    focus('button[kind="primary"]')


def story_screen(g):
    beat = g.beat
    picture(pictures.story_art(beat["art"]), wide=True)
    st.header(f"📜 {beat['title']}")
    st.markdown(beat["text"])
    st.button("Continue ➡️", type="primary", on_click=g.continue_story,
              key=f"story_{g.beats_seen}")
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
    st.button("⬅️ Back to the map", on_click=g.leave_region, key="defeat_leave")
    focus('button[kind="primary"]')


def victory_screen(g):
    if not st.session_state.get("celebrated"):
        st.balloons()
        st.session_state.celebrated = True
    rows = ""
    for row in g.summary():
        acc = f"{row['accuracy']}%" if row["accuracy"] is not None else "–"
        rows += (f"<tr><td style='text-align:left'>{g.label(row['topic'])}</td>"
                 f"<td>{row['right']} / {row['asked']}</td><td>{acc}</td>"
                 f"<td>{'⭐' * row['tier']}</td></tr>")
    right = sum(s[0] for s in g.stats.values())
    asked = sum(s[1] for s in g.stats.values())
    st.markdown(
        f"""<div class="cert">
        <div>📜 Kingdom of Arithmos · Certificate of Heroism</div>
        <h2>{esc(g.name)}</h2>
        <div>returned the stolen numbers and earned the rank of</div>
        <div class="big">🎖️ {esc(g.rank)}</div>
        <div>✨ {g.xp} XP · 💎 {len(g.done)} gems · today: {right} of {asked} first
             tries right · best streak {g.best_streak} · {datetime.date.today():%B %d, %Y}</div>
        <table style="margin:14px auto 0; border-collapse:collapse;">
        <tr><th style='text-align:left'>Skill</th><th>Right today</th><th>Accuracy</th>
            <th>Highest level</th></tr>
        {rows}
        </table></div>""",
        unsafe_allow_html=True,
    )
    st.caption("Show this screen to your teacher! (Teachers: Ctrl+P prints it.)")
    st.button("Back to the map 🗺️", type="primary", on_click=g.back_to_map)
    with st.expander("Start over with a brand new hero"):
        st.caption("This hero's gems and XP are erased.")
        sure = st.checkbox("Yes, erase this hero", key="end_sure")
        if st.button("Play again from the beginning 🔁", disabled=not sure):
            st.session_state.pop("end_sure", None)
            end_game()
            st.rerun()


SCREENS = {
    "map": map_screen,
    "region_intro": region_intro,
    "question": question_screen,
    "task": task_screen,
    "feedback": feedback_screen,
    "region_done": region_done,
    "trial_done": trial_done,
    "story": story_screen,
    "defeat": defeat_screen,
    "victory": victory_screen,
}


def main():
    if "link_grade" not in st.session_state:
        # First run of this visit. A ?grade= with no hero is a teacher's link;
        # one next to a hero was written by sync_url and is not.
        st.session_state.link_grade = (None if st.query_params.get("hero")
                                       else st.query_params.get("grade"))
    if "game" not in st.session_state and st.query_params.get("hero"):
        # The page was refreshed or bookmarked: bring the hero back from the address.
        name = (st.query_params.get("name") or "Hero").strip()[:20] or "Hero"
        game = start_game(lambda: Game.from_code(name, st.query_params.get("hero")))
        if game is None:
            st.query_params.clear()
        elif game:
            new_game(game)
    if "game" not in st.session_state:
        title_screen()
        return
    g = st.session_state.game
    sync_url(g)
    sidebar(g)
    hud(g)
    SCREENS[g.phase](g)


main()
