"""WK sc03 RECRUITED (04:00-07:00): 'Out.'; the one-handed spin fails; Ishaan holds the other end;
'You touch nothing'; the hatch in the big rusty tank; the WORKSHOP REVEAL; 'Start sweeping.'"""
from __future__ import annotations

import math

import skia

from .... import core as K, fx
from ....core import W, H, clamp, lerp, seg
from ....timeline import Sfx
from .. import rig as R
from ..sets import roof, workshop
from ..sets import weather_fx as WX
from ._util_a import S, seq, ccam, cam, cam_move
from .sc02 import tank, BX, BY, MS, LX, LY, LR, CKX, CKY, DOOR, TANK, IS, MEGH

HX, HY, HW, HH = roof.HATCH_RECT       # (1420, 640, 110, 130)

# standing marks on the roof for this scene
M_STAND = (BX + 30, BY + 10)           # Meghnath stands up in front of his bucket
TARA_M = (410, 810)
REHAN_M = (510, 790)
ISH_M = (600, 839)
KS = 1.12                              # kid scale in roof mediums


def roof_cam(cv, t, camc, steam=0.3, spin=0.0):
    roof.draw_roof(cv, t, "evening", "wide", steam_on=steam, spin=spin, cam=camc)


def meg(cv, t, c, x=None, y=None, legs="stand", flip=False, brow=0.0, expr="angry", look=(-1.0, 0.0), arms=None,
        hold_l=None, s=MS, turn=0.5, lean=0.0):
    x = M_STAND[0] if x is None else x
    y = M_STAND[1] if y is None else y
    R.draw(cv, "meghnath", x=x, y=y, s=s, legs=legs, t=t, flip=flip, turn=turn, extra=dict(MEGH, brow_lift=brow),
           expr=expr, look=look, mouth=c.mouth("meghnath"), arms=arms or {}, hold_l=hold_l, lean=lean)


def kids_group(cv, t, c, expr=("awe", "awe", "awe"), looks=((1, -0.4),) * 3, bhaap=True, hold_tara="notebook",
               rehan_arms=None, tara_arms=None):
    R.draw(cv, "tara", x=TARA_M[0], y=TARA_M[1], s=KS, t=t, expr=expr[0], look=looks[0], turn=0.65,
           mouth=c.mouth("tara"), hold_l=hold_tara, arms=tara_arms or {})
    R.draw(cv, "rehan", x=REHAN_M[0], y=REHAN_M[1], s=KS, t=t, expr=expr[1], look=looks[1], turn=0.65,
           mouth=c.mouth("rehan"), arms=rehan_arms or {})
    R.draw(cv, "ishaan", x=ISH_M[0], y=ISH_M[1], s=IS, t=t, expr=expr[2], look=looks[2], turn=0.65,
           mouth=c.mouth("ishaan"))


def bhaap_on_ishaan(cv, t, mood="shy", dx=0.0):
    R.draw_bhaap(cv, ISH_M[0] + 70 + dx, ISH_M[1] - 300 * IS, 0.85, t, mood=mood, look=(0.8, 0.0))


def small_puff(cv, x, y, s, t, a=1.0):
    """A faceless puff of new cloud."""
    if a <= 0.01:
        return
    for (dx, dy, r) in [(0, 0, 26), (-22, 6, 18), (22, 5, 19), (-10, -14, 17), (12, -15, 16)]:
        rr = r * s * (1 + 0.05 * math.sin(t * 2 + dx))
        cv.drawCircle(x + dx * s, y + dy * s, rr + 2.4, K.fill("#4a5a70", 0.9 * a))
    for (dx, dy, r) in [(0, 0, 26), (-22, 6, 18), (22, 5, 19), (-10, -14, 17), (12, -15, 16)]:
        rr = r * s * (1 + 0.05 * math.sin(t * 2 + dx))
        cv.drawCircle(x + dx * s, y + dy * s, rr, K.fill("#ffffff", a))


# ------------------------------------------------------------------ OUT.
def sh01(cv, c):
    """He stands. Even with the sling and the stoop he is tall. The eyebrows come down like shutters."""
    t = c.t
    camc = ccam(M_STAND[0] + 60, M_STAND[1] - 330, lerp(1.9, 2.1, c.u))
    roof_cam(cv, t, camc)
    with cam(cv, camc):
        rise = K.ease_out_back(seg(t, 0.4, 1.4))
        with K.lit(cv, "heat_dusk"):
            if t < 0.6:
                meg(cv, t, c, x=BX, y=BY, legs="sit", brow=-0.6, look=(-1, 0))
            else:
                cv.save(); cv.translate(M_STAND[0], M_STAND[1]); cv.scale(1, lerp(0.85, 1.0, rise))
                cv.translate(-M_STAND[0], -M_STAND[1])
                meg(cv, t, c, brow=lerp(-0.3, -1.0, K.ease_in_out(seg(t, 1.8, 3.2))), look=(-1, 0.1))
                cv.restore()


