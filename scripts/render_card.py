"""Render the animated RPG character-card SVG for the GitHub profile README.

Usage: python scripts/render_card.py data/stats.json assets/profile-card.svg
"""
import json
import math
import random
import sys
from datetime import date
from pathlib import Path

from svg_kit import (ART, BG, CARD, DIM, GOLD, INK, PALE, PROFILE, RULE, SOFT, corners, diamond, document,
                     embers, esc, foil_defs, foil_sheet, level_of, sigil, sparkle, starfield, write)

HERE = Path(__file__).parent
W, H = 880, 580

# Skill tree: languages on the top row (labels above), frameworks, runtimes and databases below.
# key: (x, row, label, GitHub languages or npm packages that count as using it)
SKILLS = {
    "html": (412, 0, "HTML", ["HTML"]),
    "css": (492, 0, "CSS", ["CSS", "SCSS", "Less"]),
    "js": (572, 0, "JavaScript", ["JavaScript"]),
    "ts": (652, 0, "TypeScript", ["TypeScript"]),
    "php": (732, 0, "PHP", ["PHP", "Blade"]),
    "py": (812, 0, "Python", ["Python"]),
    "react": (492, 1, "React", ["react"]),
    "next": (572, 1, "Next.js", ["next"]),
    "node": (652, 1, "Node.js", ["package.json"]),
    "nest": (732, 1, "NestJS", ["@nestjs/core"]),
    "mysql": (812, 1, "MySQL", ["mysql", "mysql2"]),
}
SKILL_EDGES = [("html", "css"), ("css", "js"), ("js", "ts"), ("js", "react"), ("react", "next"),
               ("js", "node"), ("ts", "nest"), ("node", "nest"), ("php", "mysql")]
# Repositories that use a skill: 10+ masters it, 3+ trains it, fewer is a novice's first steps.
TIERS = [(10, "mastered"), (3, "trained"), (0, "novice")]

# Radar axes reach the rim at these values; a log scale keeps small numbers visible.
RADAR_CAPS = {"commits": 1500, "prs": 150, "active_days": 365, "issues": 60, "repos": 60, "longest_streak": 90}


def derive(stats):
    s = {**PROFILE, "season": date.today().year, "sample": False,
         "repo_languages": {}, "repo_packages": {}, **stats}
    s["level"], s["xp_next"] = level_of(s["xp"])
    usage = {**s["repo_languages"], **s["repo_packages"]}
    s["skills"] = {}
    for key, (*_, sources) in SKILLS.items():
        n = sum(usage.get(src, 0) for src in sources)
        s["skills"][key] = (n, next(t for floor, t in TIERS if n >= floor))
    return s


