"""Game rules: XP, HP, damage, adaptive difficulty and progress through the story.

Pure Python (no Streamlit) so it can be tested on its own.
"""
from __future__ import annotations

import random
from dataclasses import dataclass

import config
import story
from questions import (ALL_TOPICS, TOPIC_TIPS, fmt, generate, is_correct,
                       parse_answer, severity)

RANKS = [
    (0, "Apprentice"),
    (300, "Squire"),
    (800, "Number Scout"),
    (1400, "Number Knight"),
    (2000, "Number Champion"),
    (2500, "Legend of Arithmos"),
]


def rank_for(xp: int) -> str:
    name = RANKS[0][1]
    for need, title in RANKS:
        if xp >= need:
            name = title
    return name


def _clamp(tier: int) -> int:
    return max(config.MIN_TIER, min(config.MAX_TIER, tier))


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


class Game:
    def __init__(self, name: str, seed: int | None = None):
        self.name = name
        self.rng = random.Random(seed)
        self.hp = config.MAX_HP
        self.xp = 0
        self.topics = [t for t in ALL_TOPICS if config.TOPICS.get(t)]
        if not self.topics:
            raise ValueError("Turn on at least one topic in config.py")
        self.tiers = {t: _clamp(config.START_TIER) for t in self.topics}
        self.best_tiers = dict(self.tiers)
        self.right_run = {t: 0 for t in self.topics}
        self.wrong_run = {t: 0 for t in self.topics}
        self.stats = {t: [0, 0] for t in self.topics}   # [correct, asked]
        self.streak = 0
        self.best_streak = 0
        self.defeats = 0
        self.regions = [r for r in story.REGIONS
                        if r.get("mix") or any(t in self.topics for t in r["topics"])]
        self.region_idx = 0
        self.enc_idx = 0
        self.phase = "region_intro"   # region_intro | question | feedback |
                                      # region_done | defeat | victory
        self.enc = None
        self.question = None
        self.feedback = None
        self.input_error = ""
        self.qcount = 0
        self.last_topic = None
        self.region_paid = {}      # encounter index -> answers already paid XP
        self.region_defeats = 0
        self._bags = {}

    # ------------------------------------------------------------------
    @property
    def region(self):
        return self.regions[self.region_idx]

    @property
    def is_last_region(self):
        return self.region_idx == len(self.regions) - 1

    def _pick_topic(self, kind):
        region = self.region
        if region.get("mix") and kind in ("fight", "boss"):
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
        tier = _clamp(tier)
        old_text = self.question.text if self.question else None
        for _ in range(6):
            q = generate(topic, tier, self.rng)
            if q.text != old_text or q.kind == "choice":
                break
        self.question = q
        self.last_topic = topic
        enc["attempt"] = 0
        enc["asked"] += 1
        self.qcount += 1
        self.feedback = None
        self.input_error = ""
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
    def start_region(self):
        if self.phase != "region_intro":
            return
        self.region_paid = {}
        self.region_defeats = 0
        self._enter_region()

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
                self.input_error = "Pick one of the two fractions."
                return False
            value = raw
        else:
            value = parse_answer(raw)
            if value is None:
                self.input_error = ("I couldn't read that. Type a number like 42"
                                    + (" or a fraction like 3/4." if q.kind == "fraction" else "."))
                return False
        self.input_error = ""
        correct = is_correct(q, value)
        fight = enc["kind"] in ("fight", "boss")
        first = enc["attempt"] == 0
        old_rank = rank_for(self.xp)
        fb = Feedback(correct=correct, topic=q.topic, answer_text=fmt(q.answer),
                      your_answer=fmt(value), explanation=q.explanation)
        if fight or first:
            fb.tier_change, sage = self._record(q.topic, correct)
            if sage:
                fb.sage_tip = TOPIC_TIPS[q.topic]

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
            if fight:
                enc["monster_hp"] -= 1
                if enc["monster_hp"] <= 0:
                    fb.encounter_over = True
                    if not fb.replay:
                        fb.bonus = (config.BOSS_BONUS if enc["kind"] == "boss"
                                    else config.MONSTER_BONUS)
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

        new_rank = rank_for(self.xp)
        if new_rank != old_rank:
            fb.rank_up = new_rank
        self.feedback = fb
        # A missed riddle goes straight back to the question with a hint.
        self.phase = "question" if fb.retry else "feedback"
        return True

    def advance(self):
        """Move on from the feedback screen."""
        fb = self.feedback
        if self.phase != "feedback" or fb is None:
            return
        if fb.defeated:
            self.defeats += 1
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
        self._enter_region()

    def next_region(self):
        if self.phase != "region_done":
            return
        if self.is_last_region:
            self.phase = "victory"
            return
        self.region_idx += 1
        self.enc_idx = 0
        self.enc = None
        self.question = None
        self.phase = "region_intro"

    # ------------------------------------------------------------------
    def summary(self):
        """Per-topic results for the certificate."""
        rows = []
        for t in self.topics:
            right, asked = self.stats[t]
            rows.append({
                "topic": t,
                "right": right,
                "asked": asked,
                "accuracy": round(100 * right / asked) if asked else None,
                "tier": self.best_tiers[t],
            })
        return rows