def sh02(cv, c):
    t = c.t
    camc = ccam(M_STAND[0] + 20, M_STAND[1] - 380, 3.0)
    roof_cam(cv, t, camc)
    with cam(cv, camc):
        with K.lit(cv, "heat_dusk"):
            meg(cv, t, c, brow=-1.0, look=(-1, 0.1))


def sh03(cv, c):
    t = c.t
    camc = ccam(430, 640, 2.3)
    roof_cam(cv, t, camc)
    with cam(cv, camc):
        with K.lit(cv, "heat_dusk"):
            kids_group(cv, t, c, expr=("awe", "awe" if not c.speaking("rehan") else "neutral", "worried"),
                       looks=((1, -0.4), (1, -0.5), (1, -0.4)))
        bhaap_on_ishaan(cv, t)


def sh05(cv, c):
    """'You MADE a CLOUD.' (Tara, arms flung wide)"""
    t = c.t
    camc = ccam(TARA_M[0] + 20, TARA_M[1] - 300, 2.8)
    roof_cam(cv, t, camc)
    fling = K.ease_out_back(seg(t, 0.2, 0.6))
    with cam(cv, camc):
        with K.lit(cv, "heat_dusk"):
            R.draw(cv, "tara", x=TARA_M[0], y=TARA_M[1], s=KS, t=t, expr="surprised", look=(1, -0.4), turn=0.6,
                   mouth=c.mouth("tara"), arms={"l": (lerp(20, 135, fling), 10), "r": (lerp(20, 135, fling), 10)},
                   hand={"l": "open", "r": "open"}, lean=-4 * fling)


# ------------------------------------------------------------------ the second cloud fails
def spin_attempt(cv, t, c, fail=True, ishaan=0.0, puff=0.0, brow=-0.2, expr="determined", look=(0.5, -0.8),
                 shake=1.0, camc=None):
    steam_spin = 0.55 + 0.25 * math.sin(t * 2.2) if fail else lerp(0.6, 1.0, puff)
    roof.draw_roof(cv, t, "evening", "wide", steam_on=1.0, spin=steam_spin, cam=camc)
    with cam(cv, camc):
        if fail:
            # wisps tearing apart instead of gathering
            r = K.rng(5)
            for i in range(9):
                life = (t * 0.5 + i / 9) % 1.0
                ang = r.uniform(0, 6.28) + t * 1.4
                rad = lerp(40, LR * 1.3, life)
                cv.drawCircle(LX + math.cos(ang) * rad, LY + math.sin(ang) * rad * 0.6 - life * 60,
                              lerp(16, 6, life), K.fill("#e8eaee", 0.55 * (1 - life)))
        else:
            WX.steam(cv, t, CKX, CKY - 30, amount=1.0, spin=1.0, loom=(LX, LY, LR), n=14)
            small_puff(cv, LX, LY, lerp(0.4, 1.0, puff), t, a=K.smooth(seg(puff, 0.0, 0.3)))
        jit = shake * 7 * K.noise1(t * 14, 3)
        with K.lit(cv, "heat_dusk"):
            R.draw(cv, "meghnath", x=BX, y=BY, s=MS, legs="sit", t=t, flip=True, turn=0.35,
                   extra=dict(MEGH, brow_lift=brow), expr=expr, look=look, head_tilt=-4,
                   arms={"l": (148 + 16 * math.sin(t * 3.2) + jit, 22 + 18 * math.cos(t * 3.2) + jit)})
            if ishaan > 0:
                k = K.ease_in_out(ishaan)
                ix = lerp(1260, 1150, k)
                R.draw(cv, "ishaan", x=ix, y=890, s=IS, t=t, legs="walk" if k < 1 else "stand", phase=t * 1.4,
                       flip=True, turn=0.6, expr="determined" if k >= 1 else "neutral", look=(-0.6, -0.8),
                       arms={"l": (lerp(20, 155, k), lerp(20, 10, k))}, hand={"l": "fist"})


def sh06(cv, c):
    """He turns back to the loom and tries again, one-handed. The steam slips and tears into wisps."""
    t = c.t
    spin_attempt(cv, t, c, fail=True, brow=lerp(-0.2, -0.6, c.u), expr="determined",
                 shake=K.smooth(seg(t, 3.0, 8.0)), camc=cam_move(c.u, (850, 600, 1.6), (820, 610, 1.75)))


