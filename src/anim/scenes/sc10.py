"""Scene 10: CODA (~60 s). Next summer: Meher tells the story, and this time she knows the ending."""
from __future__ import annotations

import math

from .. import core as K, fx
from ..rig import chars
from ..sets import rooftop as R, gali
from ..timeline import Shot, Line, Sfx
from ._util_d import hand_pos, thread_band, draw_cousin

AN = R.ANCHORS
NB = AN["charpai_nani"]      # Meher now sits here, where Nani used to
MB = AN["charpai_meher"]     # Nani sits here
MX, MY = NB["surface"][0], NB["surface"][1] + 10
MS = NB["s"] * 1.5
NX, NY = MB["surface"][0] + 30, MB["surface"][1] + 10
NS = MB["s"] * 1.5
KB = AN["charpai_kabir"]     # Kabir sits on his own charpai, listening
KX, KY = KB["surface"][0], KB["surface"][1] + 10
KS = KB["s"] * 1.5
C1 = (300, 1010)    # cousin_boy, faces right toward Meher
C2 = (610, 1020)    # cousin_girl, faces left toward Meher


def _meher(cv, t, c=None, expr="happy", look=(0.6, -0.1), gesture=0.0, head_tilt=0.0):
    g = math.sin(t * 2.2) * 18 * gesture
    arms = {"r": (35 + 30 * gesture, 70 + g), "l": (14, 40)}
    chars.draw(cv, "meher", x=MX, y=MY, s=MS, t=t, legs="sit", expr=expr, turn=0.4, look=look,
               mouth=c.mouth("meher") if c else 0.0, arms=arms, hand={"r": "open"}, head_tilt=head_tilt,
               extra={"swing": 1.0})
    return arms


def _meher_band(cv, t, arms):
    (wx, wy), _ = hand_pos("meher", MX, MY, MS, arms, False, "sit", "r", frac=0.72)
    thread_band(cv, wx, wy, MS * 0.62, t, 1.0)


def _nani(cv, t, expr="happy", fan=True, look=(-0.7, 0.0), mouth=0.0, blink=None):
    f = math.sin(t * 3.2) * 18 if fan else 0
    kw = dict(x=NX, y=NY, s=NS, t=t, legs="sit", flip=True, expr=expr, turn=0.35, look=look, hold="fan",
              arms={"r": (30, 100 + f)}, mouth=mouth)
    if blink is not None:
        kw["blink"] = blink
    chars.draw(cv, "nani", **kw)


def _kabir(cv, t, expr="happy"):
    chars.draw(cv, "kabir", x=KX, y=KY, s=KS, t=t, flip=True, expr=expr, turn=0.45, lean=-4, legs="sit",
               arms={"l": (30, 120), "r": (24, 110)}, look=(0.8, 0.2), head_tilt=-7 + math.sin(t * 0.7) * 2)


def _cousins(cv, t, rapt=1.0):
    draw_cousin(cv, "cousin_boy", x=C1[0], y=C1[1], s=1.7, t=t, legs="sit", expr="awe" if rapt else "happy",
                turn=0.5, look=(0.8, -0.8), head_tilt=6 + math.sin(t * 0.8) * 2)
    draw_cousin(cv, "cousin_girl", x=C2[0], y=C2[1], s=1.7, t=t, legs="sit", flip=True,
                expr="awe" if rapt else "grin", turn=0.5, look=(0.8, -0.8), head_tilt=-6,
                arms={"l": (60, 120), "r": (60, 120)})


def sh01(cv, c):
    fx.card(cv, c.t, "Next summer.", a=K.clamp(min(c.t / 0.8, (c.dur - c.t) / 0.6)), size=96)


def sh02(cv, c):
    """Wide: power cut, stars, the same charpais. Meher has Nani's place now."""
    t = c.t
    z = K.lerp(1.0, 1.05, K.ease_in_out(c.u))
    cam = dict(cx=960, cy=560, zoom=z)
    R.draw_rooftop(cv, t, "night", lantern=1.0, cam=cam)
    with K.camera(cv, 960, 560, z):
        with K.lit(cv, "moon"):
            _kabir(cv, t)
            _nani(cv, t)
            arms = _meher(cv, t, expr="happy", gesture=0.6 if t > 3 else 0.2, look=(0.4, 0.4))
            _cousins(cv, t)
        _meher_band(cv, t, arms)


def sh03(cv, c):
    """MS: Meher tells the ending to the little cousins."""
    t = c.t
    cam = (560, 680, 1.55)
    R.draw_rooftop(cv, t, "night", lantern=1.0, cam=dict(cx=cam[0], cy=cam[1], zoom=cam[2]))
    with K.camera(cv, *cam):
        with K.lit(cv, "moon"):
            arms = _meher(cv, t, c, expr="happy", gesture=1.0, look=(0.3, 0.6), head_tilt=4)
            _cousins(cv, t)
        _meher_band(cv, t, arms)


