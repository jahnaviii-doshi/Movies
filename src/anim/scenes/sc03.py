"""Scene 3 — THE RULES (03:30-06:00). Floating laddoo, Tola weighs a kindness, the flight, first light."""
from __future__ import annotations

import math

import skia

from .. import core as K, fx
from ..core import W, H, lerp, seg, ease_in_out, ease_out, ease_out_back, ease_out_elastic, smooth
from ..rig import chars
from ..sets import rooftop as RT, gali as G, wall as WL, shop as SH, aerial as AE, town
from ..timeline import Shot, Line, Sfx
from ._util_a import bed, seat, head_y, amma, tola, dog, cam as ccam

CA = SH.ANCHORS["counter"]
MEHER_SEAT = seat("charpai_meher")


def hand_pos(x, y, s, side, sh_deg, el_deg, who="meher"):
    """Screen position of a rig hand for given arm angles (mirrors human.draw_arm)."""
    rig = chars.CAST[who]
    sgn = -1 if side == "l" else 1
    sx, sy = sgn * (rig.shoulder_w + 4), rig.neck_y + 16
    a1 = math.radians(sh_deg) * sgn
    ex, ey = sx + math.sin(a1) * rig.upper_arm, sy + math.cos(a1) * rig.upper_arm
    a2 = a1 - math.radians(el_deg) * sgn
    hx, hy = ex + math.sin(a2) * rig.fore_arm, ey + math.cos(a2) * rig.fore_arm
    return x + hx * s, y + hy * s


def counter(cv, c, cam, amma_kw=None, meher_kw=None, tola_kw=None, dog_kw=None, after=None):
    """Counter view with layering: shop -> Amma -> counter front -> Tola -> dog -> Meher."""
    t = c.t
    cam = ccam(*cam)
    SH.draw_shop(cv, t, view="counter", cam=cam)
    with K.camera(cv, *cam):
        ax, ay, az = CA["amma"]
        kw = dict(expr="happy", turn=-0.3, look=(-0.8, 0.2))
        kw.update(amma_kw or {})
        amma(cv, t, ax, ay, az, mouth=c.mouth("amma"), alpha=0.82, desat=0.18, **kw)
        SH.draw_counter_front(cv, t, "counter")
        tx, ty, ts = CA["tola"]
        kw = dict(eyes="happy", mouth="smile")
        kw.update(tola_kw or {})
        tola(cv, t, tx, ty, ts, **kw)
        if dog_kw is not None:
            dx, dy, dz = CA["dog"]
            kw = dict(x=dx, y=dy, s=dz, t=t, mode="sit", ear=0.8, look_up=0.3)
            kw.update(dog_kw)
            with K.lit(cv, "shop"):
                dog(cv, **kw)
        mx, my, ms = CA["customer"]
        kw = dict(expr="awe", turn=0.5, look=(0.9, -0.3))
        kw.update(meher_kw or {})
        lift = kw.pop("lift", 0.0)
        kw.setdefault("mouth", c.mouth("meher"))
        with K.lit(cv, "shop"):
            chars.draw(cv, "meher", x=mx + kw.pop("dx", 0), y=my - lift, s=ms, t=t, **kw)
        if after:
            after(cv)


# ---------------------------------------------------------------- shelves
def sh01(cv, c):
    """Meher drifts along the shelves like a moth."""
    t = c.t
    cx = lerp(1000, 1560, ease_in_out(c.u))
    z = 1.05
    SH.draw_shop(cv, t, view="shelves", cam=(cx, 540, z))
    with K.camera(cv, cx, 540, z):
        with K.lit(cv, "shop"):
            chars.draw(cv, "meher", x=cx - 420 + 60 * math.sin(t * 0.7), y=1330, s=2.5, t=t, legs="tiptoe", turn=0.5,
                       expr="awe", look=(0.7 * math.sin(t * 0.9), -0.8), head_tilt=8 * math.sin(t * 0.6))
    fx.motes(cv, t, (0, 0, W, H), n=50, color="#ffe7a8", a=0.55, seed=21)


