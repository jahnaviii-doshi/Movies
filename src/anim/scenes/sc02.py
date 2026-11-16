"""Scene 2 — MIDNIGHT (01:30-03:30). The clock, Chutney, the stairs, the gali, THE SHOP UNFOLDS, Amma."""
from __future__ import annotations

import math

from .. import core as K, fx
from ..core import W, H, lerp, seg, ease_in_out, ease_out, ease_out_back, smooth
from ..rig import chars
from ..rig.human import Pose
from ..sets import rooftop as RT, gali as G, stairwell as ST, wall as WL, shop as SH
from ..timeline import Shot, Line, Sfx
from ._util_a import bed, seat, head_y, amma, tola, dog, cam as ccam

MEHER = seat("charpai_meher")


def sleepers(cv, t, meher=True):
    for key, who, cover in (("charpai_nani", "nani", False), ("charpai_kabir", "kabir", True),
                            ("charpai_meher", "meher", False)):
        if who == "meher" and not meher:
            continue
        sx, sy = RT.ANCHORS[key]["surface"]
        RT.draw_sleeper(cv, sx, sy, RT.ANCHORS[key]["s"], t, who=who, face_cover=cover)


def lying_head(cv, key, t, who="meher", expr="neutral", blink=0.0, look=(0, 0)):
    """Draw an awake head in exactly the sleeper's head position (to open her eyes)."""
    sx, sy = RT.ANCHORS[key]["surface"]
    s = RT.ANCHORS[key]["s"]
    L = 280
    hx = -L / 2 + 20
    cv.save(); cv.translate(sx, sy); cv.scale(s, s); cv.translate(hx, -34); cv.rotate(-78); cv.scale(0.55, 0.55)
    chars.CAST[who].draw_head(cv, Pose(expr=expr, blink=blink, t=t, look=look))
    cv.restore()


# ---------------------------------------------------------------- rooftop
def sh01(cv, c):
    """Everyone asleep. Far away, the clock tower begins to strike."""
    z = lerp(1.0, 1.08, ease_in_out(c.u))
    cam = dict(cx=960, cy=640, zoom=z)
    RT.draw_rooftop(cv, c.t, time="night_dim", lantern=0.35, cam=cam)
    with K.camera(cv, 960, 640, z):
        with K.lit(cv, "moon"):
            sleepers(cv, c.t)
    # the clock tower face glints on each strike
    k = (c.t - 1.0) % 1.7
    if c.t > 1.0:
        tx, ty = 1155, 400
        fx.glow_dot(cv, tx, ty, 60, "#ffe7a8", 0.35 * max(0, 1 - k / 0.6))


def sh02(cv, c):
    """Close on Meher asleep... her eyes open."""
    sx, sy = RT.ANCHORS["charpai_meher"]["surface"]
    s = RT.ANCHORS["charpai_meher"]["s"]
    hx = sx + (-120) * s
    z = 3.4
    cx, cy = hx + 40, sy - 40
    RT.draw_rooftop(cv, c.t, time="night_dim", lantern=0.35, cam=dict(cx=cx, cy=cy, zoom=z))
    with K.camera(cv, cx, cy, z):
        with K.lit(cv, "moon"):
            sleepers(cv, c.t)
            if c.t > 1.8:
                o = smooth(seg(c.t, 1.8, 2.2))
                blink = 1 - o
                look = (0.0, 0.0) if c.t < 3.4 else (0.9, -0.3)
                lying_head(cv, "charpai_meher", c.t, expr="neutral", blink=blink, look=look)


