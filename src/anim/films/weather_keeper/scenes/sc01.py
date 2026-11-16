"""WK sc01 HEATWAVE (00:00-02:00): the city melts, the power goes, the courtyard squabbles,
Tara's flat (Ishaan, Captain, Dadi), the stairwell and Khadoos Uncle."""
from __future__ import annotations

import math

import skia

from .... import core as K, fx
from ....core import W, H, clamp, lerp, seg
from ....timeline import Sfx
from .. import rig as R
from ..sets import skyline, block, flats, stairwell
from ..sets import weather_fx as WX
from ._util_a import S, seq, ccam, cam, cam_move, lying, title, wiggle

MEGH = {"sling": True}


# ------------------------------------------------------------------ 1. skyline + title
def sh01(cv, c):
    t = c.t
    skyline.draw_skyline(cv, t, "heat", cam_x=lerp(40, 360, K.ease_in_out(c.u)), heat=1.0)
    a = K.smooth(seg(t, 1.8, 3.6)) * (1 - K.smooth(seg(t, 10.2, 12.0)))
    title(cv, a, t)


def sh02(cv, c):
    t = c.t
    z = lerp(1.0, 1.12, K.ease_in_out(c.u))
    with cam(cv, ccam(1000, 560, z)):
        skyline.draw_chemist_sign(cv, t, heat=lerp(0.55, 1.0, K.ease_in(seg(t, 0.3, 3.9))), pop_t=4.0)


# ------------------------------------------------------------------ 2. Block C, fans stop
def sh03(cv, c):
    t = c.t
    fans = 1 - K.smooth(seg(t, 3.4, 5.6))
    with cam(cv, cam_move(c.u, (960, 520, 1.0), (960, 560, 1.06))):
        block.draw_block(cv, t, "heat", fans=fans, wind=0.15)


# ------------------------------------------------------------------ 3. courtyard tanker squabble
def sh04(cv, c):
    t = c.t
    tx = lerp(2300, 1180, K.ease_out(seg(t, 0.0, 3.6)))
    gush = K.smooth(seg(t, 4.2, 5.0))
    with cam(cv, cam_move(c.u, (1150, 820, 1.75), (1080, 830, 1.9))):
        block.draw_block(cv, t, "heat", fans=0.0, tanker_x=tx, tanker_gush=gush)
        # buckets jostling at the tap (no crowd, just buckets on the ground)
        for i, bx in enumerate((1250, 1305, 1365)):
            jig = 3 * math.sin(t * 9 + i * 2) if 4.5 < t < 10 else 0
            p = K.rrect(bx - 20 + jig, 990, 40, 38, 6)
            cv.drawPath(p, K.fill(["#3a7bd5", "#e0413a", "#f2c12e"][i]))
            cv.drawPath(p, K.stroke("line", 2.6))
        WX.heat_shimmer(cv, t, (700, 700, 1500, 1000), 0.6)


# ------------------------------------------------------------------ 4. Tara's flat
TX, TY, TS = flats.TABLE_SEAT
IX, IY, IS = flats.ISHAAN_FLOOR
SX, SY = flats.SILL_POS


def flat_room(cv, t):
    flats.draw_tara_flat(cv, t, "heat", fan=0.0, door=0.6)
    dx, dy, ds = flats.DADI_BED
    x, y, w, h = flats.DADI_DOOR
    cv.save()
    cv.clipRect(skia.Rect.MakeXYWH(x, y, w, h))
    R.draw_dadi(cv, dx, dy, ds, t, fan=0.35)
    cv.restore()


def tara_at_table(cv, t, c, expr="angry", crossing=True, look=(0.0, 0.0), turn=0.35, flip=False, stop=None):
    # crossing out the sun list: the pencil hand scrubs back and forth
    k = 0.0 if not crossing else math.sin(t * 15)
    if stop is not None and t > stop:
        k = 0.0
    R.draw(cv, "tara", x=TX, y=TY, s=TS, legs="sit", t=t, expr=expr, mouth=c.mouth("tara"), look=look,
           turn=turn, flip=flip, hold_l="notebook", arms={"r": (52 + 8 * k, 92 + 10 * k), "l": (40, 100)},
           hand={"r": "fist"})


