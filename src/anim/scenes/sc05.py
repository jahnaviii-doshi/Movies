"""Scene 5: A MONTAGE OF NIGHTS (08:00-10:30).

By day, small real kindnesses (laundry for the ironing cart, water for wilted marigolds, a story
for a sleepy toddler). By night, the shop pays out: brave toffee (her shadow grows heroic and scares
off the spectacle-thief monkey) and kulfi of tongues (Chutney's one line). Each night Amma is
fainter and the shelves emptier. 'Amma, where are all the sweets going?' 'Oh, sweets come, sweets go.'
"""
from __future__ import annotations

import math

import skia

from .. import core as K, fx
from ..core import lerp, clamp, fill, stroke
from ..rig import chars, animals as A
from ..sets import rooftop, shop, day, town, gali, wall
from ..timeline import Shot, Line, Sfx
from ._util_b import bed, reach, head_world, cam, wrinkled_hand, shiny_toffee, finalize

RA = rooftop.ANCHORS
SA = shop.ANCHORS
TX, TY, TS = SA["counter"]["tola"]
MX, MY, MS = 420, 950, 1.9


def pan_top(side="l", tilt=0.0):
    ex = -180 if side == "l" else 180
    a = math.radians(tilt)
    return TX + ex * math.cos(a) * TS, TY + (-330 + ex * math.sin(a) + 150) * TS - 3


# ---------------------------------------------------------------- props
def laundry_stack(cv, x, y, s=1.0, n=7, wob=0.0):
    """A tower of folded clothes; (x, y) = bottom centre."""
    cols = ["#e9d9b0", "#7fb0d9", "#e98c8c", "#f3efe4", "#b4d98c", "#d9a8e0", "#f2c46a", "#8fc9c2"]
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    yy = 0
    for i in range(n):
        h = 16
        off = math.sin(i * 1.7) * 6 + wob * i * 1.6
        r = K.rrect(-58 + off, yy - h, 116, h, 5)
        cv.drawPath(r, fill(cols[i % len(cols)])); cv.drawPath(r, stroke("line", 2.4))
        cv.drawLine(-50 + off, yy - h / 2, 40 + off, yy - h / 2, stroke("#00000022", 1.5))
        yy -= h
    cv.restore()


def water_stream(cv, x0, y0, x1, y1, t, a=1.0):
    p = skia.Path()
    p.moveTo(x0, y0)
    p.quadTo(x0 + (x1 - x0) * 0.6, y0 - 30, x1, y1)
    cv.drawPath(p, stroke("#bfe6ff", 9, 0.85 * a))
    cv.drawPath(p, stroke("#ffffff", 3, 0.7 * a))
    for i in range(5):
        u = ((t * 2.3 + i * 0.2) % 1)
        cv.drawCircle(x1 + math.sin(i * 3) * 18 * u, y1 - 10 * u, 4 * (1 - u), fill("#e6f6ff", 0.9 * a))


def _shop_layers(cv, t, amma, tola, fullness=1.0, front=None, view="counter", fade=0.0):
    shop.draw_shop(cv, t, view=view, fullness=fullness, fade=fade)
    amma(cv)
    shop.draw_counter_front(cv, t, view, fade=fade)
    if tola:
        tola(cv)
    if front:
        with K.lit(cv, "shop", amount=0.7):
            front(cv)


def _amma(t, alpha=1.0, desat=0.0, **kw):
    ax, ay, as_ = SA["counter"]["amma"]
    pose = dict(x=ax, y=ay, s=as_, t=t, flip=True, turn=0.4)
    pose.update(kw)

    def f(cv):
        with K.lit(cv, "shop", amount=0.7, alpha=alpha, desat=desat):
            chars.draw(cv, "amma", **pose)
        if alpha < 0.95:
            fx.sparkles(cv, t, ax, ay - 220, spread=120, n=10, color="shawl_light", size=5, seed=9, a=1 - alpha,
                        rise=1.0)
    return f


# ---------------------------------------------------------------- DAY 1: laundry
def _town_day(cv, c):
    town.draw_town(cv, c.t, "day", lights=0.0, heat=0.5, cam_x=lerp(120, 300, c.u))


def _laundry_walk(cv, c):
    t = c.t
    x = lerp(-80, 820, K.ease_out(c.seg(0.0, 4.4)))
    wob = math.sin(t * 3.1) * 1.2
    day.draw_ironing_cart(cv, t)
    mx, my, ms = day.MEHER_IRON
    with K.lit(cv, "day", amount=0.6):
        chars.draw(cv, "meher", x=x, y=my, s=ms, t=t, legs="walk" if t < 4.4 else "stand", phase=t * 1.2,
                   expr="determined", arms={"l": (165, 20), "r": (165, 20)}, lean=wob * 4, look=(0.6, -0.3),
                   head_tilt=wob * 3)
        hx, hy = head_world("meher", x, my, ms, lean=wob * 4)
        laundry_stack(cv, hx + wob * 12, hy - 70 * ms, ms * 0.9, n=9, wob=wob)