def sh02(cv, c):
    """The jar of floating laddoos: the laddoos bob up against the lid. 'Very popular.'"""
    t = c.t
    j = SH.FLOAT_JAR
    jx, jy = j["x"], 468
    z = lerp(2.3, 2.5, ease_in_out(c.u))
    SH.draw_shop(cv, t, view="shelves", cam=(jx, jy - 90, z))
    with K.camera(cv, jx, jy - 90, z):
        fx.glow_dot(cv, jx, jy - 90, 160, "gold", 0.25 + 0.1 * math.sin(t * 2))
    fx.sparkles(cv, t, W / 2, H / 2 - 80, spread=300, n=12, color="gold", size=8, seed=7)


def sh03(cv, c):
    """Pockets: one button and a rubber band."""
    t = c.t
    mx, my, ms = CA["customer"]
    dig = t < 1.6
    arms = {"l": (12, 10), "r": (12, 10)} if dig else {"l": (34, 70), "r": (34, 70)}
    hand = {"l": "open", "r": "open"}

    def items(cv_):
        if not dig:
            lx, ly = hand_pos(mx, my, ms, "l", 34, 70)
            rx, ry = hand_pos(mx, my, ms, "r", 34, 70)
            cv_.drawCircle(lx, ly - 22, 9, K.fill("#c9a35b")); cv_.drawCircle(lx, ly - 22, 9, K.stroke("line", 2.4))
            for d in (-3, 3):
                cv_.drawCircle(lx + d, ly - 22, 1.6, K.fill("line"))
            cv_.drawOval(skia.Rect.MakeLTRB(rx - 14, ry - 30, rx + 14, ry - 16), K.stroke("#d8333d", 3))
    counter(cv, c, (560, 640, 1.45),
            amma_kw=dict(expr="happy", look=(-0.9, 0.3)),
            meher_kw=dict(expr="worried" if t > 1.6 else "neutral", look=(0.0, 0.8) if t < 2.4 else (0.9, -0.3),
                          arms=arms, hand=hand, head_tilt=-8 if t < 2.4 else -3, dx=40),
            after=items)


def sh04(cv, c):
    """'Money?' Amma laughs, a wheezy delighted laugh; Tola wakes and rattles along."""
    t = c.t
    laugh = c.shot.lines[1].at
    lau = laugh <= t < laugh + 2.2
    counter(cv, c, (1000, 520, 1.15),
            amma_kw=dict(expr="laugh" if lau else ("surprised" if t < laugh else "happy"), look=(-0.9, 0.2),
                         head_tilt=-6 if lau else 4, lean=(-6 + 4 * math.sin(t * 14)) if lau else 0,
                         arms={"l": (40, 120), "r": (40, 120)}),
            tola_kw=dict(eyes="closed" if t < laugh + 0.3 else "happy", mouth="grin" if t > laugh + 0.3 else "line",
                         jitter=1.0 if laugh + 0.3 < t < laugh + 2.4 else 0.0),
            meher_kw=dict(expr="shy", look=(0.9, -0.3)))


def sh05(cv, c):
    """'Tola weighs something heavier.' Tola tilts a pan toward Meher, polite as a waiter."""
    t = c.t
    ln2 = c.shot.lines[1]
    bow = ease_out_back(seg(t, ln2.at + 0.8, ln2.at + 1.6))
    tap = ln2.at - 0.2 < t < ln2.at + 0.6
    counter(cv, c, (760, 560, 1.2),
            amma_kw=dict(expr="happy", look=(-0.9, 0.2), arms={"l": (40, 120), "r": (95 if tap else 40, 20 if tap else 120)},
                         hand={"r": "point" if tap else "open"}),
            tola_kw=dict(eyes="open", mouth="smile", tilt=-12 * bow),
            meher_kw=dict(expr="surprised" if bow > 0.3 else "awe", look=(0.9, -0.1)))