def sh05(cv, c):
    t = c.t
    with cam(cv, cam_move(c.u, (960, 600, 1.05), (900, 640, 1.12))):
        flat_room(cv, t)
        with K.lit(cv, "heat"):
            tara_at_table(cv, t, c, expr="angry")
            lying(cv, "ishaan", IX, IY, IS, t, expr="sleepy", look=(0.6, -0.3))
        R.draw_pigeon(cv, SX, SY, 1.2, t, mode="one_leg", lid=0.6)


def sh06(cv, c):
    t = c.t
    with cam(cv, ccam(IX - 150, IY - 90, 2.1)):
        flat_room(cv, t)
        with K.lit(cv, "heat"):
            lying(cv, "ishaan", IX, IY, IS, t, expr="happy" if c.speaking("ishaan") else "sleepy",
                  mouth=c.mouth("ishaan"), look=(0.8, -0.6))
        R.draw_pigeon(cv, SX, SY, 1.2, t, mode="one_leg", lid=0.6, head_bob=0.3)


def sh07(cv, c):
    t = c.t
    with cam(cv, ccam(TX + 60, TY - 280, 2.3)):
        flat_room(cv, t)
        with K.lit(cv, "heat"):
            tara_at_table(cv, t, c, expr="neutral" if c.speaking("tara") else "smug", crossing=False,
                          look=(0.9, 0.2), turn=0.6, flip=False)


def sh08(cv, c):
    """Captain, offended, turns his back on Tara."""
    t = c.t
    z = lerp(2.8, 3.0, c.u)
    with cam(cv, ccam(SX - 60, SY - 40, z)):
        flat_room(cv, t)
        mode = "stand" if t < 1.4 else "turn_away"
        R.draw_pigeon(cv, SX, SY, 1.2, t, mode=mode, lid=0.75, head_bob=0.0 if t > 1.4 else 0.4)
        if 1.4 < t < 2.0:
            fx.vibe_lines(cv, SX, SY - 30, 30, t, a=1 - seg(t, 1.4, 2.0))


def sh09(cv, c):
    """Through the half-open door: Dadi fanning slowly under a fan that isn't turning."""
    t = c.t
    dx, dy, w, h = flats.DADI_DOOR
    with cam(cv, cam_move(c.u, (1000, 520, 1.25), (dx + w / 2, dy + h / 2 + 20, 2.25))):
        flat_room(cv, t)
        with K.lit(cv, "heat"):
            tara_at_table(cv, t, c, expr="worried", look=(1.0, -0.3), turn=0.8, stop=0.6)


def sh10(cv, c):
    t = c.t
    with cam(cv, ccam(TX + 40, TY - 300, lerp(2.4, 2.65, c.u))):
        flat_room(cv, t)
        with K.lit(cv, "heat"):
            tara_at_table(cv, t, c, expr="sad", crossing=False, look=(1.0, -0.2), turn=0.75)


# ------------------------------------------------------------------ 5. stairwell landing
LY, LS = stairwell.LANDING_Y, stairwell.LANDING_S
RX = 640
WALL = stairwell.BALL_WALL_X
STEPS = stairwell.STEPS_DOWN
STOP = STEPS[8]


def ball_cycle(t, period=0.85):
    """Rehan's ball: hand -> wall -> floor -> hand. returns (x, y, in_hand, hit_times)."""
    hx, hy = RX - 70, LY - 210
    ph = (t % period) / period
    if ph < 0.4:
        k = ph / 0.4
        return lerp(hx, WALL + 14, k), lerp(hy, LY - 240, k) - math.sin(k * math.pi) * 20
    if ph < 0.75:
        k = (ph - 0.4) / 0.35
        return lerp(WALL + 14, RX - 140, k), LY - 240 + (LY - 14 - (LY - 240)) * (k ** 1.6)
    k = (ph - 0.75) / 0.25
    return lerp(RX - 140, hx, k), lerp(LY - 14, hy, K.ease_out(k))