def _laundry_drop(cv, c):
    t = c.t
    dx, dy = day.DROP_ANCHOR
    hx_, hy_ = day.HAND_ANCHOR
    mx, my, ms = 900, day.MEHER_IRON[1], day.MEHER_IRON[2]
    k = K.ease_in_out(c.seg(0.3, 1.3))
    with cam(cv, 1150, 560, lerp(1.15, 1.2, c.u), t=t):
        day.draw_ironing_cart(cv, t, steam=1.0 + 0.8 * c.seg(2.0, 2.6))
        hx, hy = head_world("meher", mx, my, ms)
        sx, sy = lerp(hx, dx, k), lerp(hy - 70 * ms, dy, k)
        with K.lit(cv, "day", amount=0.6):
            arms = {"l": (lerp(165, 120, k), 20), "r": (lerp(165, 120, k), 20)} if t < 1.5 else \
                {"l": (10, 20), "r": (10, 20)}
            chars.draw(cv, "meher", x=mx, y=my, s=ms, t=t, expr="happy" if t < 2.4 else "grin", arms=arms,
                       look=(0.8, -0.2) if t < 2.2 else (1, -0.4), turn=0.6)
        laundry_stack(cv, sx, sy, lerp(ms * 0.9, 1.1, k), n=9)
        thumb = K.ease_out_back(c.seg(2.0, 2.5))
        wrinkled_hand(cv, lerp(2150, hx_ - 80, thumb), hy_ + 60, 1.2, thumb=thumb, t=t)
        if t > 2.5:
            fx.star4(cv, hx_ - 120, hy_ + 10, 18 * clamp(1 - c.seg(2.5, 3.4)), "#ffffff", 1.0)


# ---------------------------------------------------------------- DAY 2: marigolds
def _marigolds(cv, c):
    t = c.t
    mx0, my, ms = day.MEHER_ANCHOR
    x = lerp(mx0 - 40, mx0 + 520, K.ease_in_out(c.seg(0.3, 5.4)))
    lift = K.ease_in_out(c.seg(0.6, 5.8))
    day.draw_balcony(cv, t, lift=lift)
    # which pot is being watered
    pots = day.POTS
    k = clamp(c.seg(0.3, 5.4))
    target = (lerp(pots[0][0], pots[3][0], k), pots[0][1] - 66)
    with K.lit(cv, "day", amount=0.6):
        hand = (target[0] - 150, target[1] - 120)
        arm = reach("meher", x, my, ms, "r", hand)
        chars.draw(cv, "meher", x=x, y=my, s=ms, t=t, legs="walk" if 0.3 < t < 5.4 else "stand",
                   phase=t * 0.8, expr="happy", arms={"r": arm, "l": (10, 30)}, hold="lota", look=(0.8, 0.6),
                   turn=0.6)
    if t > 0.4:
        water_stream(cv, hand[0] + 18, hand[1] + 10, target[0], target[1], t)


# ---------------------------------------------------------------- DAY 3: the toddler
def _toddler(cv, c):
    t = c.t
    sx, sy, ss = day.SIT_ANCHOR
    droop = K.ease_in_out(c.seg(1.2, 4.0))
    with cam(cv, sx + 120, sy - 200, lerp(1.25, 1.35, c.u), t=t):
        day.draw_room(cv, t)
        with K.lit(cv, "day", amount=0.4):
            chars.draw(cv, "meher", x=sx, y=sy, s=ss, t=t, legs="sit", expr="happy",
                       mouth=0.35 * abs(math.sin(t * 7)) * (1 - 0.7 * droop),
                       arms={"l": (40, 70), "r": (40, 70)}, hold="book", look=(0.4, 0.6) if droop < 0.6 else (0.8, 0.8),
                       head_tilt=4 + 6 * droop)
            # toddler leans over until his head rests on her lap
            cv.save()
            px, py = sx + 120 * ss, sy
            cv.translate(px, py)
            cv.rotate(-62 * droop)
            cv.translate(-px, -py)
            chars.draw(cv, "toddler", x=px, y=py, s=ss * 1.05, t=t, legs="sit", expr="sleepy",
                       blink=lerp(0.5, 1.0, droop), flip=True, turn=0.5)
            cv.restore()
        if droop > 0.9:
            # a tiny 'z'
            u = (t * 0.6) % 1
            K.text_center(cv, "z", sx + 40 * ss, sy - 140 * ss - u * 60, size=34, color="#7d6a9a", a=1 - u,
                          family="DejaVu Sans", shadow=False)


# ---------------------------------------------------------------- NIGHT: paying at Tola
def _bubble_inside_laundry(cv):
    day.draw_ironing_cart(cv, 0.0)
    chars.draw(cv, "meher", x=900, y=960, s=1.45, t=0.0, expr="happy", arms={"l": (120, 20), "r": (120, 20)})
    laundry_stack(cv, 900, 600, 1.1, n=9)


def _bubble_inside_flowers(cv):
    day.draw_balcony(cv, 0.0, lift=1.0)
    chars.draw(cv, "meher", x=760, y=960, s=1.45, t=0.0, expr="grin", hold="lota", arms={"r": (70, 10)})


def _bubble_inside_toddler(cv):
    sx, sy, ss = day.SIT_ANCHOR
    day.draw_room(cv, 0.0)
    chars.draw(cv, "meher", x=sx, y=sy, s=ss, t=0.0, legs="sit", expr="happy", hold="book",
               arms={"l": (40, 70), "r": (40, 70)})


