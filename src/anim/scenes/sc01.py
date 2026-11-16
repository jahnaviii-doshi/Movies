"""Scene 1 — SUMMER NIGHT (00:00-01:30). Title, power cut, Nani's half-story, the blue wall."""
from __future__ import annotations

import math

from .. import core as K, fx
from ..core import W, H, lerp, seg, ease_in_out, ease_out, smooth
from ..rig import chars
from ..sets import town, rooftop as RT
from ..timeline import Shot, Line, Sfx
from ._util_a import bed, seat, head_y, look_dart, title_text

NANI = seat("charpai_nani")
MEHER = seat("charpai_meher")
KABIR = seat("charpai_kabir")


def fan_arm(t, speed=1.0, amp=1.0):
    return {"r": (34 + 12 * amp * math.sin(t * 5.5 * speed), 104 + 10 * amp * math.sin(t * 5.5 * speed + 0.6))}


def cap_arm(t, speed=1.0):
    return {"r": (70 + 26 * math.sin(t * 7 * speed), 70)}


def roof_people(cv, c, nani=None, meher=None, kabir=None, light="moon"):
    """Draw the three on their charpais with per-shot pose overrides."""
    t = c.t
    with K.lit(cv, light):
        nx, ny, ns = NANI
        kw = dict(x=nx, y=ny, s=ns, legs="sit", t=t, turn=0.45, hold="fan", arms=fan_arm(t),
                  expr="happy", mouth=c.mouth("nani"))
        kw.update(nani or {})
        if kw.pop("hide", False) is False:
            chars.draw(cv, "nani", **kw)
        kx, ky, ks = KABIR
        kw = dict(x=kx, y=ky, s=ks, legs="sit", t=t, turn=0.4, flip=True, hold="cap", arms=cap_arm(t),
                  expr="sleepy", mouth=c.mouth("kabir"))
        kw.update(kabir or {})
        if kw.pop("hide", False) is False:
            chars.draw(cv, "kabir", **kw)
        mx, my, ms = MEHER
        kw = dict(x=mx, y=my, s=ms, legs="sit", t=t, turn=0.0, expr="happy", look=(-0.6, 0),
                  mouth=c.mouth("meher"), head_tilt=-4, extra={"swing": 1.0})
        kw.update(meher or {})
        if kw.pop("hide", False) is False:
            chars.draw(cv, "meher", **kw)


# ---------------------------------------------------------------- shots
def sh01(cv, c):
    """Dusk over Chandpur, heat shimmer, title."""
    cx = lerp(0, 320, ease_in_out(c.t / 12.5))
    town.draw_town(cv, c.t, time="dusk", lights=1.0, heat=0.7, cam_x=cx)
    a = smooth(seg(c.t, 1.6, 3.4)) * (1 - smooth(seg(c.t, 8.6, 10.4)))
    title_text(cv, "The Midnight", W / 2, 250, 110, a)
    title_text(cv, "Sweet Shop", W / 2, 380, 110, a)
    fx.sparkles(cv, c.t, W / 2, 300, spread=420, n=18, color="gold", size=6, seed=5, a=a * 0.8)


def sh02(cv, c):
    """The power cut: windows go dark in a wave."""
    cx = lerp(320, 430, ease_in_out(c.u))
    pu = ease_in_out(seg(c.t, 1.8, 4.6))
    town.draw_town(cv, c.t, time="dusk", lights=1.0, powercut_u=pu, heat=0.5 * (1 - pu), cam_x=cx)
    # the sky darkens a little as the town goes out
    fx.fade(cv, "#0b0d2a", 0.28 * seg(c.t, 3.0, 7.0))


def sh03(cv, c):
    """Rooftop establishing: stars, lantern, the family on their charpais."""
    z = lerp(1.0, 1.06, ease_in_out(c.u))
    cam = dict(cx=960, cy=620, zoom=z)
    RT.draw_rooftop(cv, c.t, time="night", lantern=1.0, cam=cam)
    with K.camera(cv, 960, 620, z):
        roof_people(cv, c, meher={"expr": "neutral", "look": (-0.8, -0.2)})


