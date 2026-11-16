"""sc08 THE FIRST RAIN (target 90 s). The rain arrives all at once; the colours flood in;
Block C cheers from its balconies; the kids dance on the roof; Meghnath wakes to a raindrop,
opens his window and LAUGHS; at dawn he gives Tara the weather notebook, sits, and rests."""
from __future__ import annotations

import math

import skia

from .... import core as K, fx
from ....core import W, H, fill, stroke, lerp, clamp
from ....timeline import Shot, Line, Sfx
from ..rig import draw, draw_bhaap, draw_pigeon, draw_key
from ..sets import roof, block, ground, flats
from ..sets import weather_fx as WX
from ._util_d import graded, crossfade, hand_pos, head_pos, draw_lying_head, drop_on_face, notebook_spread, \
    sparkle_burst, fit_beds

TRUNK = roof.ANCHORS["trunk"]
VIVID = ((1.08, 1.09, 0.94), (0.025, 0.02, 0.0), 1.65)   # the colours flood in
RS = roof.roof_scale


# ------------------------------------------------------------------ dance moves
def dance(who, t, x, y, s, seed=0):
    """Big joyful rain-dance poses: returns (pose dict) incl. adjusted y."""
    tt = t + seed * 0.37
    hop = abs(math.sin(tt * 4.2)) * 26 * s
    if who == "tara":   # spinning, arms flung wide
        spin = (tt * 1.6) % 1.0
        flip = spin > 0.5
        return dict(x=x, y=y - hop * 0.6, s=s, t=t, flip=flip, turn=abs(math.sin(spin * math.pi)) * 0.8,
                    arms={"l": (95 + 10 * math.sin(tt * 6), 8), "r": (95 + 10 * math.cos(tt * 6), 8)},
                    expr="laugh", head_tilt=-8, legs="walk", phase=tt * 1.4)
    if who == "rehan":  # jumping, double fist pumps
        up = math.sin(tt * 4.2) > 0
        return dict(x=x, y=y - hop * 1.2, s=s, t=t, flip=False, turn=0.3,
                    arms={"l": (165 if up else 120, 30), "r": (120 if up else 165, 30)},
                    hand={"l": "fist", "r": "fist"}, expr="grin", legs="walk", phase=tt * 2.0, lean=-4)
    # ishaan: face to the sky, arms out, slow twirl, catching drops
    flip = math.sin(tt * 1.3) > 0
    return dict(x=x, y=y - hop * 0.4, s=s, t=t, flip=flip, turn=0.25,
                arms={"l": (70 + 20 * math.sin(tt * 2), 20), "r": (70 + 20 * math.cos(tt * 2), 20)},
                expr="laugh", head_tilt=-14, legs="walk", phase=tt * 0.8, look=(0, -1))


def greenery(cv, t, pts, grow=1.0):
    """Bright wet green leaves bursting out of the dried flowerpots."""
    for i, (x, y, s) in enumerate(pts):
        for j in range(6):
            ang = -90 + (j - 2.5) * 22 + 6 * math.sin(t * 2 + i + j)
            ln = (30 + 12 * (j % 3)) * s * grow
            a = math.radians(ang)
            tip = (x + math.cos(a) * ln, y + math.sin(a) * ln)
            leaf = K.smooth_path([(x, y), (x + math.cos(a - 0.35) * ln * 0.6, y + math.sin(a - 0.35) * ln * 0.6), tip,
                                  (x + math.cos(a + 0.35) * ln * 0.6, y + math.sin(a + 0.35) * ln * 0.6)], tension=0.5)
            cv.drawPath(leaf, fill(["#2fb24c", "#46c95c", "#25994a"][j % 3]))
            cv.drawPath(leaf, stroke("line", 2))
            cv.drawLine(x, y, tip[0], tip[1], stroke("#bff3b4", 1.2, 0.8))


POTS = [(70, 1040, 1.2), (1990, 1060, 1.3), (1395, 630, 0.7), (205, 640, 0.6)]