def _pay(inside, fullness=1.0, alpha=1.0, desat=0.0, clonk_t=2.6):
    def draw(cv, c):
        t = c.t
        tilt = -14 * K.ease_out_elastic(c.seg(clonk_t, clonk_t + 0.8)) * (0.7 if alpha < 0.9 else 1.0)
        lp = pan_top("l", tilt)
        arm = reach("meher", MX, MY, MS, "r", (lp[0] - 6, lp[1] - 6), branch=-1) if t < 1.2 else (10, 30)
        rise = K.ease_out(c.seg(0.3, 1.5))
        settle = K.ease_in_out(c.seg(1.7, clonk_t))
        bx, by = lp[0] + 40 * rise * (1 - settle), lerp(lerp(lp[1], lp[1] - 260, rise), lp[1] - 44, settle)
        r = lerp(lerp(24, 120, K.ease_out_back(c.seg(0.3, 1.2))), 44, settle)
        with cam(cv, 700, 460, 1.5, t=t):
            _shop_layers(cv, t, _amma(t, alpha, desat, expr="happy", look=(0.8, 0.3)),
                         lambda cv: A.draw_scale(cv, A.ScalePose(TX, TY, s=TS, t=t, tilt=tilt,
                                                                 eyes="happy" if t > clonk_t else "open",
                                                                 mouth="smile",
                                                                 bubble_on="l" if t > clonk_t else None,
                                                                 bubble_r=40)),
                         fullness=fullness,
                         front=lambda cv: chars.draw(cv, "meher", x=MX, y=MY, s=MS, t=t,
                                                     expr="awe" if t < clonk_t else "grin",
                                                     arms={"r": arm, "l": (10, 30)}, look=(0.6, -0.6), turn=0.5))
            if t < clonk_t:
                fx.memory_bubble(cv, bx, by, r, t, inside)
            else:
                rings = 0.6 if alpha < 0.9 else 1.0
                for i, (jx, jy) in enumerate([(200, 230), (560, 120), (1000, 180), (1480, 160)]):
                    fx.chime_rings(cv, jx, jy, clonk_t + 0.05 * i, t, "gold", n=2, max_r=110 * rings, a=rings)
    return draw


def _hand_down(item, alpha=1.0, desat=0.0, fullness=1.0):
    def draw(cv, c):
        t = c.t
        ax, ay, as_ = SA["counter"]["amma"]
        k = K.ease_in_out(c.seg(0.4, 2.0))
        start = (ax - 140, ay - 260)
        end = (MX + 150, MY - 430)
        px, py = lerp(start[0], end[0], k), lerp(start[1], end[1], k) - 60 * math.sin(math.pi * k)
        amma_arm = reach("amma", ax, ay, as_, "r", (px + 20, py + 10), flip=True) if k < 0.98 else (20, 40)
        meher_arm = reach("meher", MX, MY, MS, "r", (end[0] - 4, end[1] + 16), branch=-1) if k > 0.6 else (10, 30)
        with cam(cv, 820, 470, 1.38, t=t):
            _shop_layers(cv, t, _amma(t, alpha, desat, expr="happy", arms={"r": amma_arm}, look=(0.8, 0.5)),
                         lambda cv: A.draw_scale(cv, A.ScalePose(TX, TY, s=TS, t=t, eyes="happy", mouth="smile")),
                         fullness=fullness,
                         front=lambda cv: chars.draw(cv, "meher", x=MX, y=MY, s=MS, t=t, expr="awe",
                                                     arms={"r": meher_arm, "l": (10, 30)}, look=(0.6, -0.6),
                                                     turn=0.5))
            if item == "toffee":
                shiny_toffee(cv, px, py, 1.4, t)
            else:
                cv.save(); cv.translate(px, py); cv.scale(2.0, 2.0)
                from ..rig.props import kulfi
                kulfi(cv, None)
                cv.restore()
            fx.sparkles(cv, t, px, py, spread=50, n=8, color="gold" if item == "toffee" else "pistachio", size=6,
                        seed=31)
    return draw


# ---------------------------------------------------------------- NIGHT: brave toffee vs the monkey
SHX, SHY, SHS = 330, 860, 1.6     # Meher in front of the mumty wall
MONK = RA["water_tank_top"]


def _monkey_specs(cv, c):
    t = c.t
    with cam(cv, 380, 250, lerp(2.0, 2.15, c.u), t=t):
        rooftop.draw_rooftop(cv, t, "night")
        _monkey(cv, t)
        # he admires himself: little head tilts
        if t > 1.5:
            fx.star4(cv, MONK[0] + 16, MONK[1] - 90, 10 * abs(math.sin(t * 3)), "#ffffff", 0.9)


def _nani_no_specs(cv, c):
    t = c.t
    a = RA["charpai_nani"]
    with cam(cv, a["head"][0] + 60, a["head"][1] - 20, 2.6, t=t):
        rooftop.draw_rooftop(cv, t, "night")
        rooftop.draw_sleeper(cv, a["surface"][0], a["surface"][1], a["s"] * 1.5, t, "nani")


def _meher_pose(t, eat=0.0, plant=0.0, thumbs=False, catch=0.0):
    if catch > 0:
        arms = {"l": (60, 70), "r": (60, 70)}
        return dict(expr="awe" if catch < 1 else "grin", arms=arms, hand={"l": "open", "r": "open"})
    if eat < 1:
        return dict(expr="happy", arms={"r": (40, 140)}, hold="toffee", mouth=0.5 * abs(math.sin(t * 9)) * eat)
    return dict(expr="determined" if plant > 0.5 else "awe", arms={"l": (25, 10), "r": (25, 10)},
                hand={"l": "fist", "r": "fist"})


SHB = (300, 702, 0.52)   # shadow figure base on the mumty wall (x, floor line of the wall, scale)


