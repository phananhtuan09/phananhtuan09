"""Render the animated RPG character-card SVG for the GitHub profile README.

All animation is CSS inside the SVG (no JavaScript), so it plays when GitHub
shows the file through an <img> tag. Fonts are subset and embedded because an
SVG loaded as an image cannot fetch external resources.
"""
import base64
import json
import io
import math
import random
import sys
from datetime import date
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

HERE = Path(__file__).parent

PROFILE = {
    "name": "Phan Anh Tuấn",
    "handle": "phananhtuan09",
    "klass": "Frontend Mage",
    "rarity": "Legendary",
}

# Skill tree: languages on the top row (labels above), frameworks, runtimes and databases below.
# key: (x, row, label)
SKILLS = {
    "html": (412, 0, "HTML"), "css": (492, 0, "CSS"), "js": (572, 0, "JavaScript"),
    "ts": (652, 0, "TypeScript"), "php": (732, 0, "PHP"), "py": (812, 0, "Python"),
    "react": (492, 1, "React"), "next": (572, 1, "Next.js"), "node": (652, 1, "Node.js"),
    "nest": (732, 1, "NestJS"), "mysql": (812, 1, "MySQL"),
}
SKILL_EDGES = [("html", "css"), ("css", "js"), ("js", "ts"), ("js", "react"), ("react", "next"),
               ("js", "node"), ("ts", "nest"), ("node", "nest"), ("php", "mysql")]
SKILL_ORDER = ["html", "css", "js", "ts", "php", "py", "react", "next", "node", "nest", "mysql"]

# Radar axes reach the rim at these values; a log scale keeps small numbers visible.
RADAR_CAPS = {"commits": 1500, "prs": 150, "reviews": 150, "issues": 60, "repos": 60, "longest_streak": 90}

GOLD, INK, DIM, BG, CARD = "#d4b072", "#ece6da", "#8a8494", "#0c0b10", "#121119"
ART = ["#d4b072", "#e8735a", "#5fb3a6", "#8a8ff0"]


def font_face(family, path, weight, style, text):
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga"]
    font = TTFont(path)
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    data = base64.b64encode(buf.getvalue()).decode()
    return (f"@font-face{{font-family:'{family}';font-weight:{weight};font-style:{style};"
            f"src:url(data:font/woff2;base64,{data}) format('woff2')}}")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def diamond(x, y, r, **attrs):
    extra = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<path d="M{x} {y - r}L{x + r} {y}L{x} {y + r}L{x - r} {y}Z" {extra}/>'


def sparkle(x, y, r, cls=""):
    return (f'<path class="{cls}" d="M{x} {y - r}Q{x} {y} {x + r} {y}Q{x} {y} {x} {y + r}'
            f'Q{x} {y} {x - r} {y}Q{x} {y} {x} {y - r}Z" fill="{GOLD}"/>')


def derive(stats):
    """Merge profile config with fetched stats and work out level and XP thresholds."""
    s = {**PROFILE, "season": date.today().year, "sample": False, **stats}
    s["level"] = max(1, int(math.sqrt(s["xp"] / 10)))
    s["xp_next"] = 10 * (s["level"] + 1) ** 2
    return s


