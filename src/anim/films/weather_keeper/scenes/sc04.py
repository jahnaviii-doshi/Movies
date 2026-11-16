"""WK sc04 - APPRENTICESHIP (montage). Target 180 s.

Dawn kites -> a breeze in a bottle -> sweeping the smog into sacks -> Tara's notebook ->
Ishaan & Bhaap inseparable -> Meghnath's slow demo -> Rehan spins too fast -> the hail cloud over
the cricket match -> deadpan aftermath -> night: Meghnath alone with Varsha's photo.
"""
from __future__ import annotations

import math

import skia

from .... import core as K, fx
from ....core import fill, stroke, lerp, clamp, ease_in_out, ease_out, ease_out_back, seg
from ....timeline import Shot, Line, Sfx
from ..rig import (draw, draw_bhaap, draw_pigeon, draw_kite, draw_breeze_jar, draw_sack, draw_varsha_photo,
                   draw_pressure_cooker, draw_stove)
from ..sets import roof as R, workshop as WS, ground as G
from ..sets import weather_fx as WF
from ._util_b import (bed, finalize, head_top, head_world, hand_world, clamp_view, breeze_ribbon, dark_cloud,
                      notebook_page, pencil, smog_puff, sleeve_cuff, toe_ouch)

SLING = {"sling": True}


def _roof(cv, c, weather, camv, **kw):
    R.draw_roof(cv, c.t, weather, cam=camv, **kw)


def _push(c, cx, cy, z0, z1, dx=0.0, dy=0.0):
    e = ease_in_out(c.u)
    return clamp_view(cx + dx * e, cy + dy * e, lerp(z0, z1, e))


def _kite_pos(base, t, mode, k):
    x, y = base
    if mode == "steady":
        return (x + math.sin(t * 0.8 + k) * 6, y + math.sin(t * 1.1 + k) * 4), math.sin(t * 0.9) * 4
    if mode == "wild":
        return (x + math.sin(t * 2.6 + k) * 160, y + math.sin(t * 3.4 + k) * 90 + math.cos(t * 1.7) * 40), \
            math.sin(t * 3.0) * 40
    return (x + math.sin(t * 0.4 + k) * 40, y + math.sin(t * 0.6 + k) * 30), math.sin(t * 0.5) * 12


# ============================================================ dawn kites
def sh_arrive(cv, c):
    """Dawn: the three stumble out of the stair hut, yawning; Meghnath already waits with kites."""
    t = c.t
    camv = _push(c, 700, 640, 1.25, 1.32, dx=40)
    _roof(cv, c, "evening", camv)
    with K.camera(cv, *camv):
        dx, dy, ds = R.ANCHORS["stair_door"]
        with K.lit(cv, "heat_dusk"):
            for i, (who, delay, expr) in enumerate((("tara", 0.4, "neutral"), ("rehan", 1.2, "sleepy"),
                                                     ("ishaan", 2.2, "sleepy"))):
                u = seg(t, delay, delay + 3.4)
                y = lerp(dy + 10, dy + 150 + i * 40, u)
                x = lerp(dx + 10, dx + 330 + i * 230, u)
                s = R.roof_scale(y) * 0.95
                yawn = 0.9 if (who != "tara" and 1.0 < t - delay < 2.3) else 0.0
                draw(cv, who, x=x, y=y, s=s, t=t, legs="walk" if 0 < u < 1 else "stand", phase=t * 0.9 + i * 0.3,
                     expr="sleepy" if yawn else ("smug" if who == "tara" else expr), mouth=yawn,
                     arms={"l": (150, 30)} if yawn else {}, hold="notebook" if who == "tara" else None,
                     alpha=clamp((t - delay) * 3))


def sh_kites_wide(cv, c):
    t = c.t
    camv = _push(c, 960, 520, 1.0, 1.07, dy=-20)
    _roof(cv, c, "evening", camv)
    rise = ease_out(seg(t, 0.5, 5.0))
    kids = (("tara", 820, 930, "#e0413a", "steady", (760, 170)),
            ("rehan", 1110, 920, "#3a7bd5", "wild", (1180, 210)),
            ("ishaan", 1400, 980, "#f2c230", "float", (1560, 260)))
    with K.camera(cv, *camv):
        hands = []
        with K.lit(cv, "heat_dusk"):
            for i, (who, x, y, col, mode, top) in enumerate(kids):
                s = R.roof_scale(y)
                arms = {"r": (150 + math.sin(t * 2 + i) * (12 if mode == "wild" else 3), 25)}
                draw(cv, who, x=x, y=y, s=s, t=t, arms=arms, hold="kite_spool", look=(0.2, -1),
                     expr={"tara": "smug", "rehan": "determined", "ishaan": "happy"}[who],
                     lean=(math.sin(t * 3) * 6 if mode == "wild" else 0))
                hands.append(hand_world(who, x, y, s, "r", arms["r"]))
        for i, (who, x, y, col, mode, top) in enumerate(kids):
            (kx, ky), rot = _kite_pos(top, t, mode, i)
            kx, ky = lerp(hands[i][0] + 40, kx, rise), lerp(hands[i][1] - 60, ky, rise)
            draw_kite(cv, kx, ky, s=1.05, rot=rot, color=col, t=t, string_to=hands[i])
        draw_bhaap(cv, 1480, 690 + math.sin(t * 2) * 8, s=0.7, t=t, mood="sleepy" if t < 3 else "happy")


