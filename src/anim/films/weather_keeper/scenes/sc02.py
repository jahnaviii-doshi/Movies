"""WK sc02 THE ROOF (02:00-04:00): Captain slips through the gap, Ishaan follows; the pressure-cooker
whistle; Meghnath spins steam into a cloud; BHAAP is born; caught."""
from __future__ import annotations

import math

import skia

from .... import core as K, fx
from ....core import W, H, clamp, lerp, seg
from ....timeline import Sfx
from .. import rig as R
from ..sets import roof, stairwell
from ..sets import weather_fx as WX
from ._util_a import S, seq, ccam, cam, cam_move

MEGH = {"sling": True}
A = roof.ANCHORS
DOOR = A["stair_door"]               # (300, 720, 1.05)
LX, LY, LR = A["loom"]               # (930, 560, 150)
CKX, CKY = A["cooker"]
BX, BY, _BS = A["bucket_seat"]
MS = 1.3                             # Meghnath scale on the roof
TANK = (540, 845)                    # our foreground tank Ishaan hides behind
IS = 1.08                            # Ishaan scale near the tank


def tank(cv, x, y, s=1.0):
    """A black plastic water tank (foreground prop, flat graphic)."""
    w, h = 150 * s, 190 * s
    body = K.rrect(x - w / 2, y - h, w, h, 26 * s)
    cv.drawPath(body, K.fill("#23252e"))
    cv.drawRect(skia.Rect.MakeLTRB(x + w * 0.12, y - h + 10, x + w * 0.32, y - 8), K.fill("#3a3e4c"))
    for k in range(1, 4):
        yy = y - h + h * k / 4
        cv.drawLine(x - w / 2 + 4, yy, x + w / 2 - 4, yy, K.stroke("#14151b", 4))
    cv.drawPath(body, K.stroke("line", 3.2))
    lid = K.ellipse(x, y - h + 4, w * 0.32, 12 * s)
    cv.drawPath(lid, K.fill("#30333f")); cv.drawPath(lid, K.stroke("line", 2.6))


def forming_cloud(cv, x, y, k, t, s=1.0):
    """Steam thickening, whitening and rounding into a cloud. k 0..1."""
    r = K.rng(77)
    n = 16
    for i in range(n):
        start = i / n * 0.7
        a = K.smooth(seg(k, start, start + 0.25))
        if a <= 0:
            continue
        ang = r.uniform(0, 6.28) + t * (1.6 + i * 0.05) * (1 - k * 0.6)
        rad = lerp(LR * 0.9, 18, K.ease_out(seg(k, start, 0.95))) * s
        px, py = x + math.cos(ang) * rad, y + math.sin(ang) * rad * 0.55
        pr = lerp(12, 30, a) * s * (0.7 + 0.3 * math.sin(i))
        grey = 1 - K.smooth(seg(k, 0.2, 0.85))
        col = K.mix("#ffffff", "#c9ced6", grey)
        cv.drawCircle(px, py, pr, K.fill(col, 0.55 * a * (1 - K.smooth(seg(k, 0.85, 1.0)))))
    if k > 0.72:
        a = K.smooth(seg(k, 0.72, 0.95))
        R.draw_bhaap(cv, x, y, lerp(0.7, 1.0, a) * s, t, mood="sleepy", blink=1.0, alpha=a)


def meghnath_spinning(cv, t, x=BX, y=BY, s=MS, spin=1.0, expr="neutral", brow=0.0, mouth=0.0, look=(0.3, -0.6)):
    w = 3.2
    a = (148 + 16 * math.sin(t * w) * spin, 22 + 18 * math.cos(t * w) * spin)
    R.draw(cv, "meghnath", x=x, y=y, s=s, legs="sit", t=t, flip=True, turn=0.35, extra=dict(MEGH, brow_lift=brow),
           arms={"l": a}, expr=expr, look=look, mouth=mouth, head_tilt=-4)


# ------------------------------------------------------------------ stairwell
TSTEPS = stairwell.TOP_STEPS
GX, GY, GW, GH = stairwell.GAP


