"""Scene 6: THE SHORTCUT (target 180 s).

Dadi in the heat -> Tara decides -> roof sneak -> torch-lit workshop -> the chained tin trunk ->
the AANDHI -> Bhaap blown away -> Meghnath spins the storm backwards -> he sits down, so tired ->
the neighbours blame "those kids".
"""
from __future__ import annotations

import math

import skia

from .... import core as K, fx
from ....core import W, H, fill, stroke, clamp, lerp
from ....timeline import Shot, Line, Sfx
from .. import rig as R
from ..rig import draw, draw_bhaap, draw_pigeon, draw_pigeon_flock, draw_dadi
from ..sets import roof, workshop, skyline, block, flats, weather_fx as WF
from ._util_c import (bed, fit_beds, ccam, push, roof_bg, tumble_bhaap, dust_world, torch_glow, head_y, frame_head, renumber)

TIN_X, TIN_Y, TIN_S = workshop.TIN_TRUNK


def stool(cv, x, y, s):
    """A low wooden stool whose seat top is at (x, y)."""
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    for lx in (-34, 34):
        cv.drawRect(skia.Rect.MakeLTRB(lx - 5, 0, lx + 5, 70), fill("#6c4a32"))
        cv.drawRect(skia.Rect.MakeLTRB(lx - 5, 0, lx + 5, 70), stroke("line", 2.4))
    seat = K.rrect(-46, -8, 92, 16, 5)
    cv.drawPath(seat, fill("#8a5a34")); cv.drawPath(seat, stroke("line", 2.6))
    cv.restore()


# ------------------------------------------------------------------ 1. Dadi in the heat, at night
def sh01(cv, c):
    t = c.t
    cam = push(c, (900, 600, 1.1), (930, 640, 1.22))
    flats.draw_tara_flat(cv, t, "night", fan=0.0, view="dadi", cam=cam)
    with K.camera(cv, *cam):
        with K.lit(cv, "night", amount=0.55):
            draw_dadi(cv, 800, 830, 2.1, t, fan=0.55 + 0.1 * math.sin(t * 0.7))
            # Tara on a stool beside the bed, fanning Dadi with her notebook
            fan = math.sin(t * 2.6)
            stool(cv, 1420, 866, 1.7)
            draw(cv, "tara", x=1420, y=860, s=1.7, t=t, legs="sit", flip=True, turn=0.4, expr="worried",
                 look=(-0.7, 0.3), head_tilt=-6, arms={"r": (70 + 18 * fan, 70), "l": (12, 40)},
                 hold="notebook", lean=-4)
    # a moonlit stripe through the shutter
    cv.drawRect(skia.Rect.MakeWH(W, H), K.lin_a((0, 0), (W, H), [("#7f9be0", 0.05), ("#000000", 0.0)]))


def sh02(cv, c):
    """Close: Tara's fanning slows; her face sets."""
    t = c.t
    hy = head_y("tara", 860, 1.7, sit=True)
    cam = push(c, frame_head(1400, hy, 2.4, 0.42), frame_head(1405, hy, 2.75, 0.4))
    flats.draw_tara_flat(cv, t, "night", fan=0.0, view="dadi", cam=cam)
    with K.camera(cv, *cam):
        with K.lit(cv, "night", amount=0.5):
            slow = 1 - K.smooth(c.seg(1.0, 3.0))
            fan = math.sin(t * 2.6) * slow
            expr = "worried" if t < 3.2 else "determined"
            stool(cv, 1420, 866, 1.7)
            draw(cv, "tara", x=1420, y=860, s=1.7, t=t, legs="sit", flip=True, turn=0.4, expr=expr,
                 look=(-0.6, 0.2) if t < 3.2 else (0.2, -0.1), head_tilt=-4 if t < 3.2 else 3,
                 arms={"r": (70 + 18 * fan, 70) if t < 3.6 else (30, 110), "l": (12, 40)},
                 hold="notebook", brow=-0.3 if t > 3.2 else 0.0)


# ------------------------------------------------------------------ 2. roof sneak
def sh03(cv, c):
    t = c.t
    cam = push(c, (960, 540, 1.0), (760, 640, 1.25))
    roof_bg(cv, c, "night", cam)
    with K.camera(cv, *cam):
        with K.lit(cv, "night"):
            for who, x0, delay, flip in (("tara", 300, 0.3, False), ("rehan", 300, 0.0, False)):
                k = K.ease_in_out(c.seg(delay, 3.4 + delay))
                x = lerp(x0, 560 if who == "tara" else 720, k)
                y = lerp(730, 790, k)
                s = roof.roof_scale(y)
                walking = 0.02 < k < 0.98
                draw(cv, who, x=x, y=y, s=s, t=t, legs="tiptoe" if not walking else "walk", phase=x / 70,
                     expr="determined" if who == "rehan" else "worried", turn=0.6,
                     flip=(who == "rehan" and t > 4.0), look=(0.6, 0) if t < 4 else (-0.5, 0),
                     mouth=c.mouth(who), hand={"r": "ball"} if who == "rehan" else {},
                     hold="notebook" if who == "tara" else None,
                     arms={"r": (40, 60)} if (who == "rehan" and c.speaking("rehan")) else {})


