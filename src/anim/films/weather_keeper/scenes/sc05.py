"""WK sc05 - THE MIDPOINT. Target 120 s.

The sky-picture calendar: the monsoon is overdue. The Monsoon Trunk revealed: three keyholes too far
apart for one old man. "It needs three. It always needed three." Varsha's memory (silhouettes, the
4-note monsoon hint). "I'm done." "GO HOME." Bhaap stays on his shoulder and drizzles.
"""
from __future__ import annotations

import math

import skia

from .... import core as K, fx
from ....core import fill, stroke, lerp, clamp, ease_in_out, ease_out, ease_out_back, seg
from ....timeline import Shot, Line, Sfx
from ..rig import draw, draw_bhaap, draw_varsha_photo, draw_silhouette, draw_key
from ..sets import roof as R, workshop as WS
from ._util_b import bed, finalize, head_top, head_world, hand_world, clamp_view

SLING = {"sling": True}
TX, TY, TS = WS.TRUNK
KEYHOLES = R.trunk_keyholes(TX, TY, TS)
SEAT = (TX + 10, TY - 150)          # sitting on the trunk lid edge
FLOOR = WS.FLOOR_Y


def _ws(cv, c, camv, **kw):
    WS.draw_workshop(cv, c.t, "wide", light="day", cam=camv, **kw)


def _push(c, cx, cy, z0, z1, dx=0.0, dy=0.0):
    e = ease_in_out(c.u)
    return clamp_view(cx + dx * e, cy + dy * e, lerp(z0, z1, e))


def _veil(cv, a=0.25, col="#0b1424"):
    cv.save(); cv.resetMatrix()
    cv.drawRect(skia.Rect.MakeWH(K.W, K.H), fill(col, a))
    cv.restore()


# ------------------------------------------------------------------ the calendar
def sh_calendar(cv, c):
    t = c.t
    x, y, w, h = WS.CALENDAR
    camv = clamp_view(lerp(x + 40, x + w - 30, ease_in_out(c.u)), y + h * 0.48, 3.0)
    WS.draw_workshop(cv, t, "calendar", light="day", cloth=1.0, cam=camv)
    with K.camera(cv, *camv):
        # the long-past cloud sticker gets a little sad pulse
        pulse = math.sin(seg(t, 4.0, 6.5) * math.pi)
        if pulse > 0:
            fx.chime_rings(cv, x + w - 38, y + 70, 4.0, t, color="#ffffff", n=2, max_r=40, a=0.7)


def sh_late(cv, c):
    t = c.t
    camv = _push(c, 560, 640, 1.9, 2.0)
    _ws(cv, c, camv, cloth=1.0)
    with K.camera(cv, *camv):
        with K.lit(cv, "workshop", amount=0.55):
            draw(cv, "tara", x=560, y=FLOOR, s=1.3, t=t, hold="notebook", arms={"r": (40, 110)},
                 mouth=c.mouth("tara"), expr="worried", look=(-0.6, -0.8) if t < 1.2 else (0.9, -0.1),
                 head_tilt=-6 if t < 1.2 else 4)
            draw(cv, "rehan", x=330, y=FLOOR + 6, s=1.3, t=t, expr="worried", look=(1, -0.2), hand={"r": "ball"})


