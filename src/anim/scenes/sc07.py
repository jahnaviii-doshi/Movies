"""Scene 7: LOW POINT (12:30-15:00).

Gloves at dinner -> the shop barely appears -> nearly bare shop, Amma almost gone ->
Kabir's confession, his sorry weighs nothing -> rule 5: Amma fades because no one remembers ->
'We need Nani.' -> the shop slams shut like a book.
"""
from __future__ import annotations

import math

import skia

from .. import core as K, fx
from ..core import W, H, fill, stroke
from ..rig import chars, animals as A
from ..sets import rooftop as RT, wall as WL, shop as SH, gali as GA
from ..timeline import Shot, Line, Sfx
from ._util_c import cam, fit_beds, bed, pan_pos, reach, shoulder, amma, sugar_rain, flicker_val, thali, tola

AN = RT.ANCHORS
NANI_SEAT = AN["charpai_nani"]["surface"]
MEHER_SEAT = AN["charpai_meher"]["surface"]
KABIR_SEAT = AN["charpai_kabir"]["surface"]
S_SIT = 1.55

# shop counter anchors
AX, AY, AS = SH.ANCHORS["counter"]["amma"]
TX, TY, TS = SH.ANCHORS["counter"]["tola"]

FADE = 0.74
FULL = 0.15
A_ALPHA = 0.26
A_DESAT = 0.8


# ------------------------------------------------------------------ rooftop dinner
def _dinner(cv, c, nani_kw=None, meher_kw=None, kabir_kw=None, chew=True):
    t = c.t
    RT.draw_rooftop(cv, t, time="evening", lantern=0.8)
    for (x, y) in (NANI_SEAT, MEHER_SEAT, KABIR_SEAT):
        thali(cv, x + 70, y + 2, 1.0)
    with K.lit(cv, "dusk", amount=0.55):
        nk = dict(x=NANI_SEAT[0], y=NANI_SEAT[1] + 10, s=S_SIT, legs="sit", t=t, turn=0.3,
                  mouth=c.mouth("nani"), arms={"r": (20, 40)})
        nk.update(nani_kw or {})
        chars.draw(cv, "nani", **nk)
        mk = dict(x=MEHER_SEAT[0], y=MEHER_SEAT[1] + 10, s=S_SIT * 1.05, legs="sit", t=t, turn=0.6,
                  look=(0.8, 0), expr="worried", mouth=c.mouth("meher"))
        mk.update(meher_kw or {})
        chars.draw(cv, "meher", **mk)
        # Kabir eats left-handed: left hand to mouth on a loop; right hand gloved, kept low
        ph = (t % 2.6) / 2.6
        up = K.smooth(K.seg(ph, 0.1, 0.35)) * (1 - K.smooth(K.seg(ph, 0.55, 0.8))) if chew else 0
        kk = dict(x=KABIR_SEAT[0], y=KABIR_SEAT[1] + 10, s=S_SIT, legs="sit", t=t, flip=True, turn=0.3,
                  arms={"l": (K.lerp(15, 40, up), K.lerp(20, 150, up)), "r": (4, 8)},
                  extra={"glove": True}, expr="neutral", mouth=c.mouth("kabir"))
        kk.update(kabir_kw or {})
        chars.draw(cv, "kabir", **kk)


def s01(cv, c):
    # establishing: dinner on the rooftop, evening glow
    z = K.lerp(1.0, 1.06, K.ease_in_out(c.u))
    with cam(cv, 960, 640, z, t=c.t):
        _dinner(cv, c, meher_kw=dict(look=(0.9, 0.1), expr="neutral"))


def s02(cv, c):
    # MS Kabir: left-handed eating, the gloved hand tucked away
    z = K.lerp(2.0, 2.1, c.u)
    with cam(cv, KABIR_SEAT[0] - 10, KABIR_SEAT[1] - 230, z, t=c.t):
        tuck = K.smooth(c.seg(2.4, 3.2))
        _dinner(cv, c, kabir_kw=dict(arms={"l": (20, 140 * (1 - tuck) + 10), "r": (4 + 18 * tuck, 8 + 70 * tuck)},
                                     look=(-0.5, 0.3) if c.t > 2.4 else (0, 0), expr="worried" if c.t > 2.4 else "neutral"),
                chew=c.t < 2.4)


def s03(cv, c):
    # Nani notices
    z = 2.0
    with cam(cv, NANI_SEAT[0] + 40, NANI_SEAT[1] - 220, K.lerp(z, z * 1.04, c.u), t=c.t):
        _dinner(cv, c, nani_kw=dict(expr="surprised" if c.t < 0.8 else "neutral", brow=0.8, head_tilt=-6,
                                    look=(0.9, 0.2), turn=0.55))