def _shadow_on_wall(cv, t, grow, pose):
    bx, by, bs = SHB

    def fig(cv):
        chars.draw(cv, "meher", x=bx, y=by, s=bs, t=t, legs="stand", turn=0.2, **pose)
    cv.save()
    clip = skia.Path(); clip.addRect(skia.Rect.MakeLTRB(92, 318, 470, 702))
    cv.clipPath(clip, doAntiAlias=True)
    if grow > 0.05:
        hx, hy = head_world("meher", bx, by, bs)
        sg = 1 + 1.6 * K.ease_out_back(grow, 1.2)
        cx, cy = bx + (hx - bx) * sg, by + (hy - by) * sg
        for side in (-1, 1):
            p = skia.Path()
            p.moveTo(cx + side * 30 * sg * bs, cy + 40 * sg * bs)
            p.quadTo(cx + side * (110 + 25 * math.sin(t * 4 + side)) * sg * bs, cy + 140 * sg * bs,
                     cx + side * (140 + 20 * math.sin(t * 3 + 1)) * sg * bs, cy + 300 * sg * bs)
            p.lineTo(cx + side * 20 * sg * bs, cy + 160 * sg * bs)
            p.close()
            cv.drawPath(p, fill("#0a0618", 0.6 * grow))
    fx.hero_shadow(cv, fig, bx, by, grow=grow, a=0.72, skew=-0.06 * grow)
    cv.restore()


def _brave(cv, c):
    """She eats the toffee; her shadow on the wall grows tall and heroic before she does."""
    t = c.t
    eat = clamp(c.seg(0.2, 1.4))
    grow = K.ease_in_out(c.seg(1.8, 4.8))
    plant = c.seg(4.6, 5.0)
    pose = _meher_pose(t, eat if t < 1.5 else 1.0, plant)
    with cam(cv, 420, 420, lerp(1.5, 1.4, c.u), t=t):
        rooftop.draw_rooftop(cv, t, "night", lantern=1.0)
        _shadow_on_wall(cv, t, grow, {k: v for k, v in pose.items() if k != "hold"})
        with K.lit(cv, "moon", amount=0.6):
            chars.draw(cv, "meher", x=SHX + 220, y=SHY, s=SHS, t=t, legs="stand", turn=0.2, **pose)
        _monkey(cv, t)
        if t < 1.5:
            fx.sparkles(cv, t, SHX + 260, SHY - 330, spread=40, n=6, color="rose", size=6, seed=3)
        if 1.8 < t < 5.0:
            fx.sparkles(cv, t, 280, 480, spread=150, n=12, color="rose", size=7, seed=8, a=grow)


def _monkey(cv, t, specs=True, flee=0.0, dx=0.0, dy=0.0):
    x, y = MONK[0] + dx, MONK[1] + 6 + dy
    fx.glow_dot(cv, x + 6, y - 60, 120, "#9fb3ff", 0.35)
    A.draw_monkey(cv, x, y, s=MONK[2] * 1.25, t=t, holding_specs=specs, flee=flee)


def _monkey_flees(cv, c):
    t = c.t
    flee = K.ease_in(c.seg(1.0, 2.4))
    drop = K.ease_in(c.seg(0.9, 1.6))
    with cam(cv, 380, 300, 1.8, t=t, shake=3 * clamp(c.seg(0.0, 0.3) - c.seg(0.6, 0.9))):
        rooftop.draw_rooftop(cv, t, "night")
        _shadow_on_wall(cv, t, 1.0, dict(expr="determined", arms={"l": (25, 10), "r": (25, 10)},
                                         hand={"l": "fist", "r": "fist"}))
        _monkey(cv, t, specs=t < 0.9, flee=1.0 if t > 0.5 else 0.0, dx=flee * 700, dy=-flee * 160)
        if t > 0.9:
            sx, sy = MONK[0] - 20, lerp(MONK[1] - 80, 760, drop)
            cv.save(); cv.translate(sx, sy); cv.rotate(t * 400); cv.scale(2.2, 2.2)
            from ..rig.props import specs
            specs(cv, None)
            cv.restore()
        if 0.3 < t < 1.0:
            fx.vibe_lines(cv, MONK[0] + 4, MONK[1] - 80, 40, t, "#cfd6e3", 1.0)


def _catch(cv, c):
    t = c.t
    catch = K.ease_out(c.seg(0.1, 0.5))
    thumb = K.ease_out_back(c.seg(1.6, 2.1))
    mx = SHX + 220
    with cam(cv, 420, 420, 1.4, t=t):
        rooftop.draw_rooftop(cv, t, "night", lantern=1.0)
        _shadow_on_wall(cv, t, 1.0, dict(expr="determined",
                                         arms={"r": (lerp(25, 165, thumb), lerp(10, 30, thumb)), "l": (25, 10)},
                                         hand={"r": "thumbsup" if thumb > 0.5 else "fist", "l": "fist"}))
        hx, hy = head_world("meher", mx, SHY, SHS)
        hold = (mx + 110, hy + 40)
        arm = reach("meher", mx, SHY, SHS, "r", hold, branch=-1)
        with K.lit(cv, "moon", amount=0.6):
            chars.draw(cv, "meher", x=mx, y=SHY, s=SHS, t=t, turn=0.6 if t > 1.4 else 0.2,
                       expr="grin" if t > 0.6 else "awe", arms={"r": arm, "l": (10, 20)},
                       look=(-0.9, -0.8) if t > 1.4 else (0.6, -0.2), head_tilt=-6 if t > 1.4 else 4)
        yy = lerp(hold[1] - 420, hold[1], catch)
        cv.save(); cv.translate(hold[0] + 4, yy - 6); cv.scale(2.4, 2.4)
        from ..rig.props import specs
        specs(cv, None)
        cv.restore()
        if t > 1.9:
            fx.star4(cv, 200, 330, 22 * clamp(1 - c.seg(2.0, 3.0)), "#ffffff", 1.0)