def rehan_bouncing(cv, t, c, freeze_t=None, look=(0.0, 0.0), expr="determined"):
    frozen = freeze_t is not None and t >= freeze_t
    R.draw(cv, "rehan", x=RX, y=LY, s=LS, t=t, flip=True, turn=0.5, expr="surprised" if frozen else expr,
           look=(0.4, -1.0) if frozen else look, arms={"r": (60 + (0 if frozen else 10 * math.sin(t * 7.4)), 70)},
           hand={"r": "open"}, mouth=c.mouth("rehan"))


def sh11(cv, c):
    t = c.t
    freeze = 6.0
    with cam(cv, cam_move(c.u, (760, 640, 1.35), (820, 620, 1.45))):
        stairwell.draw_stairwell(cv, t, "landing", "heat")
        with K.lit(cv, "heat"):
            rehan_bouncing(cv, t, c, freeze_t=freeze)
        if t < freeze:
            bx, by = ball_cycle(t)
        else:
            # missed catch: the ball rolls away toward the stairs
            k = seg(t, freeze, freeze + 2.2)
            bx, by = lerp(RX - 60, STOP[0] - 60, K.ease_out(k)), LY - 12 - abs(math.sin(k * 9)) * 30 * (1 - k)
        R.draw_ball(cv, bx, by, 1.5)


def sh12(cv, c):
    """Meghnath comes down the stairs and stops on the step above Rehan; the ball rolls to his slipper."""
    t = c.t
    with cam(cv, cam_move(c.u, (1220, 560, 1.15), (1060, 620, 1.3))):
        stairwell.draw_stairwell(cv, t, "landing", "heat")
        k = clamp(t / 5.2)
        i = k * 8
        i0, f = int(min(i, 7)), i - int(min(i, 7))
        ax, ay = STEPS[i0]
        bx, by = STEPS[min(i0 + 1, 8)]
        step_lift = math.sin(f * math.pi) * 10 if k < 1 else 0
        mx, my = lerp(ax, bx, f), lerp(ay, by, f) - step_lift
        with K.lit(cv, "heat"):
            R.draw(cv, "rehan", x=RX, y=LY, s=LS, t=t, flip=True, turn=0.6, expr="worried", look=(1.0, -0.8),
                   arms={"r": (20, 60), "l": (15, 30)})
            R.draw(cv, "meghnath", x=mx, y=my, s=LS, t=t, flip=True, turn=0.4, extra=MEGH,
                   legs="walk" if k < 1 else "stand", phase=k * 4,
                   expr="angry", look=(-0.4, 0.6) if k >= 1 else (-0.6, 0.2))
        R.draw_ball(cv, STOP[0] - 70, STOP[1] + 2, 1.5)


def sh13(cv, c):
    """He looks at the ball. Eyebrows lower like shutters."""
    t = c.t
    with cam(cv, ccam(STOP[0] + 10, STOP[1] - 400, 2.4)):
        stairwell.draw_stairwell(cv, t, "landing", "heat")
        with K.lit(cv, "heat"):
            R.draw(cv, "meghnath", x=STOP[0], y=STOP[1], s=LS, t=t, flip=True, turn=0.4, extra=dict(
                MEGH, brow_lift=lerp(0.0, -0.9, K.ease_in_out(seg(t, 0.6, 2.0)))), expr="neutral", look=(-0.4, 1.0))