def sh07(cv, c):
    """His good hand shakes. He winces; the sling pulls."""
    t = c.t
    camc = ccam(BX + 50, BY - 150, 2.6)
    roof.draw_roof(cv, t, "evening", "wide", steam_on=0.8, spin=0.3, cam=camc)
    with cam(cv, camc):
        jit = 9 * K.noise1(t * 16, 7)
        wince = t > 1.6
        with K.lit(cv, "heat_dusk"):
            R.draw(cv, "meghnath", x=BX, y=BY, s=MS, legs="sit", t=t, flip=True, turn=0.35,
                   extra=dict(MEGH, brow_lift=-0.9 if wince else -0.4), expr="wince" if wince else "determined",
                   look=(0.5, -0.6), head_tilt=-4 + (5 if wince else 0), lean=4 if wince else 0,
                   arms={"l": (lerp(150, 90, seg(t, 1.6, 2.6)) + jit, 25 + jit)})


def sh08(cv, c):
    """Ishaan quietly steps up and holds the other end of the wire."""
    t = c.t
    spin_attempt(cv, t, c, fail=t < 3.5, ishaan=seg(t, 0.4, 3.4), puff=0.0, brow=-0.5, expr="neutral",
                 shake=0.4, camc=ccam(980, 620, 1.65))


def sh09(cv, c):
    """The steam catches and spins. A wisp becomes a puff."""
    t = c.t
    spin_attempt(cv, t, c, fail=False, ishaan=1.0, puff=K.ease_in_out(seg(t, 1.0, 8.5)), brow=0.0, expr="neutral",
                 shake=0.0, camc=cam_move(c.u, (980, 620, 1.65), (960, 600, 1.85)))


def sh10(cv, c):
    """Meghnath looks down at Ishaan for a long moment."""
    t = c.t
    camc = ccam(1000, 560, 2.0)
    roof.draw_roof(cv, t, "evening", "wide", steam_on=0.6, spin=0.6, cam=camc)
    with cam(cv, camc):
        small_puff(cv, LX, LY - 10 * math.sin(t), 1.0, t)
        with K.lit(cv, "heat_dusk"):
            R.draw(cv, "meghnath", x=BX, y=BY, s=MS, legs="sit", t=t, flip=True, turn=0.55,
                   extra=dict(MEGH, brow_lift=lerp(-0.6, 0.35, K.ease_in_out(seg(t, 1.5, 5.5)))),
                   expr="neutral", look=(1.0, 0.4), head_tilt=6, arms={"l": (60, 50)})
            R.draw(cv, "ishaan", x=1150, y=890, s=IS, t=t, flip=True, turn=0.6, expr="shy" if t > 3 else "neutral",
                   look=(-1.0, -0.6), arms={"l": (155, 10)}, hand={"l": "fist"})


def sh11(cv, c):
    t = c.t
    camc = ccam(BX + 40, BY - 140, 2.4)
    roof.draw_roof(cv, t, "evening", "wide", steam_on=0.6, spin=0.6, cam=camc)
    with cam(cv, camc):
        with K.lit(cv, "heat_dusk"):
            R.draw(cv, "meghnath", x=BX, y=BY, s=MS, legs="sit", t=t, flip=True, turn=0.55,
                   extra=dict(MEGH, brow_lift=-0.5 if t > 1.6 else 0.0), expr="angry" if t > 1.6 else "neutral",
                   look=(1.0, 0.3), mouth=c.mouth("meghnath"), arms={"l": (40, 60)},
                   hand={"l": "point"} if t > 2.2 else {})


def sh12(cv, c):
    """Rehan pumps a fist. Tara opens her notebook."""
    t = c.t
    camc = ccam(420, 650, 2.2)
    roof_cam(cv, t, camc)
    pump = math.sin(math.pi * seg(t, 0.4, 1.0))
    with cam(cv, camc):
        with K.lit(cv, "heat_dusk"):
            R.draw(cv, "tara", x=TARA_M[0], y=TARA_M[1], s=KS, t=t, expr="determined" if t > 1.6 else "awe",
                   look=(0.0, 0.8) if t > 1.6 else (1, -0.4), turn=0.6,
                   arms={"l": (40, 120), "r": (40, 115)} if t > 1.4 else {}, hold_l=None if t > 1.4 else "notebook")
            R.draw(cv, "rehan", x=REHAN_M[0], y=REHAN_M[1], s=KS, t=t, expr="grin", look=(1, -0.4), turn=0.6,
                   arms={"r": (lerp(30, 170, pump), lerp(60, 10, pump))}, hand={"r": "fist"},
                   lean=-6 * pump)
        if t > 1.4:
            R.draw_notebook(cv, TARA_M[0] + 18, TARA_M[1] - 150 * KS, 1.2, open_=True)