def sh06(cv, c):
    """Amma, gently: put your hand on the pan."""
    t = c.t
    ax, ay, az = CA["amma"]
    hy = ay + (chars.CAST["amma"].neck_y - 38) * az
    counter(cv, c, (ax - 260, hy + 120, 1.55),
            amma_kw=dict(expr="happy", look=(-0.9, 0.2), head_tilt=6 * math.sin(t * 0.7),
                         arms={"l": (40, 120), "r": (60, 60)}),
            tola_kw=dict(eyes="open", mouth="smile", tilt=-12))


def sh07(cv, c):
    """She hesitates... then lays her palm on the cold brass."""
    t = c.t
    reach = ease_in_out(seg(t, 1.4, 2.8))
    counter(cv, c, (640, 600, 1.45),
            amma_kw=dict(expr="happy", look=(-0.9, 0.3)),
            tola_kw=dict(eyes="half", mouth="line", tilt=-12),
            meher_kw=dict(expr="worried" if t < 1.4 else "determined", look=(0.9, -0.1),
                          arms={"r": (lerp(12, 82, reach), lerp(10, 0, reach)), "l": (12, 10)}, lean=4 * reach,
                          dx=lerp(0, 110, reach)))


def memory_day(cv):
    """The memory: harsh noon, Chutney panting in the shade; Meher pours her water into her hands."""
    tt = 1.0
    G.draw_gali(cv, tt, time="day")
    y, s = G.gali_ground(0.1)
    with K.lit(cv, "day"):
        dog(cv, x=1120, y=y - 20, s=s * 0.9, t=tt, mode="sit", tongue=True, flip=True, look_up=0.2, ear=0.6)
        chars.draw(cv, "meher", x=760, y=y - 10, s=s * 0.95, t=tt, expr="happy", turn=0.6, hold="bottle",
                   arms={"r": (80, 40), "l": (70, 60)}, look=(0.9, 0.4), head_tilt=8)
    for i in range(6):
        cv.drawCircle(960 + i * 6, y - 470 + i * 26, 7, K.fill("#9fd3e8", 0.9))


def sh08(cv, c):
    """From under her hand a glowing bubble rises: a memory floating in light."""
    t = c.t
    counter(cv, c, (640, 560, 1.3),
            amma_kw=dict(expr="awe", look=(-0.6, -0.6)),
            tola_kw=dict(eyes="half", mouth="o", tilt=-12),
            meher_kw=dict(expr="awe", look=(0.6, -0.9), arms={"r": (82, 0), "l": (12, 10)}, dx=110, lean=4))
    grow = ease_out(seg(t, 0.3, 3.0))
    with K.camera(cv, *ccam(640, 560, 1.3)):
        bx = lerp(560, 760, grow)
        by = lerp(760, 380, grow) + 10 * math.sin(t * 2)
        fx.memory_bubble(cv, bx, by, lerp(30, 230, grow), t, memory_day)


def sh09(cv, c):
    """Inside the bubble."""
    t = c.t
    r = lerp(620, 700, ease_in_out(c.u))
    cv.drawRect(skia.Rect.MakeWH(W, H), K.fill("#2a1608"))
    fx.memory_bubble(cv, W / 2, H / 2, r, t, memory_day, inner_scale=2 * r / H * 0.95)