def sh04(cv, c):
    """Two-shot at the hatch: Tara's whisper."""
    t = c.t
    cam = push(c, (1350, 690, 1.9), (1360, 680, 2.05))
    roof_bg(cv, c, "night", cam)
    with K.camera(cv, *cam):
        with K.lit(cv, "night"):
            draw(cv, "rehan", x=1590, y=870, s=1.45, t=t, flip=True, turn=0.5, expr="determined",
                 look=(-0.6, 0), hand={"r": "ball"}, arms={"l": (20, 30)})
            draw(cv, "tara", x=1190, y=880, s=1.45, t=t, turn=0.6, expr="determined", mouth=c.mouth("tara"),
                 look=(0.6, -0.1), hold="notebook", arms={"l": (30, 90)} if c.speaking("tara") else {},
                 head_tilt=4)


# ------------------------------------------------------------------ 3. torch-lit workshop
def _ws_kids(cv, c, tara, rehan, torch=True):
    t = c.t
    with K.lit(cv, "workshop", amount=1.0):
        with K.lit(cv, "dim", amount=0.45):
            for who, (x, y, s, kw) in (("tara", tara), ("rehan", rehan)):
                if x is None:
                    continue
                draw(cv, who, x=x, y=y, s=s, t=t, mouth=c.mouth(who), **kw)


def sh05(cv, c):
    t = c.t
    k = K.ease_in_out(c.seg(0.0, 6.0))
    tx, rx = lerp(1880, 1240, k), lerp(2000, 1440, k)
    ty = 985
    torches = [(rx - 30, ty - 300, 200 + 8 * math.sin(t * 1.3)), (tx - 30, ty - 300, 196 + 10 * math.sin(t * 1.1 + 1))]
    cam = push(c, (1100, 560, 1.05), (1060, 600, 1.15))
    workshop.draw_workshop(cv, t, "wide", "night", cloth=1.0, keys=(1, 1, 1), torches=torches, cam=cam)
    with K.camera(cv, *cam):
        for (x, y, a) in torches:
            torch_glow(cv, x, y, a, length=700, spread=14, a=0.22)
        _ws_kids(cv, c,
                 (tx, ty, 1.15, dict(legs="walk", phase=tx / 70, flip=True, turn=0.5, expr="worried",
                                     hold="torch", arms={"r": (70, 20)}, look=(-0.4, -0.5))),
                 (rx, ty + 10, 1.18, dict(legs="walk", phase=rx / 70, flip=True, turn=0.5, expr="awe",
                                          hold="torch", arms={"r": (75, 20)}, look=(-0.5, -0.6))))


def sh06(cv, c):
    """Torch beams sliding over the gentle breezes in their jars."""
    t = c.t
    pan = lerp(0.45, 0.62, K.ease_in_out(c.u))
    cx, cy, z = workshop.shelves_cam(pan)
    beams = [(cx + 380, cy + 380, -150 + 20 * math.sin(t * 0.8)), (cx + 520, cy + 420, -160 + 14 * math.sin(t * 0.6 + 2))]
    workshop.draw_workshop(cv, t, "shelves", "night", torches=beams, pan=pan, rattle=0.4)
    with K.camera(cv, cx, cy, z):
        for (x, y, a) in beams:
            torch_glow(cv, x, y, a, length=600, spread=12, a=0.2)


def sh07(cv, c):
    """Rehan stops at the chained tin trunk. Tara reads her notes. He cuts her off."""
    t = c.t
    cam = ccam(*push(c, (520, 820, 2.0), (500, 830, 2.15))[:3])
    beams = [(560, 700, 200), (820, 700, 195)]
    workshop.draw_workshop(cv, t, "wide", "night", cloth=1.0, torches=beams, cam=cam)
    with K.camera(cv, *cam):
        torch_glow(cv, 560, 700, 168, length=320, spread=16, a=0.3)
        _ws_kids(cv, c,
                 (820, 990, 1.25, dict(flip=True, turn=0.45, expr="worried", hold="notebook",
                                       arms={"r": (40, 110)}, look=(0.0, 0.6) if c.speaking("tara") else (-0.6, 0),
                                       head_tilt=-6)),
                 (600, 995, 1.28, dict(flip=True, turn=0.6, expr="determined" if t > 2 else "awe", hold="torch",
                                       arms={"r": (75, 25)}, look=(-0.7, 0.4), lean=6)))


def sh08(cv, c):
    """Chains unwind."""
    t = c.t
    ch = 1 - K.ease_in_out(c.seg(0.6, 3.6))
    cam = ccam(TIN_X + 40, TIN_Y - 70, 3.1)
    workshop.draw_workshop(cv, t, "wide", "night", cloth=1.0, torches=[(560, 700, 160)], cam=cam)
    with K.camera(cv, *cam):
        roof.draw_tin_trunk(cv, TIN_X, TIN_Y, TIN_S, t, open=0.0, chains=ch, weather="night")
        torch_glow(cv, 520, 760, 160, length=300, spread=20, a=0.3)


