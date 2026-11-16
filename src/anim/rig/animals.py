"""Chutney (the dog), Tola (the brass scale), the buffalo, the monkey, the cycle-rickshaw.

CHUTNEY: scruffy street dog, ochre with white chest/muzzle/socks, ONE ear (his left, which
flops/perks); the right ear is a little tufted stub. Curly tail, huge brown eyes, pink tongue.
TOLA: polished brass shop scale; stepped round base, slim pillar, a beam with two pans on chains;
a round plate at the fulcrum has an engraved face (eyes, mouth). Talks only in tilts and clanks.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import skia

from .. import core as K
from ..core import fill, stroke, limb, ellipse, smooth_path, poly, lerp, clamp


# =============================================================== CHUTNEY
@dataclass
class DogPose:
    x: float = 960
    y: float = 900
    s: float = 1.6
    flip: bool = False        # default faces screen-right
    mode: str = "stand"       # stand | walk | trot | sit | lie | float | beg
    phase: float = 0.0
    t: float = 0.0
    wag: float = 1.0          # tail wag energy 0..2
    ear: float = 0.5          # 0 flop .. 1 perked
    head_tilt: float = 0.0
    look_up: float = 0.0      # 0..1 raise head toward sky
    mouth: float = 0.0        # 0..1 open (talk/bark)
    tongue: bool = False
    expr: str = "happy"       # happy | sad | alert | sneeze | guilty | proud
    blink: float = 0.0
    alpha: float = 1.0
    light_glow: float = 0.0


def draw_dog(cv, d: DogPose):
    cv.save()
    cv.translate(d.x, d.y)
    cv.scale(-d.s if d.flip else d.s, d.s)
    if d.alpha < 1:
        pt = skia.Paint(); pt.setAlphaf(d.alpha); cv.saveLayer(None, pt)
    t = d.t
    trot = d.mode in ("walk", "trot")
    spd = 2.0 if d.mode == "trot" else 1.0
    bob = -abs(math.sin(d.phase * 2 * math.pi * spd)) * 5 if trot else math.sin(t * 2.4) * 1.0
    if d.mode == "float":
        bob = math.sin(t * 1.8) * 5
    if d.mode not in ("float",):
        cv.drawOval(skia.Rect.MakeLTRB(-70, -7, 75, 7), fill("#000000", 0.2))
    cv.translate(0, bob)
    sit = d.mode in ("sit", "beg")
    lie = d.mode == "lie"
    body_y = -62 if not lie else -30
    tilt = -18 if sit else 0
    lw = 3.0
    ochre, white, dark = "dog_ochre", "dog_white", "dog_dark"

    def leg(x0, y0, ang_deg, length=44, front=True, paw=True, col=ochre):
        a = math.radians(ang_deg)
        x1, y1 = x0 + math.sin(a) * length, y0 + math.cos(a) * length
        pth = limb(x0, y0, x1, y1, 15, 12)
        cv.drawPath(pth, fill(col if front else K.shade(col, -0.15)))
        cv.drawPath(pth, stroke("line", lw))
        if paw:
            pw = ellipse(x1 + 5, y1, 10, 6)
            cv.drawPath(pw, fill(white if front else K.shade(white, -0.12)))
            cv.drawPath(pw, stroke("line", lw * 0.9))

    # --- tail (behind)
    wagang = math.sin(t * (9 if d.wag > 1 else 6)) * 26 * d.wag
    if d.mode == "float":
        wagang = math.sin(t * 5) * 15
    tx, ty = (-52, body_y - 6) if not sit else (-40, -24)
    cv.save(); cv.translate(tx, ty); cv.rotate(-35 + wagang)
    tail = smooth_path([(0, 0), (-18, -14), (-26, -34), (-14, -46), (-8, -36), (-14, -24), (2, -10)], tension=0.5)
    cv.drawPath(tail, fill(ochre)); cv.drawPath(tail, stroke("line", lw))
    cv.drawPath(ellipse(-16, -42, 6, 5), fill(white))
    cv.restore()

    # --- far legs
    if lie:
        leg(36, -18, 80, 40, front=False)
    elif sit:
        leg(26, -48, 4, 46, front=False)
    elif d.mode == "float":
        for i, x in enumerate((-34, 30)):
            leg(x, body_y + 10, math.sin(t * 9 + i) * 35, 40, front=False)
    else:
        ph = d.phase * 2 * math.pi * spd
        leg(-34, body_y + 12, (math.sin(ph + math.pi) * 28) if trot else 3, 46, front=False)
        leg(32, body_y + 12, (math.sin(ph) * 28) if trot else -3, 46, front=False)

    # --- body
    cv.save(); cv.translate(0, body_y); cv.rotate(tilt)
    body = smooth_path([(-58, -6), (-40, -26), (0, -30), (40, -26), (56, -8), (48, 18), (0, 24), (-46, 18)], tension=0.5)
    cv.drawPath(body, K.lin((0, -30), (0, 24), [K.shade(ochre, 0.1), ochre, K.shade(ochre, -0.12)]))
    cv.save(); cv.clipPath(body, doAntiAlias=True)
    cv.drawPath(ellipse(28, 18, 40, 18), fill(white))        # chest/belly
    cv.drawPath(ellipse(-20, -22, 18, 9), fill(K.shade(ochre, -0.2), 0.5))  # scruffy patch
    cv.restore()
    cv.drawPath(body, stroke("line", lw))
    # scruff tufts
    for i in range(5):
        x = -40 + i * 18
        cv.drawPath(smooth_path([(x, -27), (x + 4, -36), (x + 8, -28)], close=False), stroke("line", 2.2))
    cv.restore()

    # --- near legs
    if lie:
        leg(44, -16, 85, 40)
        leg(-40, -12, 80, 34)
    elif sit:
        cv.drawPath(ellipse(-22, -26, 30, 22), fill(ochre)); cv.drawPath(ellipse(-22, -26, 30, 22), stroke("line", lw))
        cv.drawPath(ellipse(0, -6, 18, 7), fill(white)); cv.drawPath(ellipse(0, -6, 18, 7), stroke("line", lw))
        if d.mode == "beg":
            leg(34, -78, 150, 34)
        else:
            leg(38, -50, -2, 48)
    elif d.mode == "float":
        for i, x in enumerate((-40, 36)):
            leg(x, body_y + 12, math.sin(t * 9 + i + 1.5) * 40, 42)
    else:
        ph = d.phase * 2 * math.pi * spd
        leg(-40, body_y + 14, (math.sin(ph) * 30) if trot else -2, 46)
        leg(38, body_y + 14, (math.sin(ph + math.pi) * 30) if trot else 2, 46)

    # --- head
    hx, hy = (58, body_y - 30) if not sit else (44, -112)
    if lie:
        hx, hy = (62, -40)
    cv.save(); cv.translate(hx, hy)
    cv.rotate(d.head_tilt - d.look_up * 35)
    # neck
    cv.drawPath(limb(-24, 26, -6, 6, 34, 30), fill(ochre))
    # far ear stub (right ear lost)
    stub = poly([(-14, -30), (-6, -46), (2, -32)])
    cv.drawPath(stub, fill(K.shade(ochre, -0.2))); cv.drawPath(stub, stroke("line", 2.4))
    head = smooth_path([(-30, -10), (-20, -34), (6, -38), (26, -24), (48, -12), (56, 2), (44, 14), (10, 18),
                        (-20, 14)], tension=0.5)
    cv.drawPath(head, K.rad((-4, -24), 60, [K.shade(ochre, 0.15), ochre, K.shade(ochre, -0.1)]))
    cv.save(); cv.clipPath(head, doAntiAlias=True)
    cv.drawPath(ellipse(38, 6, 26, 16), fill(white))            # muzzle
    cv.drawPath(ellipse(4, -26, 7, 14), fill(white, 0.9))      # blaze
    cv.restore()
    cv.drawPath(head, stroke("line", lw))
    # mouth / tongue
    m = clamp(d.mouth)
    if m > 0.05 or d.tongue:
        jaw = smooth_path([(26, 10), (50, 8 + m * 4), (40, 16 + m * 14), (22, 16 + m * 6)], tension=0.5)
        cv.drawPath(jaw, fill("#5a1e22")); cv.drawPath(jaw, stroke("line", 2.4))
        if d.tongue or m > 0.3:
            tg = ellipse(36, 18 + m * 10 + (6 if d.tongue else 0), 8, 10 if d.tongue else 6)
            cv.drawPath(tg, fill("#ef7b8a")); cv.drawPath(tg, stroke("line", 2))
    else:
        cv.drawPath(smooth_path([(28, 12), (38, 16), (48, 10)], close=False), stroke("line", 2.4))
    # nose
    cv.drawPath(ellipse(55, 0, 8, 6), fill("#2a1a1c"))
    cv.drawCircle(53, -2, 2, fill("#ffffff", 0.7))
    # eye (big)
    if d.expr == "sneeze" or d.blink > 0.95:
        cv.drawPath(smooth_path([(10, -14), (18, -10), (26, -14)], close=False), stroke("line", 3))
    else:
        ey = -14
        cv.drawOval(skia.Rect.MakeLTRB(9, ey - 11, 29, ey + 9), fill("#fbf6ef"))
        look = d.look_up * -3
        cv.drawOval(skia.Rect.MakeLTRB(11, ey - 9 + look, 28, ey + 8 + look), K.rad((19, ey), 10, ["#7a4a24", "#3a2010"]))
        cv.drawCircle(16, ey - 4 + look, 3.4, fill("#ffffff"))
        cv.drawCircle(23, ey + 3 + look, 1.6, fill("#ffffff", 0.8))
        if d.expr in ("sad", "guilty"):
            cv.drawLine(8, ey - 14, 28, ey - 10, stroke("line", 3))
        if d.expr == "proud":
            cv.drawPath(smooth_path([(9, ey + 3), (19, ey - 2), (29, ey + 3)], close=False), stroke(ochre, 6))
    # brow tuft
    cv.drawPath(smooth_path([(8, -26 - (4 if d.expr == "alert" else 0)), (18, -30), (28, -25)], close=False),
                stroke(K.shade(ochre, -0.35), 3))
    # THE ear (left): flop..perk
    e = clamp(d.ear + (0.25 if d.expr == "alert" else 0))
    ear_ang = lerp(70, -10, e) + math.sin(t * 3) * 4
    cv.save(); cv.translate(-12, -30); cv.rotate(ear_ang)
    ear = smooth_path([(0, 0), (-8, -24), (-2, -46), (10, -40), (14, -18), (10, 0)], tension=0.5)
    cv.drawPath(ear, fill(K.shade(ochre, -0.12))); cv.drawPath(ear, stroke("line", lw))
    cv.drawPath(smooth_path([(2, -6), (0, -30), (6, -38)], close=False), stroke("#e8a87a", 4))
    cv.restore()
    cv.restore()  # head
    if d.alpha < 1:
        cv.restore()
    cv.restore()


# =============================================================== TOLA
@dataclass
class ScalePose:
    x: float = 960
    y: float = 700           # base bottom
    s: float = 1.0
    tilt: float = 0.0        # beam angle deg (+ = right pan down)
    t: float = 0.0
    eyes: str = "open"       # open | closed | half | wide | squint | happy
    mouth: str = "line"      # line | smile | o | frown | grin | wobble
    tarnish: float = 0.0     # 0 polished .. 1 dull
    shine: float = 0.0       # extra gleam 0..1 (blaze)
    bubble_on: str | None = None   # 'l'|'r': draw a glowing bubble sitting in that pan
    bubble_col: str = "gold"
    bubble_r: float = 26
    jitter: float = 0.0      # rattle amount (laugh/alarm)
    alpha: float = 1.0


def draw_scale(cv, s: ScalePose):
    cv.save()
    cv.translate(s.x, s.y)
    cv.scale(s.s, s.s)
    if s.alpha < 1:
        pt = skia.Paint(); pt.setAlphaf(s.alpha); cv.saveLayer(None, pt)
    brass = K.mix("brass", "#7d6a4a", s.tarnish * 0.8)
    bl = K.mix("brass_light", "#a39270", s.tarnish * 0.8)
    bd = K.mix("brass_dark", "#4a3d2a", s.tarnish * 0.6)
    jit = s.jitter * math.sin(s.t * 60)
    # base
    for i, (w, h) in enumerate([(150, 22), (110, 18), (70, 16)]):
        y = -sum(hh for _, hh in [(150, 22), (110, 18), (70, 16)][:i + 1])
        r = K.rrect(-w / 2, y, w, h, 8)
        cv.drawPath(r, K.lin((-w / 2, 0), (w / 2, 0), [bd, bl, brass, bd], [0, 0.3, 0.7, 1]))
        cv.drawPath(r, stroke("line", 3))
    # pillar
    pil = K.rrect(-11, -330, 22, 276, 10)
    cv.drawPath(pil, K.lin((-11, 0), (11, 0), [bd, bl, bd]))
    cv.drawPath(pil, stroke("line", 3))
    # beam
    cv.save(); cv.translate(0, -330); cv.rotate(s.tilt + jit * 2)
    beam = smooth_path([(-180, -6), (0, -14), (180, -6), (180, 4), (0, 8), (-180, 4)], tension=0.2)
    cv.drawPath(beam, K.lin((0, -14), (0, 8), [bl, brass, bd]))
    cv.drawPath(beam, stroke("line", 3))
    for ex in (-180, 180):
        cv.drawCircle(ex, 0, 9, fill(brass)); cv.drawCircle(ex, 0, 9, stroke("line", 2.6))
    ends = []
    for ex in (-180, 180):
        m = cv.getTotalMatrix()
        ends.append(ex)
    cv.restore()
    # pans hang vertically from beam ends
    a = math.radians(s.tilt + jit * 2)
    for side, ex in (("l", -180), ("r", 180)):
        px, py = ex * math.cos(a), -330 + ex * math.sin(a)
        sway = math.sin(s.t * 2.2 + (side == "l")) * 2 + jit * 3
        pan_y = py + 150
        for cx in (-46, 0, 46):
            cv.drawLine(px, py, px + cx + sway, pan_y, stroke(bd, 2.2))
        pan = smooth_path([(px - 64 + sway, pan_y), (px + 64 + sway, pan_y), (px + 44 + sway, pan_y + 26),
                           (px - 44 + sway, pan_y + 26)], tension=0.35)
        if s.bubble_on == side:
            br = s.bubble_r
            bx, by = px + sway, pan_y - br + 4
            cv.drawCircle(bx, by, br * 2.2, K.rad_a((bx, by), br * 2.2, [(s.bubble_col, 0.45), (s.bubble_col, 0)]))
            cv.drawCircle(bx, by, br, K.rad_a((bx - br * 0.3, by - br * 0.3), br * 1.2,
                                              [("#ffffff", 0.9), (s.bubble_col, 0.7), (s.bubble_col, 0.35)]))
            cv.drawCircle(bx, by, br, stroke("#ffffff", 2, 0.8))
        cv.drawPath(pan, K.lin((px - 64, 0), (px + 64, 0), [bd, bl, brass, bd], [0, 0.35, 0.65, 1]))
        cv.drawPath(pan, stroke("line", 3))
        cv.drawLine(px - 56 + sway, pan_y + 3, px + 56 + sway, pan_y + 3, stroke(bl, 2, 0.8))
    # face plate
    fy = -330
    cv.drawCircle(0, fy, 50, K.rad((-14, fy - 16), 60, [bl, brass, bd]))
    cv.drawCircle(0, fy, 50, stroke("line", 3))
    cv.drawCircle(0, fy, 42, stroke(bd, 1.6, 0.7))
    eng = stroke(bd, 3.4)
    for side in (-1, 1):
        ex, ey = side * 17, fy - 6
        if s.eyes == "closed":
            cv.drawPath(smooth_path([(ex - 9, ey), (ex, ey + 5), (ex + 9, ey)], close=False), eng)
        elif s.eyes == "happy":
            cv.drawPath(smooth_path([(ex - 9, ey + 3), (ex, ey - 5), (ex + 9, ey + 3)], close=False), eng)
        elif s.eyes == "half":
            cv.drawLine(ex - 9, ey - 1, ex + 9, ey - 1, eng)
            cv.drawPath(smooth_path([(ex - 8, ey - 1), (ex, ey + 6), (ex + 8, ey - 1)], close=False), eng)
        elif s.eyes == "squint":
            cv.drawLine(ex - 9, ey + side * 2, ex + 9, ey - side * 2, eng)
        else:
            rr = 10 if s.eyes == "wide" else 7.5
            cv.drawCircle(ex, ey, rr, eng)
            cv.drawCircle(ex, ey, 3.2, fill(bd))
    my = fy + 20
    if s.mouth == "smile":
        cv.drawPath(smooth_path([(-14, my - 3), (0, my + 6), (14, my - 3)], close=False), eng)
    elif s.mouth == "grin":
        cv.drawPath(smooth_path([(-18, my - 4), (0, my + 10), (18, my - 4)], close=True), fill(bd))
    elif s.mouth == "o":
        cv.drawCircle(0, my + 2, 6, eng)
    elif s.mouth == "frown":
        cv.drawPath(smooth_path([(-12, my + 5), (0, my - 2), (12, my + 5)], close=False), eng)
    elif s.mouth == "wobble":
        cv.drawPath(smooth_path([(-14, my), (-7, my - 4), (0, my + 2), (7, my - 4), (14, my)], close=False), eng)
    else:
        cv.drawLine(-11, my + 1, 11, my + 1, eng)
    # gleam
    g = 0.35 * (1 - s.tarnish) + s.shine
    if g > 0:
        cv.drawLine(-30, fy - 28, -18, fy - 38, stroke("#ffffff", 4, clamp(g)))
        cv.drawLine(-6, -300, -6, -120, stroke("#ffffff", 2.6, clamp(g * 0.7)))
    if s.alpha < 1:
        cv.restore()
    cv.restore()


# =============================================================== BUFFALO
def draw_buffalo(cv, x, y, s=1.0, t=0.0, pink=0.0, chew=True, flip=False, look=0.0):
    cv.save(); cv.translate(x, y); cv.scale(-s if flip else s, s)
    col = K.mix("#4a4652", "#ff8fc2", pink)
    dk = K.mix("#2e2b34", "#e0629f", pink)
    cv.drawOval(skia.Rect.MakeLTRB(-150, -10, 160, 10), fill("#000000", 0.22))
    for lx in (-100, -70, 80, 110):
        lg = limb(lx, -90, lx + 2, -6, 30, 24)
        cv.drawPath(lg, fill(dk if lx in (-70, 110) else col)); cv.drawPath(lg, stroke("line", 3))
        cv.drawPath(K.rrect(lx - 14, -14, 30, 14, 4), fill("#2a1a1c"))
    body = smooth_path([(-150, -110), (-120, -170), (40, -180), (130, -160), (150, -100), (120, -70), (-130, -70)], tension=0.5)
    cv.drawPath(body, K.lin((0, -180), (0, -70), [K.shade(col, 0.12), col, dk])); cv.drawPath(body, stroke("line", 3))
    tail = smooth_path([(-148, -140), (-170, -110), (-166, -70)], close=False)
    cv.drawPath(tail, stroke(dk, 6)); cv.drawPath(ellipse(-166, -66, 8, 12), fill("#2a1a1c"))
    # head
    cv.save(); cv.translate(150, -120); cv.rotate(18 + look * -20); cv.scale(1.55, 1.55)
    head = smooth_path([(-20, -30), (40, -30), (66, 10), (60, 40), (20, 44), (-10, 20)], tension=0.5)
    cv.drawPath(head, fill(col)); cv.drawPath(head, stroke("line", 3))
    for d in (-1, 1):
        horn = smooth_path([(0, -26), (-30, -56 + d * 4), (-60, -40), (-56, -30), (-28, -44), (8, -20)], tension=0.4)
        if d == 1:
            cv.drawPath(horn, fill("#d8cdb8")); cv.drawPath(horn, stroke("line", 2.6))
    cv.drawPath(ellipse(52, 30, 18, 13), fill(K.mix("#6e6470", "#ffc0dc", pink)))
    cv.drawCircle(58, 26, 3, fill("#2a1a1c"))
    jaw = math.sin(t * 6) * 3 if chew else 0
    cv.drawLine(36, 40 + jaw, 60, 40 + jaw, stroke("line", 2.4))
    cv.drawOval(skia.Rect.MakeLTRB(14, -8, 32, 10), fill("#fbf6ef"))
    cv.drawCircle(25, 2, 5, fill("#2a1a1c"))
    cv.drawLine(12, -10, 34, -6, stroke("line", 3))      # heavy, unimpressed lid
    cv.drawRect(skia.Rect.MakeLTRB(13, -10, 33, -2), fill(col))
    cv.drawLine(12, -2, 34, -2, stroke("line", 2.6))
    cv.drawPath(ellipse(-12, -8, 14, 8), fill(dk)); cv.drawPath(ellipse(-12, -8, 14, 8), stroke("line", 2.4))
    cv.restore()
    cv.restore()


# =============================================================== MONKEY (silhouette-ish, rim-lit)
def draw_monkey(cv, x, y, s=1.0, t=0.0, holding_specs=True, flee=0.0, flip=False):
    cv.save(); cv.translate(x, y); cv.scale(-s if flip else s, s)
    col, rim = "#2a2236", "#9fb3ff"
    cv.rotate(flee * -25)
    tail = smooth_path([(-20, -20), (-50, -10), (-60, -50), (-40, -80), (-30, -70)], close=False)
    cv.drawPath(tail, stroke(col, 7))
    body = ellipse(0, -40, 24, 32)
    cv.drawPath(body, fill(col)); cv.drawPath(body, stroke(rim, 2, 0.6))
    for lx in (-12, 12):
        cv.drawPath(limb(lx, -14, lx * 1.6, 0, 12, 10), fill(col))
    cv.drawCircle(4, -86, 20, fill(col)); cv.drawCircle(4, -86, 20, stroke(rim, 2, 0.6))
    cv.drawPath(ellipse(10, -82, 13, 11), fill("#7a6a7e"))
    for ex in (-14, 22):
        cv.drawCircle(ex, -90, 7, fill(col))
    eyes_y = -88
    if holding_specs:
        for dx in (0, 18):
            cv.drawOval(skia.Rect.MakeLTRB(dx - 8, eyes_y - 7, dx + 8, eyes_y + 7), stroke("#cfd6e3", 2.4))
        cv.drawLine(7, eyes_y, 11, eyes_y, stroke("#cfd6e3", 2))
    for dx in (0, 18):
        cv.drawCircle(dx, eyes_y, 3.2, fill("#ffffff"))
        cv.drawCircle(dx + 0.5, eyes_y, 1.6, fill("#000000"))
    cv.drawPath(smooth_path([(4, -76), (10, -72), (16, -76)], close=False),
                stroke("#ffffff", 2) if flee < 0.1 else stroke("#ffffff", 2))
    if flee > 0.1:
        cv.drawPath(ellipse(10, -74, 5, 6), fill("#1a0f14"))
    arm_a = -40 + math.sin(t * 3) * 6
    cv.drawPath(limb(14, -54, 26, -80 + arm_a * 0.1, 10, 9), fill(col))
    cv.restore()


# =============================================================== CYCLE RICKSHAW
def draw_rickshaw(cv, x, y, s=1.0, t=0.0, spin=0.0, flip=False, wheel_rot=0.0, canopy="#2f7d6a", tilt=0.0):
    cv.save(); cv.translate(x, y); cv.scale(-s if flip else s, s); cv.rotate(tilt)
    if spin:
        cv.rotate(spin)
    def wheel(cx, cy, r):
        cv.drawCircle(cx, cy, r, stroke("#1f1f26", 7))
        cv.drawCircle(cx, cy, r - 5, stroke("#5a5a66", 2))
        for i in range(10):
            a = wheel_rot + i * math.pi / 5
            cv.drawLine(cx, cy, cx + math.cos(a) * (r - 6), cy + math.sin(a) * (r - 6), stroke("#9aa1ad", 1.4))
        cv.drawCircle(cx, cy, 6, fill("#3a3a44"))
    # far rear wheel (dim), near rear wheel, front wheel
    cv.save(); cv.translate(14, -8); cv.scale(0.96, 0.96)
    wheel(-100, -52, 52)
    cv.restore()
    cv.drawRect(skia.Rect.MakeLTRB(-100, -60, -86, -44), fill("#2f3a4a"))
    wheel(-100, -52, 52); wheel(170, -44, 44)
    # frame: rear axle -> crank -> seat post -> head tube -> fork
    for a, b in [((-100, -52), (40, -50)), ((40, -50), (60, -150)), ((60, -150), (150, -150)),
                 ((40, -50), (150, -150)), ((150, -150), (170, -44)), ((150, -150), (146, -190))]:
        cv.drawLine(*a, *b, stroke("#2f3a4a", 7))
    cv.drawLine(126, -194, 172, -186, stroke("#2f3a4a", 6))
    cv.drawCircle(40, -50, 12, stroke("#2f3a4a", 4))
    cv.drawPath(K.rrect(44, -164, 36, 12, 5), fill("#3a2a24"))   # rider saddle
    # passenger seat
    seat = K.rrect(-170, -150, 150, 34, 8)  # passenger bench over rear axle
    cv.drawPath(seat, fill("#b8322f")); cv.drawPath(seat, stroke("line", 3))
    back = K.rrect(-176, -230, 30, 96, 8)
    cv.drawPath(back, fill("#a02a28")); cv.drawPath(back, stroke("line", 3))
    cv.drawPath(K.rrect(-170, -116, 150, 30, 6), fill("#2c6db0")); cv.drawPath(K.rrect(-170, -116, 150, 30, 6), stroke("line", 3))
    # folded canopy
    can = smooth_path([(-186, -150), (-190, -250), (-120, -290), (-60, -270), (-40, -150)], tension=0.4)
    cv.drawPath(can, fill(canopy)); cv.drawPath(can, stroke("line", 3))
    for i in range(3):
        cv.drawPath(smooth_path([(-180 + i * 8, -160), (-176 + i * 14, -250 + i * 6), (-100 + i * 10, -276 + i * 6)],
                                close=False), stroke(K.shade(canopy, -0.25), 2))
    # decoration
    for i in range(6):
        cv.drawCircle(-160 + i * 26, -112, 4, fill(["#ffd23f", "#ff6fa5", "#9bdc6b"][i % 3]))
    cv.restore()