def sh_tara_steady(cv, c):
    t = c.t
    camv = _push(c, 830, 640, 2.0, 2.1)
    _roof(cv, c, "evening", camv)
    x, y = 830, 930
    s = R.roof_scale(y)
    arms = {"r": (150, 20), "l": (35, 120) if 1.6 < t < 3.8 else (10, 20)}
    with K.camera(cv, *camv):
        with K.lit(cv, "heat_dusk"):
            draw(cv, "tara", x=x, y=y, s=s, t=t, arms=arms, hold="kite_spool",
                 look=(-0.6, 0.6) if 1.6 < t < 3.8 else (0.2, -1),
                 head_tilt=6 if 1.6 < t < 3.8 else -4, expr="smug" if t > 3.8 else "neutral")
        hx, hy = hand_world("tara", x, y, s, "r", arms["r"])
        cv.drawLine(hx, hy, hx + 220, hy - 700, stroke("#f4f0e6", 2))


def sh_rehan_dragged(cv, c):
    """The kite yanks; Rehan is dragged across the roof on his tummy."""
    t = c.t
    camv = clamp_view(lerp(1250, 700, ease_in_out(seg(t, 1.2, 6.0))), 700, 1.35)
    _roof(cv, c, "evening", camv)
    yank = seg(t, 1.0, 1.6)
    drag = ease_in_out(seg(t, 1.5, 6.2))
    with K.camera(cv, *camv):
        y = 960
        s = R.roof_scale(y)
        if t < 1.5:
            x = 1350 - yank * 40
            arms = {"r": (160, 10), "l": (160, 10)}
            with K.lit(cv, "heat_dusk"):
                draw(cv, "rehan", x=x, y=y, s=s, t=t, arms=arms, hold="kite_spool", lean=-18 * yank + math.sin(t * 9) * 4,
                     expr="surprised" if t > 0.9 else "determined", legs="tiptoe" if t > 0.9 else "stand",
                     look=(-1, -0.8), flip=True)
            hand = hand_world("rehan", x, y, s, "r", arms["r"], flip=True)
        else:
            x = lerp(1310, 520, drag)
            # lying on his tummy, being towed head-first (to the left)
            cv.save()
            cv.translate(x, y - 40)
            cv.rotate(-90 + math.sin(t * 7) * 3)
            with K.lit(cv, "heat_dusk"):
                draw(cv, "rehan", x=0, y=0, s=s, t=t, arms={"r": (175, 0), "l": (175, 0)}, hold="kite_spool",
                     legs="float", expr="surprised", mouth=0.6 + 0.3 * math.sin(t * 9), flip=True)
            cv.restore()
            hand = (x - 330 * s, y - 40)
            for k in range(4):   # dust scuffs behind him
                px = x + 60 + k * 70 + (t * 300 % 70)
                cv.drawCircle(px, y + 10 - k * 3, 18 - k * 3, fill("#d8b48a", 0.55 - k * 0.12))
        (kx, ky), rot = _kite_pos((lerp(1100, 200, drag), 220), t, "wild", 1)
        draw_kite(cv, kx, ky, s=1.0, rot=rot - 30 * yank, color="#3a7bd5", t=t, string_to=hand)


def sh_ishaan_floats(cv, c):
    t = c.t
    camv = _push(c, 1420, 640, 2.0, 2.15)
    _roof(cv, c, "evening", camv)
    x, y = 1430, 960
    s = R.roof_scale(y)
    arms = {"r": (140, 30)}
    with K.camera(cv, *camv):
        with K.lit(cv, "heat_dusk"):
            draw(cv, "ishaan", x=x, y=y, s=s, t=t, arms=arms, hold="kite_spool", expr="happy",
                 blink=0.55, look=(0.4, -1), head_tilt=8 + math.sin(t * 0.8) * 3)
        hx, hy = hand_world("ishaan", x, y, s, "r", arms["r"])
        (kx, ky), rot = _kite_pos((1520, 360), t, "float", 2)
        draw_kite(cv, kx, ky, s=1.0, rot=rot, color="#f2c230", t=t, string_to=(hx, hy))
        draw_bhaap(cv, x - 150, y - 430 + math.sin(t * 1.5) * 10, s=0.8, t=t, mood="sleepy", blink=0.0)


def sh_bottle_breeze(cv, c):
    """Meghnath unscrews a jar; the kites dip; the breeze slides off into it. Lid on."""
    t = c.t
    camv = _push(c, 760, 600, 1.7, 1.8)
    _roof(cv, c, "evening", camv)
    bx, by, bs = R.ANCHORS["bucket_seat"]
    lift = ease_out_back(seg(t, 5.2, 6.2))
    arm_l = (lerp(40, 75, lift), lerp(95, 70, lift))
    with K.camera(cv, *camv):
        with K.lit(cv, "heat_dusk"):
            draw(cv, "meghnath", x=bx, y=by, s=bs, t=t, legs="sit", extra=dict(SLING, brow_lift=0.6 * lift - 0.2),
                 arms={"l": arm_l}, hold_l=None, look=(0.6, -0.8) if t < 5 else (0.2, 0.2),
                 expr="happy" if t > 5.4 else "neutral")
        jx, jy = hand_world("meghnath", bx, by, bs, "l", arm_l, sit=True)
        lid_on = t > 4.4
        flow = seg(t, 1.6, 4.6)
        if 1.4 < t < 5.0:
            breeze_ribbon(cv, (1080, 380), (jx, jy - 40), t, "#e8f4ff", a=math.sin(flow * math.pi), bend=50, width=7)
        draw_breeze_jar(cv, jx, jy - 10, s=0.9, t=t, color="#9fd0f0", lid=lid_on, swirl=0.3 + flow)
        # the kites dipping at top of frame
        for i, (x0, col) in enumerate(((1060, "#e0413a"), (1240, "#3a7bd5"))):
            dip = math.sin(seg(t, 1.0, 4.0) * math.pi) * 60
            draw_kite(cv, x0 - 120 + math.sin(t + i) * 10, 340 + dip * 0.6, s=0.7, rot=-20 * (dip / 60), color=col, t=t)