def splash(cv, t, x, y, s=1.0, a=1.0, seed=0):
    r = K.rng(seed)
    for i in range(7):
        ph = (t * 2.2 + r.random()) % 1.0
        ang = math.pi + r.uniform(0.2, 2.9)
        rr = 40 * s * ph
        cv.drawCircle(x + math.cos(ang) * rr, y + math.sin(ang) * rr * 1.4 - 40 * s * ph * (1 - ph),
                      3.5 * s * (1 - ph), fill("#d6ecff", a * (1 - ph)))


def bhaap_spin(cv, x, y, s, t, mood="excited", spark=1.0, mouth=0.6, rate=200):
    cv.save(); cv.translate(x, y); cv.rotate((t * rate) % 360)
    draw_bhaap(cv, 0, 0, s, t, mood=mood, spark=spark, mouth=mouth, squash=0.15 * math.sin(t * 9))
    cv.restore()


# ------------------------------------------------------------------ shots
def sh01(cv, c):
    """Block C wide: night into dawn; the rain arrives all at once and the colour floods in."""
    t = c.t
    k = K.smooth(c.seg(0.6, 4.5))
    cheer = K.smooth(c.seg(1.6, 5.0))
    z = lerp(1.0, 1.06, K.ease_in_out(c.u))
    with graded(cv, VIVID, amount=0.35 + 0.65 * k):
        with K.camera(cv, 960, 540, z):
            crossfade(cv, lambda q: block.draw_block(q, t, "monsoon_night", fans=0, rain=1.0, cheer=cheer * 0.6),
                      lambda q: block.draw_block(q, t, "monsoon", fans=0, rain=1.0, cheer=cheer), k)
    WX.rain(cv, t, 0.6 + 0.4 * k, wind=0.1, seed=11)
    if t < 0.9:
        WX.lightning_flash(cv, 0.55 * (1 - t / 0.9))


def sh02(cv, c):
    """Balconies close: hands out, faces up, dripping laundry; someone drums a steel plate."""
    t = c.t
    z = lerp(1.04, 1.1, c.u)
    with graded(cv, VIVID, 1.0):
        with K.camera(cv, lerp(900, 1010, c.u), 540, z):
            block.draw_block(cv, t, "monsoon", fans=0, rain=1.0, cheer=1.0, view="balconies")
            # the steel-plate drummer: a hand and a plate poking over a rail, bashing in rhythm
            bx, by = 1180, 620
            beat = abs(math.sin(t * math.pi * 2.0))
            cv.save(); cv.translate(bx, by - beat * 18); cv.rotate(-15 + beat * 10)
            cv.drawCircle(0, 0, 34, fill("#c9ccd2")); cv.drawCircle(0, 0, 34, stroke("line", 3))
            cv.drawCircle(0, 0, 22, stroke("#e9ebef", 2))
            cv.restore()
            cv.drawPath(K.limb(bx + 70, by + 40, bx + 30 - beat * 6, by + 6 - beat * 18, 18, 14), fill("#b97b52"))
            cv.drawPath(K.limb(bx + 70, by + 40, bx + 30 - beat * 6, by + 6 - beat * 18, 18, 14), stroke("line", 2.6))
            if beat > 0.92:
                fx.vibe_lines(cv, bx, by - 18, 40, t, color="#ffffff", a=0.8, n=2)
    WX.rain(cv, t, 1.0, wind=0.08, seed=12)


def sh03(cv, c):
    """The colony ground from the roof: tiny cricket kids sliding through the mud."""
    t = c.t
    with graded(cv, VIVID, 1.0):
        with K.camera(cv, 960, lerp(600, 560, c.u), lerp(1.45, 1.55, c.u)):
            ground.draw_ground(cv, t, "monsoon", players=False)
            px, py, pw, ph = ground.PITCH
            # four tiny kids taking run-ups and sliding on their bellies along the wet pitch
            for i in range(4):
                ph_ = ((t * 0.32) + i * 0.27) % 1.0
                sx = px - 220 + ph_ * 520
                sy = py + 140 + i * 95
                slide = ph_ > 0.45
                if slide:
                    cv.drawLine(sx - 70, sy + 4, sx, sy + 4, stroke("#5a4630", 7, 0.5))
                    cv.save(); cv.translate(sx, sy); cv.rotate(-80)
                    ground.draw_player(cv, 0, 0, 2.2, t, run=0.0, col=["#f4f4f0", "#ee6f57", "#ffd23f", "#9bdc6b"][i])
                    cv.restore()
                    splash(cv, t, sx + 20, sy, 0.8, 0.9, seed=i)
                else:
                    ground.draw_player(cv, sx, sy, 2.2, t, run=1.0, col=["#f4f4f0", "#ee6f57", "#ffd23f", "#9bdc6b"][i])
    WX.rain(cv, t, 1.0, wind=0.1, seed=13)