def sh03(cv, c):
    """A thin, hopeful whine from below. Meher sits up and listens."""
    t = c.t
    mx, my, ms = MEHER
    hy = head_y("meher", my, ms)
    z = 2.1
    cx, cy = mx + 120, hy + 80
    RT.draw_rooftop(cv, t, time="night_dim", lantern=0.35, cam=dict(cx=cx, cy=cy, zoom=z))
    with K.camera(cv, cx, cy, z):
        with K.lit(cv, "moon"):
            up = ease_out_back(seg(t, 0.2, 0.9))
            chars.draw(cv, "meher", x=mx, y=my, s=ms, legs="sit", t=t, turn=0.6,
                       expr="surprised" if t > 1.4 else "neutral", look=(1.0, 0.4) if t > 1.4 else (0.3, 0),
                       head_tilt=lerp(0, 12, smooth(seg(t, 1.4, 2.0))), lean=lerp(-10, 0, up),
                       brow=0.6 if t > 1.4 else 0)
    # the whine drawn as a little wavy sound curl rising from below right
    u = seg(t, 1.0, 2.6)
    if 0 < u < 1:
        for i in range(3):
            y = 1080 - u * 360 - i * 30
            x = 1700 + 20 * math.sin(u * 10 + i)
            cv.drawPath(K.smooth_path([(x - 30, y), (x - 10, y - 12), (x + 10, y), (x + 30, y - 12)], close=False),
                        K.stroke("#cfd8ff", 4, (1 - u) * 0.7))


# ---------------------------------------------------------------- the gali
def sh04(cv, c):
    """Chutney in the lane, looking straight up at her. Then: come on."""
    t = c.t
    cz = lerp(1.35, 1.5, ease_in_out(c.u))
    G.draw_gali(cv, t, time="night", cam=(960, 700, cz))
    with K.camera(cv, 960, 700, cz):
        # stage: 0-2.6 look up wagging; 2.6-4.0 trot; 4.0-5.2 look back; 5.2-7 trot on
        if t < 2.6:
            d, mode, flip, lu = 0.18, "sit", False, 0.9
        elif t < 4.0:
            d, mode, flip, lu = lerp(0.18, 0.38, ease_in_out(seg(t, 2.6, 4.0))), "trot", False, 0.0
        elif t < 5.2:
            d, mode, flip, lu = 0.38, "stand", True, 0.4
        else:
            d, mode, flip, lu = lerp(0.38, 0.62, ease_in_out(seg(t, 5.2, 7.2))), "trot", False, 0.0
        y, s = G.gali_ground(d)
        x = G.gali_x(d, -0.3)
        with K.lit(cv, "moon"):
            dog(cv, x=x, y=y, s=s * 1.0, t=t, mode=mode, flip=flip, phase=t * 1.6, look_up=lu,
                ear=1.0, wag=1.8 if t < 2.6 or 4.0 < t < 5.2 else 1.0, tongue=t < 2.6, expr="happy")


def sh05(cv, c):
    """Down the narrow stairs, barefoot, holding her breath on the step that creaks."""
    t = c.t
    steps = ST.STEPS
    cz = 1.45
    # step timing: one tread every ~0.55 s; freeze on tread 6 (the creak) for 1.2 s
    pos = 0.0
    tt = t - 0.4
    for i in range(len(steps) - 1):
        dur = 0.55 if i != 5 else 0.55 + 1.3
        if tt > dur:
            tt -= dur
            pos += 1
        else:
            pos += min(1.0, tt / 0.55)
            break
    pos = max(0.0, min(pos, len(steps) - 1))
    i0 = int(pos)
    i1 = min(i0 + 1, len(steps) - 1)
    f = pos - i0
    x = lerp(steps[i0][0], steps[i1][0], f)
    y = lerp(steps[i0][1], steps[i1][1], f) - math.sin(f * math.pi) * 8
    frozen = 5.9 <= pos < 6.05 and t > 2.0
    ccx, ccy, cz = ccam(x + 60, y - 160, cz)
    cv.save()
    cv.translate(W / 2, H / 2); cv.scale(cz, cz); cv.translate(-ccx, -ccy)
    ST.draw_stairwell(cv, t, light="moon")
    with K.lit(cv, "moon"):
        chars.draw(cv, "meher", x=x, y=y, s=ST.CHAR_S * 1.25, t=t, legs="tiptoe" if not frozen else "stand",
                   expr="wince" if frozen else "neutral", turn=0.6, look=(0.6, 0.6),
                   arms={"l": (30, 40), "r": (30, 40)} if not frozen else {"l": (10, 120), "r": (10, 120)},
                   head_tilt=-6 if frozen else 0)
    cv.restore()