def sh13(cv, c):
    t = c.t
    camc = ccam(TARA_M[0] + 10, TARA_M[1] - 290, 2.9)
    roof_cam(cv, t, camc)
    with cam(cv, camc):
        with K.lit(cv, "heat_dusk"):
            R.draw(cv, "tara", x=TARA_M[0], y=TARA_M[1], s=KS, t=t, expr="neutral", look=(1, -0.5), turn=0.6,
                   mouth=c.mouth("tara"), arms={"l": (40, 120), "r": (45, 115)}, head_tilt=5)
        R.draw_notebook(cv, TARA_M[0] + 18, TARA_M[1] - 150 * KS, 1.2, open_=True)


def sh14(cv, c):
    """'That was the rules.' Deadpan."""
    t = c.t
    camc = ccam(BX + 30, BY - 150, 2.6)
    roof.draw_roof(cv, t, "evening", "wide", steam_on=0.5, spin=0.5, cam=camc)
    with cam(cv, camc):
        with K.lit(cv, "heat_dusk"):
            R.draw(cv, "meghnath", x=BX, y=BY, s=MS, legs="sit", t=t, flip=False, turn=0.55,
                   extra=dict(MEGH, brow_lift=-0.7), expr="neutral", look=(-1.0, 0.0), mouth=c.mouth("meghnath"),
                   arms={"l": (30, 60)})


# ------------------------------------------------------------------ to the big tank; the hatch
def walker(cv, t, who, x0, x1, y, s, t0, t1, flip=False, **kw):
    k = seg(t, t0, t1)
    x = lerp(x0, x1, K.ease_in_out(k))
    R.draw(cv, who, x=x, y=y, s=s, t=t, legs="walk" if 0 < k < 1 else "stand", phase=t * 1.5, flip=flip, **kw)


def sh15(cv, c):
    """He leads them to the oldest, biggest, rustiest tank."""
    t = c.t
    camc = cam_move(c.u, (1050, 640, 1.45), (1250, 640, 1.6))
    roof.draw_roof(cv, t, "evening", "wide", steam_on=0.2, cam=camc)
    with cam(cv, camc):
        with K.lit(cv, "heat_dusk"):
            walker(cv, t, "rehan", 760, 1180, 900, KS, 1.4, 7.4, turn=0.6, expr="awe", look=(1, -0.5))
            walker(cv, t, "tara", 640, 1060, 910, KS, 1.0, 7.0, turn=0.6, expr="awe", look=(1, -0.5),
                   hold_l="notebook")
            walker(cv, t, "meghnath", 980, HX - 20, 830, MS, 0.0, 6.0, turn=0.5, extra=dict(MEGH, brow_lift=-0.3),
                   expr="neutral", look=(1, 0))


def sh16(cv, c):
    """He opens the iron hatch. Cool silver-blue light spills out onto their faces."""
    t = c.t
    camc = ccam(HX + 20, HY + 40, 2.0)
    roof.draw_roof(cv, t, "evening", "wide", steam_on=0.1, cam=camc)
    op = K.ease_out_back(seg(t, 0.8, 2.0))
    with cam(cv, camc):
        # the open hatch: a cold glowing hole, the door swung outward
        if op > 0:
            cv.drawRect(skia.Rect.MakeXYWH(HX + 6, HY + 6, HW - 12, HH - 12), K.fill("#bfe0ff", 0.95))
            cv.drawRect(skia.Rect.MakeXYWH(HX + 6, HY + 6, HW - 12, HH - 12),
                        K.rad_a((HX + HW / 2, HY + HH / 2), HW, [("#ffffff", 0.9), ("#8fb7e8", 0.0)]))
            dw = HW * (1 - op * 0.85)
            door = skia.Rect.MakeXYWH(HX + HW - 4, HY, max(6, HW * 0.25 * op), HH)
            cv.drawRect(door, K.fill("#2f4848")); cv.drawRect(door, K.stroke("line", 3))
            fx.light_rays(cv, HX + HW / 2, HY + HH / 2, 160, spread_deg=60, length=700, color="#cfe6ff",
                          a=0.35 * K.smooth(seg(t, 1.0, 2.0)), n=6, t=t)
        with K.lit(cv, "heat_dusk"):
            R.draw(cv, "meghnath", x=HX - 40, y=830, s=MS, t=t, flip=False, turn=0.7,
                   extra=dict(MEGH, brow_lift=0.2), expr="neutral", look=(1, 0),
                   arms={"l": (lerp(30, 80, seg(t, 0.4, 1.0)) - 50 * seg(t, 1.2, 2.0), 30)})
        with K.lit(cv, "workshop", amount=0.45 * K.smooth(seg(t, 1.2, 2.4))):
            R.draw(cv, "tara", x=HX - 260, y=930, s=KS, t=t, expr="awe", look=(1, -0.3), turn=0.7, hold_l="notebook")
            R.draw(cv, "rehan", x=HX - 150, y=950, s=KS, t=t, expr="awe", look=(1, -0.3), turn=0.7)
        if 1.2 < t:
            fx.motes(cv, t, (HX - 300, HY - 100, HX + 200, HY + 300), n=18, color="#e8f3ff", a=0.6, seed=9)