def sh_pull_cloth(cv, c):
    """He doesn't answer. He goes to the big shape and pulls the cloth away."""
    t = c.t
    camv = _push(c, 960, 640, 1.2, 1.28)
    walk = ease_in_out(seg(t, 0.3, 2.8))
    pull = ease_in_out(seg(t, 3.2, 4.4))
    _ws(cv, c, camv, cloth=1.0 - pull)
    with K.camera(cv, *camv):
        with K.lit(cv, "workshop", amount=0.55):
            mx = lerp(1400, 1220, walk)
            draw(cv, "meghnath", x=mx, y=FLOOR, s=1.25, t=t, legs="walk" if 0 < walk < 1 else "stand",
                 phase=t * 0.55, flip=True, extra=dict(SLING, brow_lift=-0.6),
                 arms={"l": (lerp(20, 95, seg(t, 2.8, 3.2)) - 70 * pull, 20)}, look=(-0.5, 0.4))
            draw(cv, "tara", x=470, y=FLOOR, s=1.22, t=t, hold="notebook", expr="surprised" if t > 4.2 else "worried",
                 look=(1, 0), arms={"r": (40, 110)})
            draw(cv, "ishaan", x=640, y=FLOOR + 8, s=1.22, t=t, expr="awe" if t > 4.2 else "neutral", look=(1, -0.2))
        if 4.0 < t < 6.5:
            u = seg(t, 4.0, 6.5)
            for k in range(8):
                ang = k * 0.8
                cv.drawCircle(TX + math.cos(ang) * (80 + 260 * u), TY - 80 - u * 120 + math.sin(ang) * 40,
                              30 + 40 * u, fill("#cfd6dd", 0.35 * (1 - u)))


def sh_trunk_reveal(cv, c):
    t = c.t
    camv = _push(c, 960, 760, 1.6, 1.8, dy=-20)
    _ws(cv, c, camv, cloth=0.0)
    with K.camera(cv, *camv):
        for i, (kx, ky) in enumerate(KEYHOLES):
            g = math.sin(seg(t, 1.5 + i * 0.7, 2.6 + i * 0.7) * math.pi)
            if g > 0:
                fx.star4(cv, kx, ky, 18 * g, "#e8f4ff", g)
        fx.motes(cv, t, (600, 300, 1320, 900), n=30, color="#e6f2ff", a=0.5, seed=12)
        with K.lit(cv, "workshop", amount=0.55):
            draw(cv, "rehan", x=1330, y=FLOOR + 40, s=1.5, t=t, flip=True, expr="awe", look=(-1, -0.4), hand={"r": "ball"})


def sh_keys(cv, c):
    """Three iron keys from the hook."""
    t = c.t
    kx, ky = WS.KEYS_HOOK
    camv = clamp_view(kx + 40, ky + 140, 2.4)
    take = [seg(t, 0.8 + i * 0.9, 1.3 + i * 0.9) for i in range(3)]
    keys = tuple(1 if u < 0.5 else 0 for u in take)
    WS.draw_workshop(cv, t, "wide", light="day", cloth=0.0, keys=keys, cam=camv)
    reach = 0.2 + 0.8 * math.sin(clamp(t / 4.0) * math.pi)
    with K.camera(cv, *camv):
        with K.lit(cv, "workshop", amount=0.55):
            draw(cv, "meghnath", x=kx + 150, y=FLOOR, s=1.3, t=t, flip=True, look=(-0.6, -1),
                 arms={"l": (lerp(30, 160, reach), lerp(20, 30, reach))}, hold_l="key" if t > 1.3 else None,
                 extra=dict(SLING, brow_lift=-0.3))


def sh_stretch(cv, c):
    """He tries to stretch from one keyhole to another. Can't."""
    t = c.t
    camv = _push(c, 960, 760, 1.55, 1.62)
    insert = seg(t, 0.6, 1.6)
    _ws(cv, c, camv, cloth=0.0, keys=(0, 0, 0), trunk_keys=(0.45 * insert, 0, 0))
    strain = ease_in_out(seg(t, 2.0, 4.4)) * (1 - ease_in_out(seg(t, 5.4, 6.4)))
    (k1x, k1y), (k2x, k2y), _ = KEYHOLES
    with K.camera(cv, *camv):
        with K.lit(cv, "workshop", amount=0.55):
            x = lerp(k1x - 40, k1x + 40, strain)
            draw(cv, "meghnath", x=x, y=FLOOR, s=1.25, t=t, lean=lerp(0, 18, strain), look=(1, 0.3),
                 arms={"l": (lerp(70, 120, strain), lerp(60, 0, strain))}, hand={"l": "open"},
                 extra=dict(SLING, brow_lift=lerp(-0.2, 0.9, strain)),
                 expr="wince" if strain > 0.5 else ("sad" if t > 5.5 else "determined"))
            # the gap he can't close
        if strain > 0.6:
            hx = k1x + 40 + 200 * strain
            cv.drawLine(hx + 20, k2y - 10, k2x - 30, k2y - 10, stroke("#ffffff", 3, 0.5 * strain))


