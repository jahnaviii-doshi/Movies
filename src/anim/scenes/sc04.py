"""Scene 4: KABIR COMES ALONG (06:00-08:00).

Morning: 'You were floating. I saw you.' -> Meher's gap-toothed grin. Next midnight: Kabir trails
them down the gali, 'If this is a joke—' is cut off by the glow, the shop unfolds, his folded arms
un-fold. In the shop: swagger, the fake kindness (a crayon-scribble bubble that weighs nothing),
'It's broken.', the BOINK, Meher's snort, Amma's gentle verdict, red ears, the storm-out,
'hungry for something', and the first dust ring on a shelf.
"""
from __future__ import annotations

import math

from .. import core as K, fx
from ..core import lerp, clamp
from ..rig import chars, animals as A
from ..sets import rooftop, wall, shop, gali
from ..timeline import Shot, Line, Sfx
from ._util_b import bed, reach, head_world, ear_flush, dizzy_stars, scribble_scene, cam, finalize

RA = rooftop.ANCHORS
SA = shop.ANCHORS


def _seat(key):
    a = RA[key]
    x, y = a["surface"]
    return x, y + 10, a["s"] * 1.5


# ---------------------------------------------------------------- rooftop morning
def _crumbs(cv, t, x, y, s):
    """Golden laddoo crumbs sparkling on Meher's kurta (x, y = her seat point)."""
    cy = y - 58 * s
    fx.sparkles(cv, t, x + 4 * s, cy, spread=26 * s, n=8, color="gold", size=4.5 * s, seed=44)
    r = K.rng(5)
    for i in range(7):
        px, py = x + 4 * s + r.uniform(-22, 22) * s, cy + r.uniform(-16, 22) * s
        cv.drawCircle(px, py, 2.6 * s, K.fill("#ffcf5a"))
        cv.drawCircle(px, py, 2.6 * s, K.stroke("#b8781a", 1.0))


def _morning_wide(cv, c):
    t = c.t
    z = lerp(1.0, 1.05, K.ease_in_out(c.u))
    with cam(cv, 960, 600, z, t=t):
        rooftop.draw_rooftop(cv, t, "morning", lantern=0.0)
        mx, my, ms = _seat("charpai_meher")
        kx, ky, ks = _seat("charpai_kabir")
        up = K.ease_out_back(c.seg(2.7, 3.15))
        if up <= 0.01:
            a = RA["charpai_kabir"]
            rooftop.draw_sleeper(cv, a["surface"][0], a["surface"][1], a["s"] * 1.5, t, "kabir", face_cover=True)
        with K.lit(cv, "day", amount=0.6):
            chars.draw(cv, "meher", x=mx, y=my, s=ms, legs="sit", t=t, expr="happy", look=(0.3, -0.8),
                       head_tilt=6 + 2 * math.sin(t * 1.3), extra={"swing": 1.0}, arms={"l": (10, 60), "r": (10, 60)})
            if up > 0.01:
                chars.draw(cv, "kabir", x=kx, y=ky + (1 - up) * 90, s=ks, legs="sit", t=t, flip=True,
                           expr="sleepy" if t < 3.8 else "determined", blink=0.55 if t > 3.8 else 0.9,
                           arms={"l": (150, 30), "r": (150, 30)} if t < 4.0 else {}, head_tilt=-6)
        _crumbs(cv, t, mx, my, ms)


def _kabir_saw(cv, c):
    t = c.t
    kx, ky, ks = _seat("charpai_kabir")
    with cam(cv, kx - 40, ky - 230, lerp(2.2, 2.32, c.u), t=t):
        rooftop.draw_rooftop(cv, t, "morning", lantern=0.0)
        with K.lit(cv, "day", amount=0.6):
            point = c.t > 0.5
            chars.draw(cv, "kabir", x=kx, y=ky, s=ks, legs="sit", t=t, flip=True, expr="determined",
                       blink=0.45, mouth=c.mouth("kabir"), lean=-3 if t > 1.6 else 0,
                       arms={"r": (78, 8)} if point else {}, hand={"r": "point"}, head_tilt=-5,
                       look=(0.6, 0.1))


