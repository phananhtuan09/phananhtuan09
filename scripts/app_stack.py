"""The banner's centrepiece: the whole app as a stack of enchanted tablets.

Isometric tablets, one per layer (data, server, interface, magic), float above the
spell circle. On a loop they rise apart, gold threads join their corners, a spark
carries a request down through every layer and back up, a star rises for the user,
and the stack snaps shut again. Pure CSS, so it plays inside an <img>.
"""
from svg_kit import ART, BG, GOLD, PALE, diamond, esc, sigil, sparkle


def mix(a, b, t):
    pa, pb = [int(a[i:i + 2], 16) for i in (1, 3, 5)], [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(pa, pb))


W, H, SC = 100, 70, .74
GLOW = "#fff3d6"


def P(ox, oy, x, y):
    return ox + (x - y) * .866 * SC, oy + (x + y) * .5 * SC


def pts(ps):
    return " ".join(f"{a:.1f},{b:.1f}" for a, b in ps)


def frame_art(c, runes, uid):
    """Gilded tablet frame in panel space: double border, corner gems, runes along the margin."""
    gems = "".join(diamond(x, y, 2.6, fill=GOLD) for x, y in ((0, 0), (W, 0), (W, H), (0, H)))
    edge = f"M5 3.6H{W - 5}M{W - 3.6} 5V{H - 5}M{W - 5} {H - 3.6}H5M3.6 {H - 5}V5"
    return (f'<rect x="7" y="7" width="{W - 14}" height="{H - 14}" fill="none" stroke="{c}" stroke-opacity=".45" stroke-width=".7"/>'
            f'<path id="mg{uid}" d="{edge}" fill="none"/>'
            f'<text class="mono" font-size="2.6" letter-spacing=".6" fill="{c}" fill-opacity=".85"><textPath href="#mg{uid}">{esc(runes)}</textPath></text>'
            f'{gems}')


def vault(c):
    tables = [(12, 12, 24, 22), (44, 14, 22, 18), (72, 12, 18, 26), (20, 42, 26, 16), (58, 42, 30, 16)]
    out = ""
    for x, y, w, h in tables:
        rows = "".join(f'<path d="M{x + 2} {y + 7 + j * 4}h{w - 4}" stroke="{c}" stroke-opacity=".55" stroke-width=".8"/>' for j in range(int((h - 7) / 4)))
        out += (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="1" fill="{mix(c, BG, .8)}" stroke="{c}" stroke-width=".8"/>'
                f'<rect x="{x}" y="{y}" width="{w}" height="4.5" fill="{c}" fill-opacity=".8"/>{rows}')
    links = f'<path class="flow" d="M36 22H44M66 22H72M30 34V42M58 32V42" stroke="{PALE}" stroke-width=".9" stroke-dasharray="1.5 1.5" fill="none"/>'
    return out + links


def forge(c):
    hub = (50, 35)
    ends = [(16, 16), (16, 54), (50, 12), (84, 16), (84, 54), (50, 58)]
    lines = "".join(f'M{hub[0]} {hub[1]}L{x} {y}' for x, y in ends)
    nodes = "".join(f'<rect x="{x - 4}" y="{y - 3}" width="8" height="6" rx="1" fill="{mix(c, BG, .7)}" stroke="{c}" stroke-width=".8"/>' for x, y in ends)
    return (f'<path d="{lines}" stroke="{c}" stroke-opacity=".5" stroke-width="1"/>'
            f'<path class="flow fast" d="{lines}" stroke="{GLOW}" stroke-width="1.1" stroke-dasharray="2 6" fill="none"/>{nodes}'
            f'<circle cx="{hub[0]}" cy="{hub[1]}" r="9" fill="{mix(c, BG, .55)}" stroke="{c}" stroke-width="1.2"/>'
            f'<circle class="ember-core" cx="{hub[0]}" cy="{hub[1]}" r="4" fill="{GLOW}"/>')