def sh10(cv, c):
    """The bubble settles onto the pan. Tola's eyes open. The pan sinks: CLONK."""
    t = c.t
    settle = ease_in_out(seg(t, 0.2, 1.8))
    sink = ease_out_elastic(seg(t, 2.4, 3.6))
    tx, ty, ts = CA["tola"]
    cam = ccam(tx, ty - 190, 1.6)
    eyes = "half" if t < 2.0 else ("wide" if t < 3.0 else "happy")

    def after(cv_):
        if t < 1.8:
            px = tx - 180 * ts
            fx.memory_bubble(cv_, lerp(px + 40, px, settle), lerp(ty - 330, ty - 150 * ts - 30, settle),
                             lerp(110, 36, settle), t, memory_day)
        if t > 2.4:
            fx.chime_rings(cv_, tx, ty - 330 * ts, 2.4, t, color="gold", max_r=260)
            fx.vibe_lines(cv_, tx, ty - 200 * ts, 160 * ts, t, color="gold", a=1 - seg(t, 2.4, 3.6))
    counter(cv, c, cam, amma_kw=dict(expr="happy"),
            tola_kw=dict(eyes=eyes, mouth="o" if 2.4 < t < 3.2 else "smile", tilt=lerp(-12, -26, sink),
                         bubble_on="l" if t >= 1.8 else None, bubble_r=30, shine=0.5 * seg(t, 2.4, 3.0)),
            after=after)


def sh11(cv, c):
    """Every jar in the shop rings at once. Chutney barks twice."""
    t = c.t
    z = 1.1
    cx, cy, z = ccam(980, 560, z)
    SH.draw_shop(cv, t, view="wide", cam=(cx, cy, z))
    with K.camera(cv, cx, cy, z):
        ax, ay, az = SH.ANCHORS["wide"]["amma"]
        amma(cv, t, ax, ay, az, alpha=0.82, expr="laugh" if t < 2.5 else "happy", arms={"l": (130, 30), "r": (130, 30)})
        SH.draw_counter_front(cv, t, "wide")
        tx, ty, ts = SH.ANCHORS["wide"]["tola"]
        tola(cv, t, tx, ty, ts, eyes="happy", mouth="grin", tilt=-26, bubble_on="l", bubble_r=30, shine=0.6)
        mx, my, ms = SH.ANCHORS["wide"]["customer"]
        dx, dy, dz = SH.ANCHORS["wide"]["dog"]
        bark = (0.6 < t < 0.9) or (1.2 < t < 1.5)
        hop = math.sin(seg(t, 0.4, 1.0) * math.pi) * 30 + math.sin(seg(t, 1.0, 1.6) * math.pi) * 30
        with K.lit(cv, "shop"):
            dog(cv, x=dx, y=dy - hop, s=dz, t=t, mode="stand", ear=1.0, mouth=0.9 if bark else 0.0,
                expr="happy", look_up=0.5, wag=2.0)
            jump = math.sin(seg(t, 0.2, 0.8) * math.pi) * 50
            chars.draw(cv, "meher", x=mx + 60, y=my - jump, s=ms, t=t, expr="grin", turn=0.3,
                       arms={"l": (150, 20), "r": (150, 20)} if t < 1.6 else {"l": (40, 100), "r": (40, 100)},
                       look=(0.4, -0.5))
        for i, (jx, jy) in enumerate([(300, 260), (640, 200), (1100, 240), (1500, 300), (1750, 220), (460, 460),
                                      (1300, 460), (1650, 520)]):
            fx.chime_rings(cv, jx, jy, 0.1 + i * 0.07, t, color=["gold", "rose", "pistachio", "silver"][i % 4],
                           max_r=90, a=0.9)
    fx.sparkles(cv, t, W / 2, 300, spread=800, n=26, color="gold", size=8, seed=19)


def sh12(cv, c):
    """Silver tongs, one laddoo, a leaf. 'It lasts until first light.'"""
    t = c.t
    ax, ay, az = CA["amma"]
    hy = ay + (chars.CAST["amma"].neck_y - 38) * az
    counter(cv, c, (ax - 240, hy + 160, 1.4),
            amma_kw=dict(expr="happy", look=(-0.9, 0.3), hold="laddoo", arms={"r": (80, 40), "l": (40, 120)},
                         head_tilt=4 * math.sin(t * 0.8)),
            meher_kw=dict(expr="awe", look=(0.9, -0.3)))