def _meher_grin(cv, c):
    t = c.t
    mx, my, ms = _seat("charpai_meher")
    with cam(cv, mx + 10, my - 230, lerp(2.3, 2.5, c.u), t=t):
        rooftop.draw_rooftop(cv, t, "morning", lantern=0.0)
        with K.lit(cv, "day", amount=0.6):
            grin = t > 3.1
            dart = 0.7 * math.copysign(1, math.sin(t * 2.4)) if 0.6 < t < 2.8 else 0.0
            chars.draw(cv, "meher", x=mx, y=my, s=ms, legs="sit", t=t, expr="grin" if grin else "neutral",
                       look=(dart, 0) if not grin else (0.5, 0), head_tilt=4 if grin else 0,
                       turn=0.5 if grin else 0.35, arms={"l": (10, 60), "r": (10, 60)})
        _crumbs(cv, t, mx, my, ms)
        if grin:
            hx, hy = head_world("meher", mx, my, ms, turn=0.5, sit=True)
            fx.star4(cv, hx + 4 * ms, hy + 30 * ms, 16 * K.ease_out_back(c.seg(3.15, 3.5)), "#ffffff",
                     clamp(1 - c.seg(3.6, 4.4)))


def _kabir_worse(cv, c):
    t = c.t
    kx, ky, ks = _seat("charpai_kabir")
    with cam(cv, kx - 40, ky - 230, 2.32, t=t):
        rooftop.draw_rooftop(cv, t, "morning", lantern=0.0)
        with K.lit(cv, "day", amount=0.6):
            chars.draw(cv, "kabir", x=kx, y=ky, s=ks, legs="sit", t=t, flip=True, expr="worried",
                       lean=-6 * K.ease_out(c.seg(0.2, 0.6)), look=(0.5, 0), blink=0.3,
                       arms={"l": (20, 90), "r": (20, 90)})


# ---------------------------------------------------------------- the gali, next midnight
def _trail(cv, c):
    """Lateral tracking: Chutney and Meher lead, Kabir trails, arms folded, yawning."""
    t = c.t
    scroll = t * 150
    gali.draw_gali_side(cv, t, "night", scroll=scroll)
    gy = gali.GROUND_Y_SIDE
    with K.lit(cv, "moon", amount=0.85):
        A.draw_dog(cv, A.DogPose(x=1500, y=gy + 4, s=1.25, t=t, mode="trot", phase=t * 1.3, expr="happy", ear=0.9))
        chars.draw(cv, "meher", x=1150, y=gy, s=1.9, t=t, legs="walk", phase=t * 1.25, expr="happy",
                   turn=0.6, look=(0.6, 0))
        yawn = clamp(c.seg(2.6, 3.0) - c.seg(3.9, 4.3))
        chars.draw(cv, "kabir", x=560, y=gy, s=1.9, t=t, legs="walk", phase=t * 1.1 + 0.3,
                   expr="sleepy" if yawn < 0.5 else "awe", mouth=0.8 * yawn, turn=0.6,
                   arms={"l": (18, 128), "r": (18, 128)}, head_tilt=-4 * yawn, look=(0.5, 0))


FOLD = {"l": (18, 128), "r": (18, 128)}       # arms folded across the chest


def _arms_unfold(k):
    return {"l": (lerp(18, 6, k), lerp(128, 8, k)), "r": (lerp(18, 6, k), lerp(128, 8, k))}


def _wall_trio(cv, t, unfold, kabir_expr, kabir_arms, glow, mouth=0.0, kturn=0.35, meher_expr="awe"):
    wall.draw_wall(cv, t, "night", glow=glow, unfold=unfold)
    with K.lit(cv, "moon", amount=lerp(0.8, 0.25, unfold)):
        A.draw_dog(cv, A.DogPose(x=520, y=wall.FLOOR_Y + 8, s=wall.DOG_S, t=t, mode="sit", expr="alert",
                                 look_up=0.25 + 0.4 * unfold, ear=0.7 + 0.3 * unfold, wag=1.0 + unfold))
        chars.draw(cv, "meher", x=640, y=wall.FLOOR_Y, s=wall.CHAR_S, t=t, expr=meher_expr, turn=0.7,
                   look=(0.6, -0.4))
        chars.draw(cv, "kabir", x=1300, y=wall.FLOOR_Y, s=wall.CHAR_S, t=t, flip=True, expr=kabir_expr,
                   arms=kabir_arms, mouth=mouth, turn=kturn, look=(0.5, -0.2) if unfold > 0 else (0, 0))