def sh01(cv, c):
    """Captain flaps past Ishaan's nose and slips through the crack by the roof door."""
    t = c.t
    with cam(cv, ccam(960, 640, 1.12)):
        stairwell.draw_stairwell(cv, t, "top", "evening", gap_glow=1.0)
        k = seg(t, 1.0, 5.2)
        # flight path: past Ishaan's face, up the stairwell, into the gap
        px = lerp(330, GX + 10, K.ease_in_out(k)) + 60 * math.sin(k * 6)
        py = lerp(760, GY + GH - 140, K.ease_in_out(k)) - 120 * math.sin(k * math.pi)
        x0, y0 = TSTEPS[0]
        with K.lit(cv, "heat_dusk"):
            R.draw(cv, "ishaan", x=x0 - 60, y=y0, s=1.6, t=t, expr="surprised" if 0.9 < t < 2.6 else "awe",
                   look=(clamp((px - x0) / 400, -1, 1), clamp((py - 600) / 300, -1, 1)), turn=0.5,
                   lean=-6 if 0.9 < t < 1.6 else 0)
        if t < 5.4:
            sq = 1 - 0.6 * K.smooth(seg(t, 4.8, 5.3))
            cv.save(); cv.translate(px, py); cv.scale(sq, 1)
            R.draw_pigeon(cv, 0, 0, 1.25, t, mode="fly", flip=False)
            cv.restore()
        if 0.9 < t < 1.6:
            fx.sparkles(cv, t, x0 - 40, y0 - 470, 40, 5, "#ffffff", 5, seed=4)


def sh02(cv, c):
    t = c.t
    x0, y0 = TSTEPS[0]
    with cam(cv, ccam(x0 - 40, y0 - 300, 2.4)):
        stairwell.draw_stairwell(cv, t, "top", "evening")
        with K.lit(cv, "heat_dusk"):
            R.draw(cv, "ishaan", x=x0 - 60, y=y0, s=1.6, t=t, expr="worried", look=(1.0, -1.0), turn=0.5,
                   mouth=c.mouth("ishaan"), arms={"r": (130, 20)}, hand={"r": "point"})


def sh03(cv, c):
    """He looks down the stairs at nobody. Then follows, squeezing through the gap with a pop."""
    t = c.t
    x0, y0 = TSTEPS[0]
    with cam(cv, cam_move(seg(t, 1.5, 8.0), (760, 760, 1.15), (1250, 520, 1.4))):
        stairwell.draw_stairwell(cv, t, "top", "evening", gap_glow=1.0)
        # 0-1.6 look back down; 1.6-5.6 climb; 5.6-7.0 walk to the gap; 7.0-7.8 squeeze; pop
        if t < 1.6:
            x, y, s, flip, legs, look = x0 - 60, y0, 1.6, True, "stand", (-1.0, 0.6)
        elif t < 5.6:
            k = seg(t, 1.6, 5.6)
            i = k * 10
            i0 = min(int(i), 9)
            f = i - i0
            ax, ay = TSTEPS[i0]
            bx, by = TSTEPS[i0 + 1]
            x, y = lerp(ax, bx, f), lerp(ay, by, f) - math.sin(f * math.pi) * 10
            s, flip, legs, look = lerp(1.6, 1.25, k), False, "walk", (0.6, -0.4)
        else:
            k = seg(t, 5.6, 7.0)
            x, y = lerp(TSTEPS[10][0], GX + GW / 2, K.ease_in_out(k)), TSTEPS[10][1]
            s, flip, legs, look = 1.25, False, "walk" if k < 1 else "stand", (1.0, 0.0)
        sq = 1 - 0.75 * K.smooth(seg(t, 7.0, 7.7))
        gone = t > 7.75
        if not gone:
            with K.lit(cv, "heat_dusk"):
                cv.save(); cv.translate(x, y); cv.scale(sq, 1 + 0.08 * (1 - sq)); cv.translate(-x, -y)
                R.draw(cv, "ishaan", x=x, y=y, s=s, t=t, flip=flip, legs=legs, phase=t * 1.6, expr="determined",
                       look=look, turn=0.5)
                cv.restore()
        if 7.7 < t < 8.3:
            fx.chime_rings(cv, GX + GW / 2, GY + GH - 150, 7.75, t, color="#fff6d8", n=2, max_r=70)


# ------------------------------------------------------------------ roof
def roof_wide(cv, t, steam=1.0, spin=0.0):
    roof.draw_roof(cv, t, "evening", "wide", steam_on=steam, spin=spin, cam=(960, 540, 1.0))


