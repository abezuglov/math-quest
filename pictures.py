"""Simple drawn pictures (SVG text). Pure Python: every function returns a string.

The pictures carry their own background, so they look the same in Streamlit's
light and dark themes.
"""
from __future__ import annotations

INK = "#4b3621"
PAPER = "#f4e7c5"
CARD = "#fbf6e9"
FONT = "font-family='Verdana, Geneva, sans-serif'"

GEM_COLORS = {
    "village": "#e2544a",
    "mines": "#f0a52c",
    "docks": "#3d8fd6",
    "forest": "#3fa45b",
    "castle": "#9460d6",
    "peak": "#f2d13a",
}


def _svg(w, h, body, label):
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}' "
            f"width='{w}' height='{h}' role='img' aria-label='{label}'>"
            f"<title>{label}</title>{body}</svg>")


def _g(x, y, s, body):
    return f"<g transform='translate({x} {y}) scale({s})'>{body}</g>"


# --------------------------------------------------------------------------
# Small icons, drawn around (0, 0), roughly 70 wide
# --------------------------------------------------------------------------
def _house(x, y, wall, roof):
    return (f"<rect x='{x}' y='{y}' width='26' height='20' fill='{wall}' stroke='{INK}' stroke-width='1.5'/>"
            f"<path d='M{x - 4} {y} L{x + 13} {y - 16} L{x + 30} {y} Z' fill='{roof}' stroke='{INK}' stroke-width='1.5'/>"
            f"<rect x='{x + 10}' y='{y + 9}' width='7' height='11' fill='{INK}'/>")


def icon_village():
    return (_house(-32, 0, "#fff3d6", "#c8553d") + _house(2, -6, "#ffe9b8", "#8a5a9e")
            + f"<circle cx='-2' cy='-24' r='2.5' fill='#ddd'/><circle cx='1' cy='-31' r='3.5' fill='#e6e6e6'/>")


def icon_mines():
    return (f"<path d='M-40 20 Q-22 -34 0 -30 Q26 -34 40 20 Z' fill='#b08d6a' stroke='{INK}' stroke-width='1.5'/>"
            f"<path d='M-13 20 V2 Q0 -12 13 2 V20 Z' fill='#2c2118'/>"
            f"<path d='M-15 20 V0 M15 20 V0 M-17 0 H17' stroke='#7a4f2a' stroke-width='4' fill='none'/>"
            f"<path d='M22 -14 l5 -8 l5 8 l-5 8 Z' fill='#7fe0e8' stroke='{INK}'/>"
            f"<path d='M-28 -6 l4 -6 l4 6 l-4 6 Z' fill='#f6c0ff' stroke='{INK}'/>")


def icon_docks():
    return (f"<path d='M-40 14 H-6 M-34 14 V26 M-20 14 V26 M-8 14 V26' stroke='#7a4f2a' stroke-width='4' fill='none'/>"
            f"<path d='M-2 8 H38 L30 22 H6 Z' fill='#a8623a' stroke='{INK}' stroke-width='1.5'/>"
            f"<path d='M17 8 V-30' stroke='{INK}' stroke-width='2'/>"
            f"<path d='M19 -28 L36 2 H19 Z' fill='#fff8e8' stroke='{INK}' stroke-width='1.5'/>"
            f"<path d='M15 -22 L2 2 H15 Z' fill='#ffd9a0' stroke='{INK}' stroke-width='1.5'/>"
            f"<path d='M-42 28 q7 -5 14 0 t14 0 t14 0 t14 0 t14 0 t14 0' stroke='#3d8fd6' stroke-width='2' fill='none'/>")


def _tree(x, y, s, c):
    return _g(x, y, s, f"<rect x='-3' y='8' width='6' height='12' fill='#7a4f2a'/>"
                       f"<path d='M0 -34 L16 -8 H-16 Z M0 -20 L20 10 H-20 Z' fill='{c}' stroke='{INK}' stroke-width='1.5'/>")


def icon_forest():
    return _tree(-24, 4, .8, "#3d8b4f") + _tree(22, 4, .85, "#57a35f") + _tree(0, 0, 1.1, "#2f7a45")


def icon_castle():
    top = "".join(f"<rect x='{x}' y='-22' width='7' height='7' fill='#c9c3d4' stroke='{INK}'/>"
                  for x in (-18, -4, 10))
    return (f"<rect x='-22' y='-16' width='44' height='36' fill='#d8d2e2' stroke='{INK}' stroke-width='1.5'/>{top}"
            f"<rect x='-36' y='-26' width='14' height='46' fill='#c9c3d4' stroke='{INK}' stroke-width='1.5'/>"
            f"<rect x='22' y='-26' width='14' height='46' fill='#c9c3d4' stroke='{INK}' stroke-width='1.5'/>"
            f"<path d='M-39 -26 L-29 -42 L-19 -26 Z M19 -26 L29 -42 L39 -26 Z' fill='#9460d6' stroke='{INK}' stroke-width='1.5'/>"
            f"<path d='M-8 20 V4 Q0 -6 8 4 V20 Z' fill='#5c3a1e'/>"
            f"<path d='M29 -42 V-52 l9 4 l-9 4' fill='#e2544a' stroke='{INK}'/>")


def icon_peak():
    return (f"<path d='M-44 22 L-8 -44 L14 -8 L24 -22 L46 22 Z' fill='#9aa3b5' stroke='{INK}' stroke-width='1.5'/>"
            f"<path d='M-8 -44 L-21 -20 L-12 -25 L-6 -17 L0 -26 L5 -22 Z' fill='#ffffff' stroke='{INK}'/>"
            f"<path d='M-4 22 V10 Q4 0 12 10 V22 Z' fill='#2c2118'/>"
            f"<circle cx='2' cy='13' r='1.6' fill='#ffd23a'/><circle cx='7' cy='13' r='1.6' fill='#ffd23a'/>")