def card(s, rnd):
    x, y, w, h = 40, 40, 300, 500
    ax, ay, aw, ah = 64, 122, 252, 216  # art window
    cx, cy = ax + aw / 2, ay + ah / 2
    arcs = []
    for i in range(40):
        rad = 30 + i * 5.2
        a0 = rnd.random() * math.tau
        a1 = a0 + math.pi * (0.3 + rnd.random() * 1.1)
        x0, y0 = cx + rad * math.cos(a0), cy + rad * math.sin(a0)
        x1, y1 = cx + rad * math.cos(a1), cy + rad * math.sin(a1)
        arcs.append(f'<path d="M{x0:.1f} {y0:.1f}A{rad:.1f} {rad:.1f} 0 {1 if a1 - a0 > math.pi else 0} 1 {x1:.1f} {y1:.1f}" '
                    f'stroke="{ART[i % 4]}" stroke-opacity="{0.15 + rnd.random() * 0.35:.2f}"/>')
    stats = [(106, s["years_on_github"], "SEASONS"), (190, s["repos_contributed"], "REALMS"),
             (274, s["merged_prs_all_time"], "QUESTS")]
    return f'''
  <circle class="breathe" cx="{x + w / 2}" cy="{y + h / 2}" r="330" fill="url(#ambient)"/>
  <g clip-path="url(#sceneClip)">{embers(rnd, x - 10, y + h - 10, w + 20, 26, rise=420)}</g>
  <g class="float">
    <rect class="fade" x="{x}" y="{y}" width="{w}" height="{h}" fill="{CARD}"/>
    <g clip-path="url(#cardClip)"><rect class="holo" x="-160" y="{y - 20}" width="160" height="{h + 40}" fill="url(#holo)"/></g>
    <rect class="draw" pathLength="100" stroke-dasharray="100 100" x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{GOLD}" stroke-width="2.4"/>
    <g class="fade d10" mask="url(#frameMask)">{foil_sheet("C", x - 4, y - 4, w + 8, h + 8)}</g>
    <rect class="fade d4" x="{x + 10}" y="{y + 10}" width="{w - 20}" height="{h - 20}" fill="none" stroke="{GOLD}" stroke-opacity=".45"/>
    {corners(x, y, w, h, r=7)}

    <g class="rise d5">
      <text x="64" y="90" class="serif b" font-size="26" fill="{INK}">{esc(s["name"])}</text>
      <text x="64" y="109" class="mono" font-size="11" letter-spacing="1.6" fill="#a39a86">@{esc(s["handle"].upper())}</text>
      <circle cx="304" cy="86" r="20" fill="none" stroke="{GOLD}"/>
      <circle class="spin-fill" cx="304" cy="86" r="24.5" fill="none" stroke="{GOLD}" stroke-opacity=".5" stroke-dasharray="1 4"/>
      <text x="304" y="80" text-anchor="middle" class="mono" font-size="8" letter-spacing="1" fill="{GOLD}">LV</text>
      <text x="304" y="98" text-anchor="middle" class="serif b" font-size="18" fill="{GOLD}">{s["level"]}</text>
    </g>

    <g class="fade d6">
      <rect x="{ax}" y="{ay}" width="{aw}" height="{ah}" fill="#0f0e15"/>
      <g clip-path="url(#artClip)" fill="none" stroke-linecap="round">
        {starfield(rnd, ax, ay, aw, ah, 60)}
        <g class="spin s120 rev" style="transform-origin:{cx}px {cy}px">{"".join(arcs)}</g>
        {sigil(cx, cy, 84, "C")}
      </g>
      <rect x="{ax}" y="{ay}" width="{aw}" height="{ah}" fill="none" stroke="{GOLD}" stroke-opacity=".45"/>
    </g>

    <g class="rise d7">
      <path d="M64 356H316M64 384H316" stroke="{GOLD}" stroke-opacity=".3"/>
      <text x="64" y="374" class="mono" font-size="11" letter-spacing="1.8" fill="{GOLD}">{esc(s["klass"].upper())}</text>
      <text x="316" y="374" text-anchor="end" class="mono" font-size="11" letter-spacing="1.8" fill="{PALE}">{esc(s["rarity"].upper())}</text>
      {sparkle(222, 370, 6, class_="tw-gold")}
    </g>

    <g class="rise d8">
      <text class="serif i" font-size="16" fill="{SOFT}">
        <tspan x="64" y="414"><tspan class="b" font-style="normal" fill="{INK}">Render.</tspan> Turns raw ideas into living</tspan>
        <tspan x="64" y="435">interfaces. Each merged pull request</tspan>
        <tspan x="64" y="456">grants +1 star to every ally.</tspan>
      </text>
    </g>

    <path class="fade d9" d="M64 476H316" stroke="{GOLD}" stroke-opacity=".2"/>
    <g class="rise d9" text-anchor="middle">
      {"".join(f'<text x="{sx}" y="505" class="serif b" font-size="25" fill="{INK}">{v}</text><text x="{sx}" y="522" class="mono" font-size="10" letter-spacing="1.6" fill="{DIM}">{label}</text>' for sx, v, label in stats)}
    </g>
  </g>'''