def s04(cv, c):
    # Kabir: "It's... fashion." - a weak grin, then he hides the glove
    with cam(cv, KABIR_SEAT[0] - 10, KABIR_SEAT[1] - 230, K.lerp(2.1, 2.2, c.u), t=c.t):
        hide = K.smooth(c.seg(2.0, 2.8))
        _dinner(cv, c, chew=False, kabir_kw=dict(
            expr="grin" if c.t < 2.2 else "worried", look=(-0.4, 0.1) if c.t < 2.2 else (0.6, 0.6),
            arms={"l": (10, 20), "r": (40 - 30 * hide, 60 + 40 * hide)}, head_tilt=4 * hide))


def s05(cv, c):
    # two-shot: Meher watches him; Kabir won't look at her
    mx = (MEHER_SEAT[0] + KABIR_SEAT[0]) / 2
    with cam(cv, mx, 640, K.lerp(1.55, 1.62, c.u), t=c.t):
        away = K.smooth(c.seg(1.4, 2.0))
        _dinner(cv, c, chew=False,
                meher_kw=dict(look=(0.9, 0.0), expr="worried", turn=0.75),
                kabir_kw=dict(look=(K.lerp(-0.6, 0.8, away), 0.5 * away), turn=K.lerp(0.4, 0.9, away),
                              expr="sad", head_tilt=8 * away, arms={"l": (8, 10), "r": (8, 10)}))


def s05b(cv, c):
    # Nani shrugs and fans herself; Meher keeps watching Kabir
    with cam(cv, (NANI_SEAT[0] + MEHER_SEAT[0]) / 2, 650, K.lerp(1.5, 1.56, c.u), t=c.t):
        fan = math.sin(c.t * 3.2) * 18
        _dinner(cv, c, chew=False,
                nani_kw=dict(hold="fan", arms={"r": (40 + fan, 100)}, expr="happy", look=(0.6, 0), turn=0.5,
                             head_tilt=-4 + math.sin(c.seg(0.4, 1.2) * math.pi) * 6),
                meher_kw=dict(look=(1.0, 0.0), expr="worried", turn=0.85),
                kabir_kw=dict(look=(0.8, 0.6), expr="sad", turn=0.9, arms={"l": (8, 10), "r": (8, 10)}))


# ------------------------------------------------------------------ midnight at the wall
MEHER_WX, KABIR_WX, DOG_WX = 560, 1330, 760


def _wall_kids(cv, c, kabir_x=KABIR_WX, kabir_walk=False, meher_kw=None, kabir_kw=None, dog_kw=None, light_amt=1.0):
    t = c.t
    with K.lit(cv, "night", amount=light_amt):
        dk = dict(x=DOG_WX, y=WL.FLOOR_Y, s=WL.DOG_S, mode="sit", t=t, ear=0.4, expr="sad", wag=0.2)
        dk.update(dog_kw or {})
        A.draw_dog(cv, A.DogPose(**dk))
        mk = dict(x=MEHER_WX, y=WL.FLOOR_Y, s=WL.CHAR_S, t=t, turn=0.35, expr="worried", mouth=c.mouth("meher"))
        mk.update(meher_kw or {})
        chars.draw(cv, "meher", **mk)
        if kabir_x is not None:
            kk = dict(x=kabir_x, y=WL.FLOOR_Y, s=WL.CHAR_S, t=t, flip=True, turn=0.4, expr="sad",
                      hold_l="jar", arms={"l": (20, 110), "r": (10, 100)}, extra={"glove": True},
                      mouth=c.mouth("kabir"))
            if kabir_walk:
                kk.update(legs="walk", phase=t * 0.8)
            kk.update(kabir_kw or {})
            chars.draw(cv, "kabir", **kk)


def s06(cv, c):
    # midnight, Meher + Chutney wait before the plain wall. Crickets. Waiting.
    with cam(cv, 960, 560, K.lerp(1.0, 1.05, c.u), t=c.t):
        WL.draw_wall(cv, c.t, time="night")
        _wall_kids(cv, c, kabir_x=None, meher_kw=dict(look=(0.5, -0.4), expr="worried"),
                   dog_kw=dict(look_up=0.2))