def sh04(cv, c):
    """Meher glances at Nani; Nani smiles and hums the six notes."""
    t = c.t
    cam = (NX - 60, NY - 200, 2.0)
    R.draw_rooftop(cv, t, "night", lantern=1.0, cam=dict(cx=cam[0], cy=cam[1], zoom=cam[2]))
    hum = t > 1.0
    with K.camera(cv, *cam):
        with K.lit(cv, "moon"):
            _nani(cv, t, expr="happy", fan=True, look=(-0.6, -0.2),
                  blink=0.95 if 2.0 < t < 6.6 else None,
                  mouth=0.12 + 0.06 * math.sin(t * 5) if 1.0 < t < 7.0 else 0.0)
    if hum:
        # tiny floating notes of the lullaby, drifting up toward the stars
        with K.camera(cv, *cam):
            for i in range(6):
                u = (t - 1.0 - i * 0.9)
                if 0 < u < 3.5:
                    x = NX - 40 + i * 14 + math.sin(u * 2 + i) * 18
                    y = NY - 360 - u * 55
                    a = K.clamp(min(u / 0.5, (3.5 - u) / 1.0))
                    fx.glow_dot(cv, x, y, 18, "gold", 0.5 * a)
                    cv.drawCircle(x, y, 5, K.fill("#ffe9b8", a))
                    cv.drawLine(x + 5, y, x + 5, y - 22, K.stroke("#ffe9b8", 2.2, a))


def sh05(cv, c):
    """Kabir at the parapet, listening, smiling."""
    t = c.t
    cam = (KX - 40, KY - 200, 2.2)
    R.draw_rooftop(cv, t, "night", lantern=1.0, cam=dict(cx=cam[0], cy=cam[1], zoom=cam[2]))
    with K.camera(cv, *cam):
        with K.lit(cv, "moon"):
            _kabir(cv, t, expr="happy" if t > 1.2 else "neutral")


def sh06(cv, c):
    """Meher: 'Well. That's how it ends. And that's how it begins.'"""
    t = c.t
    z = K.lerp(1.55, 1.68, K.ease_in_out(c.u))
    cam = (580, 680, z)
    R.draw_rooftop(cv, t, "night", lantern=1.0, cam=dict(cx=cam[0], cy=cam[1], zoom=z))
    end = c.shot.lines[0].end if c.shot.lines else 4
    look_out = c.seg(end + 0.2, end + 1.0)
    with K.camera(cv, *cam):
        with K.lit(cv, "moon"):
            arms = _meher(cv, t, c, expr="grin" if t > end else "happy", gesture=0.5 * (1 - look_out),
                          look=(K.lerp(0.3, 0.9, look_out), K.lerp(0.5, -0.5, look_out)),
                          head_tilt=K.lerp(2, -6, look_out))
            _cousins(cv, t, rapt=0 if t > end else 1)
        _meher_band(cv, t, arms)


def sh07(cv, c):
    """Pull back: the rooftop under the stars, a small lantern-lit island in the dark town."""
    t = c.t
    z = K.lerp(1.12, 0.98, K.ease_in_out(c.u))
    R.draw_rooftop(cv, t, "night", lantern=1.0, cam=dict(cx=960, cy=560, zoom=z))
    with K.camera(cv, 960, 560, z):
        with K.lit(cv, "moon"):
            _kabir(cv, t)
            _nani(cv, t, fan=False, expr="sleepy")
            arms = _meher(cv, t, expr="happy", look=(0.2, -0.6))
            _cousins(cv, t, rapt=0)
        _meher_band(cv, t, arms)


def sh08(cv, c):
    """Down the dark gali, the blue wall shimmers once, gold in its cracks."""
    t = c.t
    pulse = math.sin(math.pi * K.clamp((t - 1.8) / 4.6)) ** 2
    z = K.lerp(1.0, 1.12, K.ease_in_out(c.u))
    cy = K.lerp(540, 505, K.ease_in_out(c.u))
    gali.draw_gali(cv, t, "night", wall_glow=0.85 * pulse, cam=(960, cy, z))
    if pulse > 0.05:
        x0, y0, x1, y1 = gali.WALL_RECT
        with K.camera(cv, 960, cy, z):
            fx.sparkles(cv, t, (x0 + x1) / 2, (y0 + y1) / 2, spread=(x1 - x0) / 2, n=14, color="gold",
                        size=6, seed=111, a=pulse)


SHOTS = [
    Shot("S10_SH01", sh01, duration=4.0, music="coda", transition="fade_black", trans_dur=1.6,
         sfx=[Sfx("crickets_bed", 0, -24, dur=4.0)]),
    Shot("S10_SH02", sh02, duration=11.0, transition="dissolve", trans_dur=1.0,
         sfx=[Sfx("night_bed", 0, -14, dur=11.0), Sfx("train_horn_distant", 3.5, -20)]),
    Shot("S10_SH03", sh03,
         lines=[Line("meher", "...and the shop stayed, as long as someone remembered it. That's the ending.", at=0.8)],
         tail=1.4, sfx=[Sfx("night_bed", 0, -15, dur=9.0)]),
    Shot("S10_SH04", sh04, duration=8.5,
         sfx=[Sfx("night_bed", 0, -18, dur=8.5), Sfx("hum_lullaby", 1.0, -4)]),
    Shot("S10_SH05", sh05, duration=4.0, sfx=[Sfx("night_bed", 0, -15, dur=4.0)]),
    Shot("S10_SH06", sh06,
         lines=[Line("meher", "Well. That's how it ends. And that's how it begins.", at=0.9)],
         tail=2.4, sfx=[Sfx("night_bed", 0, -15, dur=8.0), Sfx("kids_laugh", 5.4, -16)]),
    Shot("S10_SH07", sh07, duration=8.5, transition="dissolve", trans_dur=1.0,
         sfx=[Sfx("night_bed", 0, -14, dur=8.5), Sfx("crickets_bed", 0, -20, dur=8.5)]),
    Shot("S10_SH08", sh08, duration=13.5, transition="dissolve", trans_dur=1.4,
         sfx=[Sfx("night_bed", 0, -14, dur=13.5), Sfx("wall_glow", 2.0, -10), Sfx("wind_chime_hello", 3.0, -16)]),
]
