"""Scene 6: THE THEFT (10:30-12:30).

Amma dozes; Meher scratches Chutney's ear; a backwards red cap in the doorway. Kabir climbs to the
violet jar of wish jalebis. Tola clanks the alarm; Amma snores on; the doorway and the high shelf are
empty. Next day in the gali: syrup flood, a flying rickshaw, a bubblegum-pink buffalo... and crystal
sugar on Kabir's fingertips.
"""
from __future__ import annotations

import math

import skia

from .. import core as K, fx
from ..core import lerp, clamp, fill, stroke
from ..rig import chars, animals as A
from ..sets import shop, gali
from ..timeline import Shot, Line, Sfx
from ._util_b import bed, reach, head_world, cam, crate, finalize

SA = shop.ANCHORS
W_ = SA["wide"]
TX, TY, TS = SA["counter"]["tola"]
FULL, AFADE = 0.55, 0.3      # the shop is thinning out; Amma is pale


def hand_world(who, x, y, s, side, arm, flip=False, lean=0.0):
    """Forward kinematics for a rig hand (matches human.draw_arm)."""
    rig = chars.CAST[who]
    sgn = -1 if side == "l" else 1
    sx, sy = sgn * (rig.shoulder_w + 4), rig.neck_y + 16
    a1 = math.radians(arm[0]) * sgn
    ex, ey = sx + math.sin(a1) * rig.upper_arm, sy + math.cos(a1) * rig.upper_arm
    a2 = a1 - math.radians(arm[1]) * sgn
    hx, hy = ex + math.sin(a2) * rig.fore_arm, ey + math.cos(a2) * rig.fore_arm
    if flip:
        hx = -hx
    a = math.radians(lean)
    dx, dy = hx * s, hy * s
    return x + dx * math.cos(a) - dy * math.sin(a), y + dx * math.sin(a) + dy * math.cos(a)


def _amma_dozing(t, alpha=0.6):
    ax, ay, as_ = W_["amma"]

    def f(cv):
        nod = 6 * math.sin(t * 0.9)
        with K.lit(cv, "shop", amount=0.7, alpha=alpha, desat=AFADE):
            chars.draw(cv, "amma", x=ax, y=ay, s=as_, t=t, flip=True, expr="sleepy", blink=1.0,
                       head_tilt=14 + nod, turn=0.3, breathe=2.0)
        hx, hy = ax - 6, ay - 150 * as_
        r = 6 + 6 * (0.5 + 0.5 * math.sin(t * 1.8))
        fx.bubble(cv, hx - 26, hy + 8, r, "#ffffff", 0.7, t)
    return f


def _wide_base(cv, t, jalebi=True, amma_alpha=0.6, tola_kw=None):
    shop.draw_shop(cv, t, view="wide", fullness=FULL, fade=0.12, jalebi_jar=jalebi)
    _amma_dozing(t, amma_alpha)(cv)
    shop.draw_counter_front(cv, t, "wide", fade=0.12)
    A.draw_scale(cv, A.ScalePose(*W_["tola"][:2], s=W_["tola"][2], t=t, tarnish=0.3, **(tola_kw or {})))


DOG = (420, 1010, 0.95)
MEH = (600, 1000, 1.35)


def _meher_scratch(cv, t, look_up=0.0, scratch=True):
    dx, dy, ds = DOG
    head = (dx + 44 * ds + 10, dy - 112 * ds - 30)
    arm = reach("meher", MEH[0], MEH[1], MEH[2], "r", head, flip=True, branch=-1) if scratch else (10, 30)
    if scratch:
        arm = (arm[0] + 6 * math.sin(t * 9), arm[1])
    A.draw_dog(cv, A.DogPose(x=dx, y=dy, s=ds, t=t, mode="sit", expr="happy", tongue=scratch, ear=0.2 if scratch else 0.9,
                             head_tilt=-14 if scratch else 0, wag=1.6 if scratch else 0.6,
                             blink=1.0 if scratch else 0.0))
    chars.draw(cv, "meher", x=MEH[0], y=MEH[1], s=MEH[2], t=t, legs="kneel", flip=True, expr="happy" if look_up < 0.5 else "surprised",
               arms={"r": arm, "l": (10, 30)}, look=(0.7, 0.6) if look_up < 0.5 else (0.9, -0.6),
               turn=0.5, head_tilt=-8 * (1 - look_up))


def _doze(cv, c):
    t = c.t
    with cam(cv, 900, 620, lerp(1.0, 1.06, c.u), t=t):
        _wide_base(cv, t)
        with K.lit(cv, "shop", amount=0.7):
            _meher_scratch(cv, t)


def _cap_peek(cv, c):
    t = c.t
    dx, dy, ds = W_["door"]
    peek = K.ease_out(c.seg(0.5, 1.4))
    with cam(cv, 300, 640, 2.0, t=t):
        _wide_base(cv, t)
        with K.lit(cv, "night", amount=0.3):
            cv.save()
            clip = skia.Path(); clip.addRect(skia.Rect.MakeLTRB(0, 0, 170 + 40 * peek, 1080))
            cv.clipPath(clip, doAntiAlias=True)
            chars.draw(cv, "kabir", x=dx - 70 + 70 * peek, y=dy, s=ds, t=t, expr="determined", look=(0.9, -0.1),
                       turn=0.8, lean=10 * peek, blink=0.3)
            cv.restore()