def _ms(cv, c, cx, cy, z0, z1, **people):
    z = lerp(z0, z1, ease_in_out(c.u))
    cam = dict(cx=cx, cy=cy, zoom=z)
    RT.draw_rooftop(cv, c.t, time="night", lantern=1.0, cam=cam)
    with K.camera(cv, cx, cy, z):
        roof_people(cv, c, **people)


def sh04(cv, c):
    """Nani begins the story."""
    t = c.t
    _ms(cv, c, 560, 600, 1.75, 1.88,
        nani={"expr": "happy", "look": (0.6, -0.1), "head_tilt": 3 * math.sin(t * 0.8), "arms": fan_arm(t, 0.6)},
        meher={"expr": "neutral", "look": (-1, -0.2)})


def sh05(cv, c):
    """Meher's eyes widen."""
    mx, my, ms = MEHER
    hy = head_y("meher", my, ms)
    awe = c.t > 0.9
    _ms(cv, c, mx, hy + 40, 2.5, 2.7,
        meher={"expr": "awe" if awe else "neutral", "look": (-0.7, -0.1), "lean": -3 if awe else 0,
               "brow": 0.6 if awe else 0})


def sh06(cv, c):
    """Two-shot Nani + Meher: 'only with goodness'."""
    t = c.t
    _ms(cv, c, 690, 640, 1.42, 1.5,
        nani={"expr": "happy", "look": (0.8, 0), "arms": {"r": (60, 70)}, "hold": "fan",
              "head_tilt": 4},
        meher={"expr": "awe", "look": (-1, -0.1), "lean": -4})


def sh07(cv, c):
    """'Then what happened?'"""
    mx, my, ms = MEHER
    hy = head_y("meher", my, ms)
    _ms(cv, c, mx - 80, hy + 60, 2.1, 2.2,
        meher={"expr": "happy", "look": (-0.9, -0.1), "lean": -7, "head_tilt": -7,
               "arms": {"l": (20, 80), "r": (20, 80)}})


def sh08(cv, c):
    """Nani reaches for the ending... and it's gone."""
    t = c.t
    ln = c.shot.lines[0]
    blank = t < ln.at
    fan_speed = lerp(0.6, 0.0, seg(t, 0.4, 2.0))
    expr = "happy" if t < 0.6 else ("worried" if t < ln.at + 2.0 else "sad")
    if t > ln.at + 4.2:
        expr = "happy"   # the gentle, resigned smile on "like a sweet..."
    _ms(cv, c, 520, 600, 1.9, 2.05,
        nani={"expr": expr, "look": (0.3 * math.sin(t * 0.7), -0.5 if blank else 0.1),
              "arms": fan_arm(t, fan_speed, amp=fan_speed), "head_tilt": -4 if blank else 2,
              "mouth": 0.25 if 0.6 < t < ln.at - 0.2 else c.mouth("nani")})


def sh09(cv, c):
    """Kabir, bored, says it's made up."""
    t = c.t
    kx, ky, ks = KABIR
    hy = head_y("kabir", ky, ks)
    roll = seg(t, 0.2, 0.8) * (1 - seg(t, 1.2, 1.7))
    _ms(cv, c, kx - 60, hy + 70, 2.0, 2.12,
        kabir={"expr": "smug", "look": (0.2, -1.0 * roll), "arms": cap_arm(t, 0.7), "head_tilt": 6,
               "mouth": c.mouth("kabir")})