ICONS = {"village": icon_village, "mines": icon_mines, "docks": icon_docks,
         "forest": icon_forest, "castle": icon_castle, "peak": icon_peak}


def dragon(x, y, s=1.0, body="#5aa469", belly="#f3e2a0", wing="#3f7d4f", flip=False):
    sx = -s if flip else s
    spikes = "".join(f"<path d='M{a} -12 L{a + 6} -25 L{a + 12} -11 Z' fill='{wing}' stroke='{INK}'/>"
                     for a in (-8, 6, 20))
    art = (f"<path d='M28 18 Q70 26 80 -6 Q64 10 32 4 Z' fill='{body}' stroke='{INK}' stroke-width='1.5'/>"
           f"<path d='M4 -6 L34 -54 L40 -24 L60 -40 L48 -2 Z' fill='{wing}' stroke='{INK}' stroke-width='1.5'/>"
           f"{spikes}"
           f"<ellipse cx='0' cy='12' rx='38' ry='26' fill='{body}' stroke='{INK}' stroke-width='1.5'/>"
           f"<ellipse cx='-5' cy='21' rx='23' ry='14' fill='{belly}'/>"
           f"<rect x='-24' y='30' width='13' height='13' rx='5' fill='{body}' stroke='{INK}' stroke-width='1.5'/>"
           f"<rect x='8' y='30' width='13' height='13' rx='5' fill='{body}' stroke='{INK}' stroke-width='1.5'/>"
           f"<path d='M-29 -33 L-23 -48 L-20 -31 Z M-41 -33 L-39 -48 L-32 -33 Z' fill='{belly}' stroke='{INK}'/>"
           f"<ellipse cx='-34' cy='-18' rx='20' ry='16' fill='{body}' stroke='{INK}' stroke-width='1.5'/>"
           f"<ellipse cx='-51' cy='-12' rx='12' ry='9' fill='{body}' stroke='{INK}' stroke-width='1.5'/>"
           f"<circle cx='-58' cy='-15' r='1.5' fill='{INK}'/>"
           f"<circle cx='-36' cy='-23' r='5.5' fill='#fff' stroke='{INK}'/><circle cx='-37.5' cy='-23' r='2.4' fill='{INK}'/>"
           f"<path d='M-60 -8 Q-51 -2 -42 -7' stroke='{INK}' stroke-width='1.5' fill='none'/>")
    return f"<g transform='translate({x} {y}) scale({sx} {s})'>{art}</g>"


ZERIX = dict(body="#5aa469", belly="#f3e2a0", wing="#3f7d4f")
NILLA = dict(body="#f29a4a", belly="#ffe9b8", wing="#d9742a")


def _gem(x, y, color, done):
    if done:
        return (f"<path d='M{x} {y - 11} L{x + 9} {y} L{x} {y + 11} L{x - 9} {y} Z' fill='{color}' "
                f"stroke='{INK}' stroke-width='1.5'/>"
                f"<path d='M{x - 4} {y - 2} L{x} {y - 7}' stroke='#fff' stroke-width='2' stroke-linecap='round'/>")
    return (f"<path d='M{x} {y - 11} L{x + 9} {y} L{x} {y + 11} L{x - 9} {y} Z' fill='{PAPER}' "
            f"stroke='{INK}' stroke-width='1.5' stroke-dasharray='3 2'/>")


def _lock(x, y):
    return (f"<path d='M{x - 5} {y - 2} V{y - 7} a5 5 0 0 1 10 0 V{y - 2}' fill='none' stroke='{INK}' stroke-width='2.5'/>"
            f"<rect x='{x - 8}' y='{y - 2}' width='16' height='12' rx='2' fill='#8c8c8c' stroke='{INK}' stroke-width='1.5'/>")


# --------------------------------------------------------------------------
# The kingdom map
# --------------------------------------------------------------------------
MAP_SPOTS = {
    "village": (115, 330),
    "mines": (265, 215),
    "forest": (395, 335),
    "docks": (590, 320),
    "castle": (505, 165),
    "peak": (300, 80),
}


def kingdom_map(places):
    """places: list of (key, name, status) with status done | open | locked."""
    body = (f"<rect width='720' height='430' rx='18' fill='{PAPER}' stroke='#b9975b' stroke-width='4'/>"
            # sea on the right
            f"<path d='M720 250 Q640 262 628 300 Q600 380 668 430 H702 Q720 430 720 412 Z' fill='#a9d5ea'/>"
            f"<path d='M660 330 q8 -5 16 0 t16 0 M650 380 q8 -5 16 0 t16 0' stroke='#5fa4c9' stroke-width='2' fill='none'/>"
            # meadows and hills
            f"<ellipse cx='150' cy='372' rx='130' ry='34' fill='#cfe0a0'/>"
            f"<ellipse cx='420' cy='378' rx='120' ry='30' fill='#bcd592'/>"
            f"<ellipse cx='500' cy='208' rx='95' ry='24' fill='#d5e3ab'/>"
            f"<path d='M40 150 q30 -40 60 0 q25 -30 50 0' fill='none' stroke='#b9975b' stroke-width='2'/>"
            f"<path d='M560 70 q26 -34 52 0 q22 -26 44 0' fill='none' stroke='#b9975b' stroke-width='2'/>")
    order = ["village", "mines", "forest", "docks", "castle", "peak"]
    pts = [MAP_SPOTS[k] for k in order if any(p[0] == k for p in places)]
    if len(pts) > 1:
        d = "M" + " L".join(f"{x} {y + 14}" for x, y in pts)
        body += (f"<path d='{d}' fill='none' stroke='#8a6a45' stroke-width='4' "
                 f"stroke-dasharray='2 10' stroke-linecap='round' stroke-linejoin='round'/>")
    for key, name, status in places:
        x, y = MAP_SPOTS[key]
        fade = " opacity='.55'" if status == "locked" else ""
        body += f"<g{fade}>{_g(x, y, 1.0, ICONS[key]())}</g>"
        if key == "peak" and status != "locked":
            body += dragon(x - 70, y - 2, .42, flip=True, **ZERIX)
        body += (_lock(x + 52, y - 30) if status == "locked"
                 else _gem(x + 52, y - 28, GEM_COLORS[key], status == "done"))
        body += (f"<text x='{x}' y='{y + 44}' text-anchor='middle' {FONT} font-size='15' "
                 f"font-weight='bold' fill='{INK}' stroke='{PAPER}' stroke-width='4' "
                 f"paint-order='stroke'>{name}</text>")
    # compass
    body += (f"<g transform='translate(668 62)'><circle r='24' fill='{PAPER}' stroke='{INK}' stroke-width='1.5'/>"
             f"<path d='M0 -20 L6 0 L0 20 L-6 0 Z' fill='#c8553d' stroke='{INK}'/>"
             f"<text y='-28' text-anchor='middle' {FONT} font-size='12' fill='{INK}'>N</text></g>"
             f"<text x='24' y='36' {FONT} font-size='18' font-weight='bold' fill='{INK}'>"
             f"The Kingdom of Arithmos</text>")
    return _svg(720, 430, body, "Map of the Kingdom of Arithmos")