def sh_sit_needs_three(cv, c):
    t = c.t
    camv = _push(c, 960, 700, 1.7, 1.8)
    _ws(cv, c, camv, cloth=0.0, keys=(0, 0, 0), trunk_keys=(0.45, 0, 0))
    down = ease_out(seg(t, 0.0, 0.7))
    with K.camera(cv, *camv):
        with K.lit(cv, "workshop", amount=0.55):
            draw(cv, "meghnath", x=SEAT[0], y=lerp(SEAT[1] - 60, SEAT[1], down), s=1.25, t=t, legs="sit",
                 mouth=c.mouth("meghnath"), look=(0, 0.6), head_tilt=8, hold_l="key",
                 arms={"l": (15, 40)}, extra=dict(SLING, brow_lift=-0.8), expr="sad")


def sh_photo(cv, c):
    t = c.t
    camv = clamp_view(1380, 500, 3.2 + 0.15 * c.u)
    WS.draw_workshop(cv, t, "photo", light="day", cloth=0.0, keys=(0, 0, 0), cam=camv)
    with K.camera(cv, *camv):
        px, py = WS.PHOTO_POS
        draw_varsha_photo(cv, px, py, s=0.85, t=t)


def sh_always_three(cv, c):
    t = c.t
    camv = _push(c, 1010, 590, 2.5, 2.6)
    _ws(cv, c, camv, cloth=0.0, keys=(0, 0, 0), trunk_keys=(0.45, 0, 0))
    with K.camera(cv, *camv):
        with K.lit(cv, "workshop", amount=0.55):
            draw(cv, "meghnath", x=SEAT[0], y=SEAT[1], s=1.25, t=t, legs="sit", mouth=c.mouth("meghnath"),
                 look=(1, -0.6), head_tilt=-4, turn=0.6, arms={"l": (15, 40)}, hold_l="key",
                 extra=dict(SLING, brow_lift=-0.9), expr="sad", blink=0.35)


def sh_ishaan_looks(cv, c):
    t = c.t
    camv = _push(c, 600, 640, 2.1, 2.2)
    _ws(cv, c, camv, cloth=0.0, keys=(0, 0, 0))
    look = (1, -0.6) if t < 1.6 else (-1, 0.1) if t < 3.2 else (1, -0.2)
    with K.camera(cv, *camv):
        with K.lit(cv, "workshop", amount=0.55):
            draw(cv, "ishaan", x=600, y=FLOOR, s=1.3, t=t, expr="sad" if t > 3.2 else "neutral", look=look,
                 head_tilt=6 if t > 3.2 else 0)


def sh_three_look(cv, c):
    """Three of them. They glance at each other (a seed planted)."""
    t = c.t
    camv = _push(c, 520, 660, 1.6, 1.68)
    _ws(cv, c, camv, cloth=0.0, keys=(0, 0, 0))
    with K.camera(cv, *camv):
        with K.lit(cv, "workshop", amount=0.55):
            looks = {"tara": [(1, -0.3), (1, 0), (-1, 0)], "rehan": [(1, -0.3), (-1, 0), (1, 0)],
                     "ishaan": [(1, -0.3), (-1, 0), (-1, 0)]}
            ph = 0 if t < 1.4 else 1 if t < 3.0 else 2
            for who, x in (("rehan", 300), ("tara", 520), ("ishaan", 720)):
                draw(cv, who, x=x, y=FLOOR + (8 if who == "ishaan" else 0), s=1.25, t=t, look=looks[who][ph],
                     expr="worried" if ph < 2 else "neutral", hold="notebook" if who == "tara" else None,
                     hand={"r": "ball"} if who == "rehan" else {}, head_tilt=4 * (ph == 2))