def sh06(cv, c):
    """Low, child-height tracking along the sleeping lane."""
    t = c.t
    scroll = t * 120
    G.draw_gali_side(cv, t, time="night", scroll=scroll)
    gy = G.GROUND_Y_SIDE
    with K.lit(cv, "moon"):
        from ..rig import animals as A
        A.draw_rickshaw(cv, 1500 - scroll, gy + 4, s=1.15, t=t)
        chars.draw(cv, "meher", x=760, y=gy, s=1.9, t=t, legs="walk", phase=t * 1.0, expr="neutral",
                   turn=0.7, look=(0.8, -0.4) if 2 < t < 4.5 else (0.9, 0))


def sh07(cv, c):
    """Chutney sits facing the blank blue wall like it's a television."""
    t = c.t
    z = lerp(1.0, 1.06, ease_in_out(c.u))
    WL.draw_wall(cv, t, time="night", cam=(960, 600, z))
    with K.camera(cv, 960, 600, z):
        mx = lerp(260, 560, ease_out(seg(t, 0.0, 2.2)))
        walking = t < 2.2
        with K.lit(cv, "moon"):
            dog(cv, x=820, y=WL.FLOOR_Y, s=WL.DOG_S, t=t, mode="sit", look_up=0.25, ear=1.0, wag=0.6,
                head_tilt=-6 if t > 3.0 else 0)
            chars.draw(cv, "meher", x=mx, y=WL.FLOOR_Y, s=WL.CHAR_S, t=t, legs="walk" if walking else "stand",
                       phase=t * 1.2, turn=0.6, expr="neutral" if not c.speaking("meher") else "shy",
                       mouth=c.mouth("meher"), look=(0.8, 0.5) if t > 2.4 else (0.9, 0),
                       head_tilt=6 if t > 2.4 else 0)


def sh08(cv, c):
    """The last chime fades... and a crack in the paint begins to glow gold."""
    t = c.t
    g = ease_in_out(seg(t, 0.8, 6.0))
    z = lerp(1.05, 1.14, ease_in_out(c.u))
    WL.draw_wall(cv, t, time="night", glow=g, cam=(960, 560, z))
    with K.camera(cv, 960, 560, z):
        with K.lit(cv, "moon"):
            dog(cv, x=820, y=WL.FLOOR_Y, s=WL.DOG_S, t=t, mode="sit", look_up=0.25 + 0.3 * g, ear=0.5 + 0.5 * g,
                expr="alert" if g > 0.2 else "happy", wag=0.3)
            back = ease_out(seg(t, 3.2, 4.2)) * 40
            chars.draw(cv, "meher", x=560 - back, y=WL.FLOOR_Y, s=WL.CHAR_S, t=t, turn=0.6,
                       expr="surprised" if g > 0.25 else "neutral", look=(0.9, -0.2), lean=-4 * g,
                       arms={"l": (10, 20), "r": (25, 100)} if g > 0.4 else {})
        # gold light starts to touch them
        fx.light_pool(cv, 960, 700, 520, 330, "gold", 0.14 * g)


def sh09(cv, c):
    """Close on Meher: a wind chime rings, with no wind. Gold light on her face."""
    t = c.t
    WL.draw_wall(cv, t, time="night", glow=1.0, unfold=0.03 * seg(t, 1.5, 3.0), cam=(640, 520, 2.3))
    with K.camera(cv, 640, 520, 2.3):
        with K.lit(cv, "moon"):
            chars.draw(cv, "meher", x=540, y=WL.FLOOR_Y, s=WL.CHAR_S, t=t, turn=0.6, expr="awe",
                       look=(0.9 + 0.1 * math.sin(t * 2), -0.3), head_tilt=-5 + 4 * math.sin(t * 1.3), brow=0.5)
        fx.light_pool(cv, 680, 520, 180, 220, "gold", 0.18 + 0.06 * math.sin(t * 5))
    fx.sparkles(cv, t, 1400, 300, spread=260, n=10, color="gold", size=8, seed=3, a=0.8)