def sh04(cv, c):
    """Out of the gap onto the roof: a maze of black tanks under an orange haze."""
    t = c.t
    with cam(cv, cam_move(c.u, (560, 620, 1.55), (520, 640, 1.65))):
        roof_wide(cv, t, steam=0.5)
        tank(cv, TANK[0], TANK[1], 1.0)
        dx, dy, _ = DOOR
        pop = K.ease_out_back(seg(t, 0.4, 1.0))
        with K.lit(cv, "heat_dusk"):
            sq = lerp(0.3, 1.0, pop)
            cv.save(); cv.translate(dx + 40, dy + 40); cv.scale(sq, lerp(1.25, 1.0, pop)); cv.translate(-(dx + 40), -(dy + 40))
            R.draw(cv, "ishaan", x=dx + 40, y=dy + 40, s=IS * 0.95, t=t, expr="awe", look=(0.8, -0.6), turn=0.6,
                   head_tilt=-6 * math.sin(t * 0.9))
            cv.restore()


def ishaan_creep(cv, t, k, look=(1.0, -0.2), expr="awe"):
    x = lerp(DOOR[0] + 40, TANK[0] - 30, k)
    y = lerp(DOOR[1] + 40, TANK[1] - 6, k)
    s = lerp(IS * 0.95, IS, k)
    R.draw(cv, "ishaan", x=x, y=y, s=s, t=t, legs="walk" if 0 < k < 1 else "stand", phase=t * 0.9, lean=10,
           expr=expr, look=look, turn=0.7, arms={"l": (40, 70), "r": (40, 70)})


def sh05(cv, c):
    """Creeping between the tanks, low and wide-eyed."""
    t = c.t
    k = K.ease_in_out(seg(t, 0.5, 9.0))
    with cam(cv, cam_move(c.u, (430, 680, 1.7), (520, 700, 1.75))):
        roof_wide(cv, t, steam=0.6)
        with K.lit(cv, "heat_dusk"):
            ishaan_creep(cv, t, k, look=(math.sin(t * 0.8), -0.3))
        tank(cv, TANK[0], TANK[1], 1.0)


def sh06(cv, c):
    """PHWEEEEEET! The pressure cooker whistles."""
    t = c.t
    zk = K.ease_out(seg(t, 0.0, 0.25))
    with cam(cv, ccam(CKX, CKY - 40, lerp(2.8, 3.3, zk))):
        roof_wide(cv, t, steam=1.0)
        R.draw_pressure_cooker(cv, CKX, CKY + 20, 1.6, t, whistle=1.0 if 0.25 < t < 2.4 else 0.0,
                               steam=1.0 if 0.25 < t < 2.6 else 0.3)
        if 0.25 < t < 2.6:
            fx.vibe_lines(cv, CKX, CKY - 20, 90, t)


def sh07(cv, c):
    """Ishaan jumps, then peeks round the tank."""
    t = c.t
    jump = math.sin(math.pi * seg(t, 0.0, 0.5)) * 30
    with cam(cv, ccam(TANK[0] - 30, TANK[1] - 220, 2.6)):
        roof_wide(cv, t, steam=1.0)
        with K.lit(cv, "heat_dusk"):
            peek = K.ease_in_out(seg(t, 1.4, 2.6))
            R.draw(cv, "ishaan", x=TANK[0] - 30 + 70 * peek, y=TANK[1] - 6 - jump, s=IS, t=t,
                   expr="surprised" if t < 1.3 else "awe", look=(1.0, -0.4), turn=0.8, lean=lerp(0, 14, peek),
                   arms={"r": (90, 60)} if t < 1.3 else {})
        tank(cv, TANK[0] + 60, TANK[1], 1.0)


def sh08(cv, c):
    """THE SPIN: one good hand spins the steam on the antenna loom into a small, perfect cloud."""
    t = c.t
    spin = K.smooth(seg(t, 1.0, 6.0))
    k = K.ease_in_out(seg(t, 3.0, 15.0))
    camc = cam_move(seg(t, 0, 17), (800, 620, 1.55), (880, 590, 1.9))
    roof.draw_roof(cv, t, "evening", "wide", steam_on=1.0, spin=spin, cam=camc)
    with cam(cv, camc):
        WX.steam(cv, t, CKX, CKY - 30, amount=1.0 - 0.5 * k, spin=spin, loom=(LX, LY, LR), n=16)
        forming_cloud(cv, LX, LY, k, t, s=1.15)
        with K.lit(cv, "heat_dusk"):
            meghnath_spinning(cv, t, spin=lerp(1.0, 0.35, seg(t, 13, 16)), look=(0.5, -0.8), expr="neutral",
                              brow=lerp(-0.2, 0.3, seg(t, 12, 15)))
        if k > 0.95:
            fx.sparkles(cv, t, LX, LY, 120, 10, "#ffffff", 7, seed=12, a=seg(t, 14.0, 15.0))