def sh09(cv, c):
    """Rehan lifts the lid one crack... a breath... ROAR."""
    t = c.t
    op = 0.35 * K.ease_out(c.seg(1.2, 2.4))
    roar = c.seg(2.9, 3.3)
    shake = 8 * roar
    cam = ccam(TIN_X + 120, TIN_Y - 160, 2.3)
    with K.camera(cv, W / 2 + K.noise1(t * 30, 3) * shake, H / 2 + K.noise1(t * 30, 9) * shake, 1.0):
        workshop.draw_workshop(cv, t, "wide", "night", cloth=1.0, torches=[(560, 700, 160)], cam=cam)
        with K.camera(cv, *cam):
            roof.draw_tin_trunk(cv, TIN_X, TIN_Y, TIN_S, t, open=max(op, 0.6 * roar), chains=0.0, weather="night")
            _ws_kids(cv, c,
                     (None, 0, 0, {}),
                     (TIN_X + 170, 995, 1.28, dict(flip=True, turn=0.6,
                                                    expr="awe" if t < 2.9 else "surprised", lean=18 - 30 * roar,
                                                    arms={"r": (60, 30), "l": (50, 30)}, look=(-0.6, 0.6))))
            if op > 0:
                fx.glow_dot(cv, TIN_X, TIN_Y - 110, 160 * op, "#d08a4c", 0.7)
    if roar > 0:
        WF.dust_storm_overlay(cv, t, roar)
        fx.flash(cv, "#e0a060", 0.5 * (1 - c.seg(3.0, 3.6)))


def sh09b(cv, c):
    """Outside: the roof at night. A brown column bursts up out of the big old tank."""
    t = c.t
    burst = K.ease_out(c.seg(0.3, 2.5))
    sh = 6 * burst
    with K.camera(cv, W / 2 + K.noise1(t * 30, 4) * sh, H / 2 + K.noise1(t * 30, 6) * sh, 1.0):
        roof_bg(cv, c, "night", push(c, (1150, 520, 1.15), (1100, 470, 1.05)))
        cam = push(c, (1150, 520, 1.15), (1100, 470, 1.05))
        with K.camera(cv, *cam):
            r = K.rng(31)
            for i in range(60):
                u = ((t * r.uniform(0.25, 0.5)) + r.uniform(0, 1)) % 1.0
                h = u * 1100 * burst
                x = 1475 + math.sin(u * 9 + i) * (30 + u * 220) * burst
                y = 640 - h
                rr = (30 + u * 140) * burst
                cv.drawCircle(x + 10, y + 12, rr, fill("#6e3818", 0.6))
                cv.drawCircle(x, y, rr, fill("#b86a34", 0.9))
                cv.drawCircle(x - rr * 0.3, y - rr * 0.3, rr * 0.4, fill("#e0a060", 0.3))
    WF.dust_storm_overlay(cv, t, 0.4 * c.seg(2.0, 5.0), debris=False)


# ------------------------------------------------------------------ 4. the AANDHI
def sh10(cv, c):
    t = c.t
    d = c.seg(0.0, 8.6)
    skyline.draw_skyline(cv, t, "night", cam_x=lerp(120, 300, c.u), dust=d, heat=0.0)
    for k in range(3):
        draw_pigeon_flock(cv, t * 1.6, lerp(-200, 2100, (t * 0.12 + k * 0.3) % 1), 260 + k * 90, n=6, spread=160,
                          s=0.8, color="#5a3218", seed=40 + k, speed=300)


def sh11(cv, c):
    """Laundry rips off a hundred balconies like startled birds; shutters rattle; a chair cartwheels."""
    t = c.t
    with dust_world(cv, 1.0):
        block.draw_block(cv, t, "dust", fans=0.0, wind=1.0, tear=c.seg(0.3, 4.5), view="balconies")
    WF.dust_storm_overlay(cv, t, 1.0)
    # pigeons tumbling past
    r = K.rng(5)
    for i in range(5):
        u = (t * 0.45 + r.uniform(0, 1)) % 1.0
        x, y = lerp(-100, W + 100, u), r.uniform(200, 800) + math.sin(t * 3 + i) * 40
        cv.save(); cv.translate(x, y); cv.rotate(t * 300 + i * 70)
        draw_pigeon(cv, 0, 0, 1.4, t, mode="flap", captain=False)
        cv.restore()