def _specs_back(cv, c):
    """She slips the spectacles gently back onto sleeping Nani."""
    t = c.t
    a = RA["charpai_nani"]
    k = K.ease_in_out(c.seg(0.4, 2.2))
    hx, hy = a["head"]
    with cam(cv, hx + 120, hy - 60, 2.0, t=t):
        rooftop.draw_rooftop(cv, t, "night")
        rooftop.draw_sleeper(cv, a["surface"][0], a["surface"][1], a["s"] * 1.5, t, "nani")
        ex, ey = hx + 12, hy - 8
        sx, sy = lerp(hx + 220, ex, k), lerp(hy - 160, ey, k)
        cv.save(); cv.translate(sx, sy); cv.rotate(lerp(-30, -90, k)); cv.scale(lerp(2.0, 1.3, k), lerp(2.0, 1.3, k))
        from ..rig.props import specs
        specs(cv, None)
        cv.restore()
        with K.lit(cv, "moon", amount=0.6):
            mx, my, ms = hx + 300, hy + 330, 1.5
            arm = reach("meher", mx, my, ms, "r", (sx + 30, sy + 10), flip=True)
            chars.draw(cv, "meher", x=mx, y=my, s=ms, t=t, flip=True, expr="happy", arms={"r": arm, "l": (10, 20)},
                       look=(0.6, 0.6), head_tilt=-10, lean=-8)


# ---------------------------------------------------------------- NIGHT: kulfi of tongues
GY = None


def _kulfi_base(cv, t, z=1.0, cxy=(960, 560), meher=None, dog=None):
    gy = gali.GROUND_Y_SIDE
    with cam(cv, cxy[0], cxy[1], z, t=t):
        gali.draw_gali_side(cv, t, "night", scroll=800)
        A.draw_rickshaw(cv, 760, gy, s=1.35, t=t)
        with K.lit(cv, "moon", amount=0.75):
            chars.draw(cv, "meher", x=620, y=gy - 150, s=1.8, t=t, legs="sit", turn=0.5,
                       **(meher or {}))
            A.draw_dog(cv, A.DogPose(x=980, y=gy + 6, s=1.6, t=t, mode="sit", flip=True, **(dog or {})))


def _kulfi_share(cv, c):
    t = c.t
    k = K.ease_in_out(c.seg(0.6, 1.8))
    lick = abs(math.sin(t * 7)) if 1.8 < t < 4.2 else 0.0
    _kulfi_base(cv, t, lerp(1.0, 1.1, c.u), (860, 600),
                meher=dict(expr="happy", hold="kulfi", arms={"r": (lerp(40, 75, k), lerp(120, 30, k)), "l": (10, 40)},
                           look=(0.7, 0.3)),
                dog=dict(expr="happy", tongue=lick > 0.3, mouth=0.3 * lick, ear=0.7, look_up=0.3))
    with cam(cv, 860, 600, lerp(1.0, 1.1, c.u), t=t):
        if t > 3.6:
            # the magic arrives: a shimmer around both their ears
            fx.sparkles(cv, t, 760, 520, spread=220, n=16, color="pistachio", size=7, seed=12,
                        a=clamp(c.seg(3.6, 4.4)))


def _nose_lick(cv, c):
    t = c.t
    lick = clamp(c.seg(0.3, 0.6) - c.seg(0.9, 1.2))
    _kulfi_base(cv, t, 2.1, (930, 690),
                meher=dict(expr="happy", look=(0.8, 0.4), arms={"r": (40, 110), "l": (10, 40)}, hold="kulfi"),
                dog=dict(expr="happy" if t < 1.5 else "alert", tongue=lick > 0.2, mouth=0.4 * lick,
                         look_up=0.4 if t > 1.5 else 0.1, ear=0.6 + 0.4 * c.seg(1.4, 1.9), head_tilt=-6))


def _chutney_line(cv, c):
    t = c.t
    m = c.mouth("chutney")
    also = t > c.shot.lines[0].at + 3.6
    _kulfi_base(cv, t, lerp(2.3, 2.5, c.u), (960, 700),
                meher=dict(expr="awe", look=(0.8, 0.4), arms={"r": (40, 110), "l": (10, 40)}, hold="kulfi"),
                dog=dict(expr="guilty" if also else "proud", mouth=m, look_up=0.45, ear=0.95 if not also else 0.35,
                         head_tilt=4 if also else -4, wag=1.4 if not also else 0.4))


def _meher_laughs(cv, c):
    t = c.t
    shake = math.sin(t * 22) * 3
    with cam(cv, 860, 640, 1.5, t=t):
        gy = gali.GROUND_Y_SIDE
        gali.draw_gali_side(cv, t, "night", scroll=800)
        A.draw_rickshaw(cv, 760, gy, s=1.35, t=t)
        with K.lit(cv, "moon", amount=0.75):
            chars.draw(cv, "meher", x=620, y=gy - 150 + shake, s=1.8, t=t, legs="sit", turn=0.5, expr="laugh",
                       arms={"l": (20, 115), "r": (20, 115)}, head_tilt=-8 + 6 * math.sin(t * 5), lean=-4)
            # Chutney wags so hard his whole back half wags
            cv.save()
            cv.translate(980, gy)
            cv.rotate(6 * math.sin(t * 16))
            cv.translate(-980, -gy)
            A.draw_dog(cv, A.DogPose(x=980, y=gy + 6, s=1.6, t=t, mode="stand", flip=True, expr="happy",
                                     tongue=True, wag=2.0, ear=0.9))
            cv.restore()


