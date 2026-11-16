"""Scene 8: CLIMAX (15:00-17:30).

Waking Nani -> Kabir guides her down the dark stairs, one step at a time -> the wall: Nani's palm,
the hum, the wall hums back -> the memory: young Sharda sang Amma back -> 'I was the girl' ->
THE BLAZE: shop back in full colour, Amma solid -> Kabir's real kindness weighs heaviest of all,
the crystal melts -> 'Now that... is heavy.' -> Chutney howls, badly.
"""
from __future__ import annotations

import math

import skia

from .. import core as K, fx
from ..core import W, H, fill, stroke, ellipse
from ..rig import chars, animals as A
from ..sets import rooftop as RT, wall as WL, shop as SH, stairwell as ST
from ..timeline import Shot, Line, Sfx
from ._util_c import (cam, fit_beds, bed, pan_pos, reach, shoulder, amma, flicker_val, tola, torch_light)

TX, TY, TS = SH.ANCHORS["counter"]["tola"]
AX, AY, AS = SH.ANCHORS["counter"]["amma"]
CRY = {"crystal": 1.0, "crystal_wrist": 1.0}


# ================================================================== rooftop: waking Nani
NB = RT.BEDS["nani"]


def _roof(cv, c, nani_sleep=True, nani_kw=None, meher_kw=None, kabir_kw=None, kabir_xy=(820, 905)):
    t = c.t
    RT.draw_rooftop(cv, t, time="night", lantern=0.7, beds=False)
    for k in ("meher", "kabir"):
        x, y = RT.BEDS[k]
        RT.draw_charpai(cv, x, y, RT.BED_S[k])
    d = RT.draw_charpai(cv, NB[0], NB[1], 1.0)
    sx, sy = d["surface"]
    if nani_sleep:
        RT.draw_sleeper(cv, sx, sy, 1.0, t, "nani")
    with K.lit(cv, "moon"):
        if not nani_sleep:
            nk = dict(x=sx - 70, y=sy + 8, s=1.32, legs="sit", t=t, turn=0.5, mouth=c.mouth("nani"))
            nk.update(nani_kw or {})
            chars.draw(cv, "nani", **nk)
        mk = dict(x=sx + 120, y=sy + 8, s=1.32, legs="sit", t=t, flip=True, turn=0.6, expr="determined",
                  look=(0.7, 0.4), mouth=c.mouth("meher"))
        mk.update(meher_kw or {})
        chars.draw(cv, "meher", **mk)
        kk = dict(x=kabir_xy[0], y=kabir_xy[1], s=1.32, t=t, flip=True, turn=0.55, expr="worried",
                  look=(0.8, 0.5), extra=dict(CRY), mouth=c.mouth("kabir"))
        kk.update(kabir_kw or {})
        chars.draw(cv, "kabir", **kk)


def s01(cv, c):
    # near midnight. Everyone else asleep. Two kids at Nani's bed.
    with cam(cv, 700, 640, K.lerp(1.15, 1.3, K.ease_in_out(c.u)), t=c.t):
        _roof(cv, c, meher_kw=dict(expr="worried", arms={"r": (40, 70)}))


def s02(cv, c):
    # Meher, close: "Nani. Wake up. It's your story. It's real."
    with cam(cv, 560, 700, K.lerp(2.2, 2.3, c.u), t=c.t):
        nudge = math.sin(c.t * 7) * 6 * K.seg(c.t, 0.4, 0.6) * (1 - K.seg(c.t, 1.2, 1.4))
        _roof(cv, c, meher_kw=dict(expr="determined", arms={"r": (55 + nudge, 40)}, look=(0.8, 0.5)))


def s03(cv, c):
    # Nani sits up, blinking, gentle and confused: "At my age? Down all those stairs?"
    rise = K.ease_out(c.seg(0.0, 1.4))
    expr = "sleepy" if c.t < 1.6 else "surprised" if c.t < 2.4 else "worried"
    with cam(cv, 470, 690, K.lerp(2.1, 2.15, c.u), t=c.t):
        _roof(cv, c, nani_sleep=False,
              nani_kw=dict(lean=K.lerp(-62, 0, rise), expr=expr, look=(0.7, 0.0), head_tilt=6 * (1 - rise),
                           extra={"no_specs": c.t < 1.4}),
              meher_kw=dict(expr="happy" if c.t < 3 else "determined", look=(0.8, 0.3)))


def s04(cv, c):
    # Kabir picks up the torch: "I'll take you, Nani."
    pick = K.smooth(c.seg(0.2, 1.2))
    with cam(cv, 700, 640, K.lerp(1.8, 1.9, c.u), t=c.t):
        _roof(cv, c, nani_sleep=False,
              nani_kw=dict(expr="surprised" if c.t > 2.6 else "worried", look=(1.0, -0.2), turn=0.7),
              meher_kw=dict(expr="happy", look=(1.0, -0.3)),
              kabir_xy=(830, 905),
              kabir_kw=dict(expr="determined", look=(-0.6, 0.1), turn=0.4, hold_l="torch" if pick > 0.5 else None,
                            arms={"l": (K.lerp(10, 40, pick), K.lerp(10, 70, pick)), "r": (10, 20)}))


# ================================================================== the stairs
def _sp(f):
    f = K.clamp(f, 0, len(ST.STEPS) - 1)
    i = int(f)
    u = f - i
    a = ST.STEPS[i]
    b = ST.STEPS[min(i + 1, len(ST.STEPS) - 1)]
    e = K.ease_in_out(u)
    lift = math.sin(u * math.pi) * 14
    return K.lerp(a[0], b[0], e), K.lerp(a[1], b[1], e) - lift