def _tiptoe(cv, c):
    t = c.t
    dx, dy, ds = W_["door"]
    k = K.ease_in_out(c.seg(0.2, 4.0))
    x, y, s = lerp(dx + 10, 520, k), lerp(dy, 790, k), lerp(ds, 0.95, k)
    lift = abs(math.sin(t * 2.4)) * 10
    with cam(cv, 700, 600, 1.15, t=t):
        _wide_base(cv, t)
        with K.lit(cv, "shop", amount=0.7):
            chars.draw(cv, "kabir", x=x, y=y - lift, s=s, t=t, legs="walk", phase=t * 0.7, expr="determined",
                       arms={"l": (70, 40), "r": (70, 40)}, hand={"l": "open", "r": "open"}, lean=-5, turn=0.5,
                       look=(0.5, -0.5), blink=0.25)
            _meher_scratch(cv, t)


def _jar_glint(cv, c):
    t = c.t
    jx, jy, jw, jh = shop.JALEBI_JAR_POS
    z = lerp(1.0, 1.25, K.ease_in_out(c.u))
    shop.draw_shop(cv, t, view="high_shelf", fullness=FULL, fade=0.12, cam=(lerp(960, jx, c.u * 0.6), lerp(540, 420, c.u), z))
    with K.camera(cv, lerp(960, jx, c.u * 0.6), lerp(540, 420, c.u), z):
        fx.glow_dot(cv, jx, jy - jh * 0.5, 130, "violet", 0.5 + 0.2 * math.sin(t * 4))
        fx.star4(cv, jx + jw * 0.3, jy - jh * 0.8, 20 * abs(math.sin(t * 2.5)), "#ffffff", 1.0)


CS = 2.1


def _climb(cv, c):
    t = c.t
    pts = shop.CLIMB
    prog = K.ease_in_out(c.seg(0.2, 5.6)) * 2.3          # feet travel up the shelf edges
    i = min(int(prog), 2)
    f = prog - i
    fx_, fy_ = lerp(pts[i][0], pts[i + 1][0], f), lerp(pts[i][1], pts[i + 1][1], f)
    hop = math.sin(f * math.pi) * 18
    x, y = fx_ + 70, fy_ - hop
    hand_l = pts[min(i + 2, 5)]
    hand_r = pts[min(i + 3, 5)]
    arm_l = reach("kabir", x, y, CS, "l", (hand_l[0] + 20, hand_l[1]), branch=-1)
    arm_r = reach("kabir", x, y, CS, "r", (hand_r[0] + 60, hand_r[1]), branch=1)
    ccx, ccy = clamp(x + 330, 712, 1208), clamp(y - 420, 400, 680)
    shop.draw_shop(cv, t, view="high_shelf", fullness=FULL, fade=0.12, cam=(ccx, ccy, 1.35))
    with K.camera(cv, ccx, ccy, 1.35), K.lit(cv, "shop", amount=0.7):
        chars.draw(cv, "kabir", x=x, y=y, s=CS, t=t, legs="float", expr="determined", arms={"l": arm_l, "r": arm_r},
                   hand={"l": "fist", "r": "fist"}, turn=0.1, look=(0.6, -0.8), blink=0.2)


def _grab(cv, c):
    t = c.t
    jx, jy, jw, jh = shop.JALEBI_JAR_POS
    reach_in = K.ease_out(c.seg(0.2, 1.0))
    lift = K.ease_in_out(c.seg(1.3, 2.4))
    hx = lerp(jx - 700, jx - jw * 0.55, reach_in) - lift * 900
    hy = jy - jh * 0.5 - lift * 120
    with cam(cv, jx, jy - 20, 2.4, t=t):
        shop.draw_shop(cv, t, view="high_shelf", fullness=FULL, fade=0.12, jalebi_jar=False)
        sx = jx + (hx - (jx - jw * 0.55)) if reach_in >= 1 else jx
        sy = jy - lift * 120
        fx.glow_dot(cv, sx, sy - jh * 0.5, 110, "violet", 0.45)
        shop.jalebi_jar_draw(cv, sx, sy, jw, jh, 1.0, t)
        # Kabir's arm reaching in from the left: blue sleeve + hand
        arm = K.limb(hx - 400, hy + 160, hx, hy, 70, 52)
        cv.drawPath(arm, fill("skin")); cv.drawPath(arm, stroke("line", 3))
        sl = K.limb(hx - 420, hy + 170, hx - 260, hy + 105, 86, 80)
        cv.drawPath(sl, fill("tee_blue")); cv.drawPath(sl, stroke("line", 3))
        cv.drawPath(K.ellipse(hx + 6, hy, 30, 34), fill("skin")); cv.drawPath(K.ellipse(hx + 6, hy, 30, 34), stroke("line", 3))


def _alarm(cv, c):
    t = c.t
    on = t > 0.5
    with cam(cv, TX, TY - 320 * TS, 2.2, t=t, shake=4 if on else 0):
        shop.draw_shop(cv, t, view="counter", fullness=FULL, fade=0.12)
        shop.draw_counter_front(cv, t, "counter", fade=0.12)
        A.draw_scale(cv, A.ScalePose(TX, TY, s=TS, t=t, eyes="wide" if on else "closed", mouth="o" if on else "line",
                                     jitter=1.0 if on else 0.0, tarnish=0.3, tilt=8 * math.sin(t * 30) if on else 0))
        if on:
            fx.vibe_lines(cv, TX, TY - 330 * TS, 70, t, "#fff2c0", 1.0)
            fx.chime_rings(cv, TX, TY - 330 * TS, 0.5 + 0.5 * int((t - 0.5) / 0.5), t, "#fff2c0", n=2, max_r=150)