def s07(cv, c):
    # Kabir comes up quietly behind them, the jar clutched to his chest; Meher turns
    x = K.lerp(1750, KABIR_WX, K.ease_out(c.seg(0.0, 3.6)))
    walking = c.t < 3.6
    turn_m = K.smooth(c.seg(2.8, 3.6))
    with cam(cv, 960, 560, 1.05, t=c.t):
        WL.draw_wall(cv, c.t, time="night")
        _wall_kids(cv, c, kabir_x=x, kabir_walk=walking,
                   meher_kw=dict(look=(K.lerp(0.4, 1.0, turn_m), 0.1), turn=K.lerp(0.35, 0.8, turn_m),
                                 expr="worried"),
                   kabir_kw=dict(look=(-0.3, 0.6), expr="sad"),
                   dog_kw=dict(ear=K.lerp(0.4, 0.9, turn_m), expr="alert" if turn_m > 0.5 else "sad"))


def s08(cv, c):
    # the clock strikes... the cracks glow BARELY. The shop flickers like a bad bulb.
    t = c.t
    base = 0.62 * K.smooth(c.seg(1.6, 4.5))
    fl = flicker_val(t, base, seed=7) if t > 1.6 else 0.0
    with cam(cv, 960, 520, K.lerp(1.0, 1.14, K.ease_in_out(c.u)), t=t):
        WL.draw_wall(cv, t, time="night", glow=0.25 * K.smooth(c.seg(0.6, 1.8)) * (1 - base), flicker=fl)
        _wall_kids(cv, c, meher_kw=dict(look=(0.3, -0.5), expr="awe" if t < 4 else "worried"),
                   kabir_kw=dict(look=(-0.5, -0.5), expr="sad"),
                   dog_kw=dict(look_up=0.5, ear=0.9, expr="alert"))


def s09(cv, c):
    # their faces in the stuttering light
    t = c.t
    fl = flicker_val(t + 3, 0.62, seed=7)
    with cam(cv, 950, 420, 1.75, t=t):
        WL.draw_wall(cv, t, time="night", flicker=fl)
        _wall_kids(cv, c, light_amt=0.9 - 0.25 * fl,
                   meher_kw=dict(look=(0.2, -0.3), expr="worried"),
                   kabir_kw=dict(look=(-0.2, -0.3), expr="sad"),
                   dog_kw=dict(look_up=0.4, expr="sad"))
    fx.glow_dot(cv, 960, 500, 520, "gold", 0.08 * fl)


def s09b(cv, c):
    # they step through a door that is mostly an idea
    t = c.t
    fl = flicker_val(t + 7, 0.6, seed=7)
    k = K.ease_in_out(c.seg(0.4, 4.4))
    with cam(cv, 960, K.lerp(560, 600, k), K.lerp(1.05, 1.35, k), t=t):
        WL.draw_wall(cv, t, time="night", flicker=fl)
        a = 1 - K.smooth(c.seg(3.6, 4.8))
        with K.lit(cv, "night", alpha=a):
            A.draw_dog(cv, A.DogPose(x=K.lerp(DOG_WX, 930, k), y=WL.FLOOR_Y, s=WL.DOG_S, mode="walk", phase=t,
                                     t=t, flip=False, ear=0.3, expr="sad", wag=0.2))
            chars.draw(cv, "meher", x=K.lerp(MEHER_WX, 900, k), y=WL.FLOOR_Y, s=WL.CHAR_S, t=t, legs="walk",
                       phase=t * 0.7, turn=0.8, expr="worried", look=(0.9, -0.3))
            chars.draw(cv, "kabir", x=K.lerp(KABIR_WX, 1030, k), y=WL.FLOOR_Y, s=WL.CHAR_S, t=t, legs="walk",
                       phase=t * 0.7, flip=True, turn=0.8, expr="sad", hold_l="jar",
                       arms={"l": (20, 110), "r": (10, 100)}, extra={"glove": True}, look=(0.5, 0.4))


# ------------------------------------------------------------------ inside: nearly bare
def _counter(cv, c, fade=FADE, full=FULL, amma_kw=None, amma_alpha=A_ALPHA, amma_desat=A_DESAT,
             tola_kw=None, kids=None, specs=0.75, sparkle=1.0, blaze=0.0):
    t = c.t
    SH.draw_shop(cv, t, view="counter", fullness=full, fade=fade, blaze=blaze)
    ak = dict(turn=0.3, expr="sad", mouth=c.mouth("amma"))
    ak.update(amma_kw or {})
    amma(cv, AX, AY, AS, t, alpha=amma_alpha, desat=amma_desat, specs_boost=specs, sparkle=sparkle, **ak)
    SH.draw_counter_front(cv, t, "counter", fade=fade, blaze=blaze)
    tk = dict(tarnish=0.8, eyes="half", mouth="frown")
    tk.update(tola_kw or {})
    tola(cv, TX, TY, TS, t, **tk)
    if kids:
        with K.lit(cv, "dim", amount=0.32):
            kids(cv)