def sh_jar_cu(cv, c):
    t = c.t
    camv = clamp_view(700, 600, 3.0 + 0.1 * c.u)
    _roof(cv, c, "evening", camv)
    with K.camera(cv, *camv):
        with K.lit(cv, "heat_dusk"):
            # Ishaan and Tara peering in from the sides
            draw(cv, "ishaan", x=470, y=900, s=1.6, t=t, expr="awe", look=(1, 0), turn=0.7)
            draw(cv, "tara", x=950, y=930, s=1.5, t=t, expr="surprised", look=(-1, 0), flip=True, turn=0.7)
        draw_breeze_jar(cv, 705, 720, s=3.0, t=t, color="#9fd0f0", lid=True, swirl=1.4, rattle=0.25)
        fx.sparkles(cv, t, 705, 640, spread=90, n=10, color="#dff0ff", size=6, seed=3)


# ============================================================ smog sweeping
def sh_smog_wide(cv, c):
    t = c.t
    camv = _push(c, 960, 520, 1.05, 1.1)
    sw = 0.05 + 0.25 * c.u
    _roof(cv, c, "heat", camv, smog=1.0, swept=sw)
    with K.camera(cv, *camv):
        with K.lit(cv, "heat"):
            for i, (who, x) in enumerate((("tara", 760), ("rehan", 1080), ("ishaan", 1380))):
                y = 690 + i * 6
                sweep = math.sin(t * (3.0 if who != "rehan" else 5.0) + i) * 30
                draw(cv, who, x=x, y=y, s=R.roof_scale(y) * 1.05, t=t, hold="broom", arms={"r": (150 + sweep, 20)},
                     flip=(i == 2), look=(0, -1), expr="determined" if who == "tara" else "happy")


def sh_smog_sweep(cv, c):
    """Close: smog gathered on brooms like cobwebs, stuffed into a sack; Rehan sneezes a grey puff."""
    t = c.t
    camv = clamp_view(1000, 560, 1.7 + 0.05 * c.u)
    _roof(cv, c, "heat", camv, smog=1.0, swept=0.3 + 0.35 * c.u)
    with K.camera(cv, *camv):
        sneeze = seg(t, 4.2, 4.6)
        with K.lit(cv, "heat"):
            for i, (who, x, y) in enumerate((("tara", 820, 720), ("rehan", 1180, 730))):
                sweep = math.sin(t * (3.0 if who == "tara" else 5.2) + i) * 32
                exp = "determined"
                if who == "rehan":
                    exp = "wince" if 3.6 < t < 4.2 else "surprised" if 4.2 < t < 5.2 else "happy"
                draw(cv, who, x=x, y=y, s=1.25, t=t, hold="broom", arms={"r": (150 + sweep, 20)},
                     flip=(who == "rehan"), expr=exp, head_tilt=(-14 * sneeze if who == "rehan" else 0),
                     look=(0, -1) if who == "tara" else (0, 0))
        # grey clumps travelling down the brooms into the sack
        draw_sack(cv, 1000, 735, s=0.9, fullness=0.4 + 0.5 * c.u, smog=True, t=t)
        for k in range(5):
            u = (t * 0.45 + k / 5) % 1.0
            smog_puff(cv, lerp(840 + k * 70, 1000, u), lerp(420, 640, u), 26 * (1 - u * 0.5), a=0.9, t=t)
        if t > 4.2:
            hx, hy = head_world("rehan", 1180, 730, 1.25, flip=True)
            u = seg(t, 4.2, 5.8)
            smog_puff(cv, hx - 70 - u * 140, hy + 20 - u * 40, 22 + u * 40, a=1 - u * 0.8, t=t)


def sh_sacks(cv, c):
    t = c.t
    camv = _push(c, 760, 640, 1.75, 1.85)
    _roof(cv, c, "heat", camv, smog=1.0, swept=1.0)
    bx, by, bs = R.ANCHORS["bucket_seat"]
    with K.camera(cv, *camv):
        for i in range(3):
            draw_sack(cv, 880 + i * 90, 860 + (i % 2) * 8, s=0.85, fullness=1.0, smog=True, t=t)
        knot = seg(t, 1.6, 3.2)
        with K.lit(cv, "heat"):
            arm_l = (lerp(30, 60, math.sin(knot * math.pi * 3) * 0.5 + 0.5) if 0 < knot < 1 else 30, 90)
            draw(cv, "meghnath", x=bx, y=by, s=bs, t=t, legs="sit", extra=dict(SLING, brow_lift=0.5 if t > 3.4 else -0.2),
                 arms={"l": arm_l}, expr="happy" if t > 3.4 else "neutral", look=(1, 0.6) if t < 3.4 else (0.4, -0.2))
        if 3.1 < t < 3.9:
            fx.star4(cv, 1060, 790, 16 * math.sin(seg(t, 3.1, 3.9) * math.pi), "#ffffff", 0.9)


