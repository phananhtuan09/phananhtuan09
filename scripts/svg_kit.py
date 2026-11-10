"""Shared drawing vocabulary for the profile SVGs: palette, fonts, motifs and motion.

Every SVG is shown through an <img> tag, so it cannot run JavaScript or fetch
anything: animation is CSS and fonts are subset and embedded as base64 woff2.
"""
import base64
import html
import io
import math
import re
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

HERE = Path(__file__).parent

GOLD, INK, DIM, BG, CARD = "#d4b072", "#ece6da", "#8a8494", "#0c0b10", "#121119"
PALE, SOFT, RULE = "#f4e3b8", "#d9d2c4", "#3a3644"
ART = ["#d4b072", "#e8735a", "#5fb3a6", "#8a8ff0"]

PROFILE = {
    "name": "Phan Anh Tuấn",
    "handle": "phananhtuan09",
    "klass": "Frontend Mage",
    "rarity": "Legendary",
    "motto": ("Render.", "Turns raw ideas into living interfaces."),
}

FONTS = [
    ("CG", "serif-600.ttf", 600, "normal"),
    ("CG", "serif-700.ttf", 700, "normal"),
    ("CG", "serif-600i.ttf", 600, "italic"),
    ("JBM", "mono-500.ttf", 500, "normal"),
]


def esc(s):
    return html.escape(str(s), quote=True)


def level_of(xp):
    level = max(1, int(math.sqrt(xp / 10)))
    return level, 10 * (level + 1) ** 2


def font_faces(body):
    """Embed the fonts, subset to exactly the characters drawn in `body` (plus digits)."""
    chars = "".join(html.unescape(t) for t in re.findall(r">([^<>]+)<", body))
    text = "".join(sorted(set(chars + "0123456789")))
    faces = []
    for family, file, weight, style in FONTS:
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.layout_features = ["kern", "liga", "lnum"]
        font = TTFont(HERE / "fonts" / file)
        sub = subset.Subsetter(opts)
        sub.populate(text=text)
        sub.subset(font)
        buf = io.BytesIO()
        font.flavor = "woff2"
        font.save(buf)
        data = base64.b64encode(buf.getvalue()).decode()
        faces.append(f"@font-face{{font-family:'{family}';font-weight:{weight};font-style:{style};"
                     f"src:url(data:font/woff2;base64,{data}) format('woff2')}}")
    return "".join(faces)


def attrs(**kw):
    return " ".join(f'{k.rstrip("_").replace("_", "-")}="{v}"' for k, v in kw.items())


def diamond(x, y, r, **kw):
    return f'<path d="M{x:g} {y - r:g}L{x + r:g} {y:g}L{x:g} {y + r:g}L{x - r:g} {y:g}Z" {attrs(**kw)}/>'


def sparkle(x, y, r, **kw):
    return (f'<path d="M{x} {y - r}Q{x} {y} {x + r} {y}Q{x} {y} {x} {y + r}'
            f'Q{x} {y} {x - r} {y}Q{x} {y} {x} {y - r}Z" fill="{GOLD}" {attrs(**kw)}/>')


def corners(x, y, w, h, r=6, delay=0.2):
    pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    return "".join(diamond(px, py, r, fill=BG, stroke=GOLD, class_="pop",
                           style=f"animation-delay:{delay + k * 0.15:.2f}s") for k, (px, py) in enumerate(pts))