def _joke(cv, c):
    t = c.t
    glow = K.ease_in_out(c.seg(2.4, 5.6))
    with cam(cv, 960, 640, lerp(1.0, 1.06, c.u), t=t):
        _wall_trio(cv, t, 0.0, "smug" if t < 2.4 else "surprised", FOLD, glow * 0.85, mouth=c.mouth("kabir"),
                   kturn=0.1 if t < 2.4 else 0.8, meher_expr="neutral" if t < 2.4 else "awe")


def _unfold(cv, c):
    t = c.t
    u = K.smooth(c.seg(0.2, 5.9))
    k = K.ease_in_out(c.seg(3.6, 6.4))       # Kabir's arms slowly un-fold as the shop does
    with cam(cv, 960, 560, lerp(1.06, 1.0, K.ease_out(c.u)), t=t):
        _wall_trio(cv, t, u, "awe", _arms_unfold(k), 1.0, mouth=0.0, kturn=0.8)


def _kabir_jaw(cv, c):
    t = c.t
    with cam(cv, 1290, 420, 2.1, t=t):
        wall.draw_wall(cv, t, "night", glow=1.0, unfold=1.0)
        with K.lit(cv, "shop", amount=0.5):
            blink = 1.0 if (0.9 < t < 1.02 or 1.25 < t < 1.37) else 0.0
            chars.draw(cv, "kabir", x=1300, y=wall.FLOOR_Y, s=wall.CHAR_S, t=t, flip=True, expr="awe",
                       arms={"l": (4, 4), "r": (4, 4)}, mouth=0.25 + 0.4 * K.ease_out(c.seg(0.1, 0.6)),
                       turn=0.8, blink=blink, look=(0.4, -0.3))


# ---------------------------------------------------------------- inside the shop
def _shop_layers(cv, t, amma, tola, view="counter", fullness=1.0, front=None):
    shop.draw_shop(cv, t, view=view, fullness=fullness)
    with K.lit(cv, "shop", amount=0.7):
        amma(cv)
    shop.draw_counter_front(cv, t, view)
    if tola:
        tola(cv)
    if front:
        with K.lit(cv, "shop", amount=0.7):
            front(cv)


def _amma(t, view="counter", **kw):
    ax, ay, as_ = SA[view]["amma"]
    pose = dict(x=ax, y=ay, s=as_, t=t, flip=True, turn=0.4)
    pose.update(kw)
    return lambda cv: chars.draw(cv, "amma", **pose)


def _stroll(cv, c):
    t = c.t
    v = SA["wide"]
    dx, dy, ds = v["door"]
    cx, cy, cs = v["customer"]
    k = K.ease_in_out(c.seg(0.3, 6.2))
    x, y, s = lerp(dx + 40, cx + 150, k), lerp(dy, cy, k), lerp(ds, cs, k)
    walking = 0.3 < t < 6.2
    with cam(cv, 960, 560, lerp(1.0, 1.05, c.u), t=t):
        _shop_layers(cv, t, _amma(t, view="wide", expr="neutral", look=(0.6, 0.2)),
                     lambda cv: A.draw_scale(cv, A.ScalePose(*v["tola"][:2], s=v["tola"][2], t=t, eyes="open")),
                     view="wide")
        with K.lit(cv, "shop", amount=0.7):
            mk = K.ease_in_out(c.seg(1.4, 6.6))
            A.draw_dog(cv, A.DogPose(x=lerp(dx - 40, 300, mk), y=lerp(dy, 1010, mk), s=lerp(0.8, 0.95, mk), t=t,
                                     mode="walk" if 1.4 < t < 6.6 else "sit", phase=t * 1.5, expr="happy"))
            chars.draw(cv, "meher", x=lerp(dx - 20, 380, mk), y=lerp(dy, 990, mk), s=lerp(ds, cs, mk), t=t,
                       legs="walk" if 1.4 < t < 6.6 else "stand", phase=t * 1.4, expr="worried", look=(0.6, 0))
            chars.draw(cv, "kabir", x=x, y=y, s=s, t=t, legs="walk" if walking else "stand", phase=t * 1.3,
                       expr="smug", arms={"l": (6, 28), "r": (6, 28)}, hand={"l": "fist", "r": "fist"},
                       lean=4 * math.sin(t * 2.6) if walking else 0, head_tilt=-6 + 4 * math.sin(t * 2.6),
                       look=(0.3, 0))