def sh11b(cv, c):
    """The dust wall swallows Block C."""
    t = c.t
    d = c.seg(0.0, 5.0)
    block.draw_block(cv, t, "night", fans=0.0, wind=0.6 + 0.4 * d, tear=0.5 * d, view="wide")
    front = lerp(-500, W + 600, K.ease_in_out(d))
    with K.layer(cv, alpha=1.0):
        cv.save(); cv.clipRect(skia.Rect.MakeLTRB(-10, 0, max(-10, front - 200), H))
        with dust_world(cv, 1.0):
            block.draw_block(cv, t, "dust", fans=0.0, wind=1.0, tear=0.6 + 0.4 * d, view="wide")
        cv.restore()
    from ..sets import _common as CC
    cv.save(); cv.clipRect(skia.Rect.MakeLTRB(front - 420, -10, W + 400, H + 10))
    CC.cloud_bank(cv, t * 3, front, H + 200, ("#a85d2c", "#d89a5a", "#6e3818"), top_y=-200, seed=21,
                  puff=170, drift=2.0)
    cv.restore()
    if d > 0.5:
        WF.dust_storm_overlay(cv, t, (d - 0.5) * 2)


def sh12(cv, c):
    """Tara and Rehan wrestle the lid; it keeps jumping open."""
    t = c.t
    jump = 0.35 + 0.25 * abs(math.sin(t * 5.3)) * (1 - c.seg(4.0, 5.5) * 0.4)
    cam = ccam(TIN_X + 170, TIN_Y - 170, 2.1)
    with dust_world(cv, 1.0):
        workshop.draw_workshop(cv, t, "wide", "day", cloth=1.0, cam=cam, rattle=2.0)
        with K.camera(cv, *cam):
            roof.draw_tin_trunk(cv, TIN_X, TIN_Y, TIN_S, t, open=jump, chains=0.0, weather="dust")
            for who, x, flip, e in (("rehan", TIN_X + 160, True, "angry"), ("tara", TIN_X + 300, True, "wince")):
                draw(cv, who, x=x + K.noise1(t * 8, len(who)) * 6, y=995, s=1.28, t=t, flip=flip, turn=0.5,
                     expr=e, lean=24, arms={"r": (95, 20), "l": (85, 25)}, look=(-0.6, 0.6))
    WF.dust_storm_overlay(cv, t, 0.8)


def sh13(cv, c):
    """Roof in the storm. Ishaan runs out of the stair hut, screaming for Bhaap."""
    t = c.t
    cam = push(c, (960, 560, 1.05), (900, 600, 1.2))
    with dust_world(cv, 1.0):
        roof_bg(cv, c, "dust", cam)
    with K.camera(cv, *cam):
        k = K.ease_out(c.seg(0.5, 4.6))
        x, y = lerp(300, 820, k), lerp(735, 860, k)
        with K.lit(cv, "dust"):
            draw(cv, "ishaan", x=x, y=y, s=roof.roof_scale(y), t=t, legs="walk", phase=t * 2.6, turn=0.6,
                 expr="cry", lean=10, mouth=0.6 + 0.3 * math.sin(t * 9) if t > 1.0 else 0,
                 arms={"r": (130, 20), "l": (120, 30)}, look=(0.6, -0.8))
        bx = 1060 + math.sin(t * 2.3) * 120 + t * 20
        by = 420 + math.cos(t * 3.1) * 70
        with K.lit(cv, "dust", amount=0.25):
            tumble_bhaap(cv, bx, by, 0.95, t, t * 220, mood="sad", squash=math.sin(t * 7) * 0.6, rain=0.3)
    WF.dust_storm_overlay(cv, t, 1.0)


def sh14(cv, c):
    """Bhaap tumbles toward Ishaan's outstretched fingers... reaches... misses."""
    t = c.t
    cam = ccam(1000, 520, 2.3)
    with dust_world(cv, 1.0):
        roof_bg(cv, c, "dust", cam)
    with K.camera(cv, *cam):
        reach = K.ease_in_out(c.seg(0.0, 2.2))
        with K.lit(cv, "dust"):
            draw(cv, "ishaan", x=900, y=920, s=1.75, t=t, turn=0.7, expr="cry" if t > 3 else "worried",
                 arms={"r": (lerp(120, 150, reach), 5), "l": (60, 30)}, hand={"r": "open"}, lean=10 - 6 * reach,
                 look=(0.8, -0.8), legs="tiptoe")
        # Bhaap stretches toward the fingers, gets within inches, then the wind snatches him away
        k = c.seg(0.0, 2.6)
        snatch = K.ease_in(c.seg(2.6, 5.0))
        bx = lerp(1260, 1105, K.ease_out(k)) + snatch * 900
        by = lerp(470, 420, k) - snatch * 300
        sq = -0.9 if t < 2.6 else 0.5 * math.sin(t * 9)
        with K.lit(cv, "dust", amount=0.25):
            tumble_bhaap(cv, bx, by, 0.85, t, -25 + snatch * 400, mood="sad", squash=sq, rain=0.4,
                         look=(-1, 0.3))
    WF.dust_storm_overlay(cv, t, 0.9)