def sigil(cx, cy, r, uid, incantation="RENDER · COMPOSE · HYDRATE · SHIP · "):
    """A spell circle: tick ring, incantation ring, seven-point star and a </> core."""
    ticks = []
    for i in range(48):
        a = i * math.tau / 48
        inner = r * (0.9 if i % 4 else 0.84)
        ticks.append(f"M{cx + inner * math.cos(a):.1f} {cy + inner * math.sin(a):.1f}"
                     f"L{cx + r * math.cos(a):.1f} {cy + r * math.sin(a):.1f}")
    star_r = r * 0.62
    star = " ".join(f"{cx + star_r * math.cos(-math.pi / 2 + k * 3 * math.tau / 7):.1f},"
                    f"{cy + star_r * math.sin(-math.pi / 2 + k * 3 * math.tau / 7):.1f}" for k in range(7))
    ring_r = r * 0.74
    core = r * 0.3
    g = core * 0.42  # glyph half-size
    glyph = (f"M{cx - g * 0.55:.1f} {cy - g * 0.7:.1f}L{cx - g * 1.25:.1f} {cy:.1f}L{cx - g * 0.55:.1f} {cy + g * 0.7:.1f}"
             f"M{cx + g * 0.55:.1f} {cy - g * 0.7:.1f}L{cx + g * 1.25:.1f} {cy:.1f}L{cx + g * 0.55:.1f} {cy + g * 0.7:.1f}"
             f"M{cx + g * 0.28:.1f} {cy - g * 0.95:.1f}L{cx - g * 0.28:.1f} {cy + g * 0.95:.1f}")
    fs = max(7, r * 0.085)
    return f'''
    <g class="sigil">
      <circle class="halo" cx="{cx}" cy="{cy}" r="{r * 0.55:.1f}" fill="url(#coreGlow)"/>
      <g class="spin s90" style="transform-origin:{cx}px {cy}px">
        <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{GOLD}" stroke-opacity=".6"/>
        <path d="{"".join(ticks)}" stroke="{GOLD}" stroke-opacity=".55"/>
      </g>
      <path id="inc{uid}" d="M{cx - ring_r:.1f} {cy}A{ring_r:.1f} {ring_r:.1f} 0 1 1 {cx + ring_r:.1f} {cy}A{ring_r:.1f} {ring_r:.1f} 0 1 1 {cx - ring_r:.1f} {cy}" fill="none"/>
      <g class="spin s60 rev" style="transform-origin:{cx}px {cy}px">
        <circle cx="{cx}" cy="{cy}" r="{ring_r - fs * 1.1:.1f}" fill="none" stroke="{GOLD}" stroke-opacity=".3"/>
        <text class="mono" font-size="{fs:.1f}" fill="{GOLD}" fill-opacity=".75"><textPath href="#inc{uid}" textLength="{math.tau * ring_r - fs * 0.8:.1f}" lengthAdjust="spacing">{esc((incantation * 2).rstrip())}</textPath></text>
      </g>
      <g class="spin s120" style="transform-origin:{cx}px {cy}px">
        <polygon class="draw" pathLength="100" stroke-dasharray="100 100" points="{star}" fill="none" stroke="{GOLD}" stroke-opacity=".5" stroke-linejoin="round"/>
      </g>
      <circle cx="{cx}" cy="{cy}" r="{core:.1f}" fill="#0f0e15" stroke="{GOLD}"/>
      <path class="glyph" d="{glyph}" fill="none" stroke="{INK}" stroke-width="{max(1.6, r * 0.028):.1f}" stroke-linecap="round" stroke-linejoin="round"/>
    </g>'''


WAVE_START, WAVE_STEP = 3.4, 0.042