def sh10(cv, c):
    """THE SHOP UNFOLDS."""
    t = c.t
    u = ease_in_out(seg(t, 0.3, 8.6))
    z = lerp(1.18, 1.0, ease_in_out(seg(t, 0.0, 9.0)))
    cy = lerp(500, 560, ease_in_out(c.u))
    WL.draw_wall(cv, t, time="night", glow=1.0, unfold=u, cam=(960, cy, z))
    with K.camera(cv, 960, cy, z):
        with K.lit(cv, "moon"):
            dog(cv, x=780, y=WL.FLOOR_Y, s=WL.DOG_S, t=t, mode="sit", look_up=0.5, ear=1.0, expr="alert",
                wag=2.0 if u > 0.6 else 0.6)
            chars.draw(cv, "meher", x=520, y=WL.FLOOR_Y, s=WL.CHAR_S, t=t, turn=0.6,
                       expr="awe" if u < 0.85 else "grin", look=(0.8, -0.4 + 0.3 * u), lean=-6 + 6 * u,
                       arms={"l": (15 + 40 * u, 30), "r": (15 + 40 * u, 30)})
        fx.light_pool(cv, 960, 860, 720, 220, "gold", 0.25 * u)


def sh11(cv, c):
    """Chutney sneezes from sheer joy."""
    t = c.t
    WL.draw_wall(cv, t, time="night", glow=1.0, unfold=1.0, cam=(820, 760, 2.4))
    with K.camera(cv, 820, 760, 2.4):
        sneeze = 1.2 < t < 1.6
        with K.lit(cv, "moon"):
            dog(cv, x=780, y=WL.FLOOR_Y, s=WL.DOG_S, t=t, mode="sit", look_up=0.5 if not sneeze else 0.1,
                ear=1.0, expr="sneeze" if 0.9 < t < 1.7 else "happy", mouth=0.8 if sneeze else 0.0,
                head_tilt=-18 if sneeze else (8 if t < 1.2 else 0), wag=2.0, tongue=t > 2.0)
        fx.light_pool(cv, 820, 760, 260, 200, "gold", 0.22)
        if 1.2 < t < 2.2:
            fx.sparkles(cv, t, 860, 720, spread=60, n=10, color="gold", size=6, seed=4, a=1 - seg(t, 1.6, 2.2))


def sh11b(cv, c):
    """Chutney trots straight in. Meher hesitates on the step... then follows."""
    t = c.t
    z = lerp(1.0, 1.1, ease_in_out(c.u))
    WL.draw_wall(cv, t, time="night", glow=1.0, unfold=1.0, cam=(960, 600, z))
    with K.camera(cv, 960, 600, z):
        du = ease_in_out(seg(t, 0.4, 2.4))
        with K.lit(cv, "moon", alpha=1.0):
            if du < 0.98:
                dog(cv, x=lerp(780, 960, du), y=lerp(WL.FLOOR_Y, WL.FLOOR_Y - 40, du), s=WL.DOG_S * lerp(1, 0.8, du),
                    t=t, mode="trot", phase=t * 1.8, ear=1.0, tongue=True, alpha=1 - seg(du, 0.8, 1.0))
            mu = ease_in_out(seg(t, 3.0, 5.2))
            chars.draw(cv, "meher", x=lerp(560, 930, mu), y=lerp(WL.FLOOR_Y, WL.FLOOR_Y - 30, mu),
                       s=WL.CHAR_S * lerp(1, 0.9, mu), t=t, legs="tiptoe" if 0.02 < mu < 0.98 else "stand",
                       phase=t, turn=0.6, expr="worried" if t < 3.0 else "awe",
                       look=(0.9, -0.2) if t < 2.4 else (0.3 * math.sin(t * 3), -0.1),
                       arms={"l": (10, 110), "r": (10, 110)} if t < 3.0 else {}, alpha=1 - seg(mu, 0.85, 1.0))
        fx.light_pool(cv, 960, 860, 700, 220, "gold", 0.25)
        fx.motes(cv, t, (600, 230, 1320, 905), n=30, color="#ffe7a8", a=0.6, seed=6)