def level_block(s):
    frac = min(1, s["xp"] / s["xp_next"])
    bx, by, bw = 380, 150, 460
    fill_w = round((bw - 2) * frac, 1)
    mx = bx + 1 + fill_w
    rays = "".join(
        f'<path d="M{mx + 12 * math.cos(a):.1f} {by + 5 + 12 * math.sin(a):.1f}L{mx + 30 * math.cos(a):.1f} {by + 5 + 30 * math.sin(a):.1f}"/>'
        for a in (k * math.tau / 10 for k in range(10)))
    return f'''
  <g class="numeral">
    <circle cx="470" cy="96" r="78" fill="url(#ambient)" class="breathe"/>
    <text x="378" y="136" class="serif i" font-size="26" fill="{SOFT}">Level</text>
    <text x="446" y="136" class="serif b" font-size="124" fill="{GOLD}">{s["level"]}</text>
  </g>
  <g class="rise d4" text-anchor="end">
    <text x="840" y="88" class="serif i" font-size="20" fill="{DIM}">next: Level {s["level"] + 1}</text>
    <text x="840" y="128" class="mono" font-size="15" fill="{GOLD}">{s["xp"]} / {s["xp_next"]} XP</text>
  </g>
  <rect class="fade d4" x="{bx}" y="{by}" width="{bw}" height="10" fill="none" stroke="{GOLD}" stroke-opacity=".5"/>
  <g clip-path="url(#xpClip)">
    <rect class="xpfill" x="{bx + 1}" y="{by + 1}" width="{fill_w}" height="8" fill="{GOLD}"/>
    <rect class="shine" x="{bx + 1}" y="{by + 1}" width="60" height="8" fill="url(#shine)"/>
  </g>
  <g class="burst" stroke="{PALE}" stroke-width="1.4" stroke-linecap="round">{rays}</g>
  <circle class="flash" cx="{mx}" cy="{by + 5}" r="10" fill="none" stroke="{PALE}" stroke-width="1.5"/>
  <g class="xpmark">{diamond(mx, by + 5, 7, fill=BG, stroke=GOLD, stroke_width=1.4)}<circle class="pulse" cx="{mx}" cy="{by + 5}" r="10" fill="none" stroke="{GOLD}"/></g>
  <text class="fade d10" x="{bx}" y="182" font-size="11" fill="{DIM}"><tspan class="mono">Season {s["season"]} · 1 XP = 1 contribution · {max(0, s["xp_next"] - s["xp"])} XP to go</tspan></text>''', fill_w


def radar_and_attributes(s):
    rx, ry, R = 478, 296, 66
    keys = ("commits", "prs", "active_days", "issues", "repos", "longest_streak")
    vals = [max(.08, min(1, math.log1p(s[k]) / math.log1p(RADAR_CAPS[k]))) for k in keys]
    labels = ["STR", "DEX", "INT", "WIS", "CHA", "CON"]

    def pt(k, f):
        a = -math.pi / 2 + k * math.pi / 3
        return rx + R * f * math.cos(a), ry + R * f * math.sin(a)

    def poly(f):
        return " ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(k, f) for k in range(6)))

    grid = "".join(f'<polygon points="{poly(f)}" fill="none" stroke="{GOLD}" stroke-opacity="{.5 if f == 1 else .18}"/>' for f in (.33, .66, 1))
    spokes = "".join(f'<line x1="{rx}" y1="{ry}" x2="{pt(k, 1)[0]:.1f}" y2="{pt(k, 1)[1]:.1f}" stroke="{GOLD}" stroke-opacity=".15"/>' for k in range(6))
    lab = "".join(f'<text x="{pt(k, 1.24)[0]:.1f}" y="{pt(k, 1.24)[1] + 4:.1f}" text-anchor="middle" class="mono" font-size="11" fill="{DIM}">{t}</text>' for k, t in enumerate(labels))
    shape = " ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(k, v) for k, v in enumerate(vals)))
    verts = "".join(diamond(round(pt(k, v)[0], 1), round(pt(k, v)[1], 1), 4, fill=BG, stroke=GOLD, class_="pop",
                            style=f"animation-delay:{1.6 + k * 0.08:.2f}s") for k, v in enumerate(vals))
    out = [f'''
  <g class="fade d6">{grid}{spokes}{lab}</g>
  <g clip-path="url(#radarClip)"><path class="sweep" d="M{rx} {ry}L{rx} {ry - R}A{R} {R} 0 0 1 {pt(1, 1)[0]:.1f} {pt(1, 1)[1]:.1f}Z" fill="url(#sweep)"/></g>
  <polygon class="grow" points="{shape}" fill="{GOLD}" fill-opacity=".18" stroke="{GOLD}" stroke-width="1.4" stroke-linejoin="round"/>
  {verts}''']
    rows = [("STR", "Commits", s["commits"]), ("DEX", "Pull requests", s["prs"]), ("INT", "Active days", s["active_days"]),
            ("WIS", "Issues", s["issues"]), ("CHA", "Repositories", s["repos"]), ("CON", "Longest streak", f'{s["longest_streak"]}d')]
    for i, (a, name, v) in enumerate(rows):
        y = 230 + i * 30
        out.append(f'''
  <g class="slide" style="animation-delay:{1.2 + i * 0.1:.2f}s">
    <text x="600" y="{y}" class="mono" font-size="11" letter-spacing="1.5" fill="{GOLD}">{a}</text>
    <text x="640" y="{y}" class="serif i" font-size="17" fill="{SOFT}">{name}</text>
    <text x="840" y="{y}" text-anchor="end" class="serif b" font-size="18" fill="{INK}">{v}</text>
    <line x1="600" y1="{y + 9}" x2="840" y2="{y + 9}" stroke="{RULE}" stroke-dasharray="1 3"/>
  </g>''')
    return "".join(out)