def roof_dance(cv, c, cam, people=(("ishaan", 470, 990), ("tara", 700, 925), ("rehan", 920, 975)),
               bhaap=(690, 330, 1.5), pigeon=(1560, 1020, 1.4), grade=1.0):
    t = c.t
    with graded(cv, VIVID, grade):
        roof.draw_roof(cv, t, "monsoon", "wide", rain=0.0, cam=cam)
        with K.camera(cv, *cam):
            x, y, s = TRUNK
            roof.draw_monsoon_trunk(cv, x + 120, y + 20, s, t, lid=1.0, keys=(1, 1, 1), glow=0.35, weather="monsoon")
            greenery(cv, t, POTS, grow=K.ease_out(c.seg(0, 2.5)))
            for i, (who, px, py) in enumerate(people):
                p = dance(who, t, px, py, RS(py), seed=i)
                draw(cv, who, **p)
                splash(cv, t, px, py + 6, RS(py), 0.9, seed=i + 3)
            if pigeon:
                gx, gy, gs = pigeon
                cv.drawOval(skia.Rect.MakeLTRB(gx - 80 * gs, gy - 14 * gs, gx + 80 * gs, gy + 14 * gs), fill("#7d9bb8", 0.7))
                draw_pigeon(cv, gx, gy, gs, t, flip=True, mode="bath")
                splash(cv, t * 1.6, gx, gy - 10, gs, 1.0, seed=9)
    with K.camera(cv, *cam):
        if bhaap:
            bx, by, bs = bhaap
            bhaap_spin(cv, bx + 120 * math.sin(t * 0.9), by + 30 * math.sin(t * 1.7), bs, t)
            sparkle_burst(cv, t, bx + 120 * math.sin(t * 0.9), by, a=0.9, seed=4, spread=120)
    WX.rain(cv, t, 1.0, wind=0.06, seed=14)


def sh04(cv, c):
    """Roof wide: the three of them dance in the rain; Bhaap spins above; Captain bathes."""
    roof_dance(cv, c, (960, lerp(560, 600, c.u), lerp(1.0, 1.08, c.u)))


def sh05(cv, c):
    """Closer on the dancers."""
    roof_dance(cv, c, (lerp(640, 720, c.u), 740, 1.6), pigeon=None, bhaap=(400, 455, 1.4))


def sh06(cv, c):
    """Bhaap close, spinning and sparking for joy; Captain splashes in a puddle below."""
    t = c.t
    cam = (1300, 860, 2.3)
    with graded(cv, VIVID, 1.0):
        roof.draw_roof(cv, t, "monsoon", "wide", rain=0.0, cam=cam)
        with K.camera(cv, *cam):
            gx, gy = 1380, 1010
            cv.drawOval(skia.Rect.MakeLTRB(gx - 120, gy - 18, gx + 120, gy + 18), fill("#7d9bb8", 0.75))
            mode = "bath" if (t % 2.4) < 1.6 else "flap"
            draw_pigeon(cv, gx, gy, 1.6, t, flip=True, mode=mode)
            splash(cv, t * 1.8, gx, gy - 12, 1.6, 1.0, seed=21)
    with K.camera(cv, *cam):
        bx, by = 1240 + 30 * math.sin(t * 1.3), 760 + 20 * math.sin(t * 2.1)
        bhaap_spin(cv, bx, by, 1.5, t, rate=260)
        sparkle_burst(cv, t, bx, by, a=1.0, seed=6, spread=90)
    WX.rain(cv, t, 1.0, wind=0.05, seed=15)