def _snores_on(cv, c):
    t = c.t
    ax, ay, as_ = W_["amma"]
    with cam(cv, ax - 20, ay - 160, 3.0, t=t):
        _wide_base(cv, t, tola_kw={"jitter": 0.6, "eyes": "wide", "mouth": "o"})
        for i in range(3):
            u = ((t * 0.7 + i * 0.33) % 1)
            K.text_center(cv, "z", ax - 40 - u * 40, ay - 190 - u * 90, size=22 + 12 * u, color="#ffffff", a=1 - u,
                          family="DejaVu Sans", shadow=False)


def _meher_looks_up(cv, c):
    t = c.t
    up = K.ease_out(c.seg(0.4, 0.8))
    with cam(cv, 560, 720, 1.9, t=t):
        _wide_base(cv, t)
        with K.lit(cv, "shop", amount=0.7):
            _meher_scratch(cv, t, look_up=up, scratch=up < 0.5)


def _empty_door(cv, c):
    t = c.t
    shop.draw_shop(cv, t, view="door", fullness=FULL, fade=0.12, cam=(960, 560, lerp(1.0, 1.12, c.u)))


def _empty_shelf(cv, c):
    t = c.t
    jx, jy, jw, jh = shop.JALEBI_JAR_POS
    z = lerp(1.2, 2.0, K.ease_in_out(c.u))
    cy = clamp(jy, 540 / z, 1080 - 540 / z)
    shop.draw_shop(cv, t, view="high_shelf", fullness=FULL, fade=0.12, jalebi_jar=False, cam=(jx, cy, z))
    with K.camera(cv, jx, cy, z):
        cv.drawPath(K.ellipse(jx, jy - 3, jw * 0.45, 8), stroke("#ffe7c0", 2.2, 0.8))
        fx.motes(cv, t, (jx - 120, jy - 150, jx + 120, jy), n=18, color="#f0dcc0", a=0.5, seed=4, size=1.3)


# ---------------------------------------------------------------- next day: the gali
CX, CY = 960, 1015                          # crate (bottom centre)
KX, KY, KSc = 960, 1015 - 118, 1.7          # Kabir standing on it


def _syrup_band(cv, x0, x1, top, bottom, t, a=0.9):
    r = skia.Rect.MakeLTRB(x0, top, x1, bottom)
    cv.drawRect(r, K.lin((0, top), (0, bottom), ["#ffcf5a", "#e8951c", "#b8600e"], a=a))
    for i in range(6):
        xx = x0 + (i + 0.5) * (x1 - x0) / 6
        cv.drawPath(K.ellipse(xx + 10 * math.sin(t * 2 + i), top + 4, 24, 4), fill("#fff2c0", 0.7 * a))


def jar_in_arm(cv, t, x, y, s, arm_l=(30, 110), lean=0.0):
    hx, hy = hand_world("kabir", x, y, s, "l", arm_l, lean=lean)
    jx, jy = hx - 6 * s, hy + 34 * s
    fx.glow_dot(cv, jx, jy - 30 * s, 60 * s, "violet", 0.35)
    shop.jalebi_jar_draw(cv, jx, jy, 46 * s, 56 * s, 1.0, t)
    # broken padlock dangling from the lid
    cv.save(); cv.translate(jx + 14 * s, jy - 52 * s); cv.rotate(20 + 10 * math.sin(t * 3))
    cv.drawPath(K.rrect(-5 * s, 0, 10 * s, 9 * s, 2 * s), fill("brass")); cv.drawPath(K.rrect(-5 * s, 0, 10 * s, 9 * s, 2 * s), stroke("line", 1.6))
    cv.drawPath(K.ellipse(-2 * s, -2 * s, 4 * s, 4 * s), stroke("brass_dark", 1.8))
    cv.restore()


def _kabir_crate(cv, t, syrup=0.0, **pose):
    crate(cv, CX, CY, 240, 118)
    if syrup > 0:
        lvl = CY - 118 * min(1, syrup * 1.25)
        _syrup_band(cv, CX - 140, CX + 140, lvl, CY + 10, t)
    p = dict(x=KX, y=KY, s=KSc, t=t, arms={"l": (30, 110), "r": (10, 20)})
    p.update(pose)
    chars.draw(cv, "kabir", **p)
    if p["arms"].get("l", (30, 110)) == (30, 110):
        jar_in_arm(cv, t, p["x"], p["y"], p["s"], lean=p.get("lean", 0.0))


def _gali_day(cv, t, syrup=0.0, rickshaw=True, z=1.0, cxy=(960, 540), shake=0.0):
    return cam(cv, cxy[0], cxy[1], z, t=t, shake=shake), lambda: gali.draw_gali(cv, t, "day", syrup=syrup, rickshaw=rickshaw)