def sh15(cv, c):
    """Blown away into the brown sky, smaller and smaller. 'BHAAP!'"""
    t = c.t
    with dust_world(cv, 1.0):
        skyline.draw_skyline(cv, t, "dust", cam_x=260, dust=1.0, heat=0.0, pigeons=False)
    k = K.ease_out(c.seg(0.0, 5.5))
    bx, by = lerp(820, 1580, k), lerp(520, 170, k)
    s = lerp(0.9, 0.12, k)
    with K.lit(cv, "dust", amount=0.25):
        tumble_bhaap(cv, bx, by, s, t, t * 260, mood="sad", squash=math.sin(t * 8) * 0.4)
    # Ishaan from behind-ish in the foreground, reaching up
    with K.lit(cv, "dust"):
        draw(cv, "ishaan", x=520, y=1250, s=2.6, t=t, turn=0.8, expr="cry", mouth=c.mouth("ishaan"),
             arms={"r": (150, 10), "l": (140, 15)}, look=(0.8, -1), legs="tiptoe")
    WF.dust_storm_overlay(cv, t, 1.0)


def sh16(cv, c):
    """The stair-hut door bursts open: Meghnath, cardigan, sling and all."""
    t = c.t
    cam = push(c, (430, 560, 1.45), (470, 560, 1.6))
    with dust_world(cv, 1.0):
        roof_bg(cv, c, "dust", cam)
    with K.camera(cv, *cam):
        k = K.ease_out(c.seg(0.4, 2.0))
        x, y = lerp(300, 470, k), lerp(735, 780, k)
        with K.lit(cv, "dust"):
            draw(cv, "meghnath", x=x, y=y, s=roof.roof_scale(y) * 1.05, t=t, legs="walk", phase=t * 1.8, turn=0.6,
                 expr="angry", lean=8, extra={"sling": True, "brow_lift": -0.4},
                 arms={"l": (40, 30)}, look=(0.7, -0.3))
    WF.dust_storm_overlay(cv, t, 1.0)


def sh17(cv, c):
    """One arm. The lid. KLANG."""
    t = c.t
    slam = K.ease_in(c.seg(1.4, 2.0))
    hit = c.seg(2.0, 2.6)
    shake = 10 * (1 - hit) if t > 2.0 else 0
    cam = ccam(TIN_X + 160, TIN_Y - 170, 2.1)
    with K.camera(cv, W / 2 + K.noise1(t * 40, 2) * shake, H / 2 + K.noise1(t * 40, 7) * shake, 1.0):
        with dust_world(cv, 1.0 - 0.3 * hit):
            workshop.draw_workshop(cv, t, "wide", "day", cloth=1.0, cam=cam, rattle=2.0 * (1 - hit))
            with K.camera(cv, *cam):
                op = lerp(0.6, 0.0, slam)
                roof.draw_tin_trunk(cv, TIN_X, TIN_Y, TIN_S, t, open=op, chains=0.0, weather="dust")
                draw(cv, "meghnath", x=TIN_X + 170, y=995, s=1.38, t=t, flip=True, turn=0.5,
                     expr="angry", lean=lerp(0, 34, slam), extra={"sling": True, "brow_lift": -0.6},
                     arms={"l": (lerp(160, 70, slam), 10)}, hand={"l": "open"}, look=(-0.6, 0.5))
                for who, x in (("tara", TIN_X + 380), ("rehan", TIN_X + 480)):
                    back = K.ease_out(c.seg(0.3, 1.0))
                    draw(cv, who, x=x + back * 40, y=995, s=1.25, t=t, flip=True, turn=0.4,
                         expr="surprised", lean=-10 * back, look=(-0.7, 0.2))
    WF.dust_storm_overlay(cv, t, 0.9 * (1 - 0.5 * hit))
    if 2.0 < t < 2.4:
        fx.flash(cv, "#fff0d0", 0.5 * (1 - (t - 2.0) / 0.4))


def _spiral(cv, t, cx, cy, amount, pull):
    """Dust being hauled down out of the sky into the loom: a big rotating spiral of grit and billows."""
    r = K.rng(19)
    for i in range(220):
        a0 = r.uniform(0, 6.28)
        rad0 = r.uniform(120, 1100)
        rad = rad0 * (1 - pull * ((t * 0.18 + i * 0.013) % 1.0))
        ang = a0 + t * (1.6 + 600 / (rad + 80)) - rad * 0.004
        x, y = cx + math.cos(ang) * rad, cy + math.sin(ang) * rad * 0.62
        s = r.uniform(10, 46) * (0.5 + rad / 1100)
        cv.drawCircle(x, y, s, fill("#a85d2c", 0.75 * amount))
        cv.drawCircle(x - s * 0.3, y - s * 0.3, s * 0.45, fill("#e0a060", 0.35 * amount))
    for i in range(70):
        a0 = r.uniform(0, 6.28)
        rad = r.uniform(60, 900) * (1 - 0.6 * pull)
        ang = a0 + t * 3.0
        x, y = cx + math.cos(ang) * rad, cy + math.sin(ang) * rad * 0.62
        cv.drawLine(x, y, x - math.sin(ang) * 30, y + math.cos(ang) * 18, stroke("#f0c080", 2, 0.6 * amount))