def sh13(cv, c):
    """'Not one minute more.' One bony finger at the sky."""
    t = c.t
    ax, ay, az = CA["amma"]
    hy = ay + (chars.CAST["amma"].neck_y - 38) * az
    up = ease_out_back(seg(t, 0.1, 0.6))
    counter(cv, c, (ax - 100, hy + 60, 1.85),
            amma_kw=dict(expr="determined", look=(-0.7, -0.6), arms={"r": (lerp(40, 135, up), lerp(0, -35, up)), "l": (40, 120)},
                         hand={"r": "point"}, head_tilt=-6, brow=0.5),
            after=lambda cv_: fx.star4(cv_, *hand_pos(CA["amma"][0], CA["amma"][1], CA["amma"][2], "r",
                                                     lerp(40, 135, up), lerp(0, -35, up), who="amma"),
                                       14 * up * (0.7 + 0.3 * math.sin(t * 8)), "gold", up))


def sh14(cv, c):
    """She bites. Her eyes go round. Heels lift... then toes. She giggles."""
    t = c.t
    lift = ease_in_out(seg(t, 2.0, 6.2)) * 160 + (math.sin(t * 2) * 6 if t > 2.5 else 0)
    bite = 0.6 < t < 1.6
    counter(cv, c, (520, 540, 1.3),
            amma_kw=dict(expr="happy", look=(-0.9, -0.2)),
            tola_kw=dict(eyes="happy", mouth="smile", tilt=-26, bubble_on="l", bubble_r=30),
            dog_kw=dict(mode="sit", x=840, y=950, s=1.15, look_up=0.4 + lift / 400, ear=1.0, expr="alert", flip=True),
            meher_kw=dict(expr="awe" if 1.6 < t < 3.4 else ("laugh" if t > 3.4 else "happy"),
                          mouth=0.5 if bite and int(t * 8) % 2 else 0.0, hold="laddoo" if t < 1.6 else None,
                          arms={"r": (100, 120)} if t < 1.6 else ({"l": (60, 20), "r": (60, 20)} if t < 3.4 else {}),
                          legs="tiptoe" if 1.8 < t < 2.4 else ("float" if t >= 2.4 else "stand"),
                          lift=lift, look=(0.0, 0.8) if 2.0 < t < 3.4 else (0.9, -0.3)))
    if t > 1.8:
        fx.sparkles(cv, t, 480, 900 - lift, spread=140, n=12, color="gold", size=7, seed=23, rise=0.4)


def sh15(cv, c):
    """Out of the door and UP, rising like a sky lantern. Chutney bounds below, barking."""
    t = c.t
    z = lerp(1.0, 1.0, c.u)
    cy = lerp(520, 330, ease_in_out(c.u))
    WL.draw_wall(cv, t, time="night", glow=1.0, unfold=1.0, cam=(960, max(540, cy), 1.0))
    with K.camera(cv, 960, max(540, cy), 1.0):
        rise = ease_in(seg(t, 0.2, 6.5)) if False else smooth(seg(t, 0.2, 6.5))
        x = lerp(960, 1180, rise)
        y = lerp(WL.FLOOR_Y - 40, 120, rise)
        with K.lit(cv, "moon"):
            amma(cv, t, 960, WL.FLOOR_Y - 20, WL.CHAR_S * 0.95, alpha=0.8, light="shop", expr="happy",
                 look=(0.6, -0.8), arms={"r": (140, 30), "l": (40, 100)})
            bounce = abs(math.sin(t * 6)) * 30
            dog(cv, x=lerp(820, 1100, rise), y=WL.FLOOR_Y - bounce, s=WL.DOG_S, t=t, mode="stand", ear=1.0,
                look_up=1.0, mouth=0.9 if int(t * 3) % 2 == 0 else 0.1, wag=2.0)
            chars.draw(cv, "meher", x=x, y=y, s=WL.CHAR_S, t=t, legs="float", expr="laugh" if t > 2 else "awe",
                       arms={"l": (120, 20), "r": (120, 20)}, look=(0.4, 0.6), turn=0.3)
        fx.sparkles(cv, t, x, y - 200, spread=160, n=12, color="gold", size=7, seed=29, rise=0.6)