def _crate_shot(expr="smug", arms=None, z=1.15, cxy=(960, 560), syrup=0.0, extra=None, bite=None, lean=0.0,
                head_tilt=0.0, hold=None):
    def draw(cv, c):
        t = c.t
        cm, bg = _gali_day(cv, t, syrup=syrup, z=lerp(z, z * 1.04, c.u), cxy=cxy)
        with cm:
            bg()
            with K.lit(cv, "day", amount=0.55):
                a = dict(arms or {"l": (30, 110), "r": (20, 40)})
                if bite and bite[0] < t < bite[1]:
                    hx, hy = head_world("kabir", KX, KY, KSc)
                    a["r"] = reach("kabir", KX, KY, KSc, "r", (hx + 30, hy + 70), branch=-1)
                _kabir_crate(cv, t, syrup=syrup, expr=expr, mouth=c.mouth("kabir"), arms=a, extra=extra or {},
                             lean=lean, head_tilt=head_tilt, hold=hold, look=(0, 0.2))
    return draw


def _wish_sweet(cv, c):
    t = c.t
    bite = (0.2, 1.0)
    cm, bg = _gali_day(cv, t, z=1.25, cxy=(960, 520))
    with cm:
        bg()
        with K.lit(cv, "day", amount=0.55):
            hx, hy = head_world("kabir", KX, KY, KSc)
            arm = reach("kabir", KX, KY, KSc, "r", (hx + 30, hy + 70), branch=-1) if bite[0] < t < bite[1] else \
                (150, 20)
            _kabir_crate(cv, t, expr="grin" if t < 1.2 else "happy", mouth=c.mouth("kabir") or (0.5 * abs(math.sin(t * 10)) if t < 1.0 else 0),
                         arms={"l": (30, 110), "r": arm}, hand={"r": "point"}, head_tilt=-6)
        if bite[0] < t < bite[1] + 0.3:
            fx.sparkles(cv, t, hx + 30, hy + 60, spread=40, n=6, color="violet", size=6, seed=2)


def _pause(cv, c):
    t = c.t
    drip = K.ease_in(c.seg(1.6, 2.6))
    look = 0.7 * math.copysign(1, math.sin(t * 2.2)) if t < 1.6 else 0.0
    cm, bg = _gali_day(cv, t, z=1.1, cxy=(960, 540))
    with cm:
        bg()
        with K.lit(cv, "day", amount=0.55):
            _kabir_crate(cv, t, expr="worried" if t < 1.6 else "surprised", arms={"l": (30, 110), "r": (10, 20)},
                         look=(look, 0))
        # first drip from a drainpipe
        px, py = 640, 480
        cv.drawPath(K.ellipse(px, py + drip * 380, 9, 13), fill("#ffb02e"))
        cv.drawPath(K.ellipse(px, py + drip * 380, 9, 13), stroke("#a05a10", 2))


def _flood(cv, c):
    t = c.t
    sy = K.ease_out(c.seg(0.2, 4.5)) * 0.85
    cm, bg = _gali_day(cv, t, syrup=sy, z=lerp(1.0, 1.03, c.u), cxy=(960, 540), shake=3 * clamp(1 - c.seg(0.2, 1.4)))
    with cm:
        bg()
        with K.lit(cv, "day", amount=0.55):
            _kabir_crate(cv, t, syrup=sy, expr="awe" if t < 2 else "laugh", arms={"l": (30, 110), "r": (150, 30)},
                         mouth=0.6 if t < 2 else 0.0, head_tilt=-4 + 4 * math.sin(t * 6))
        # gushing spouts from drainpipes / window boxes
        for i, (x, y, d) in enumerate([(560, 420, 1), (1380, 400, -1), (700, 300, 1), (1250, 280, -1)]):
            a = clamp(c.seg(0.2 + i * 0.2, 0.6 + i * 0.2)) * clamp(1 - c.seg(4.2, 5.4))
            p = skia.Path(); p.moveTo(x, y)
            p.quadTo(x + d * 90, y + 40, x + d * 140, 900)
            cv.drawPath(p, stroke("#ffb02e", 26, 0.9 * a)); cv.drawPath(p, stroke("#ffe08a", 8, 0.8 * a))


def _wade(cv, c):
    t = c.t
    gy, gs = gali.gali_ground(0.12)
    x = lerp(760, 1160, K.ease_in_out(c.seg(0.2, 4.4)))
    with cam(cv, 960, 640, 1.2, t=t):
        gali.draw_gali(cv, t, "day", syrup=0.85)
        crate(cv, CX - 260, CY, 240, 118)
        _syrup_band(cv, CX - 400, CX - 120, CY - 100, CY + 10, t)
        with K.lit(cv, "day", amount=0.55):
            chars.draw(cv, "kabir", x=x, y=gy, s=gs * 1.35, t=t, legs="walk", phase=t * 0.8, expr="laugh",
                       arms={"l": (30, 110), "r": (120, 40)}, lean=4 * math.sin(t * 2.4))
            jar_in_arm(cv, t, x, gy, gs * 1.35, lean=4 * math.sin(t * 2.4))
        # syrup up to his knees
        _syrup_band(cv, x - 120, x + 120, gy - 100, gy + 20, t, a=0.92)
        # the floating slipper drifting by
        sx = lerp(1500, 400, c.u)
        cv.drawPath(K.rrect(sx, gy - 112, 70, 26, 12), fill("#7b4a8f")); cv.drawPath(K.rrect(sx, gy - 112, 70, 26, 12), stroke("line", 2.4))