def _megh_room(cv, t, cam, curtain, k_dawn=0.0):
    flats.draw_meghnath_flat(cv, t, "monsoon_night", curtain=curtain, rain_glass=1.0, cam=cam)


def _blanket(cv, x, y, s, t):
    """Meghnath asleep under a blanket on the bed; head end at left."""
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    b = K.smooth_path([(-200, -30), (-120, -56), (40, -60), (220, -44), (250, -6), (-210, -4)], tension=0.4)
    cv.drawPath(b, fill("#8a6a9c")); cv.drawPath(b, stroke("line", 3))
    for i in range(4):
        cv.drawLine(-100 + i * 70, -50, -80 + i * 70, -8, stroke("#6e5180", 2))
    cv.drawPath(K.rrect(-250, -60, 70, 46, 18), fill("#e9e3f2")); cv.drawPath(K.rrect(-250, -60, 70, 46, 18), stroke("line", 2.6))
    cv.restore()


def sh07(cv, c):
    """His bedroom: rain on the window, the curtain blows in. He's asleep."""
    t = c.t
    cam = (900, 560, lerp(1.0, 1.08, c.u))
    curtain = 0.35 + 0.45 * (0.5 + 0.5 * math.sin(t * 1.4))
    _megh_room(cv, t, cam, curtain)
    bx, by, bs = flats.BED
    with K.camera(cv, *cam):
        with K.lit(cv, "monsoon_night", amount=0.5):
            _blanket(cv, bx, by, bs * 0.95, t)
            draw_lying_head(cv, "meghnath", bx - 205 * bs * 0.95, by - 70 * bs * 0.95, bs * 0.95, t, rot=-55,
                            expr="sleepy", blink=1.0)


def sh08(cv, c):
    """Close on his face on the pillow: a single drop finds him. His eyes open."""
    t = c.t
    bx, by, bs = flats.BED
    hx, hy = bx - 205 * bs * 0.95, by - 70 * bs * 0.95
    cam = (hx + 60, hy - 10, lerp(2.2, 2.35, c.u))
    _megh_room(cv, t, cam, 0.6)
    T_DROP = 1.6
    woke = t > T_DROP + 0.75
    with K.camera(cv, *cam):
        with K.lit(cv, "monsoon_night", amount=0.3):
            _blanket(cv, bx, by, bs * 0.95, t)
            draw_lying_head(cv, "meghnath", hx, hy, bs * 0.95, t, rot=-18,
                            expr="surprised" if woke else "sleepy", blink=0.0 if woke else 1.0,
                            look=(0.0, 0.0), brow=0.6 if woke else 0.0)
        drop_on_face(cv, hx + 8, hy + 10, t, T_DROP, dur=0.7, s=1.2)


def sh09(cv, c):
    """He goes to the window and throws it wide."""
    t = c.t
    cam = (700, 560, 1.15)
    open_ = K.ease_out_back(c.seg(1.6, 2.3))
    _megh_room(cv, t, cam, 0.5 + 0.5 * open_)
    sx, sy, ss = flats.STAND_WINDOW
    with K.camera(cv, *cam):
        with K.lit(cv, "monsoon_night", amount=0.5):
            draw(cv, "meghnath", x=sx, y=sy, s=ss, t=t, flip=True, turn=0.7, expr="surprised",
                 arms={"l": (lerp(10, 150, open_), 30)}, extra={"sling": True}, lean=lerp(0, 8, open_))
        if open_ > 0.2:
            wx, wy, ww, wh = flats.WINDOW
            WX.rain(cv, t, 0.9 * open_, wind=-0.2, rect=(wx, wy, wx + ww, wy + wh), seed=31, splash=False)