def sh08b(cv, c):
    """The little cloud hangs over the loom in the golden haze. The old man lowers his hand."""
    t = c.t
    camc = cam_move(c.u, (760, 600, 1.45), (720, 610, 1.5))
    roof.draw_roof(cv, t, "evening", "wide", steam_on=0.3, cam=camc)
    with cam(cv, camc):
        with K.lit(cv, "heat_dusk"):
            lower = K.ease_in_out(seg(t, 0.5, 2.5))
            R.draw(cv, "meghnath", x=BX, y=BY, s=MS, legs="sit", t=t, flip=True, turn=0.35,
                   extra=dict(MEGH, brow_lift=0.4), arms={"l": (lerp(140, 30, lower), lerp(30, 70, lower))},
                   expr="happy" if t > 2.5 else "neutral", look=(0.5, -0.8), head_tilt=-4)
            R.draw(cv, "ishaan", x=TANK[0] - 30, y=TANK[1] - 6, s=IS, t=t, expr="awe", look=(1.0, -0.8), turn=0.8)
        tank(cv, TANK[0] + 30, TANK[1] + 10, 1.0)
        R.draw_bhaap(cv, LX, LY + 10 + 6 * math.sin(t), 1.1, t, mood="sleepy", blink=1.0)


def sh09(cv, c):
    """Ishaan watching, mouth open, the cloud reflected in his eyes."""
    t = c.t
    with cam(cv, ccam(TANK[0] + 50, TANK[1] - 320, 3.0)):
        roof_wide(cv, t, steam=0.8, spin=1.0)
        with K.lit(cv, "heat_dusk"):
            R.draw(cv, "ishaan", x=TANK[0] + 40, y=TANK[1] - 6, s=IS, t=t, expr="awe", look=(1.0, -0.6), turn=0.8,
                   lean=14, blink=0.0)
        tank(cv, TANK[0] - 40, TANK[1], 1.0)


def sh10(cv, c):
    """The cloud opens two dot eyes. Blinks. Sneezes a tiny spark. Tzik."""
    t = c.t
    blink = 1.0 if t < 1.3 else (1 - seg(t, 1.3, 1.6))
    if 2.6 < t < 2.8:
        blink = 1.0
    sneeze = seg(t, 3.9, 4.25)
    squash = -0.6 * math.sin(math.pi * seg(t, 3.5, 3.9)) + 0.8 * math.sin(math.pi * sneeze)
    spark = 1.0 if 4.0 < t < 4.7 else 0.0
    mood = "sleepy" if t < 1.3 else ("excited" if 4.0 < t < 5.2 else "shy")
    with cam(cv, ccam(LX, LY + 20, 3.0)):
        roof.draw_roof(cv, t, "evening", "wide", steam_on=0.3, spin=0.0, cam=ccam(LX, LY + 20, 3.0))
    with cam(cv, ccam(LX, LY + 20, 3.0)):
        R.draw_bhaap(cv, LX, LY + 10, 1.15, t, mood=mood, blink=blink, spark=spark, squash=squash,
                     look=(math.sin(t * 1.3) * 0.6, 0.0) if t > 1.6 else (0, 0))


def sh11(cv, c):
    t = c.t
    with cam(cv, ccam(TANK[0] + 50, TANK[1] - 330, 3.2)):
        roof_wide(cv, t, steam=0.5)
        with K.lit(cv, "heat_dusk"):
            R.draw(cv, "ishaan", x=TANK[0] + 40, y=TANK[1] - 6, s=IS, t=t, expr="awe", look=(1.0, -0.5), turn=0.8,
                   lean=10, mouth=c.mouth("ishaan") * 0.8)
        tank(cv, TANK[0] - 40, TANK[1], 1.0)