def _fastest(cv, c):
    t = c.t
    bite = (0.2, 0.9)
    cm, bg = _gali_day(cv, t, syrup=0.85, z=1.25, cxy=(960, 520))
    with cm:
        bg()
        with K.lit(cv, "day", amount=0.55):
            hx, hy = head_world("kabir", KX, KY, KSc)
            arm = reach("kabir", KX, KY, KSc, "r", (hx + 30, hy + 70), branch=-1) if bite[0] < t < bite[1] else (160, 30)
            _kabir_crate(cv, t, syrup=0.85, expr="grin", mouth=c.mouth("kabir"), arms={"l": (30, 110), "r": arm},
                         hand={"r": "fist"}, head_tilt=-8)


def _rickshaw_rises(cv, c):
    t = c.t
    rp = gali.RICKSHAW_POS
    rise = K.ease_in_out(c.seg(0.3, 2.4))
    spin = K.ease_in_out(c.seg(2.4, 3.6)) * 360
    zoom_off = K.ease_in(c.seg(3.8, 4.6))
    x = rp["x"] - zoom_off * 1600
    y = rp["y"] - rise * 260 - math.sin(t * 3) * 10 * rise
    with cam(cv, rp["x"] - 60, lerp(rp["y"] - 120, rp["y"] - 330, rise), 2.4, t=t,
             shake=4 * clamp(c.seg(0.2, 0.6) - c.seg(1.6, 2.2))):
        gali.draw_gali(cv, t, "day", syrup=0.85, rickshaw=False)
        cv.save(); cv.translate(x, y - 120 * rp["s"]); cv.rotate(spin); cv.translate(-x, -(y - 120 * rp["s"]))
        A.draw_rickshaw(cv, x, y, s=rp["s"], t=t, wheel_rot=t * 6 * rise)
        with K.lit(cv, "day", amount=0.55):
            chars.draw(cv, "kabir", x=x - 80 * rp["s"], y=y - 150 * rp["s"], s=rp["s"] * 0.85, t=t, legs="sit",
                       expr="surprised" if rise < 1 else "laugh", mouth=0.7, arms={"l": (150, 30), "r": (150, 30)},
                       hand={"l": "fist", "r": "fist"})
        cv.restore()
        if rise > 0.05:
            # syrup dripping off the wheels
            for i in range(4):
                u = ((t * 1.4 + i * 0.25) % 1)
                cv.drawPath(K.ellipse(x - 80 + i * 50, y + u * 200, 5, 8), fill("#ffb02e", 1 - u))


def _zoom_side(cv, c):
    t = c.t
    gy = gali.GROUND_Y_SIDE
    gali.draw_gali_side(cv, t, "day", scroll=t * 2200, syrup=0.6)
    loop = K.ease_in_out(c.seg(1.6, 2.8))
    cx, cy = 960, 520
    ang = loop * 360
    r = 220 * math.sin(loop * math.pi)
    x = cx + math.sin(math.radians(ang)) * r
    y = cy - 60 + (1 - math.cos(math.radians(ang))) * -r * 0.3 + math.sin(t * 9) * 8
    # the electricity pole it loops around
    cv.drawRect(skia.Rect.MakeLTRB(cx - 14, 120, cx + 14, gy), fill("#4a4a52"))
    cv.drawRect(skia.Rect.MakeLTRB(cx - 14, 120, cx + 14, gy), stroke("line", 3))
    cv.drawRect(skia.Rect.MakeLTRB(cx - 90, 150, cx + 90, 168), fill("#4a4a52"))
    cv.save(); cv.translate(x, y); cv.rotate(-ang - 8); cv.translate(-x, -y)
    cv.translate(x, y); cv.scale(1.5, 1.5); cv.translate(-x, -y)
    A.draw_rickshaw(cv, x, y + 140, s=1.0, t=t, wheel_rot=t * 30)
    with K.lit(cv, "day", amount=0.55):
        chars.draw(cv, "kabir", x=x - 100, y=y, s=0.95, t=t, legs="sit", expr="surprised", mouth=0.9,
                   arms={"l": (160, 20), "r": (160, 20)}, hand={"l": "fist", "r": "fist"}, head_tilt=-10)
    cv.restore()
    # speed lines
    r_ = K.rng(7)
    for i in range(14):
        yy = r_.uniform(100, 900)
        xx = (r_.uniform(0, 1920) + t * 3000) % 2400 - 240
        cv.drawLine(xx, yy, xx + 260, yy, stroke("#ffffff", 4, 0.5))


def _sploosh(cv, c):
    t = c.t
    rp = gali.RICKSHAW_POS
    drop = K.ease_in(c.seg(0.0, 0.5))
    y = lerp(rp["y"] - 700, rp["y"] + 10, drop)
    hit = c.seg(0.5, 1.6)
    with cam(cv, rp["x"] - 60, rp["y"] - 140, 2.3, t=t, shake=10 * clamp(1 - c.seg(0.5, 1.0)) if t > 0.5 else 0):
        gali.draw_gali(cv, t, "day", syrup=0.85, rickshaw=False)
        A.draw_rickshaw(cv, rp["x"], y, s=rp["s"], t=t, tilt=-6 * clamp(1 - hit))
        with K.lit(cv, "day", amount=0.55):
            chars.draw(cv, "kabir", x=rp["x"] - 80 * rp["s"], y=y - 150 * rp["s"], s=rp["s"] * 0.85, t=t, legs="sit",
                       expr="laugh" if t > 1.4 else "wince", arms={"l": (40, 60), "r": (150, 30)},
                       head_tilt=10 * math.sin(t * 5) * clamp(1 - c.seg(1.4, 2.6)))
        _syrup_band(cv, rp["x"] - 240, rp["x"] + 200, rp["y"] - 30, rp["y"] + 40, t, a=0.95)
        if 0.5 < t < 2.0:
            r_ = K.rng(3)
            for i in range(26):
                ang = r_.uniform(-170, -10)
                v = r_.uniform(250, 600)
                u = hit
                px = rp["x"] - 40 + math.cos(math.radians(ang)) * v * u
                py = rp["y"] + math.sin(math.radians(ang)) * v * u + 700 * u * u
                cv.drawCircle(px, py, r_.uniform(6, 14) * (1 - u * 0.5), fill("#ffb02e", 1 - u))