def render(s):
    rnd = random.Random(9)
    out = []
    add = out.append

    # ---------- card (left) ----------
    cx, cy = 190, 226  # centre of the art window
    arcs = {k: [] for k in range(4)}
    for i in range(46):
        rad = 8 + i * 5.6
        a0 = rnd.random() * math.tau
        a1 = a0 + math.pi * (0.3 + rnd.random() * 1.2)
        x0, y0 = cx + rad * math.cos(a0), cy + rad * math.sin(a0)
        x1, y1 = cx + rad * math.cos(a1), cy + rad * math.sin(a1)
        large = 1 if a1 - a0 > math.pi else 0
        op = 0.25 + rnd.random() * 0.6
        w = 2.4 if i % 7 == 0 else 1
        arcs[i % 4].append(
            f'<path d="M{x0:.1f} {y0:.1f}A{rad:.1f} {rad:.1f} 0 {large} 1 {x1:.1f} {y1:.1f}" '
            f'stroke="{ART[i % 4]}" stroke-opacity="{op:.2f}" stroke-width="{w}"/>')
    dust = []
    for i in range(70):
        x, y = 64 + rnd.random() * 252, 118 + rnd.random() * 194
        d = -rnd.random() * 4
        dust.append(f'<rect class="tw" style="animation-delay:{d:.2f}s" x="{x:.1f}" y="{y:.1f}" '
                    f'width="1.3" height="1.3" fill="{INK}" opacity="{0.3 + rnd.random() * 0.6:.2f}"/>')

    add(f'''
  <g class="float">
    <g class="card-in">
      <rect x="40" y="40" width="300" height="460" fill="{CARD}"/>
      <g clip-path="url(#cardClip)"><rect class="holo" x="-160" y="20" width="160" height="500" fill="url(#holo)"/></g>
    </g>
    <rect class="draw" pathLength="100" stroke-dasharray="100 100" x="40" y="40" width="300" height="460" fill="none" stroke="{GOLD}"/>
    <rect class="fade d4" x="50" y="50" width="280" height="440" fill="none" stroke="{GOLD}" stroke-opacity=".45"/>
    {"".join(diamond(x, y, 6, fill=BG, stroke=GOLD, **{"class": "pop", "style": f"animation-delay:{0.2 + k * 0.15:.2f}s"}) for k, (x, y) in enumerate([(40, 40), (340, 40), (340, 500), (40, 500)]))}

    <g class="rise d5">
      <text x="64" y="88" class="serif b" font-size="25" fill="{INK}">{esc(s["name"])}</text>
      <text x="64" y="106" class="mono" font-size="9" letter-spacing="1.8" fill="#a39a86">@{esc(s["handle"].upper())}</text>
      <circle cx="306" cy="86" r="19" fill="none" stroke="{GOLD}"/>
      <circle class="spin-slow" cx="306" cy="86" r="23" fill="none" stroke="{GOLD}" stroke-opacity=".5" stroke-dasharray="1 4"/>
      <text x="306" y="80" text-anchor="middle" class="mono" font-size="7" letter-spacing="1" fill="{GOLD}">LV</text>
      <text x="306" y="97" text-anchor="middle" class="serif" font-size="17" fill="{GOLD}">{s["level"]}</text>
    </g>

    <g class="fade d6">
      <rect x="64" y="118" width="252" height="194" fill="#0f0e15"/>
      <g clip-path="url(#artClip)" fill="none" stroke-linecap="round">
        {"".join(dust)}
        <g class="orbit o0">{"".join(arcs[0])}</g>
        <g class="orbit o1">{"".join(arcs[1])}</g>
        <g class="orbit o2">{"".join(arcs[2])}</g>
        <g class="orbit o3">{"".join(arcs[3])}</g>
        <circle class="halo" cx="{cx}" cy="{cy}" r="16" fill="{INK}" opacity=".1"/>
        <circle cx="{cx}" cy="{cy}" r="5" fill="{INK}"/>
      </g>
      <rect x="64" y="118" width="252" height="194" fill="none" stroke="{GOLD}" stroke-opacity=".45"/>
    </g>

    <g class="rise d7">
      <path d="M64 326H316M64 352H316" stroke="{GOLD}" stroke-opacity=".3"/>
      <text x="64" y="343" class="mono" font-size="9.5" letter-spacing="1.6" fill="{GOLD}">{esc(s["klass"].upper())}</text>
      <text x="316" y="343" text-anchor="end" class="mono" font-size="9.5" letter-spacing="1.6" fill="{GOLD}">{esc(s["rarity"].upper())}</text>
      {sparkle(229, 339.5, 6, "tw-gold")}
    </g>

    <g class="rise d8">
      <text class="serif i" font-size="15" fill="#d9d2c4">
        <tspan x="64" y="378"><tspan class="serif b" font-style="normal" fill="{INK}">Render.</tspan> Turns raw ideas into living</tspan>
        <tspan x="64" y="398">interfaces. Each merged pull request</tspan>
        <tspan x="64" y="418">grants +1 star to every ally.</tspan>
      </text>
    </g>

    <g class="rise d9" text-anchor="middle">
      {"".join(f'<text x="{x}" y="463" class="serif b" font-size="23" fill="{INK}">{v}</text><text x="{x}" y="479" class="mono" font-size="9" letter-spacing="1.5" fill="{DIM}">{label}</text>' for x, v, label in [(106, s["commits"], "ATK"), (190, s["prs"], "MANA"), (274, s["reviews"], "WIS")])}
    </g>
  </g>''')

    # ---------- sheet (right) ----------
    frac = min(1, s["xp"] / s["xp_next"])
    fill_w = round(458 * frac, 1)
    sample = (f'<text x="840" y="52" text-anchor="end" class="mono" font-size="9" letter-spacing="1.8" '
              f'fill="#c9a14a" opacity=".85">SAMPLE DATA</text>') if s["sample"] else ""
    add(f'''
  <g class="rise d3">
    <text x="380" y="52" class="mono" font-size="10" letter-spacing="2.6" fill="{DIM}">CHARACTER SHEET · SEASON {s["season"]}</text>
    {sample}
    <text x="380" y="100" class="serif" font-size="32" fill="{INK}">Level {s["level"]}<tspan class="mono" dx="12" font-size="15" fill="{DIM}">→</tspan><tspan class="serif i" dx="6" font-size="21" fill="{DIM}">{s["level"] + 1}</tspan></text>
    <text x="840" y="98" text-anchor="end" class="mono" font-size="12" fill="{GOLD}">{s["xp"]} / {s["xp_next"]} XP</text>
  </g>
  <rect class="fade d4" x="380" y="114" width="460" height="9" fill="none" stroke="{GOLD}" stroke-opacity=".5"/>
  <g clip-path="url(#xpClip)">
    <rect class="xpfill" x="381" y="115" width="{fill_w}" height="7" fill="{GOLD}"/>
    <rect class="shine" x="381" y="115" width="60" height="7" fill="url(#shine)"/>
  </g>
  <g class="xpmark">{diamond(381 + fill_w, 118.5, 6, fill=BG, stroke=GOLD, stroke_width=1.3)}<circle class="pulse" cx="{381 + fill_w}" cy="118.5" r="9" fill="none" stroke="{GOLD}"/></g>
  <text class="fade d10" x="380" y="142" font-size="10" fill="{DIM}"><tspan class="mono">1 XP = 1 contribution · {max(0, s["xp_next"] - s["xp"])} XP to next level</tspan></text>''')

    # radar
    rx, ry, R = 478, 266, 70
    vals = [max(.08, min(1, math.log1p(s[k]) / math.log1p(RADAR_CAPS[k])))
            for k in ("commits", "prs", "reviews", "issues", "repos", "longest_streak")]
    labels = ["STR", "DEX", "INT", "WIS", "CHA", "CON"]

    def pt(k, f):
        a = -math.pi / 2 + k * math.pi / 3
        return rx + R * f * math.cos(a), ry + R * f * math.sin(a)

    def poly(f):
        return " ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(k, f) for k in range(6)))

    grid = "".join(f'<polygon points="{poly(f)}" fill="none" stroke="{GOLD}" stroke-opacity="{.5 if f == 1 else .18}"/>' for f in (.33, .66, 1))
    spokes = "".join(f'<line x1="{rx}" y1="{ry}" x2="{pt(k, 1)[0]:.1f}" y2="{pt(k, 1)[1]:.1f}" stroke="{GOLD}" stroke-opacity=".15"/>' for k in range(6))
    lab = "".join(f'<text x="{pt(k, 1.2)[0]:.1f}" y="{pt(k, 1.2)[1] + 3:.1f}" text-anchor="middle" class="mono" font-size="8" fill="{DIM}">{t}</text>' for k, t in enumerate(labels))
    shape = " ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(k, v) for k, v in enumerate(vals)))
    verts = "".join(diamond(round(pt(k, v)[0], 1), round(pt(k, v)[1], 1), 4, fill=BG, stroke=GOLD, **{"class": "pop", "style": f"animation-delay:{1.6 + k * 0.08:.2f}s"}) for k, v in enumerate(vals))
    add(f'''
  <g class="fade d6">{grid}{spokes}{lab}</g>
  <g clip-path="url(#radarClip)"><path class="sweep" d="M{rx} {ry}L{rx} {ry - R}A{R} {R} 0 0 1 {pt(1, 1)[0]:.1f} {pt(1, 1)[1]:.1f}Z" fill="url(#sweep)"/></g>
  <polygon class="grow" points="{shape}" fill="{GOLD}" fill-opacity=".18" stroke="{GOLD}" stroke-width="1.4" stroke-linejoin="round"/>
  {verts}''')

    # attribute list
    rows = [("STR", "Commits", s["commits"]), ("DEX", "Pull requests", s["prs"]), ("INT", "Code reviews", s["reviews"]),
            ("WIS", "Issues", s["issues"]), ("CHA", "Repositories", s["repos"]), ("CON", "Longest streak", f'{s["longest_streak"]}d')]
    for i, (a, name, v) in enumerate(rows):
        y = 190 + i * 31
        add(f'''
  <g class="slide" style="animation-delay:{1.2 + i * 0.1:.2f}s">
    <text x="600" y="{y}" class="mono" font-size="10" letter-spacing="1.5" fill="{GOLD}">{a}</text>
    <text x="640" y="{y}" class="serif i" font-size="17" fill="#d9d2c4">{name}</text>
    <text x="840" y="{y}" text-anchor="end" class="serif b" font-size="17" fill="{INK}">{v}</text>
    <line x1="600" y1="{y + 9}" x2="840" y2="{y + 9}" stroke="#3a3644" stroke-dasharray="1 3"/>
  </g>''')

    # skill tree
    row_y = [414, 458]
    pos = {k: (x, row_y[r]) for k, (x, r, _) in SKILLS.items()}
    add(f'<text class="fade d10" x="380" y="378" font-size="10" letter-spacing="2.6" fill="{DIM}"><tspan class="mono">SKILL TREE</tspan></text>')
    for i, (a, b) in enumerate(SKILL_EDGES):
        (x0, y0), (x1, y1) = pos[a], pos[b]
        mx = (x0 + x1) / 2
        d = f"M{x0} {y0}C{mx} {y0} {mx} {y1} {x1} {y1}"
        add(f'<path class="draw" style="animation-delay:{2.0 + i * 0.14:.2f}s" pathLength="100" stroke-dasharray="100 100" d="{d}" fill="none" stroke="{GOLD}" stroke-opacity=".5"/>')
    for i, k in enumerate(SKILL_ORDER):
        x, y = pos[k]
        delay = 2.0 + i * 0.12
        add(f'''
  <g class="pop" style="animation-delay:{delay:.2f}s">
    {diamond(x, y, 7, fill=GOLD, stroke=GOLD)}
  </g>
  <text class="rise serif b" style="animation-delay:{delay + 0.1:.2f}s" x="{x}" y="{y - 13 if SKILLS[k][1] == 0 else y + 23}" text-anchor="middle" font-size="14" fill="{INK}">{SKILLS[k][2]}</text>''')

    body = "".join(out)

    # Collect every character the SVG renders so fonts can be subset to it (plus digits for future stats).
    text_chars = "".join(sorted(set(
        s["name"] + s["handle"].upper() + s["klass"].upper() + s["rarity"].upper()
        + "0123456789 /·→+?.dLVXPATKMNWISTRDEXCOHRSEFCHAP"
        + "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ" + "@=:-,'")))
    fonts = "".join([
        font_face("CG", HERE / "fonts/serif-600.ttf", 600, "normal", text_chars),
        font_face("CG", HERE / "fonts/serif-700.ttf", 700, "normal", text_chars),
        font_face("CG", HERE / "fonts/serif-600i.ttf", 600, "italic", text_chars),
        font_face("JBM", HERE / "fonts/mono-500.ttf", 500, "normal", text_chars),
    ])

    css = f"""
{fonts}
.serif{{font-family:'CG',Georgia,serif;font-weight:600}}
.b{{font-weight:700}}
.i{{font-style:italic}}
.mono{{font-family:'JBM',ui-monospace,monospace;font-weight:500}}

/* entrance: keyframes only hold the starting state, so the resting state is the final design */
.draw{{animation:draw 1.6s cubic-bezier(.6,0,.2,1) both}}
.fade{{animation:fade .9s ease both}}
.rise{{animation:rise .9s cubic-bezier(.2,.7,.2,1) both}}
.slide{{animation:slide .8s cubic-bezier(.2,.7,.2,1) both}}
.pop{{transform-box:fill-box;transform-origin:center;animation:pop .6s cubic-bezier(.3,1.6,.5,1) both}}
.grow{{transform-box:fill-box;transform-origin:center;animation:grow 1.1s cubic-bezier(.2,.8,.2,1) 1.3s both}}
.card-in{{animation:fade 1s ease .1s both}}
.d3{{animation-delay:.3s}}.d4{{animation-delay:.45s}}.d5{{animation-delay:.6s}}.d6{{animation-delay:.75s}}
.d7{{animation-delay:.9s}}.d8{{animation-delay:1.05s}}.d9{{animation-delay:1.2s}}.d10{{animation-delay:1.4s}}
.xpfill{{transform-box:fill-box;transform-origin:left center;animation:fillx 1.8s cubic-bezier(.6,0,.2,1) .7s both}}
.xpmark{{animation:markx 1.8s cubic-bezier(.6,0,.2,1) .7s both}}

/* ambient loops */
.float{{animation:float 7s ease-in-out 2.5s infinite}}
.holo{{animation:holo 7s ease-in-out 2s infinite}}
.orbit{{transform-box:view-box;transform-origin:{cx}px {cy}px}}
.o0{{animation:spin 70s linear infinite}}
.o1{{animation:spin 52s linear infinite reverse}}
.o2{{animation:spin 90s linear infinite}}
.o3{{animation:spin 40s linear infinite reverse}}
.spin-slow{{transform-box:fill-box;transform-origin:center;animation:spin 24s linear infinite}}
.halo{{transform-box:fill-box;transform-origin:center;animation:halo 3.6s ease-in-out infinite}}
.tw{{animation:tw 4s ease-in-out infinite}}
.tw-gold{{transform-box:fill-box;transform-origin:center;animation:twg 2.8s ease-in-out infinite}}
.sweep{{transform-box:view-box;transform-origin:{rx}px {ry}px;animation:spin 5s linear 2.4s infinite,fade .6s ease 2.4s both}}
.shine{{animation:shine 4.5s ease-in-out 2.8s infinite}}
.pulse{{transform-box:fill-box;transform-origin:center;animation:ring 2.4s ease-out 2.6s infinite}}

@keyframes draw{{from{{stroke-dashoffset:100}}}}
@keyframes fade{{from{{opacity:0}}}}
@keyframes rise{{from{{opacity:0;transform:translateY(8px)}}}}
@keyframes slide{{from{{opacity:0;transform:translateX(14px)}}}}
@keyframes pop{{from{{opacity:0;transform:scale(0) rotate(-90deg)}}}}
@keyframes grow{{from{{opacity:0;transform:scale(0)}}}}
@keyframes fillx{{from{{transform:scaleX(0)}}}}
@keyframes markx{{from{{transform:translateX(-{fill_w}px);opacity:0}}10%{{opacity:1}}}}
@keyframes float{{50%{{transform:translateY(-5px)}}}}
@keyframes holo{{0%{{transform:translateX(0)}}45%,100%{{transform:translateX(520px)}}}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
@keyframes halo{{50%{{transform:scale(1.6);opacity:.05}}}}
@keyframes tw{{50%{{opacity:.05}}}}
@keyframes twg{{50%{{transform:scale(.55) rotate(45deg);opacity:.6}}}}
@keyframes shine{{0%{{transform:translateX(-70px)}}60%,100%{{transform:translateX({fill_w + 10}px)}}}}
@keyframes ring{{0%{{transform:scale(.5);opacity:.9}}100%{{transform:scale(1.8);opacity:0}}}}

@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
"""

    defs = f"""
<defs>
  <clipPath id="cardClip"><rect x="40" y="40" width="300" height="460"/></clipPath>
  <clipPath id="artClip"><rect x="64" y="118" width="252" height="194"/></clipPath>
  <clipPath id="xpClip"><rect x="381" y="115" width="{fill_w}" height="7"/></clipPath>
  <clipPath id="radarClip"><circle cx="{rx}" cy="{ry}" r="{R}"/></clipPath>
  <linearGradient id="holo" x1="0" y1="0" x2="1" y2="0" gradientTransform="rotate(12)">
    <stop offset="0" stop-color="{GOLD}" stop-opacity="0"/>
    <stop offset=".45" stop-color="#f4e3b8" stop-opacity=".10"/>
    <stop offset=".55" stop-color="#bfe8ff" stop-opacity=".08"/>
    <stop offset="1" stop-color="{GOLD}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".75"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{GOLD}" stop-opacity=".35"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/>
  </linearGradient>
</defs>"""

    title = f'{s["name"]} — Level {s["level"]} {s["klass"]}'
    desc = (f'{s["xp"]} contributions this year; {s["commits"]} commits, {s["prs"]} pull requests, '
            f'{s["reviews"]} code reviews, {s["issues"]} issues, {s["repos"]} repositories, longest streak {s["longest_streak"]} days.')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="880" height="540" viewBox="0 0 880 540" role="img" aria-labelledby="t d">'
            f'<title id="t">{esc(title)}</title><desc id="d">{esc(desc)}</desc>'
            f'<style>{css}</style>{defs}'
            f'<rect width="880" height="540" rx="12" fill="{BG}"/>{body}</svg>')


if __name__ == "__main__":
    stats_path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "data/stats.json"
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE.parent / "assets/profile-card.svg"
    stats = json.loads(stats_path.read_text(encoding="utf-8"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(derive(stats)), encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size / 1024:.1f} KB)")