def ease_in(x):
    return K.ease_in(x)


# ---------------------------------------------------------------- the flight
def flyer(cv, x, y, s, t, rot=55, expr="laugh", wave=False, light="moon", look=(0.6, 0.3)):
    """Meher in a gliding pose, rotated about her middle."""
    cy_off = -150 * s
    cv.save()
    cv.translate(x, y + cy_off)
    cv.rotate(rot + 4 * math.sin(t * 1.4))
    cv.translate(-x, -(y + cy_off))
    arms = {"l": (160, 10), "r": (160, 10)} if not wave else {"l": (160, 10), "r": (100 + 30 * math.sin(t * 9), 40)}
    with K.lit(cv, light):
        chars.draw(cv, "meher", x=x, y=y, s=s, t=t, legs="float", expr=expr, arms=arms, look=look, turn=0.4)
    cv.restore()


def sh16(cv, c):
    """Over the moonlit rooftops of Chandpur."""
    t = c.t
    AE.draw_aerial(cv, t, scroll=t * 260, time="night")
    x = lerp(700, 980, ease_in_out(c.u))
    y = 520 + 30 * math.sin(t * 0.9)
    flyer(cv, x, y, 1.25, t, rot=62)
    fx.sparkles(cv, t, x - 220, y - 150, spread=120, n=10, color="gold", size=6, seed=31)


def sh16b(cv, c):
    """Close: wind in her braids, laughing out loud at the sky."""
    t = c.t
    with K.camera(cv, 960, 640, 1.7):
        AE.draw_aerial(cv, t, scroll=2600 + t * 520, time="night")
    x, y = 860 + 30 * math.sin(t * 0.8), 860 + 20 * math.sin(t * 1.1)
    flyer(cv, x, y, 2.6, t, rot=58, expr="laugh" if (t % 3) < 2 else "grin", look=(0.9, 0.2))
    for i in range(8):
        u = ((t * 1.3 + i / 8) % 1)
        yy = 200 + i * 95
        cv.drawLine(1900 - u * 2200, yy, 1900 - u * 2200 + 160, yy, K.stroke("#cfd8ff", 2.5, 0.35 * (1 - abs(u - 0.5) * 2)))
    fx.sparkles(cv, t, x - 300, y - 330, spread=140, n=10, color="gold", size=7, seed=47)


def sh17(cv, c):
    """Swooping past the clock tower."""
    t = c.t
    cx = lerp(200, 620, ease_in_out(c.u))
    town.draw_town(cv, t, time="night", lights=0.0, cam_x=cx)
    u = ease_in_out(seg(t, 0.3, 6.6))
    x = lerp(-200, 2100, u)
    y = 420 + math.sin(u * math.pi * 1.5) * 120
    flyer(cv, x, y, 1.05, t, rot=lerp(48, 72, u))
    fx.sparkles(cv, t, x - 160, y - 120, spread=90, n=8, color="gold", size=6, seed=37)


def sh18(cv, c):
    """Over her own roof: Nani and Kabir asleep. She waves; nobody sees."""
    t = c.t
    RT.draw_rooftop(cv, t, time="night", lantern=0.4)
    with K.lit(cv, "moon"):
        for key, who, cover in (("charpai_nani", "nani", False), ("charpai_kabir", "kabir", True)):
            sx, sy = RT.ANCHORS[key]["surface"]
            RT.draw_sleeper(cv, sx, sy, RT.ANCHORS[key]["s"], t, who=who, face_cover=cover)
    u = ease_in_out(seg(t, 0.0, 7.0))
    x = lerp(300, 1500, u)
    y = 500 + 40 * math.sin(t * 1.2)
    flyer(cv, x, y, 1.5, t, rot=lerp(20, 30, u), expr="grin", wave=True, look=(0.0, 1.0))