def sh10(cv, c):
    """Nani lies back and hums six notes she can't name."""
    t = c.t
    lie = ease_in_out(seg(t, 0.3, 2.0))
    z = lerp(1.35, 1.5, ease_in_out(c.u))
    cx, cy = 600, 680
    RT.draw_rooftop(cv, t, time="night", lantern=1.0, cam=dict(cx=cx, cy=cy, zoom=z))
    with K.camera(cv, cx, cy, z):
        sx, sy = RT.ANCHORS["charpai_nani"]["surface"]
        if lie < 1:
            with K.lit(cv, "moon", alpha=1 - lie):
                nx, ny, ns = NANI
                chars.draw(cv, "nani", x=nx, y=ny, s=ns, legs="sit", t=t, turn=0.45, hold="fan",
                           arms=fan_arm(t, 0.3, 0.3), expr="sleepy", lean=-8 * lie)
        if lie > 0:
            with K.lit(cv, "moon", alpha=lie):
                RT.draw_sleeper(cv, sx, sy, RT.ANCHORS["charpai_nani"]["s"], t, who="nani")
        mx, my, ms = MEHER
        with K.lit(cv, "moon"):
            chars.draw(cv, "meher", x=mx, y=my, s=ms, legs="sit", t=t, expr="neutral", look=(-0.8, 0.1),
                       head_tilt=-6, extra={"swing": 0.6})
    # the hum drifts up like a little curl of light
    for i in range(6):
        u = seg(t, 2.0 + i * 0.75, 4.5 + i * 0.75)
        if 0 < u < 1:
            x = 330 + i * 40 + 30 * math.sin(u * 4)
            y = 470 - u * 220
            fx.star4(cv, x, y, 9 * (1 - u), "#ffe2a8", 0.8 * (1 - u))


def sh11(cv, c):
    """Meher slides off her charpai and pads to the parapet."""
    t = c.t
    cam = dict(cx=1100, cy=640, zoom=1.12)
    RT.draw_rooftop(cv, t, time="night", lantern=1.0, cam=cam)
    with K.camera(cv, 1100, 640, 1.12):
        with K.lit(cv, "moon"):
            for key in ("charpai_nani",):
                sx, sy = RT.ANCHORS[key]["surface"]
                RT.draw_sleeper(cv, sx, sy, RT.ANCHORS[key]["s"], t, who="nani")
            sx, sy = RT.ANCHORS["charpai_kabir"]["surface"]
            RT.draw_sleeper(cv, sx, sy, RT.ANCHORS["charpai_kabir"]["s"], t, who="kabir", face_cover=True)
            mx, my, ms = MEHER
            px, py, ps = RT.ANCHORS["parapet_lean"]
            u = ease_in_out(seg(t, 0.8, 5.0))
            if t < 0.8:
                chars.draw(cv, "meher", x=mx, y=my, s=ms, legs="sit", t=t, expr="neutral", look=(1, 0.2))
            else:
                x = lerp(mx + 40, px - 40, u)
                y = lerp(my + 95, py, u)
                s = lerp(ms, ps * 1.45, u)
                walking = 0.05 < u < 0.97
                chars.draw(cv, "meher", x=x, y=y, s=s, t=t, legs="tiptoe" if not walking else "walk",
                           phase=t * 1.3, expr="neutral", turn=0.6, look=(0.8, 0.3),
                           arms={"l": (20, 30), "r": (20, 30)} if walking else {})


def sh12(cv, c):
    """Her gaze: down the dark gali to the dead end, where the blue wall catches the moonlight."""
    from ..sets import gali as G
    l, tp, r, b = G.WALL_RECT
    wx, wy = (l + r) / 2, (tp + b) / 2
    z = lerp(1.0, 1.9, ease_in_out(c.u))
    cx, cy = lerp(960, wx, ease_in_out(c.u)), lerp(560, wy, ease_in_out(c.u))
    G.draw_gali(cv, c.t, time="night", cam=(cx, cy, z))
    with K.camera(cv, cx, cy, z):
        pulse = 0.22 + 0.08 * math.sin(c.t * 1.3)
        fx.light_pool(cv, wx, wy, (r - l) * 0.75, (b - tp) * 0.7, "#a9bcff", pulse)
        fx.sparkles(cv, c.t, wx, wy, spread=(r - l) * 0.45, n=6, color="#dfe6ff", size=4, seed=17, a=0.5)