def sh10(cv, c):
    """Outside: he leans out into the downpour; the rain flattens his eyebrows... and he LAUGHS."""
    t = c.t
    T_LAUGH = 2.4
    wet = K.smooth(c.seg(0.4, 2.2))
    laugh = t > T_LAUGH
    shake = math.sin(t * 22) * 2.5 if laugh else 0.0
    z = lerp(2.2, 2.6, K.ease_in_out(c.seg(0, c.dur)))
    x, y, s = block.TOP_ANCHOR
    with graded(cv, VIVID, 1.0):
        with K.camera(cv, x + 10, y - 420, z):
            block.draw_block(cv, t, "monsoon", rain=1.0, view="top")
            draw(cv, "meghnath", x=x, y=y + shake * 0.3, s=s, t=t, turn=0.2,
                 expr="laugh" if laugh else "surprised", mouth=(0.6 + 0.4 * abs(math.sin(t * 9))) if laugh else 0.0,
                 head_tilt=-16 if laugh else -10, lean=-3 + shake * 0.2,
                 arms={"l": (lerp(20, 150, K.smooth(c.seg(T_LAUGH, T_LAUGH + 0.8))), lerp(25, -10, K.smooth(c.seg(T_LAUGH, T_LAUGH + 0.8))))},
                 hand={"l": "open"}, extra={"sling": True, "wet": wet})
            block.draw_top_rail(cv, t, "monsoon", coda=False, rain=1.0)
            if laugh:
                hx, hy = head_pos("meghnath", x, y, s, turn=0.2)
                sparkle_burst(cv, t, hx, hy - 40, a=0.8, seed=8, spread=160, color="#e7f6ff")
    WX.rain(cv, t, 1.0, wind=0.04, seed=16)


def _dawn_roof(cv, t, cam, people, megh=None, bhaap_pos=None, extra_draw=None, rest=0.0, pre_draw=None):
    with graded(cv, VIVID, 0.55):
        roof.draw_roof(cv, t, "dawn_wet", "wide", rain=0.55, cam=cam)
        with K.camera(cv, *cam):
            x, y, s = TRUNK
            roof.draw_monsoon_trunk(cv, x + 140, y + 20, s, t, lid=1.0, keys=(1, 1, 0.0), glow=0.25, weather="dawn_wet")
            greenery(cv, t, POTS, grow=1.0)
            if pre_draw:
                pre_draw(cv)
            items = list(people) + ([megh] if megh else [])
            for who, pose in sorted(items, key=lambda q: q[1]["y"]):
                draw(cv, who, **pose)
            if extra_draw:
                extra_draw(cv)
    if bhaap_pos:
        with K.camera(cv, *cam):
            bx, by, bs, mood = bhaap_pos
            draw_bhaap(cv, bx, by, bs, t, mood=mood, spark=0.2, mouth=0.3 if mood == "happy" else 0.0)
    WX.rain(cv, t, 0.55, wind=0.04, seed=17)


def sh11(cv, c):
    """Dawn. He comes up out of the stair hut. The kids stop dancing mid-move."""
    t = c.t
    cam = (900, 600, 1.05)
    T_STOP = 1.4
    sx, sy, ss = roof.ANCHORS["stair_door"]
    w = K.ease_in_out(c.seg(0.4, 5.6))
    mx, my = lerp(sx + 20, 640, w), lerp(sy + 10, 900, w)
    frozen = t > T_STOP
    kids = []
    for i, (who, px, py) in enumerate((("ishaan", 1060, 975), ("tara", 1250, 905), ("rehan", 1420, 960))):
        if frozen:
            pose = dict(x=px, y=py, s=RS(py), t=t, flip=True, turn=0.4, expr="surprised",
                        arms={"l": (150, 20), "r": (150, 20)} if who == "rehan" else {"l": (30, 40), "r": (30, 40)},
                        head_tilt=6)
        else:
            pose = dance(who, t, px, py, RS(py), seed=i)
        kids.append((who, pose))
    megh = ("meghnath", dict(x=mx, y=my, s=RS(my), t=t, legs="walk" if w < 0.99 else "stand", phase=t * 0.7,
                             turn=0.5, expr="neutral", extra={"sling": True, "wet": 1.0}))
    _dawn_roof(cv, t, cam, kids, megh, bhaap_pos=(1240, 560 if not frozen else 600, 1.2, "shy" if frozen else "excited"))