# ---------------------------------------------------------------- NIGHT: the fading
def _count_jars(cv, c):
    t = c.t
    pts = [(240, 230), (420, 230), (600, 330), (900, 230), (1100, 330)]
    i = min(len(pts) - 1, int(t / 1.0))
    tgt = pts[i]
    arm = reach("meher", MX, MY, MS, "r", tgt, branch=-1)
    with cam(cv, 760, 420, 1.3, t=t):
        _shop_layers(cv, t, _amma(t, 0.65, 0.35, expr="neutral", look=(0.8, 0.3)),
                     lambda cv: A.draw_scale(cv, A.ScalePose(TX, TY, s=TS, t=t, eyes="open", tarnish=0.3)),
                     fullness=0.6, fade=0.15,
                     front=lambda cv: chars.draw(cv, "meher", x=MX, y=MY, s=MS, t=t, expr="worried",
                                                 arms={"r": arm, "l": (10, 30)}, hand={"r": "point"},
                                                 look=(0.8, -0.8), head_tilt=6 * math.sin(t * 3)))


def _hand_lantern(cv, c):
    """Close: Amma's hand passes in front of a lantern, and the lantern shows straight through it."""
    t = c.t
    with cam(cv, 960, 420, 1.5, t=t):
        shop.draw_shop(cv, t, view="counter", fullness=0.6, fade=0.2)
    cv.drawRect(skia.Rect.MakeWH(1920, 1080), fill("#1a0c04", 0.45))
    fx.glow_dot(cv, 960, 520, 420, "gold", 0.55)
    wall.lantern(cv, 960, 120, s=6.5, lit=1.0, t=t, seed=3)
    hx = lerp(1900, 40, K.ease_in_out(c.seg(0.3, 4.2)))
    hy = 520 + 30 * math.sin(t * 2)
    p = skia.Paint(); p.setAlphaf(0.4)
    cv.saveLayer(None, p)
    sleeve = K.limb(hx + 700, hy + 260, hx + 170, hy + 30, 260, 210)
    cv.drawPath(sleeve, K.lin((hx, hy), (hx + 600, hy + 300), ["shawl_light", "shawl"]))
    cv.drawPath(sleeve, stroke("line", 5))
    palm = K.rrect(hx - 60, hy - 90, 250, 210, 90)
    cv.drawPath(palm, fill("#c08a64")); cv.drawPath(palm, stroke("line", 5))
    for i in range(4):
        f = K.limb(hx - 10, hy - 60 + i * 50, hx - 130, hy - 70 + i * 52, 46, 40)
        cv.drawPath(f, fill("#c08a64")); cv.drawPath(f, stroke("line", 4))
    th = K.limb(hx + 60, hy - 80, hx + 10, hy - 160, 50, 42)
    cv.drawPath(th, fill("#c08a64")); cv.drawPath(th, stroke("line", 4))
    cv.restore()
    fx.sparkles(cv, t, hx + 60, hy, spread=180, n=14, color="shawl_light", size=8, seed=5, rise=1.0)


def _where(cv, c):
    t = c.t
    with cam(cv, 560, 470, 1.75, t=t):
        _shop_layers(cv, t, _amma(t, 0.6, 0.4, expr="neutral"),
                     lambda cv: A.draw_scale(cv, A.ScalePose(TX, TY, s=TS, t=t, eyes="open", tarnish=0.3)),
                     fullness=0.6, fade=0.2,
                     front=lambda cv: chars.draw(cv, "meher", x=MX, y=MY, s=MS, t=t, expr="worried",
                                                 mouth=c.mouth("meher"), look=(0.8, -0.6), head_tilt=8, turn=0.6,
                                                 arms={"l": (10, 30), "r": (30, 70)}))


def _sweets_come(cv, c):
    t = c.t
    ax, ay, as_ = SA["counter"]["amma"]
    wave = math.sin(t * 5) * 30
    flick = 0.55 + 0.25 * math.sin(t * 23) * math.sin(t * 7.3) if t > 1.4 else 0.6
    with cam(cv, ax - 80, ay - 300, lerp(1.6, 1.7, c.u), t=t):
        _shop_layers(cv, t, _amma(t, flick, 0.4, expr="happy", mouth=c.mouth("amma"), look=(0.9, 0.3),
                                  arms={"l": (120 + wave, 40)}, hand={"l": "open"}, head_tilt=6),
                     lambda cv: A.draw_scale(cv, A.ScalePose(TX, TY, s=TS, t=t, eyes="half", tarnish=0.3)),
                     fullness=0.6, fade=0.2)


def _meher_notices(cv, c):
    t = c.t
    with cam(cv, 520, 480, lerp(1.8, 1.95, c.u), t=t):
        _shop_layers(cv, t, _amma(t, 0.45, 0.5, expr="happy"),
                     lambda cv: A.draw_scale(cv, A.ScalePose(TX, TY, s=TS, t=t, eyes="half", tarnish=0.35,
                                                             mouth="frown")),
                     fullness=0.55, fade=0.25,
                     front=lambda cv: chars.draw(cv, "meher", x=MX, y=MY, s=MS, t=t, expr="sad",
                                                 look=(0.9, -0.5), head_tilt=4, turn=0.6,
                                                 arms={"l": (10, 30), "r": (10, 30)}))