# counter-view geometry: kids stand on the step at the counter (feet kept below frame)
KX, KY, KS = 420, 940, 1.9
MX, MY = 200, 950
TX, TY, TS = SA["counter"]["tola"]


def pan_top(side="l", tilt=0.0):
    ex = -180 if side == "l" else 180
    a = math.radians(tilt)
    return TX + ex * math.cos(a) * TS, TY + (-330 + ex * math.sin(a) + 150) * TS - 3


L_PAN = pan_top("l")


def _tola(t, **kw):
    return lambda cv: A.draw_scale(cv, A.ScalePose(TX, TY, s=TS, t=t, **kw))


def _best(cv, c):
    t = c.t
    with cam(cv, 760, 540, lerp(1.55, 1.6, c.u), t=t):
        _shop_layers(cv, t, _amma(t, expr="neutral", look=(0.7, 0.3)), _tola(t, eyes="open"),
                     front=lambda cv: chars.draw(cv, "kabir", x=KX, y=KY, s=KS, t=t, expr="smug",
                                                 mouth=c.mouth("kabir"), arms={"l": (6, 28), "r": (35, 120)},
                                                 hand={"r": "point"}, head_tilt=-6, lean=-3, look=(0.6, -0.2)))


def _pay_first(cv, c):
    t = c.t
    ax, ay, as_ = SA["counter"]["amma"]
    with cam(cv, ax - 60, ay - 300, lerp(1.6, 1.68, c.u), t=t):
        _shop_layers(cv, t, _amma(t, expr="neutral", mouth=c.mouth("amma"), arms={"l": (150, 20)},
                                  hand={"l": "point"}, look=(0.8, 0.3)), _tola(t, eyes="open"))


def _slap(cv, c):
    t = c.t
    slam = K.ease_in(c.seg(0.25, 0.42))
    raise_ = K.ease_out(c.seg(0.0, 0.25)) * (1 - slam)
    tgt = (L_PAN[0] - 10, L_PAN[1] - 6 - 200 * raise_)
    arm = reach("kabir", KX, KY, KS, "r", tgt, branch=-1)
    shake = 4 * clamp(1 - c.seg(0.42, 0.7)) * math.sin(t * 70)
    with cam(cv, 680, 500, lerp(1.6, 1.66, c.u), t=t):
        _shop_layers(cv, t, _amma(t, expr="neutral", look=(0.6, 0.4), blink=0.3),
                     _tola(t, eyes="open", jitter=0.15 * clamp(1 - c.seg(0.42, 0.9))),
                     front=lambda cv: chars.draw(cv, "kabir", x=KX + shake, y=KY, s=KS, t=t,
                                                 expr="smug" if t < 1.0 else "happy", mouth=c.mouth("kabir"),
                                                 arms={"r": arm, "l": (6, 28)}, hand={"r": "open"},
                                                 head_tilt=-8 + 3 * math.sin(t * 1.7), lean=-4, look=(0.2, -0.4),
                                                 turn=0.2))
        if 0.42 < t < 0.9:
            fx.vibe_lines(cv, L_PAN[0], L_PAN[1], 70, t, "line", clamp(1 - c.seg(0.42, 0.9)))


def _scribble_bubble(cv, c):
    t = c.t
    rise = K.ease_out(c.seg(0.1, 2.0))
    drift = K.ease_in_out(c.seg(3.0, 4.8))
    bx = lerp(L_PAN[0] - 10, L_PAN[0] + 60, rise) + math.sin(t * 2.2) * 12 * (1 - drift)
    by = lerp(L_PAN[1] - 20, L_PAN[1] - 280, rise)
    by = lerp(by, L_PAN[1] - 48, drift)
    r = lerp(30, 120, K.ease_out_back(c.seg(0.1, 1.3)))
    r = lerp(r, 46, drift)
    tola_eyes = "half" if t > 5.1 else "open"
    with cam(cv, 640, 420, 1.55, t=t):
        _shop_layers(cv, t, _amma(t, expr="neutral", look=(0.8, -0.6) if t < 4.5 else (0.8, 0.4)),
                     _tola(t, eyes=tola_eyes, mouth="line"),
                     front=lambda cv: chars.draw(cv, "kabir", x=KX, y=KY, s=KS, t=t,
                                                 expr="smug" if t < 5.0 else "surprised",
                                                 arms={"l": (6, 28), "r": (40, 130)}, hand={"r": "fist"},
                                                 look=(0.6, -0.8 + drift * 1.0), head_tilt=-6))
        fx.memory_bubble(cv, bx, by + math.sin(t * 3) * 6 * (1 - drift), r, t, scribble_scene, light="neutral",
                         color="#bfe3ff")