def sh12(cv, c):
    """Rehan, sheepish, holds out the third key."""
    t = c.t
    cam = (1200, 700, 1.75)
    out = K.ease_out_back(c.seg(0.5, 1.4))
    px, py = 1320, 960
    kids = [("rehan", dict(x=px, y=py, s=RS(py), t=t, flip=True, turn=0.45, expr="shy", head_tilt=8,
                           arms={"r": (lerp(10, 80, out), lerp(20, 10, out)), "l": (20, 60)}, hand={"r": "open"},
                           look=(-0.4, 0.4))),
            ("tara", dict(x=1060, y=905, s=RS(905), t=t, flip=False, turn=0.4, expr="worried",
                          arms={"l": (25, 70), "r": (25, 70)}))]
    _dawn_roof(cv, t, cam, kids)
    with K.camera(cv, *cam):
        hx, hy = hand_pos("rehan", px, py, RS(py), "r", flip=True, arms={"r": (lerp(10, 80, out), lerp(20, 10, out))})
        draw_key(cv, hx - 10, hy - 6, 0.9, rot=-30, glow=0.3 * out, t=t)


def sh13(cv, c):
    """He looks: at the open trunk... at the three of them... at the little cloud."""
    t = c.t
    # three beats of an eyeline: trunk (left), kids (right), cloud (up)
    look = (-1, 0.3) if t < 2.0 else (1, 0.2) if t < 4.0 else (0.4, -1)
    cam = (640, 560, 2.2)
    megh = ("meghnath", dict(x=640, y=900, s=RS(900), t=t, turn=0.35, expr="neutral", look=look,
                             head_tilt=-6 if t > 4.0 else 0, extra={"sling": True, "wet": 1.0,
                                                                   "brow_lift": 0.5 if t > 4.0 else 0.0}))
    _dawn_roof(cv, t, cam, [], megh, bhaap_pos=(760, 470, 1.0, "shy") if t > 4.0 else None)


def sh14(cv, c):
    """He draws the battered notebook from his cardigan pocket and holds it out to Tara: 'It needs three.'"""
    t = c.t
    cam = (760, 640, 1.65)
    reach = K.ease_in_out(c.seg(0.6, 2.2))      # hand to pocket and back up with the notebook
    out = K.ease_out_back(c.seg(2.3, 3.3), 1.1)  # arm extends toward Tara
    mx, my = 545, 910
    # flip=True puts his free LEFT arm on the screen-right side, toward Tara
    sh = lerp(lerp(15, 40, reach), 78, out)
    el = lerp(lerp(20, 120, math.sin(math.pi * reach)), 8, out)
    arms_m = {"l": (sh, el)}
    megh = ("meghnath", dict(x=mx, y=my, s=RS(my), t=t, flip=True, turn=0.1, look=(-0.7, 0.2),
                             expr="neutral", mouth=c.mouth("meghnath"), arms=arms_m, hand={"l": "open"},
                             extra={"sling": True, "wet": 1.0, "brow_lift": 0.25}))
    kids = [("tara", dict(x=930, y=915, s=RS(915), t=t, flip=True, turn=0.45,
                          expr="awe" if out > 0.5 else "surprised", arms={"l": (20, 40), "r": (20, 40)}))]

    def nb(q):
        if reach > 0.35:
            hx, hy = hand_pos("meghnath", mx, my, RS(my), "l", flip=True, arms=arms_m)
            from ..rig import draw_notebook
            draw_notebook(q, hx + 4, hy - 16, 1.25)
            if out > 0.95:
                sparkle_burst(q, t, hx, hy - 20, a=0.5, seed=19, spread=50, color="#fff1c2")
    _dawn_roof(cv, t, cam, kids, megh, extra_draw=nb)