# ------------------------------------------------------------------ THE WORKSHOP
def ws(cv, t, camc, view="wide", **kw):
    workshop.draw_workshop(cv, t, view, light="day", cam=camc, **kw)


def sh17(cv, c):
    """Impossibly huge. We crane DOWN the spiral of shelves from the light at the top."""
    t = c.t
    pan = lerp(1.0, 0.0, K.ease_in_out(seg(t, 0.0, 14.0)))
    camc = workshop.shelves_cam(pan)
    ws(cv, t, camc, view="shelves", pan=pan)
    with cam(cv, camc):
        fx.motes(cv, t, (0, 0, W, H), n=50, color="#e8f3ff", a=0.5, seed=21)


WS_FLOOR = workshop.FLOOR_Y
KIDS_WS = [("tara", 640, 1.2), ("rehan", 860, 1.2), ("ishaan", 1060, 1.1)]


def kids_ws(cv, t, c, turn_k=0.0, exprs=("awe", "awe", "awe"), look_up=-0.9):
    for i, (who, x, s) in enumerate(KIDS_WS):
        tk = (turn_k * 1.1 + i * 0.25) % 2.0
        turn = 0.7 * math.cos(math.pi * tk)
        flip = math.sin(math.pi * tk) < 0
        R.draw(cv, who, x=x, y=WS_FLOOR, s=s, t=t, turn=abs(turn), flip=flip, expr=exprs[i],
               look=(0.0, look_up), mouth=c.mouth(who) if who != "ishaan" else 0.25,
               hold_l="notebook" if who == "tara" else None)


def sh18(cv, c):
    """Jars of breezes: pale-blue morning, green evening, a dusty-yellow loo wind rattling its lid."""
    t = c.t
    pan = lerp(0.46, 0.56, c.u)
    camc = workshop.shelves_cam(pan)
    ws(cv, t, camc, view="shelves", pan=pan, rattle=1.0)


def sh19(cv, c):
    """Kites hang from the ceiling like sleeping bats; looms hold half-woven clouds."""
    t = c.t
    camc = cam_move(c.u, (960, 260, 1.5), (900, 330, 1.55))
    ws(cv, t, camc)


def sh20(cv, c):
    """The kids turn slowly, mouths open. Bhaap zips loops above them, sparking."""
    t = c.t
    camc = cam_move(c.u, (850, 760, 1.6), (850, 740, 1.7))
    ws(cv, t, camc)
    with cam(cv, camc):
        with K.lit(cv, "workshop"):
            kids_ws(cv, t, c, turn_k=t * 0.18)
        a = t * 1.9
        R.draw_bhaap(cv, 850 + 300 * math.cos(a), 470 + 110 * math.sin(a * 2), 0.85, t, mood="excited",
                     spark=1.0 if math.sin(a * 3) > 0.3 else 0.0, squash=-0.4, look=(-math.sin(a), 0))


def sh21(cv, c):
    t = c.t
    camc = ccam(960, 420, 2.0)
    ws(cv, t, camc)
    with cam(cv, camc):
        a = t * 2.4
        x, y = 960 + 230 * math.sin(a), 420 + 90 * math.sin(a * 2)
        for k in range(1, 6):   # sparkle trail
            ta = a - k * 0.12
            fx.star4(cv, 960 + 230 * math.sin(ta), 420 + 90 * math.sin(ta * 2), 8 - k, "#fff6c0", 0.8 - k * 0.14)
        R.draw_bhaap(cv, x, y, 1.1, t, mood="excited", mouth=0.6, spark=1.0 if math.sin(a * 2) > 0 else 0.4,
                     squash=-0.5 * abs(math.cos(a)), look=(math.cos(a), 0))


def sh22(cv, c):
    """In the middle, under a dusty cloth, a huge shape. Something big."""
    t = c.t
    camc = cam_move(c.u, (960, 800, 1.6), (960, 820, 2.1))
    ws(cv, t, camc, view="trunk", cloth=1.0)
    with cam(cv, camc):
        fx.motes(cv, t, (700, 600, 1220, 960), n=20, color="#dfe8f5", a=0.5, seed=31)


