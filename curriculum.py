"""Curriculum loader and question engine.

The math content lives in plain text files, one per grade, in curriculum/
(grade_k.toml, grade_1.toml ... grade_5.toml). Each file lists topics, and each
topic lists question TEMPLATES. This module reads the files, checks them, and
turns a template into a concrete Question with random numbers.

See curriculum/FORMAT.md for how to write a template. Short version:

    [[topic.question]]
    levels = [1, 2]                     # difficulty levels that use it (1-5)
    vars   = { a = "randint(1, 5 * L)", b = "randint(1, 5)" }
    where  = "a > b"                    # re-roll until true (optional)
    text   = "What is {a} - {b}?"
    answer = "a - b"
    hint   = "Count back {b} from {a}."
    explain = "{a} - {b} = {answer}."

Expressions are evaluated by a tiny safe evaluator (no eval(), no imports, no
attributes), so a content file can never run arbitrary code.
"""
from __future__ import annotations

import ast
import math
import random
import re
import tomllib
from dataclasses import dataclass, field
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

import questions
import tasks
from questions import Question, fmt, is_correct, parse_answer

CURRICULUM_DIR = Path(__file__).parent / "curriculum"
GRADE_ORDER = ["K", "1", "2", "3", "4", "5"]
GRADE_NAMES = {"K": "Kindergarten", "1": "1st grade", "2": "2nd grade",
               "3": "3rd grade", "4": "4th grade", "5": "5th grade"}
KINDS = ("number", "fraction", "decimal", "choice")
NO_TYPED_FRACTIONS = ("K", "1")   # these grades never type a fraction or decimal
LEVELS = (1, 2, 3, 4, 5)
REGION_KEYS = ("village", "mines", "docks", "forest", "castle", "peak")
MAX_NUMBER = 10 ** 15    # no expression may make a number bigger than this
MAX_LIST = 2000          # ... or a list / text longer than this
MAX_TRIES = 300          # re-rolls allowed to satisfy `where`


class CurriculumError(ValueError):
    """A content file has a mistake. The message says where."""


# --------------------------------------------------------------------------
# Safe expression evaluator
# --------------------------------------------------------------------------
NAMES = ["Mira", "Tom", "Lena", "Omar", "Jen", "Theo", "Rosa", "Sam", "Ava", "Leo"]
ITEMS = ["apples", "acorns", "marbles", "seashells", "stickers", "blocks",
         "crayons", "gold coins", "lanterns", "buttons"]
_ONES = ("zero one two three four five six seven eight nine ten eleven twelve "
         "thirteen fourteen fifteen sixteen seventeen eighteen nineteen").split()
_TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def number_word(n) -> str:
    """12 -> 'twelve', 345 -> 'three hundred forty-five' (up to 999,999)."""
    n = int(n)
    if n < 0:
        return "minus " + number_word(-n)
    if n < 20:
        return _ONES[n]
    if n < 100:
        return _TENS[n // 10] + ("-" + _ONES[n % 10] if n % 10 else "")
    if n < 1000:
        rest = n % 100
        return _ONES[n // 100] + " hundred" + (" " + number_word(rest) if rest else "")
    if n < 1_000_000:
        rest = n % 1000
        return number_word(n // 1000) + " thousand" + (" " + number_word(rest) if rest else "")
    raise ValueError("number_word supports numbers below one million")


def ordinal(n) -> str:
    n = int(n)
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def round_to(n, place):
    """Round to the nearest `place` (10, 100, 1000...), 5 rounds up, as taught."""
    n, place = Fraction(n), int(place)
    return int((n + Fraction(place, 2)) // place * place)


def digit(n, place):
    """digit(4372, 100) -> 3"""
    return int(n) // int(place) % 10


def fmt_decimal(value) -> str:
    """Fraction(13, 4) -> '3.25'. Only for values with a finite decimal."""
    value = Fraction(value)
    sign = "-" if value < 0 else ""
    value = abs(value)
    for places in range(0, 7):
        scaled = value * 10 ** places
        if scaled.denominator == 1:
            whole, frac = divmod(scaled.numerator, 10 ** places)
            if not places:
                return f"{sign}{whole:,}"
            return f"{sign}{whole:,}.{frac:0{places}d}"
    raise ValueError(f"{value} has no short decimal form")


def fmt_money(value) -> str:
    """Fraction(13, 4) dollars -> '$3.25'"""
    value = Fraction(value)
    cents = round(value * 100)
    return f"${cents // 100:,}.{cents % 100:02d}"


def plural(n, word, many=None):
    """plural(1, 'apple') -> '1 apple', plural(3, 'apple') -> '3 apples'."""
    return f"{fmt(Fraction(n))} {word if n == 1 else (many or word + 's')}"


def compare_sign(a, b) -> str:
    """compare(3, 5) -> '<'"""
    return "<" if a < b else ">" if a > b else "="


def is_prime(n) -> bool:
    n = int(n)
    return n > 1 and all(n % d for d in range(2, math.isqrt(n) + 1))


def factors(n) -> list:
    """factors(12) -> [1, 2, 3, 4, 6, 12]"""
    n = int(n)
    if not 1 <= n <= 100_000:
        raise ValueError("factors() needs a number from 1 to 100,000")
    return [d for d in range(1, n + 1) if n % d == 0]


def expanded(n) -> str:
    """expanded(345) -> '300 + 40 + 5'"""
    n = int(n)
    parts = [int(ch) * 10 ** i for i, ch in enumerate(str(n)[::-1]) if ch != "0"]
    return " + ".join(f"{x:,}" for x in reversed(parts)) or "0"


def clock_text(h, m=0) -> str:
    """time(3, 5) -> '3:05'"""
    return f"{int(h)}:{int(m):02d}"


def different(*values) -> bool:
    """True when no two of the values are equal."""
    values = values[0] if len(values) == 1 and isinstance(values[0], list) else values
    return all(a != b for i, a in enumerate(values) for b in values[i + 1:])


def _bind(rng: random.Random) -> dict:
    """Functions a template may call. The random ones use the game's rng."""
    def randint(lo, hi):
        lo, hi = int(lo), int(hi)
        if lo > hi:
            raise CurriculumError(f"randint({lo}, {hi}): low end is above high end")
        return rng.randint(lo, hi)

    def randstep(lo, hi, step):
        lo, hi, step = int(lo), int(hi), int(step)
        if lo > hi or step < 1:
            raise CurriculumError(f"randstep({lo}, {hi}, {step}): bad range")
        return rng.randrange(lo, hi + 1, step)

    def choice(seq):
        seq = list(seq)
        if not seq:
            raise CurriculumError("choice() of an empty list")
        return rng.choice(seq)

    def sample(seq, k):
        return rng.sample(list(seq), int(k))

    def shuffled(seq):
        seq = list(seq)
        rng.shuffle(seq)
        return seq

    return {
        # random
        "randint": randint, "randstep": randstep, "choice": choice,
        "sample": sample, "shuffled": shuffled,
        "coin": lambda p=0.5: rng.random() < float(p),
        "name": lambda: rng.choice(NAMES), "item": lambda: rng.choice(ITEMS),
        "names": lambda k: rng.sample(NAMES, int(k)),
        # numbers
        "frac": lambda n, d=1: Fraction(n, d) if not isinstance(n, Fraction) else n / d,
        "dec": lambda s: Fraction(str(s)), "num": lambda x: x.numerator,
        "den": lambda x: Fraction(x).denominator,
        "gcd": lambda a, b: math.gcd(int(a), int(b)),
        "lcm": lambda a, b: math.lcm(int(a), int(b)),
        "min": min, "max": max, "abs": abs, "sum": sum, "len": len,
        "int": lambda x: int(x), "round_to": round_to, "digit": digit,
        "range": _range, "sorted": sorted, "list": list,
        "reversed": lambda seq: list(seq)[::-1],
        "compare": compare_sign, "yesno": lambda ok: "Yes" if ok else "No",
        "is_prime": is_prime, "factors": factors, "different": different,
        "count": lambda seq, x: list(seq).count(x),
        "index": lambda seq, x: list(seq).index(x),
        # words and display
        "word": number_word, "ordinal": ordinal, "plural": plural,
        "fmt": fmt, "dec_text": fmt_decimal, "money": fmt_money,
        "expanded": expanded, "time": clock_text, "plain": _plain,
        "str": _show, "join": lambda seq, sep=", ": sep.join(_show(x) for x in seq),
    }


def _range(*args):
    r = range(*(int(x) for x in args))
    if len(r) > MAX_LIST:
        raise CurriculumError("range() is too long")
    return list(r)


def _plain(v) -> str:
    """1234 -> '1234' (no comma)."""
    return str(int(v)) if _is_num(v) and Fraction(v).denominator == 1 else _show(v)


def _checked(value):
    """Keep results small, so a content file cannot eat the memory."""
    if isinstance(value, (int, Fraction)) and not isinstance(value, bool):
        if abs(value) > MAX_NUMBER:
            raise CurriculumError("number is too big")
    elif isinstance(value, (str, list)) and len(value) > MAX_LIST:
        raise CurriculumError("list or text is too long")
    return value


def _times(a, b):
    for seq, n in ((a, b), (b, a)):
        if isinstance(seq, (str, list)):       # 'ab' * 3 and [0] * 3 are fine
            if not isinstance(n, int) or n * max(1, len(seq)) > MAX_LIST:
                raise CurriculumError("list or text is too long")
    return a * b


_BINOPS = {
    ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b,
    ast.Mult: _times, ast.Mod: lambda a, b: a % b,
    ast.FloorDiv: lambda a, b: a // b,
    ast.Div: lambda a, b: Fraction(a) / Fraction(b),     # 7 / 2 is exactly 7/2
}
_CMP = {
    ast.Eq: lambda a, b: a == b, ast.NotEq: lambda a, b: a != b,
    ast.Lt: lambda a, b: a < b, ast.LtE: lambda a, b: a <= b,
    ast.Gt: lambda a, b: a > b, ast.GtE: lambda a, b: a >= b,
    ast.In: lambda a, b: a in b, ast.NotIn: lambda a, b: a not in b,
}


@lru_cache(maxsize=4096)
def _parse(expr: str):
    try:
        return ast.parse(expr.strip(), mode="eval").body
    except SyntaxError as e:
        raise CurriculumError(f"cannot read expression {expr!r}: {e.msg}") from None


def _ev(node, env, funcs):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, str, bool)) or node.value is None:
            return _checked(node.value)
        if isinstance(node.value, float):       # 0.25 means exactly 1/4
            return Fraction(str(node.value))
        raise CurriculumError(f"constant {node.value!r} is not allowed")
    if isinstance(node, ast.Name):
        if node.id in env:
            return env[node.id]
        if node.id in ("True", "False"):
            return node.id == "True"
        raise CurriculumError(f"unknown name {node.id!r}")
    if isinstance(node, ast.BinOp):
        a, b = _ev(node.left, env, funcs), _ev(node.right, env, funcs)
        if isinstance(node.op, ast.Pow):
            if not isinstance(b, int) or abs(b) > 12 or abs(a) > 10 ** 6:
                raise CurriculumError("power is too big")
            return Fraction(a) ** b if b < 0 else a ** b
        op = _BINOPS.get(type(node.op))
        if op is None:
            raise CurriculumError(f"operator {type(node.op).__name__} is not allowed")
        return _checked(op(a, b))
    if isinstance(node, ast.UnaryOp):
        v = _ev(node.operand, env, funcs)
        if isinstance(node.op, ast.USub):
            return -v
        if isinstance(node.op, ast.UAdd):
            return +v
        if isinstance(node.op, ast.Not):
            return not v
        raise CurriculumError("operator is not allowed")
    if isinstance(node, ast.BoolOp):
        is_and = isinstance(node.op, ast.And)
        result = is_and
        for sub in node.values:
            result = _ev(sub, env, funcs)
            if bool(result) != is_and:
                return result
        return result
    if isinstance(node, ast.Compare):
        left = _ev(node.left, env, funcs)
        for op, right_node in zip(node.ops, node.comparators):
            right = _ev(right_node, env, funcs)
            if type(op) not in _CMP:
                raise CurriculumError(f"comparison {type(op).__name__} is not allowed")
            if not _CMP[type(op)](left, right):
                return False
            left = right
        return True
    if isinstance(node, ast.IfExp):
        return _ev(node.body if _ev(node.test, env, funcs) else node.orelse, env, funcs)
    if isinstance(node, (ast.List, ast.Tuple)):
        return [_ev(e, env, funcs) for e in node.elts]
    if isinstance(node, ast.Subscript):
        seq = _ev(node.value, env, funcs)
        if not isinstance(seq, (list, str)):
            raise CurriculumError("only a list or text can be indexed")
        if isinstance(node.slice, ast.Slice):          # seq[a:b], no step
            if node.slice.step is not None:
                raise CurriculumError("a slice step is not allowed")
            lo = None if node.slice.lower is None else int(_ev(node.slice.lower, env, funcs))
            hi = None if node.slice.upper is None else int(_ev(node.slice.upper, env, funcs))
            return seq[lo:hi]
        return seq[int(_ev(node.slice, env, funcs))]
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in funcs or node.keywords:
            name = getattr(node.func, "id", "?")
            raise CurriculumError(f"function {name!r} is not allowed")
        if any(isinstance(a, ast.Starred) for a in node.args):
            raise CurriculumError("* in a function call is not allowed")
        return _checked(funcs[node.func.id](*(_ev(a, env, funcs) for a in node.args)))
    raise CurriculumError(f"{type(node).__name__} is not allowed in an expression")


_CONTENT_ERRORS = (ZeroDivisionError, TypeError, ValueError, IndexError, KeyError,
                   AttributeError, OverflowError, RecursionError)


def evaluate(expr, env: dict, rng: random.Random | None = None, funcs=None):
    """Evaluate one expression string. Non-strings (TOML numbers) pass through."""
    if not isinstance(expr, str):
        return Fraction(str(expr)) if isinstance(expr, float) else expr
    try:
        return _ev(_parse(expr), env, funcs or _bind(rng or random.Random()))
    except _CONTENT_ERRORS as e:
        raise CurriculumError(f"{expr!r}: {type(e).__name__}: {e}") from None


# --------------------------------------------------------------------------
# Text templates:  "What is {a} + {b}?"  "{total|plain}"  "{price|money}"
# --------------------------------------------------------------------------
_SLOT = re.compile(r"\{([^{}]+)\}")
_STYLES = {
    "plain": lambda v: _plain(v),
    "word": number_word, "money": fmt_money, "dec": fmt_decimal,
    "ordinal": ordinal,
}


def _is_num(v):
    return isinstance(v, (int, Fraction)) and not isinstance(v, bool)


def _show(v) -> str:
    if isinstance(v, bool):
        return "yes" if v else "no"
    if _is_num(v):
        return fmt(Fraction(v))
    if isinstance(v, list):
        return ", ".join(_show(x) for x in v)
    return str(v)


def render(template: str, env: dict, funcs) -> str:
    def slot(m):
        expr, _, style = m.group(1).partition("|")
        value = _ev(_parse(expr), env, funcs)
        style = style.strip()
        if style:
            if style not in _STYLES:
                raise CurriculumError(f"unknown style |{style} (use one of {sorted(_STYLES)})")
            return _STYLES[style](value)
        return _show(value)
    return _SLOT.sub(slot, template)


# --------------------------------------------------------------------------
# Data model
# --------------------------------------------------------------------------
@dataclass
class Template:
    where_from: str                 # "grade_k.toml, topic k_count, question 2"
    levels: tuple
    weight: float = 1.0
    kind: str = "number"
    vars: dict = field(default_factory=dict)
    where: str | None = None
    text: str = ""
    answer: str = ""
    hint: str = ""
    explain: str = ""
    choices: list | None = None     # expressions; for kind "choice"
    shuffle: bool = True
    picture: list | None = None     # ["array", "rows_expr", "cols_expr"]
    generator: str | None = None    # use a hand-written Python generator instead


@dataclass
class Topic:
    id: str
    label: str
    grade: str
    tip: str
    standard: str = ""
    templates: list = field(default_factory=list)
    enabled: bool = True            # the teacher's switch

    def for_level(self, level):
        return [t for t in self.templates if level in t.levels]


@dataclass
class Grade:
    code: str                       # "K", "1" ... "5"
    name: str
    title: str
    topics: dict                    # id -> Topic, in file order
    regions: list                   # list of dicts (see FORMAT.md)
    source: str

    @property
    def decimal_places(self):
        """Most decimal places an answer may have in this grade."""
        return 3 if self.code == "5" else 2


_TEMPLATE_KEYS = {"levels", "weight", "kind", "vars", "where", "text", "answer",
                  "hint", "explain", "choices", "shuffle", "picture", "generator"}


def _template(raw: dict, where_from: str) -> Template:
    unknown = set(raw) - _TEMPLATE_KEYS
    if unknown:
        raise CurriculumError(f"{where_from}: unknown key(s) {sorted(unknown)}")
    levels = raw.get("levels", list(LEVELS))
    if isinstance(levels, int):
        levels = [levels]
    if not levels or any(lv not in LEVELS for lv in levels):
        raise CurriculumError(f"{where_from}: levels must be numbers from 1 to 5")
    weight = raw.get("weight", 1)
    if isinstance(weight, bool) or not isinstance(weight, (int, float)) or weight <= 0:
        raise CurriculumError(f"{where_from}: weight must be a number above 0")
    if raw.get("generator"):
        if raw["generator"] not in questions._GENERATORS:
            raise CurriculumError(f"{where_from}: no generator named {raw['generator']!r}")
        return Template(where_from, tuple(levels), float(raw.get("weight", 1)),
                        generator=raw["generator"])
    kind = raw.get("kind", "number")
    if kind not in KINDS:
        raise CurriculumError(f"{where_from}: kind must be one of {KINDS}")
    for key in ("text", "answer", "hint", "explain"):
        if not raw.get(key):
            raise CurriculumError(f"{where_from}: missing {key!r}")
    if kind == "choice" and not raw.get("choices"):
        raise CurriculumError(f"{where_from}: a choice question needs 'choices'")
    return Template(where_from, tuple(levels), float(raw.get("weight", 1)), kind,
                    dict(raw.get("vars", {})), raw.get("where"), raw["text"],
                    str(raw["answer"]), raw["hint"], raw["explain"],
                    raw.get("choices"), bool(raw.get("shuffle", True)),
                    raw.get("picture"))


_TOPIC_KEYS = {"id", "label", "standard", "tip", "enabled", "question"}
_REGION_KEYS = {"key", "name", "gem", "topics", "intro", "outro", "memory", "task",
                "task_topic", "task_levels", "mix", "final", "encounter"}
_ENCOUNTER_KEYS = {"slot", "name", "emoji", "intro", "win"}


def _region(raw: dict, topics: dict, source: str) -> dict:
    """Check one [[region]] and fill in the defaults."""
    key = raw.get("key")
    here = f"{source}: region {key!r}"
    if key not in REGION_KEYS:
        raise CurriculumError(f"{here}: key must be one of {list(REGION_KEYS)}")
    unknown = set(raw) - _REGION_KEYS
    if unknown:
        raise CurriculumError(f"{here}: unknown key(s) {sorted(unknown)}")
    for need in ("name", "gem"):
        if not isinstance(raw.get(need), str) or not raw[need].strip():
            raise CurriculumError(f"{here}: missing {need!r}")
    listed = raw.get("topics")
    if not isinstance(listed, list) or not listed:
        raise CurriculumError(f"{here}: 'topics' must list at least one topic id")
    bad = [t for t in listed if t not in topics]
    if bad:
        raise CurriculumError(f"{here} lists unknown topics {bad}")
    region = {"key": key, "name": raw["name"], "gem": raw["gem"], "topics": list(listed),
              "mix": bool(raw.get("mix", False)), "final": bool(raw.get("final", False)),
              "task": raw.get("task"), "task_topic": raw.get("task_topic") or listed[0],
              "task_levels": raw.get("task_levels", [1, 5]), "encounter": []}
    for opt in ("intro", "outro", "memory"):
        if raw.get(opt):
            region[opt] = str(raw[opt])
    if region["task"] is not None and region["task"] not in tasks.TASK_TOPIC:
        raise CurriculumError(f"{here}: task must be one of {sorted(tasks.TASK_TOPIC)}")
    if region["task_topic"] not in topics:
        raise CurriculumError(f"{here}: task_topic {region['task_topic']!r} is not a topic")
    lv = region["task_levels"]
    if (not isinstance(lv, list) or len(lv) != 2 or any(x not in LEVELS for x in lv)
            or lv[0] > lv[1]):
        raise CurriculumError(f"{here}: task_levels must be [lowest, highest], from 1 to 5")
    for enc in raw.get("encounter", []):
        unknown = set(enc) - _ENCOUNTER_KEYS
        if unknown or not isinstance(enc.get("slot"), int) or isinstance(enc.get("slot"), bool):
            raise CurriculumError(f"{here}: an encounter needs a whole-number 'slot' and "
                                  f"may only set {sorted(_ENCOUNTER_KEYS)}")
        region["encounter"].append(dict(enc))
    return region


def load_grade(path: Path) -> Grade:
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as e:
        raise CurriculumError(f"{path.name}: {e}") from None
    code = str(data.get("grade", ""))
    if code not in GRADE_ORDER:
        raise CurriculumError(f"{path.name}: grade must be one of {GRADE_ORDER}")
    unknown = set(data) - {"grade", "name", "title", "region", "topic"}
    if unknown:
        raise CurriculumError(f"{path.name}: unknown key(s) {sorted(unknown)}")
    topics = {}
    for raw in data.get("topic", []):
        tid = raw.get("id", "")
        if not isinstance(tid, str) or not re.fullmatch(r"[a-z0-9_]+", tid) or tid in topics:
            raise CurriculumError(f"{path.name}: bad or repeated topic id {tid!r}")
        unknown = set(raw) - _TOPIC_KEYS
        if unknown:
            raise CurriculumError(f"{path.name}: topic {tid}: unknown key(s) {sorted(unknown)}")
        if not isinstance(raw.get("enabled", True), bool):
            raise CurriculumError(f"{path.name}: topic {tid}: enabled must be true or false")
        legacy = [q.get("generator") for q in raw.get("question", []) if q.get("generator")]
        tip = raw.get("tip") or (questions.TOPIC_TIPS.get(legacy[0]) if legacy else None)
        label = raw.get("label") or (questions.TOPIC_LABELS.get(legacy[0]) if legacy else None)
        if not tip or not label:
            raise CurriculumError(f"{path.name}: topic {tid} needs a label and a tip")
        templates = [_template(q, f"{path.name}, topic {tid}, question {i + 1}")
                     for i, q in enumerate(raw.get("question", []))]
        topic = Topic(tid, label, code, tip, raw.get("standard", ""), templates,
                      raw.get("enabled", True))
        typed = [t for t in templates if t.kind in ("fraction", "decimal")]
        if code in NO_TYPED_FRACTIONS and typed:
            raise CurriculumError(f"{typed[0].where_from}: {GRADE_NAMES[code]} children "
                                  f"do not type fractions or decimals; use a choice "
                                  f"question instead")
        missing = [lv for lv in LEVELS if not topic.for_level(lv)]
        if missing:
            raise CurriculumError(f"{path.name}: topic {tid} has no question for level(s) {missing}")
        topics[tid] = topic
    if not topics:
        raise CurriculumError(f"{path.name}: no topics")
    regions = [_region(r, topics, path.name) for r in data.get("region", [])]
    keys = [r["key"] for r in regions]
    if keys != list(REGION_KEYS):
        raise CurriculumError(f"{path.name}: needs exactly 6 regions, one for each of "
                              f"{list(REGION_KEYS)}, in that order")
    if any(r["final"] for r in regions[:-1]):
        raise CurriculumError(f"{path.name}: only the last region may be the finale")
    regions[-1]["final"] = True
    return Grade(code, data.get("name", GRADE_NAMES[code]), data.get("title", ""),
                 topics, regions, path.name)


@lru_cache(maxsize=None)
def load_all(directory: str | None = None) -> dict:
    """{grade code: Grade} for every grade_*.toml file, in K..5 order."""
    folder = Path(directory) if directory else CURRICULUM_DIR
    grades = {}
    for path in sorted(folder.glob("grade_*.toml")):
        g = load_grade(path)
        if g.code in grades:
            raise CurriculumError(f"{path.name}: grade {g.code} is defined twice")
        grades[g.code] = g
    return {c: grades[c] for c in GRADE_ORDER if c in grades}


def grade(code: str) -> Grade:
    return load_all()[str(code).upper()]


# --------------------------------------------------------------------------
# Making a question
# --------------------------------------------------------------------------
def _pick(templates, rng):
    if len(templates) == 1:
        return templates[0]
    total = sum(t.weight for t in templates)
    x = rng.random() * total
    for t in templates:
        x -= t.weight
        if x < 0:
            return t
    return templates[-1]


def build(tpl: Template, topic_id: str, level: int, rng: random.Random) -> Question:
    """Turn one template into a Question. Raises CurriculumError on bad content."""
    if tpl.generator:
        d = questions._GENERATORS[tpl.generator](level, rng)
        if not isinstance(d["answer"], str):
            d["answer"] = Fraction(d["answer"])
        return Question(topic=topic_id, tier=level, **d)
    funcs = _bind(rng)
    try:
        for _ in range(MAX_TRIES):
            env = {"L": level}
            for name, expr in tpl.vars.items():
                env[name] = evaluate(expr, env, funcs=funcs)
            if not tpl.where or _ev(_parse(tpl.where), env, funcs):
                break
        else:
            raise CurriculumError(f"'where' was never true after {MAX_TRIES} tries")
        answer = _ev(_parse(tpl.answer), env, funcs)
        env["answer"] = answer
        choices = []
        if tpl.kind == "choice":
            choices = [_show(evaluate(c, env, funcs=funcs)) for c in tpl.choices]
            if tpl.shuffle:
                rng.shuffle(choices)
            answer = _show(answer)
        else:
            if not _is_num(answer):
                raise CurriculumError(f"answer {answer!r} is not a number")
            answer = Fraction(answer)
        picture = None
        if tpl.picture:
            picture = (tpl.picture[0],
                       *(evaluate(p, env, funcs=funcs) for p in tpl.picture[1:]))
        return Question(topic=topic_id, tier=level,
                        text=render(tpl.text, env, funcs),
                        answer=answer,
                        hint=render(tpl.hint, env, funcs),
                        explanation=render(tpl.explain, env, funcs),
                        kind=tpl.kind, choices=choices, picture=picture)
    except CurriculumError as e:
        raise CurriculumError(f"{tpl.where_from}: {e}") from None
    except _CONTENT_ERRORS as e:
        raise CurriculumError(f"{tpl.where_from}: {type(e).__name__}: {e}") from None


def generate(topic: Topic, level: int, rng: random.Random | None = None) -> Question:
    rng = rng or random.Random()
    level = max(1, min(5, int(level)))
    return build(_pick(topic.for_level(level), rng), topic.id, level, rng)


def show_answer(q: Question, value=None) -> str:
    """The answer (or a child's value) the way the screen should print it."""
    value = q.answer if value is None else value
    if q.kind == "decimal" and not isinstance(value, str):
        try:
            return fmt_decimal(value)
        except ValueError:
            return fmt(value)
    return fmt(value)


_SPOKEN_SIGNS = [("−", " minus "), ("+", " plus "), ("×", " times "), ("÷", " divided by "),
                 ("=", " equals "), ("<", " is less than "), (">", " is greater than "),
                 ("¢", " cents")]
_SIGN_CHOICES = {"<": "less than", ">": "greater than", "=": "equal"}


def spoken(text: str, choices=None) -> str:
    """Question text the way a reading voice should say it: signs as words,
    '7 + ? = 10' as 'seven plus what number equals ten', '3:00' as 'three
    o'clock'. Choices that the text does not already name are read at the end."""
    out = re.sub(r"\b(\d{1,2}):00\b", r"\1 o'clock", str(text))
    out = re.sub(r"\b(\d{1,2}):0(\d)\b", r"\1 oh \2", out)
    out = re.sub(r"\b(\d{1,2}):(\d\d)\b", r"\1 \2", out)
    out = re.sub(r"(?<![\w)\]])\s*\?", " blank", out)     # a ? that stands for a missing part
    for sign, words in _SPOKEN_SIGNS:
        out = out.replace(sign, words)
    if choices and any(str(c) not in str(text) for c in choices):
        said = [_SIGN_CHOICES.get(str(c)) or spoken(c) for c in choices]
        out += " Is it " + ", ".join(said[:-1]) + ", or " + said[-1] + "?"
    return re.sub(r"\s+", " ", out).strip()


# --------------------------------------------------------------------------
# Checking content (used by the tests and by `python curriculum.py`)
# --------------------------------------------------------------------------
def check_template(tpl: Template, topic_id: str, samples: int = 60, seed: int = 0,
                   max_places: int = 2) -> list:
    """Generate many questions from one template. Returns a list of problems.

    Checks: the text has no leftover braces; a choice question has 2-4 different
    choices and exactly one of them is the answer; other answers are not
    negative, a `number` answer is whole, a `decimal` answer has a short decimal
    form with at most `max_places` places, and the answer as shown on screen is
    accepted back when typed; a picture, if any, can be drawn."""
    import pictures
    problems = []
    rng = random.Random(seed)
    for level in tpl.levels:
        for _ in range(samples):
            try:
                q = build(tpl, topic_id, level, rng)
            except CurriculumError as e:
                return problems + [str(e)]
            where = f"{tpl.where_from}, level {level}: {q.text!r}"
            for text in (q.text, q.hint, q.explanation):
                if "{" in text or "}" in text:
                    problems.append(f"{where}: leftover brace in {text!r}")
            if q.kind == "choice":
                if q.choices.count(q.answer) != 1:
                    problems.append(f"{where}: answer {q.answer!r} must be exactly one of {q.choices}")
                if not 2 <= len(q.choices) <= 4 or len(set(q.choices)) != len(q.choices):
                    problems.append(f"{where}: needs 2-4 different choices, got {q.choices}")
            else:
                if q.answer < 0:
                    problems.append(f"{where}: negative answer {q.answer}")
                if q.kind == "number" and q.answer.denominator != 1:
                    problems.append(f"{where}: answer {q.answer} is not a whole number "
                                    f"(use kind = \"fraction\" or \"decimal\")")
                if q.kind == "decimal":
                    try:
                        places = len(fmt_decimal(q.answer).partition(".")[2])
                    except ValueError:
                        places = None
                    if places is None or places > max_places:
                        problems.append(f"{where}: decimal answer {q.answer} needs more than "
                                        f"{max_places} decimal places")
                shown = show_answer(q)
                if not is_correct(q, parse_answer(shown)):
                    problems.append(f"{where}: the shown answer {shown!r} is not accepted back")
            if q.picture:
                try:
                    svg = pictures.for_question(q.picture)
                except _CONTENT_ERRORS as e:
                    problems.append(f"{where}: picture {q.picture!r} failed: {e}")
                else:
                    if svg is None:
                        problems.append(f"{where}: unknown picture {q.picture[0]!r} "
                                        f"(use one of {pictures.PICTURE_KINDS})")
            if problems:
                return problems
    return problems


def check_all(samples: int = 60) -> list:
    problems = []
    for g in load_all().values():
        for topic in g.topics.values():
            for i, tpl in enumerate(topic.templates):
                problems += check_template(tpl, topic.id, samples, seed=i,
                                           max_places=g.decimal_places)
    return problems


if __name__ == "__main__":       # python curriculum.py  -> checks every file
    import sys
    load_all.cache_clear()
    found = check_all()
    for p in found:
        print("PROBLEM:", p)
    for g in load_all().values():
        n = sum(len(t.templates) for t in g.topics.values())
        print(f"Grade {g.code}: {len(g.topics)} topics, {n} templates")
    sys.exit(1 if found else 0)