def sh19(cv, c):
    """A slow somersault in front of the moon."""
    t = c.t
    AE.draw_moon_sky(cv, t, time="night")
    mx, my = AE.MOON_CENTER
    spin = ease_in_out(seg(t, 1.2, 6.2)) * 360
    x = lerp(760, 1160, ease_in_out(c.u))
    s = 1.35
    cy = my + 40
    cv.save()
    cv.translate(x, cy); cv.rotate(spin + 20); cv.translate(-x, -cy)
    # a moon-rim silhouette: deep blue, warm rim
    with K.lit(cv, "moon"):
        chars.draw(cv, "meher", x=x, y=cy + 150 * s, s=s, t=t, legs="float", expr="laugh",
                   arms={"l": (150, 30), "r": (150, 30)}, turn=0.2)
    cv.restore()
    fx.sparkles(cv, t, x, cy, spread=260, n=16, color="#fff3c8", size=7, seed=41)


def sh20(cv, c):
    """The sky blushes pink at its edge. Lower now; slower."""
    t = c.t
    k = smooth(seg(t, 0.5, 5.5))
    AE.draw_aerial(cv, t, scroll=1900 + t * 150, time="night", altitude=lerp(1.0, 0.85, k))
    with K.layer(cv, alpha=k):
        AE.draw_aerial(cv, t, scroll=1900 + t * 150, time="dawn", altitude=lerp(1.0, 0.85, k))
    x = 900
    y = lerp(500, 640, k) + 20 * math.sin(t)
    flyer(cv, x, y, 1.25, t, rot=lerp(55, 20, k), expr="happy", light="dawn" if k > 0.5 else "moon")


def sh21(cv, c):
    """She sinks, light as a dropped feather, onto her charpai. Her weight comes back."""
    t = c.t
    mx, my, ms = MEHER_SEAT
    z = lerp(1.25, 1.4, ease_in_out(c.u))
    hy = head_y("meher", my, ms)
    camr = dict(cx=mx, cy=hy + 120, zoom=z)
    RT.draw_rooftop(cv, t, time="dawn", lantern=0.0, cam=camr)
    with K.camera(cv, mx, hy + 120, z):
        with K.lit(cv, "dawn"):
            for key, who, cover in (("charpai_nani", "nani", False), ("charpai_kabir", "kabir", True)):
                sx, sy = RT.ANCHORS[key]["surface"]
                RT.draw_sleeper(cv, sx, sy, RT.ANCHORS[key]["s"], t, who=who, face_cover=cover)
            d = ease_out(seg(t, 0.0, 3.2))
            land = t > 3.2
            squash = math.sin(seg(t, 3.2, 3.6) * math.pi) * 14
            y = lerp(my - 420, my, d) + (squash if land else 0)
            chars.draw(cv, "meher", x=mx + lerp(60, 0, d), y=y, s=ms, t=t, legs="sit" if land else "float",
                       expr="grin" if t > 4.2 else "happy", look=(0.3 * math.sin(t * 0.5), -0.3),
                       arms={"l": (60, 30), "r": (60, 30)} if not land else {"l": (20, 40), "r": (20, 40)},
                       head_tilt=-6 if t > 4.2 else 0)
        if t < 3.6:
            fx.sparkles(cv, t, mx, y - 180, spread=120, n=10, color="gold", size=6, seed=43,
                        a=1 - seg(t, 3.0, 3.6))