def skill_tree(s):
    row_y = [460, 512]
    pos = {k: (x, row_y[r]) for k, (x, r, *_) in SKILLS.items()}
    tier = {k: t for k, (_, t) in s["skills"].items()}
    rank = {"mastered": 2, "trained": 1, "novice": 0}
    legend = [("mastered", "MASTERED"), ("trained", "TRAINED"), ("novice", "NOVICE")]
    lx = 840
    leg = []
    for key, label in reversed(legend):
        tw = len(label) * 6.6 + 1.5 * (len(label) - 1)
        leg.append(f'<text x="{lx}" y="420" text-anchor="end" class="mono" font-size="10" letter-spacing="1.5" fill="{DIM}">{label}</text>')
        leg.append(node(lx - tw - 12, 416, key, small=True))
        lx -= tw + 34
    out = [f'<g class="fade d10"><text x="380" y="420" class="mono" font-size="11" letter-spacing="2.6" fill="{DIM}">SKILL TREE</text>{"".join(leg)}</g>']
    for i, (a, b) in enumerate(SKILL_EDGES):
        (x0, y0), (x1, y1) = pos[a], pos[b]
        mx = (x0 + x1) / 2
        op = [.25, .45, .7][min(rank[tier[a]], rank[tier[b]])]
        out.append(f'<path class="draw" style="animation-delay:{2.0 + i * 0.14:.2f}s" pathLength="100" stroke-dasharray="100 100" '
                   f'd="M{x0} {y0}C{mx} {y0} {mx} {y1} {x1} {y1}" fill="none" stroke="{GOLD}" stroke-opacity="{op}"/>')
    for i, k in enumerate(SKILLS):
        x, y = pos[k]
        delay = 2.0 + i * 0.12
        label_y = y - 16 if SKILLS[k][1] == 0 else y + 26
        color = DIM if tier[k] == "novice" else INK
        out.append(f'''
  <g class="pop" style="animation-delay:{delay:.2f}s">{node(x, y, tier[k])}</g>
  <text class="rise serif b" style="animation-delay:{delay + 0.1:.2f}s" x="{x}" y="{label_y}" text-anchor="middle" font-size="15" fill="{color}">{SKILLS[k][2]}</text>''')
    return "".join(out)


def node(x, y, tier, small=False):
    if tier == "mastered":
        r = 5 if small else 9
        ring = (f'<circle cx="{x}" cy="{y}" r="8" fill="none" stroke="{GOLD}" stroke-opacity=".6"/>' if small
                else f'<circle class="pulse-slow" cx="{x}" cy="{y}" r="13" fill="none" stroke="{GOLD}" stroke-opacity=".6"/>')
        glow = "" if small else f'<circle cx="{x}" cy="{y}" r="18" fill="url(#coreGlow)"/>'
        return glow + ring + diamond(x, y, r, fill=PALE, stroke=GOLD, stroke_width=1.2)
    if tier == "trained":
        return diamond(x, y, 4.5 if small else 7, fill=GOLD, stroke=GOLD)
    return diamond(x, y, 4.5 if small else 6.5, fill=BG, stroke=GOLD, stroke_opacity=".6")