def sh12(cv, c):
    """Bhaap turns, sees Ishaan and zooms at him; bumps his face like a puppy. Ishaan giggles."""
    t = c.t
    ix, iy = TANK[0] + 60, TANK[1] - 6
    face = (ix + 18, iy - 250 * IS)
    with cam(cv, ccam(ix + 160, iy - 230, 2.2)):
        roof_wide(cv, t, steam=0.4)
        with K.lit(cv, "heat_dusk"):
            giggle = t > 2.6
            R.draw(cv, "ishaan", x=ix, y=iy, s=IS, t=t, expr="laugh" if giggle else "surprised",
                   look=(1.0, -0.2), turn=0.8, lean=-8 * math.sin(math.pi * seg(t, 2.2, 2.8)) + (4 if giggle else 0),
                   head_tilt=(-8 + 4 * math.sin(t * 14)) if giggle else 0, arms={"l": (60, 90), "r": (70, 80)}
                   if giggle else {})
        # zoom in from the right; bump, bounce, nuzzle
        k = seg(t, 0.9, 2.2)
        bx = lerp(ix + 520, face[0] + 64, K.ease_in(k))
        by = lerp(iy - 330, face[1], k)
        if t > 2.2:
            nuzzle = math.sin((t - 2.2) * 9) * 8 * (1 - seg(t, 4.5, 6.5))
            bx, by = face[0] + 70 + nuzzle, face[1] - 6 + abs(nuzzle) * 0.3
        sq = -0.8 * math.sin(math.pi * k) if t < 2.2 else 0.7 * math.sin(math.pi * seg(t, 2.2, 2.5))
        R.draw_bhaap(cv, bx, by, 0.9, t, mood="happy" if t > 2.3 else "excited", mouth=0.6 if t > 2.4 else 0.0,
                     spark=1.0 if 2.2 < t < 2.9 else 0.0, squash=sq, look=(-1.0, 0.0))
        if 2.2 < t < 2.6:
            fx.chime_rings(cv, face[0] + 40, face[1], 2.2, t, color="#ffffff", n=2, max_r=60)


def sh13(cv, c):
    """'WHO is on my roof?'"""
    t = c.t
    camc = ccam(BX + 30, BY - 150, 2.4)
    roof.draw_roof(cv, t, "evening", "wide", steam_on=0.4, cam=camc)
    with cam(cv, camc):
        with K.lit(cv, "heat_dusk"):
            R.draw(cv, "meghnath", x=BX, y=BY, s=MS, legs="sit", t=t, flip=False, turn=0.5,
                   extra=dict(MEGH, brow_lift=-1.0), expr="angry", look=(-1.0, 0.0),
                   mouth=c.mouth("meghnath"), head_tilt=-3, arms={"l": (40, 60)})


def sh14(cv, c):
    """Ishaan freezes. Bhaap hides behind Ishaan's head, which hides nothing."""
    t = c.t
    ix, iy = TANK[0] + 60, TANK[1] - 6
    hx, hy = ix + 18, iy - 250 * IS
    with cam(cv, ccam(ix + 20, iy - 250, 3.0)):
        roof_wide(cv, t, steam=0.3)
        dart = K.ease_out_back(seg(t, 0.3, 0.7))
        R.draw_bhaap(cv, lerp(hx + 90, hx, dart), lerp(hy - 10, hy - 6, dart), 1.0, t, mood="shy",
                     squash=0.3 * math.sin(math.pi * seg(t, 0.6, 0.9)),
                     look=(-0.2, 0.0), blink=None)
        with K.lit(cv, "heat_dusk"):
            R.draw(cv, "ishaan", x=ix, y=iy, s=IS, t=t, expr="worried", look=(-1.0, 0.0), turn=0.4, breathe=0.0,
                   blink=0.0)
        # Bhaap's eyes peeking round the side of Ishaan's head
        if t > 1.6:
            pk = K.ease_in_out(seg(t, 1.6, 2.2)) * (1 - K.ease_in_out(seg(t, 3.4, 3.9)))
            for d in (-1, 1):
                ex = hx + d * 66 * IS
                cv.drawCircle(ex + d * 6 * pk, hy - 18, 4.5 * pk, K.fill("#1d1418"))