def _kabir_sulks(cv, c):
    """Day: Kabir sulks on the parapet; when Meher looks over, he turns away."""
    t = c.t
    lx, ly, ls = RA["parapet_lean"]
    with cam(cv, 1300, 640, 1.35, t=t):
        rooftop.draw_rooftop(cv, t, "morning", lantern=0.0)
        with K.lit(cv, "day", amount=0.6):
            mx, my, ms = RA["charpai_meher"]["surface"][0], RA["charpai_meher"]["surface"][1] + 10, \
                RA["charpai_meher"]["s"] * 1.5
            chars.draw(cv, "meher", x=mx, y=my, s=ms, legs="sit", t=t, expr="worried", look=(0.8, 0), turn=0.6)
            away = t > 1.8
            chars.draw(cv, "kabir", x=lx, y=ly, s=ls * 1.45, t=t, flip=not away, expr="sad" if not away else "angry",
                       arms={"l": (20, 110), "r": (20, 110)}, turn=0.6 if not away else 0.1, look=(0.6, 0.3),
                       head_tilt=-6)


def _town_dusk(cv, c):
    town.draw_town(cv, c.t, "night" if c.t > 1.6 else "dusk", lights=0.0, cam_x=lerp(500, 640, c.u))



def _roof_night_arrive(cv, c):
    """Night: Meher back from the shop, toffee twist in hand, onto the moonlit roof."""
    t = c.t
    dx, dy, ds = RA["stair_door"]
    k = K.ease_in_out(c.seg(0.3, 3.2))
    with cam(cv, 960, 560, lerp(1.0, 1.04, c.u), t=t):
        rooftop.draw_rooftop(cv, t, "night", lantern=1.0)
        a = RA["charpai_nani"]
        rooftop.draw_sleeper(cv, a["surface"][0], a["surface"][1], a["s"] * 1.5, t, "nani")
        _monkey(cv, t)
        with K.lit(cv, "moon", amount=0.6):
            chars.draw(cv, "meher", x=lerp(dx, SHX + 220, k), y=lerp(dy, SHY, k), s=lerp(ds * 1.4, SHS, k), t=t,
                       legs="walk" if 0.3 < t < 3.2 else "stand", phase=t * 1.3, expr="happy", hold="toffee",
                       arms={"r": (40, 140)}, look=(0.4, -0.2) if t < 3.0 else (-0.6, -0.9))


def _kabir_peeks(cv, c):
    """Kabir watching from the shop doorway, half hidden: he wants in."""
    t = c.t
    v = SA["wide"]
    dx, dy, ds = v["door"]
    peek = K.ease_out(c.seg(0.4, 1.2)) - K.ease_in(c.seg(3.4, 4.0))
    with cam(cv, 520, 640, 1.9, t=t):
        shop.draw_shop(cv, t, view="wide", fullness=0.75)
        with K.lit(cv, "night", amount=0.7):
            cv.save()
            clip = skia.Path(); clip.addRect(skia.Rect.MakeLTRB(0, 0, 150 + 70 * peek, 1080))
            cv.clipPath(clip, doAntiAlias=True)
            chars.draw(cv, "kabir", x=dx - 60 + 80 * peek, y=dy, s=ds, t=t, expr="sad" if t < 2.5 else "determined",
                       look=(0.9, -0.2), turn=0.7, lean=8 * peek)
            cv.restore()


def _walk_home(cv, c):
    t = c.t
    gali.draw_gali_side(cv, t, "night", scroll=900 + t * 120)
    gy = gali.GROUND_Y_SIDE
    with K.lit(cv, "moon", amount=0.8):
        A.draw_dog(cv, A.DogPose(x=1180, y=gy + 4, s=1.25, t=t, mode="trot", phase=t * 1.3, flip=False,
                                 expr="happy", tongue=True, wag=1.6, ear=0.9))
        chars.draw(cv, "meher", x=880, y=gy, s=1.9, t=t, legs="walk", phase=t * 1.2, expr="happy", turn=0.6,
                   look=(0.7, 0.3), hold="kulfi", arms={"r": (30, 60)})


D_CHUTNEY = ("You gave me your water when you were thirsty too, so I'll guard you forever... "
             "also I ate your slipper last week. Sorry.")