def sh18(cv, c):
    """Meghnath spins the storm BACKWARDS: his whole body in it, hauling the dust out of the sky like a net."""
    t = c.t
    drain = K.ease_in_out(c.seg(1.5, 9.5))
    cam = push(c, (900, 560, 1.6), (900, 520, 1.45))
    roof_bg(cv, c, "heat", cam)
    if drain < 1:
        with K.layer(cv, alpha=1 - drain):
            with dust_world(cv, 1.0):
                roof_bg(cv, c, "dust", cam)
    lx, ly, lr = roof.ANCHORS["loom"]
    with K.camera(cv, *cam):
        _spiral(cv, t, lx, ly - 80, 1 - drain * 0.85, pull=0.4 + 0.5 * drain)
        sw = math.sin(t * 2.4)
        with K.lit(cv, "dust", amount=1 - drain):
            draw(cv, "meghnath", x=lx - 40 + sw * 30, y=900, s=1.7, t=t, turn=0.4 + 0.3 * sw,
                 expr="determined", lean=sw * 16, extra={"sling": True, "brow_lift": -0.3 + 0.3 * sw},
                 arms={"l": (150 + 30 * sw, 20 + 20 * math.cos(t * 2.4))}, hand={"l": "fist"},
                 look=(0.2 * sw, -0.9), legs="stand")
    WF.dust_storm_overlay(cv, t, 1 - drain)


def sh19(cv, c):
    """Close: the strain on his face; eyebrows streaming in the wind."""
    t = c.t
    drain = K.ease_in_out(c.seg(0, 5.0))
    cam = frame_head(900, head_y("meghnath", 900, 1.6), 2.5, 0.4)
    roof_bg(cv, c, "heat", cam)
    with K.layer(cv, alpha=0.6 * (1 - drain)):
        with dust_world(cv, 1.0):
            roof_bg(cv, c, "dust", cam)
    with K.camera(cv, *cam):
        sw = math.sin(t * 2.4)
        with K.lit(cv, "dust", amount=0.6 * (1 - drain)):
            draw(cv, "meghnath", x=880, y=900, s=1.6, t=t, turn=0.5 + 0.2 * sw, expr="wince",
                 lean=sw * 10, extra={"sling": True, "brow_lift": -0.8 + 0.3 * sw},
                 arms={"l": (160 + 20 * sw, 20)}, hand={"l": "fist"}, look=(0.3, -1.0), head_tilt=8 * sw)
    WF.dust_storm_overlay(cv, t, 0.5 * (1 - drain), debris=False)


def sh20(cv, c):
    """The dust wall drains back out of the city; colour returns."""
    t = c.t
    d = 1 - K.ease_in_out(c.seg(0.0, 5.0))
    skyline.draw_skyline(cv, t, "heat", cam_x=lerp(300, 200, c.u), dust=d, heat=1.0)


def sh21(cv, c):
    """He sways. Sits down hard against a tank. Eyes close."""
    t = c.t
    cam = push(c, (1180, 720, 1.6), (1200, 760, 1.75))
    roof_bg(cv, c, "heat", cam)
    sit = t > 2.4
    with K.camera(cv, *cam):
        with K.lit(cv, "heat"):
            draw(cv, "ishaan", x=760, y=820, s=1.2, t=t, turn=0.6, expr="sad", look=(0.6, -1.0))
            if not sit:
                sway = math.sin(t * 2.8) * 8 * (1 + t * 0.3)
                draw(cv, "meghnath", x=1290, y=900, s=1.45, t=t, turn=0.5, expr="sleepy", lean=sway,
                     extra={"sling": True, "brow_lift": -0.6}, arms={"l": (20, 30)}, blink=clamp(t / 2.4) * 0.7,
                     legs="stand")
            else:
                drop = K.ease_out_back(c.seg(2.4, 2.9), 2.0)
                draw(cv, "meghnath", x=1300, y=lerp(760, 820, drop), s=1.45, t=t, turn=0.4, expr="sleepy",
                     extra={"sling": True, "brow_lift": -0.7}, legs="sit", blink=min(1.0, 0.7 + c.seg(3.2, 4.2)),
                     head_tilt=-6, arms={"l": (8, 20)})


def sh22(cv, c):
    """Tara: 'Uncle?'"""
    t = c.t
    hy = head_y("tara", 900, 1.55)
    cam = push(c, frame_head(1150, hy, 2.2, 0.38), frame_head(1150, hy, 2.4, 0.37))
    roof_bg(cv, c, "heat", cam)
    with K.camera(cv, *cam):
        with K.lit(cv, "heat"):
            draw(cv, "tara", x=1110, y=900, s=1.55, t=t, turn=0.5, expr="worried", mouth=c.mouth("tara"),
                 look=(0.7, 0.1), lean=8, head_tilt=-6, arms={"r": (40, 60)})