def corona(cx, cy, r, length, days):
    """A year of contributions as rays around a sigil: one ray per week, clockwise from
    twelve o'clock a year ago to today, its length set by that week's contributions.
    `days` is a list of (iso_date, count), oldest first. Returns (svg, weeks, best_week).
    """
    weeks = [sum(c for _, c in days[i:i + 7]) for i in range(0, len(days), 7)]
    n, top = len(weeks), max(max(weeks), 1)
    width = math.tau * r / n * 0.36
    rays = {0: [], 1: [], 2: [], 3: []}
    tip = r
    for i, v in enumerate(weeks):
        a = -math.pi / 2 + (i + 0.5) * math.tau / n
        ln = 2.5 if not v else 4 + (length - 4) * math.sqrt(v / top)
        x0, y0 = cx + r * math.cos(a), cy + r * math.sin(a)
        x1, y1 = cx + (r + ln) * math.cos(a), cy + (r + ln) * math.sin(a)
        tip = r + ln + 6
        band = 0 if not v else 1 + (v >= top * 0.25) + (v >= top * 0.6)
        rays[band].append((i, f"M{x0:.1f} {y0:.1f}L{x1:.1f} {y1:.1f}"))
    style = {0: (DIM, ".35"), 1: (GOLD, ".55"), 2: (GOLD, ".9"), 3: (PALE, "1")}
    # Rays grow out week by week, sweeping clockwise to today; once grown, a wave of light
    # keeps running the same way round the year and flares on today's marker.
    out = []
    for band, items in rays.items():
        color, op = style[band]
        out.extend(f'<path class="ray" style="--c:{color};--o:{op};--d:{0.9 + i * 0.03:.2f}s;--w:{WAVE_START + i * WAVE_STEP:.3f}s" '
                   f'd="{d}" pathLength="1" stroke-width="{width:.1f}"/>' for i, d in items)
    a = -math.pi / 2 + (n - 0.5) * math.tau / n
    tx, ty = round(cx + tip * math.cos(a), 1), round(cy + tip * math.sin(a), 1)
    today = (f'<g class="fade" style="animation-delay:{0.9 + n * 0.03:.2f}s">'
             f'<circle class="flare-ring" style="--w:{WAVE_START + n * WAVE_STEP:.3f}s" cx="{tx}" cy="{ty}" r="6" fill="none" stroke="{PALE}"/>'
             + diamond(tx, ty, 3.2, fill=PALE, class_="flare", style=f"--w:{WAVE_START + n * WAVE_STEP:.3f}s") + '</g>')
    svg = f'<g stroke-linecap="round">{"".join(out)}</g>{today}'
    return svg, n, max(weeks)


def foil_defs(uid, width):
    """A moving iridescent sheet; mask it to any stroke to make that stroke read as foil."""
    return f'''
  <linearGradient id="foil{uid}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{GOLD}"/><stop offset=".2" stop-color="{PALE}"/>
    <stop offset=".35" stop-color="{ART[2]}"/><stop offset=".5" stop-color="{ART[3]}"/>
    <stop offset=".65" stop-color="{ART[1]}"/><stop offset=".8" stop-color="{PALE}"/>
    <stop offset="1" stop-color="{GOLD}"/>
  </linearGradient>
  <radialGradient id="coreGlow"><stop offset="0" stop-color="{PALE}" stop-opacity=".35"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></radialGradient>
  <radialGradient id="ambient"><stop offset="0" stop-color="{GOLD}" stop-opacity=".2"/><stop offset=".55" stop-color="{GOLD}" stop-opacity=".05"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></radialGradient>'''


def foil_sheet(uid, x, y, w, h):
    """Two copies of the foil gradient side by side, sliding by one width: a seamless loop."""
    return (f'<g class="foil" style="--w:{w}px"><rect x="{x - w}" y="{y}" width="{w}" height="{h}" fill="url(#foil{uid})"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#foil{uid})"/></g>')


def starfield(rnd, x, y, w, h, n, size=1.3):
    return "".join(
        f'<rect class="tw" style="animation-delay:{-rnd.random() * 4:.2f}s" x="{x + rnd.random() * w:.1f}" '
        f'y="{y + rnd.random() * h:.1f}" width="{size}" height="{size}" fill="{INK}" opacity="{0.25 + rnd.random() * 0.6:.2f}"/>'
        for _ in range(n))


def embers(rnd, x, y, w, n, rise=160):
    return "".join(
        f'<circle class="ember" opacity="0" style="animation-delay:{-rnd.random() * 9:.2f}s;animation-duration:{6 + rnd.random() * 6:.1f}s;--rise:-{rise * (0.6 + rnd.random() * 0.6):.0f}px" '
        f'cx="{x + rnd.random() * w:.1f}" cy="{y + rnd.random() * 20:.1f}" r="{0.8 + rnd.random() * 1.2:.1f}" fill="{PALE}"/>'
        for _ in range(n))


