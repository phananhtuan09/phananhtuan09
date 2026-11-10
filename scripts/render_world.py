"""Render the rest of the profile world: title banner and achievements.

Usage: python scripts/render_world.py data/stats.json assets/
"""
import json
import math
import random
import sys
from pathlib import Path

from app_stack import app_stack
from render_card import derive
from svg_kit import (ART, BG, CARD, DIM, GOLD, INK, PALE, RULE, SOFT, corners, diamond, document, embers, esc,
                     foil_defs, foil_sheet, sparkle, starfield, write)

W = 880

# (name, stat key, unit, what it measures, thresholds for tiers I, II, III)
ACHIEVEMENTS = [
    ("Scribe", "commits", "COMMITS", "this season", (100, 500, 1000)),
    ("Questbreaker", "merged_prs_all_time", "PRS", "merged, all time", (25, 100, 250)),
    ("Unbroken", "longest_streak", "DAYS", "longest streak", (7, 21, 60)),
    ("Devoted", "active_days", "DAYS", "active this season", (50, 150, 250)),
    ("Architect", "repos", "REPOS", "founded", (10, 30, 60)),
    ("Wanderer", "repos_contributed", "REALMS", "contributed to", (5, 15, 30)),
    ("Seeker", "issues", "ISSUES", "opened this season", (10, 30, 60)),
    ("Veteran", "years_on_github", "YEARS", "on GitHub", (1, 3, 5)),
]
ROMAN = ["", "I", "II", "III"]


def frame(w, h, uid, inset=14):
    x, y, fw, fh = inset, inset, w - 2 * inset, h - 2 * inset
    return (f'<rect class="draw" pathLength="100" stroke-dasharray="100 100" x="{x}" y="{y}" width="{fw}" height="{fh}" fill="none" stroke="{GOLD}" stroke-opacity=".55"/>'
            f'<g class="fade d10" mask="url(#frameMask{uid})">{foil_sheet(uid, x - 2, y - 2, fw + 4, fh + 4)}</g>'
            f'{corners(x, y, fw, fh, r=5)}'), (f'<mask id="frameMask{uid}"><rect x="{x}" y="{y}" width="{fw}" height="{fh}" '
                                              f'fill="none" stroke="#fff" stroke-width="1.6"/></mask>{foil_defs(uid, fw)}')


def banner(s):
    H = 250
    rnd = random.Random(4)
    cx, cy = 744, H / 2
    arcs = []
    for i in range(22):
        rad = 100 + i * 7
        a0 = rnd.random() * math.tau
        a1 = a0 + math.pi * (0.2 + rnd.random() * 0.7)
        arcs.append(f'<path d="M{cx + rad * math.cos(a0):.1f} {cy + rad * math.sin(a0):.1f}A{rad} {rad} 0 0 1 '
                    f'{cx + rad * math.cos(a1):.1f} {cy + rad * math.sin(a1):.1f}" stroke="{ART[i % 4]}" stroke-opacity="{0.12 + rnd.random() * 0.3:.2f}"/>')
    sky, stack_css = app_stack(764)
    mastered = sum(1 for _, t in s["skills"].values() if t == "mastered")
    border, border_defs = frame(W, H, "B")
    body = f'''
  <g clip-path="url(#bannerClip)">
    <circle class="breathe" cx="{cx}" cy="{cy}" r="230" fill="url(#ambient)"/>
    {starfield(rnd, 20, 20, W - 40, H - 40, 90)}
    <g fill="none" stroke-linecap="round" class="spin s120" style="transform-origin:{cx}px {cy}px">{"".join(arcs)}</g>
    {embers(rnd, 560, H - 20, 300, 18, rise=200)}
  </g>
  <g class="fade d4" fill="none">{sky}</g>
  {border}
  <g class="land">
    <text x="56" y="122" class="serif b" font-size="70" fill="{INK}">{esc(s["name"])}</text>
  </g>
  <text class="rise d6" x="58" y="162" font-size="23" fill="{SOFT}"><tspan class="serif i" fill="{GOLD}">{esc(s["klass"])}</tspan><tspan class="serif i"> who turns raw ideas into living interfaces.</tspan></text>
  <g class="rise d8">
    <path d="M58 186H520" stroke="{GOLD}" stroke-opacity=".3"/>
    <text x="58" y="208" class="mono" font-size="11" letter-spacing="2" fill="{DIM}">LEVEL <tspan fill="{GOLD}">{s["level"]}</tspan> · <tspan fill="{GOLD}">{mastered}</tspan> SKILLS MASTERED · <tspan fill="{GOLD}">{s["merged_prs_all_time"]}</tspan> QUESTS COMPLETE</text>
  </g>'''
    css = ("\n.land{animation:land 1.2s cubic-bezier(.2,.9,.25,1) .2s both}\n@keyframes land{from{opacity:0;transform:translateY(-12px);filter:blur(8px)}}"
           + stack_css)
    defs = f'<clipPath id="bannerClip"><rect width="{W}" height="{H}" rx="12"/></clipPath>{border_defs}'
    title = f'{s["name"]} — {s["klass"]}'
    desc = (f'Level {s["level"]} {s["klass"]}, {mastered} skills mastered, {s["merged_prs_all_time"]} pull requests merged. '
            'Beside it, the layers of an app (data, server, interface, magic) float as enchanted tablets above a spell circle.')
    return document(W, H, title, desc, body, css, defs)


