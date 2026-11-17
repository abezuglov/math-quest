"""Game rules: XP, HP, damage, adaptive difficulty and progress through the story.

Pure Python (no Streamlit) so it can be tested on its own.
"""
from __future__ import annotations

import random
import time
from dataclasses import dataclass

import config
import curriculum
import questions
import story
import tasks
from curriculum import show_answer
from questions import is_correct, parse_answer, severity

# Settings are kept inside safe limits, so a typo in config.py cannot make the
# game unwinnable.
TRIAL_QUESTIONS = max(1, int(getattr(config, "TRIAL_QUESTIONS", 5)))
TRIAL_PASS = max(1, min(TRIAL_QUESTIONS, int(getattr(config, "TRIAL_PASS", 4))))
TRIAL_MIN_TIER = getattr(config, "TRIAL_MIN_TIER", 3)
TASK_XP_FACTOR = getattr(config, "TASK_XP_FACTOR", 2)

# Hero codes: letters and digits that are hard to mix up (no I, L, O, U).
_B32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
_V1_LEN = 12               # the old 4th-grade-only code
_V2_MIN_DIGITS = 15        # so a v2 code (16+ characters) is never mistaken for v1
_XP_BITS = 17
_TOPIC_BITS = 5            # a grade may have up to 31 topics
_CHECK = 16381             # prime; the check value fits in 14 bits


def _clean_code(code: str) -> str:
    text = (code or "").upper().replace("O", "0").replace("I", "1").replace("L", "1")
    return "".join(ch for ch in text if ch.isalnum())


def _digits(v: int, n: int) -> str:
    out = ""
    for _ in range(n):
        out = _B32[v & 31] + out
        v >>= 5
    assert v == 0, "code value does not fit"
    return out


def _value(digits: str) -> int:
    v = 0
    for ch in digits:
        v = v * 32 + _B32.index(ch)
    return v


def _check(v: int, grade: str) -> int:
    """Check value of a v2 code. The grade letter is mixed in, so a typo in the
    first character is caught too instead of opening another grade."""
    return (v * 7 + curriculum.GRADE_ORDER.index(str(grade).upper()) + 1) % _CHECK