BASE_CSS = """
.serif{font-family:'CG',Georgia,serif;font-weight:600;font-variant-numeric:lining-nums}
.b{font-weight:700}
.i{font-style:italic}
.mono{font-family:'JBM',ui-monospace,monospace;font-weight:500}

/* entrances: keyframes hold only the starting state, so the resting state is the final design */
.draw{animation:draw 1.6s cubic-bezier(.6,0,.2,1) both}
.fade{animation:fade .9s ease both}
.rise{animation:rise .9s cubic-bezier(.2,.7,.2,1) both}
.slide{animation:slide .8s cubic-bezier(.2,.7,.2,1) both}
.pop{transform-box:fill-box;transform-origin:center;animation:pop .6s cubic-bezier(.3,1.6,.5,1) both}
.d3{animation-delay:.3s}.d4{animation-delay:.45s}.d5{animation-delay:.6s}.d6{animation-delay:.75s}
.d7{animation-delay:.9s}.d8{animation-delay:1.05s}.d9{animation-delay:1.2s}.d10{animation-delay:1.4s}

/* ambient loops */
.spin{transform-box:view-box}
.s60{animation:spin 30s linear infinite}.s90{animation:spin 45s linear infinite}.s120{animation:spin 70s linear infinite}
.rev{animation-direction:reverse}
.sigil .draw{animation-delay:.8s}
.halo{transform-box:fill-box;transform-origin:center;animation:halo 4s ease-in-out infinite}
.glyph{animation:glyph 4s ease-in-out infinite}
.tw{animation:tw 4s ease-in-out infinite}
.foil{animation:foil 7s linear infinite}
.ember{animation:ember 9s linear infinite}
.ray{stroke:var(--c);stroke-opacity:var(--o);stroke-dasharray:1 1;animation:ray .7s cubic-bezier(.2,.7,.2,1) var(--d) both,wave 6s ease-in-out var(--w) infinite}
.flare{transform-box:fill-box;transform-origin:center;animation:flare 6s ease-out var(--w) infinite}
.flare-ring{opacity:0;transform-box:fill-box;transform-origin:center;animation:flare-ring 6s ease-out var(--w) infinite}
.breathe{animation:breathe 6s ease-in-out infinite}

@keyframes draw{from{stroke-dashoffset:100}}
@keyframes fade{from{opacity:0}}
@keyframes rise{from{opacity:0;transform:translateY(8px)}}
@keyframes slide{from{opacity:0;transform:translateX(14px)}}
@keyframes pop{from{opacity:0;transform:scale(0) rotate(-90deg)}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes halo{50%{transform:scale(1.25);opacity:.6}}
@keyframes glyph{50%{stroke:#f4e3b8}}
@keyframes tw{50%{opacity:.05}}
@keyframes foil{to{transform:translateX(var(--w))}}
@keyframes ember{0%{transform:translateY(0);opacity:0}15%{opacity:.9}100%{transform:translateY(var(--rise));opacity:0}}
@keyframes breathe{50%{opacity:.55}}
@keyframes ray{from{stroke-dashoffset:1;opacity:0}}
@keyframes wave{0%,9%,100%{stroke:var(--c);stroke-opacity:var(--o)}3%{stroke:#fff3d6;stroke-opacity:1}}
@keyframes flare{0%{transform:scale(1)}4%{transform:scale(2.2) rotate(45deg)}14%,100%{transform:scale(1) rotate(90deg)}}
@keyframes flare-ring{0%{opacity:0;transform:scale(.4)}3%{opacity:1}22%,100%{opacity:0;transform:scale(2.6)}}

@media (prefers-reduced-motion:reduce){*{animation:none!important}.sweep,.mana{display:none}}
"""


def document(width, height, title, desc, body, css="", defs=""):
    style = font_faces(body) + BASE_CSS + css
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
            f'role="img" aria-labelledby="t d"><title id="t">{esc(title)}</title><desc id="d">{esc(desc)}</desc>'
            f'<style>{style}</style><defs>{defs}</defs>'
            f'<rect width="{width}" height="{height}" rx="12" fill="{BG}"/>{body}</svg>')


def write(path, svg):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")
    print(f"wrote {path} ({path.stat().st_size / 1024:.1f} KB)")