# ============================================================ workshop notebook
def _desk_bg(cv, light="day"):
    cv.drawRect(skia.Rect.MakeWH(K.W, K.H), fill("#24384f" if light == "day" else "#101a28"))
    for k in range(9):
        cv.drawRect(skia.Rect.MakeXYWH(0, k * 120, K.W, 118), fill("#5a4430" if k % 2 else "#634b35"))
    cv.drawRect(skia.Rect.MakeWH(K.W, K.H), K.rad_a((960, 540), 1100, [("#cfe6f4", 0.12), ("#000000", 0.35)]))


def sh_notebook_cu(cv, c):
    t = c.t
    _desk_bg(cv)
    rv = ease_in_out(seg(t, 0.3, c.dur - 0.8))
    notebook_page(cv, 960, 560, 2.2, t, reveal=rv, variant="cloud")
    px = 960 + (-310 + 620 * rv) * 2.2
    pencil(cv, px, 560 + math.sin(t * 9) * 60 + 40, s=2.2)


def sh_tara_writes(cv, c):
    """Tara copies everything; Meghnath peers over her shoulder, grunts; she decides it's approval."""
    t = c.t
    camv = _push(c, 900, 760, 1.75, 1.85)
    WS.draw_workshop(cv, t, "wide", cloth=1.0, cam=camv)
    with K.camera(cv, *camv):
        # a crate seat
        cv.drawRect(skia.Rect.MakeXYWH(760, 880, 170, 100), fill("#8a6a4a"))
        cv.drawRect(skia.Rect.MakeXYWH(760, 880, 170, 100), stroke("#2a1a1c", 3))
        cv.drawLine(760, 930, 930, 930, stroke("#5a4430", 3))
        enter = ease_out(seg(t, 1.2, 2.6))
        with K.lit(cv, "workshop", amount=0.55):
            mx = lerp(1260, 1010, enter)
            draw(cv, "meghnath", x=mx, y=982, s=1.3, t=t, lean=lerp(0, 16, enter), flip=True,
                 extra=dict(SLING, brow_lift=-0.6 if t < 4.6 else -0.1), expr="neutral",
                 look=(-0.7, 0.8), mouth=c.mouth("meghnath"))
            beam = t > 4.8
            draw(cv, "tara", x=840, y=884, s=1.3, t=t, legs="sit", hold="notebook", arms={"r": (40, 110), "l": (30, 100)},
                 look=(0.9, -0.5) if 3.3 < t < 4.8 else (0.2, 0.9), expr="grin" if beam else "neutral",
                 head_tilt=-6 if beam else 6)


def sh_bhaap_hat(cv, c):
    """Bhaap sits on Ishaan's head like a hat and keeps him cool; when Ishaan laughs, Bhaap sparks."""
    t = c.t
    camv = _push(c, 1000, 640, 1.8, 1.9)
    _roof(cv, c, "evening", camv)
    x, y = 1000, 960
    s = R.roof_scale(y)
    laugh = 2.4 < t < 4.6
    with K.camera(cv, *camv):
        with K.lit(cv, "heat_dusk"):
            # Tara and Rehan sweating and fanning behind him
            draw(cv, "tara", x=760, y=820, s=R.roof_scale(820), t=t, expr="worried", hold="notebook",
                 arms={"r": (70 + math.sin(t * 9) * 20, 90)})
            draw(cv, "ishaan", x=x, y=y, s=s, t=t, expr="laugh" if laugh else "happy", blink=0.3 if not laugh else 0,
                 mouth=0.5 + 0.3 * math.sin(t * 14) if laugh else 0, legs="stand")
        tx, ty = head_top("ishaan", x, y, s)
        draw_bhaap(cv, tx, ty - 20 + math.sin(t * 2) * 3, s=0.95, t=t, mood="excited" if laugh else "happy",
                   spark=1.0 if laugh else 0.0, squash=0.25, mouth=0.4 if laugh else 0.0)
        for k in range(3):   # sweat drops on Tara
            u = (t * 0.8 + k * 0.33) % 1
            cv.drawCircle(720 + k * 30, 470 + u * 60, 6, fill("#bfe3ff", 1 - u))