def sh15(cv, c):
    """Tara takes it with both hands."""
    t = c.t
    cam = (1000, 700, 2.4)
    take = K.ease_out(c.seg(0.5, 1.6))
    arms_t = {"l": (lerp(20, 70, take), 70), "r": (lerp(20, 70, take), 70)}
    kids = [("tara", dict(x=1040, y=915, s=RS(915), t=t, flip=True, turn=0.35, expr="awe", arms=arms_t,
                          look=(0, 0.5)))]

    def nb(q):
        lx, ly = hand_pos("tara", 1040, 915, RS(915), "l", flip=True, arms=arms_t)
        rx, ry = hand_pos("tara", 1040, 915, RS(915), "r", flip=True, arms=arms_t)
        from ..rig import draw_notebook
        draw_notebook(q, (lx + rx) / 2, (ly + ry) / 2 - 18, 1.35)
        if take > 0.9:
            sparkle_burst(q, t, (lx + rx) / 2, (ly + ry) / 2 - 30, a=0.7, seed=12, spread=60, color="#fff1c2")
    _dawn_roof(cv, t, cam, kids, extra_draw=nb)


def sh16(cv, c):
    """He sits on his upturned bucket in the rain, folds his good hand over the sling, tips his face
    up, and, for the first time, rests."""
    t = c.t
    bx, by, bs = roof.ANCHORS["bucket_seat"]
    pull = K.ease_in_out(c.seg(4.5, c.dur))
    cam = (lerp(bx + 10, bx + 330, pull), lerp(by - 230, 588, pull), lerp(2.1, 1.12, pull))
    tilt = -K.smooth(c.seg(1.6, 4.0)) * 20
    closed = t > 3.4
    fold = K.smooth(c.seg(0.6, 2.0))
    pose = dict(x=bx, y=by, s=bs * 0.95, t=t, legs="sit", turn=0.25, head_tilt=tilt,
                expr="happy" if closed else "neutral",
                arms={"l": (lerp(12, 28, fold), lerp(10, 112, fold))}, hand={"l": "open"},
                extra={"sling": True, "wet": 1.0, "brow_lift": 0.35}, breathe=0.6)
    if closed:
        pose["blink"] = 1.0
    megh = ("meghnath", pose)
    kids = [("ishaan", dict(x=1225, y=840, s=RS(840) * 0.9, t=t, flip=True, turn=0.4, expr="happy",
                            arms={"l": (15, 20), "r": (15, 20)})),
            ("tara", dict(x=1370, y=820, s=RS(820) * 0.9, t=t, flip=True, turn=0.4, expr="happy", hold="notebook",
                          arms={"r": (40, 90)})),
            ("rehan", dict(x=1515, y=832, s=RS(832) * 0.9, t=t, flip=True, turn=0.4, expr="happy"))]
    hx, hy = head_pos("meghnath", bx, by, bs * 0.95, turn=0.25, legs="sit")

    def bucket(q):
        # his upturned blue bucket, rim-down on the wet floor, seat at (bx, by)
        sc = bs * 0.95
        top, bot = by + 2 * sc, by + 96 * sc
        b = K.poly([(bx - 46 * sc, top), (bx + 46 * sc, top), (bx + 58 * sc, bot), (bx - 58 * sc, bot)])
        q.drawPath(b, fill("#2f7fd0")); q.drawPath(b, stroke("line", 3))
        q.drawLine(bx - 52 * sc, top + 16 * sc, bx + 52 * sc, top + 16 * sc, stroke("#1f5c9e", 3))
        q.drawRect(skia.Rect.MakeLTRB(bx - 60 * sc, bot - 10 * sc, bx + 60 * sc, bot), fill("#2a6fb6"))
        q.drawOval(skia.Rect.MakeLTRB(bx - 30 * sc, top + 30 * sc, bx - 14 * sc, top + 70 * sc), fill("#ffffff", 0.35))
    _dawn_roof(cv, t, cam, kids, megh, pre_draw=bucket,
               bhaap_pos=(lerp(1100, hx + 110, K.smooth(c.seg(2.0, 6.0))), lerp(560, hy - 120, K.smooth(c.seg(2.0, 6.0))),
                          1.0, "happy"))


