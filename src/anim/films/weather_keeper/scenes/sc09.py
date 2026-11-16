"""sc09 CODA (target 30 s). The notebook in Tara's hand; Ishaan walks to school under his own small
rain cloud; Meghnath, no cardigan, no sling, waters his chillies, and waves back."""
from __future__ import annotations

import math

import skia

from .... import core as K, fx
from ....core import W, H, fill, stroke, lerp, clamp
from ....timeline import Shot, Line, Sfx
from ..rig import draw, draw_bhaap
from ..sets import workshop, street, block
from ..sets import weather_fx as WX
from ._util_d import hand_pos, head_pos, schoolbag, lota_pour, notebook_spread, sparkle_burst, fit_beds


def sh01(cv, c):
    """Weeks later: the notebook lies open on the Monsoon Trunk. The new pages are Tara's."""
    t = c.t
    z = lerp(2.4, 2.65, K.ease_in_out(c.u))
    workshop.draw_workshop(cv, t, view="trunk", light="day", cloth=0.0, keys=(1, 1, 1), cam=(960, 830, z))
    with K.camera(cv, 960, 830, z):
        with K.lit(cv, "workshop", amount=0.35):
            notebook_spread(cv, 960, 830, 380, t)
        # a little glint where the newest drawing is
        if 1.0 < t < 3.5:
            sparkle_burst(cv, t, 1035, 800, a=0.8 * math.sin(math.pi * (t - 1.0) / 2.5), seed=3, spread=40,
                          color="#ffffff")
        # Bhaap peeks in from the top edge, curious, then sparks with pride
        peek = K.ease_out_back(c.seg(3.0, 4.0)) - K.ease_in(c.seg(5.4, 6.0))
        if peek > 0.01:
            draw_bhaap(cv, 1080, lerp(650, 740, peek), 0.55, t, mood="happy" if t > 4.2 else "shy",
                       mouth=0.3 if t > 4.2 else 0.0, spark=0.6 if 4.2 < t < 5.0 else 0.0)


def sh02(cv, c):
    """A hot bright day. Ishaan walks to school under Bhaap, who rains gently on him alone."""
    t = c.t
    scroll = t * 110
    street.draw_street(cv, t, "heat", scroll=scroll, kids=True)
    x, y, s = 860, street.WALK_Y + 60, 1.95
    wave = K.smooth(c.seg(5.6, 6.2)) * (1 - K.smooth(c.seg(8.0, 8.6)))
    look_side = t > 5.2
    with K.lit(cv, "heat", amount=0.6):
        schoolbag(cv, x - 8 * s, y - 175 * s, s * 0.95, t)
        draw(cv, "ishaan", x=x, y=y, s=s, t=t, legs="walk", phase=t * 0.95, turn=0.45 if not look_side else 0.8,
             expr="happy", look=(0.8, -0.2) if look_side else (0.2, -0.6),
             arms={"r": (lerp(10, 160, wave), lerp(14, 20, wave) + 18 * math.sin(t * 14) * wave)} if wave > 0.02 else {},
             hand={"r": "open"})
    hx, hy = head_pos("ishaan", x, y, s, turn=0.45)
    bx, by = hx + 6 * math.sin(t * 1.3), hy - 215 + 8 * math.sin(t * 2.0)
    # his personal drizzle, only on him: short bright streaks from Bhaap's belly to the ground
    r = K.rng(41)
    for i in range(34):
        sx = bx + r.uniform(-62, 62)
        sp = r.uniform(520, 760)
        span = (y - 6) - (by + 34)
        yy = by + 34 + ((r.random() * span + t * sp) % span)
        cv.drawLine(sx, yy, sx - 2, yy - 20, stroke("#3f86c6", 3.0, 0.75))
    for i in range(6):
        ph = (t * 1.8 + i / 6) % 1
        cv.drawCircle(x + r.uniform(-60, 60), y - 6 - ph * 12, 3.5 * (1 - ph), fill("#3f86c6", 0.7 * (1 - ph)))
    cv.drawOval(skia.Rect.MakeLTRB(x - 70, y - 10, x + 70, y + 10), fill("#5b8fb5", 0.35))
    draw_bhaap(cv, bx, by, 1.15, t, mood="happy", rain=0.0, mouth=0.25, spark=0.3 if wave > 0.5 else 0.0)