def render(s):
    rnd = random.Random(9)
    level, fill_w = level_block(s)
    body = "".join([card(s, rnd), level, radar_and_attributes(s), skill_tree(s)])
    if s["sample"]:
        body += f'<text x="840" y="40" text-anchor="end" class="mono" font-size="10" letter-spacing="1.8" fill="#c9a14a">SAMPLE DATA</text>'

    css = f"""
.float{{animation:float 7s ease-in-out 2.5s infinite}}
.holo{{animation:holo 7s ease-in-out 2s infinite}}
.spin-fill{{transform-box:fill-box;transform-origin:center;animation:spin 24s linear infinite}}
.tw-gold{{transform-box:fill-box;transform-origin:center;animation:twg 2.8s ease-in-out infinite}}
.grow{{transform-box:fill-box;transform-origin:center;animation:grow 1.1s cubic-bezier(.2,.8,.2,1) 1.3s both}}
.sweep{{transform-box:view-box;transform-origin:478px 296px;animation:spin 5s linear 2.4s infinite,fade .6s ease 2.4s both}}

/* the level reveal: numeral lands, bar fills, the marker bursts */
.numeral{{animation:land 1.1s cubic-bezier(.2,.9,.25,1) .2s both}}
.xpfill{{transform-box:fill-box;transform-origin:left center;animation:fillx 1.8s cubic-bezier(.6,0,.2,1) .7s both}}
.xpmark{{animation:markx 1.8s cubic-bezier(.6,0,.2,1) .7s both}}
.burst{{opacity:0;transform-box:fill-box;transform-origin:center;animation:burst .9s cubic-bezier(.1,.8,.2,1) 2.45s both}}
.flash{{opacity:0;transform-box:fill-box;transform-origin:center;animation:flash 1.2s ease-out 2.45s both}}
.shine{{animation:shine 4.5s ease-in-out 3.2s infinite}}
.pulse{{transform-box:fill-box;transform-origin:center;animation:ring 2.4s ease-out 3.2s infinite}}
.pulse-slow{{transform-box:fill-box;transform-origin:center;animation:ring2 3.6s ease-out 3s infinite}}

@keyframes float{{50%{{transform:translateY(-5px)}}}}
@keyframes holo{{0%{{transform:translateX(0)}}45%,100%{{transform:translateX(520px)}}}}
@keyframes twg{{50%{{transform:scale(.55) rotate(45deg);opacity:.6}}}}
@keyframes grow{{from{{opacity:0;transform:scale(0)}}}}
@keyframes land{{from{{opacity:0;transform:translateY(-14px);filter:blur(6px)}}}}
@keyframes fillx{{from{{transform:scaleX(0)}}}}
@keyframes markx{{from{{transform:translateX(-{fill_w}px);opacity:0}}10%{{opacity:1}}}}
@keyframes burst{{0%{{opacity:0;transform:scale(.4)}}5%{{opacity:1}}100%{{opacity:0;transform:scale(1.5)}}}}
@keyframes flash{{0%{{opacity:0;transform:scale(.6)}}5%{{opacity:1}}100%{{opacity:0;transform:scale(3.2)}}}}
@keyframes shine{{0%{{transform:translateX(-70px)}}60%,100%{{transform:translateX({fill_w + 10}px)}}}}
@keyframes ring{{0%{{transform:scale(.5);opacity:.9}}100%{{transform:scale(1.8);opacity:0}}}}
@keyframes ring2{{0%{{transform:scale(.7);opacity:.7}}100%{{transform:scale(1.6);opacity:0}}}}
"""
    x, y, w, h = 40, 40, 300, 500
    defs = f"""
  <clipPath id="sceneClip"><rect width="{W}" height="{H}" rx="12"/></clipPath>
  <clipPath id="cardClip"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath>
  <clipPath id="artClip"><rect x="64" y="122" width="252" height="216"/></clipPath>
  <clipPath id="xpClip"><rect x="381" y="151" width="{fill_w}" height="8"/></clipPath>
  <clipPath id="radarClip"><circle cx="478" cy="296" r="66"/></clipPath>
  <mask id="frameMask"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#fff" stroke-width="2.4"/></mask>
  {foil_defs("C", w)}
  <linearGradient id="holo" x1="0" y1="0" x2="1" y2="0" gradientTransform="rotate(12)">
    <stop offset="0" stop-color="{GOLD}" stop-opacity="0"/><stop offset=".45" stop-color="{PALE}" stop-opacity=".1"/>
    <stop offset=".55" stop-color="#bfe8ff" stop-opacity=".08"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".75"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{GOLD}" stop-opacity=".35"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/>
  </linearGradient>"""
    title = f'{s["name"]} — Level {s["level"]} {s["klass"]}'
    mastered = [SKILLS[k][2] for k, (_, t) in s["skills"].items() if t == "mastered"]
    desc = (f'{s["xp"]} contributions this year; {s["commits"]} commits, {s["prs"]} pull requests, '
            f'{s["active_days"]} active days, {s["issues"]} issues, {s["repos"]} repositories, '
            f'longest streak {s["longest_streak"]} days. Mastered skills: {", ".join(mastered) or "none yet"}.')
    return document(W, H, title, desc, body, css, defs)


if __name__ == "__main__":
    stats_path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "data/stats.json"
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE.parent / "assets/profile-card.svg"
    write(out, render(derive(json.loads(stats_path.read_text(encoding="utf-8")))))