def sh_bhaap_settles(cv, c):
    t = c.t
    camv = _push(c, 1000, 620, 2.1, 2.2)
    _ws(cv, c, camv, cloth=0.0, keys=(0, 0, 0), trunk_keys=(0.45, 0, 0))
    u = ease_in_out(seg(t, 0.4, 3.6))
    with K.camera(cv, *camv):
        with K.lit(cv, "workshop", amount=0.55):
            draw(cv, "meghnath", x=SEAT[0], y=SEAT[1], s=1.25, t=t, legs="sit", look=(0.7, -0.4) if u > 0.9 else (0, 0.6),
                 arms={"l": (15, 40)}, hold_l="key", extra=dict(SLING, brow_lift=-0.6 + 0.4 * seg(t, 3.8, 4.8)),
                 expr="sad" if t < 4.2 else "happy", head_tilt=6)
        hx, hy = head_world("meghnath", SEAT[0], SEAT[1], 1.25, sit=True)
        sx, sy = hx + 70, hy + 70          # his far shoulder
        draw_bhaap(cv, lerp(sx + 140, sx, u), lerp(sy - 260, sy - 18, u), s=0.62, t=t, mood="shy" if u < 1 else "sleepy",
                   squash=0.2 * seg(t, 3.4, 3.8))


# ------------------------------------------------------------------ the memory (silhouettes)
MEM_COL = "#1d1430"


def _purple_sky(cv, t):
    cv.drawRect(skia.Rect.MakeWH(K.W, K.H), K.lin((0, 0), (0, K.H), ["#1c1033", "#3e2550", "#7a4a6e", "#b07a7a"],
                                                  [0, 0.45, 0.8, 1]))
    K.stars(cv, K.W, K.H * 0.55, t, n=90, seed=44, alpha=0.6)
    # heavy bruised clouds (the monsoon about to come)
    for (x, y, r) in ((300, 300, 160), (520, 260, 190), (1500, 280, 200), (1720, 330, 150), (1050, 220, 140)):
        cv.drawPath(K.ellipse(x, y, r * 2.2, r * 0.55), fill("#2c1a40", 0.45))
        cv.drawPath(K.ellipse(x - r * 0.3, y - r * 0.2, r * 1.2, r * 0.25), fill("#6a4a7a", 0.25))
    # rooftop silhouette line + tanks
    cv.drawRect(skia.Rect.MakeXYWH(0, 860, K.W, 220), fill(MEM_COL))
    for (x, w, h) in ((140, 120, 120), (290, 90, 90), (1620, 140, 150), (1790, 100, 100)):
        cv.drawRect(skia.Rect.MakeXYWH(x, 860 - h, w, h), fill(MEM_COL))
    for x in (520, 1420):
        cv.drawLine(x, 860, x, 620, stroke(MEM_COL, 6))
        cv.drawLine(x - 50, 650, x + 50, 650, stroke(MEM_COL, 5))