def tier_of(value, thresholds):
    return sum(1 for t in thresholds if value >= t)


def achievements(s):
    H = 312
    earned = 0
    out = []
    defs = [foil_defs("A", 60), f'<linearGradient id="barShine"><stop offset="0" stop-color="{PALE}" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="#fff8e8"/><stop offset="1" stop-color="{PALE}" stop-opacity="0"/></linearGradient>',
            '<linearGradient id="sheen"><stop offset="0" stop-color="#fff8e8" stop-opacity="0"/>'
            '<stop offset=".5" stop-color="#fff8e8" stop-opacity=".55"/><stop offset="1" stop-color="#fff8e8" stop-opacity="0"/></linearGradient>']
    for i, (name, key, unit, measure, thresholds) in enumerate(ACHIEVEMENTS):
        col, row = i % 4, i // 4
        x, y = 40 + col * 205, 116 + row * 96
        value = s[key]
        tier = tier_of(value, thresholds)
        earned += tier
        maxed = tier == 3
        target = thresholds[min(tier, 2)]
        frac = 1 if maxed else min(1, value / target)
        mx, my, r = x + 28, y + 30, 27
        bar_w = 112
        beat = 1.8 + i * 0.25  # this medallion's moment in the light that runs along the rows
        if maxed:
            defs.append(f'<mask id="medal{i}">{diamond(mx, my, r, fill="none", stroke="#fff", stroke_width=2.4)}</mask>')
            ring = (diamond(mx, my, r, fill=CARD, stroke=GOLD, stroke_width=2.4)
                    + f'<g mask="url(#medal{i})">{foil_sheet("A", mx - r - 2, my - r - 2, 60, 2 * r + 4)}</g>'
                    + f'<circle class="breathe" cx="{mx}" cy="{my}" r="24" fill="url(#coreGlow)"/>')
        elif tier:
            ring = diamond(mx, my, r, fill=CARD, stroke=GOLD, stroke_width=1.4, class_="glint",
                           style=f"animation-delay:{beat:.1f}s")
        else:
            ring = diamond(mx, my, r, fill=BG, stroke=GOLD, stroke_opacity=".35", stroke_dasharray="2 3")
        inner = diamond(mx, my, r - 6, fill="none", stroke=GOLD, stroke_opacity=".3",
                        **({"class_": "turn", "style": f"animation-delay:{beat:.1f}s"} if tier else {}))
        if maxed:
            inner += "".join(sparkle(round(mx + dx, 1), round(my + dy, 1), sr, class_="twk",
                                     style=f"animation-delay:{-k * 0.9:.1f}s")
                             for k, (dx, dy, sr) in enumerate([(-24, -20, 4), (25, -12, 3), (18, 24, 3.5)]))
        if tier:  # a band of light crosses the earned medallion face
            defs.append(f'<clipPath id="face{i}">{diamond(mx, my, r - 1)}</clipPath>')
            inner += (f'<g clip-path="url(#face{i})"><g transform="translate({mx} {my}) skewX(-22) translate({-mx} {-my})">'
                      f'<rect class="sheen" style="animation-delay:{beat:.2f}s" x="{mx - r - 22}" y="{my - r}" width="18" height="{2 * r}" fill="url(#sheen)"/></g></g>')
        numeral = (f'<text class="serif b{"" if maxed else " beat"}" style="animation-delay:{beat:.2f}s" x="{mx}" y="{my + 7}" text-anchor="middle" font-size="20" fill="{PALE if maxed else GOLD}">{ROMAN[tier]}</text>'
                   if tier else f'<text x="{mx}" y="{my + 4}" text-anchor="middle" class="mono" font-size="11" fill="{DIM}">—</text>')
        defs.append(f'<clipPath id="bar{i}"><rect x="{x + 70}" y="{y + 43}" width="{bar_w * frac:.1f}" height="5"/></clipPath>')
        spark = ("" if maxed or not frac else
                 f'<circle class="spark" style="animation-delay:{beat + 0.9:.2f}s" cx="{x + 70 + bar_w * frac:.1f}" cy="{y + 45.5}" r="3" fill="none" stroke="{PALE}" stroke-width="1.5"/>'
                 f'<circle cx="{x + 70 + bar_w * frac:.1f}" cy="{y + 45.5}" r="1.8" fill="{PALE}"/>')
        progress = f"MAX · {value} {unit}" if maxed else f"{value} / {target} {unit}"
        out.append(f'''
  <g class="pop" style="animation-delay:{0.4 + i * 0.09:.2f}s">{ring}{inner}{numeral}</g>
  <g class="slide" style="animation-delay:{0.5 + i * 0.09:.2f}s">
    <text x="{x + 70}" y="{y + 16}" class="serif b" font-size="19" fill="{INK if tier else DIM}">{name}</text>
    <text x="{x + 70}" y="{y + 34}" font-size="14" fill="{DIM}"><tspan class="serif i">{measure}</tspan></text>
    <rect x="{x + 70}" y="{y + 44}" width="{bar_w}" height="3" fill="{RULE}"/>
    <g clip-path="url(#bar{i})">
      <rect class="fillbar" style="animation-delay:{0.9 + i * 0.09:.2f}s" x="{x + 70}" y="{y + 44}" width="{bar_w * frac:.1f}" height="3" fill="{PALE if maxed else GOLD}"/>
      <rect class="shimmer" style="--bw:{bar_w * frac + 40:.1f}px;animation-delay:{beat + 0.25:.2f}s" x="{x + 30}" y="{y + 43}" width="40" height="5" fill="url(#barShine)"/>
    </g>{spark}
    <text x="{x + 70}" y="{y + 64}" class="mono" font-size="10.5" letter-spacing=".6" fill="{GOLD if tier else DIM}">{progress}</text>
  </g>''')
    total = 3 * len(ACHIEVEMENTS)
    head = f'''
  <text class="rise" x="40" y="70" font-size="36" fill="{INK}"><tspan class="serif b">Achievements</tspan></text>
  <text class="rise d3" x="840" y="70" text-anchor="end" font-size="16" fill="{DIM}"><tspan class="serif i">{earned} of {total} tiers earned</tspan></text>
  <path class="fade d3" d="M40 88H840" stroke="{GOLD}" stroke-opacity=".3"/>'''
    css = """
.glint{animation:glint 5s ease-in-out infinite}
@keyframes glint{0%,16%,100%{stroke:#d4b072;stroke-width:1.4px;filter:drop-shadow(0 0 0 rgba(244,227,184,0))}
  6%{stroke:#fff3d6;stroke-width:2.6px;filter:drop-shadow(0 0 10px rgba(244,227,184,.95))}}
.sheen{animation:sheen 5s cubic-bezier(.4,0,.2,1) infinite both}
@keyframes sheen{0%{transform:translateX(0)}16%,100%{transform:translateX(98px)}}
.beat{transform-box:fill-box;transform-origin:center;animation:beat 5s ease-out infinite}
@keyframes beat{0%,14%,100%{transform:scale(1);fill:#d4b072}5%{transform:scale(1.25);fill:#fff3d6}}
.turn{transform-box:fill-box;transform-origin:center;animation:turn 5s cubic-bezier(.6,0,.2,1) infinite}
@keyframes turn{0%,3%{transform:rotate(0);stroke-opacity:.3}8%{stroke:#fff3d6;stroke-opacity:1}14%,100%{transform:rotate(90deg);stroke-opacity:.3}}
.shimmer{animation:shimmer 5s cubic-bezier(.4,0,.2,1) infinite both}
@keyframes shimmer{0%{transform:translateX(0)}16%,100%{transform:translateX(var(--bw))}}
.spark{opacity:0;transform-box:fill-box;transform-origin:center;animation:spark 5s ease-out infinite}
@keyframes spark{0%{opacity:1;transform:scale(.6)}14%,100%{opacity:0;transform:scale(3.4)}}
.twk{transform-box:fill-box;transform-origin:center;animation:twk 2.7s ease-in-out infinite}
@keyframes twk{50%{transform:scale(.3) rotate(45deg);opacity:.3}}
.fillbar{transform-box:fill-box;transform-origin:left center;animation:fillx 1.4s cubic-bezier(.6,0,.2,1) both}
@keyframes fillx{from{transform:scaleX(0)}}"""
    title = f"Achievements — {earned} of {total} tiers earned"
    desc = "; ".join(f"{n}: tier {tier_of(s[k], t)} of 3 ({s[k]} {u.lower()} {m})" for n, k, u, m, t in ACHIEVEMENTS)
    return document(W, H, title, desc, head + "".join(out), css, "".join(defs))


if __name__ == "__main__":
    stats_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent / "data/stats.json"
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parent.parent / "assets"
    s = derive(json.loads(stats_path.read_text(encoding="utf-8")))
    write(out_dir / "banner.svg", banner(s))
    write(out_dir / "achievements.svg", achievements(s))