def weave(c):
    blocks = [(10, 10, 80, 9, GOLD), (10, 23, 20, 37, mix(GOLD, BG, .45)), (35, 23, 55, 18, ART[1]), (35, 45, 26, 15, ART[2]), (64, 45, 26, 15, ART[3])]
    out = "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="1.5" fill="{col}" fill-opacity=".6" stroke="{GOLD}" stroke-opacity=".6" stroke-width=".6"/>' for x, y, w, h, col in blocks)
    out += (f'<path d="M39 29h32M39 34h40M14 29h10M14 35h8M14 41h11" stroke="{PALE}" stroke-width="1.6" stroke-linecap="round" stroke-opacity=".85"/>'
            f'{diamond(14, 14.5, 2.2, fill=PALE)}<path d="M20 14.5h20" stroke="{BG}" stroke-width="1.6" stroke-linecap="round" stroke-opacity=".7"/>')
    return out


def spells(c):
    return (f'<rect x="30" y="47" width="22" height="5" rx="2.5" fill="none" stroke="{PALE}"/>'
            f'<rect class="jsbar" x="30" y="47" width="22" height="5" rx="2.5" fill="{PALE}"/>'
            f'<rect x="64" y="46" width="14" height="7" rx="3.5" fill="none" stroke="{PALE}"/>'
            f'<circle class="knob" cx="67.5" cy="49.5" r="2.4" fill="{GLOW}"/>'
            f'<g class="twk">{sparkle(80, 17, 4)}</g><g class="twk" style="animation-delay:-1.2s">{sparkle(22, 24, 3)}</g>'
            f'<circle class="pingr" cx="84" cy="17" r="3" fill="none" stroke="{GLOW}"/>'
            f'<path class="cursor" d="M50 24l0 9 2.5-2.4 2 4.2 1.6-.8-2-4.1 3.4-.2z" fill="{GLOW}" stroke="{BG}" stroke-width=".6"/>'
            f'<path class="flow" d="M14 58Q40 52 52 32" fill="none" stroke="{PALE}" stroke-opacity=".7" stroke-dasharray="1 3"/>')