def sh14(cv, c):
    """He looks at Rehan. Rehan does not breathe."""
    t = c.t
    with cam(cv, ccam(RX + 90, LY - 330, 2.4)):
        stairwell.draw_stairwell(cv, t, "landing", "heat")
        with K.lit(cv, "heat"):
            R.draw(cv, "rehan", x=RX, y=LY, s=LS, t=t, flip=True, turn=0.6, expr="worried", look=(1.0, -0.9),
                   arms={"r": (20, 60), "l": (15, 30)}, breathe=0.0)
        # a single bead of sweat
        k = seg(t, 1.0, 3.2)
        sx, sy = RX + 50, LY - 470 + 60 * K.ease_in(k)
        cv.drawPath(K.ellipse(sx, sy, 6, 9), K.fill("#bfe3ff", 0.9 * (1 - seg(t, 3.0, 3.3))))


def sh15(cv, c):
    """He picks up the ball. Looks at it. Turns. Climbs back up with it."""
    t = c.t
    with cam(cv, ccam(1180, 600, 1.3)):
        stairwell.draw_stairwell(cv, t, "landing", "heat")
        bend = math.sin(math.pi * seg(t, 0.5, 2.0))
        has = t > 1.25
        up = seg(t, 3.4, 7.0)
        i = 8 - up * 8
        i0 = int(clamp(math.floor(i), 0, 7))
        f = i - i0
        ax, ay = STEPS[i0]
        bx, by = STEPS[min(i0 + 1, 8)]
        mx, my = lerp(ax, bx, f), lerp(ay, by, f) - (math.sin(f * math.pi) * 10 if 0 < up < 1 else 0)
        flip = t < 3.2
        with K.lit(cv, "heat"):
            R.draw(cv, "rehan", x=RX, y=LY, s=LS, t=t, flip=True, turn=0.6, expr="surprised", look=(1.0, -0.6),
                   arms={"r": (lerp(20, 70, seg(t, 2.6, 3.0)), 30), "l": (15, 30)}, mouth=0.25 if t > 3.0 else 0)
            R.draw(cv, "meghnath", x=mx, y=my, s=LS, t=t, flip=flip, turn=0.4, extra=MEGH, lean=-8 * bend if flip else 0,
                   legs="walk" if 0 < up < 1 else "stand", phase=up * 4, expr="neutral",
                   look=(-0.5, 0.8) if t < 2.6 else (0.2, 0.0),
                   arms={"l": (lerp(10, 40, bend), lerp(10, 30, bend))} if t < 3.2 else {"l": (30, 80)},
                   hold_l="ball" if has else None)
        if not has:
            R.draw_ball(cv, STOP[0] - 70, STOP[1] + 2, 1.5)


def kids_whisper(cv, c, who, lx, look, expr="worried", hold_l=None):
    R.draw(cv, who, x=lx, y=LY, s=LS, t=c.t, flip=False, turn=0.55, expr=expr, look=look, mouth=c.mouth(who) * 0.7,
           hold_l=hold_l, arms={"l": (30, 110)} if who == "tara" else {})


def sh16(cv, c):
    t = c.t
    with cam(cv, ccam(RX + 60, LY - 340, 2.5)):
        stairwell.draw_stairwell(cv, t, "landing", "heat")
        with K.lit(cv, "heat"):
            R.draw(cv, "rehan", x=RX, y=LY, s=LS, t=t, flip=False, turn=0.7, expr="worried", look=(-0.8, 0.0),
                   mouth=c.mouth("rehan") * 0.6, lean=-6)


def sh17(cv, c):
    t = c.t
    with cam(cv, ccam(420, 640, 1.85)):
        stairwell.draw_stairwell(cv, t, "landing", "heat")
        with K.lit(cv, "heat"):
            kids_whisper(cv, c, "tara", 330, (0.9, -0.2), expr="smug" if t > 2.5 else "worried", hold_l="notebook")
            kids_whisper(cv, c, "ishaan", 530, (-0.6, -0.3), expr="neutral")


def sh18(cv, c):
    t = c.t
    with cam(cv, ccam(460, 640, 2.15)):
        stairwell.draw_stairwell(cv, t, "landing", "heat")
        with K.lit(cv, "heat"):
            kids_whisper(cv, c, "tara", 330, (0.9, -0.1), expr="neutral", hold_l="notebook")
            kids_whisper(cv, c, "ishaan", 530, (0.2, -1.0), expr="awe")