def s10(cv, c):
    # the shop, barely: dust, bare shelves; the kids step in
    t = c.t
    with cam(cv, 960, 540, K.lerp(1.0, 1.05, c.u), t=t):
        SH.draw_shop(cv, t, view="wide", fullness=FULL, fade=FADE)
        ax, ay, asc = SH.ANCHORS["wide"]["amma"]
        amma(cv, ax, ay, asc, t, alpha=0.22, desat=0.85, specs_boost=0.6, sparkle=1.0, expr="sad")
        SH.draw_counter_front(cv, t, "wide", fade=FADE)
        tx, ty, ts = SH.ANCHORS["wide"]["tola"]
        tola(cv, tx, ty, ts, t, tarnish=0.8, eyes="half")
        cx, cy, cs = SH.ANCHORS["wide"]["customer"]
        dx_, dy_, ds = SH.ANCHORS["wide"]["dog"]
        k = K.ease_out(c.seg(0, 3.5))
        with K.lit(cv, "dim", amount=0.5):
            A.draw_dog(cv, A.DogPose(x=K.lerp(130, dx_, k), y=dy_, s=ds, t=t, mode="walk" if k < 1 else "stand",
                                     phase=t * 1.2, ear=0.3, expr="sad", wag=0.2))
            chars.draw(cv, "meher", x=K.lerp(60, cx - 40, k), y=cy, s=cs, t=t, legs="walk" if k < 1 else "stand",
                       phase=t * 0.9, expr="worried", look=(0.8, -0.3), turn=0.6)
            chars.draw(cv, "kabir", x=K.lerp(-120, cx + 130, K.ease_out(c.seg(0.6, 4.2))), y=cy + 10, s=cs,
                       t=t, legs="walk" if t < 4.2 else "stand", phase=t * 0.8, expr="sad",
                       hold_l="jar", arms={"l": (20, 110), "r": (10, 100)}, extra={"glove": True}, look=(0.5, 0.4))
    fx.motes(cv, t, (0, 0, W, H), n=50, color="#b8b2a8", a=0.35, seed=11)


def _kids_counter(c, meher=True, kabir=True, mk=None, kk=None, kabir_xy=(250, 1150), meher_xy=(500, 1190)):
    t = c.t

    def f(cv):
        if kabir:
            d = dict(x=kabir_xy[0], y=kabir_xy[1], s=1.9, t=t, turn=0.55, expr="sad", look=(0.6, -0.2),
                     extra={"glove": True}, mouth=c.mouth("kabir"))
            d.update(kk or {})
            chars.draw(cv, "kabir", **d)
        if meher:
            d = dict(x=meher_xy[0], y=meher_xy[1], s=1.8, t=t, turn=0.6, expr="worried", look=(0.7, -0.3),
                     mouth=c.mouth("meher"))
            d.update(mk or {})
            chars.draw(cv, "meher", **d)
    return f


def s11(cv, c):
    # "Ah. Both of you." - the faint voice; the spectacles turn to them
    t = c.t
    with cam(cv, 1040, 520, K.lerp(1.05, 1.12, c.u), t=t):
        _counter(cv, c, amma_kw=dict(turn=0.15, look=(-0.6, 0.1), expr="sad"),
                 kids=_kids_counter(c, kk=dict(hold_l="jar", arms={"l": (20, 110), "r": (10, 100)})))


def s12(cv, c):
    # Kabir sets the jar on the counter. "I took it. I wanted them to think I was... somebody."
    t = c.t
    put = K.smooth(c.seg(0.2, 1.4))
    with cam(cv, 560, 640, K.lerp(1.55, 1.68, c.u), t=t):
        _counter(cv, c, amma_kw=dict(look=(-0.8, 0.3)),
                 kids=_kids_counter(c, meher=False, kabir_xy=(380, 1110),
                                    kk=dict(hold_l="jar" if put < 0.6 else None, expr="cry" if t > 3.0 else "sad",
                                            look=(0.2, 0.7) if t < 3 else (-0.2, 0.5),
                                            arms={"l": (K.lerp(20, 60, put), K.lerp(110, 70, put)), "r": (10, 90)},
                                            head_tilt=6)))
        if put >= 0.6:
            # the jar now stands on the counter: nearly empty, a couple of violet coils
            jx, jy = 520, 660
            from ..sets.shop import jalebi_jar_draw
            jalebi_jar_draw(cv, jx, jy, 90, 66, lit=0.35, t=t)