def sh17b(cv, c):
    """Meghnath ducks in through the hatch behind the kids, a tall silhouette against the light."""
    t = c.t
    camc = cam_move(c.u, (900, 700, 1.45), (900, 720, 1.55))
    ws(cv, t, camc)
    with cam(cv, camc):
        # the hatch from inside: a bright square high on the far wall with a ladder below
        hx, hy = 1260, 600
        cv.drawRect(skia.Rect.MakeXYWH(hx - 60, hy - 70, 120, 140), K.fill("#ffe2b8"))
        cv.drawRect(skia.Rect.MakeXYWH(hx - 60, hy - 70, 120, 140), K.stroke("line", 4))
        for k in range(6):
            cv.drawLine(hx - 34, hy + 70 + k * 46, hx + 34, hy + 70 + k * 46, K.stroke("#6b4a32", 6))
        cv.drawLine(hx - 34, hy + 70, hx - 34, WS_FLOOR, K.stroke("#6b4a32", 7))
        cv.drawLine(hx + 34, hy + 70, hx + 34, WS_FLOOR, K.stroke("#6b4a32", 7))
        k = K.ease_in_out(seg(t, 0.6, 4.2))
        with K.lit(cv, "workshop"):
            kids_ws(cv, t, c, turn_k=0.0, exprs=("awe", "awe", "awe"), look_up=-0.7)
            R.draw(cv, "meghnath", x=hx + 90, y=lerp(hy + 40, WS_FLOOR, k), s=1.15, t=t, flip=True, turn=0.4,
                   extra=dict(MEGH, brow_lift=0.0), legs="walk" if 0 < k < 1 else "stand", phase=t,
                   expr="neutral", look=(-1, 0), alpha=1.0)
        R.draw_bhaap(cv, 1060 + 30 * math.sin(t * 2), WS_FLOOR - 330, 0.85, t, mood="happy", look=(1, -0.3))


def sh22b(cv, c):
    """Rehan pokes the dusty-yellow loo-wind jar. It rattles, pops its lid, and blasts his hair flat."""
    t = c.t
    camc = ccam(780, 640, 2.5)
    ws(cv, t, camc)
    jx, jy = 900, 655
    pop = t > 2.4
    with cam(cv, camc):
        R.draw_breeze_jar(cv, jx, jy, 1.4, t, color="#e8c86a", lid=not pop, swirl=1.0,
                          rattle=1.0 if 1.2 < t < 2.4 else 0.2)
        blast = K.smooth(seg(t, 2.4, 2.7)) * (1 - K.smooth(seg(t, 3.8, 4.6)))
        with K.lit(cv, "workshop"):
            R.draw(cv, "rehan", x=760, y=WS_FLOOR, s=1.35, t=t, flip=False, turn=0.7,
                   expr="surprised" if pop else "grin", look=(1, -0.3), lean=-14 * blast,
                   arms={"r": (lerp(20, 95, seg(t, 0.4, 1.0)) * (0 if pop else 1) + (40 if pop else 0), 10)},
                   hand={"r": "point"} if not pop else {})
        if blast > 0:
            for i in range(10):
                yy = jy - 140 + i * 16
                xx = jx - 40 - ((t * 900 + i * 70) % 420)
                cv.drawLine(xx, yy, xx - 80, yy - 6, K.stroke("#e8c86a", 4, 0.8 * blast))
            fx.motes(cv, t, (420, 380, 900, 700), n=24, color="#e8c86a", a=blast, seed=40, size=3.0)
        if pop:
            k = seg(t, 2.4, 3.6)
            lx, ly = jx + 160 * k, jy - 120 - 260 * k + 320 * k * k
            cv.save(); cv.translate(lx, ly); cv.rotate(720 * k)
            cv.drawPath(K.rrect(-26, -8, 52, 16, 5), K.fill("brass")); cv.drawPath(K.rrect(-26, -8, 52, 16, 5), K.stroke("line", 2.4))
            cv.restore()


def sh22c(cv, c):
    """Tara scribbles furiously: arrows, a jar, a cloud."""
    t = c.t
    camc = ccam(640, 700, 2.7)
    ws(cv, t, camc)
    with cam(cv, camc):
        with K.lit(cv, "workshop"):
            scrub = math.sin(t * 16)
            R.draw(cv, "tara", x=640, y=WS_FLOOR, s=1.2, t=t, expr="determined", look=(0.2, 0.9), turn=0.6,
                   arms={"l": (40, 120), "r": (55 + 6 * scrub, 112 + 6 * scrub)}, hand={"r": "fist"}, head_tilt=6)
        R.draw_notebook(cv, 640 + 20, WS_FLOOR - 150 * 1.2, 1.25, open_=True)