# ------------------------------------------------------------------ 6. the top landing, the forbidden roof door
TSTEPS = stairwell.TOP_STEPS
TOPS = stairwell.TOP_S
MD = stairwell.MEGHNATH_DOOR
RD = stairwell.ROOF_DOOR


def sh19(cv, c):
    t = c.t
    with cam(cv, cam_move(c.u, (1000, 470, 1.25), (860, 470, 1.25))):
        stairwell.draw_stairwell(cv, t, "top", "heat", gap_glow=0.8)
        # timeline: arrives at top (0-2.2), stands before roof door & looks at it (2.2-4.4),
        # walks to his own door (4.4-7.0), goes in, door shuts (7.4)
        k = seg(t, 0.0, 2.2)
        i = 7 + k * 3
        i0 = int(min(i, 9))
        f = i - i0
        ax, ay = TSTEPS[i0]
        bx, by = TSTEPS[min(i0 + 1, 10)]
        mx, my = lerp(ax, bx, f), lerp(ay, by, f) - (math.sin(f * math.pi) * 8 if k < 1 else 0)
        flip = False
        if t > 2.2:
            mx, my = TSTEPS[10]
            mx += 40 * K.ease_out(seg(t, 2.2, 3.0))
        door_x = MD[0] + MD[2] / 2
        if t > 4.4:
            flip = True
            mx = lerp(TSTEPS[10][0] + 40, door_x, K.ease_in_out(seg(t, 4.4, 7.0)))
        inside = seg(t, 7.0, 7.4)
        # open doorway while he goes in
        if 6.4 < t < 7.6:
            cv.drawRect(skia.Rect.MakeXYWH(MD[0] + 14, MD[1] + 14, MD[2] - 28, MD[3] - 14), K.fill("#2a1e1a"))
        with K.lit(cv, "heat"):
            look = (1.0, -0.2) if 2.4 < t < 4.4 else (0.0, 0.0)
            brow = -0.5 if 2.4 < t < 4.4 else 0.0
            if inside < 1:
                cv.save()
                if t > 6.4:
                    cv.clipRect(skia.Rect.MakeLTRB(0, 0, W, H))
                R.draw(cv, "meghnath", x=mx, y=my, s=TOPS, t=t, flip=flip, turn=0.5 if 2.4 < t < 4.4 else 0.3,
                       extra=dict(MEGH, brow_lift=brow), legs="walk" if (k < 1 or 4.4 < t < 7.0) else "stand",
                       phase=t * 1.3, expr="sad" if 2.4 < t < 4.4 else "neutral", look=look,
                       alpha=1 - inside, hold_l="ball")
                cv.restore()


def sh20(cv, c):
    """The roof door: fat padlock, a red-cross sign. Nobody goes through it."""
    t = c.t
    x, y, w, h = RD
    with cam(cv, cam_move(c.u, (x + w / 2, y + h / 2, 1.9), (x + w / 2 + 30, y + h / 2 - 10, 2.3))):
        stairwell.draw_stairwell(cv, t, "top", "heat", gap_glow=0.6 + 0.4 * math.sin(t * 2) ** 2)


# ------------------------------------------------------------------ shots
L04 = seq(4.6, [("neighbor_m", "I was here first!", 0.0), ("neighbor_f", "Since when?", 0.25),
                ("neighbor_m", "Since breakfast!", 0.25)])
for _l in L04:
    _l.onscreen = False

SH01_D = 12.5
SH02_D = 6.0