def sh23(cv, c):
    """Close on Meghnath, eyes shut, waving his good hand weakly."""
    t = c.t
    hy = head_y("meghnath", 820, 1.45, sit=True)
    cam = push(c, frame_head(1290, hy, 2.3, 0.4), frame_head(1290, hy, 2.5, 0.4))
    roof_bg(cv, c, "heat", cam)
    with K.camera(cv, *cam):
        with K.lit(cv, "heat"):
            wave = math.sin(t * 3.0) * 12 * (1 - c.seg(1.0, 3.5))
            draw(cv, "meghnath", x=1300, y=820, s=1.45, t=t, turn=0.4, expr="sleepy", blink=1.0,
                 mouth=c.mouth("meghnath"), extra={"sling": True, "brow_lift": -0.5}, legs="sit",
                 head_tilt=-6, arms={"l": (50 + wave, 60)}, hand={"l": "open"})


def sh24(cv, c):
    """He's asleep, sitting up. Tara and Rehan look at each other. Ishaan stares at an empty sky."""
    t = c.t
    cam = push(c, (1100, 640, 1.45), (1080, 620, 1.35))
    roof_bg(cv, c, "heat", cam)
    with K.camera(cv, *cam):
        with K.lit(cv, "heat"):
            snore = 0.08 * (1 + math.sin(t * 1.4))
            draw(cv, "meghnath", x=1300, y=820, s=1.45, t=t, turn=0.4, expr="sleepy", blink=1.0, mouth=snore,
                 extra={"sling": True, "brow_lift": -0.5}, legs="sit", head_tilt=-10, arms={"l": (8, 20)})
            look = t > 1.6
            draw(cv, "tara", x=1060, y=900, s=1.5, t=t, turn=0.4, expr="sad",
                 look=(0.8, 0.2) if not look else (-0.8, 0), head_tilt=-4)
            draw(cv, "rehan", x=860, y=880, s=1.45, t=t, turn=0.4, expr="sad",
                 look=(0.7, 0.2) if not look else (0.8, 0), hand={"r": "ball"})
            draw(cv, "ishaan", x=620, y=760, s=1.1, t=t, turn=0.7, expr="sad", look=(0.3, -1.0))


# ------------------------------------------------------------------ 5. the courtyard: blame
def sh25(cv, c):
    t = c.t
    block.draw_block(cv, t, "heat", fans=0.0, wind=0.25, tear=1.0, view="wide")
    with K.lit(cv, "heat"):
        draw(cv, "tara", x=900, y=block.GROUND_Y + 10, s=0.6, t=t, turn=0.2, expr="sad", look=(0, -0.8),
             head_tilt=-6)
        draw(cv, "rehan", x=990, y=block.GROUND_Y + 12, s=0.6, t=t, turn=0.3, expr="sad", look=(0, 0.6),
             hand={"r": "ball"}, head_tilt=8)
    # rags of laundry drifting down
    r = K.rng(8)
    for i in range(9):
        u = (t * 0.07 + r.uniform(0, 1)) % 1.0
        x = r.uniform(300, 1600) + math.sin(t + i) * 40
        y = lerp(200, 980, u)
        cv.save(); cv.translate(x, y); cv.rotate(math.sin(t * 1.5 + i) * 30)
        cv.drawPath(K.poly([(-18, -10), (16, -14), (20, 8), (-6, 14), (-20, 4)]),
                    fill(["#e8a3a0", "#6f9ac0", "#f2e2a8", "#9bc59a"][i % 4], 0.85))
        cv.restore()


def sh26(cv, c):
    """Ishaan alone on the step by the stair hut, staring up at an empty sky."""
    t = c.t
    cam = push(c, (560, 520, 1.5), (520, 470, 1.6))
    roof_bg(cv, c, "heat", cam)
    with K.camera(cv, *cam):
        with K.lit(cv, "heat"):
            draw(cv, "ishaan", x=390, y=742, s=1.05, t=t, legs="sit", turn=0.5, expr="sad", look=(0.4, -1.0),
                 arms={"l": (15, 60), "r": (15, 60)}, head_tilt=-8, extra={"swing": 0.2})