def _dripping(cv, c):
    """Dripping with syrup, Kabir pops a stray jalebi coil out of his mouth and gives a thumbs-up."""
    t = c.t
    rp = gali.RICKSHAW_POS
    thumb = K.ease_out_back(c.seg(1.2, 1.7))
    with cam(cv, rp["x"] - 110, rp["y"] - 200, 3.0, t=t):
        gali.draw_gali(cv, t, "day", syrup=0.85, rickshaw=False)
        A.draw_rickshaw(cv, rp["x"], rp["y"] + 10, s=rp["s"], t=t)
        kx, ky, ks = rp["x"] - 80 * rp["s"], rp["y"] + 10 - 150 * rp["s"], rp["s"] * 0.85
        with K.lit(cv, "day", amount=0.55):
            chars.draw(cv, "kabir", x=kx, y=ky, s=ks, t=t, legs="sit", expr="grin" if t > 1.0 else "surprised",
                       arms={"r": (lerp(20, 150, thumb), 40), "l": (20, 30)}, hand={"r": "thumbsup"},
                       mouth=0.6 if t < 0.8 else 0.0)
        _syrup_band(cv, rp["x"] - 240, rp["x"] + 200, rp["y"] - 30, rp["y"] + 40, t, a=0.95)
        hx, hy = head_world("kabir", kx, ky, ks, sit=True)
        for i in range(5):
            u = ((t * 1.1 + i * 0.2) % 1)
            cv.drawPath(K.ellipse(hx - 40 + i * 20, hy - 30 + u * 140, 3.5, 6), fill("#ffb02e", 1 - u))
        if t < 1.0:
            u = c.seg(0.2, 0.9)
            cx_, cy_ = hx + 10 + 60 * u, hy + 30 - 80 * u + 120 * u * u
            cv.drawPath(K.ellipse(cx_, cy_, 9, 9), stroke("#ff9a1a", 4))


def _tableau(cv, c):
    """Wide: syrup lane, rickshaw upside-down-ish, the pink buffalo, Kabir on his crate, arms wide."""
    t = c.t
    rp = gali.RICKSHAW_POS
    with cam(cv, 960, 560, lerp(1.0, 1.06, c.u), t=t):
        gali.draw_gali(cv, t, "day", syrup=0.85, rickshaw=False)
        A.draw_rickshaw(cv, rp["x"], rp["y"] + 10, s=rp["s"], t=t, tilt=-14)
        with K.lit(cv, "day", amount=0.55):
            A.draw_buffalo(cv, BUF[0] - 140 * BUF[2], BUF[1], s=BUF[2], t=t, pink=1.0, chew=True)
            _kabir_crate(cv, t, syrup=0.85, expr="laugh", arms={"l": (30, 110), "r": (140, 20)}, head_tilt=-6)


BUF = (gali.gali_x(0.62, -0.2), gali.gali_ground(0.62)[0], gali.gali_ground(0.62)[1] * 1.6)


def _pink_buffalo(cv, c):
    t = c.t
    pink = K.ease_in_out(c.seg(1.6, 2.6))
    with cam(cv, 960, 560, lerp(1.15, 1.3, c.u), t=t):
        gali.draw_gali(cv, t, "day", syrup=0.85)
        with K.lit(cv, "day", amount=0.55):
            A.draw_buffalo(cv, BUF[0] - 140 * BUF[2], BUF[1], s=BUF[2], t=t, pink=pink, chew=True, look=0.0)
            # Kabir in the foreground, back on his crate, biting
            hx, hy = head_world("kabir", KX, KY, KSc)
            bite = 0.3 < t < 1.1
            arm = reach("kabir", KX, KY, KSc, "r", (hx + 30, hy + 70), branch=-1) if bite else (150, 30)
            cv.save(); cv.translate(-520, 60)
            _kabir_crate(cv, t, syrup=0.85, expr="grin", arms={"l": (30, 110), "r": arm}, hand={"r": "point"}, turn=0.8)
            cv.restore()
        if pink > 0:
            fx.sparkles(cv, t, BUF[0], BUF[1] - 90 * BUF[2], spread=160 * BUF[2] + 40, n=18, color="rose", size=9,
                        seed=19, a=clamp(1 - c.seg(3.0, 4.2)) * 1.0)


def _buffalo_cu(cv, c):
    t = c.t
    with cam(cv, BUF[0] + 130 * BUF[2], BUF[1] - 150 * BUF[2], 3.4, t=t):
        gali.draw_gali(cv, t, "day", syrup=0.85)
        with K.lit(cv, "day", amount=0.55):
            A.draw_buffalo(cv, BUF[0] - 140 * BUF[2], BUF[1], s=BUF[2], t=t, pink=1.0, chew=True,
                           look=0.6 * K.ease_in_out(c.seg(0.3, 1.0)) - 0.6 * K.ease_in_out(c.seg(2.0, 2.6)))