def sh_memory(cv, c):
    t = c.t
    camv = clamp_view(960, 560, lerp(1.0, 1.08, ease_in_out(c.u)))
    with K.camera(cv, *camv):
        _purple_sky(cv, t)
        tx, ty, ts = 960, 900, 1.25
        holes = R.trunk_keyholes(tx, ty, ts)
        k = [ease_in_out(seg(t, 2.5, 4.5)), ease_in_out(seg(t, 3.0, 5.0)), ease_in_out(seg(t, 3.6, 6.4))]
        lid = ease_in_out(seg(t, 6.6, 10.0))
        m = [0, 0, 0, 0, K.hexrgb(MEM_COL)[0], 0, 0, 0, 0, K.hexrgb(MEM_COL)[1], 0, 0, 0, 0, K.hexrgb(MEM_COL)[2],
             0, 0, 0, 1, 0]
        with K.layer(cv, color_filter=K.matrix_filter(m)):
            R.draw_monsoon_trunk(cv, tx, ty, ts, t, lid=lid, keys=(0.5 + 0.5 * k[0], 0.5 + 0.5 * k[1], 0.5 + 0.5 * k[2]))
        # light spilling out of the lid
        if lid > 0.05:
            fx.light_rays(cv, tx, ty - 330 * ts, -90, spread_deg=70, length=900, color="#e8d8ff", a=0.35 * lid, n=9, t=t)
            fx.glow_dot(cv, tx, ty - 300 * ts, 360 * lid, "#e8d8ff", 0.6 * lid)
            for i in range(6):
                u = (t * 0.3 + i / 6) % 1
                cv.drawCircle(tx + math.sin(i * 2.1 + t) * 90 * u, ty - 330 * ts - u * 420, 30 + 50 * u,
                              fill("#5a6a8a", 0.5 * lid * (1 - u)))
        # the two of them, laughing, each turning a key
        (l1x, l1y), (l2x, l2y), (l3x, l3y) = holes
        draw_silhouette(cv, "meghnath", l1x - 110, 900, 1.35, color=MEM_COL, arms={"l": (60, 30), "r": (95, 10 + 20 * k[0])},
                        head_tilt=-6 + 8 * math.sin(t * 2.4) * seg(t, 7, 9), flip=False)
        draw_silhouette(cv, "varsha", l2x + 110, 900, 1.3, color=MEM_COL, arms={"l": (95, 10 + 20 * k[1]), "r": (40, 30)},
                        head_tilt=6 + 8 * math.sin(t * 2.6 + 1) * seg(t, 7, 9), flip=False)
        # tiny Bhaap turning the third key with his whole body
        bx, by = l3x + 40 - 30 * k[2], l3y - 40
        draw_bhaap(cv, bx, by, s=0.55, t=t, mood="excited" if lid > 0.3 else "happy", squash=0.4 * math.sin(t * 8) * (1 - lid),
                   spark=0.8 * lid, alpha=0.9)
    # memory edges: soft dark vignette
    cv.save(); cv.resetMatrix()
    cv.drawRect(skia.Rect.MakeWH(K.W, K.H), K.rad_a((K.W / 2, K.H / 2), 1100, [("#000000", 0), ("#0b0518", 0.6)], [0.55, 1]))
    cv.restore()


# ------------------------------------------------------------------ back: done
def sh_done(cv, c):
    t = c.t
    camv = _push(c, 1000, 600, 2.3, 2.45)
    _ws(cv, c, camv, cloth=0.0, keys=(0, 0, 0), trunk_keys=(0.45, 0, 0))
    with K.camera(cv, *camv):
        with K.lit(cv, "workshop", amount=0.55):
            draw(cv, "meghnath", x=SEAT[0], y=SEAT[1], s=1.25, t=t, legs="sit", mouth=c.mouth("meghnath"),
                 look=(-0.3, 0.5), head_tilt=6, arms={"l": (15, 40)}, hold_l="key",
                 extra=dict(SLING, brow_lift=-1.0), expr="sad", blink=0.4)
        hx, hy = head_world("meghnath", SEAT[0], SEAT[1], 1.25, sit=True)
        draw_bhaap(cv, hx + 70, hy + 52, s=0.62, t=t, mood="sad", blink=0.0)


def sh_hang_keys(cv, c):
    t = c.t
    kx, ky = WS.KEYS_HOOK
    camv = clamp_view(kx + 40, ky + 140, 2.4)
    put = [seg(t, 1.0 + i * 0.8, 1.5 + i * 0.8) for i in range(3)]
    keys = tuple(1 if u >= 0.5 else 0 for u in put)
    WS.draw_workshop(cv, t, "wide", light="day", cloth=0.0, keys=keys, cam=camv)
    reach = 0.3 + 0.7 * math.sin(clamp((t - 0.4) / 3.6) * math.pi)
    with K.camera(cv, *camv):
        with K.lit(cv, "workshop", amount=0.55):
            draw(cv, "meghnath", x=kx + 150, y=FLOOR, s=1.3, t=t, flip=True, look=(-0.6, -1),
                 arms={"l": (lerp(30, 160, reach), 25)}, hold_l="key" if t < 3.0 else None,
                 extra=dict(SLING, brow_lift=-0.8), expr="sad")