def _broken(cv, c):
    t = c.t
    with cam(cv, 600, 470, 1.65, t=t):
        _shop_layers(cv, t, _amma(t, expr="neutral", look=(0.8, 0.4)), _tola(t, eyes="half", mouth="line"),
                     front=lambda cv: chars.draw(cv, "kabir", x=KX, y=KY, s=KS, t=t, expr="angry",
                                                 mouth=c.mouth("kabir"), arms={"l": (6, 28), "r": (60, 40)},
                                                 hand={"r": "open"}, look=(0.7, -0.3), head_tilt=6))
        fx.bubble(cv, L_PAN[0], L_PAN[1] - 46, 46, "#bfe3ff", 0.9, t)


BX, BY = 440, 880   # boink staging: Kabir leaning over the pan


def _boink(cv, c):
    """He leans over the pan, pushes it down with one finger... it springs back up into his nose."""
    t = c.t
    push = K.ease_in_out(c.seg(0.9, 1.7))
    T0 = 2.4
    if t < T0:
        tilt = -16 * push
    else:
        tr = t - T0
        tilt = -16 * math.cos(tr * 17) * math.exp(-tr * 3.4) if tr > 0.09 else lerp(-16, 22, tr / 0.09)
        if tr > 0.09:
            tilt = 22 * math.exp(-(tr - 0.09) * 3.6) * math.cos((tr - 0.09) * 15)
    hit = K.ease_out(c.seg(T0 + 0.08, T0 + 0.28))
    lean = lerp(12, -9, hit) + 3 * math.sin(clamp(t - T0 - 0.3) * 12) * clamp(1 - c.seg(T0 + 0.3, T0 + 1.1))
    px, py = pan_top("l", tilt)
    arm = reach("kabir", BX, BY, KS, "r", (px - 8, py - 6), lean=lean) if t < T0 + 0.02 else (40, 110)
    expr = "smug" if t < 1.9 else "happy" if t < T0 + 0.08 else "wince" if t < T0 + 0.8 else "surprised"
    with cam(cv, 600, 430, 1.75, t=t, shake=12 * clamp(1 - c.seg(T0 + 0.08, T0 + 0.7))):
        _shop_layers(cv, t, _amma(t, expr="surprised" if t > T0 + 0.1 else "neutral", look=(0.8, 0.3)), None)
        with K.lit(cv, "shop", amount=0.7):
            chars.draw(cv, "kabir", x=BX, y=BY, s=KS, t=t, expr=expr, lean=lean,
                       arms={"l": (6, 28), "r": arm}, hand={"r": "point"},
                       look=(0.4, 0.9) if t < T0 else (0, 0), head_tilt=lerp(6, -16, hit),
                       blink=1.0 if T0 + 0.08 < t < T0 + 0.4 else 0.0)
        A.draw_scale(cv, A.ScalePose(TX, TY, s=TS, t=t, tilt=tilt,
                                     eyes="squint" if t < T0 else "wide", mouth="line" if t < T0 else "o"))
        hx, hy = head_world("kabir", BX, BY, KS, lean=lean)
        if t > T0 + 0.1:
            dizzy_stars(cv, hx, hy - 120, 110, t, a=clamp(1 - c.seg(4.8, 5.8)))
        if T0 + 0.05 < t < T0 + 0.6:
            fx.chime_rings(cv, px, py - 20, T0 + 0.08, t, "#ffffff", n=2, max_r=110)
            fx.star4(cv, px + 10, py - 30, 26 * clamp(1 - c.seg(T0 + 0.1, T0 + 0.5)), "#fff6c0", 1.0)