def s13(cv, c):
    # he peels off the glove: crystal sugar past the knuckles to the wrist
    t = c.t
    peel = K.smooth(c.seg(0.6, 2.2))
    with cam(cv, 470, 760, K.lerp(2.0, 2.25, K.ease_in_out(c.u)), t=t):
        _counter(cv, c, sparkle=0.6, kids=_kids_counter(
            c, meher=False, kabir_xy=(380, 1110),
            kk=dict(expr="sad", look=(0.3, 0.9), arms={"r": (60, 70), "l": (35, 120)},
                    extra={"glove": peel < 0.5, "crystal": 1.0, "crystal_wrist": 1.0})))
    if peel > 0.5:
        sx, sy = shoulder("kabir", 380, 1110, 1.9, "r")
        fx.sparkles(cv, t, 470 + (sx - 470) * 0 + 0, 760, spread=60, n=6, color="#eaf7ff", size=6, seed=4,
                    a=K.smooth(c.seg(2.2, 2.8)))


def s14(cv, c):
    # CU: "I'm sorry."
    t = c.t
    with cam(cv, 400, 650, K.lerp(2.4, 2.5, c.u), t=t):
        _counter(cv, c, sparkle=0.4, kids=_kids_counter(
            c, meher=False, kabir_xy=(380, 1110),
            kk=dict(expr="cry", look=(0.2, 0.8), head_tilt=8, arms={"r": (40, 60), "l": (10, 20)},
                    extra={"crystal": 1.0, "crystal_wrist": 1.0})))


def s15(cv, c):
    # Amma, soft: "Oh, little man."  (only her spectacles really catch the light)
    t = c.t
    with cam(cv, AX, AY - 300, K.lerp(1.9, 2.0, c.u), t=t):
        _counter(cv, c, amma_alpha=0.3, specs=0.85, amma_kw=dict(turn=0.1, look=(-0.7, 0.4), expr="sad",
                                                                 head_tilt=-6))


def s16(cv, c):
    # "Then take my sorry." hand on the pan; a bubble rises, flickers, fizzles. Tola cannot move.
    t = c.t
    lpx, lpy = pan_pos(TX, TY, TS, "l", 0)
    kx, ky = 330, 1060
    sx, sy = shoulder("kabir", kx, ky, 1.9, "r")
    reach_k = K.smooth(c.seg(2.2, 3.4))
    ang = reach(sx, sy, lpx, lpy - 6, "r")
    arm = (K.lerp(40, ang, reach_k), K.lerp(60, 0, reach_k))
    with cam(cv, 640, 560, K.lerp(1.4, 1.5, c.u), t=t):
        _counter(cv, c, sparkle=0.5, amma_kw=dict(look=(-0.8, 0.4)),
                 tola_kw=dict(eyes="half", mouth="frown", jitter=0.15 * K.smooth(c.seg(4.6, 5.4)) *
                              (1 - K.smooth(c.seg(5.8, 6.4)))),
                 kids=_kids_counter(c, meher=False, kabir_xy=(kx, ky),
                                    kk=dict(expr="cry" if t > 7 else "sad", look=(0.8, -0.4), turn=0.7,
                                            arms={"r": arm, "l": (10, 20)},
                                            extra={"crystal": 1.0, "crystal_wrist": 1.0})))
        # the bubble: rises from his palm, wobbles, flickers, and pops into nothing
        rise = K.ease_out(c.seg(3.6, 5.2))
        life = 1 - K.smooth(c.seg(5.6, 6.6))
        if 3.6 < t < 6.8:
            fl = 0.55 + 0.45 * math.sin(t * 31) * math.sin(t * 13)
            r = 34 * K.ease_out_back(c.seg(3.6, 4.3)) * (0.7 + 0.3 * life)
            fx.bubble(cv, lpx, lpy - 40 - 90 * rise, r, "#cfd6e3", a=life * K.clamp(fl), t=t)
        if 6.4 < t < 7.2:
            u = c.seg(6.4, 7.2)
            for i in range(8):
                a = i * math.pi / 4
                fx.star4(cv, lpx + math.cos(a) * 50 * u, lpy - 130 + math.sin(a) * 50 * u, 6 * (1 - u), "#cfd6e3", 1 - u)


def s16b(cv, c):
    # CU Tola: dull, eyes half shut; it tries, rattles, and cannot move
    t = c.t
    with cam(cv, TX, TY - 330 * TS, K.lerp(2.3, 2.4, c.u), t=t):
        _counter(cv, c, amma_alpha=0.18, specs=0.5, sparkle=0.6,
                 tola_kw=dict(eyes="half" if t < 1.2 else "closed", mouth="wobble" if t < 2 else "frown",
                              jitter=0.25 * (1 - K.smooth(c.seg(0.6, 1.8)))))