def sh_toe(cv, c):
    t = c.t
    camv = _push(c, 960, 760, 2.1, 2.2, dx=-60)
    _roof(cv, c, "evening", camv)
    stub = 1.6
    walk = clamp(t / stub)
    x = lerp(1180, 960, walk)
    y = 960
    s = R.roof_scale(y)
    hurt = stub < t < 3.4
    with K.camera(cv, *camv):
        # the flowerpot (wobbles when kicked)
        wob = math.sin((t - stub) * 18) * 12 * max(0, 1 - (t - stub) / 0.8) if t > stub else 0
        cv.save(); cv.translate(880, 980); cv.rotate(wob)
        cv.drawPath(K.poly([(-34, -60), (34, -60), (24, 0), (-24, 0)]), fill("#b4613f"))
        cv.drawPath(K.poly([(-34, -60), (34, -60), (24, 0), (-24, 0)]), stroke("#2a1a1c", 3))
        cv.drawLine(-6, -60, -14, -96, stroke("#6b7a3a", 4)); cv.drawLine(6, -60, 18, -92, stroke("#6b7a3a", 4))
        cv.restore()
        hop = abs(math.sin((t - stub) * 9)) * 22 if hurt else 0
        with K.lit(cv, "heat_dusk"):
            draw(cv, "ishaan", x=x, y=y - hop, s=s, t=t, legs="walk" if t < stub else "stand", phase=t * 1.1, flip=True,
                 expr="cry" if hurt else ("happy" if t > 3.6 else "neutral"), arms={"l": (60, 40), "r": (60, 40)} if hurt else {},
                 mouth=0.6 if hurt else 0)
        tx, ty = head_top("ishaan", x, y - hop, s, flip=True)
        rain = seg(t, 2.2, 2.6) * (1 - seg(t, 4.6, 5.2))
        bx = lerp(tx, x - 40, seg(t, 1.8, 2.4))
        by = lerp(ty - 20, y - 160, seg(t, 1.8, 2.4))
        draw_bhaap(cv, bx, by, s=0.85, t=t, mood="sad" if hurt else "happy", rain=rain)
        if hurt:
            toe_ouch(cv, x - 50, y - 10, t, a=1 - seg(t, 2.8, 3.4))


# ============================================================ the loom: demo, then Rehan
def _loom_scene(cv, c, camv, spin=0.3, steam=1.0):
    _roof(cv, c, "heat", camv, steam_on=steam, spin=spin)


def sh_demo(cv, c):
    """Meghnath shows them: one hand, slowly, round and round; a small perfect cloud."""
    t = c.t
    camv = _push(c, 820, 640, 1.6, 1.7)
    _loom_scene(cv, c, camv, spin=0.6)
    bx, by, bs = R.ANCHORS["bucket_seat"]
    lx, ly, lr = R.ANCHORS["loom"]
    ang = t * 1.2
    arm_l = (110 + math.sin(ang) * 25, 40 + math.cos(ang) * 25)
    with K.camera(cv, *camv):
        with K.lit(cv, "heat"):
            draw(cv, "meghnath", x=bx, y=by, s=bs, t=t, legs="sit", arms={"l": arm_l}, extra=dict(SLING, brow_lift=0.2),
                 look=(0.8, -0.6), expr="neutral")
            draw(cv, "rehan", x=1180, y=870, s=R.roof_scale(870), t=t, flip=True, expr="neutral", hand={"r": "ball"},
                 look=(-0.8, -0.3), head_tilt=math.sin(t * 2) * 4)
        grow = ease_out(seg(t, 1.0, 5.0))
        if grow > 0.02:
            draw_bhaap(cv, lx - 40, ly + 30, s=0.25 + 0.35 * grow, t=t, mood="sleepy", alpha=grow, blink=1.0)


def sh_slowly(cv, c):
    t = c.t
    camv = _push(c, 900, 640, 1.7, 1.75)
    _loom_scene(cv, c, camv, spin=0.2)
    bx, by, bs = R.ANCHORS["bucket_seat"]
    nod = math.sin(seg(t, c.dur - 2.2, c.dur - 0.8) * math.pi * 4) * 8
    with K.camera(cv, *camv):
        with K.lit(cv, "heat"):
            talking = c.speaking("meghnath")
            draw(cv, "meghnath", x=bx, y=by, s=bs, t=t, legs="sit", mouth=c.mouth("meghnath"),
                 arms={"l": (60 + (20 * math.sin(t * 2) if talking else 0), 80)}, hand={"l": "point"},
                 extra=dict(SLING, brow_lift=-0.5), look=(0.8, -0.3), expr="angry" if t > 3.2 and talking else "neutral")
            draw(cv, "rehan", x=1130, y=880, s=R.roof_scale(880), t=t, flip=True, head_tilt=nod,
                 expr="determined", look=(-0.6, 0.2), hand={"r": "ball"})


def sh_spin_fast(cv, c):
    """Rehan spins as fast as he can: the cloud goes dark, hard, lumpy and rattling."""
    t = c.t
    camv = clamp_view(lerp(980, 1000, c.u), 600, lerp(1.6, 1.9, ease_in_out(c.u)))
    _loom_scene(cv, c, camv, spin=1.0, steam=1.0)
    lx, ly, lr = R.ANCHORS["loom"]
    spd = lerp(4, 22, seg(t, 0.2, 2.0))
    ang = t * spd
    arm = (110 + math.sin(ang) * 40, 30 + math.cos(ang) * 40)
    with K.camera(cv, *camv):
        with K.lit(cv, "heat"):
            draw(cv, "rehan", x=1140, y=880, s=R.roof_scale(880), t=t, flip=True, arms={"r": arm, "l": (50, 60)},
                 expr="determined", lean=-6 + math.sin(t * 20) * 3, look=(-1, -0.4))
        # whirl lines
        for k in range(3):
            a0 = math.degrees(ang) + k * 120
            cv.drawArc(skia.Rect.MakeXYWH(lx - 120, ly - 120, 240, 240), a0, 60, False, stroke("#ffffff", 5, 0.6))
        dk = ease_in_out(seg(t, 1.2, 3.6))
        dark_cloud(cv, lx, ly, 0.45 + 0.6 * dk, t, rattle=dk, dark=dk)