SHOTS = [
    Shot("S03_SH01", sh01, duration=8.0, sfx=[bed("night_bed", 8.0, -30), Sfx("floor_creak", 2.2, -18)]),
    Shot("S03_SH02", sh02, lines=[Line("amma", "Floating laddoo. Very popular.", at=1.6, onscreen=False)], tail=2.0,
         sfx=[Sfx("magic_float", 0.4, -16)]),
    Shot("S03_SH03", sh03, lines=[Line("meher", "I don't have any money.", at=2.5)], tail=1.0),
    Shot("S03_SH04", sh04, lines=[Line("amma", "Money?", at=0.5), Line("amma", "Hee hee hee hee!", at=1.6)],
         tail=1.2, sfx=[Sfx("tola_laugh", 2.0, -6)]),
    Shot("S03_SH05", sh05, lines=[Line("amma", "We don't take money here.", at=0.4),
                                   Line("amma", "Tola weighs something heavier.", at=2.6)], tail=1.8,
         sfx=[Sfx("tola_tink", 2.5, -10), Sfx("tola_clank", 4.6, -12)]),
    Shot("S03_SH06", sh06, lines=[Line("amma", "Put your hand on the pan.", at=0.4),
                                   Line("amma", "Think of one kind thing you did today. A true one.", at=2.6)], tail=1.0),
    Shot("S03_SH07", sh07, duration=4.0, sfx=[Sfx("tola_tink", 2.8, -12)]),
    Shot("S03_SH08", sh08, duration=4.6, music="memory", sfx=[Sfx("bubble_rise", 0.3, -6)]),
    Shot("S03_SH09", sh09, duration=7.0, transition="dissolve", trans_dur=0.6,
         sfx=[bed("day_bed", 7.0, -20), Sfx("dog_pant", 0.5, -12), Sfx("water_pour", 1.4, -10)]),
    Shot("S03_SH10", sh10, duration=4.6, transition="dissolve", trans_dur=0.6, music="shop_warm",
         sfx=[Sfx("bubble_settle", 1.4, -8), Sfx("tola_clonk", 2.4, -2)]),
    Shot("S03_SH11", sh11, duration=5.0, sfx=[Sfx("jar_chord", 0.05, -4), Sfx("dog_bark", 0.55, -8, params={"n": 2})]),
    Shot("S03_SH12", sh12, lines=[Line("amma", "One floating laddoo. It lasts until first light.", at=0.8)], tail=0.8,
         sfx=[Sfx("sparkle", 0.4, -14)]),
    Shot("S03_SH13", sh13, lines=[Line("amma", "Not one minute more.", at=0.5)], tail=1.0),
    Shot("S03_SH14", sh14, duration=8.0, sfx=[Sfx("munch", 0.7, -6), Sfx("swallow_gulp", 1.5, -10),
                                               Sfx("magic_float", 2.0, -6)]),
    Shot("S03_SH15", sh15, duration=8.0, music="flight",
         sfx=[bed("night_bed", 8.0, -18), Sfx("dog_bark", 1.0, -10, params={"n": 3}), Sfx("whoosh", 0.4, -12)]),
    Shot("S03_SH16", sh16, duration=10.0, sfx=[bed("wind_flight", 10.0, -12)]),
    Shot("S03_SH16B", sh16b, duration=6.0, sfx=[bed("wind_flight", 6.0, -10), Sfx("whoosh", 1.0, -10)]),
    Shot("S03_SH17", sh17, duration=8.0, sfx=[bed("wind_flight", 8.0, -12), Sfx("whoosh", 2.6, -8, params={"intensity": 1.0}),
                                               Sfx("clock_strike", 3.2, -18, params={"n": 1})]),
    Shot("S03_SH18", sh18, duration=8.5, sfx=[bed("wind_flight", 8.5, -18), bed("crickets_bed", 8.5, -22)]),
    Shot("S03_SH19", sh19, duration=9.0, sfx=[bed("wind_flight", 9.0, -20), Sfx("sparkle", 3.4, -12)]),
    Shot("S03_SH20", sh20, duration=7.5, transition="dissolve", trans_dur=1.0,
         sfx=[bed("wind_flight", 7.5, -16), Sfx("koel_call", 4.0, -18)]),
    Shot("S03_SH21", sh21, duration=8.5, music="dawn_soft",
         sfx=[bed("sparrows_dawn", 8.5, -16), Sfx("koel_call", 1.0, -16)]),
]