# ---------------------------------------------------------------- inside
def sh12(cv, c):
    """From inside: Meher steps through the doorway; the floorboards sigh."""
    t = c.t
    SH.draw_shop(cv, t, view="door")
    dx, dy, ds = SH.ANCHORS["door"]["doorway"]
    ix, iy, iz = SH.ANCHORS["door"]["inside"]
    u = ease_in_out(seg(t, 0.4, 3.6))
    with K.lit(cv, "shop"):
        chars.draw(cv, "meher", x=lerp(dx, ix + 120, u), y=lerp(dy, iy, u), s=lerp(ds, iz, u), t=t,
                   legs="tiptoe" if 0.05 < u < 0.95 else "stand", phase=t, expr="awe", turn=0.2,
                   look=(-0.4 + 0.8 * math.sin(t * 0.9), -0.6))


def sh13(cv, c):
    """The shop, gold and humming. Tola asleep on the counter."""
    t = c.t
    cx, cy, z = ccam(lerp(860, 1060, ease_in_out(c.u)), 560, lerp(1.06, 1.12, ease_in_out(c.u)))
    SH.draw_shop(cv, t, view="wide", cam=(cx, cy, z))
    with K.camera(cv, cx, cy, z):
        SH.draw_counter_front(cv, t, "wide")
        tx, ty, ts = SH.ANCHORS["wide"]["tola"]
        tola(cv, t, tx, ty, ts, eyes="closed", mouth="o", jitter=0.0)
        mx, my, ms = SH.ANCHORS["wide"]["customer"]
        with K.lit(cv, "shop"):
            chars.draw(cv, "meher", x=mx + lerp(0, 120, ease_in_out(seg(t, 1.5, 5.5))), y=my, s=ms, t=t,
                       legs="tiptoe" if 1.5 < t < 5.5 else "stand", phase=t * 0.8, expr="awe", turn=0.3,
                       look=(math.sin(t * 0.8), -0.7), head_tilt=6 * math.sin(t * 0.6))
            dx, dy, dz = SH.ANCHORS["wide"]["dog"]
            dog(cv, x=dx, y=dy, s=dz, t=t, mode="stand", ear=1.0, tongue=True, look_up=0.3)
    fx.motes(cv, t, (0, 0, W, H), n=40, color="#ffe7a8", a=0.5, seed=12)


def sh14(cv, c):
    """Tola, asleep: its pans rise and fall with each snore."""
    t = c.t
    tx, ty, ts = SH.ANCHORS["counter"]["tola"]
    z = lerp(1.7, 1.85, ease_in_out(c.u))
    cx, cy = tx, ty - 230 * ts
    SH.draw_shop(cv, t, view="counter", cam=(cx, cy, z))
    with K.camera(cv, cx, cy, z):
        SH.draw_counter_front(cv, t, "counter")
        snore = math.sin(t * 2.4)
        tola(cv, t, tx, ty, ts, eyes="closed", mouth="o" if snore > 0 else "line", tilt=3 * snore)
    for i in range(3):
        u = ((t * 0.6 + i / 3) % 1)
        fx.star4(cv, cx + 120 + u * 80, H / 2 - 200 - u * 140, 10 * (1 - u), "#fff3c8", 0.7 * (1 - u))