def sh23(cv, c):
    t = c.t
    camc = ccam(860, 700, 2.0)
    ws(cv, t, camc)
    with cam(cv, camc):
        with K.lit(cv, "workshop"):
            kids_ws(cv, t, c, exprs=("awe", "neutral", "awe"), look_up=-0.5)


def sh24(cv, c):
    t = c.t
    camc = ccam(1300, 640, 2.4)
    ws(cv, t, camc)
    with cam(cv, camc):
        with K.lit(cv, "workshop"):
            meg(cv, t, c, x=1300, y=WS_FLOOR, s=1.25, flip=True, brow=0.1, expr="neutral", look=(-1.0, -0.1))


def sh25(cv, c):
    t = c.t
    camc = ccam(640, 700, 2.6)
    ws(cv, t, camc)
    with cam(cv, camc):
        with K.lit(cv, "workshop"):
            R.draw(cv, "tara", x=640, y=WS_FLOOR, s=1.2, t=t, expr="neutral", look=(1.0, -0.4), turn=0.7,
                   mouth=c.mouth("tara"), hold_l="notebook", head_tilt=6)


def sh26(cv, c):
    """He taps his own chest, once."""
    t = c.t
    camc = ccam(1300, 640, 2.4)
    ws(cv, t, camc)
    tap = math.sin(math.pi * seg(t, 1.0, 1.5))
    with cam(cv, camc):
        with K.lit(cv, "workshop"):
            meg(cv, t, c, x=1300, y=WS_FLOOR, s=1.25, flip=True, brow=0.4 * tap, expr="neutral",
                look=(-1.0, -0.1), arms={"l": (lerp(20, 40, K.smooth(seg(t, 0.4, 1.0))), lerp(20, 150, K.smooth(seg(t, 0.4, 1.0))))},
                lean=-3 * tap)


def sh27(cv, c):
    """He picks up a broom. 'Start sweeping.'"""
    t = c.t
    camc = cam_move(c.u, (1050, 680, 1.7), (1000, 690, 1.75))
    ws(cv, t, camc)
    hold = t > 1.0
    with cam(cv, camc):
        with K.lit(cv, "workshop"):
            kids_ws(cv, t, c, exprs=("neutral", "surprised" if t > 3.2 else "awe", "happy"), look_up=-0.1)
            meg(cv, t, c, x=1300, y=WS_FLOOR, s=1.25, flip=True, brow=-0.2, expr="neutral",
                look=(-1.0, 0.0), hold_l="broom" if hold else None,
                arms={"l": (lerp(10, 70, K.ease_out_back(seg(t, 1.0, 1.8))), 30)})
        if not hold:
            R.draw_broom(cv, 1400, WS_FLOOR - 10, 1.25, rot=8)