def _amma_hides_smile(cv, c):
    t = c.t
    ax, ay, as_ = SA["counter"]["amma"]
    with cam(cv, ax - 120, ay - 280, 1.6, t=t):
        cover = K.ease_out(c.seg(0.3, 0.6))
        _shop_layers(cv, t, _amma(t, expr="grin" if t < 1.6 else "happy", look=(0.8, 0.2),
                                  arms={"l": (lerp(10, 150, cover), lerp(10, 120, cover))}, hand={"l": "open"},
                                  head_tilt=-6), _tola(t, eyes="happy", mouth="grin",
                                                        jitter=0.3 * clamp(c.seg(0.2, 0.4) - c.seg(1.6, 2.0))))


def _snort(cv, c):
    t = c.t
    ms = 1.9
    hx, hy = head_world("meher", MX, MY, ms, turn=0.4)
    cover = K.ease_out(c.seg(0.45, 0.75))
    arm = reach("meher", MX, MY, ms, "r", (lerp(MX + 120, hx + 24, cover), lerp(MY - 200, hy + 62, cover)))
    shake = 3 * math.sin(t * 30) * clamp(c.seg(0.5, 0.7) - c.seg(2.6, 3.1))
    with cam(cv, 330, 480, 1.7, t=t):
        _shop_layers(cv, t, _amma(t, expr="neutral"), _tola(t, eyes="half", mouth="line"),
                     front=lambda cv: chars.draw(cv, "meher", x=MX, y=MY + shake, s=ms, t=t,
                                                 expr="laugh" if t > 0.4 else "grin", arms={"r": arm, "l": (10, 40)},
                                                 hand={"r": "open"}, head_tilt=-6 + 4 * math.sin(t * 9), turn=0.4))


def _verdict(cv, c):
    t = c.t
    ax, ay, as_ = SA["counter"]["amma"]
    with cam(cv, ax - 80, ay - 300, lerp(1.6, 1.7, c.u), t=t):
        _shop_layers(cv, t, _amma(t, expr="happy", mouth=c.mouth("amma"), head_tilt=8, look=(0.9, 0.4),
                                  arms={"l": (40, 70)}), _tola(t, eyes="closed", mouth="smile"))


def _red_ears(cv, c):
    t = c.t
    flush = K.ease_out(c.seg(0.3, 1.6))
    hx, hy = head_world("kabir", KX, KY, KS)
    with cam(cv, KX + 20, hy + 60, lerp(2.0, 2.15, c.u), t=t):
        _shop_layers(cv, t, _amma(t, expr="happy"), _tola(t, eyes="closed", mouth="smile"),
                     front=lambda cv: chars.draw(cv, "kabir", x=KX, y=KY, s=KS, t=t,
                                                 expr="sad" if t < 1.2 else "angry", look=(-0.4, 0.5),
                                                 arms={"l": (6, 20), "r": (6, 20)}, hand={"l": "fist", "r": "fist"},
                                                 head_tilt=-3))
        ear_flush(cv, "kabir", KX, KY, KS, flush)
        if t > 1.4:
            for side in (-1, 1):
                for i in range(2):
                    u = ((t - 1.4) * 1.3 + i * 0.5) % 1
                    cv.drawCircle(hx + side * (110 + u * 50), hy - u * 70, 10 + u * 14, K.fill("#ffffff", 0.5 * (1 - u)))


def _stupid(cv, c):
    t = c.t
    turn_away = K.ease_in_out(c.seg(2.8, 3.6))
    hx, hy = head_world("kabir", KX, KY, KS)
    with cam(cv, KX + 120, hy + 120, lerp(1.9, 1.8, c.u), t=t):
        _shop_layers(cv, t, _amma(t, expr="neutral"), _tola(t, eyes="half", mouth="frown"),
                     front=lambda cv: chars.draw(cv, "kabir", x=KX, y=KY, s=KS, t=t, expr="angry",
                                                 mouth=c.mouth("kabir"), flip=turn_away > 0.5,
                                                 turn=abs(0.5 - turn_away) * 1.2 + 0.1,
                                                 arms={"l": (40, 60), "r": (55, 40)} if t < 2.8 else
                                                 {"l": (6, 20), "r": (6, 20)}, hand={"l": "fist", "r": "open"},
                                                 head_tilt=8))
        ear_flush(cv, "kabir", KX, KY, KS, 1.0, flip=turn_away > 0.5)