def counter_shot(cv, c, cam, amma_rise=1.0, amma_kw=None, meher_kw=None, tola_kw=None, amma_alpha=0.82):
    t = c.t
    cam = ccam(*cam)
    SH.draw_shop(cv, t, view="counter", cam=cam)
    with K.camera(cv, *cam):
        ax, ay, az = SH.ANCHORS["counter"]["amma"]
        if amma_rise > 0:
            hide = (1 - amma_rise) * 300
            kw = dict(expr="neutral", turn=-0.3, look=(-0.8, 0.2))
            kw.update(amma_kw or {})
            amma(cv, t, ax, ay + hide, az, mouth=c.mouth("amma"), alpha=amma_alpha, desat=0.18, **kw)
        SH.draw_counter_front(cv, t, "counter")
        tx, ty, ts = SH.ANCHORS["counter"]["tola"]
        kw = dict(eyes="closed", mouth="line")
        kw.update(tola_kw or {})
        tola(cv, t, tx, ty, ts, **kw)
        mx, my, ms = SH.ANCHORS["counter"]["customer"]
        kw = dict(expr="awe", turn=0.5, look=(0.9, -0.3))
        kw.update(meher_kw or {})
        jump = kw.pop("jump", 0.0)
        with K.lit(cv, "shop"):
            chars.draw(cv, "meher", x=mx, y=my - jump, s=ms, t=t, mouth=c.mouth("meher"), **kw)


def sh15(cv, c):
    """'You're late.' Out of nowhere. Meher jumps."""
    t = c.t
    ln = c.shot.lines[0]
    jumped = t > ln.at + 0.15
    jump = math.sin(min(1, seg(t, ln.at + 0.15, ln.at + 0.6)) * math.pi) * 60
    counter_shot(cv, c, (960, 540, 1.0), amma_rise=0.0,
                 meher_kw=dict(expr="surprised" if jumped else "awe", jump=jump,
                               look=(0.9, -0.5) if not jumped else (0.6 * math.sin(t * 6), -0.2),
                               arms={"l": (60, 40), "r": (60, 40)} if jumped else {}))


def sh16(cv, c):
    """Over the counter rise a pair of round spectacles, a cloud of white hair... Mishri Amma."""
    t = c.t
    ln = c.shot.lines[0]
    rise = ease_out(seg(t, 0.3, 2.4)) * 0.55 + ease_out_back(seg(t, 2.6, 3.4)) * 0.45
    cam = (1150, 520, lerp(1.25, 1.35, ease_in_out(c.u)))
    counter_shot(cv, c, cam, amma_rise=rise,
                 amma_kw=dict(expr="neutral" if t < ln.at else "smug", look=(-0.9, 0.3), head_tilt=-4,
                              arms={"l": (40, 120), "r": (40, 120)}),
                 meher_kw=dict(expr="surprised", look=(0.9, -0.2)))


def sh17(cv, c):
    """'I'm only nine.'"""
    t = c.t
    mx, my, ms = SH.ANCHORS["counter"]["customer"]
    hy = my + (chars.CAST["meher"].neck_y - 46) * ms
    counter_shot(cv, c, (mx + 160, hy + 120, 1.7),
                 amma_kw=dict(expr="neutral", look=(-0.9, 0.3)),
                 meher_kw=dict(expr="worried" if c.speaking("meher") else "shy", look=(0.9, -0.4),
                               head_tilt=-6, arms={"l": (15, 90), "r": (15, 90)}))


def sh18(cv, c):
    """Amma peers at her over the spectacles."""
    t = c.t
    ax, ay, az = SH.ANCHORS["counter"]["amma"]
    hy = ay + (chars.CAST["amma"].neck_y - 38) * az
    lean = ease_in_out(seg(t, 0.2, 1.0)) * 10
    counter_shot(cv, c, (ax - 160, hy + 60, 1.75),
                 amma_kw=dict(expr="happy" if t > c.shot.lines[0].end - 0.4 else "smug", look=(-0.9, -0.4),
                              head_tilt=8 + lean * 0.3, lean=-lean, arms={"l": (40, 120), "r": (40, 120)}),
                 meher_kw=dict(expr="shy"))