# --------------------------------------------------------------------------
# Region banners and story pictures
# --------------------------------------------------------------------------
_SKY = {"village": ("#cfe9f7", "#b9d48b"), "mines": ("#e9d9c2", "#8d7358"),
        "docks": ("#cfe9f7", "#7fbfe0"), "forest": ("#d9efd2", "#6fa868"),
        "castle": ("#e3dcf2", "#b9d48b"), "peak": ("#c9d3ea", "#e8eef7")}


def _cloud(x, y, s=1.0):
    return _g(x, y, s, "<ellipse cx='0' cy='0' rx='26' ry='11' fill='#fff'/>"
                       "<ellipse cx='-12' cy='-8' rx='14' ry='10' fill='#fff'/>"
                       "<ellipse cx='10' cy='-10' rx='16' ry='12' fill='#fff'/>")


def scene(key):
    sky, ground = _SKY[key]
    body = (f"<rect width='720' height='170' rx='16' fill='{sky}'/>"
            f"<circle cx='640' cy='42' r='22' fill='#ffd86b'/>"
            f"{_cloud(120, 44)}{_cloud(470, 34, .8)}"
            f"<path d='M0 126 Q180 104 360 122 T720 116 V154 Q720 170 704 170 H16 Q0 170 0 154 Z' fill='{ground}'/>")
    icon = ICONS[key]()
    if key == "village":
        body += _g(210, 104, 1.7, icon) + _g(420, 112, 1.3, icon) + _g(575, 118, 1.0, icon_forest())
    elif key == "mines":
        body += _g(250, 100, 2.1, icon) + _g(520, 112, 1.3, icon)
    elif key == "docks":
        body += _g(250, 96, 2.0, icon) + _g(520, 104, 1.2, icon)
    elif key == "forest":
        body += "".join(_g(x, y, s, icon) for x, y, s in
                        [(110, 108, 1.2), (270, 98, 1.8), (450, 104, 1.5), (600, 112, 1.1)])
    elif key == "castle":
        body += _g(300, 96, 2.0, icon) + _g(540, 116, 1.0, icon_forest())
    else:
        body += _g(250, 96, 2.2, icon) + dragon(500, 96, 1.0, **ZERIX)
    return _svg(720, 170, body, f"Picture of the {key}")


def story_art(which):
    """Pictures for the story pages: note | nilla | ledger | finale."""
    body = f"<rect width='720' height='190' rx='16' fill='{PAPER}' stroke='#b9975b' stroke-width='3'/>"
    if which == "note":
        body += (f"<g transform='translate(360 96) rotate(-4)'>"
                 f"<path d='M-150 -62 H150 V52 Q110 66 60 54 T-40 58 T-150 50 Z' fill='#fffaf0' stroke='{INK}' stroke-width='2'/>"
                 f"<path d='M118 30 q18 -6 30 6 q-14 14 -34 10 Z' fill='#5c4630' opacity='.6'/>"
                 f"<text x='0' y='-14' text-anchor='middle' {FONT} font-size='22' font-style='italic' fill='{INK}'>Sorry about the mess.</text>"
                 f"<text x='0' y='18' text-anchor='middle' {FONT} font-size='22' font-style='italic' fill='{INK}'>I am still looking.   - Z</text>"
                 f"</g>")
    elif which == "nilla":
        body += (dragon(250, 110, 1.5, **ZERIX) + dragon(470, 128, .85, flip=True, **NILLA)
                 + f"<text x='470' y='68' text-anchor='middle' {FONT} font-size='16' font-weight='bold' fill='{INK}'>Nilla</text>"
                 + f"<text x='250' y='30' text-anchor='middle' {FONT} font-size='16' font-weight='bold' fill='{INK}'>Zerix</text>")
    elif which == "ledger":
        rows = "".join(f"<path d='M{x} {y} h110' stroke='{INK}' stroke-width='2' opacity='.55'/>"
                       for x in (228, 382) for y in (62, 82, 102, 122))
        body += (f"<path d='M210 36 H360 V160 H210 Z M360 36 H510 V160 H360 Z' fill='#fffaf0' stroke='{INK}' stroke-width='2.5'/>"
                 f"{rows}"
                 f"<circle cx='437' cy='102' r='20' fill='none' stroke='#d64545' stroke-width='4'/>"
                 f"<text x='360' y='26' text-anchor='middle' {FONT} font-size='15' font-weight='bold' fill='{INK}'>The Great Ledger</text>")
    else:
        body += (_g(130, 120, 1.5, icon_village()) + dragon(380, 108, 1.4, **ZERIX)
                 + dragon(560, 130, .8, flip=True, **NILLA)
                 + "".join(f"<text x='{x}' y='{y}' {FONT} font-size='{z}' font-weight='bold' fill='{c}'>{t}</text>"
                           for x, y, z, c, t in [(238, 46, 26, "#e2544a", "7"), (468, 40, 30, "#3d8fd6", "42"),
                                                 (610, 62, 24, "#3fa45b", "9"), (214, 100, 20, "#9460d6", "1/2"),
                                                 (648, 110, 22, "#f0a52c", "100")]))
    return _svg(720, 190, body, "Story picture")