SHOTS = [
    Shot("S05_SH01", _town_day, duration=4.0, music="montage", transition="fade_black", trans_dur=1.0,
         sfx=[bed("day_bed", 3.4), Sfx("heat_cicadas", 0, -16, dur=3.4)]),
    Shot("S05_SH02", _laundry_walk, duration=5.8, sfx=[bed("day_bed", 5.8), Sfx("footsteps_soft", 0.2, -10, dur=4.2)]),
    Shot("S05_SH03", _laundry_drop, duration=4.4, sfx=[bed("day_bed", 4.4), Sfx("iron_steam", 1.9, -8), Sfx("pop", 2.1, -10)]),
    Shot("S05_SH04", _marigolds, duration=6.8, transition="dissolve", trans_dur=0.5,
         sfx=[bed("day_bed", 6.2), Sfx("water_pour", 0.4, -8, dur=5.2), Sfx("sparkle", 5.0, -14)]),
    Shot("S05_SH05", _toddler, duration=7.2, transition="dissolve", trans_dur=0.5,
         sfx=[bed("day_bed", 6.4, -18), Sfx("page_turn", 0.6, -10), Sfx("page_turn", 3.2, -14)]),
    Shot("S05_SH06", _town_dusk, duration=3.4, transition="dissolve", trans_dur=0.8,
         sfx=[bed("night_bed", 3.4), Sfx("train_horn_distant", 0.5, -18)]),
    Shot("S05_SH07", _pay(_bubble_inside_laundry), duration=4.8, transition="dissolve", trans_dur=0.5,
         sfx=[bed("crickets_bed", 4.8, -24), Sfx("bubble_rise", 0.3, -8), Sfx("tola_clonk", 2.6, -4),
              Sfx("jar_chord", 2.7, -6)]),
    Shot("S05_SH08", _hand_down("toffee"), duration=3.6, sfx=[bed("crickets_bed", 3.6, -24), Sfx("sparkle", 0.5, -10)]),
    Shot("S05_SH08b", _roof_night_arrive, duration=3.8, transition="dissolve", trans_dur=0.6,
         sfx=[bed("night_bed", 3.8), Sfx("footsteps_soft", 0.3, -14, dur=3.0)]),
    Shot("S05_SH09", _monkey_specs, duration=4.2, sfx=[bed("night_bed", 3.8), Sfx("monkey_chatter", 0.5, -6)]),
    Shot("S05_SH10", _nani_no_specs, duration=2.6, sfx=[bed("night_bed", 2.6)]),
    Shot("S05_SH11", _brave, duration=6.4, music="brave", music_hits=[1.6, 4.3],
         sfx=[bed("night_bed", 5.6, -18), Sfx("munch", 0.3, -6), Sfx("swallow_gulp", 1.3, -8),
              Sfx("shadow_grow", 1.6, -3)]),
    Shot("S05_SH12", _monkey_flees, duration=3.4,
         sfx=[bed("night_bed", 3.4, -18), Sfx("monkey_chatter", 0.3, -2), Sfx("whoosh", 1.0, -8)]),
    Shot("S05_SH13", _catch, duration=4.0, sfx=[bed("night_bed", 4.0, -18), Sfx("pop", 0.5, -8), Sfx("sparkle", 1.9, -8)]),
    Shot("S05_SH14", _specs_back, duration=5.0, music="montage",
         sfx=[bed("night_bed", 4.2, -16), Sfx("sparkle", 2.3, -16)]),
    Shot("S05_SH15", _kabir_sulks, duration=4.2, transition="dissolve", trans_dur=0.6,
         sfx=[bed("sparrows_dawn", 4.2, -16)]),
    Shot("S05_SH16", _pay(_bubble_inside_flowers, fullness=0.75, alpha=0.72, desat=0.3), duration=4.8,
         transition="dissolve", trans_dur=0.6,
         sfx=[bed("crickets_bed", 4.8, -24), Sfx("bubble_rise", 0.3, -8), Sfx("tola_clonk", 2.6, -8),
              Sfx("jar_chord", 2.7, -12)]),
    Shot("S05_SH16b", _kabir_peeks, duration=4.2, sfx=[bed("crickets_bed", 4.2, -22)]),
    Shot("S05_SH17", _hand_down("kulfi", alpha=0.72, desat=0.3, fullness=0.75), duration=3.6,
         sfx=[bed("crickets_bed", 3.6, -24), Sfx("sparkle", 0.5, -12)]),
    Shot("S05_SH18", _kulfi_share, duration=6.2, music="chutney_tender", transition="dissolve", trans_dur=0.6,
         sfx=[bed("night_bed", 5.4), Sfx("dog_pant", 1.8, -12), Sfx("sparkle", 3.6, -10)]),
    Shot("S05_SH19", _nose_lick, duration=2.6, sfx=[bed("night_bed", 2.6)]),
    Shot("S05_SH20", _chutney_line, lines=[Line("chutney", D_CHUTNEY, at=0.6)], tail=1.0,
         sfx=[bed("night_bed", 10.0, -18)]),
    Shot("S05_SH21", _meher_laughs, duration=5.0, sfx=[bed("night_bed", 4.4), Sfx("kids_laugh", 0.1, -14)]),
    Shot("S05_SH21b", _walk_home, duration=4.4, sfx=[bed("night_bed", 4.4), Sfx("footsteps_soft", 0.2, -12, dur=4.0)]),
    Shot("S05_SH22", _pay(_bubble_inside_toddler, fullness=0.6, alpha=0.55, desat=0.45), duration=4.8,
         music="fading", transition="dissolve", trans_dur=0.6,
         sfx=[bed("crickets_bed", 4.8, -24), Sfx("bubble_rise", 0.3, -10), Sfx("tola_clonk", 2.6, -12),
              Sfx("jar_chord", 2.7, -18)]),
    Shot("S05_SH23", _count_jars, duration=6.0, sfx=[bed("crickets_bed", 5.2, -24)]),
    Shot("S05_SH24", _hand_lantern, duration=5.0, sfx=[bed("crickets_bed", 4.2, -24), Sfx("sparkle", 1.0, -16)]),
    Shot("S05_SH25", _where, lines=[Line("meher", "Amma, where are all the sweets going?", at=0.4)], tail=0.8,
         sfx=[bed("crickets_bed", 4.0, -24)]),
    Shot("S05_SH26", _sweets_come, lines=[Line("amma", "Oh, sweets come, sweets go.", at=0.4)], tail=1.6,
         sfx=[bed("crickets_bed", 4.0, -24), Sfx("shop_flicker", 1.6, -14)]),
    Shot("S05_SH27", _meher_notices, duration=4.4, sfx=[bed("crickets_bed", 3.4, -24)]),
]

SHOTS = finalize(SHOTS, 5)