def _storm_out(cv, c):
    t = c.t
    v = SA["wide"]
    dx, dy, ds = v["door"]
    cx, cy, cs = v["customer"]
    k = K.ease_in(c.seg(0.2, 2.6))
    x, y, s = lerp(cx + 150, dx, k), lerp(cy, dy, k), lerp(cs, ds, k)
    gone = t > 2.8
    with cam(cv, 900, 560, 1.02, t=t):
        _shop_layers(cv, t, _amma(t, view="wide", expr="sad", look=(-0.9, 0.2)),
                     lambda cv: A.draw_scale(cv, A.ScalePose(*v["tola"][:2], s=v["tola"][2], t=t,
                                                              eyes="half", mouth="frown")), view="wide")
        with K.lit(cv, "shop", amount=0.7):
            A.draw_dog(cv, A.DogPose(x=300, y=1010, s=0.95, t=t, mode="sit", expr="sad", ear=0.2, wag=0.2))
            chars.draw(cv, "meher", x=420, y=1000, s=cs, t=t, expr="worried", flip=True, look=(0.8, 0))
            if not gone:
                chars.draw(cv, "kabir", x=x, y=y, s=s, t=t, legs="walk", phase=t * 2.2, flip=True, expr="angry",
                           arms={"l": (10, 20), "r": (10, 20)}, hand={"l": "fist", "r": "fist"}, lean=-6)


def _hungry(cv, c):
    t = c.t
    ax, ay, as_ = SA["counter"]["amma"]
    with cam(cv, lerp(ax - 260, ax - 180, c.u), ay - 300, lerp(1.35, 1.45, c.u), t=t):
        _shop_layers(cv, t, _amma(t, expr="sad", mouth=c.mouth("amma"), look=(-0.9, -0.1), flip=False, head_tilt=-6),
                     _tola(t, eyes="half", mouth="line"),
                     front=lambda cv: chars.draw(cv, "meher", x=640, y=MY, s=1.9, t=t, expr="worried",
                                                 look=(0.8, -0.7), head_tilt=8, turn=0.6))


RING = (3200, 262)


def _dust_ring(cv, c):
    t = c.t
    k = K.ease_in_out(c.seg(0.3, 5.8))
    cx, cy, z = lerp(2700, RING[0], k), lerp(540, RING[1] + 20, k), lerp(1.0, 2.4, k)
    cy = clamp(cy, 540 / z, 1080 - 540 / z)
    shop.draw_shop(cv, t, view="shelves", fullness=0.92, cam=(cx, cy, z))
    with K.camera(cv, cx, cy, z, t=t):
        a = clamp(c.seg(1.0, 3.2))
        x, y = RING
        cv.drawPath(K.ellipse(x, y - 3, 44, 9), K.fill("#d9c09a", 0.35 * a))
        cv.drawPath(K.ellipse(x, y - 3, 44, 9), K.stroke("#ffe7c0", 2.2, 0.85 * a))
        cv.drawPath(K.ellipse(x, y - 3, 32, 6), K.fill("#3a2010", 0.6 * a))
        fx.motes(cv, t, (x - 110, y - 150, x + 110, y + 4), n=26, color="#f0dcc0", a=0.6 * a, seed=17, size=1.3)


D_KABIR = Line("kabir", "Today I saved a whole busload of children from a flood. With a rope. And a helicopter.", at=1.0)