# ------------------------------------------------------------------ shots
SHOTS = [
    S("S03_SH01", sh01, 4.4, bed="heat_bed", bed_db=-22, sfx=[Sfx("bucket_clang", 0.5, -16)]),
    S("S03_SH02", sh02, lines=seq(0.3, [("meghnath", "Out.", 0)]), tail=0.7, bed="heat_bed", bed_db=-22),
    S("S03_SH03", sh03, lines=seq(0.3, [("rehan", "You made a cloud.", 0)]), tail=0.5, bed="heat_bed", bed_db=-22),
    S("S03_SH04", sh02, lines=seq(0.2, [("meghnath", "Out.", 0)]), tail=0.6, bed="heat_bed", bed_db=-22),
    S("S03_SH05", sh05, lines=seq(0.3, [("tara", "You MADE a CLOUD.", 0)]), tail=0.9, bed="heat_bed", bed_db=-22),
    S("S03_SH06", sh06, 11.0, bed="heat_bed", bed_db=-20,
      sfx=[Sfx("steam_hiss", 0, -12, dur=9.0), Sfx("cloud_puff", 3.0, -18), Sfx("whoosh", 5.2, -18)]),
    S("S03_SH07", sh07, 4.6, bed="heat_bed", bed_db=-22, sfx=[Sfx("steam_hiss", 0, -18, dur=4.6)]),
    S("S03_SH08", sh08, 6.2, music="recruited", bed="heat_bed", bed_db=-22,
      sfx=[Sfx("footsteps_soft", 0.4, -16, dur=3.0), Sfx("steam_hiss", 0, -14, dur=6.2)]),
    S("S03_SH09", sh09, 10.0, bed="heat_bed", bed_db=-22,
      sfx=[Sfx("steam_hiss", 0, -12, dur=8.0), Sfx("cloud_puff", 5.5, -10), Sfx("bhaap_coo", 6.6, -14)]),
    S("S03_SH10", sh10, 8.5, bed="heat_bed", bed_db=-24),
    S("S03_SH11", sh11, lines=seq(0.5, [("meghnath", "You touch nothing. You do exactly as I say.", 0)]), tail=0.8,
      bed="heat_bed", bed_db=-24),
    S("S03_SH12", sh12, 5.5, bed="heat_bed", bed_db=-22, sfx=[Sfx("whoosh", 0.4, -14, params={"intensity": 0.4}),
                                                              Sfx("page_turn", 1.5, -8)]),
    S("S03_SH13", sh13, lines=seq(0.3, [("tara", "What are the rules?", 0)]), tail=0.6, bed="heat_bed", bed_db=-22),
    S("S03_SH14", sh14, lines=seq(0.5, [("meghnath", "That was the rules.", 0)]), tail=1.6, bed="heat_bed",
      bed_db=-22),
    S("S03_SH15", sh15, 8.6, bed="heat_bed", bed_db=-20,
      sfx=[Sfx("footsteps_slipper", 0.0, -14, dur=6.0), Sfx("footsteps_soft", 1.0, -16, dur=6.0)]),
    S("S03_SH16", sh16, 7.0, music="workshop_reveal", bed="heat_bed", bed_db=-22,
      sfx=[Sfx("metal_hatch", 0.8, -4), Sfx("workshop_ambience", 1.4, -16, dur=5.6)]),
    S("S03_SH17", sh17, 15.0, tr="dissolve", td=0.8, bed="workshop_ambience", bed_db=-12,
      sfx=[Sfx("jar_breeze", 3.0, -18), Sfx("kite_wind", 6.0, -20)]),
    S("S03_SH17B", sh17b, 5.4, bed="workshop_ambience", bed_db=-12, sfx=[Sfx("footsteps_slipper", 0.6, -14, dur=3.6)]),
    S("S03_SH18", sh18, 7.0, bed="workshop_ambience", bed_db=-12,
      sfx=[Sfx("jar_breeze", 0.8, -12), Sfx("jar_unscrew", 3.6, -16), Sfx("shutter_rattle", 4.2, -20)]),
    S("S03_SH19", sh19, 7.8, bed="workshop_ambience", bed_db=-12, sfx=[Sfx("kite_wind", 0.5, -14)]),
    S("S03_SH20", sh20, 9.0, bed="workshop_ambience", bed_db=-12,
      sfx=[Sfx("bhaap_giggle", 1.5, -10), Sfx("spark_tzik", 2.4, -12), Sfx("spark_tzik", 4.1, -12),
           Sfx("spark_tzik", 5.6, -12)]),
    S("S03_SH21", sh21, 6.0, bed="workshop_ambience", bed_db=-12,
      sfx=[Sfx("whoosh", 0.6, -14, params={"intensity": 0.5}), Sfx("spark_tzik", 1.4, -8),
           Sfx("bhaap_giggle", 2.4, -8), Sfx("spark_tzik", 3.6, -10)]),
    S("S03_SH22", sh22, 8.0, bed="workshop_ambience", bed_db=-14),
    S("S03_SH22B", sh22b, 5.0, bed="workshop_ambience", bed_db=-14,
      sfx=[Sfx("tola_clank", 1.2, -18), Sfx("jar_unscrew", 2.3, -10), Sfx("pop", 2.4, -6), Sfx("jar_breeze", 2.45, -4),
           Sfx("whoosh", 2.5, -8, params={"intensity": 0.8})]),
    S("S03_SH22C", sh22c, 4.0, bed="workshop_ambience", bed_db=-14, sfx=[Sfx("page_turn", 0.3, -12), Sfx("page_turn", 2.4, -14)]),
    S("S03_SH23", sh23, lines=seq(0.5, [("rehan", "This is... the weather?", 0)]), tail=0.8,
      bed="workshop_ambience", bed_db=-14),
    S("S03_SH24", sh24, lines=seq(0.5, [("meghnath", "The weather of Delhi. Somebody has to keep it.", 0)]),
      tail=0.8, bed="workshop_ambience", bed_db=-14),
    S("S03_SH25", sh25, lines=seq(0.3, [("tara", "Who?", 0)]), tail=0.8, bed="workshop_ambience", bed_db=-14),
    S("S03_SH26", sh26, 3.6, bed="workshop_ambience", bed_db=-14),
    S("S03_SH27", sh27, lines=seq(1.8, [("meghnath", "Start sweeping.", 0)]), tail=2.4,
      bed="workshop_ambience", bed_db=-14, sfx=[Sfx("broom_sweep", 1.0, -14)]),
]