def sh_but_it_cant(cv, c):
    t = c.t
    camv = _push(c, 500, 640, 1.9, 2.0)
    _ws(cv, c, camv, cloth=0.0, keys=(1, 1, 1))
    with K.camera(cv, *camv):
        with K.lit(cv, "workshop", amount=0.55):
            draw(cv, "tara", x=560, y=FLOOR, s=1.3, t=t, hold="notebook", arms={"r": (40, 110), "l": (70, 40)},
                 mouth=c.mouth("tara"), expr="angry" if t > 0.6 else "worried", look=(1, -0.3), lean=6)
            draw(cv, "ishaan", x=330, y=FLOOR + 8, s=1.3, t=t, expr="worried", look=(1, -0.3))


def sh_go_home(cv, c):
    t = c.t
    camv = clamp_view(1000, 620, 2.5)
    _ws(cv, c, camv, cloth=0.0, keys=(1, 1, 1), trunk_keys=(0.45, 0, 0))
    with K.camera(cv, *camv):
        with K.lit(cv, "workshop", amount=0.55):
            draw(cv, "meghnath", x=SEAT[0], y=SEAT[1], s=1.25, t=t, legs="sit", mouth=c.mouth("meghnath"),
                 look=(-1, -0.1), head_tilt=-4, arms={"l": (15, 40)},
                 extra=dict(SLING, brow_lift=-0.4 if t < 1.4 else -1.0), expr="angry" if t < 1.4 else "sad")
        hx, hy = head_world("meghnath", SEAT[0], SEAT[1], 1.25, sit=True)
        draw_bhaap(cv, hx + 70, hy + 52, s=0.62, t=t, mood="sad", blink=0.0)


def sh_kids_go(cv, c):
    t = c.t
    camv = clamp_view(900, 620, 1.3)
    _ws(cv, c, camv, cloth=0.0, keys=(1, 1, 1))
    with K.camera(cv, *camv):
        with K.lit(cv, "workshop", amount=0.55):
            for i, who in enumerate(("tara", "rehan", "ishaan")):
                u = ease_in_out(seg(t, 0.3 + i * 0.5, 5.0 + i * 0.4))
                x = lerp(760 - i * 180, 160 - i * 180, u)
                look_back = (who == "ishaan" and 1.5 < t < 3.5)
                draw(cv, who, x=x, y=FLOOR, s=1.22, t=t, flip=not look_back, legs="walk" if 0 < u < 1 else "stand",
                     phase=t * 0.8 + i * 0.3, expr="sad", look=(1, -0.2) if look_back else (0, 0.3))


def sh_alone_drizzle(cv, c):
    t = c.t
    camv = _push(c, 980, 640, 1.6, 1.8)
    _ws(cv, c, camv, cloth=0.0, keys=(1, 1, 1), trunk_keys=(0.45, 0, 0))
    _veil(cv, 0.15 + 0.2 * c.u)
    with K.camera(cv, *camv):
        with K.lit(cv, "workshop", amount=0.55):
            draw(cv, "meghnath", x=SEAT[0], y=SEAT[1], s=1.25, t=t, legs="sit", look=(-0.3, 0.7), head_tilt=10,
                 arms={"l": (15, 40)}, extra=dict(SLING, brow_lift=-1.0), expr="sad", blink=0.5)
        hx, hy = head_world("meghnath", SEAT[0], SEAT[1], 1.25, sit=True)
        draw_bhaap(cv, hx + 70, hy + 52, s=0.62, t=t, mood="sad", rain=0.35 + 0.25 * seg(t, 2, 4), blink=0.0)