def encode_code(grade: str, gems: list, levels: list, xp: int, beats: int) -> str:
    """Hero code v2: the grade, then base-32 digits holding (high to low) the
    gems (6 bits), one level per topic in file order (3 bits each), XP (17
    bits), story pages (2 bits), the topic count (5 bits) and a check value
    (14 bits). The length grows with the number of topics; dashes every 4."""
    if not 1 <= len(levels) < 2 ** _TOPIC_BITS:
        raise ValueError("a grade may have 1 to 31 topics")
    v = 0
    for won in gems:
        v = (v << 1) | bool(won)
    for level in levels:
        v = (v << 3) | max(1, min(5, int(level)))
    v = (v << _XP_BITS) | max(0, min(int(xp), 2 ** _XP_BITS - 1))
    v = (v << 2) | max(0, min(int(beats), 3))
    v = (v << _TOPIC_BITS) | len(levels)
    v = v * 16384 + _check(v, grade)
    bits = len(gems) + 3 * len(levels) + _XP_BITS + 2 + _TOPIC_BITS + 14
    n = max(_V2_MIN_DIGITS, -(-bits // 5))
    n = -(-(n + 1) // 4) * 4 - 1          # grade + digits is a multiple of 4
    text = str(grade).upper() + _digits(v, n)
    return "-".join(text[i:i + 4] for i in range(0, len(text), 4))


def decode_code(code: str):
    """(grade, gems, levels, xp, beats) from a hero code, or None if it is not
    valid. Old 12-character codes (no grade letter) are 4th grade."""
    text = _clean_code(code)
    if len(text) == _V1_LEN and all(ch in _B32 for ch in text):
        return _decode_v1(text)
    grade, digits = text[:1], text[1:]
    if (grade not in curriculum.load_all() or len(text) % 4 or len(text) < 16
            or any(ch not in _B32 for ch in digits)):
        return None
    v = _value(digits)
    check, v = v % 16384, v // 16384
    if _check(v, grade) != check:
        return None
    count = v & (2 ** _TOPIC_BITS - 1)
    v >>= _TOPIC_BITS
    beats = v & 3
    v >>= 2
    xp = v & (2 ** _XP_BITS - 1)
    v >>= _XP_BITS
    levels = []
    for _ in range(count):
        levels.insert(0, v & 7)
        v >>= 3
    gems = []
    for _ in range(len(curriculum.REGION_KEYS)):
        gems.insert(0, bool(v & 1))
        v >>= 1
    if v or not count or any(not 1 <= x <= 5 for x in levels):
        return None
    return grade, gems, levels, xp, beats


def _decode_v1(text: str):
    """The old code: always the original seven 4th-grade topics and six gems."""
    v = _value(text)
    check, v = v % 16384, v // 16384
    if v % _CHECK != check:
        return None
    beats = v & 3
    v >>= 2
    xp = v & (2 ** _XP_BITS - 1)
    v >>= _XP_BITS
    levels = []
    for _ in questions.ALL_TOPICS:
        levels.insert(0, v & 7)
        v >>= 3
    gems = []
    for _ in curriculum.REGION_KEYS:
        gems.insert(0, bool(v & 1))
        v >>= 1
    if v or any(not 1 <= x <= 5 for x in levels):
        return None
    return "4", gems, levels, xp, beats

# Rank thresholds for a full 4th-grade game. A grade with fewer encounters
# (see config.ENCOUNTERS_BY_GRADE) scales them down, so every grade can reach
# the top rank.
RANKS = [
    (0, "Apprentice"),
    (300, "Squire"),
    (800, "Number Scout"),
    (1400, "Number Knight"),
    (2000, "Number Champion"),
    (2500, "Legend of Arithmos"),
]


def rank_for(xp: int, scale: float = 1.0) -> str:
    name = RANKS[0][1]
    for need, title in RANKS:
        if xp >= round(need * scale / 10) * 10:
            name = title
    return name


def _encounter_weight(regions) -> int:
    """Roughly how many right answers a perfect run of these regions takes."""
    hits = {"riddle": 1, "fight": config.MONSTER_HITS, "boss": config.BOSS_HITS,
            "task": TASK_XP_FACTOR}
    total = 0
    for r in regions:
        for e in r["encounters"]:
            total += (config.FINAL_BOSS_HITS if e.get("hp") == "final"
                      else hits.get(e["kind"], 1))
    return total


_FULL_WEIGHT = _encounter_weight(story.REGIONS)


def _clamp(tier: int) -> int:
    lo = max(1, min(5, config.MIN_TIER))
    hi = max(lo, min(5, config.MAX_TIER))
    return max(lo, min(hi, tier))


@dataclass
class Feedback:
    correct: bool
    topic: str
    answer_text: str = ""
    your_answer: str = ""
    explanation: str = ""
    severity: str | None = None
    damage: int = 0
    xp: int = 0
    bonus: int = 0
    heal: int = 0
    retry: bool = False           # riddle: gets a hint and a second try
    encounter_over: bool = False
    defeated: bool = False        # player ran out of HP
    tier_change: int = 0
    sage_tip: str = ""
    rank_up: str = ""
    replay: bool = False
    is_task: bool = False


class Game:
    def __init__(self, name: str, grade: str = "4", seed: int | None = None):
        self.name = name
        self.grade = str(grade).upper()
        self.content = curriculum.grade(self.grade)     # the grade's topics and regions
        self.rng = random.Random(seed)
        self.hp = config.MAX_HP
        self.xp = 0
        self.topics = [t for t, topic in self.content.topics.items() if topic.enabled]
        if not self.topics:
            raise ValueError(f"Every topic of grade {self.grade} is switched off "
                             f"in {self.content.source}")
        self.tiers = {t: _clamp(config.START_TIER) for t in self.topics}
        self.best_tiers = dict(self.tiers)
        self.right_run = {t: 0 for t in self.topics}
        self.wrong_run = {t: 0 for t in self.topics}
        self.stats = {t: [0, 0] for t in self.topics}   # [correct, asked]
        self.streak = 0
        self.best_streak = 0
        self.defeats = 0
        limit = getattr(config, "ENCOUNTERS_BY_GRADE", {}).get(self.grade)
        limit = max(1, int(limit)) if limit else None
        self.regions = [story.build_region(r, limit) for r in self.content.regions
                        if r.get("mix") or any(t in self.topics for t in r["topics"])]
        self.rank_scale = max(0.2, _encounter_weight(self.regions) / _FULL_WEIGHT)
        self.region_idx = 0
        self.enc_idx = 0
        # map | region_intro | question | task | feedback | region_done |
        # trial_done | story | defeat | victory
        self.phase = "map"
        self.mode = None           # "quest" or "trial" while inside a region
        self.half = False          # region already won: practice pays half XP
        self._other_done = set()   # from a hero code: gems of regions switched off
        self._other_tiers = {}     # from a hero code: levels of topics switched off
        self.done = set()          # keys of the regions whose gem is won
        self.beats_seen = 0        # story pages already shown
        self.just_won = False      # the region just finished gave a NEW gem
        self.trial_result = None
        self.enc = None
        self.question = None
        self.task = None
        self.feedback = None
        self.input_error = ""
        self.qcount = 0
        self.last_topic = None
        self._paid = {}            # region key -> {encounter index: answers paid}
        self.region_paid = {}      # the entry of _paid for the current region
        self.region_defeats = 0
        self._bags = {}
        n = sum(1 for r in self.regions if not r.get("final"))
        # Story pages appear after the 1st and 3rd gem and when the Peak opens.
        self._beat_at = [min(1, n), min(3, n), n][:len(story.BEATS)] if n else []
        # Usage events for the stats (see usage.py). The app takes them out
        # after every click; nothing here names the child.
        self.events = []
        self._clock = time.monotonic
        self._asked_at = None      # when the current question/task appeared
        self._region_at = None     # when the current quest or trial began

    # ------------------------------------------------------------------
    def _log(self, event, **data):
        """Note a usage event (every one happens in a region: it says which)."""
        data.setdefault("region", self.region["key"])
        data.setdefault("mode", self.mode)
        data["event"] = event
        data["gems"] = len(self.done)
        data["xp"] = self.xp
        self.events.append(data)
        del self.events[:-500]     # never grows without end if nobody collects them

    def _since(self, t0):
        return round(self._clock() - t0, 1) if t0 is not None else None

    def _log_answer(self, item, correct, fb, given):
        enc = self.enc
        text = getattr(item, "text", None) or getattr(item, "prompt", "")  # task: prompt
        self._log("answer", kind=enc["kind"], topic=item.topic, tier=item.tier,
                  correct=correct, attempt=enc["attempt"] + 1,
                  seconds=self._since(self._asked_at), potion=bool(enc["potion"]),
                  task=fb.is_task, change=fb.tier_change, sage=bool(fb.sage_tip),
                  damage=fb.damage, question=str(text)[:300],
                  given=str(given)[:80], expected=str(fb.answer_text)[:80])
        self._asked_at = self._clock()   # a retry is timed from here

    def label(self, topic: str) -> str:
        return self.content.topics[topic].label

    def tip(self, topic: str) -> str:
        return self.content.topics[topic].tip

    def standard(self, topic: str) -> str:
        return self.content.topics[topic].standard

    @property
    def rank(self) -> str:
        return rank_for(self.xp, self.rank_scale)

    @property
    def region(self):
        return self.regions[self.region_idx]

    @property
    def is_last_region(self):
        return bool(self.region.get("final"))

    @property
    def all_done(self):
        return all(r["key"] in self.done for r in self.regions)

    def status(self, i):
        """'done', 'open' or 'locked' for region number i."""
        r = self.regions[i]
        if r["key"] in self.done:
            return "done"
        if r.get("final") and any(o["key"] not in self.done
                                  for o in self.regions if not o.get("final")):
            return "locked"
        return "open"

    def can_trial(self, i):
        """The final region's story must be played in full once."""
        r = self.regions[i]
        return self.status(i) != "locked" and (not r.get("final") or r["key"] in self.done)

    def _beats_due(self):
        won = sum(1 for r in self.regions
                  if not r.get("final") and r["key"] in self.done)
        return sum(1 for need in self._beat_at if need <= won)

    @property
    def beat(self):
        return story.BEATS[self.beats_seen]

    def _pick_topic(self, kind):
        region = self.region
        if region.get("mix") and kind in ("fight", "boss", "trial"):
            pool = self.topics
        else:
            pool = [t for t in region["topics"] if t in self.topics] or self.topics
        key = tuple(pool)
        if not self._bags.get(key):
            bag = list(pool)
            self.rng.shuffle(bag)
            self._bags[key] = bag
        return self._bags[key].pop()

    def _begin_encounter(self, healer=False):
        spec = story.HEALER if healer else self.region["encounters"][self.enc_idx]
        kind = spec["kind"]
        if kind == "task":
            topic = self.region["task_topic"]
            lo, hi = self.region.get("task_levels", (1, 5))
            tier = max(lo, min(hi, _clamp(self.tiers.get(topic, config.START_TIER))))
            self.enc = {"spec": spec, "kind": kind, "attempt": 0, "asked": 1,
                        "potion": False, "monster_hp": 0, "monster_max": 0}
            self.task = tasks.generate(spec["task"], tier, self.rng, topic=topic,
                                       gentle=self.grade in ("K", "1"))
            self.question = None
            self.feedback = None
            self.input_error = ""
            self.qcount += 1
            self._asked_at = self._clock()
            self.phase = "task"
            return
        hits = 0
        if kind == "fight":
            hits = config.MONSTER_HITS
        elif kind == "boss":
            hits = config.FINAL_BOSS_HITS if spec.get("hp") == "final" else config.BOSS_HITS
        self.enc = {
            "spec": spec,
            "kind": kind,
            "attempt": 0,
            "asked": 0,
            "potion": kind == "healer" or (kind == "riddle" and self.hp < config.LOW_HP),
            "monster_hp": hits,
            "monster_max": hits,
        }
        self._new_question()

    def _new_question(self):
        enc = self.enc
        topic = self._pick_topic(enc["kind"])
        tier = self.tiers[topic]
        if enc["potion"]:
            tier -= 1
        if enc["kind"] == "boss":
            tier = max(tier, 2)
        if enc["kind"] == "trial" and enc["prove"]:
            tier = max(tier, TRIAL_MIN_TIER)   # skipping the quest must be earned
        tier = _clamp(tier)
        old_text = self.question.text if self.question else None
        for _ in range(6):
            q = curriculum.generate(self.content.topics[topic], tier, self.rng)
            if q.text != old_text or q.kind == "choice":
                break
        self.question = q
        self.last_topic = topic
        enc["attempt"] = 0
        enc["asked"] += 1
        self.qcount += 1
        self.feedback = None
        self.input_error = ""
        self._asked_at = self._clock()
        self.phase = "question"

    def _record(self, topic, correct):
        """Update stats and the adaptive tier. Returns (tier_change, sage)."""
        self.stats[topic][1] += 1
        change, sage = 0, False
        if correct:
            self.stats[topic][0] += 1
            self.streak += 1
            self.best_streak = max(self.best_streak, self.streak)
            self.wrong_run[topic] = 0
            self.right_run[topic] += 1
            if self.right_run[topic] >= config.UP_AFTER:
                self.right_run[topic] = 0
                if self.tiers[topic] < config.MAX_TIER:
                    self.tiers[topic] += 1
                    change = 1
        else:
            self.streak = 0
            self.right_run[topic] = 0
            self.wrong_run[topic] += 1
            if self.wrong_run[topic] >= config.DOWN_AFTER:
                self.wrong_run[topic] = 0
                sage = True
                if self.tiers[topic] > config.MIN_TIER:
                    self.tiers[topic] -= 1
                    change = -1
        self.best_tiers[topic] = max(self.best_tiers[topic], self.tiers[topic])
        return change, sage

    # ------------------------------------------------------------------
    # Actions called by the screens
    # ------------------------------------------------------------------
    def choose_region(self, i, mode="quest"):
        """Picked on the map. mode: 'quest' (full story) or 'trial' (5 questions)."""
        if self.phase != "map" or not 0 <= i < len(self.regions):
            return
        if self.status(i) == "locked" or (mode == "trial" and not self.can_trial(i)):
            return
        self.region_idx = i
        self.enc_idx = 0
        self.enc = self.question = self.task = self.feedback = None
        self.mode = mode
        self.half = self.region["key"] in self.done
        if mode == "trial":
            self._start_trial()
        else:
            self.phase = "region_intro"

    def leave_region(self):
        """Back to the map from inside a region. XP is kept, the quest is not."""
        if self.phase not in ("region_intro", "question", "task", "feedback", "defeat"):
            return
        if self.phase != "region_intro":     # from the intro: never went in
            self._log("region_left", stage=self.phase, encounter=self.enc_idx,
                      topic=self.question.topic if self.phase == "question" else None,
                      seconds=self._since(self._region_at))
        self._region_at = None
        self.enc = self.question = self.task = self.feedback = None
        self.input_error = ""
        self.hp = config.MAX_HP
        self.phase = "map"

    def start_region(self):
        if self.phase != "region_intro":
            return
        self.region_paid = self._paid.setdefault(self.region["key"], {})
        self.region_defeats = 0
        self._region_at = self._clock()
        self._log("region_start", encounters=len(self.region["encounters"]),
                  replay=self.half)
        self._enter_region()

    # --- speed trial ---------------------------------------------------
    def _start_trial(self):
        self.trial_result = None
        self.half = self.region["key"] in self.done
        self.enc = {"spec": story.TRIAL_HOST, "kind": "trial", "attempt": 0,
                    "asked": 0, "right": 0, "total": TRIAL_QUESTIONS,
                    "potion": False, "monster_hp": 0, "monster_max": 0,
                    "prove": self.region["key"] not in self.done}
        self._region_at = self._clock()
        self._log("region_start", encounters=TRIAL_QUESTIONS, replay=self.half)
        self._new_question()

    def retry_trial(self):
        if self.phase == "trial_done":
            self._start_trial()

    def leave_trial(self):
        if self.phase == "trial_done":
            self._after_region()

    def _after_region(self):
        self.enc = self.question = self.task = self.feedback = None
        self.phase = "story" if self.beats_seen < self._beats_due() else "map"

    def continue_story(self):
        if self.phase != "story":
            return
        self.beats_seen += 1
        self._after_region()

    def show_certificate(self):
        if self.phase == "map" and self.all_done:
            self.phase = "victory"

    def back_to_map(self):
        if self.phase == "victory":
            self._after_region()

    def _enter_region(self):
        self.hp = config.MAX_HP
        self.enc_idx = 0
        self._begin_encounter()

    def submit(self, raw: str) -> bool:
        """Check an answer. Returns False if the input could not be read."""
        if self.phase != "question":
            return False
        q, enc = self.question, self.enc
        if q.kind == "choice":
            if raw not in q.choices:
                self.input_error = "Pick one of the choices."
                return False
            value = raw
        else:
            value = parse_answer(raw)
            if value is None:
                like = {"fraction": " or a fraction like 3/4",
                        "decimal": " or a decimal like 0.75"}.get(q.kind, "")
                self.input_error = f"I couldn't read that. Type a number like 42{like}."
                return False
        self.input_error = ""
        correct = is_correct(q, value)
        if enc["kind"] == "trial":
            return self._submit_trial(q, value, correct)
        fight = enc["kind"] in ("fight", "boss")
        first = enc["attempt"] == 0
        old_rank = self.rank
        fb = Feedback(correct=correct, topic=q.topic, answer_text=show_answer(q),
                      your_answer=show_answer(q, value), explanation=q.explanation)
        if fight or first:
            fb.tier_change, sage = self._record(q.topic, correct)
            if sage:
                fb.sage_tip = self.tip(q.topic)

        if correct:
            xp = config.XP_BASE * q.tier
            if not fight and not first:
                xp //= 2
            if self.streak >= 3:
                xp += config.STREAK_BONUS
            # Replaying part of a region after a defeat pays no XP twice.
            if enc["kind"] == "healer":
                fb.replay = self.region_defeats > 0
            else:
                step = enc["monster_max"] - enc["monster_hp"] if fight else 0
                fb.replay = self.region_paid.get(self.enc_idx, 0) > step
                if not fb.replay:
                    self.region_paid[self.enc_idx] = step + 1
            fb.xp = 0 if fb.replay else xp
            if self.half:
                fb.xp //= 2
            if fight:
                enc["monster_hp"] -= 1
                if enc["monster_hp"] <= 0:
                    fb.encounter_over = True
                    if not fb.replay:
                        fb.bonus = (config.BOSS_BONUS if enc["kind"] == "boss"
                                    else config.MONSTER_BONUS) // (2 if self.half else 1)
            else:
                fb.encounter_over = True
                if enc["potion"]:
                    fb.heal = min(config.POTION_HEAL, config.MAX_HP - self.hp)
                    self.hp += fb.heal
            self.xp += fb.xp + fb.bonus
        elif fight:
            fb.severity = severity(q, value)
            # Pip's glow-shield: each defeat in a region softens later hits.
            fb.damage = max(1, round(config.DAMAGE[fb.severity]
                                     * config.SHIELD_FACTOR ** self.region_defeats))
            self.hp = max(0, self.hp - fb.damage)
            fb.defeated = self.hp <= 0
        elif first and q.kind != "choice":   # two buttons: a retry would be a giveaway
            fb.retry = True
            enc["attempt"] = 1
        else:
            fb.encounter_over = True

        new_rank = self.rank
        if new_rank != old_rank:
            fb.rank_up = new_rank
        self.feedback = fb
        self._log_answer(q, correct, fb, fb.your_answer)
        # A missed riddle goes straight back to the question with a hint.
        self.phase = "question" if fb.retry else "feedback"
        return True

    def _submit_trial(self, q, value, correct):
        enc = self.enc
        old_rank = self.rank
        fb = Feedback(correct=correct, topic=q.topic, answer_text=show_answer(q),
                      your_answer=show_answer(q, value), explanation=q.explanation)
        fb.tier_change, sage = self._record(q.topic, correct)
        if sage:
            fb.sage_tip = self.tip(q.topic)
        if correct:
            enc["right"] += 1
            fb.xp = config.XP_BASE * q.tier + (config.STREAK_BONUS if self.streak >= 3 else 0)
            if self.half:
                fb.xp //= 2
            self.xp += fb.xp
        fb.encounter_over = enc["asked"] >= enc["total"]
        if self.rank != old_rank:
            fb.rank_up = self.rank
        self.feedback = fb
        self._log_answer(q, correct, fb, fb.your_answer)
        self.phase = "feedback"
        return True

    def submit_task(self, value) -> bool:
        """Check a hands-on task. One hint and a second try, like a riddle."""
        if self.phase != "task":
            return False
        task, enc = self.task, self.enc
        correct = tasks.check(task, value)
        first = enc["attempt"] == 0
        old_rank = self.rank
        fb = Feedback(correct=correct, topic=task.topic, answer_text=task.solution,
                      your_answer=tasks.describe(task, value),
                      explanation=task.explanation, is_task=True)
        if first and task.topic in self.topics:
            fb.tier_change, sage = self._record(task.topic, correct)
            if sage:
                fb.sage_tip = self.tip(task.topic)
        elif first:
            self.streak = self.streak + 1 if correct else 0
            self.best_streak = max(self.best_streak, self.streak)
        if correct:
            xp = config.XP_BASE * task.tier * (TASK_XP_FACTOR if first else 1)
            if self.streak >= 3:
                xp += config.STREAK_BONUS
            fb.replay = self.region_paid.get(self.enc_idx, 0) > 0
            if not fb.replay:
                self.region_paid[self.enc_idx] = 1
            fb.xp = 0 if fb.replay else xp
            if self.half:
                fb.xp //= 2
            self.xp += fb.xp
            fb.encounter_over = True
        elif first:
            fb.retry = True
            enc["attempt"] = 1
        else:
            fb.encounter_over = True
        if self.rank != old_rank:
            fb.rank_up = self.rank
        self.feedback = fb
        self._log_answer(task, correct, fb, fb.your_answer)
        self.phase = "task" if fb.retry else "feedback"
        return True

    def _win_gem(self):
        key = self.region["key"]
        self.just_won = key not in self.done
        self.done.add(key)
        self._paid.pop(key, None)

    def advance(self):
        """Move on from the feedback screen."""
        fb = self.feedback
        if self.phase != "feedback" or fb is None:
            return
        if self.enc["kind"] == "trial":
            if not fb.encounter_over:
                self._new_question()
                return
            right = self.enc["right"]
            passed = right >= TRIAL_PASS
            bonus = 0
            self.just_won = False
            if passed:
                self._win_gem()
                if self.just_won:
                    bonus = config.BOSS_BONUS
                    self.xp += bonus
            self.trial_result = {"right": right, "total": self.enc["total"],
                                 "passed": passed, "new_gem": self.just_won,
                                 "bonus": bonus}
            self._log("trial_done", right=right, total=self.enc["total"], passed=passed,
                      new_gem=self.just_won, seconds=self._since(self._region_at))
            self.feedback = None
            self.phase = "trial_done"
            return
        if fb.defeated:
            self.defeats += 1
            self._log("defeat", encounter=self.enc_idx, kind=self.enc["kind"],
                      topic=fb.topic, seconds=self._since(self._region_at))
            self.phase = "defeat"
            return
        if not fb.encounter_over:
            self._new_question()
            return
        was_healer = self.enc["kind"] == "healer"
        if not was_healer:
            self.enc_idx += 1
        encounters = self.region["encounters"]
        if self.enc_idx >= len(encounters):
            self.feedback = None
            self._win_gem()
            self._log("region_won", new_gem=self.just_won, defeats=self.region_defeats,
                      seconds=self._since(self._region_at))
            self.phase = "region_done"
            return
        nxt = encounters[self.enc_idx]
        need_healer = (nxt["kind"] in ("fight", "boss")
                       and self.hp < config.LOW_HP and not was_healer)
        self._begin_encounter(healer=need_healer)

    def retry_region(self):
        """After running out of HP: full health, slightly easier, same region."""
        if self.phase != "defeat":
            return
        if self.last_topic:
            t = self.last_topic
            self.tiers[t] = _clamp(self.tiers[t] - 1)
            self.wrong_run[t] = 0
        self.region_defeats += 1
        self._log("region_retry", defeats=self.region_defeats)
        self._enter_region()

    def next_region(self):
        if self.phase != "region_done":
            return
        if self.is_last_region:
            self.enc = self.question = self.task = None
            self.phase = "victory"
            self._log("victory", defeats=self.defeats, best_streak=self.best_streak)
            return
        self._after_region()

    # --- hero code: grade, gems, skill levels, XP and story pages ---------
    def to_code(self) -> str:
        topics = list(self.content.topics)
        gems = [r["key"] in self.done or r["key"] in self._other_done
                for r in self.content.regions]
        levels = [self.tiers.get(t, self._other_tiers.get(t, config.START_TIER))
                  for t in topics]
        return encode_code(self.grade, gems, levels, self.xp, self.beats_seen)

    @classmethod
    def from_code(cls, name: str, code: str, seed: int | None = None):
        """Rebuild a hero from a code. Returns None if the code is not valid."""
        decoded = decode_code(code)
        if decoded is None:
            return None
        grade, gems, levels, xp, beats = decoded
        content = curriculum.grade(grade)
        topics = list(content.topics)
        # A topic added to the end of the file after the code was made starts
        # at the usual level; extra levels for topics since removed are dropped.
        levels = (levels + [config.START_TIER] * len(topics))[:len(topics)]
        tiers = dict(zip(topics, levels))
        done = {r["key"] for r, won in zip(content.regions, gems) if won}
        g = cls(name, grade, seed)
        g.xp = xp
        g.tiers = {t: _clamp(tiers[t]) for t in g.topics}
        g.best_tiers = dict(g.tiers)
        g.done = {r["key"] for r in g.regions if r["key"] in done}
        # Keep what belongs to regions and topics the teacher has switched off,
        # so it is not lost if they are switched on again.
        g._other_done = done - g.done
        g._other_tiers = {t: x for t, x in tiers.items() if t not in g.topics}
        # A story page that was due but not read yet is shown first.
        g.beats_seen = min(beats, g._beats_due(), len(story.BEATS))
        if g.beats_seen < g._beats_due():
            g.phase = "story"
        return g

    # ------------------------------------------------------------------
    def summary(self):
        """Per-topic results for the certificate."""
        rows = []
        for t in self.topics:
            right, asked = self.stats[t]
            rows.append({
                "topic": t,
                "standard": self.standard(t),
                "right": right,
                "asked": asked,
                "accuracy": round(100 * right / asked) if asked else None,
                "tier": self.best_tiers[t],
            })
        return rows

    def practiced_standards(self):
        """Common Core codes of the topics answered at least once, in file order."""
        codes = []
        for t in self.topics:
            code = self.standard(t)
            if self.stats[t][1] and code and code not in codes:
                codes.append(code)
        return codes