def s17(cv, c):
    # Kabir's shoulders shake. Meher's hand on his shoulder.
    t = c.t
    shake = math.sin(t * 9) * 2.5 * (1 - K.smooth(c.seg(3.5, 4.5)))
    touch = K.smooth(c.seg(1.0, 2.0))
    with cam(cv, 420, 680, K.lerp(1.65, 1.72, c.u), t=t):
        _counter(cv, c, sparkle=0.5, kids=_kids_counter(
            c, kabir_xy=(300, 1120 + shake), meher_xy=(580, 1170),
            kk=dict(expr="cry", look=(-0.1, 0.9), head_tilt=10 + shake, turn=0.4, arms={"r": (12, 30), "l": (8, 20)},
                    extra={"crystal": 1.0, "crystal_wrist": 1.0}),
            mk=dict(flip=True, turn=0.6, look=(0.6, 0.3), expr="sad", arms={"r": (K.lerp(8, 95, touch), K.lerp(10, 40, touch))})))


def s18(cv, c):
    # Meher turns to the faint shape: "Amma, why are you fading?"
    t = c.t
    with cam(cv, 820, 560, K.lerp(1.15, 1.22, c.u), t=t):
        _counter(cv, c, amma_kw=dict(look=(-0.6, 0.2), turn=0.2),
                 kids=_kids_counter(c, kabir_xy=(170, 1150), meher_xy=(470, 1180),
                                    kk=dict(expr="sad", look=(0.6, -0.1), extra={"crystal": 1.0, "crystal_wrist": 1.0},
                                            arms={"r": (12, 40)}),
                                    mk=dict(look=(0.9, -0.6), expr="worried", turn=0.75, brow=0.6)))


def s19(cv, c):
    # Amma: "A shop like this lives in people's remembering. When the last one forgets..."
    t = c.t
    with cam(cv, AX - 60, AY - 260, K.lerp(1.65, 1.8, K.ease_in_out(c.u)), t=t):
        _counter(cv, c, amma_alpha=0.28, specs=0.85, sparkle=1.2,
                 amma_kw=dict(turn=0.25, look=(-0.5, 0.2), expr="happy" if t < 2 else "sad", head_tilt=-4,
                              arms={"r": (K.lerp(10, 50, c.seg(1, 2)), 60)}))


def s20(cv, c):
    # "...poof. Sugar in the rain."  a tiny shrug; sugar sparkles drifting down like rain
    t = c.t
    shrug = math.sin(c.seg(0.2, 1.0) * math.pi) * 6
    with cam(cv, AX - 60, AY - 260, K.lerp(1.8, 1.7, c.u), t=t):
        _counter(cv, c, amma_alpha=0.24, specs=0.8, sparkle=1.5,
                 amma_kw=dict(turn=0.25, look=(-0.2, -0.4), expr="happy", head_tilt=-shrug,
                              arms={"l": (20 + shrug * 4, 50), "r": (20 + shrug * 4, 50)}))
    sugar_rain(cv, t, (300, -40, 1700, 1100), n=80, a=K.smooth(c.seg(0.8, 2.0)), seed=5)


def s21(cv, c):
    # CU Meher putting it together: eyes darting... then "Nani's story. She forgot the ending..."
    t = c.t
    dart = (math.sin(t * 5) * 0.8 if t < 2.2 else 0.3, -0.2 if t < 2.2 else 0)
    with cam(cv, 480, 730, K.lerp(2.5, 2.65, c.u), t=t):
        _counter(cv, c, kids=_kids_counter(
            c, kabir=False, meher_xy=(470, 1180),
            mk=dict(look=dart, expr="worried" if t < 2.2 else "surprised" if t < 3.0 else "determined",
                    brow=0.5 if t < 3 else 0, turn=0.45, head_tilt=math.sin(t * 2) * 2)))
    sugar_rain(cv, t, (0, -40, 1920, 1100), n=40, a=0.6 * (1 - K.smooth(c.seg(0, 3))), seed=6)


def s22(cv, c):
    # Amma, gently confused: "Who's Nani?"
    t = c.t
    with cam(cv, AX - 40, AY - 280, K.lerp(1.9, 1.95, c.u), t=t):
        _counter(cv, c, amma_alpha=0.2, specs=0.75, sparkle=1.4,
                 amma_kw=dict(turn=0.3, look=(-0.4, 0.0), expr="neutral", head_tilt=8, brow=0.5))