SHOTS = [
    S("S01_SH01", sh01, 12.5, music="heat_open", hits=[SH01_D + 4.0, SH01_D + SH02_D + 3.4],
      tr="fade_black", td=1.6, bed="heat_bed", bed_db=-12, sfx=[Sfx("heat_cicadas", 0, -18, dur=12.5)]),
    S("S01_SH02", sh02, SH02_D, bed="heat_bed", bed_db=-14, sfx=[Sfx("pop", 4.0, -2), Sfx("sparkle", 4.05, -10)]),
    S("S01_SH03", sh03, 9.0, bed="heat_bed", bed_db=-14,
      sfx=[Sfx("cooler_hum", 0, -18, dur=3.6), Sfx("ceiling_fans_stop", 3.4, -6), Sfx("power_cut_groan", 4.4, -6)]),
    S("S01_SH04", sh04, 11.0, lines=L04, music="block_life", bed="heat_bed", bed_db=-16,
      sfx=[Sfx("water_tanker", 0.0, -8, dur=6.0), Sfx("bucket_clang", 4.4, -8), Sfx("bucket_clang", 6.1, -10),
           Sfx("bucket_clang", 8.0, -9)]),
    S("S01_SH05", sh05, 6.5, bed="heat_bed", bed_db=-20, sfx=[Sfx("pigeon_coo", 2.5, -16)], tr="dissolve", td=0.6),
    S("S01_SH06", sh06, lines=seq(0.6, [("ishaan", "Captain says it's too hot to fly.", 0)]), tail=0.8,
      bed="heat_bed", bed_db=-20),
    S("S01_SH07", sh07, lines=seq(0.4, [("tara", "Pigeons don't say things.", 0)]), tail=0.6, bed="heat_bed", bed_db=-20),
    S("S01_SH08", sh08, 3.6, bed="heat_bed", bed_db=-20, sfx=[Sfx("pigeon_flap", 1.3, -12), Sfx("pigeon_coo", 1.9, -10)]),
    S("S01_SH09", sh09, 8.0, bed="heat_bed", bed_db=-22),
    S("S01_SH10", sh10, 5.5, bed="heat_bed", bed_db=-24),
    S("S01_SH11", sh11, 8.5, music="stairs_khadoos", bed="heat_bed", bed_db=-20,
      sfx=[Sfx("ball_tok", 0.34 + 0.85 * i, -6) for i in range(7)] +
          [Sfx("door_creak", 6.0, -4), Sfx("ball_tok", 6.6, -12), Sfx("ball_tok", 7.1, -16)],
      tr="dissolve", td=0.5),
    S("S01_SH12", sh12, 6.6, bed="heat_bed", bed_db=-20,
      sfx=[Sfx("footsteps_slipper", 0.0, -10, dur=5.2)]),
    S("S01_SH13", sh13, 3.4, bed="heat_bed", bed_db=-22),
    S("S01_SH14", sh14, 3.6, bed="heat_bed", bed_db=-22),
    S("S01_SH15", sh15, 7.6, bed="heat_bed", bed_db=-20, sfx=[Sfx("footsteps_slipper", 3.4, -10, dur=3.6)]),
    S("S01_SH16", sh16, lines=seq(0.5, [("rehan", "Khadoos Uncle.", 0)]), tail=0.8, bed="heat_bed", bed_db=-22),
    S("S01_SH17", sh17, lines=seq(0.3, [("tara", "He wears a cardigan. In June.", 0)]), tail=0.5, bed="heat_bed",
      bed_db=-22),
    S("S01_SH18", sh18, lines=seq(0.4, [("ishaan", "Maybe he's cold inside.", 0)]), tail=1.4, bed="heat_bed",
      bed_db=-22),
    S("S01_SH19", sh19, 8.4, bed="heat_bed", bed_db=-22,
      sfx=[Sfx("footsteps_slipper", 0.0, -12, dur=2.2), Sfx("padlock_rattle", 2.8, -18),
           Sfx("footsteps_slipper", 4.4, -12, dur=2.6), Sfx("door_creak", 6.5, -10), Sfx("bucket_clang", 7.4, -14)]),
    S("S01_SH20", sh20, 4.5, bed="heat_bed", bed_db=-22),
]