SHOTS = fit_beds([
    Shot("S08_SH01", sh01, duration=7.0, music="first_rain_dance", transition="cut",
         sfx=[Sfx("rain_roar", 0, -6, dur=7.0), Sfx("thunder", 0.1, -4, params={"dist": 0.2}),
              Sfx("cheers_distant", 2.4, -8)]),
    Shot("S08_SH02", sh02, duration=5.5,
         sfx=[Sfx("rain_roar", 0, -9, dur=5.5), Sfx("steel_plate_drum", 0.0, -6, dur=5.5, params={"bpm": 120}),
              Sfx("cheers_distant", 0.8, -10)]),
    Shot("S08_SH03", sh03, duration=5.5,
         sfx=[Sfx("rain_roar", 0, -10, dur=5.5), Sfx("mud_slide", 1.2, -6), Sfx("mud_slide", 3.4, -7),
              Sfx("crowd_howl_distant", 1.6, -14)]),
    Shot("S08_SH04", sh04, duration=8.0,
         sfx=[Sfx("rain_roar", 0, -10, dur=8.0), Sfx("rain_puddles", 0, -12, dur=8.0),
              Sfx("kids_laugh", 0.8, -10), Sfx("bhaap_giggle", 3.0, -8), Sfx("spark_tzik", 3.6, -10)]),
    Shot("S08_SH05", sh05, duration=6.0,
         sfx=[Sfx("rain_roar", 0, -11, dur=6.0), Sfx("kids_laugh", 0.6, -8), Sfx("rain_puddles", 0, -12, dur=6.0)]),
    Shot("S08_SH06", sh06, duration=4.5,
         sfx=[Sfx("rain_roar", 0, -12, dur=4.5), Sfx("bhaap_giggle", 0.4, -6), Sfx("spark_tzik", 1.2, -8),
              Sfx("pigeon_flap", 1.7, -10), Sfx("pigeon_coo", 3.2, -12)]),
    Shot("S08_SH07", sh07, duration=5.0, music="keeper_laughs", transition="dissolve", trans_dur=0.8,
         sfx=[Sfx("raindrops_tin", 0, -14, dur=5.0, params={"density": 0.7}), Sfx("curtain_flutter", 1.0, -12)]),
    Shot("S08_SH08", sh08, duration=4.6,
         sfx=[Sfx("raindrops_tin", 0, -18, dur=4.6, params={"density": 0.5}), Sfx("pop", 2.3, -6)]),
    Shot("S08_SH09", sh09, duration=4.0,
         sfx=[Sfx("raindrops_tin", 0, -16, dur=4.0, params={"density": 0.7}), Sfx("window_open", 1.6, -6),
              Sfx("rain_roar", 1.8, -12, dur=2.2)]),
    Shot("S08_SH10", sh10, duration=8.5,
         sfx=[Sfx("rain_roar", 0, -9, dur=8.5), Sfx("creaky_laugh", 2.4, -2), Sfx("thunder", 6.0, -14, params={"dist": 0.8})]),
    Shot("S08_SH11", sh11, duration=6.5, music="notebook_passed", transition="fade_white", trans_dur=1.0,
         sfx=[Sfx("raindrops_tin", 0, -14, dur=6.5, params={"density": 0.5}), Sfx("door_creak", 0.3, -10),
              Sfx("footsteps_slipper", 1.0, -14), Sfx("kids_laugh", 0.0, -12)]),
    Shot("S08_SH12", sh12, duration=4.0,
         sfx=[Sfx("raindrops_tin", 0, -16, dur=4.0, params={"density": 0.4})]),
    Shot("S08_SH13", sh13, duration=6.0,
         sfx=[Sfx("raindrops_tin", 0, -16, dur=6.0, params={"density": 0.4}), Sfx("bhaap_coo", 4.3, -10)]),
    Shot("S08_SH14", sh14, duration=None, tail=1.6,
         lines=[Line("meghnath", "It needs three.", at=3.6)],
         sfx=[Sfx("raindrops_tin", 0, -16, dur=6.6, params={"density": 0.4})]),
    Shot("S08_SH15", sh15, duration=4.5,
         sfx=[Sfx("raindrops_tin", 0, -16, dur=4.5, params={"density": 0.4}), Sfx("sparkle", 1.4, -12)]),
    Shot("S08_SH16", sh16, duration=8.5,
         sfx=[Sfx("raindrops_tin", 0, -14, dur=8.5, params={"density": 0.35}), Sfx("bhaap_coo", 5.0, -14)]),
])