def s23(cv, c):
    # Meher grabs Kabir's good hand: "We need Nani."
    t = c.t
    grab = K.smooth(c.seg(0.2, 0.8))
    with cam(cv, 400, 650, K.lerp(1.9, 2.05, c.u), t=t):
        _counter(cv, c, kids=_kids_counter(
            c, kabir_xy=(230, 1130), meher_xy=(500, 1170),
            kk=dict(expr="surprised" if t < 1.6 else "determined", look=(0.8, 0.0), turn=0.5,
                    arms={"r": (12, 40), "l": (8, 10)}, extra={"crystal": 1.0, "crystal_wrist": 1.0}),
            mk=dict(flip=True, turn=0.55, expr="determined", look=(0.7, 0.0),
                    arms={"r": (K.lerp(8, 70, grab), K.lerp(10, 20, grab))})))


def s24(cv, c):
    # outside: the lantern gutters and the shop slams flat into the wall like a book shut
    t = c.t
    slam = c.seg(1.4, 1.75)
    fl = flicker_val(t, 0.65, seed=9) * (1 - K.ease_in(slam))
    if t < 1.4:
        fl = flicker_val(t, 0.65 * (1 - 0.4 * c.seg(0.6, 1.4)), seed=9)
    shake = 9 * (1 - K.smooth(c.seg(1.75, 2.4))) if t > 1.75 else 0
    with cam(cv, 960, 560, 1.0, shake=shake, t=t):
        WL.draw_wall(cv, t, time="night", flicker=fl)
        _wall_kids(cv, c, light_amt=1.0,
                   meher_kw=dict(expr="surprised" if 1.75 < t < 3 else "determined", look=(0.2, -0.5)),
                   kabir_kw=dict(expr="surprised" if 1.75 < t < 3 else "sad", hold_l=None,
                                 arms={"l": (10, 20), "r": (12, 40)}, extra={"crystal": 1.0, "crystal_wrist": 1.0}),
                   dog_kw=dict(mode="stand", ear=1.0 if t > 1.75 else 0.4, expr="alert"))
    if 1.75 < t < 2.3:
        fx.flash(cv, "#fff1d0", 0.55 * (1 - c.seg(1.75, 2.3)))
        fx.sparkles(cv, t, 960, 560, spread=380, n=26, color="gold", size=8, seed=13, a=1 - c.seg(1.75, 2.3))


def s25(cv, c):
    # the dark gali. small figures. silence.
    t = c.t
    with cam(cv, 960, 560, K.lerp(1.0, 0.97, c.u), t=t):
        GA.draw_gali(cv, t, time="night")
        y, s = GA.gali_ground(0.78)
        with K.lit(cv, "night"):
            chars.draw(cv, "meher", x=GA.gali_x(0.78, -0.25), y=y, s=s, t=t, expr="determined", turn=0.1)
            chars.draw(cv, "kabir", x=GA.gali_x(0.78, 0.3), y=y, s=s, t=t, expr="sad", flip=True, turn=0.1,
                       extra={"crystal": 1.0, "crystal_wrist": 1.0})
            A.draw_dog(cv, A.DogPose(x=GA.gali_x(0.78, -0.75), y=y, s=s * 0.72, mode="sit", t=t, expr="sad", ear=0.3))