def tumble(cv, t, who, delay, end_x, end_y, s, look):
    k = seg(t, delay, delay + 0.9)
    x = lerp(DOOR[0] + 30, end_x, K.ease_out(k))
    y = lerp(DOOR[1] + 40, end_y, k) - math.sin(k * math.pi) * 20
    stumble = 22 * math.sin(math.pi * k)
    R.draw(cv, who, x=x, y=y, s=s, t=t, legs="walk" if k < 1 else "stand", phase=t * 2, lean=stumble,
           expr="surprised" if k < 1 else ("worried" if who == "rehan" else "neutral"), look=look, turn=0.6,
           arms={"l": (80, 30), "r": (80, 30)} if k < 1 else {}, mouth=0.0)


def sh15(cv, c):
    """The roof door scrapes open: Tara and Rehan tumble through."""
    t = c.t
    with cam(cv, ccam(430, 660, 1.8)):
        roof_wide(cv, t, steam=0.3)
        with K.lit(cv, "heat_dusk"):
            tumble(cv, t, "rehan", 0.55, DOOR[0] + 210, DOOR[1] + 70, 1.12, (1.0, -0.2))
            k = seg(t, 0.3, 1.1)
            x = lerp(DOOR[0] + 30, DOOR[0] + 110, K.ease_out(k))
            y = lerp(DOOR[1] + 40, DOOR[1] + 90, k)
            R.draw(cv, "tara", x=x, y=y, s=1.12, t=t, legs="walk" if k < 1 else "stand", phase=t * 2,
                   lean=20 * math.sin(math.pi * k), expr="angry", look=(1.0, -0.1), turn=0.6,
                   mouth=c.mouth("tara"), hold_l="notebook", arms={"r": (60, 70)}, hand={"r": "point"})


def sh16(cv, c):
    """She sees the cloud. '...trouble.'"""
    t = c.t
    x, y = DOOR[0] + 110, DOOR[1] + 90
    with cam(cv, ccam(x + 30, y - 280, 3.0)):
        roof_wide(cv, t, steam=0.3)
        with K.lit(cv, "heat_dusk"):
            R.draw(cv, "tara", x=x, y=y, s=1.12, t=t, expr="awe", look=(1.0, -0.3), turn=0.7,
                   mouth=c.mouth("tara") * 0.6, hold_l="notebook", head_tilt=4 * seg(t, 0.2, 1.0))
        # spectacles glint
        g = math.sin(math.pi * seg(t, 1.6, 2.1))
        if g > 0:
            fx.star4(cv, x + 10, y - 290, 10 * g, "#ffffff", g)


def sh17(cv, c):
    """Three kids. Nobody moves."""
    t = c.t
    with cam(cv, ccam(500, 660, 1.6)):
        roof_wide(cv, t, steam=0.3)
        with K.lit(cv, "heat_dusk"):
            R.draw(cv, "tara", x=DOOR[0] + 110, y=DOOR[1] + 90, s=1.12, t=t, expr="awe", look=(1.0, -0.2),
                   turn=0.7, hold_l="notebook", breathe=0.2)
            R.draw(cv, "rehan", x=DOOR[0] + 210, y=DOOR[1] + 70, s=1.12, t=t, expr="awe", look=(1.0, -0.2),
                   turn=0.7, breathe=0.2)
            R.draw(cv, "ishaan", x=TANK[0] + 60, y=TANK[1] - 6, s=IS, t=t, expr="worried", look=(1.0, -0.1),
                   turn=0.7, breathe=0.2)
        R.draw_bhaap(cv, TANK[0] + 78 + 66, TANK[1] - 6 - 250 * IS, 1.0, t, mood="shy", look=(0.6, 0.0))
        tank(cv, TANK[0] - 70, TANK[1] + 20, 1.0)


def sh18(cv, c):
    """One grumpy old man. One cloud. Nobody moves. (an eyebrow twitches)"""
    t = c.t
    camc = ccam(BX + 50, BY - 160, 2.2)
    roof.draw_roof(cv, t, "evening", "wide", steam_on=0.3, cam=camc)
    with cam(cv, camc):
        twitch = 0.6 * math.sin(math.pi * seg(t, 2.4, 2.8))
        with K.lit(cv, "heat_dusk"):
            R.draw(cv, "meghnath", x=BX, y=BY, s=MS, legs="sit", t=t, flip=False, turn=0.5,
                   extra=dict(MEGH, brow_lift=-0.8 + twitch), expr="angry", look=(-1.0, 0.0), breathe=0.2)