SHOTS = [
    Shot("S02_SH01", sh01, duration=8.5, music="midnight_mystery", transition="fade_black", trans_dur=2.0,
         sfx=[bed("crickets_bed", 8.5, -16), Sfx("clock_strike", 1.0, -8, params={"n": 12, "interval": 1.7})]),
    Shot("S02_SH02", sh02, duration=5.0, sfx=[bed("crickets_bed", 5.0, -18)]),
    Shot("S02_SH03", sh03, duration=5.0, sfx=[bed("crickets_bed", 5.0, -18), Sfx("dog_whine", 1.0, -6)]),
    Shot("S02_SH04", sh04, duration=7.6, sfx=[bed("night_bed", 7.6, -16), Sfx("dog_whine", 0.4, -10),
                                               Sfx("footsteps_soft", 2.7, -18, params={"rate": 4})]),
    Shot("S02_SH05", sh05, duration=9.0, sfx=[bed("night_bed", 9.0, -22), Sfx("footsteps_soft", 0.4, -18),
                                               Sfx("stair_creak", 3.65, -6)]),
    Shot("S02_SH06", sh06, duration=7.0, sfx=[bed("night_bed", 7.0, -16), Sfx("footsteps_soft", 0.0, -16)]),
    Shot("S02_SH07", sh07, lines=[Line("meher", "It's just a wall, Chutney.", at=3.0)], tail=1.6,
         sfx=[bed("night_bed", 7.0, -16)]),
    Shot("S02_SH08", sh08, duration=6.5, music="wonder_unfold", music_hits=[0.8, 6.5 + 3.0 + 1.3, 6.5 + 3.0 + 4.5, 6.5 + 3.0 + 8.6],
         sfx=[bed("night_bed", 6.5, -20), Sfx("wall_glow", 0.8, -6)]),
    Shot("S02_SH09", sh09, duration=3.0, sfx=[Sfx("wind_chime_hello", 0.3, -4)]),
    Shot("S02_SH10", sh10, duration=11.0,
         sfx=[Sfx("shop_unfold", 0.4, -4), Sfx("awning_snap", 3.4, -6), Sfx("lantern_light", 5.0, -8),
              Sfx("lantern_light", 5.5, -8), Sfx("lantern_light", 6.0, -8), Sfx("lantern_light", 6.5, -8),
              Sfx("sparkle", 7.6, -8), Sfx("jar_chord", 8.6, -10)]),
    Shot("S02_SH11", sh11, duration=3.6, sfx=[Sfx("dog_sneeze", 1.2, -4)]),
    Shot("S02_SH11B", sh11b, duration=5.8, sfx=[Sfx("footsteps_soft", 0.5, -18), Sfx("floor_creak", 4.6, -12)]),
    Shot("S02_SH12", sh12, duration=4.2, music="shop_warm", sfx=[Sfx("floor_creak", 1.8, -8), bed("night_bed", 4.2, -28)]),
    Shot("S02_SH13", sh13, duration=9.5, sfx=[Sfx("sparkle", 1.0, -18)]),
    Shot("S02_SH14", sh14, duration=4.2, sfx=[Sfx("tola_tink", 0.6, -18), Sfx("tola_tink", 3.2, -20)]),
    Shot("S02_SH15", sh15, lines=[Line("amma", "You're late.", at=1.4, onscreen=False)], tail=1.4),
    Shot("S02_SH16", sh16, lines=[Line("amma", "Eighty years late.", at=3.6)], tail=1.0,
         sfx=[Sfx("sparkle", 0.5, -16)]),
    Shot("S02_SH17", sh17, lines=[Line("meher", "I'm only nine.", at=0.5)], tail=1.0),
    Shot("S02_SH18", sh18, lines=[Line("amma", "Then you're very early for someone so late.", at=1.0)], tail=1.6),
]