# ------------------------------------------------------------------ shot list
_S = [
    Shot("A", sh_calendar, duration=7.5, music="overdue", transition="fade_black", trans_dur=1.4,
         sfx=[bed("workshop_ambience", gain=-16), Sfx("calendar_flip", 4.0, -10)]),
    Shot("A", sh_late, duration=None, tail=1.6, lines=[Line("tara", "The monsoon's late. It's very late.", at=1.0)],
         sfx=[bed("workshop_ambience", gain=-16)]),
    Shot("A", sh_pull_cloth, duration=8.0, music="trunk_reveal", music_hits=[4.0, 5.6],
         sfx=[bed("workshop_ambience", gain=-16), Sfx("footsteps_slipper", 0.4, -14), Sfx("whoosh", 3.6, -8),
              Sfx("cloud_puff", 4.1, -8)]),
    Shot("A", sh_trunk_reveal, duration=7.0, sfx=[bed("workshop_ambience", gain=-18), Sfx("sparkle", 1.6, -14),
                                                   Sfx("sparkle", 2.3, -14), Sfx("sparkle", 3.0, -14)]),
    Shot("A", sh_keys, duration=4.8, sfx=[bed("workshop_ambience", gain=-18), Sfx("key_turn_clack", 1.0, -16),
                                          Sfx("key_turn_clack", 1.9, -16), Sfx("key_turn_clack", 2.8, -16)]),
    Shot("A", sh_stretch, duration=7.2, sfx=[bed("workshop_ambience", gain=-18), Sfx("key_click", 1.4, -10)]),
    Shot("A", sh_sit_needs_three, duration=None, tail=1.6, lines=[Line("meghnath", "It needs three.", at=1.4)],
         sfx=[bed("workshop_ambience", gain=-18), Sfx("klang", 0.5, -20)]),
    Shot("A", sh_photo, duration=4.5, sfx=[bed("workshop_ambience", gain=-20)]),
    Shot("A", sh_always_three, duration=None, tail=1.8, lines=[Line("meghnath", "It always needed three.", at=0.9)],
         sfx=[bed("workshop_ambience", gain=-20)]),
    Shot("A", sh_ishaan_looks, duration=4.8, sfx=[bed("workshop_ambience", gain=-20)]),
    Shot("A", sh_three_look, duration=4.6, sfx=[bed("workshop_ambience", gain=-20)]),
    Shot("A", sh_bhaap_settles, duration=6.2, sfx=[bed("workshop_ambience", gain=-20), Sfx("bhaap_coo", 3.4, -10)]),
    Shot("A", sh_memory, duration=16.0, music="varsha_memory", music_hits=[1.0], transition="dissolve", trans_dur=1.4,
         sfx=[bed("night_bed_delhi", gain=-22), Sfx("key_turn_clack", 4.5, -14), Sfx("key_turn_clack", 5.0, -14),
              Sfx("key_turn_clack", 6.4, -12), Sfx("trunk_lid_rise", 6.8, -10), Sfx("thunder", 9.0, -16,
                                                                                    params={"dist": 1.0})]),
    Shot("A", sh_done, duration=None, tail=1.6, music="", transition="dissolve", trans_dur=1.2,
         lines=[Line("meghnath", "I'm done. I'm old. The city can manage on its own now.", at=1.2)],
         sfx=[bed("workshop_ambience", gain=-20)]),
    Shot("A", sh_hang_keys, duration=4.6, sfx=[bed("workshop_ambience", gain=-20), Sfx("key_turn_clack", 1.3, -16),
                                               Sfx("key_turn_clack", 2.1, -16), Sfx("key_turn_clack", 2.9, -16)]),
    Shot("A", sh_but_it_cant, duration=None, tail=0.05,
         lines=[Line("tara", "But it can't! It's too hot. People are—", at=0.4)],
         sfx=[bed("workshop_ambience", gain=-20)]),
    Shot("A", sh_go_home, duration=None, tail=1.8, lines=[Line("meghnath", "GO HOME.", at=0.1)],
         sfx=[bed("workshop_ambience", gain=-20)]),
    Shot("A", sh_kids_go, duration=6.0, music="go_home",
         sfx=[bed("workshop_ambience", gain=-20), Sfx("footsteps_soft", 0.4, -16), Sfx("metal_hatch", 5.4, -14)]),
    Shot("A", sh_alone_drizzle, duration=11.0, sfx=[bed("workshop_ambience", gain=-20),
                                                     Sfx("bhaap_drizzle", 0.5, -12, dur=9.0)]),
]

SHOTS = finalize(_S, 5)