def _patient(t, start, period=2.2, move=0.75):
    """Step index progress: one step... wait... one step."""
    if t < 0:
        return start
    n = int(t // period)
    r = (t % period) / period
    return start + n + K.clamp(r / move)


def _stairs(cv, c, kf, nf, mf, s=ST.CHAR_S, kabir_kw=None, nani_kw=None, meher_kw=None, torch_ang=205,
            dark=True):
    t = c.t
    ST.draw_stairwell(cv, t, light="torch")
    kx, ky = _sp(kf)
    nx, ny = _sp(nf)
    mx, my = _sp(mf)
    ksx, ksy = shoulder("kabir", kx, ky, s, "r", flip=True)
    nsx, nsy = shoulder("nani", nx, ny, s, "r")
    midx, midy = (ksx + nsx) / 2, (ksy + nsy) / 2 + 50
    ka = reach(ksx, ksy, midx, midy, "r", flip=True)
    na = reach(nsx, nsy, midx, midy, "r")
    mk = dict(x=mx, y=my, s=s, t=t, hold="slippers", arms={"r": (40, 60)}, expr="happy", look=(0.7, 0.4),
              mouth=c.mouth("meher"))
    mk.update(meher_kw or {})
    chars.draw(cv, "meher", **mk)
    nk = dict(x=nx, y=ny, s=s, t=t, arms={"r": (na, 0)}, expr="neutral", look=(0.6, 0.7), mouth=c.mouth("nani"))
    nk.update(nani_kw or {})
    chars.draw(cv, "nani", **nk)
    kk = dict(x=kx, y=ky, s=s, t=t, flip=True, arms={"r": (ka, 0), "l": (150, 20)}, hold_l="torch",
              extra=dict(CRY), expr="determined", look=(0.2, 0.5), mouth=c.mouth("kabir"))
    kk.update(kabir_kw or {})
    chars.draw(cv, "kabir", **kk)
    if dark:
        tsx, tsy = shoulder("kabir", kx, ky, s, "l", flip=True)
        tx_, ty_ = tsx + 57 * s, tsy - 116 * s
        ang = math.degrees(math.atan2(ny - 10 - ty_, nx - 60 * s - tx_))
        torch_light(cv, t, tx_, ty_, ang)
    return (kx, ky), (nx, ny)


def s05(cv, c):
    # wide: the dark staircase. Kabir walks BACKWARDS, torch up, holding Nani's hand. One step. Wait.
    t = c.t
    kf = _patient(t - 0.5, 4.0)
    kx, ky = _sp(kf)
    with cam(cv, kx - 120, ky - 170, K.lerp(1.12, 1.18, c.u), t=t):
        _stairs(cv, c, kf, kf - 1.5, kf - 3.4)


def s06(cv, c):
    # closer: Kabir's face in the torchlight, waiting. Nani's foot finds the next step.
    t = c.t
    kf = _patient(t, 6.0, period=2.4)
    kx, ky = _sp(kf)
    with cam(cv, kx - 90, ky - 260, K.lerp(2.2, 2.3, c.u), t=t):
        _stairs(cv, c, kf, kf - 1.5, kf - 3.4,
                kabir_kw=dict(expr="determined" if (t % 2.4) / 2.4 < 0.4 else "happy", look=(0.0, 0.7)))


def s07(cv, c):
    # "One more, Nani. I've got you."
    t = c.t
    kf = _patient(t - 1.5, 8.0, period=2.6)
    kx, ky = _sp(kf)
    with cam(cv, kx - 120, ky - 250, K.lerp(1.8, 1.85, c.u), t=t):
        _stairs(cv, c, kf, kf - 1.5, kf - 3.4,
                kabir_kw=dict(expr="happy", look=(-0.3, 0.3), turn=0.5),
                nani_kw=dict(expr="happy" if t > 3 else "neutral", look=(0.6, 0.2)))


def s08(cv, c):
    # Meher behind, carrying Nani's slippers like treasure
    t = c.t
    kf = _patient(t, 9.0, period=2.6)
    mx, my = _sp(kf - 3.4)
    with cam(cv, mx + 40, my - 230, K.lerp(2.3, 2.4, c.u), t=t):
        _stairs(cv, c, kf, kf - 1.5, kf - 3.4,
                meher_kw=dict(expr="happy", look=(0.8, 0.6), arms={"r": (50, 75), "l": (45, 80)}, head_tilt=-5))


def s09(cv, c):
    # the bottom: the street door. They made it. Kabir lets out a breath.
    t = c.t
    kf = K.lerp(10.0, 12.0, K.ease_in_out(c.seg(0.2, 3.0)))
    with cam(cv, 1100, 620, K.lerp(1.3, 1.25, c.u), t=t):
        _stairs(cv, c, kf, kf - 1.4, kf - 3.0, kabir_kw=dict(expr="happy" if t > 3 else "determined"),
                nani_kw=dict(expr="happy" if t > 3.2 else "neutral"), torch_ang=200)


# ================================================================== the wall: the hum
NANI_WX, MEHER_WX, KABIR_WX, DOG_WX = 960, 640, 1290, 470


def _wall_people(cv, c, nani_x=NANI_WX, nani_kw=None, meher_kw=None, kabir_kw=None, dog_kw=None,
                 light="night", amount=1.0, nani=True):
    t = c.t
    with K.lit(cv, light, amount=amount):
        dk = dict(x=DOG_WX, y=WL.FLOOR_Y, s=WL.DOG_S, mode="sit", t=t, ear=0.6, look_up=0.3)
        dk.update(dog_kw or {})
        A.draw_dog(cv, A.DogPose(**dk))
        mk = dict(x=MEHER_WX, y=WL.FLOOR_Y, s=WL.CHAR_S, t=t, turn=0.5, expr="worried", hold="slippers",
                  arms={"r": (40, 60)}, look=(0.6, -0.2), mouth=c.mouth("meher"))
        mk.update(meher_kw or {})
        chars.draw(cv, "meher", **mk)
        kk = dict(x=KABIR_WX, y=WL.FLOOR_Y, s=WL.CHAR_S, t=t, flip=True, turn=0.5, expr="worried",
                  hold_l="torch", arms={"l": (20, 40)}, extra=dict(CRY), look=(0.6, -0.2), mouth=c.mouth("kabir"))
        kk.update(kabir_kw or {})
        chars.draw(cv, "kabir", **kk)
        if nani:
            nk = dict(x=nani_x, y=WL.FLOOR_Y, s=WL.CHAR_S * 1.02, t=t, turn=0.2, expr="neutral",
                      look=(0.0, -0.4), mouth=c.mouth("nani"))
            nk.update(nani_kw or {})
            chars.draw(cv, "nani", **nk)


def s10(cv, c):
    # midnight strikes; the faintest flicker. Nani stares at the peeling blue paint.
    t = c.t
    fl = flicker_val(t, 0.25 * K.smooth(c.seg(2.0, 3.5)), seed=21) if t > 2 else 0
    with cam(cv, 960, 560, K.lerp(1.0, 1.07, K.ease_in_out(c.u)), t=t):
        WL.draw_wall(cv, t, time="night", flicker=fl)
        _wall_people(cv, c, nani_kw=dict(expr="neutral", look=(0.0, -0.6)))


def _palm(cv, x, y, s=1.0, a=1.0):
    """Nani's palm pressed flat on the wall (insert), with silver bangles."""
    skin = "#b77b55"
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    pt = skia.Paint(); pt.setAlphaf(a); cv.saveLayer(None, pt)
    # forearm from below
    arm = K.limb(30, 240, 6, 40, 70, 58)
    cv.drawPath(arm, fill(K.shade(skin, -0.05))); cv.drawPath(arm, stroke("line", 4))
    cv.drawPath(K.rrect(-40, 120, 92, 50, 18), fill("#d6c8ef")); cv.drawPath(K.rrect(-40, 120, 92, 50, 18), stroke("line", 4))
    for k in range(3):
        cv.drawOval(skia.Rect.MakeLTRB(-30, 70 + k * 14, 46, 90 + k * 14), stroke("bangle", 6))
    palm = K.smooth_path([(-34, 30), (-40, -30), (-20, -50), (20, -50), (40, -24), (36, 30), (0, 46)], tension=0.5)
    cv.drawPath(palm, fill(skin)); cv.drawPath(palm, stroke("line", 4))
    for i, (fx_, fy_, ln) in enumerate([(-30, -44, 54), (-10, -50, 70), (10, -50, 74), (28, -44, 60)]):
        f = K.limb(fx_, fy_, fx_ - 4 + i * 2, fy_ - ln, 18, 15)
        cv.drawPath(f, fill(skin)); cv.drawPath(f, stroke("line", 4))
    th = K.limb(-34, 6, -76, -30, 20, 16)
    cv.drawPath(th, fill(skin)); cv.drawPath(th, stroke("line", 4))
    cv.restore(); cv.restore()


def s11(cv, c):
    # Nani steps forward and reaches out to the wall
    t = c.t
    k = K.ease_in_out(c.seg(0.3, 3.0))
    reach_k = K.smooth(c.seg(2.4, 3.8))
    with cam(cv, 960, K.lerp(520, 470, k), K.lerp(1.15, 1.5, k), t=t):
        WL.draw_wall(cv, t, time="night", flicker=flicker_val(t + 4, 0.22, seed=21))
        _wall_people(cv, c, nani_x=K.lerp(NANI_WX, 900, k),
                     nani_kw=dict(legs="walk" if 0.3 < t < 3.0 else "stand", phase=t * 0.5, turn=K.lerp(0.2, 0.9, k),
                                  look=(0.8, -0.6), expr="neutral",
                                  arms={"r": (K.lerp(10, 150, reach_k), K.lerp(10, 40, reach_k))}, hand={"r": "open"}))


def s12(cv, c):
    # INSERT: the palm on the peeling wall. She hums. The wall hums back: golden ripples.
    t = c.t
    px, py = 960, 560
    with cam(cv, px, py - 40, K.lerp(3.0, 3.15, c.u), t=t):
        WL.draw_wall(cv, t, time="night", glow=0.12 * K.smooth(c.seg(4.0, 8.0)))
    _palm(cv, 980, 600, 1.4, a=K.smooth(c.seg(0.2, 0.8)))
    for i, t0 in enumerate([3.6, 4.3, 5.0, 5.8, 6.5, 7.2]):
        fx.chime_rings(cv, 960, 520, t0, t, color="gold", n=2, max_r=520, a=0.55)
    fx.glow_dot(cv, 960, 520, 360, "gold", 0.18 * K.smooth(c.seg(3.5, 7.5)))
    fx.sparkles(cv, t, 960, 520, spread=300, n=14, color="gold", size=6, seed=31, a=K.smooth(c.seg(4.5, 7.5)))


def _memory_inner(t):
    """The same wall, eighty years ago: young Sharda sings; the fading shop glows back; Amma returns."""
    def f(cv):
        back = K.smooth(K.seg(t, 4.0, 9.0))
        if back < 0.02:
            WL.draw_wall(cv, t, time="night", flicker=flicker_val(t, 0.55, seed=41))
        else:
            WL.draw_wall(cv, t, time="night", unfold=K.lerp(0.25, 1.0, back))
        with K.lit(cv, "night", amount=0.5 * (1 - back)):
            chars.draw(cv, "young_sharda", x=620, y=WL.FLOOR_Y, s=WL.CHAR_S, t=t, turn=0.7, expr="happy",
                       look=(0.9, -0.2), mouth=0.35 + 0.35 * math.sin(t * 5.5) if 1.0 < t < 8.5 else 0.0,
                       arms={"l": (20, 40), "r": (30, 60)})
        amma(cv, 1000, WL.FLOOR_Y, WL.CHAR_S, t, alpha=K.lerp(0.25, 1.0, back), desat=K.lerp(0.8, 0.0, back),
             light="shop", specs_boost=0.6 * (1 - back), sparkle=1 - back, flip=True, turn=0.6,
             expr="happy" if back > 0.5 else "sad", look=(0.8, -0.1))
    return f


def s13(cv, c):
    # a big sepia-gold bubble rises from her palm: the memory
    t = c.t
    grow = K.ease_out(c.seg(0.0, 2.5))
    y = K.lerp(640, 470, K.ease_in_out(c.seg(0.0, 4.0)))
    with cam(cv, 960, 520, K.lerp(1.6, 1.45, c.u), t=t):
        WL.draw_wall(cv, t, time="night", glow=0.15)
    _palm(cv, 980, 980, 1.2, a=1 - K.smooth(c.seg(1.0, 3.0)))
    fx.light_rays(cv, 960, y, -90, 360, 900, "gold", a=0.1 * grow, n=12, t=t)
    fx.memory_bubble(cv, 960, y, 300 * grow + 2, t, _memory_inner(t), light="memory", a=grow, color="gold")


def s14(cv, c):
    # CU Nani, lit gold by the bubble: "I was the girl. I was the girl in the story."
    t = c.t
    with cam(cv, 905, 530, K.lerp(2.5, 2.65, c.u), t=t):
        WL.draw_wall(cv, t, time="night", glow=0.15)
        with K.lit(cv, "shop", amount=0.65):
            chars.draw(cv, "nani", x=900, y=WL.FLOOR_Y, s=WL.CHAR_S * 1.02, t=t, turn=0.35,
                       expr="awe" if t < 1.2 else "cry" if t > 4.6 else "happy", look=(0.3, -0.7),
                       mouth=c.mouth("nani"), head_tilt=-4, arms={"r": (30, 120)})
    fx.glow_dot(cv, 1300, 120, 520, "gold", 0.35)
    fx.sparkles(cv, t, 1200, 250, spread=260, n=12, color="gold", size=6, seed=7)


def s15(cv, c):
    # the bubble drifts into the wall... and the wall BLAZES: the shop unfolds, faster and brighter than ever
    t = c.t
    bub = c.seg(0.0, 2.0)
    unf = K.smooth(c.seg(2.0, 6.0))
    flash_a = math.exp(-((t - 2.0) / 0.35) ** 2) * 0.9
    with cam(cv, 960, 540, K.lerp(1.15, 1.0, K.ease_out(c.seg(1.8, 5.0))), shake=6 * flash_a, t=t):
        WL.draw_wall(cv, t, time="night", glow=K.lerp(0.4, 1.0, bub) if t < 2.0 else 0.0, unfold=unf)
        _wall_people(cv, c, light="night", amount=1 - 0.75 * unf,
                     nani_kw=dict(expr="awe", look=(0.0, -0.5), turn=0.3, arms={"r": (40, 60)}),
                     meher_kw=dict(expr="awe", look=(0.5, -0.5)), kabir_kw=dict(expr="awe", look=(-0.5, -0.5)),
                     dog_kw=dict(ear=1.0, expr="alert", look_up=0.6, wag=1.6))
    if t < 2.2:
        r = K.lerp(220, 30, K.ease_in(bub))
        fx.bubble(cv, 960, K.lerp(420, 600, K.ease_in(bub)), r, "gold", a=1 - c.seg(1.8, 2.2), t=t)
    fx.flash(cv, "#fff1c8", flash_a)
    fx.sparkles(cv, t, 960, 520, spread=600, n=40, color="gold", size=9, seed=17, a=unf)
    fx.light_rays(cv, 960, 560, 90, 160, 900, "gold", a=0.18 * unf, n=9, t=t)


# ================================================================== inside: the blaze
def _shop(cv, c, prog, view="counter", amma_kw=None, tola_kw=None, people=None, amma_on=True):
    """prog 0..1: from faded/bare to blazing/full."""
    t = c.t
    fade = K.lerp(0.74, 0.0, prog)
    full = K.lerp(0.15, 1.0, prog)
    blaze = prog
    SH.draw_shop(cv, t, view=view, fullness=full, fade=fade, blaze=blaze)
    if amma_on:
        ax, ay, asc = SH.ANCHORS[view]["amma"]
        ak = dict(turn=0.3, expr="happy", mouth=c.mouth("amma"))
        ak.update(amma_kw or {})
        amma(cv, ax, ay, asc, t, alpha=K.lerp(0.25, 1.0, prog), desat=K.lerp(0.8, 0.0, prog),
             specs_boost=0.7 * (1 - prog), sparkle=1 - prog, **ak)
    SH.draw_counter_front(cv, t, view, fade=fade, blaze=blaze)
    tx, ty, ts = SH.ANCHORS[view]["tola"]
    tk = dict(tarnish=K.lerp(0.8, 0.0, prog), shine=prog, eyes="happy" if prog > 0.6 else "half",
              mouth="smile" if prog > 0.6 else "line")
    tk.update({k: v for k, v in (tola_kw or {}).items() if v is not None})
    tola(cv, tx, ty, ts, t, **tk)
    if people:
        with K.lit(cv, "shop", amount=K.lerp(0.3, 1.0, prog)):
            people(cv)


def s16(cv, c):
    # the bubble settles onto Tola's pan: CLONNNG. Lanterns flare, jars refill, colour floods back.
    t = c.t
    land = K.ease_in_out(c.seg(0.0, 1.6))
    tilt = -14 * K.ease_out_elastic(c.seg(1.6, 2.6))
    prog = K.smooth(c.seg(1.8, 5.0))
    lpx, lpy = pan_pos(TX, TY, TS, "l", tilt)
    with cam(cv, 960, 520, K.lerp(1.25, 1.05, K.ease_out(c.seg(1.6, 6.0))), shake=5 * math.exp(-((t - 1.7) / 0.3) ** 2), t=t):
        _shop(cv, c, prog, tola_kw=dict(tilt=tilt, bubble_on="l" if t > 1.6 else None, bubble_r=30,
                                        eyes="wide" if 1.6 < t < 2.6 else None) if True else {},
              amma_kw=dict(expr="surprised" if t > 2.5 else "sad", look=(-0.6, 0.3)))
        if t <= 1.6:
            fx.bubble(cv, K.lerp(960, lpx, land), K.lerp(-60, lpy - 30, land), K.lerp(70, 30, land), "gold", t=t)
        for i, t0 in enumerate([1.65, 2.5, 3.1, 3.7, 4.3]):
            fx.chime_rings(cv, lpx if i == 0 else 300 + i * 330, lpy if i == 0 else 300, t0, t, "gold", n=2, max_r=180)
    fx.flash(cv, "#fff1c8", 0.6 * math.exp(-((t - 1.75) / 0.4) ** 2))
    fx.sparkles(cv, t, 960, 450, spread=800, n=60, color="gold", size=8, seed=23, a=prog)
    fx.motes(cv, t, (0, 0, W, H), n=50, color="#ffe7a8", a=0.6 * prog, seed=4)


def _tola_eyes_fix(kw):
    return {k: v for k, v in kw.items() if v is not None}


def s17(cv, c):
    # Amma is SOLID. A gasp. She looks at her own hands. And laughs.
    t = c.t
    look_hands = K.smooth(c.seg(0.6, 1.4)) * (1 - K.smooth(c.seg(3.0, 3.6)))
    expr = "surprised" if t < 1.2 else "awe" if t < 3.0 else "laugh"
    with cam(cv, AX - 40, AY - 280, K.lerp(1.75, 1.85, c.u), t=t):
        _shop(cv, c, 1.0, tola_kw=dict(tilt=-14),
              amma_kw=dict(expr=expr, look=(0.0, 0.9 * look_hands), head_tilt=8 * look_hands - 4 * (t > 3) *
                           math.sin(t * 9),
                           arms={"l": (K.lerp(10, 40, look_hands), K.lerp(10, 120, look_hands)),
                                 "r": (K.lerp(10, 40, look_hands), K.lerp(10, 120, look_hands))}))
    fx.sparkles(cv, t, AX, AY - 300, spread=260, n=16, color="gold", size=7, seed=29)


NANI_CX, NANI_CY = 360, 1160


def _nani_cust(c, **kw):
    t = c.t

    def f(cv):
        d = dict(x=NANI_CX, y=NANI_CY, s=1.95, t=t, turn=0.7, expr="happy", look=(0.9, -0.4), mouth=c.mouth("nani"))
        d.update(kw)
        chars.draw(cv, "nani", **d)
    return f


def s18(cv, c):
    # two-shot: Amma and Nani. "There you are, Sharda."
    t = c.t
    with cam(cv, 860, 560, K.lerp(1.08, 1.14, c.u), t=t):
        _shop(cv, c, 1.0, tola_kw=dict(tilt=-14),
              amma_kw=dict(expr="happy", look=(-0.9, 0.3), turn=0.1, head_tilt=-6,
                           arms={"l": (30, 60), "r": (30, 60)}),
              people=_nani_cust(c, expr="cry" if t > 2.4 else "awe"))


def s19(cv, c):
    # CU Nani: "I forgot you."
    t = c.t
    with cam(cv, NANI_CX + 60, NANI_CY - 470, K.lerp(2.3, 2.4, c.u), t=t):
        _shop(cv, c, 1.0, tola_kw=dict(tilt=-14), amma_on=True,
              people=_nani_cust(c, expr="cry", look=(0.9, -0.3), head_tilt=-5))


def s20(cv, c):
    # CU Amma, warm: "Everybody forgets. The trick is remembering again."
    t = c.t
    with cam(cv, AX - 50, AY - 290, K.lerp(1.9, 2.0, c.u), t=t):
        _shop(cv, c, 1.0, tola_kw=dict(tilt=-14),
              amma_kw=dict(expr="happy", look=(-0.8, 0.3), turn=0.15, head_tilt=-5 + math.sin(t * 1.4) * 2))


KAB_X, KAB_Y = 410, 1085


def _kabir_at_counter(c, arm=None, expr="worried", crystal=1.0, wrist=1.0, look=(0.8, -0.5), extra_people=True,
                      head_tilt=0.0, hand="open"):
    t = c.t

    def f(cv):
        if extra_people:
            chars.draw(cv, "nani", x=150, y=1180, s=1.9, t=t, turn=0.6, expr="happy", look=(0.9, -0.3))
        chars.draw(cv, "kabir", x=KAB_X, y=KAB_Y, s=1.9, t=t, turn=0.6, expr=expr, look=look,
                   head_tilt=head_tilt, arms={"r": arm or (12, 30), "l": (8, 10)}, hand={"r": hand},
                   extra={"crystal": crystal, "crystal_wrist": wrist}, mouth=c.mouth("kabir"))
    return f


def _kabir_reach_arm(tilt):
    lpx, lpy = pan_pos(TX, TY, TS, "l", tilt)
    sx, sy = shoulder("kabir", KAB_X, KAB_Y, 1.9, "r")
    return reach(sx, sy, lpx, lpy - 4, "r"), (lpx, lpy)


def _tonight_inner(t):
    """Inside Kabir's bubble: tonight's dark stairs, one step at a time."""
    def f(cv):
        ST.draw_stairwell(cv, t, light="torch")
        kf = _patient(t, 6.0, period=1.6)
        kx, ky = _sp(kf)
        nx, ny = _sp(kf - 1.5)
        chars.draw(cv, "nani", x=nx, y=ny, s=ST.CHAR_S, t=t, arms={"r": (30, 0)}, look=(0.6, 0.6))
        chars.draw(cv, "kabir", x=kx, y=ky, s=ST.CHAR_S, t=t, flip=True, hold_l="torch",
                   arms={"r": (40, 0), "l": (150, 20)}, extra=dict(CRY), expr="happy")
        tsx, tsy = shoulder("kabir", kx, ky, ST.CHAR_S, "l", flip=True)
        tx_, ty_ = tsx + 57 * ST.CHAR_S, tsy - 116 * ST.CHAR_S
        torch_light(cv, t, tx_, ty_, math.degrees(math.atan2(ny - ty_, nx - 70 - tx_)))
    return f


def s21(cv, c):
    # Kabir steps up and lays his crystal hand on the pan. A bubble rises: tonight.
    t = c.t
    ang, (lpx, lpy) = _kabir_reach_arm(0)
    rk = K.smooth(c.seg(0.6, 2.0))
    with cam(cv, 700, 520, K.lerp(1.25, 1.35, c.u), t=t):
        _shop(cv, c, 1.0, tola_kw=dict(tilt=0, eyes="open", mouth="o" if t > 3 else "line"),
              amma_kw=dict(expr="happy", look=(-0.9, 0.4)),
              people=_kabir_at_counter(c, arm=(K.lerp(12, ang, rk), K.lerp(30, 0, rk)), expr="worried" if t < 2.4
                                       else "awe"))
        grow = K.ease_out(c.seg(2.4, 4.0))
        rise = K.ease_in_out(c.seg(2.4, 5.0))
        if t > 2.4:
            fx.memory_bubble(cv, lpx + 20, lpy - 60 - 170 * rise, 120 * grow + 1, t, _tonight_inner(t), light="memory",
                             a=grow, color="gold")


def s22(cv, c):
    # it drops onto the pan: Tola tips ALL the way down. THUNK. The jars ring like temple bells.
    t = c.t
    drop = K.ease_in(c.seg(0.0, 0.7))
    tilt = -27 * K.ease_out_elastic(c.seg(0.7, 1.8)) if t > 0.7 else 0
    ang, (lpx, lpy) = _kabir_reach_arm(tilt)
    hit = math.exp(-((t - 0.75) / 0.25) ** 2)
    with cam(cv, 720, 500, K.lerp(1.4, 1.3, c.u), shake=12 * hit, t=t):
        _shop(cv, c, 1.0, tola_kw=dict(tilt=tilt, eyes="wide" if t > 0.7 else "open", mouth="o",
                                        bubble_on="l" if t > 0.7 else None, bubble_r=34, shine=1.0),
              amma_kw=dict(expr="surprised" if t < 2 else "happy", look=(-0.9, 0.4)),
              people=_kabir_at_counter(c, arm=(ang if t < 0.9 else 30, 0 if t < 0.9 else 40),
                                       expr="surprised", look=(0.7, -0.6)))
        if t < 0.75:
            fx.memory_bubble(cv, lpx + 20, K.lerp(lpy - 230, lpy - 34, drop), K.lerp(120, 40, drop), t,
                             _tonight_inner(t + 4), light="memory", a=1.0, color="gold")
        for i, t0 in enumerate([0.75, 1.0, 1.3, 1.7, 2.1, 2.6]):
            fx.chime_rings(cv, lpx if i < 2 else 150 + i * 300, lpy if i < 2 else 260 - (i % 2) * 120, t0, t, "gold",
                           n=3, max_r=260 if i < 2 else 160)
    fx.flash(cv, "#fff1c8", 0.5 * hit)
    fx.sparkles(cv, t, 960, 400, spread=800, n=40, color="gold", size=9, seed=33, a=K.smooth(c.seg(0.7, 1.4)))


def s23(cv, c):
    # CU: the crystal MELTS - wrist, knuckles, fingertips - until it's just a hand again
    t = c.t
    wrist = 1 - K.smooth(c.seg(0.6, 2.6))
    cry = 1 - K.smooth(c.seg(2.4, 4.6))
    lift = K.smooth(c.seg(0.2, 1.0))
    sx, sy = shoulder("kabir", KAB_X, KAB_Y, 1.9, "r")
    with cam(cv, KAB_X + 120, KAB_Y - 430, K.lerp(2.15, 2.3, c.u), t=t):
        _shop(cv, c, 1.0, tola_kw=dict(tilt=-27),
              people=_kabir_at_counter(c, arm=(K.lerp(30, 70, lift), K.lerp(40, 95, lift)), crystal=cry, wrist=wrist,
                                       expr="awe", look=(0.9, 0.5), extra_people=False))
    hx, hy = 960, 560
    if 0.6 < t < 5.0:
        fx.sparkles(cv, t, hx, hy, spread=140, n=18, color="#eaf7ff", size=7, seed=41, rise=1.0,
                    a=K.smooth(c.seg(0.6, 1.2)) * (1 - K.smooth(c.seg(4.4, 5.0))))


def s24(cv, c):
    # he flexes his hand, laughs, eyes wet
    t = c.t
    flex = (math.sin(t * 6) > 0)
    with cam(cv, KAB_X + 100, KAB_Y - 420, K.lerp(1.9, 1.95, c.u), t=t):
        _shop(cv, c, 1.0, tola_kw=dict(tilt=-27),
              people=_kabir_at_counter(c, arm=(70, 95), crystal=0, wrist=0, hand="fist" if flex and t < 2 else "open",
                                       expr="laugh" if t > 1.4 else "cry", look=(0.4, 0.3), extra_people=False,
                                       head_tilt=math.sin(t * 8) * 2 if t > 1.4 else 0))


def s25(cv, c):
    # Amma: "Now that... is heavy."
    t = c.t
    with cam(cv, AX - 140, AY - 250, K.lerp(1.55, 1.6, c.u), t=t):
        _shop(cv, c, 1.0, tola_kw=dict(tilt=-27, eyes="happy", mouth="grin"),
              amma_kw=dict(expr="happy" if t < 1.0 else "grin", look=(-0.9, 0.3), turn=0.2,
                           arms={"r": (40, 100)}, head_tilt=-6))


def s26(cv, c):
    # wide: everyone. Chutney throws back his head and howls along with the chimes. Badly.
    t = c.t
    v = "wide"
    howl = c.seg(0.8, 4.0) > 0 and t < 4.4
    with cam(cv, 900, 560, K.lerp(1.0, 1.06, c.u), t=t):
        def people(cv):
            cx, cy, cs = SH.ANCHORS[v]["customer"]
            dx, dy, ds = SH.ANCHORS[v]["dog"]
            chars.draw(cv, "nani", x=cx + 420, y=cy, s=cs, t=t, turn=0.6, expr="laugh" if howl else "happy",
                       look=(-0.6, 0.4))
            chars.draw(cv, "meher", x=cx + 60, y=cy + 6, s=cs, t=t, turn=0.4, expr="laugh" if t > 1.5 else "happy",
                       look=(-0.8, 0.5), hold="slippers", arms={"r": (40, 60)})
            chars.draw(cv, "kabir", x=cx + 240, y=cy, s=cs, t=t, flip=True, turn=0.4, expr="laugh" if t > 1.5 else
                       "happy", look=(0.8, 0.5), extra={"crystal": 0})
            A.draw_dog(cv, A.DogPose(x=dx - 60, y=dy + 20, s=ds * 1.1, t=t, mode="sit", look_up=1.0 if howl else 0.2,
                                     mouth=(0.6 + 0.3 * math.sin(t * 9)) if howl else 0.0, ear=1.0,
                                     expr="proud" if howl else "happy", wag=1.5))
        _shop(cv, c, 1.0, view=v, tola_kw=dict(tilt=-27, eyes="happy", mouth="grin"),
              amma_kw=dict(expr="laugh" if howl else "happy", look=(-0.6, 0.2)), people=people)
        if howl:
            dx, dy, ds = SH.ANCHORS[v]["dog"]
            dx -= 60
            for i in range(3):
                u = ((t - 0.8) * 0.8 + i / 3) % 1.0
                cv.save(); cv.translate(dx + 70 + u * 160, dy - 190 - u * 120); cv.rotate(-25)
                cv.drawPath(K.smooth_path([(-12, 0), (-4, -6), (4, 0), (12, -6)], close=False),
                            stroke("line", 3, 1 - u))
                cv.restore()


SHOTS = [
    # rooftop
    Shot("S08_SH01", s01, duration=5.5, transition="fade_black", trans_dur=1.2,
         sfx=[bed("night_bed", None, -18), Sfx("crickets_bed", 0, -24, dur=5.5)]),
    Shot("S08_SH02", s02, lines=[Line("meher", "Nani. Wake up. It's your story. It's real.", at=0.5)], tail=0.8,
         sfx=[bed("night_bed", None, -18)]),
    Shot("S08_SH03", s03, lines=[Line("nani", "At my age? Down all those stairs?", at=2.0)], tail=1.0,
         sfx=[bed("night_bed", None, -18)]),
    Shot("S08_SH04", s04, lines=[Line("kabir", "I'll take you, Nani.", at=1.5)], tail=1.6,
         sfx=[bed("night_bed", None, -18)]),
    # stairs
    Shot("S08_SH05", s05, duration=9.5, music="stairs_tender", transition="fade_black", trans_dur=0.8,
         sfx=[bed("crickets_bed", None, -28), Sfx("stair_creak", 1.2, -12), Sfx("stair_creak", 3.4, -14),
              Sfx("footsteps_soft", 1.0, -18, dur=8.0), Sfx("stair_creak", 5.6, -12), Sfx("stair_creak", 7.8, -14)]),
    Shot("S08_SH06", s06, duration=6.0, sfx=[bed("crickets_bed", None, -28), Sfx("stair_creak", 0.6, -14),
                                              Sfx("stair_creak", 3.0, -12), Sfx("stair_creak", 5.4, -14)]),
    Shot("S08_SH07", s07, lines=[Line("kabir", "One more, Nani. I've got you.", at=1.0)], tail=2.4,
         sfx=[bed("crickets_bed", None, -28), Sfx("stair_creak", 1.6, -14), Sfx("stair_creak", 4.2, -14)]),
    Shot("S08_SH08", s08, duration=4.4, sfx=[bed("crickets_bed", None, -28), Sfx("stair_creak", 1.4, -16)]),
    Shot("S08_SH09", s09, duration=4.6, sfx=[bed("crickets_bed", None, -28), Sfx("footsteps_soft", 0.3, -16, dur=2.8)]),
    # the wall
    Shot("S08_SH10", s10, duration=6.5, music="wall_hum", transition="fade_black", trans_dur=1.0,
         sfx=[bed("night_bed", None, -18), Sfx("clock_strike", 0.0, -8, params={"n": 3, "interval": 1.4}),
              Sfx("shop_flicker", 2.4, -20, dur=4.0)]),
    Shot("S08_SH11", s11, duration=5.0, sfx=[bed("night_bed", None, -18), Sfx("footsteps_soft", 0.3, -18, dur=2.6)]),
    Shot("S08_SH12", s12, duration=9.0, sfx=[bed("night_bed", None, -22), Sfx("hum_lullaby", 0.8, -4),
                                              Sfx("wall_echo_lullaby", 3.6, -8)]),
    Shot("S08_SH13", s13, duration=11.0, music="memory",
         sfx=[bed("night_bed", None, -24), Sfx("bubble_rise", 0.0, -8), Sfx("sung_lullaby_child", 1.5, -6),
              Sfx("sparkle", 6.5, -14)]),
    Shot("S08_SH14", s14, lines=[Line("nani", "I was the girl. I was the girl in the story.", at=1.2)], tail=2.0,
         sfx=[bed("night_bed", None, -24)]),
    Shot("S08_SH15", s15, duration=7.0, music="blaze", music_hits=[2.0, 4.0],
         sfx=[bed("night_bed", None, -24), Sfx("bubble_settle", 1.6, -8), Sfx("wall_glow", 0.4, -8),
              Sfx("shop_unfold", 2.0, -2), Sfx("awning_snap", 3.6, -6), Sfx("lantern_light", 4.2, -8),
              Sfx("dog_bark", 4.8, -10)]),
    # inside: blaze
    Shot("S08_SH16", s16, duration=6.5, transition="dissolve", trans_dur=0.6,
         sfx=[bed("crickets_bed", None, -30), Sfx("tola_clonng", 1.6, 0), Sfx("jars_refill", 2.0, -4),
              Sfx("jar_chord", 2.4, -6), Sfx("lantern_light", 2.2, -10)]),
    Shot("S08_SH17", s17, duration=5.0, sfx=[bed("crickets_bed", None, -30), Sfx("sparkle", 0.4, -16)]),
    Shot("S08_SH18", s18, lines=[Line("amma", "There you are, Sharda.", at=0.7)], tail=1.8,
         sfx=[bed("crickets_bed", None, -30)]),
    Shot("S08_SH19", s19, lines=[Line("nani", "I forgot you.", at=0.6)], tail=1.6, sfx=[bed("crickets_bed", None, -30)]),
    Shot("S08_SH20", s20, lines=[Line("amma", "Everybody forgets. The trick is remembering again.", at=0.6)], tail=2.0,
         sfx=[bed("crickets_bed", None, -30)]),
    Shot("S08_SH21", s21, duration=6.0, music="heavy", sfx=[bed("crickets_bed", None, -30),
                                                           Sfx("bubble_rise", 2.4, -8)]),
    Shot("S08_SH22", s22, duration=4.2, sfx=[bed("crickets_bed", None, -30), Sfx("tola_thunk", 0.72, 0),
                                              Sfx("jar_chord", 0.9, -4), Sfx("jar_chord", 1.6, -8)]),
    Shot("S08_SH23", s23, duration=5.2, sfx=[bed("crickets_bed", None, -30), Sfx("crystal_melt", 0.6, -4),
                                              Sfx("sparkle", 2.6, -14)]),
    Shot("S08_SH24", s24, duration=3.6, sfx=[bed("crickets_bed", None, -30)]),
    Shot("S08_SH25", s25, lines=[Line("amma", "Now that... is heavy.", at=0.6)], tail=1.4,
         sfx=[bed("crickets_bed", None, -30)]),
    Shot("S08_SH26", s26, duration=5.0, sfx=[bed("crickets_bed", None, -30), Sfx("dog_howl", 0.8, -4),
                                              Sfx("jar_chord", 0.6, -14)]),
]

fit_beds(SHOTS)
