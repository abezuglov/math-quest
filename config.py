"""Teacher settings for The Number Thief of Arithmos.

Change the values here, save, and restart the app.
"""

# --- Grades -----------------------------------------------------------------
# The math content lives in curriculum/grade_*.toml (see curriculum/FORMAT.md).
# To switch a topic off, set `enabled = false` on it in the grade file.
GRADES = ["K", "1", "2", "3", "4", "5"]   # grades offered on the title screen
DEFAULT_GRADE = None   # e.g. "3" to skip the grade buttons; None = ask (or ?grade= in the link)

# --- Difficulty tiers (1 = easiest, 5 = hardest) ----------------------------
# Every topic has its own tier per child. Clamp the range for the whole class here.
MIN_TIER = 1
MAX_TIER = 5
START_TIER = 2
UP_AFTER = 3          # right answers in a row (same topic) to move up a tier
DOWN_AFTER = 2        # wrong answers in a row (same topic) to move down a tier

# Largest times-table fact used in multiplication/division (10 or 12).
TIMES_TABLE_MAX = 12

# --- Health and damage ------------------------------------------------------
MAX_HP = 100
# Damage taken in a fight depends on how far off the answer is.
DAMAGE = {"light": 5, "medium": 12, "heavy": 20}
LIGHT_WITHIN = 0.10   # within 10% of the right answer (or off by 1)
MEDIUM_WITHIN = 0.30  # within 30%
LOW_HP = 30           # below this, a healer offers an easier potion riddle
POTION_HEAL = 40
# After each defeat in a region, later hits there are multiplied by this.
SHIELD_FACTOR = 0.6

# --- Rewards ----------------------------------------------------------------
XP_BASE = 10          # XP per right answer = XP_BASE x tier
STREAK_BONUS = 5      # extra XP per answer once a streak reaches 3
MONSTER_BONUS = 20
BOSS_BONUS = 50

# --- Speed trials (the quick way to win or polish a gem) --------------------
TRIAL_QUESTIONS = 5   # riddles in a speed trial
TRIAL_PASS = 4        # right answers needed to pass
TRIAL_MIN_TIER = 3    # lowest riddle level when a trial is used to SKIP a quest
TASK_XP_FACTOR = 2    # hands-on tasks pay this many times a riddle's XP

# --- Fight length (right answers needed to win) -----------------------------
MONSTER_HITS = 2
BOSS_HITS = 3
FINAL_BOSS_HITS = 5