# ------------------------------------------------------------------ shots
SHOTS = renumber(fit_beds([
    Shot("S06_SH01", sh01, duration=9.0, music="dadi_night", transition="fade_black", trans_dur=1.2,
         sfx=[bed("night_bed_delhi", -20), Sfx("ceiling_fans_stop", 0.0, -30)]),
    Shot("S06_SH02", sh02, duration=7.0, sfx=[bed("night_bed_delhi", -22)]),
    Shot("S06_SH03", sh03, music="shortcut_sneak",
         lines=[Line("rehan", "We just push the clouds in. Push them. Fast.", at=3.6)], tail=1.4,
         sfx=[bed("night_bed_delhi", -18), Sfx("door_creak", 0.2, -12), Sfx("footsteps_slipper", 0.6, -18)]),
    Shot("S06_SH04", sh04, lines=[Line("tara", "We need wind. A lot of wind.", at=0.6)], tail=2.4,
         sfx=[bed("night_bed_delhi", -20), Sfx("metal_hatch", 3.2, -12)]),
    Shot("S06_SH05", sh05, duration=8.0, transition="dissolve", trans_dur=0.6,
         sfx=[bed("workshop_ambience", -16), Sfx("footsteps_soft", 0.5, -16)]),
    Shot("S06_SH06", sh06, duration=5.5, sfx=[bed("workshop_ambience", -16), Sfx("jar_breeze", 1.5, -20)]),
    Shot("S06_SH07", sh07,
         lines=[Line("tara", "Uncle said never—", at=1.6), Line("rehan", "He's not here.", at=2.85)], tail=1.8,
         sfx=[bed("workshop_ambience", -16)]),
    Shot("S06_SH08", sh08, duration=4.6, sfx=[bed("workshop_ambience", -18), Sfx("chains_unwind", 0.5, -6)]),
    Shot("S06_SH09", sh09, duration=4.4, music="",
         sfx=[bed("workshop_ambience", -18), Sfx("tin_lid_creak", 1.1, -8), Sfx("aandhi_roar", 2.85, -2)]),
    Shot("S06_SH09B", sh09b, duration=4.5, music="aandhi",
         sfx=[bed("aandhi_roar", -4), Sfx("metal_hatch", 0.2, -8)]),
    Shot("S06_SH10", sh10, duration=9.0,
         sfx=[bed("aandhi_roar", -4), Sfx("pigeon_flock", 2.0, -14)]),
    Shot("S06_SH11", sh11, duration=6.0,
         sfx=[bed("aandhi_roar", -6), Sfx("laundry_flap", 0.2, -8), Sfx("shutter_rattle", 1.2, -10),
              Sfx("chair_cartwheel", 2.6, -10), Sfx("pigeon_flap", 3.5, -14)]),
    Shot("S06_SH11B", sh11b, duration=5.5,
         sfx=[bed("aandhi_roar", -6), Sfx("laundry_flap", 1.0, -10), Sfx("shutter_rattle", 2.5, -12)]),
    Shot("S06_SH12", sh12, duration=5.5,
         sfx=[bed("aandhi_roar", -8), Sfx("tin_lid_creak", 0.3, -10), Sfx("bucket_clang", 2.2, -16)]),
    Shot("S06_SH13", sh13, duration=6.5, sfx=[bed("aandhi_roar", -6), Sfx("door_creak", 0.3, -14),
                                              Sfx("bhaap_coo", 2.5, -12)]),
    Shot("S06_SH14", sh14, duration=5.2, sfx=[bed("aandhi_roar", -8), Sfx("whoosh", 2.6, -8, params={"intensity": 0.9})]),
    Shot("S06_SH15", sh15, lines=[Line("ishaan", "BHAAP!", at=1.4)], duration=6.0,
         sfx=[bed("aandhi_roar", -8)]),
    Shot("S06_SH16", sh16, duration=4.2, music="storm_rescue",
         sfx=[bed("aandhi_roar", -8), Sfx("door_creak", 0.2, -6)]),
    Shot("S06_SH17", sh17, duration=4.4, music_hits=[2.0],
         sfx=[bed("aandhi_roar", -10), Sfx("klang", 2.0, -1)]),
    Shot("S06_SH18", sh18, duration=11.0,
         sfx=[bed("aandhi_roar", -12), Sfx("storm_reverse", 0.8, -4), Sfx("steam_hiss", 5.0, -18)]),
    Shot("S06_SH19", sh19, duration=5.0, sfx=[bed("wind_gusts", -14, build=0.3)]),
    Shot("S06_SH20", sh20, duration=6.5, sfx=[bed("heat_bed", -18), Sfx("storm_reverse", 0.0, -12)]),
    Shot("S06_SH21", sh21, duration=7.0, music="aftermath",
         sfx=[bed("heat_bed", -18), Sfx("bucket_clang", 2.55, -18)]),
    Shot("S06_SH22", sh22, lines=[Line("tara", "Uncle?", at=0.9)], tail=1.8, sfx=[bed("heat_bed", -20)]),
    Shot("S06_SH23", sh23, lines=[Line("meghnath", "Just... tired. Very... tired.", at=0.8)], tail=2.4,
         sfx=[bed("heat_bed", -22)]),
    Shot("S06_SH24", sh24, duration=8.0, sfx=[bed("heat_bed", -20), Sfx("pigeon_coo", 4.5, -20)]),
    Shot("S06_SH25", sh25, transition="dissolve", trans_dur=0.8,
         lines=[Line("neighbor_f", "Those kids were on the roof!", at=0.8),
                Line("neighbor_m", "I SAW them!", at=3.0)], tail=3.0,
         sfx=[bed("heat_bed", -16), Sfx("shutter_rattle", 4.2, -22)]),
    Shot("S06_SH26", sh26, duration=8.0, sfx=[bed("heat_bed", -20), Sfx("pigeon_coo", 3.0, -22)]),
]), 6)