def sh_oh_no(cv, c):
    t = c.t
    camv = clamp_view(700, 640, 2.4)
    _loom_scene(cv, c, camv, spin=0.0, steam=0.3)
    bx, by, bs = R.ANCHORS["bucket_seat"]
    with K.camera(cv, *camv):
        with K.lit(cv, "heat"):
            draw(cv, "meghnath", x=bx, y=by, s=bs, t=t, legs="sit", mouth=c.mouth("meghnath"),
                 extra=dict(SLING, brow_lift=lerp(-0.2, 1.0, ease_out_back(seg(t, 0.2, 0.6)))),
                 expr="surprised", look=(0.6, -0.8))


def sh_cloud_shoots(cv, c):
    t = c.t
    camv = clamp_view(960, 540, 1.0)
    _loom_scene(cv, c, camv, spin=0.0, steam=0.4)
    lx, ly, lr = R.ANCHORS["loom"]
    u = ease_in_out(seg(t, 0.6, 2.4))
    with K.camera(cv, *camv):
        with K.lit(cv, "heat"):
            draw(cv, "rehan", x=1140, y=880, s=R.roof_scale(880), t=t, flip=True, expr="surprised",
                 look=(lerp(-0.6, 1, u), -1), arms={"r": (60, 20)})
        x = lerp(lx, 2200, u)
        y = lerp(ly, 60, u) - math.sin(u * math.pi) * 140
        dark_cloud(cv, x, y, 1.05 * (1 - 0.5 * u), t, rattle=1.0, dark=1.0)
        for k in range(4):   # speed streaks
            cv.drawLine(x - 90 - k * 40, y + k * 14 - 20, x - 200 - k * 50, y + k * 14 - 20 + 40 * u,
                        stroke("#ffffff", 5, 0.5 * clamp(u * 3) * (1 - u)))


def sh_hail_ground(cv, c):
    t = c.t
    hail = ease_out(seg(t, 1.4, 2.4))
    G.draw_ground(cv, t, "heat", hail=hail, stumps_fall=seg(t, 2.4, 2.9), batsman_run=seg(t, 2.0, c.dur))
    cx, cy = G.CLOUD_POS
    arrive = ease_out(seg(t, 0.0, 1.3))
    dark_cloud(cv, lerp(cx - 1300, cx, arrive), lerp(-200, cy, arrive), 1.6, t, rattle=1.0, dark=1.0)


def sh_deadpan(cv, c):
    """Rehan stares. Meghnath slowly lowers his face into his good hand."""
    t = c.t
    camv = _push(c, 900, 640, 1.65, 1.72)
    _loom_scene(cv, c, camv, spin=0.0, steam=0.2)
    bx, by, bs = R.ANCHORS["bucket_seat"]
    face = ease_in_out(seg(t, 1.4, 4.4))
    with K.camera(cv, *camv):
        with K.lit(cv, "heat"):
            draw(cv, "meghnath", x=bx, y=by, s=bs, t=t, legs="sit", head_tilt=lerp(0, 16, face),
                 arms={"l": (lerp(20, 140, face), lerp(20, 135, face))}, **({"blink": 1.0} if face > 0.6 else {}),
                 extra=dict(SLING, brow_lift=lerp(0.0, -1.0, face)), expr="sad" if face > 0.6 else "neutral")
            draw(cv, "rehan", x=1140, y=880, s=R.roof_scale(880), t=t, flip=True, expr="surprised", mouth=0.5,
                 look=(1, -0.6), blink=0.0)


def sh_underline(cv, c):
    t = c.t
    _desk_bg(cv)
    notebook_page(cv, 960, 560, 2.2, t, reveal=ease_out(seg(t, 0.2, 1.4)), underline=lerp(0, 3, seg(t, 1.8, 3.8)),
                  variant="nofast")
    k = min(2, int(lerp(0, 3, seg(t, 1.8, 3.8))))
    u = (lerp(0, 3, seg(t, 1.8, 3.8)) - k)
    pencil(cv, 960 + (-260 + 200 * K.ease_out(clamp(u))) * 2.2, 560 + (120 + k * 22) * 2.2, s=2.2)


def sh_captain(cv, c):
    t = c.t
    camv = _push(c, 1120, 640, 1.9, 2.0)
    _loom_scene(cv, c, camv, spin=0.0, steam=0.1)
    x, y = 1120, 960
    s = R.roof_scale(y)
    with K.camera(cv, *camv):
        with K.lit(cv, "heat"):
            draw(cv, "ishaan", x=x, y=y, s=s, t=t, expr="happy", mouth=c.mouth("ishaan"), look=(0.7, -0.5), turn=0.5)
        hx, hy = head_world("ishaan", x, y, s, turn=0.5)
        draw_pigeon(cv, hx + 170, hy + 70, s=2.0, t=t, mode="one_leg", head_bob=math.sin(t * 6) * (1 if t > 3.0 else 0.2),
                    flip=True)


# ============================================================ night: Meghnath alone with the photo
def _veil(cv, a=0.4):
    """Late evening in the tank: deepen the cool set without crushing it."""
    cv.save(); cv.resetMatrix()
    cv.drawRect(skia.Rect.MakeWH(K.W, K.H), fill("#0b1424", a))
    cv.drawRect(skia.Rect.MakeWH(K.W, K.H), K.rad_a((K.W * 0.62, K.H * 0.45), 900, [("#cfe2ff", 0.10), ("#cfe2ff", 0)]))
    cv.restore()