def _megh_balcony(cv, c, x_off=0.0, expr="angry", wave=0.0, water=0.0, mouth=0.0, cam=None):
    t = c.t
    x, y, s = block.TOP_ANCHOR
    px, py = block.TOP_POT
    cam = cam or (1000, 640, 1.2)
    with K.camera(cv, *cam):
        block.draw_block(cv, t, "heat", coda=True, view="top")
        arms = {"l": (lerp(30, 70, water), lerp(40, 10, water))}
        hold_l = "lota" if water > 0.05 else None
        if wave > 0.02:
            arms = {"r": (lerp(10, 150, wave), 20 + 14 * math.sin(t * 9) * wave), "l": (20, 20)}
            hold_l = None
        with K.lit(cv, "heat", amount=0.6):
            draw(cv, "meghnath", x=x + x_off, y=y, s=s, t=t, turn=0.15, expr=expr, mouth=mouth,
                 arms=arms, hand={"r": "open", "l": "fist"}, hold_l=hold_l, look=(0.0, 0.6),
                 extra={"cardigan": False, "brow_lift": -0.6 if expr == "angry" else 0.4})
        if water > 0.3 and hold_l:
            hx, hy = hand_pos("meghnath", x + x_off, y, s, "l", arms=arms)
            lota_pour(cv, hx - 18, hy + 10, px + 10, py - 30, t, a=K.smooth((water - 0.3) / 0.3))
        block.draw_top_rail(cv, t, "heat", coda=True)


def sh03(cv, c):
    """Top-floor balcony: Meghnath, short sleeves, no sling, waters his pot of green chillies."""
    _megh_balcony(cv, c, expr="neutral", water=K.smooth(c.seg(0.5, 1.5)), cam=(1000, 650, lerp(1.15, 1.25, c.u)))


def sh04(cv, c):
    """Below, in the courtyard, Rehan and Tara wave up: 'Morning, Meghnath Uncle!'"""
    t = c.t
    with K.camera(cv, 960, lerp(860, 840, c.u), 2.3):
        block.draw_block(cv, t, "heat", coda=True, view="wide")
    wv = 14 * math.sin(t * 10)
    with K.lit(cv, "heat", amount=0.6):
        draw(cv, "tara", x=760, y=1110, s=1.75, t=t, turn=0.3, expr="happy", look=(0.3, -1), head_tilt=-8,
             arms={"r": (160, 20 + wv), "l": (15, 30)}, hand={"r": "open"})
        draw(cv, "rehan", x=1130, y=1120, s=1.8, t=t, flip=True, turn=0.3, expr="grin", mouth=c.mouth("rehan"),
             look=(-0.3, -1), head_tilt=8, arms={"r": (165, 15 - wv), "l": (160, 15 + wv)}, hand={"r": "open", "l": "open"})


def sh05(cv, c):
    """He scowls... then waves back."""
    t = c.t
    T_WAVE = 2.8
    wave = K.ease_out_back(c.seg(T_WAVE, T_WAVE + 0.7), 1.2)
    expr = "angry" if t < T_WAVE - 0.3 else "happy"
    x, y, s = block.TOP_ANCHOR
    _megh_balcony(cv, c, expr=expr, wave=wave, cam=(x - 20, y - 400, lerp(2.0, 2.2, c.u)))


SHOTS = fit_beds([
    Shot("S09_SH01", sh01, duration=6.0, music="coda", transition="fade_white", trans_dur=1.2,
         sfx=[Sfx("workshop_ambience", 0, -14, dur=6.0), Sfx("page_turn", 0.6, -10), Sfx("bhaap_coo", 3.4, -12),
              Sfx("spark_tzik", 4.3, -14)]),
    Shot("S09_SH02", sh02, duration=9.0, transition="dissolve", trans_dur=0.8,
         sfx=[Sfx("heat_bed", 0, -16, dur=9.0), Sfx("bhaap_drizzle", 0, -12, dur=9.0), Sfx("footsteps_soft", 0.2, -18),
              Sfx("school_bell", 6.8, -16), Sfx("bhaap_giggle", 6.0, -12)]),
    Shot("S09_SH03", sh03, duration=4.5,
         sfx=[Sfx("heat_bed", 0, -18, dur=4.5), Sfx("chilli_watering", 1.0, -8)]),
    Shot("S09_SH04", sh04, duration=None, tail=1.0,
         lines=[Line("rehan", "Morning, Meghnath Uncle!", at=0.6)],
         sfx=[Sfx("heat_bed", 0, -18, dur=3.2)]),
    Shot("S09_SH05", sh05, duration=6.5,
         sfx=[Sfx("heat_bed", 0, -18, dur=6.5)]),
])