def app_stack(cx):
    """Returns (svg, css) for the stack centred on x = cx."""
    C = 11.0
    p = lambda t: f"{t / C * 100:.2f}%"
    fy = 212
    layers = [  # uid, label, accent, art, runes, centre y
        ("vault", "DATA", ART[2], vault, "PERSIST · QUERY · INDEX · ", 184),
        ("forge", "SERVER", ART[1], forge, "ROUTE · GUARD · RESOLVE · ", 147),
        ("weave", "INTERFACE", GOLD, weave, "RENDER · COMPOSE · STYLE · ", 110),
        ("spell", "MAGIC", PALE, spells, "HYDRATE · ANIMATE · DELIGHT · ", 73),
    ]
    ox = cx - (W / 2 - H / 2) * .866 * SC
    half = (W + H) / 2 * .5 * SC
    out, labels, threads, css = [], [], [], []
    req = {"spell": 3.6, "weave": 3.9, "forge": 4.2, "vault": 4.5}
    res = {"forge": 5.0, "weave": 5.3, "spell": 5.6}
    for i, (uid, label, c, art, runes, y) in enumerate(layers):
        oy = y - half
        corners = [P(ox, oy, 0, 0), P(ox, oy, W, 0), P(ox, oy, W, H), P(ox, oy, 0, H)]
        th = 4
        glass = uid == "spell"
        side = (f'<polygon points="{pts([corners[1], corners[2], (corners[2][0], corners[2][1] + th), (corners[1][0], corners[1][1] + th)])}" fill="{mix(c, BG, .5)}" fill-opacity="{.35 if glass else 1}"/>'
                f'<polygon points="{pts([corners[3], corners[2], (corners[2][0], corners[2][1] + th), (corners[3][0], corners[3][1] + th)])}" fill="{mix(c, BG, .68)}" fill-opacity="{.35 if glass else 1}"/>')
        m = f"matrix({.866 * SC:.3f} {.5 * SC:.3f} {-.866 * SC:.3f} {.5 * SC:.3f} {ox:.1f} {oy:.1f})"
        bg = (f'<rect width="{W}" height="{H}" rx="2" fill="{GLOW if glass else "#14121a"}" fill-opacity="{.07 if glass else 1}" stroke="{GOLD}" stroke-width="1.3"/>')
        # the border lights up as a request passes down and the answer climbs back
        beats = sorted(t for t in (req.get(uid), res.get(uid)) if t)
        frames = "".join(f"{p(t - .05)}{{opacity:0}}{p(t + .1)}{{opacity:1}}{p(t + .6)}{{opacity:0}}" for t in beats)
        css.append(f"#lit-{uid}{{opacity:0;animation:lit-{uid} {C}s ease-out 1s infinite backwards}}@keyframes lit-{uid}{{0%{{opacity:0}}{frames}100%{{opacity:0}}}}")
        lit = f'<rect id="lit-{uid}" width="{W}" height="{H}" rx="2" fill="{c}" fill-opacity=".18" stroke="{GLOW}" stroke-width="2.2"/>'
        out.append(f'<g class="lay" style="--c:{(184 - i * 7) - y}px">{side}<g transform="{m}">{bg}{art(c)}{frame_art(c, runes * 4, uid)}{lit}</g></g>')
        lx, ly = corners[3]
        labels.append(f'<g class="lab" text-anchor="end">{diamond(lx - 8, ly, 2.4, fill=c)}'
                      f'<text x="{lx - 15:.1f}" y="{ly + 3.5:.1f}" class="mono" font-size="10" letter-spacing="1.8" fill="{c}">{label}</text></g>')
        if i:
            below = layers[i - 1][5] - half
            for corner in ((0, 0), (W, 0), (W, H), (0, H)):
                x0, y0 = P(ox, oy, *corner)
                y1 = P(ox, below, *corner)[1]
                threads.append(f'M{x0:.1f} {y0:.1f}V{y1:.1f}')
    th_d = "".join(threads)
    spine_top, spine_bot = layers[-1][5], layers[0][5]
    spark = diamond(cx, spine_top, 3.4, fill=GLOW)
    css.append(f"""
.lay{{animation:lay {C}s cubic-bezier(.65,0,.35,1) 1s infinite backwards}}
@keyframes lay{{0%,{p(1.2)}{{transform:translateY(var(--c))}}{p(2.8)},{p(8.6)}{{transform:none}}{p(10)},100%{{transform:translateY(var(--c))}}}}
.lab{{animation:lab {C}s ease 1s infinite backwards}}
@keyframes lab{{0%,{p(2.6)}{{opacity:0}}{p(3.2)},{p(8.2)}{{opacity:1}}{p(8.6)},100%{{opacity:0}}}}
.thread{{stroke-dasharray:1 1;animation:thread {C}s ease-out 1s infinite backwards}}
@keyframes thread{{0%,{p(2.8)}{{stroke-dashoffset:1;opacity:0}}{p(3.4)}{{stroke-dashoffset:0;opacity:1}}{p(8.2)}{{opacity:1;stroke-dashoffset:0}}{p(8.5)},100%{{opacity:0;stroke-dashoffset:0}}}}
.runeflow{{stroke-dasharray:2 10;animation:runeflow 1.2s linear infinite}}
@keyframes runeflow{{to{{stroke-dashoffset:-12}}}}
.rf-wrap{{animation:lab {C}s ease 1s infinite backwards}}
.spark{{opacity:0;animation:spark {C}s cubic-bezier(.5,0,.5,1) 1s infinite backwards}}
@keyframes spark{{0%,{p(3.5)}{{opacity:0;transform:none}}{p(3.6)}{{opacity:1;transform:none}}{p(4.5)}{{opacity:1;transform:translateY({spine_bot - spine_top}px)}}{p(4.6)}{{opacity:1;transform:translateY({spine_bot - spine_top}px)}}{p(5.6)}{{opacity:1;transform:none}}{p(5.7)},100%{{opacity:0;transform:none}}}}
.crown{{transform-box:fill-box;transform-origin:center;opacity:0;animation:crown {C}s ease-out 1s infinite backwards}}
@keyframes crown{{0%,{p(5.6)}{{opacity:0;transform:scale(.3)}}{p(5.8)}{{opacity:1;transform:scale(1.8) rotate(45deg);filter:drop-shadow(0 0 10px #fff3d6)}}{p(7)},{p(8.2)}{{opacity:1;transform:scale(1) rotate(90deg)}}{p(8.6)},100%{{opacity:0;transform:scale(1) rotate(90deg)}}}}
.snap{{opacity:0;transform-box:fill-box;transform-origin:center;animation:snap {C}s ease-out 1s infinite backwards}}
@keyframes snap{{0%,{p(9.9)}{{opacity:0;transform:scale(.6)}}{p(10)}{{opacity:1;transform:scale(.8)}}{p(10.8)},100%{{opacity:0;transform:scale(1.6)}}}}
.flow{{animation:runeflow 1.6s linear infinite}}.flow.fast{{animation-duration:.9s}}
.ember-core{{animation:breathe 1.6s ease-in-out infinite}}
.jsbar{{transform-box:fill-box;transform-origin:left;animation:jsbar 3s ease-in-out infinite}}
@keyframes jsbar{{0%{{transform:scaleX(.1)}}60%,100%{{transform:scaleX(1)}}}}
.knob{{animation:knob 3s ease-in-out infinite}}
@keyframes knob{{0%,40%{{transform:none}}55%,90%{{transform:translateX(7px)}}}}
.pingr{{transform-box:fill-box;transform-origin:center;animation:pingr 1.8s ease-out infinite}}
@keyframes pingr{{from{{transform:scale(1);opacity:1}}to{{transform:scale(3.4);opacity:0}}}}
.cursor{{animation:cursor 4.5s ease-in-out infinite}}
@keyframes cursor{{0%,100%{{transform:none}}35%{{transform:translate(12px,12px)}}65%{{transform:translate(22px,-8px)}}}}
.twk{{transform-box:fill-box;transform-origin:center;animation:twk 2.7s ease-in-out infinite}}
@keyframes twk{{50%{{transform:scale(.3) rotate(45deg);opacity:.3}}}}
""")
    floor = f'<g transform="translate(0 {fy}) scale(1 .3) translate(0 {-fy})">{sigil(cx, fy, 96, "B")}</g>'
    floor_label = (f'<g class="lab" text-anchor="end">{diamond(cx - 104, fy, 2.4, fill=GOLD)}'
                   f'<text x="{cx - 111}" y="{fy + 3.5}" class="mono" font-size="10" letter-spacing="1.8" fill="{GOLD}">DEPLOY</text></g>')
    thread_svg = (f'<path class="thread" d="{th_d}" pathLength="1" stroke="{GOLD}" stroke-opacity=".55" fill="none"/>'
                  f'<g class="rf-wrap"><path class="runeflow" d="{th_d}" stroke="{GLOW}" stroke-width="1.4" fill="none"/></g>')
    top = layers[-1][5] - half
    crown = f'<g class="crown">{sparkle(cx, top - 11, 8)}</g>'
    snap = f'<ellipse class="snap" cx="{cx}" cy="{layers[0][5]}" rx="{half * 2:.0f}" ry="{half:.0f}" fill="none" stroke="{GLOW}" stroke-width="1.5"/>'
    svg = (f'{floor}{thread_svg}{"".join(out)}'
           f'<g class="spark">{spark}</g>{crown}{snap}{floor_label}{"".join(labels)}')
    return svg, "".join(css)