# ------------------------------------------------------------------ shots
SHOTS = [
    S("S02_SH01", sh01, 6.6, tr="fade_black", td=1.0, bed="heat_bed", bed_db=-22,
      sfx=[Sfx("pigeon_flap", 1.0, -6), Sfx("pigeon_flap", 3.0, -10), Sfx("pigeon_coo", 5.0, -14)]),
    S("S02_SH02", sh02, lines=seq(0.3, [("ishaan", "Captain! You're not allowed!", 0)]), tail=0.7,
      bed="heat_bed", bed_db=-22),
    S("S02_SH03", sh03, 8.6, bed="heat_bed", bed_db=-22,
      sfx=[Sfx("footsteps_soft", 1.6, -12, dur=5.2), Sfx("pop", 7.75, -4)]),
    S("S02_SH04", sh04, 9.0, music="roof_sneak", hits=[9.0 + 11.0 + 0.25], bed="heat_bed", bed_db=-16,
      sfx=[Sfx("pigeon_flock", 2.0, -18), Sfx("steam_hiss", 0, -26, dur=8.5)]),
    S("S02_SH05", sh05, 11.0, bed="heat_bed", bed_db=-18, sfx=[Sfx("footsteps_soft", 0.5, -18, dur=8.5),
                                                              Sfx("steam_hiss", 0, -24, dur=11.0)]),
    S("S02_SH06", sh06, 2.8, bed="heat_bed", bed_db=-20, sfx=[Sfx("pressure_cooker_whistle", 0.25, 0)]),
    S("S02_SH07", sh07, 3.6, bed="heat_bed", bed_db=-20, sfx=[Sfx("steam_hiss", 0, -16, dur=3.6)]),
    S("S02_SH08", sh08, 19.0, bed="heat_bed", bed_db=-20,
      sfx=[Sfx("steam_hiss", 0, -12, dur=19.0), Sfx("cloud_puff", 9.0, -14), Sfx("cloud_puff", 12.5, -10),
           Sfx("sparkle", 14.2, -12)]),
    S("S02_SH08B", sh08b, 6.0, bed="heat_bed", bed_db=-22, sfx=[Sfx("steam_hiss", 0, -24, dur=6.0)]),
    S("S02_SH09", sh09, 4.6, bed="heat_bed", bed_db=-22, sfx=[Sfx("steam_hiss", 0, -20, dur=4.6)]),
    S("S02_SH10", sh10, 6.4, music="cloud_birth", bed="heat_bed", bed_db=-24,
      sfx=[Sfx("bhaap_coo", 1.5, -10), Sfx("bhaap_sneeze_spark", 4.0, -4)]),
    S("S02_SH11", sh11, lines=seq(0.4, [("ishaan", "Whoa.", 0)]), tail=1.0, bed="heat_bed", bed_db=-24),
    S("S02_SH12", sh12, 8.0, bed="heat_bed", bed_db=-22,
      sfx=[Sfx("whoosh", 0.9, -8, params={"intensity": 0.6}), Sfx("cloud_puff", 2.2, -6), Sfx("spark_tzik", 2.25, -10),
           Sfx("bhaap_giggle", 2.5, -8), Sfx("kids_laugh", 2.7, -18)]),
    S("S02_SH13", sh13, lines=seq(0.3, [("meghnath", "WHO is on my roof?", 0)]), tail=0.6, music="",
      bed="heat_bed", bed_db=-22),
    S("S02_SH14", sh14, 4.4, bed="heat_bed", bed_db=-22, sfx=[Sfx("whoosh", 0.3, -14, params={"intensity": 0.3})]),
    S("S02_SH15", sh15, lines=seq(0.9, [("tara", "Ishaan, we are going to be in so much—", 0)]), tail=0.0,
      bed="heat_bed", bed_db=-20, sfx=[Sfx("door_creak", 0.0, -4), Sfx("footsteps_soft", 0.3, -10, dur=1.2)]),
    S("S02_SH16", sh16, lines=seq(0.6, [("tara", "...trouble.", 0)]), tail=1.1, bed="heat_bed", bed_db=-22),
    S("S02_SH17", sh17, 6.0, music="caught", bed="heat_bed", bed_db=-22),
    S("S02_SH18", sh18, 5.0, bed="heat_bed", bed_db=-22),
]