def sh13(cv, c):
    """Meher's long look. Nobody has ever looked at that wall this long."""
    t = c.t
    px, py, ps = RT.ANCHORS["parapet_lean"]
    s = ps * 1.45
    hy = head_y("meher", py, s, sitting=False)
    z = lerp(2.3, 2.6, ease_in_out(c.u))
    cx, cy = px - 60, hy + 40
    RT.draw_rooftop(cv, t, time="night", lantern=0.8, cam=dict(cx=cx, cy=cy, zoom=z))
    with K.camera(cv, cx, cy, z):
        with K.lit(cv, "moon"):
            chars.draw(cv, "meher", x=px - 40, y=py, s=s, t=t, turn=0.7, expr="neutral" if t < 3.5 else "determined",
                       look=(0.9, 0.7), head_tilt=8, arms={"l": (40, 70), "r": (40, 70)}, lean=6,
                       brow=0.3 if t < 3.5 else 0)
        fx.sparkles(cv, t, px + 120, hy + 30, spread=60, n=4, color="#cfd8ff", size=5, seed=9, a=0.5)


SH01_D = 14.5

SHOTS = [
    Shot("S01_SH01", sh01, duration=SH01_D, music="dusk", music_hits=[SH01_D + 2.0],
         transition="fade_black", trans_dur=3.0,
         sfx=[bed("heat_cicadas", SH01_D, -16), bed("day_bed", SH01_D, -20)]),
    Shot("S01_SH02", sh02, duration=7.5,
         sfx=[bed("heat_cicadas", 2.2, -16), Sfx("fans_wind_down", 1.9, -6), Sfx("town_groan", 2.9, -10),
              Sfx("train_horn_distant", 5.0, -14), bed("crickets_bed", 5.0, -18, at=2.5)]),
    Shot("S01_SH03", sh03, duration=6.0, music="rooftop_story", transition="dissolve", trans_dur=1.0,
         sfx=[bed("night_bed", 6.0)]),
    Shot("S01_SH04", sh04, lines=[Line("nani", "Once, in this very town, there was a sweet shop that opened only at midnight.", at=0.6)],
         tail=1.0, sfx=[bed("night_bed", 9.0)]),
    Shot("S01_SH05", sh05, duration=3.2, sfx=[bed("night_bed", 3.2)]),
    Shot("S01_SH06", sh06, lines=[Line("nani", "And you could not pay with money there.", at=0.4),
                                   Line("nani", "Only with goodness.", at=3.3)],
         tail=1.0, sfx=[bed("night_bed", 8.0)]),
    Shot("S01_SH07", sh07, lines=[Line("meher", "Then what happened?", at=0.4)], tail=1.0,
         sfx=[bed("night_bed", 4.0)]),
    Shot("S01_SH08", sh08, lines=[Line("nani", "Then... hm. The ending's gone again. Like a sweet you left in your pocket.", at=2.3)],
         tail=1.4, sfx=[bed("night_bed", 12.0)]),
    Shot("S01_SH09", sh09, lines=[Line("kabir", "Because there is no ending. It's made up.", at=0.5)], tail=1.0,
         sfx=[bed("night_bed", 5.0)]),
    Shot("S01_SH10", sh10, duration=9.0, sfx=[bed("night_bed", 9.0, -18), Sfx("hum_lullaby", 1.6, -6)]),
    Shot("S01_SH11", sh11, duration=6.0, sfx=[bed("night_bed", 6.0), Sfx("footsteps_soft", 1.0, -14)]),
    Shot("S01_SH12", sh12, duration=7.0, sfx=[bed("night_bed", 7.0, -16)]),
    Shot("S01_SH13", sh13, duration=6.5, sfx=[bed("night_bed", 6.5)]),
]