# --------------------------------------------------------------------------
# Math pictures
# --------------------------------------------------------------------------
def _card(w, h):
    return f"<rect width='{w}' height='{h}' rx='12' fill='{CARD}' stroke='#d9cba6' stroke-width='2'/>"


def _bar(x, y, w, h, shaded, parts, color="#f0a52c"):
    cell = w / parts
    out = "".join(f"<rect x='{x + i * cell:.1f}' y='{y}' width='{cell:.1f}' height='{h}' "
                  f"fill='{color if i < shaded else '#fff'}' stroke='{INK}' stroke-width='1.5'/>"
                  for i in range(parts))
    return out


def bars(fracs, blank_parts=None):
    """Fraction bars of equal length. fracs: [(a, b), ...].
    blank_parts adds an unshaded bar cut into that many pieces."""
    rows = [(a, b, f"{a}/{b}") for a, b in fracs]
    if blank_parts:
        rows.append((0, blank_parts, f"?/{blank_parts}"))
    h = 20 + 46 * len(rows)
    body = _card(520, h)
    for i, (a, b, label) in enumerate(rows):
        y = 18 + 46 * i
        body += (f"<text x='20' y='{y + 22}' {FONT} font-size='18' font-weight='bold' fill='{INK}'>{label}</text>"
                 + _bar(90, y, 410, 30, a, b))
    return _svg(520, h, body, "Fraction bars: " + " and ".join(r[2] for r in rows))


def shade_bars(a, b, parts, shaded):
    """The target fraction on top, the child's shading below."""
    body = (_card(520, 132)
            + f"<text x='20' y='44' {FONT} font-size='18' font-weight='bold' fill='{INK}'>{a}/{b}</text>"
            + _bar(90, 22, 410, 32, a, b)
            + f"<text x='20' y='100' {FONT} font-size='18' font-weight='bold' fill='{INK}'>{shaded}/{parts}</text>"
            + _bar(90, 78, 410, 32, shaded, parts, "#3fa45b"))
    return _svg(520, 132, body, f"Two bars: {a}/{b} and {shaded}/{parts}")


def pie(k, n):
    import math
    cx, cy, r = 110, 92, 78
    body = _card(220, 208)
    body += (f"<text x='110' y='196' text-anchor='middle' {FONT} font-size='14' "
             f"fill='{INK}'>white = eaten</text>")
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n - math.pi / 2, 2 * math.pi * (i + 1) / n - math.pi / 2
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        fill = "#fff" if i < k else "#f0a52c"
        dash = " stroke-dasharray='5 4'" if i < k else ""
        body += (f"<path d='M{cx} {cy} L{x0:.1f} {y0:.1f} A{r} {r} 0 0 1 {x1:.1f} {y1:.1f} Z' "
                 f"fill='{fill}' stroke='{INK}' stroke-width='1.5'{dash}/>")
    return _svg(220, 208, body, f"A pie cut into {n} slices, {k} eaten (shown white)")


def rect_fig(l, w, top, side, grid=False):
    """A rectangle drawn roughly to scale with labels on two sides."""
    scale = min(300 / l, 150 / w)
    scale = max(scale, 28 / w) if w * scale < 28 else scale
    W, H = min(300, l * scale), min(150, max(28, w * scale))
    x, y = 40, 34
    body = _card(W + 150, H + 60)
    body += f"<rect x='{x}' y='{y}' width='{W:.1f}' height='{H:.1f}' fill='#bfe3c4' stroke='{INK}' stroke-width='2.5'/>"
    if grid and l <= 14 and w <= 14:
        body += "".join(f"<path d='M{x + i * W / l:.1f} {y} v{H:.1f}' stroke='{INK}' stroke-width='.7' opacity='.5'/>"
                        for i in range(1, l))
        body += "".join(f"<path d='M{x} {y + j * H / w:.1f} h{W:.1f}' stroke='{INK}' stroke-width='.7' opacity='.5'/>"
                        for j in range(1, w))
    body += (f"<text x='{x + W / 2:.1f}' y='24' text-anchor='middle' {FONT} font-size='16' font-weight='bold' fill='{INK}'>{top}</text>"
             f"<text x='{x + W + 10:.1f}' y='{y + H / 2 + 6:.1f}' {FONT} font-size='16' font-weight='bold' fill='{INK}'>{side}</text>")
    return _svg(round(W + 150), round(H + 60), body, f"Rectangle labeled {top} and {side}")