def _bow(cv, c):
    t = c.t
    b = K.ease_in_out(c.seg(0.5, 1.2)) - K.ease_in_out(c.seg(2.4, 3.1))
    cm, bg = _gali_day(cv, t, syrup=0.85, z=1.2, cxy=(960, 540))
    with cm:
        bg()
        with K.lit(cv, "day", amount=0.55):
            _kabir_crate(cv, t, syrup=0.85, expr="grin", arms={"l": (30, 110), "r": (lerp(10, 95, b), lerp(20, 10, b))},
                         hold="cap" if b > 0.3 else None, lean=-22 * b, head_tilt=-12 * b, look=(0, 0.4))


HAND_UP = None


def _look_hand(cv, c):
    t = c.t
    hx, hy = head_world("kabir", KX, KY, KSc)
    tgt = (hx + 70, hy + 30)
    k = K.ease_out(c.seg(0.3, 1.0))
    arm = reach("kabir", KX, KY, KSc, "r", (lerp(KX + 80, tgt[0], k), lerp(KY - 100, tgt[1], k)), branch=-1)
    cr = K.ease_in(c.seg(1.0, 3.4)) * 0.7
    cm, bg = _gali_day(cv, t, syrup=0.85, z=lerp(1.6, 2.1, K.ease_in_out(c.u)), cxy=(KX + 30, hy + 60))
    with cm:
        bg()
        with K.lit(cv, "day", amount=0.55):
            _kabir_crate(cv, t, syrup=0.85, expr="grin" if t < 1.4 else "surprised", arms={"l": (30, 110), "r": arm},
                         hand={"r": "open"}, extra={"crystal": cr}, look=(0.8, 0.0) if t > 1.0 else (0, 0.3))


def _tap_jar(cv, c):
    t = c.t
    hx, hy = head_world("kabir", KX, KY, KSc)
    jar = hand_world("kabir", KX, KY, KSc, "l", (30, 110))
    taps = [0.8, 1.5]
    tap = any(a < t < a + 0.18 for a in taps)
    tgt = (jar[0] + 30, jar[1] - 40 if not tap else jar[1] - 20)
    arm = reach("kabir", KX, KY, KSc, "r", tgt, branch=-1)
    cm, bg = _gali_day(cv, t, syrup=0.85, z=2.6, cxy=(jar[0] + 20, jar[1] - 60))
    with cm:
        bg()
        with K.lit(cv, "day", amount=0.55):
            _kabir_crate(cv, t, syrup=0.85, expr="worried", arms={"l": (30, 110), "r": arm}, hand={"r": "point"},
                         extra={"crystal": 0.75})
        for a in taps:
            if a < t < a + 0.5:
                fx.star4(cv, tgt[0], tgt[1] - 10, 22 * (1 - (t - a) / 0.5), "#ffffff", 1.0)
                fx.chime_rings(cv, tgt[0], tgt[1], a, t, "#dff3ff", n=1, max_r=70)


def _pocket(cv, c):
    t = c.t
    hide = K.ease_in_out(c.seg(1.6, 2.4))
    arm = (lerp(80, 4, hide), lerp(110, 6, hide))
    hx, hy = head_world("kabir", KX, KY, KSc)
    cm, bg = _gali_day(cv, t, syrup=0.85, z=lerp(1.5, 1.65, c.u), cxy=(KX, hy + 140))
    with cm:
        bg()
        with K.lit(cv, "day", amount=0.55):
            _kabir_crate(cv, t, syrup=0.85, expr="sad" if t > 0.8 else "worried",
                         arms={"l": (30, 110), "r": arm}, hand={"r": "fist"}, extra={"crystal": 0.75 * (1 - hide)},
                         look=(0.6, 0.6) if t < 1.6 else (-0.4, 0.2), head_tilt=-6 * hide)
            if hide > 0.9:
                px, py = hand_world("kabir", KX, KY, KSc, "r", arm)
                cv.drawPath(K.rrect(px - 26, py - 22, 52, 40, 8), fill("khaki"))
                cv.drawPath(K.rrect(px - 26, py - 22, 52, 40, 8), stroke("line", 3))