SHOTS = [
    Shot("S04_SH01", _morning_wide, duration=5.6, transition="fade_black", trans_dur=1.2,
         sfx=[bed("sparrows_dawn", 5.6, -12), Sfx("koel_call", 0.8, -14), Sfx("whoosh", 2.75, -14, params={"intensity": 0.3})]),
    Shot("S04_SH02", _kabir_saw, lines=[Line("kabir", "You were floating. I saw you.", at=0.5)], tail=0.9,
         music="", sfx=[bed("sparrows_dawn", 5.0, -16)]),
    Shot("S04_SH03", _meher_grin, duration=5.8, sfx=[bed("sparrows_dawn", 5.8, -16), Sfx("sparkle", 3.15, -10)]),
    Shot("S04_SH04", _kabir_worse, duration=2.8, sfx=[bed("sparrows_dawn", 2.8, -16), Sfx("koel_call", 1.2, -16)]),
    Shot("S04_SH05", _trail, duration=6.4, transition="fade_black", trans_dur=1.4, music="midnight_mystery",
         sfx=[bed("night_bed", 6.4), Sfx("footsteps_soft", 0.2, -12, dur=6.0)]),
    Shot("S04_SH06", _joke, duration=6.2, transition="dissolve", trans_dur=0.6,
         lines=[Line("kabir", "If this is a joke—", at=1.0)],
         sfx=[bed("night_bed", 6.2), Sfx("wall_glow", 2.4, -6), Sfx("wind_chime_hello", 4.6, -8)]),
    Shot("S04_SH07", _unfold, duration=7.0, music="wonder_unfold", music_hits=[0.4, 2.8, 4.6],
         sfx=[bed("night_bed", 7.0, -18), Sfx("shop_unfold", 0.3, -4), Sfx("awning_snap", 2.7, -6),
              Sfx("lantern_light", 3.4, -8), Sfx("lantern_light", 3.9, -9), Sfx("sparkle", 5.0, -8),
              Sfx("dog_bark", 5.6, -10, params={"n": 1})]),
    Shot("S04_SH08", _kabir_jaw, duration=3.0, sfx=[bed("night_bed", 3.0, -20)]),
    Shot("S04_SH09", _stroll, duration=7.4, music="swagger", transition="dissolve", trans_dur=0.6,
         sfx=[bed("crickets_bed", 7.4, -24), Sfx("footsteps_soft", 0.4, -10, dur=5.8), Sfx("floor_creak", 2.2, -12)]),
    Shot("S04_SH10", _best, lines=[Line("kabir", "I'll have the best thing you've got.", at=0.4)], tail=0.7,
         sfx=[bed("crickets_bed", 4.0, -24)]),
    Shot("S04_SH11", _pay_first, lines=[Line("amma", "Pay first.", at=0.5)], tail=1.2,
         sfx=[bed("crickets_bed", 3.0, -24)]),
    Shot("S04_SH12", _slap, lines=[D_KABIR], tail=0.7,
         sfx=[bed("crickets_bed", 9.0, -24), Sfx("tola_clank", 0.42, -6)]),
    Shot("S04_SH13", _scribble_bubble, duration=7.0,
         sfx=[bed("crickets_bed", 7.0, -24), Sfx("bubble_rise", 0.1, -6), Sfx("bubble_settle", 4.7, -8),
              Sfx("tola_tink", 5.2, -4)]),
    Shot("S04_SH14", _broken, lines=[Line("kabir", "It's broken.", at=0.4)], tail=0.8,
         sfx=[bed("crickets_bed", 3.0, -24)]),
    Shot("S04_SH15", _boink, duration=6.2, music_hits=[2.48],
         sfx=[bed("crickets_bed", 6.2, -24), Sfx("tola_clank", 1.1, -12), Sfx("boing", 2.46, -2),
              Sfx("pop", 2.5, -6), Sfx("sparkle", 2.9, -12)]),
    Shot("S04_SH16", _amma_hides_smile, duration=2.6, sfx=[bed("crickets_bed", 2.6, -24), Sfx("tola_laugh", 0.25, -8)]),
    Shot("S04_SH17", _snort, duration=3.6, sfx=[bed("crickets_bed", 3.6, -24), Sfx("pop", 0.5, -10)]),
    Shot("S04_SH18", _verdict, lines=[
        Line("amma", "Tola only weighs what's true, little man. Come back when you've done something real.", at=0.4)],
         tail=0.8, sfx=[bed("crickets_bed", 7.0, -24)]),
    Shot("S04_SH19", _red_ears, duration=3.2, sfx=[bed("crickets_bed", 3.2, -24), Sfx("iron_steam", 1.4, -16)]),
    Shot("S04_SH20", _stupid, lines=[Line("kabir", "It's a stupid shop anyway. A stupid sugar museum.", at=0.3)],
         tail=1.0, sfx=[bed("crickets_bed", 5.0, -24)]),
    Shot("S04_SH21", _storm_out, duration=3.6, music="deflate",
         sfx=[bed("crickets_bed", 3.6, -24), Sfx("footsteps_soft", 0.2, -6, dur=2.4, params={"rate": 2.2})]),
    Shot("S04_SH22", _hungry, lines=[Line("amma", "That one's hungry for something. And it isn't sweets.", at=0.8)],
         tail=1.4, sfx=[bed("crickets_bed", 7.0, -24)]),
    Shot("S04_SH23", _dust_ring, duration=7.0, sfx=[bed("crickets_bed", 7.0, -24), Sfx("sparkle", 3.0, -18)]),
]

SHOTS = finalize(SHOTS, 4)