def garden_fig(l, w, biggest):
    """The garden being built: one square per square meter, always the same size,
    drawn on the empty plot so the child sees it grow and shrink."""
    cell = min(26, 312 // biggest)
    x, y = 34, 34
    W = biggest * cell
    body = _card(W + 120, W + 64)
    body += (f"<rect x='{x}' y='{y}' width='{W}' height='{W}' fill='#efe6cf' "
             f"stroke='{INK}' stroke-width='1' stroke-dasharray='4 4' opacity='.7'/>")
    body += f"<rect x='{x}' y='{y}' width='{l * cell}' height='{w * cell}' fill='#a9dcae' stroke='{INK}' stroke-width='2.5'/>"
    body += "".join(f"<path d='M{x + i * cell} {y} v{w * cell}' stroke='{INK}' stroke-width='.8' opacity='.5'/>"
                    for i in range(1, l))
    body += "".join(f"<path d='M{x} {y + j * cell} h{l * cell}' stroke='{INK}' stroke-width='.8' opacity='.5'/>"
                    for j in range(1, w))
    body += (f"<text x='{x + l * cell / 2:.1f}' y='24' text-anchor='middle' {FONT} font-size='16' font-weight='bold' fill='{INK}'>{l} m</text>"
             f"<text x='{x + l * cell + 8}' y='{y + w * cell / 2 + 6:.1f}' {FONT} font-size='16' font-weight='bold' fill='{INK}'>{w} m</text>")
    return _svg(W + 120, W + 64, body, f"A garden {l} meters long and {w} meters wide, drawn in square meters")


def array_fig(rows, cols):
    """rows groups of cols dots."""
    step = min(26, 420 / cols)
    r = step * .34
    W, H = cols * step + 30, rows * step + 30
    body = _card(W, H)
    colors = ["#e2544a", "#3d8fd6"]
    for i in range(rows):
        for j in range(cols):
            body += (f"<circle cx='{15 + j * step + step / 2:.1f}' cy='{15 + i * step + step / 2:.1f}' "
                     f"r='{r:.1f}' fill='{colors[i % 2]}'/>")
    return _svg(round(W), round(H), body, f"{rows} rows of {cols} dots")


def share_fig(n, boats, each):
    """Crates loaded on boats, with the rest waiting on the dock."""
    each = max(0, each)
    used = boats * each
    left = n - used
    bw = 84
    W = max(360, boats * (bw + 14) + 150)
    rows_on_boat = (each + 3) // 4
    top = 26 + max(rows_on_boat, (max(left, 0) + 6) // 7) * 16
    H = top + 70
    body = _card(W, H)
    for b in range(boats):
        x = 16 + b * (bw + 14)
        for c in range(each):
            cx, cy = x + 10 + (c % 4) * 16, top - 16 - (c // 4) * 16
            body += f"<rect x='{cx}' y='{cy}' width='14' height='14' fill='#d9a05b' stroke='{INK}'/>"
        body += (f"<path d='M{x} {top} H{x + bw} L{x + bw - 12} {top + 22} H{x + 12} Z' "
                 f"fill='#a8623a' stroke='{INK}' stroke-width='1.5'/>")
    waves = " t16 0" * (boats * (bw + 14) // 16 - 1)
    body += (f"<path d='M10 {top + 30} q8 -5 16 0{waves}' "
             f"stroke='#3d8fd6' stroke-width='2' fill='none'/>")
    px = boats * (bw + 14) + 30
    if left < 0:
        body += (f"<text x='{px}' y='{top}' {FONT} font-size='14' font-weight='bold' fill='#c0392b'>"
                 f"Not enough</text><text x='{px}' y='{top + 18}' {FONT} font-size='14' "
                 f"font-weight='bold' fill='#c0392b'>crates!</text>")
    else:
        for c in range(left):
            cx, cy = px + (c % 7) * 16, top + 6 - (c // 7) * 16
            body += f"<rect x='{cx}' y='{cy}' width='14' height='14' fill='#f3d08a' stroke='{INK}'/>"
        body += (f"<text x='{px}' y='{top + 44}' {FONT} font-size='14' fill='{INK}'>"
                 f"still on the dock</text>")
    return _svg(W, H, body, f"{boats} boats with {each} crates each, {left} crates on the dock")


def vmul_fig(a, b, hide, pos):
    """a x b worked in columns with partial products; one digit is a '?' box.

    hide is 'factor' (ones digit of b), 'partial' (second row) or 'total'.
    pos counts digits from the right (0 = ones).
    """
    ones, tens = b % 10, b // 10 * 10
    rows = [("", a), ("×", b), None, ("", a * ones), ("+", a * tens), None,
            ("", a * b)]
    target = {"factor": 1, "partial": 4, "total": 6}[hide]
    cw, comma = 22, 9

    def span(n):
        text = f"{n:,}"
        return sum(comma if ch == "," else cw for ch in text)

    widest = max(span(n) for _, n in (r for r in rows if r))
    left = 30                                  # room for the × and + signs
    right = left + widest + 14
    W = right + 24
    body, y = "", 12
    for i, row in enumerate(rows):
        if row is None:
            ly = y + 10
            body += (f"<line x1='{left - 16}' y1='{ly}' x2='{right + 4}' y2='{ly}' "
                     f"stroke='{INK}' stroke-width='2'/>")
            y = ly + 4
            continue
        sign, n = row
        y += 30
        digit_i, x_edge = 0, right
        for ch in f"{n:,}"[::-1]:
            step = comma if ch == "," else cw
            x = x_edge - step / 2
            x_edge -= step
            hidden = i == target and ch != "," and digit_i == pos
            if hidden:
                body += (f"<rect x='{x - 10:.0f}' y='{y - 22}' width='20' height='28' "
                         f"fill='#fff4c2' stroke='#c0392b' stroke-width='2'/>"
                         f"<text x='{x:.0f}' y='{y}' text-anchor='middle' {FONT} "
                         f"font-size='20' font-weight='bold' fill='#c0392b'>?</text>")
            else:
                body += (f"<text x='{x:.0f}' y='{y}' text-anchor='middle' {FONT} "
                         f"font-size='22' fill='{INK}'>{ch}</text>")
            if ch != ",":
                digit_i += 1
        if sign:
            body += (f"<text x='{left - 16}' y='{y}' {FONT} font-size='22' "
                     f"fill='{INK}'>{sign}</text>")
    H = y + 16
    return _svg(W, H, _card(W, H) + body,
                f"{a} times {b} worked out in columns, with one digit hidden")


# --------------------------------------------------------------------------
# Pictures for the younger grades (K-3) and 5th grade
# --------------------------------------------------------------------------
def _txt(x, y, text, size=16, anchor="middle", bold=True, color=INK):
    weight = " font-weight='bold'" if bold else ""
    return (f"<text x='{x:.1f}' y='{y:.1f}' text-anchor='{anchor}' {FONT} font-size='{size}'"
            f"{weight} fill='{color}'>{text}</text>")


def dots(n, per_row=5):
    """Up to 20 counting dots in rows of 5 (a double ten-frame)."""
    n = max(0, min(20, int(n)))
    rows = max(1, -(-n // per_row))
    step = 46
    W, H = per_row * step + 30, rows * step + 30
    body = _card(W, H)
    for i in range(n):
        x = 15 + (i % per_row) * step + step / 2
        y = 15 + (i // per_row) * step + step / 2
        color = "#e2544a" if i < 10 else "#3d8fd6"
        body += f"<circle cx='{x:.1f}' cy='{y:.1f}' r='15' fill='{color}' stroke='{INK}' stroke-width='1.5'/>"
    return _svg(W, H, body, f"{n} dots")


def clock(h, m=0):
    """An analog clock showing h:mm."""
    import math
    h, m = int(h) % 12, int(m) % 60
    cx = cy = 100
    body = _card(200, 200)
    body += f"<circle cx='{cx}' cy='{cy}' r='84' fill='#fff' stroke='{INK}' stroke-width='3'/>"
    for i in range(60):
        a = math.radians(i * 6)
        long = i % 5 == 0
        r0 = 70 if long else 78
        body += (f"<line x1='{cx + r0 * math.sin(a):.1f}' y1='{cy - r0 * math.cos(a):.1f}' "
                 f"x2='{cx + 84 * math.sin(a):.1f}' y2='{cy - 84 * math.cos(a):.1f}' "
                 f"stroke='{INK}' stroke-width='{2 if long else 1}'/>")
    for i in range(1, 13):
        a = math.radians(i * 30)
        body += _txt(cx + 58 * math.sin(a), cy - 58 * math.cos(a) + 6, i, 16)
    ah = math.radians((h + m / 60) * 30)
    am = math.radians(m * 6)
    body += (f"<line x1='{cx}' y1='{cy}' x2='{cx + 40 * math.sin(ah):.1f}' y2='{cy - 40 * math.cos(ah):.1f}' "
             f"stroke='{INK}' stroke-width='6' stroke-linecap='round'/>"
             f"<line x1='{cx}' y1='{cy}' x2='{cx + 64 * math.sin(am):.1f}' y2='{cy - 64 * math.cos(am):.1f}' "
             f"stroke='#d64545' stroke-width='4' stroke-linecap='round'/>"
             f"<circle cx='{cx}' cy='{cy}' r='5' fill='{INK}'/>")
    return _svg(200, 200, body, f"A clock showing {h or 12}:{m:02d}")


_COIN = {1: ("1c", "#c77d4a", 18), 5: ("5c", "#b8b8b8", 22), 10: ("10c", "#c9c9c9", 17),
         25: ("25c", "#bdbdbd", 25), 50: ("50c", "#b5b5b5", 29)}


def coins(values):
    """Coins (1, 5, 10, 25, 50 cents) and bills (100 = $1, 500 = $5 ...)."""
    values = [int(v) for v in values][:16]
    per_row = 8
    rows = max(1, -(-len(values) // per_row))
    W, H = max(1, min(len(values), per_row)) * 66 + 20, rows * 66 + 20
    body = _card(W, H)
    for i, v in enumerate(values):
        cx, cy = 10 + (i % per_row) * 66 + 33, 10 + (i // per_row) * 66 + 33
        if v in _COIN:
            label, color, r = _COIN[v]
            body += (f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='{color}' stroke='{INK}' stroke-width='2'/>"
                     + _txt(cx, cy + 5, label, 13))
        else:
            body += (f"<rect x='{cx - 30}' y='{cy - 15}' width='60' height='30' rx='3' fill='#bfe3c4' "
                     f"stroke='{INK}' stroke-width='2'/>" + _txt(cx, cy + 5, f"${v // 100}", 14))
    return _svg(W, H, body, "Money: " + ", ".join(
        _COIN[v][0] if v in _COIN else f"${v // 100}" for v in values))


def number_line(lo, hi, mark=None, parts=1):
    """A number line from lo to hi with a dot at `mark` (which may be a fraction).
    `parts` cuts every unit into that many pieces."""
    from fractions import Fraction
    lo, hi, parts = int(lo), int(hi), max(1, int(parts))
    if hi <= lo:
        hi = lo + 1
    span = hi - lo
    W = 520
    x0, x1, y = 40, W - 40, 60
    unit = (x1 - x0) / span
    body = _card(W, 100)
    body += f"<line x1='{x0 - 20}' y1='{y}' x2='{x1 + 20}' y2='{y}' stroke='{INK}' stroke-width='3'/>"
    body += (f"<path d='M{x1 + 20} {y} l-8 -6 v12 Z' fill='{INK}'/>"
             f"<path d='M{x0 - 20} {y} l8 -6 v12 Z' fill='{INK}'/>")
    label_every = max(1, span // 10)
    for i in range(span * parts + 1):
        x = x0 + i * unit / parts
        whole = i % parts == 0
        body += (f"<line x1='{x:.1f}' y1='{y - (12 if whole else 6)}' x2='{x:.1f}' "
                 f"y2='{y + (12 if whole else 6)}' stroke='{INK}' stroke-width='{2 if whole else 1}'/>")
        if whole and (i // parts) % label_every == 0:
            body += _txt(x, y + 32, lo + i // parts, 15)
    if mark is not None:
        m = Fraction(mark)
        if lo <= m <= hi:
            x = x0 + float(m - lo) * unit
            body += f"<circle cx='{x:.1f}' cy='{y}' r='9' fill='#e2544a' stroke='{INK}' stroke-width='2'/>"
            body += _txt(x, y - 20, "?", 18, color="#d64545")
    return _svg(W, 100, body, f"A number line from {lo} to {hi}"
                + (" with a point marked" if mark is not None else ""))


_SHAPES = {
    "circle": "<circle cx='0' cy='0' r='60'/>",
    "triangle": "<path d='M0 -60 L60 50 H-60 Z'/>",
    "square": "<rect x='-55' y='-55' width='110' height='110'/>",
    "rectangle": "<rect x='-75' y='-40' width='150' height='80'/>",
    "pentagon": "<path d='M0 -62 L59 -19 L36 50 H-36 L-59 -19 Z'/>",
    "hexagon": "<path d='M-30 -52 H30 L60 0 L30 52 H-30 L-60 0 Z'/>",
    "rhombus": "<path d='M0 -60 L55 0 L0 60 L-55 0 Z'/>",
    "trapezoid": "<path d='M-35 -45 H35 L70 45 H-70 Z'/>",
    "parallelogram": "<path d='M-45 -45 H75 L45 45 H-75 Z'/>",
    "oval": "<ellipse cx='0' cy='0' rx='72' ry='45'/>",
    "cube": ("<path d='M-45 -20 H25 V50 H-45 Z'/><path d='M-45 -20 L-15 -50 H55 L25 -20 Z'/>"
             "<path d='M25 -20 L55 -50 V20 L25 50 Z'/>"),
    "box": ("<path d='M-60 -10 H20 V45 H-60 Z'/><path d='M-60 -10 L-30 -40 H50 L20 -10 Z'/>"
            "<path d='M20 -10 L50 -40 V15 L20 45 Z'/>"),
    "sphere": ("<circle cx='0' cy='0' r='58'/>"
               "<ellipse cx='0' cy='0' rx='58' ry='18' fill='none' stroke-dasharray='4 3'/>"),
    "cone": ("<path d='M0 -60 L55 35 A55 18 0 0 1 -55 35 Z'/>"
             "<ellipse cx='0' cy='35' rx='55' ry='18' fill='none' stroke-dasharray='4 3'/>"),
    "cylinder": "<path d='M-45 -40 V40 A45 15 0 0 0 45 40 V-40'/><ellipse cx='0' cy='-40' rx='45' ry='15'/>",
    "pyramid": "<path d='M0 -60 L60 40 H-60 Z'/><path d='M0 -60 L60 40 L0 55 Z' opacity='.6'/>",
}
SHAPE_NAMES = list(_SHAPES)


def shape(name):
    """One flat or solid shape, drawn big."""
    name = str(name).lower()
    art = _SHAPES.get(name, _SHAPES["circle"])
    body = _card(200, 170)
    body += (f"<g transform='translate(100 85)' fill='#ffd86b' stroke='{INK}' stroke-width='3' "
             f"stroke-linejoin='round'>{art}</g>")
    return _svg(200, 170, body, "A shape")


def parts(n, shaded=0):
    """A rectangle cut into n equal parts, `shaded` of them colored (no labels)."""
    n = max(1, min(16, int(n)))
    body = _card(360, 90) + _bar(20, 20, 320, 50, int(shaded), n, "#3fa45b")
    return _svg(360, 90, body, f"A shape cut into {n} equal parts, {shaded} shaded")


def tally(labels, counts):
    """Rows of tally marks, one per label."""
    labels, counts = [str(x) for x in labels], [max(0, min(30, int(c))) for c in counts]
    rows = min(len(labels), len(counts))
    H = 20 + 44 * max(1, rows)
    W = 520
    body = _card(W, H)
    for i in range(rows):
        y = 20 + 44 * i
        body += _txt(20, y + 28, labels[i], 16, anchor="start")
        x = 160
        for k in range(counts[i]):
            if k % 5 == 4:
                body += (f"<line x1='{x - 52}' y1='{y + 8}' x2='{x + 4}' y2='{y + 32}' "
                         f"stroke='{INK}' stroke-width='3'/>")
                x += 20
            else:
                body += f"<line x1='{x}' y1='{y + 6}' x2='{x}' y2='{y + 34}' stroke='{INK}' stroke-width='3'/>"
                x += 12
    return _svg(W, H, body, "Tally chart: " + ", ".join(f"{l} {c}" for l, c in zip(labels, counts)))


def bar_graph(labels, counts, step=1):
    """A bar graph with a labelled scale."""
    labels, counts = [str(x) for x in labels], [max(0, int(c)) for c in counts]
    n = min(len(labels), len(counts))
    labels, counts = labels[:n], counts[:n]
    step = max(1, int(step))
    top = max(-(-max(counts + [1]) // step) * step, step)
    W, H = 520, 260
    x0, y0, plot_h = 70, 210, 170
    body = _card(W, H)
    body += f"<line x1='{x0}' y1='{y0}' x2='{W - 20}' y2='{y0}' stroke='{INK}' stroke-width='2'/>"
    body += f"<line x1='{x0}' y1='{y0}' x2='{x0}' y2='{y0 - plot_h - 10}' stroke='{INK}' stroke-width='2'/>"
    for v in range(0, top + 1, step):
        y = y0 - v / top * plot_h
        body += (f"<line x1='{x0 - 5}' y1='{y:.1f}' x2='{W - 20}' y2='{y:.1f}' "
                 f"stroke='{INK}' stroke-width='.6' opacity='.4'/>")
        body += _txt(x0 - 10, y + 5, v, 13, anchor="end", bold=False)
    slot = (W - 40 - x0) / max(1, n)
    colors = ["#e2544a", "#3d8fd6", "#3fa45b", "#f0a52c", "#9460d6", "#5fa4c9"]
    for i, (label, c) in enumerate(zip(labels, counts)):
        bw = slot * .6
        x = x0 + 10 + i * slot + (slot - bw) / 2
        h = c / top * plot_h
        body += (f"<rect x='{x:.1f}' y='{y0 - h:.1f}' width='{bw:.1f}' height='{h:.1f}' "
                 f"fill='{colors[i % 6]}' stroke='{INK}' stroke-width='1.5'/>")
        body += _txt(x + bw / 2, y0 + 20, label, 14)
    return _svg(W, H, body, "Bar graph: " + ", ".join(f"{l} {c}" for l, c in zip(labels, counts)))


def picture_graph(labels, counts, each=1):
    """A picture graph: one star for every `each` things."""
    labels, counts = [str(x) for x in labels], [max(0, int(c)) for c in counts]
    each = max(1, int(each))
    rows = min(len(labels), len(counts))
    H = 24 + 40 * max(1, rows) + 26
    W = 520
    body = _card(W, H)
    for i in range(rows):
        y = 16 + 40 * i
        body += _txt(20, y + 26, labels[i], 16, anchor="start")
        for k in range(min(12, counts[i] // each)):
            cx = 160 + k * 28
            body += (f"<path transform='translate({cx} {y + 20}) scale(1.1)' fill='#f0a52c' stroke='{INK}' "
                     f"stroke-width='1' d='M0 -10 L3 -3 L10 -3 L4 2 L6 9 L0 5 L-6 9 L-4 2 L-10 -3 L-3 -3 Z'/>")
    body += _txt(20, H - 8, f"Each star = {each}", 13, anchor="start", bold=False)
    return _svg(W, H, body, "Picture graph: " + ", ".join(f"{l} {c}" for l, c in zip(labels, counts))
                + f", each star is {each}")


def cubes(l, w, h):
    """A box built from unit cubes, drawn in 3-D."""
    l, w, h = (max(1, min(8, int(v))) for v in (l, w, h))
    s, dx, dy = 26, 12, 7
    W = 40 + l * s + w * dx + 20
    H = 40 + h * s + w * dy + 20
    ox, oy = 30, H - 30
    body = _card(W, H)
    for z in range(h):
        for y in range(w - 1, -1, -1):
            for x in range(l):
                px = ox + x * s + y * dx
                py = oy - z * s - y * dy
                body += (f"<rect x='{px}' y='{py - s}' width='{s}' height='{s}' fill='#ffd86b' stroke='{INK}' stroke-width='1'/>"
                         f"<path d='M{px} {py - s} l{dx} -{dy} h{s} l-{dx} {dy} Z' fill='#f3b23b' stroke='{INK}' stroke-width='1'/>"
                         f"<path d='M{px + s} {py - s} l{dx} -{dy} v{s} l-{dx} {dy} Z' fill='#d9932b' stroke='{INK}' stroke-width='1'/>")
    body += _txt(ox + l * s / 2, oy + 18, f"{l}", 14)
    body += _txt(ox + l * s + w * dx / 2 + 10, oy - w * dy / 2 + 12, f"{w}", 14, anchor="start")
    body += _txt(ox - 12, oy - h * s / 2, f"{h}", 14, anchor="end")
    return _svg(W, H, body, f"A box of cubes {l} long, {w} wide and {h} high")


def grid_point(x, y, size=10):
    """A point on a coordinate grid (first quadrant)."""
    size = max(5, min(12, int(size)))
    x, y = max(0, min(size, int(x))), max(0, min(size, int(y)))
    cell = 28
    ox, oy = 40, 20 + size * cell
    W, H = ox + size * cell + 30, oy + 40
    body = _card(W, H)
    for i in range(size + 1):
        px, py = ox + i * cell, oy - i * cell
        body += (f"<line x1='{px}' y1='{oy}' x2='{px}' y2='{oy - size * cell}' stroke='{INK}' "
                 f"stroke-width='{2 if i == 0 else .6}' opacity='{1 if i == 0 else .5}'/>")
        body += (f"<line x1='{ox}' y1='{py}' x2='{ox + size * cell}' y2='{py}' stroke='{INK}' "
                 f"stroke-width='{2 if i == 0 else .6}' opacity='{1 if i == 0 else .5}'/>")
        body += _txt(px, oy + 18, i, 12, bold=False)
        body += _txt(ox - 8, py + 4, i, 12, anchor="end", bold=False)
    body += f"<circle cx='{ox + x * cell}' cy='{oy - y * cell}' r='7' fill='#e2544a' stroke='{INK}' stroke-width='2'/>"
    body += _txt(ox + size * cell / 2, H - 4, "x", 13) + _txt(14, oy - size * cell / 2, "y", 13)
    return _svg(W, H, body, f"A grid with a point at ({x}, {y})")


def angle(deg):
    """An angle of `deg` degrees with an arc."""
    import math
    deg = max(5, min(180, int(deg)))
    cx, cy, r = 50, 130, 110
    a = math.radians(deg)
    ex, ey = cx + r * math.cos(a), cy - r * math.sin(a)
    ar = 36
    body = _card(220, 160)
    body += (f"<line x1='{cx}' y1='{cy}' x2='{cx + r}' y2='{cy}' stroke='{INK}' stroke-width='3'/>"
             f"<line x1='{cx}' y1='{cy}' x2='{ex:.1f}' y2='{ey:.1f}' stroke='{INK}' stroke-width='3'/>"
             f"<path d='M{cx + ar} {cy} A{ar} {ar} 0 0 0 "
             f"{cx + ar * math.cos(a):.1f} {cy - ar * math.sin(a):.1f}' fill='none' stroke='#d64545' stroke-width='3'/>")
    if deg == 90:
        body += f"<path d='M{cx + 16} {cy} v-16 h-16' fill='none' stroke='#d64545' stroke-width='2'/>"
    return _svg(220, 160, body, f"An angle of {deg} degrees")


_PICTURES = {
    "array": array_fig, "bars": bars, "pie": pie, "rect": rect_fig, "vmul": vmul_fig,
    "dots": dots, "clock": clock, "coins": coins, "number_line": number_line,
    "shape": shape, "parts": parts, "tally": tally, "bar_graph": bar_graph,
    "picture_graph": picture_graph, "cubes": cubes, "grid_point": grid_point, "angle": angle,
}
PICTURE_KINDS = sorted(_PICTURES)


# --------------------------------------------------------------------------
def for_question(picture):
    """Turn a Question.picture tuple into SVG text (or None)."""
    if not picture:
        return None
    kind, *args = picture
    maker = _PICTURES.get(kind)
    return maker(*args) if maker else None