SHOTS = [
    Shot("S06_01", _doze, duration=6.0, music="sneak", transition="fade_black", trans_dur=1.0,
         sfx=[bed("crickets_bed", 6.0, -22), Sfx("dog_pant", 1.0, -14)]),
    Shot("S06_02", _cap_peek, duration=3.4, sfx=[bed("crickets_bed", 3.4, -22)]),
    Shot("S06_03", _tiptoe, duration=4.6, sfx=[bed("crickets_bed", 4.6, -22), Sfx("floor_creak", 2.1, -14)]),
    Shot("S06_04", _jar_glint, duration=3.4, sfx=[bed("crickets_bed", 3.4, -22), Sfx("sparkle", 1.0, -10)]),
    Shot("S06_05", _climb, duration=6.0, sfx=[bed("crickets_bed", 6.0, -22), Sfx("floor_creak", 1.5, -16),
                                               Sfx("floor_creak", 3.8, -16)]),
    Shot("S06_06", _grab, duration=3.0, sfx=[bed("crickets_bed", 3.0, -22), Sfx("pop", 1.3, -12)]),
    Shot("S06_07", _alarm, duration=3.2, music_hits=[0.5],
         sfx=[bed("crickets_bed", 3.2, -22), Sfx("tola_alarm", 0.5, -2)]),
    Shot("S06_08", _snores_on, duration=3.2, sfx=[bed("crickets_bed", 3.2, -22), Sfx("tola_alarm", 0.0, -12)]),
    Shot("S06_09", _meher_looks_up, duration=2.8, sfx=[bed("crickets_bed", 2.8, -22)]),
    Shot("S06_10", _empty_door, duration=3.0, music="", sfx=[bed("crickets_bed", 3.0, -20)]),
    Shot("S06_11", _empty_shelf, duration=3.6, sfx=[bed("crickets_bed", 3.6, -20)]),
    # ------------------------------------------------ next day
    Shot("S06_12", _crate_shot(expr="smug", arms={"l": (30, 110), "r": (40, 120)}, z=1.0, cxy=(960, 540)),
         lines=[Line("kid1", "Show us!", at=1.0)], tail=0.6, transition="fade_black", trans_dur=1.2,
         sfx=[bed("day_bed", 4.0), Sfx("kids_gasp", 0.2, -16)]),
    Shot("S06_13", _crate_shot(expr="smug", arms={"l": (30, 110), "r": (150, 40)}, z=1.4, cxy=(960, 500)),
         lines=[Line("kabir", "Wish jalebis. One coil, one wish. Watch this.", at=0.3)], tail=0.6,
         sfx=[bed("day_bed", 5.0)]),
    Shot("S06_14", _wish_sweet, lines=[Line("kabir", "I wish this gali was the sweetest place in the world!", at=1.3)],
         tail=0.4, music="wish_chaos", sfx=[bed("day_bed", 5.0), Sfx("munch", 0.3, -6)]),
    Shot("S06_15", _pause, duration=2.8, sfx=[bed("day_bed", 2.8, -18)]),
    Shot("S06_16", _flood, duration=6.0, music_hits=[0.2],
         sfx=[bed("day_bed", 5.4, -18), Sfx("syrup_gush", 0.2, -2), Sfx("kids_gasp", 0.8, -10), Sfx("slosh", 3.0, -8)]),
    Shot("S06_17", _wade, duration=4.8, sfx=[bed("day_bed", 4.8, -18), Sfx("slosh", 0.5, -8), Sfx("slosh", 2.2, -8),
                                             Sfx("kids_laugh", 1.0, -12)]),
    Shot("S06_18", _fastest, lines=[Line("kabir", "I wish I had the fastest ride in town!", at=1.0)], tail=0.3,
         sfx=[bed("day_bed", 4.0), Sfx("munch", 0.25, -6)]),
    Shot("S06_19", _rickshaw_rises, duration=5.4,
         sfx=[bed("day_bed", 4.8, -18), Sfx("magic_float", 0.3, -6), Sfx("rickshaw_bell", 1.8, -8),
              Sfx("whoosh", 3.9, -4, params={"intensity": 1.0})]),
    Shot("S06_20", _zoom_side, duration=4.0,
         sfx=[Sfx("rickshaw_zoom", 0.0, -3), Sfx("whoosh", 1.6, -6, params={"intensity": 0.8}), Sfx("rickshaw_bell", 2.6, -8)]),
    Shot("S06_21", _sploosh, duration=3.2, sfx=[bed("day_bed", 3.2, -18), Sfx("sploosh", 0.5, 0), Sfx("kids_laugh", 1.2, -10)]),
    Shot("S06_21b", _dripping, duration=3.0, sfx=[bed("day_bed", 3.0, -18), Sfx("pop", 0.85, -10), Sfx("kids_laugh", 1.3, -12)]),
    Shot("S06_22", _crate_shot(expr="grin", arms={"l": (30, 110), "r": (40, 30)}, z=1.3, cxy=(960, 520), syrup=0.85,
                               extra={}, head_tilt=8),
         lines=[Line("kid2", "Make the buffalo pretty!", at=0.3)], tail=0.8, sfx=[bed("day_bed", 3.0)]),
    Shot("S06_23", _pink_buffalo, duration=4.6, music_hits=[1.6],
         sfx=[bed("day_bed", 4.6, -18), Sfx("munch", 0.35, -8), Sfx("sparkle", 1.6, -4), Sfx("magic_float", 1.6, -10)]),
    Shot("S06_24", _buffalo_cu, duration=3.4, sfx=[bed("day_bed", 3.4, -18), Sfx("buffalo_moo", 1.2, -2)]),
    Shot("S06_24b", _tableau, duration=3.8, sfx=[bed("day_bed", 3.8, -18), Sfx("kids_laugh", 0.3, -8)]),
    Shot("S06_25", _bow, duration=3.6, sfx=[bed("day_bed", 3.6, -18), Sfx("kids_laugh", 0.0, -4)]),
    Shot("S06_26", _look_hand, duration=4.0, music="crystal_sting", music_hits=[1.4],
         sfx=[bed("day_bed", 4.0, -20), Sfx("kids_laugh", 0.0, -14), Sfx("crystal_spread", 1.2, -6)]),
    Shot("S06_27", _tap_jar, duration=2.6, sfx=[bed("day_bed", 2.6, -20), Sfx("crystal_tink", 0.8, -4),
                                                Sfx("crystal_tink", 1.5, -6)]),
    Shot("S06_28", _pocket, duration=4.2, sfx=[bed("day_bed", 4.2, -20), Sfx("kids_laugh", 0.2, -16)]),
]

SHOTS = finalize(SHOTS, 6)