SHOTS = [
    Shot("S07_SH01", s01, duration=7.5, music="fading", transition="fade_black", trans_dur=1.2,
         sfx=[bed("night_bed", 6.5, -20), Sfx("crickets_bed", 0, -24, dur=6.5)]),
    Shot("S07_SH02", s02, duration=4.6, sfx=[bed("night_bed", 4.6, -20)]),
    Shot("S07_SH03", s03, lines=[Line("nani", "Gloves? In this heat?", at=0.6)], tail=1.6,
         sfx=[bed("night_bed", 5.0, -20)]),
    Shot("S07_SH04", s04, lines=[Line("kabir", "It's... fashion.", at=0.4)], tail=2.4,
         sfx=[bed("night_bed", 5.0, -20)]),
    Shot("S07_SH05", s05, duration=5.0, sfx=[bed("night_bed")]),
    Shot("S07_SH05B", s05b, duration=4.2, sfx=[bed("night_bed")]),
    Shot("S07_SH06", s06, duration=7.0, music="", transition="fade_black", trans_dur=1.4,
         sfx=[bed("night_bed", 6.0, -16), Sfx("dog_whine", 4.0, -14)]),
    Shot("S07_SH07", s07, duration=5.5, sfx=[bed("night_bed", 5.5, -16), Sfx("footsteps_soft", 0.3, -14, dur=3.2)]),
    Shot("S07_SH08", s08, duration=8.0, music="low_point", music_hits=[1.6],
         sfx=[bed("night_bed", 8.0, -18), Sfx("clock_strike", 0.0, -8, params={"n": 3, "interval": 1.5}),
              Sfx("shop_flicker", 1.8, -8, dur=6.0)]),
    Shot("S07_SH09", s09, duration=4.2, sfx=[bed("night_bed", 4.2, -18), Sfx("shop_flicker", 0, -10, dur=4.2)]),
    Shot("S07_SH09B", s09b, duration=5.0, sfx=[bed("night_bed"), Sfx("shop_flicker", 0, -12, dur=5.0), Sfx("footsteps_soft", 0.4, -16, dur=4.0)]),
    Shot("S07_SH10", s10, duration=6.0, transition="dissolve", trans_dur=0.8,
         sfx=[bed("crickets_bed", 6.0, -26), Sfx("floor_creak", 1.2, -12), Sfx("shop_flicker", 0, -18, dur=6.0)]),
    Shot("S07_SH11", s11, lines=[Line("amma", "Ah. Both of you.", at=1.0)], tail=2.0,
         sfx=[bed("crickets_bed", 5.0, -26)]),
    Shot("S07_SH12", s12, lines=[Line("kabir", "I took it. I wanted them to think I was... somebody.", at=1.6)],
         tail=2.2, sfx=[bed("crickets_bed", 9.0, -26), Sfx("tola_tink", 0.9, -16)]),
    Shot("S07_SH13", s13, duration=4.8, sfx=[bed("crickets_bed", 4.8, -26), Sfx("crystal_tink", 2.3, -8),
                                              Sfx("crystal_spread", 2.4, -14)]),
    Shot("S07_SH14", s14, lines=[Line("kabir", "I'm sorry.", at=0.8)], tail=2.6,
         sfx=[bed("crickets_bed", 4.0, -26)]),
    Shot("S07_SH15", s15, lines=[Line("amma", "Oh, little man.", at=0.6)], tail=2.2,
         sfx=[bed("crickets_bed", 4.0, -26)]),
    Shot("S07_SH16", s16, lines=[Line("kabir", "Then take my sorry.", at=0.6)], duration=8.6,
         sfx=[bed("crickets_bed", 8.6, -26), Sfx("bubble_rise", 3.6, -10), Sfx("bubble_fizzle", 6.0, -8),
              Sfx("tola_tink", 4.8, -18)]),
    Shot("S07_SH16B", s16b, duration=3.6, sfx=[bed("crickets_bed", None, -26), Sfx("tola_clank", 0.5, -16), Sfx("tola_tink", 1.3, -18)]),
    Shot("S07_SH17", s17, duration=4.6, sfx=[bed("crickets_bed", 4.6, -26)]),
    Shot("S07_SH18", s18, lines=[Line("meher", "Amma, why are you fading?", at=0.7)], tail=1.8,
         sfx=[bed("crickets_bed", 4.5, -26)]),
    Shot("S07_SH19", s19, lines=[Line("amma", "A shop like this lives in people's remembering. When the last one forgets...", at=0.6)],
         tail=1.8, sfx=[bed("crickets_bed", 9.0, -26)]),
    Shot("S07_SH20", s20, lines=[Line("amma", "...poof. Sugar in the rain.", at=0.7)], tail=2.6,
         sfx=[bed("crickets_bed", 5.5, -26), Sfx("sparkle", 0.8, -14)]),
    Shot("S07_SH21", s21, lines=[Line("meher", "Nani's story. She forgot the ending... and you started to fade.", at=2.4)],
         tail=1.8, sfx=[bed("crickets_bed", 9.0, -26)]),
    Shot("S07_SH22", s22, lines=[Line("amma", "Who's Nani?", at=0.7)], tail=2.2, sfx=[bed("crickets_bed", 4.0, -26)]),
    Shot("S07_SH23", s23, lines=[Line("meher", "We need Nani.", at=0.9)], tail=1.6,
         sfx=[bed("crickets_bed", 3.5, -26)]),
    Shot("S07_SH24", s24, duration=4.8, sfx=[bed("night_bed", 4.8, -18), Sfx("shop_flicker", 0, -10, dur=1.6),
                                              Sfx("shop_shut", 1.62, -2)]),
    Shot("S07_SH25", s25, duration=5.5, music="", sfx=[bed("night_bed", 4.5, -18)]),
]

fit_beds(SHOTS)