def sh_kids_leave(cv, c):
    t = c.t
    camv = clamp_view(960, 640, 1.25)
    WS.draw_workshop(cv, t, "wide", light="day", cloth=1.0, cam=camv)
    _veil(cv)
    with K.camera(cv, *camv):
        with K.lit(cv, "workshop", amount=0.55):
            for i, who in enumerate(("tara", "rehan", "ishaan")):
                u = seg(t, 0.2 + i * 0.6, 4.8 + i * 0.6)
                x = lerp(620 + i * 230, 1380 + i * 230, u)
                draw(cv, who, x=x, y=980, s=1.2, t=t, legs="walk" if u < 1 else "stand", phase=t * 0.9 + i * 0.3,
                     arms={"l": (150, 20)} if (who == "ishaan" and 1.0 < t < 3.0) else {},
                     expr="happy", alpha=1 - seg(t, 4.0 + i * 0.4, 5.0 + i * 0.4), turn=0.6)


def sh_alone_walk(cv, c):
    t = c.t
    camv = _push(c, 1250, 600, 1.6, 1.7)
    WS.draw_workshop(cv, t, "wide", light="day", cloth=1.0, cam=camv)
    _veil(cv)
    with K.camera(cv, *camv):
        u = ease_in_out(seg(t, 0.5, 4.5))
        with K.lit(cv, "workshop", amount=0.55):
            draw(cv, "meghnath", x=lerp(1000, 1330, u), y=980, s=1.3, t=t, legs="walk" if 0 < u < 1 else "stand",
                 phase=t * 0.6, extra=dict(SLING, brow_lift=-0.4), look=(0.6, -0.6), expr="neutral")
        px, py = WS.PHOTO_POS
        draw_varsha_photo(cv, px, py, s=0.55, t=t)


def sh_photo_wipe(cv, c):
    """CU: he wipes the glass with his cardigan cuff and puts the photo back. Gently."""
    t = c.t
    camv = (1380, 470, 3.0)
    WS.draw_workshop(cv, t, "photo", light="day", cam=camv)
    _veil(cv, 0.3)
    with K.camera(cv, *camv):
        px, py = WS.PHOTO_POS
        lift = math.sin(seg(t, 0.4, c.dur - 0.6) * math.pi) * 22
        draw_varsha_photo(cv, px, py - lift, s=0.9, t=t, glass=1.0 - 0.6 * seg(t, 2.0, 5.0))
        for k in range(2):
            u = seg(t, 1.8 + k * 1.6, 3.3 + k * 1.6)
            if 0 < u < 1:
                sleeve_cuff(cv, lerp(px - 70, px + 80, ease_in_out(u)) + 90, py - lift - 40 + math.sin(u * math.pi) * 10,
                            s=0.5, ang=-8)
        fx.motes(cv, t, (px - 200, py - 200, px + 200, py + 100), n=14, color="#dce8ff", a=0.4, seed=4, size=1.6)


def sh_photo_face(cv, c):
    t = c.t
    camv = _push(c, 1290, 600, 2.4, 2.5)
    WS.draw_workshop(cv, t, "wide", light="day", cam=camv)
    _veil(cv)
    with K.camera(cv, *camv):
        with K.lit(cv, "workshop", amount=0.55):
            draw(cv, "meghnath", x=1260, y=980, s=1.3, t=t, extra=dict(SLING, brow_lift=-0.7), look=(0.8, -0.3),
                 expr="sad" if t < 3 else "happy", blink=0.4, head_tilt=4)
        px, py = WS.PHOTO_POS
        draw_varsha_photo(cv, px, py, s=0.55, t=t, glass=0.4)


# ============================================================ shot list
_S = [
    Shot("A", sh_arrive, duration=7.0, music="montage_brass", music_hits=[0.4],
         sfx=[bed("heat_bed", gain=-20), Sfx("door_creak", 0.3, -10), Sfx("pigeon_coo", 2.0, -14),
              Sfx("footsteps_slipper", 0.6, -12)], transition="fade_black", trans_dur=1.2),
    Shot("A", sh_kites_wide, duration=8.0, sfx=[bed("heat_bed", gain=-20), Sfx("kite_wind", 0.5, -10, dur=6.5)]),
    Shot("A", sh_tara_steady, duration=5.5, sfx=[bed("heat_bed", gain=-20), Sfx("kite_wind", 0.0, -14, dur=5.5)]),
    Shot("A", sh_rehan_dragged, duration=7.0, music_hits=[1.0],
         sfx=[bed("heat_bed", gain=-20), Sfx("whoosh", 1.0, -6, params={"intensity": 0.8}),
              Sfx("broom_sweep", 1.6, -8), Sfx("broom_sweep", 3.2, -10), Sfx("kite_wind", 1.0, -8, dur=5.0)]),
    Shot("A", sh_ishaan_floats, duration=5.5, sfx=[bed("heat_bed", gain=-20), Sfx("kite_wind", 0.0, -18, dur=5.5),
                                                   Sfx("bhaap_coo", 2.2, -10)]),
    Shot("A", sh_bottle_breeze, duration=8.5,
         sfx=[bed("heat_bed", gain=-20), Sfx("jar_unscrew", 0.8, -6), Sfx("jar_breeze", 1.8, -4)]),
    Shot("A", sh_jar_cu, duration=5.0, sfx=[bed("heat_bed", gain=-22), Sfx("jar_breeze", 0.2, -14)]),
    # midday smog
    Shot("A", sh_smog_wide, duration=6.5, music="smog_sweep", transition="dissolve", trans_dur=0.6,
         sfx=[bed("heat_bed"), Sfx("broom_sweep", 0.5, -8), Sfx("broom_sweep", 2.4, -9), Sfx("broom_sweep", 4.3, -9)]),
    Shot("A", sh_smog_sweep, duration=8.0,
         sfx=[bed("heat_bed"), Sfx("broom_sweep", 0.4, -8), Sfx("broom_sweep", 2.0, -8), Sfx("cloud_puff", 4.2, -2),
              Sfx("pop", 4.2, -8)]),
    Shot("A", sh_sacks, duration=6.0, sfx=[bed("heat_bed"), Sfx("sack_tie", 1.6, -4), Sfx("sparkle", 3.1, -12)]),
    # workshop: notebook
    Shot("A", sh_notebook_cu, duration=6.5, music="notebook", transition="dissolve", trans_dur=0.6,
         sfx=[bed("workshop_ambience", gain=-16), Sfx("page_turn", 0.2, -10)]),
    Shot("A", sh_tara_writes, duration=8.0, lines=[Line("meghnath", "Hm.", at=3.2)],
         sfx=[bed("workshop_ambience", gain=-16), Sfx("footsteps_slipper", 1.2, -14)]),
    # Ishaan & Bhaap
    Shot("A", sh_bhaap_hat, duration=6.5, music="montage_brass", transition="dissolve", trans_dur=0.5,
         sfx=[bed("heat_bed"), Sfx("bhaap_giggle", 2.5, -6), Sfx("spark_tzik", 2.6, -6), Sfx("spark_tzik", 3.4, -8)]),
    Shot("A", sh_toe, duration=6.0,
         sfx=[bed("heat_bed"), Sfx("bucket_clang", 1.6, -10), Sfx("bhaap_drizzle", 2.3, -6, dur=2.6)]),
    # the loom
    Shot("A", sh_demo, duration=7.0, music="", transition="dissolve", trans_dur=0.5,
         sfx=[bed("heat_bed"), Sfx("steam_hiss", 0.2, -12), Sfx("cloud_puff", 4.6, -6)]),
    Shot("A", sh_slowly, duration=None, tail=2.4,
         lines=[Line("meghnath", "Slowly. Slowly. You are spinning a cloud, not bowling a bouncer.", at=0.6)],
         sfx=[bed("heat_bed"), Sfx("steam_hiss", 0.0, -16)]),
    Shot("A", sh_spin_fast, duration=5.5, music="hailstorm", music_hits=[2.6],
         sfx=[bed("heat_bed"), Sfx("whoosh", 0.3, -8, params={"intensity": 0.6}), Sfx("steam_hiss", 0.5, -8),
              Sfx("hail_rattle", 2.4, -6)]),
    Shot("A", sh_oh_no, duration=None, tail=1.2, lines=[Line("meghnath", "Oh no.", at=0.5)],
         sfx=[bed("heat_bed"), Sfx("hail_rattle", 0.0, -12)]),
    Shot("A", sh_cloud_shoots, duration=3.5,
         sfx=[bed("heat_bed"), Sfx("whoosh", 0.5, -2, params={"intensity": 1.0}), Sfx("hail_rattle", 0.4, -10)]),
    Shot("A", sh_hail_ground, duration=9.0, music_hits=[1.4, 2.5],
         sfx=[bed("heat_bed", gain=-18), Sfx("hail_rattle", 1.3, -2), Sfx("stumps_fall", 2.45, -4),
              Sfx("crowd_howl_distant", 2.0, -6)]),
    Shot("A", sh_deadpan, duration=7.0, music="",
         sfx=[bed("heat_bed"), Sfx("crowd_howl_distant", 0.0, -22)]),
    Shot("A", sh_underline, duration=5.0, sfx=[bed("heat_bed", gain=-20), Sfx("page_turn", 0.0, -12)]),
    Shot("A", sh_captain, duration=None, tail=1.8,
         lines=[Line("ishaan", "Captain says that was the best day of his life.", at=0.6)],
         sfx=[bed("heat_bed"), Sfx("pigeon_coo", 3.6, -6)]),
    # night: Meghnath alone
    Shot("A", sh_kids_leave, duration=6.0, music="photo_alone", transition="fade_black", trans_dur=1.2,
         sfx=[bed("workshop_ambience", gain=-18), Sfx("footsteps_soft", 0.3, -16), Sfx("metal_hatch", 5.0, -12)]),
    Shot("A", sh_alone_walk, duration=6.0, sfx=[bed("workshop_ambience", gain=-18), Sfx("footsteps_slipper", 0.5, -16)]),
    Shot("A", sh_photo_wipe, duration=10.0, sfx=[bed("workshop_ambience", gain=-20)]),
    Shot("A", sh_photo_face, duration=8.0, sfx=[bed("workshop_ambience", gain=-20)]),
]

SHOTS = finalize(_S, 4)
