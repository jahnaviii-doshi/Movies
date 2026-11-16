"""Scene 7: CLIMAX (target 180 s).

Meghnath defeated; Tara sets the photo upright -> Ishaan waits on the parapet -> Bhaap comes home,
tiny and grey -> the three apologies -> 'the trunk needs three' -> the plan -> 'Nothing.' ->
the roof: the wind steals the third key -> Rehan BOWLS it -> click -> CLACK CLACK CLACK ->
the MONSOON rolls out over Delhi -> silence -> one fat raindrop on the tin roof.
"""
from __future__ import annotations

import math

import skia

from .... import core as K, fx
from ....core import W, H, fill, stroke, clamp, lerp
from ....timeline import Shot, Line, Sfx
from .. import rig as R
from ..rig import draw, draw_bhaap, draw_pigeon, draw_key, draw_cooker_lid, bowling_pose, bowling_hop
from ..sets import roof, workshop, skyline, block, flats, weather_fx as WF
from ..sets import _common as CC
from ._util_c import (bed, fit_beds, ccam, push, roof_bg, night_sky, plane, lying_meghnath, photo_back,
                      torch_glow, paper_plan, head_y, frame_head, renumber)

PX, PY, PS = roof.ANCHORS["parapet_sit"]          # Ishaan's seat on the back parapet
TX, TY, TS = roof.ANCHORS["trunk"]                # the Monsoon Trunk under the open sky
KH = roof.trunk_keyholes(TX, TY, TS)              # [left (Tara), right (Rehan), top/back (Ishaan + Bhaap)]


def wind_streaks(cv, t, amount=1.0, seed=3, rect=(0, 0, W, H)):
    r = K.rng(seed)
    x0, y0, x1, y1 = rect
    for i in range(int(60 * amount)):
        y = r.uniform(y0, y1)
        sp = r.uniform(900, 1700)
        x = x0 + ((t * sp + r.uniform(0, 3000)) % (x1 - x0 + 600)) - 300
        L = r.uniform(60, 180)
        cv.drawLine(x, y, x + L, y + L * 0.06, stroke("#cfd8f0", 2.0, 0.28 * amount))
    for i in range(int(10 * amount)):
        u = (t * r.uniform(0.6, 1.1) + r.uniform(0, 1)) % 1.0
        x, y = lerp(x0 - 50, x1 + 50, u), r.uniform(y0, y1) + math.sin(t * 6 + i) * 30
        cv.save(); cv.translate(x, y); cv.rotate(t * 400 + i * 50)
        cv.drawPath(K.poly([(-8, 0), (0, -5), (9, 0), (0, 5)]), fill("#7a9a5a", 0.8 * amount))
        cv.restore()


# ------------------------------------------------------------------ 1. Meghnath's flat
def sh01(cv, c):
    """Night. He lies awake under the blanket. The photograph is face down."""
    t = c.t
    cam = push(c, (960, 560, 1.15), (900, 560, 1.3))
    flats.draw_meghnath_flat(cv, t, "night", cam=cam)
    with K.camera(cv, *cam):
        with K.lit(cv, "night", amount=0.6):
            lying_meghnath(cv, 700, 612, 1.35, t, expr="sad", blink=0.25, look=(0.3, -0.7), brow_lift=-0.6)
            photo_back(cv, *flats.PHOTO_SPOT, s=0.9, up=0.0)


def sh02(cv, c):
    """Tara tiptoes in, sets the photo upright, tiptoes out."""
    t = c.t
    cam = push(c, (1380, 640, 1.9), (1400, 640, 2.0))
    flats.draw_meghnath_flat(cv, t, "night", cam=cam)
    up = K.ease_in_out(c.seg(3.2, 4.4))
    with K.camera(cv, *cam):
        with K.lit(cv, "night", amount=0.55):
            lying_meghnath(cv, 700, 612, 1.35, t, expr="sad", blink=0.3, look=(0.6, -0.4), brow_lift=-0.6)
            photo_back(cv, *flats.PHOTO_SPOT, s=0.9, up=up, t=t)
            k_in = K.ease_in_out(c.seg(0.0, 2.6))
            k_out = K.ease_in_out(c.seg(5.6, 8.5))
            x = lerp(1950, 1660, k_in) + k_out * 360
            walking = (0.02 < k_in < 0.98) or (0.02 < k_out < 0.98)
            reach = c.seg(2.6, 3.2) * (1 - c.seg(4.6, 5.2))
            draw(cv, "tara", x=x, y=1005, s=1.7, t=t, flip=not (k_out > 0.02), turn=0.5,
                 legs="tiptoe" if not walking else "walk", phase=x / 60, expr="sad" if up < 1 else "shy",
                 look=(-0.7, 0.3) if k_out < 0.02 else (0.6, 0), lean=4 + 8 * reach,
                 arms={"r": (lerp(10, 92, reach), lerp(20, 10, reach))} if k_out < 0.02 else {})


# ------------------------------------------------------------------ 2. Ishaan waits
def sh03(cv, c):
    """Ishaan alone on the parapet, legs swinging, a pressure-cooker lid beside him. He waits."""
    t = c.t
    hy = head_y("ishaan", PY, PS, sit=True)
    cam = push(c, ccam(PX, hy + 60, 2.6), ccam(PX, hy + 40, 2.9))
    roof_bg(cv, c, "night", cam)
    with K.camera(cv, *cam):
        with K.lit(cv, "night"):
            draw_cooker_lid(cv, PX + 70 * PS, PY - 4, 0.5 * PS)
            draw(cv, "ishaan", x=PX, y=PY, s=PS, t=t, legs="sit", turn=0.1, expr="sad", look=(0.1, -1.0),
                 arms={"l": (18, 30), "r": (18, 30)}, extra={"swing": 1.0})


def sh04(cv, c):
    """Stars. A plane blinks across. Nothing else comes."""
    t = c.t
    night_sky(cv, t)
    plane(cv, t, 300, 260, 1700, 200, 0.5, 7.5, s=1.2)
    skyline.draw_skyline(cv, t, "night", cam_x=200, heat=0.0, pigeons=False) if False else None
    # the parapet edge and Ishaan small, from behind his shoulder
    cv.drawRect(skia.Rect.MakeLTRB(0, 880, W, H), fill("#1e2440"))
    cv.drawRect(skia.Rect.MakeLTRB(0, 870, W, 890), fill("#2c3456"))
    with K.lit(cv, "night"):
        draw(cv, "ishaan", x=1500, y=1180, s=2.2, t=t, turn=0.9, flip=True, expr="sad", look=(-0.6, -1.0))


def sh05(cv, c):
    """Captain the pigeon flutters down beside him, and waits too."""
    t = c.t
    hy = head_y("ishaan", PY, PS, sit=True)
    cam = push(c, ccam(PX + 30, hy + 60, 2.6), ccam(PX + 40, hy + 50, 2.7))
    roof_bg(cv, c, "night", cam)
    land = K.ease_out(c.seg(0.4, 2.2))
    with K.camera(cv, *cam):
        with K.lit(cv, "night"):
            draw_cooker_lid(cv, PX + 70 * PS, PY - 4, 0.5 * PS)
            draw(cv, "ishaan", x=PX, y=PY, s=PS, t=t, legs="sit", turn=0.1, expr="sad",
                 look=(-0.6, 0.2) if t > 2.6 else (-0.5, -0.6), arms={"l": (18, 30), "r": (18, 30)},
                 extra={"swing": 0.6})
            bx = lerp(PX - 260, PX - 80 * PS, land)
            by = lerp(PY - 260, PY - 2, land)
            mode = "flap" if land < 0.98 else ("one_leg" if t > 4.0 else "stand")
            draw_pigeon(cv, bx, by, 0.9 * PS, t, flip=False, mode=mode, head_bob=0.2)


def sh06(cv, c):
    """Far off, something small and grey drifts toward them."""
    t = c.t
    cam = push(c, (1150, 360, 1.6), (1150, 380, 1.9))
    roof_bg(cv, c, "night", cam)
    with K.camera(cv, *cam):
        with K.lit(cv, "night"):
            draw(cv, "ishaan", x=PX, y=PY, s=PS, t=t, legs="sit", turn=0.1, expr="awe" if t > 3.5 else "sad",
                 look=(0.2, -0.9), arms={"l": (18, 30), "r": (18, 30)}, extra={"swing": 0.3 * (1 - c.seg(3, 4))})
            draw_pigeon(cv, PX - 80 * PS, PY - 2, 0.9 * PS, t, mode="stand", head_bob=0.1)
        k = K.ease_in_out(c.seg(0.0, 8.0))
        bx, by = lerp(1550, 1240, k), lerp(140, 380, k) + math.sin(t * 1.6) * 10
        draw_bhaap(cv, bx, by, lerp(0.12, 0.38, k), t, mood="tired", grey=1.0, rain=0.2, glow=0.2)


def sh07(cv, c):
    """Close on Ishaan: 'Bhaap.'"""
    t = c.t
    hy = head_y("ishaan", PY, PS, sit=True)
    cam = push(c, frame_head(PX, hy, 4.6, 0.42), frame_head(PX, hy, 5.0, 0.42))
    roof_bg(cv, c, "night", cam)
    with K.camera(cv, *cam):
        with K.lit(cv, "night"):
            draw(cv, "ishaan", x=PX, y=PY, s=PS, t=t, legs="sit", turn=0.15, expr="awe" if t < 2.2 else "happy",
                 mouth=c.mouth("ishaan"), look=(0.4, -0.6), brow=0.4, arms={"l": (40, 80), "r": (40, 80)})


def sh08(cv, c):
    """The tiny grey cloud lands in his hands, shivering, drizzling. He hugs it."""
    t = c.t
    hy = head_y("ishaan", PY, PS, sit=True)
    cam = frame_head(PX, hy, 3.6, 0.35)
    roof_bg(cv, c, "night", cam)
    land = K.ease_out(c.seg(0.0, 1.8))
    hug = K.ease_in_out(c.seg(3.2, 4.4))
    with K.camera(cv, *cam):
        hx, hyy = PX, PY - 92 * PS
        with K.lit(cv, "night"):
            draw(cv, "ishaan", x=PX, y=PY, s=PS, t=t, legs="sit", turn=0.1, expr="sad" if t < 3.2 else "happy",
                 look=(0.0, 0.8), head_tilt=8 * hug,
                 arms={"l": (lerp(30, 45, hug), lerp(100, 125, hug)), "r": (lerp(30, 45, hug), lerp(100, 125, hug))})
        shiver = math.sin(t * 40) * 1.5 * (1 - hug * 0.6)
        bx = lerp(PX + 140, hx, land) + shiver
        by = lerp(hyy - 120, hyy - 6, land)
        draw_bhaap(cv, bx, by, 0.32 * PS * 1.4, t, mood="tired", grey=1.0, rain=0.6 * (1 - hug * 0.5),
                   glow=0.15, squash=0.3 * hug)


def sh09(cv, c):
    """Slowly he whitens and fluffs... Tzik: one small, happy spark."""
    t = c.t
    hy = head_y("ishaan", PY, PS, sit=True)
    cam = push(c, frame_head(PX, hy, 3.6, 0.35), frame_head(PX, hy, 3.9, 0.36))
    roof_bg(cv, c, "night", cam)
    k = K.ease_in_out(c.seg(0.4, 5.0))
    with K.camera(cv, *cam):
        with K.lit(cv, "night"):
            draw(cv, "ishaan", x=PX, y=PY, s=PS, t=t, legs="sit", turn=0.1,
                 expr="happy" if t < 5.6 else "grin", look=(0.0, 0.8), head_tilt=6,
                 arms={"l": (40, 118), "r": (40, 118)})
        spark = clamp(1 - abs(t - 5.8) / 0.25) if t > 5.5 else 0.0
        draw_bhaap(cv, PX, PY - 98 * PS - 6 * k, lerp(0.45, 0.62, k) * PS, t,
                   mood="happy" if t > 5.5 else "sleepy", grey=1 - k, mouth=0.4 if t > 5.6 else 0.0,
                   glow=k, spark=spark)


def sh10(cv, c):
    """Wider: Tara and Rehan have been standing there a while. The three apologies."""
    t = c.t
    cam = push(c, (1170, 560, 2.0), (1170, 570, 2.1))
    roof_bg(cv, c, "night", cam)
    with K.camera(cv, *cam):
        with K.lit(cv, "night"):
            draw(cv, "ishaan", x=PX, y=PY, s=PS, t=t, legs="sit", turn=0.1, expr="happy",
                 mouth=c.mouth("ishaan"), look=(-0.6, 0.4) if t < 4 else (0.6, 0.4),
                 arms={"l": (40, 118), "r": (40, 118)}, extra={"swing": 0.4})
            draw(cv, "rehan", x=PX - 230, y=PY + 110, s=1.0, t=t, turn=0.5, expr="sad",
                 mouth=c.mouth("rehan"), look=(0.7, -0.3), hand={"r": "ball"}, head_tilt=-6)
            draw(cv, "tara", x=PX + 250, y=PY + 110, s=1.0, t=t, flip=True, turn=0.5, expr="sad",
                 mouth=c.mouth("tara"), look=(0.7, -0.3), hold="notebook", head_tilt=6)
        draw_bhaap(cv, PX, PY - 98 * PS - 6, 0.6 * PS, t, mood="happy" if not c.speaking("ishaan") else "excited",
                   mouth=0.3, spark=0.4 if c.speaking("ishaan") else 0.0)


def sh11(cv, c):
    """They look at each other. Three of them."""
    t = c.t
    cam = push(c, (1170, 560, 2.1), (1170, 545, 2.35))
    roof_bg(cv, c, "night", cam)
    with K.camera(cv, *cam):
        with K.lit(cv, "night"):
            a = c.seg(0.4, 1.2)
            draw(cv, "ishaan", x=PX, y=PY, s=PS, t=t, legs="sit", turn=0.1, expr="happy",
                 look=(-0.7 if t < 2 else 0.7, 0.4), arms={"l": (40, 118), "r": (40, 118)})
            draw(cv, "rehan", x=PX - 230, y=PY + 110, s=1.0, t=t, turn=0.5, expr="determined" if t > 2.2 else "sad",
                 look=(0.8, -0.1) if t < 2.4 else (0.9, 0), hand={"r": "ball"})
            draw(cv, "tara", x=PX + 250, y=PY + 110, s=1.0, t=t, flip=True, turn=0.5,
                 expr="determined" if t > 2.2 else "sad", look=(0.8, -0.1), hold="notebook")
        draw_bhaap(cv, PX, PY - 98 * PS - 6, 0.6 * PS, t, mood="excited" if t > 2.8 else "happy",
                   spark=0.6 if t > 2.8 else 0.0)


# ------------------------------------------------------------------ 3. the workshop: the plan
def _ws_trunk(cv, c, cam, tara_kw, rehan_kw, ishaan_kw, bhaap=None, torches=True):
    t = c.t
    tor = [(700, 860, -40), (1220, 860, -140)] if torches else None
    workshop.draw_workshop(cv, t, "trunk", "night", cloth=0.0, keys=(0, 0, 0), torches=tor, cam=cam)
    with K.camera(cv, *cam):
        if torches:
            for (x, y, a) in tor:
                torch_glow(cv, x, y, a, length=360, spread=22, a=0.22)
        with K.lit(cv, "workshop"):
            with K.lit(cv, "dim", amount=0.3):
                draw(cv, "ishaan", t=t, mouth=c.mouth("ishaan"), **ishaan_kw)
                draw(cv, "rehan", t=t, mouth=c.mouth("rehan"), **rehan_kw)
                draw(cv, "tara", t=t, mouth=c.mouth("tara"), **tara_kw)
        if bhaap:
            draw_bhaap(cv, t=t, **bhaap)


def sh12(cv, c):
    """Three keys from the hook. Tara tears out a page."""
    t = c.t
    cam = push(c, (960, 760, 1.7), (960, 780, 1.85))
    tear = c.seg(2.4, 3.0)
    _ws_trunk(cv, c, cam,
              dict(x=700, y=985, s=1.25, turn=0.6, expr="determined", hold="notebook",
                   arms={"r": (40, 110), "l": (lerp(30, 70, tear), lerp(100, 40, tear))}, look=(0.2, 0.6)),
              dict(x=1230, y=985, s=1.28, flip=True, turn=0.6, expr="determined", hold="key",
                   arms={"r": (40, 90)}, look=(-0.7, 0.2)),
              dict(x=960, y=920, s=1.0, turn=0.2, expr="happy", hold="key", arms={"r": (30, 100)}, look=(-0.4, 0)),
              bhaap=dict(x=1020, y=660, s=0.65, mood="happy"))


def sh13(cv, c):
    """Insert: the plan, drawn in pencil."""
    t = c.t
    cv.drawRect(skia.Rect.MakeWH(W, H), K.lin((0, 0), (0, H), ["#1a2638", "#0e1622"]))
    fx.light_pool(cv, 960, 560, 900, 560, "#ffe6a8", 0.25)
    paper_plan(cv, t, K.ease_in_out(c.seg(0.4, 6.2)), x=960, y=560, s=1.0 + 0.03 * c.u)


def sh14(cv, c):
    """'We don't ask for anything...'  'Nothing.'  'Nothing.'  Bhaap sparks."""
    t = c.t
    cam = push(c, (960, 760, 1.85), (960, 770, 2.0))
    _ws_trunk(cv, c, cam,
              dict(x=700, y=985, s=1.25, turn=0.6, expr="determined", hold="notebook",
                   arms={"r": (40, 110), "l": (60, 50)} if c.speaking("tara") else {"r": (40, 110)},
                   look=(0.6, -0.1)),
              dict(x=1230, y=985, s=1.28, flip=True, turn=0.6, expr="determined", hold="key",
                   arms={"r": (40, 90)}, look=(-0.7, -0.1)),
              dict(x=960, y=920, s=1.0, turn=0.2, expr="determined" if t < 8 else "happy", hold="key",
                   arms={"r": (30, 100)}, look=(0, -0.3)),
              bhaap=dict(x=1020, y=660, s=0.65, mood="excited" if c.seg(9.2, 9.3) > 0 else "happy",
                         spark=clamp((t - 9.2) / 0.3) * (1 - c.seg(10.5, 11.5)), mouth=0.3))


# ------------------------------------------------------------------ 4. the roof: three keys
def _trunk_people(cv, c, keys=(0.5, 0.5, 0.0), lid=0.0, glow=0.0, rehan=None, poses=None, bhaap_push=0.0):
    """Draw Ishaan (behind the trunk), the trunk, then Tara (left) and Rehan (right) in world coords."""
    t = c.t
    poses = poses or {}
    with K.lit(cv, "night"):
        draw(cv, "ishaan", x=TX + 10, y=TY - 95, s=1.15, t=t, turn=0.1, mouth=c.mouth("ishaan"),
             **poses.get("ishaan", dict(expr="determined", arms={"l": (40, 80), "r": (30, 80)}, look=(0, 0.6))))
    roof.draw_monsoon_trunk(cv, TX, TY, TS, t, lid=lid, keys=keys, glow=glow, weather="night")
    bx, by = KH[2]
    draw_bhaap(cv, bx + 40 - 30 * bhaap_push, by - 46 + 10 * bhaap_push, 0.6, t,
               mood="excited" if bhaap_push > 0.1 else "happy", squash=0.6 * bhaap_push, mouth=0.3)
    with K.lit(cv, "night"):
        draw(cv, "tara", x=KH[0][0] - 150, y=TY + 50, s=1.45, t=t, turn=0.6, mouth=c.mouth("tara"),
             **poses.get("tara", dict(expr="determined", arms={"r": (88, 10)}, look=(0.6, 0.2))))
        if rehan is not False:
            kw = dict(x=KH[1][0] + 170, y=TY + 50, s=1.45, flip=True, turn=0.6,
                      expr="determined", arms={"r": (88, 10)}, look=(0.6, 0.2))
            kw.update(rehan or {})
            draw(cv, "rehan", t=t, mouth=c.mouth("rehan"), **kw)


def sh15(cv, c):
    """They drag the trunk out under the open sky."""
    t = c.t
    cam = push(c, (1000, 560, 1.0), (1080, 620, 1.2))
    roof_bg(cv, c, "night", cam)
    k = K.ease_in_out(c.seg(0.4, 6.0))
    x = lerp(1560, TX, k)
    with K.camera(cv, *cam):
        roof.draw_monsoon_trunk(cv, x, TY, TS, t, weather="night")
        with K.lit(cv, "night"):
            for who, dx, sc in (("tara", -330, 1.45), ("rehan", -190, 1.45)):
                draw(cv, who, x=x + dx, y=TY + 50, s=sc, t=t, flip=True, turn=0.6, legs="walk",
                     phase=t * 0.8 if 0.02 < k < 0.98 else 0.0, lean=-16 if k < 0.98 else 0, expr="wince",
                     arms={"r": (60, 10), "l": (55, 15)}, look=(0.6, 0.2))
            draw(cv, "ishaan", x=x + 300, y=TY + 40, s=1.2, t=t, flip=True, turn=0.5, legs="walk",
                 phase=t * 0.8 if 0.02 < k < 0.98 else 0.0, lean=14 if k < 0.98 else 0, expr="determined",
                 arms={"r": (80, 10), "l": (75, 10)})
        draw_bhaap(cv, x + 120, TY - 380, 0.6, t, mood="excited", spark=0.3)


def sh16(cv, c):
    """Positions. Then a gust tears the third key from Rehan's fingers and it skitters toward the edge."""
    t = c.t
    gust = c.seg(3.0, 3.6)
    cam = push(c, (TX, 700, 1.45), (TX + 100, 730, 1.35))
    roof_bg(cv, c, "night", cam)
    with K.camera(cv, *cam):
        wind_streaks(cv, t, 0.3 + 0.7 * gust)
        _trunk_people(cv, c, keys=(0.5, 0.5, 0.0),
                      rehan=dict(lean=-12 * gust, expr="surprised" if t > 3.1 else "determined",
                                 arms={"r": (lerp(88, 120, gust), 10)}, hand={"r": "open"}))
        if t < 3.1:
            draw_key(cv, KH[1][0] + 100, KH[1][1] + 30, 0.5, rot=180)
        else:
            k = K.ease_out(c.seg(3.1, 5.4))
            kx = lerp(KH[1][0] + 100, 1880, k)
            ky = lerp(KH[1][1] + 30, 1010, K.ease_in(c.seg(3.1, 3.7))) - abs(math.sin(t * 14)) * 10 * (1 - k)
            draw_key(cv, kx, ky, 0.5, rot=t * 900 * (1 - k) + 180)
        if t > 3.0:
            draw_bhaap(cv, 0, 0, 0, t) if False else None


def sh17(cv, c):
    """Rehan dives. Gets it, right at the edge."""
    t = c.t
    cam = ccam(1600, 820, 2.2)
    roof_bg(cv, c, "night", cam)
    dive = K.ease_out(c.seg(0.2, 1.1))
    with K.camera(cv, *cam):
        wind_streaks(cv, t, 0.8)
        kx = lerp(1840, 1872, c.seg(0, 1.1))
        if t < 1.1:
            draw_key(cv, kx, 1012, 0.5, rot=200 + t * 200)
        with K.lit(cv, "night"):
            draw(cv, "rehan", x=lerp(1380, 1680, dive), y=1030, s=1.8, t=t, turn=0.7,
                 lean=lerp(10, 62, dive) - 40 * c.seg(2.0, 3.0), legs="walk", phase=0.3,
                 expr="determined" if t < 1.6 else "grin", arms={"r": (lerp(80, 130, dive), 10), "l": (40, 20)},
                 hold="key" if t > 1.1 else None, look=(0.8, 0.6))


def sh18(cv, c):
    """The wind rises. 'Throw it!' 'It's a key, not a ball!' 'Then bowl it!'"""
    t = c.t
    cam = push(c, (TX - 80, 690, 1.35), (TX - 40, 680, 1.45))
    roof_bg(cv, c, "night", cam)
    with K.camera(cv, *cam):
        wind_streaks(cv, t, 0.9)
        _trunk_people(cv, c, keys=(0.5, 0.5, 0.0),
                      poses={"tara": dict(expr="determined", arms={"l": (70, 20), "r": (88, 10)} if c.speaking("tara")
                                          else {"r": (88, 10)}, hand={"l": "point"}, look=(0.9, 0.3), lean=-6)},
                      rehan=dict(x=KH[1][0] + 520, y=TY + 120, s=1.6, lean=-14, hold="key",
                                 expr="angry" if c.speaking("rehan") else "worried",
                                 arms={"r": (60, 60), "l": (40, 40)} if c.speaking("rehan") else {"r": (30, 60)},
                                 look=(0.7, 0.0)))


def sh19(cv, c):
    """Rehan looks down the length of the roof. The keyhole: small, far away."""
    t = c.t
    cam = push(c, (KH[1][0], KH[1][1] + 40, 1.5), (KH[1][0], KH[1][1] + 20, 3.2), ease=K.ease_in)
    roof_bg(cv, c, "night", cam)
    with K.camera(cv, *cam):
        wind_streaks(cv, t, 0.9)
        roof.draw_monsoon_trunk(cv, TX, TY, TS, t, keys=(0.5, 0.5, 0.0), weather="night")
        fx.glow_dot(cv, *KH[1], 30, "#bfe3ff", 0.4 + 0.3 * math.sin(t * 5))


def sh20(cv, c):
    """The run-up: past the tanks, under the antennas, the wind in his face..."""
    t = c.t
    u = clamp(t / 5.4 * 0.80)
    x = lerp(140, 640, K.ease_in(clamp(u / 0.7)))
    cam = push(c, (560, 760, 1.45), (760, 720, 1.25))
    roof_bg(cv, c, "night", cam)
    with K.camera(cv, *cam):
        wind_streaks(cv, t, 1.0)
        roof.draw_monsoon_trunk(cv, TX, TY, TS, t, keys=(0.5, 0.5, 0.0), weather="night")
        pose = bowling_pose(u)
        pose.pop("hand", None)
        with K.lit(cv, "night"):
            draw(cv, "rehan", x=x, y=1010 + bowling_hop(u) * 1.85, s=1.85, t=t, hold="key" if u < 0.79 else None,
                 hand={"l": "point"} if 0.55 < u < 0.7 else {}, **pose)


def sh21(cv, c):
    """SLOW MOTION: the key spins end over end across the roof, through the wind..."""
    t = c.t
    k = K.ease_in_out(c.seg(0.0, 6.2))
    sx, sy = 700, 560
    ex, ey = KH[1]
    kx = lerp(sx, ex, k)
    ky = lerp(sy, ey, k) - math.sin(k * math.pi) * 170
    cam = ccam(lerp(860, ex - 120, k), lerp(600, ey - 40, k), lerp(1.7, 2.6, k))
    roof_bg(cv, c, "night", cam)
    with K.camera(cv, *cam):
        r = K.rng(4)
        for i in range(40):          # wind, slowed to a crawl
            y = r.uniform(300, 900)
            x = (r.uniform(0, 2400) + t * 60) % 2400 - 200
            cv.drawLine(x, y, x + 140, y + 6, stroke("#cfd8f0", 2.0, 0.22))
        roof.draw_monsoon_trunk(cv, TX, TY, TS, t, keys=(0.5, 0.5, 0.45 * c.seg(6.0, 6.25)), weather="night")
        if t < 6.0:
            for g in range(5):        # motion ghosts
                kk = max(0.0, k - g * 0.012)
                gx = lerp(sx, ex, kk)
                gy = lerp(sy, ey, kk) - math.sin(kk * math.pi) * 170
                draw_key(cv, gx, gy, 0.55, rot=kk * 1440, glow=0.6 if g == 0 else 0.0)
        fx.glow_dot(cv, ex, ey, 40, "#bfe3ff", 0.5 + 0.5 * c.seg(5.8, 6.2))
    if 6.0 < t < 6.5:
        fx.flash(cv, "#e8f0ff", 0.35 * (1 - (t - 6.0) / 0.5))


def sh22(cv, c):
    """CLICK. Close on the keyhole."""
    t = c.t
    cam = ccam(KH[1][0], KH[1][1] + 10, 5.0)
    roof_bg(cv, c, "night", cam)
    with K.camera(cv, *cam):
        roof.draw_monsoon_trunk(cv, TX, TY, TS, t, keys=(0.5, 0.5, 0.5), weather="night")
        fx.chime_rings(cv, KH[1][0], KH[1][1], 0.15, t, color="#bfe3ff", max_r=80)
        fx.sparkles(cv, t, KH[1][0], KH[1][1], spread=40, n=8, color="#ffffff", size=5, seed=8,
                    a=clamp(1 - t / 2.0))


def sh23(cv, c):
    """'Now. All together.'  CLACK. CLACK. CLACK. Bhaap pushes with his whole fluffy body."""
    t = c.t
    cam = push(c, (TX, 680, 1.55), (TX, 650, 1.7))
    roof_bg(cv, c, "night", cam)
    k1 = 0.5 + 0.5 * K.ease_out(c.seg(3.0, 3.5))
    k2 = 0.5 + 0.5 * K.ease_out(c.seg(3.6, 4.1))
    k3 = 0.5 + 0.5 * K.ease_out(c.seg(4.2, 5.2))
    rehan_in = K.ease_out(c.seg(0.0, 1.6))
    with K.camera(cv, *cam):
        wind_streaks(cv, t, 0.6 * (1 - c.seg(4.2, 5.4)))
        _trunk_people(cv, c, keys=(k1, k3, k2), bhaap_push=c.seg(3.6, 4.2) * (1 - c.seg(4.6, 5.4)),
                      poses={"tara": dict(expr="determined", arms={"r": (88 + 30 * (k1 - 0.5), 10)},
                                          look=(0.7, -0.1) if c.speaking("tara") else (0.6, 0.3)),
                             "ishaan": dict(expr="determined" if t < 4 else "grin",
                                            arms={"l": (40, 80), "r": (30 + 40 * (k2 - 0.5), 80)}, look=(0, 0.7))},
                      rehan=dict(x=lerp(KH[1][0] + 520, KH[1][0] + 170, rehan_in), legs="walk" if rehan_in < 0.98 else "stand",
                                 phase=t * 2, arms={"r": (88 + 40 * (k3 - 0.5), 10)}, expr="determined"))


def sh24(cv, c):
    """The lid lifts. Light spills. A slate-blue cloud wells up..."""
    t = c.t
    lid = K.ease_in_out(c.seg(0.5, 3.2))
    cam = push(c, (TX, 640, 1.5), (TX, 560, 1.2))
    roof_bg(cv, c, "night", cam)
    with K.camera(cv, *cam):
        _trunk_people(cv, c, keys=(1, 1, 1), lid=lid, glow=lid,
                      poses={"tara": dict(expr="awe", arms={"r": (40, 20)}, look=(0.4, -0.8), lean=-6),
                             "ishaan": dict(expr="awe", arms={"l": (20, 20), "r": (20, 20)}, look=(0, -1))},
                      rehan=dict(expr="awe", arms={"r": (30, 20)}, look=(0.4, -0.8), lean=-6))
        # the monsoon welling out of the trunk and climbing
        well = K.ease_in(c.seg(1.8, 6.5))
        if well > 0:
            CC.cloud_bank(cv, t * 2, TX + 900 * well, TY - 300 + 40 * (1 - well), ("#3c4c6e", "#5a6c90", "#28324c"),
                          top_y=TY - 300 - 900 * well, seed=5, puff=120, drift=1.0)


def sh25(cv, c):
    """The monsoon rolls over the whole skyline of Delhi in one great sweep. Lightning stitches its edges."""
    t = c.t
    m = K.ease_in_out(c.seg(0.0, 9.0))
    skyline.draw_skyline(cv, t, "night", cam_x=lerp(80, 420, c.u), monsoon=m, heat=0.0)
    if 6.4 < t < 6.8:
        WF.lightning_flash(cv, 0.4 * (1 - (t - 6.4) / 0.4))


def sh26(cv, c):
    """Over Block C: the cloud mountain rolls in, the haze shivers and breaks. Then stillness."""
    t = c.t
    block.draw_block(cv, t, "night", fans=0.0, wind=0.3 * (1 - c.seg(3.0, 6.0)), view="wide")
    front = lerp(-300, W + 900, K.ease_in_out(c.seg(0.0, 5.5)))
    cv.save(); cv.clipRect(skia.Rect.MakeLTRB(-10, -10, front, 520))
    cv.drawRect(skia.Rect.MakeLTRB(-10, -10, W + 10, 520), K.lin((0, 0), (0, 520), ["#1c2440", "#2e3a5c"]))
    cv.restore()
    CC.cloud_bank(cv, t * 2, front, 520, ("#3c4c6e", "#5a6c90", "#28324c"), top_y=-200, seed=11, puff=140,
                  drift=0.8)
    if 3.0 < t < 3.3:
        WF.lightning(cv, t, [(front - 200, 80), (front - 260, 260), (front - 190, 380), (front - 240, 520)], a=1.0,
                     seed=3)
        WF.lightning_flash(cv, 0.3)


def sh27(cv, c):
    """Silence. On the tin roof of the stair hut, one fat raindrop. Tunk."""
    t = c.t
    x0, y0, x1, y1 = roof.ANCHORS["tin_roof"]
    cam = push(c, ccam((x0 + x1) / 2, (y0 + y1) / 2 + 10, 3.6), ccam((x0 + x1) / 2, (y0 + y1) / 2 + 10, 3.9))
    roof_bg(cv, c, "monsoon_night", cam, tin_drops=[2.4], rain=0.0, puddles=False)


def sh28(cv, c):
    """Another. Tunk. Tunk-tunk."""
    t = c.t
    x0, y0, x1, y1 = roof.ANCHORS["tin_roof"]
    cam = push(c, ccam((x0 + x1) / 2, (y0 + y1) / 2, 3.2), ccam((x0 + x1) / 2, (y0 + y1) / 2 - 20, 2.0))
    roof_bg(cv, c, "monsoon_night", cam, tin_drops=[0.6, 2.0, 2.5, 3.1, 3.4, 3.8, 4.1, 4.3, 4.6, 4.8, 5.0],
            rain=0.15 * c.seg(4.0, 6.0), puddles=False)


# ------------------------------------------------------------------ shots
SHOTS = renumber(fit_beds([
    Shot("S07_SH01", sh01, duration=7.0, music="photo_alone", transition="fade_black", trans_dur=1.2,
         sfx=[bed("night_bed_delhi", -22)]),
    Shot("S07_SH02", sh02, duration=9.0, sfx=[bed("night_bed_delhi", -22), Sfx("footsteps_slipper", 0.4, -22),
                                              Sfx("footsteps_slipper", 5.8, -22)]),
    Shot("S07_SH03", sh03, duration=9.0, music="waiting", transition="dissolve", trans_dur=1.0,
         sfx=[bed("night_bed_delhi", -16)]),
    Shot("S07_SH04", sh04, duration=7.5, sfx=[bed("night_bed_delhi", -18), Sfx("plane_distant", 0.4, -16)]),
    Shot("S07_SH05", sh05, duration=6.5, sfx=[bed("night_bed_delhi", -18), Sfx("pigeon_flap", 0.4, -10),
                                              Sfx("pigeon_coo", 3.4, -16)]),
    Shot("S07_SH06", sh06, duration=8.5, music="bhaap_returns", sfx=[bed("night_bed_delhi", -18)]),
    Shot("S07_SH07", sh07, lines=[Line("ishaan", "Bhaap.", at=1.4)], tail=1.8, sfx=[bed("night_bed_delhi", -20)]),
    Shot("S07_SH08", sh08, duration=6.0, sfx=[bed("night_bed_delhi", -20), Sfx("bhaap_drizzle", 1.0, -10),
                                              Sfx("bhaap_coo", 3.4, -12)]),
    Shot("S07_SH09", sh09, duration=7.0, sfx=[bed("night_bed_delhi", -20), Sfx("cloud_puff", 2.5, -14),
                                              Sfx("bhaap_sneeze_spark", 5.75, -6), Sfx("bhaap_giggle", 6.2, -12)]),
    Shot("S07_SH10", sh10,
         lines=[Line("rehan", "I'm sorry. About the trunk.", at=0.8),
                Line("tara", "I'm sorry about my plan.", at=3.4),
                Line("ishaan", "Bhaap says the trunk needs three.", at=6.0)], tail=1.0,
         sfx=[bed("night_bed_delhi", -20)]),
    Shot("S07_SH11", sh11, duration=4.5, sfx=[bed("night_bed_delhi", -20), Sfx("spark_tzik", 2.9, -10)]),
    Shot("S07_SH12", sh12, duration=5.0, music="three_keys", transition="dissolve", trans_dur=0.6,
         sfx=[bed("workshop_ambience", -16), Sfx("key_turn_clack", 0.6, -18), Sfx("page_turn", 2.5, -8)]),
    Shot("S07_SH13", sh13, duration=7.0, sfx=[bed("workshop_ambience", -18)]),
    Shot("S07_SH14", sh14,
         lines=[Line("tara", "We don't ask for anything. Not ice cream, not thank you. Nothing.", at=0.6),
                Line("rehan", "Nothing.", at=6.6), Line("ishaan", "Nothing.", at=8.0)], tail=2.2,
         sfx=[bed("workshop_ambience", -18), Sfx("spark_tzik", 9.25, -8)]),
    Shot("S07_SH15", sh15, duration=7.0, transition="dissolve", trans_dur=0.6,
         sfx=[bed("wind_gusts", -18, build=0.2), Sfx("tin_lid_creak", 0.6, -14)]),
    Shot("S07_SH16", sh16, duration=5.6, sfx=[bed("wind_gusts", -14, build=0.5), Sfx("whoosh", 3.0, -8),
                                              Sfx("key_skitter", 3.15, -6)]),
    Shot("S07_SH17", sh17, duration=3.6, sfx=[bed("wind_gusts", -12, build=0.6), Sfx("mud_slide", 0.4, -16)]),
    Shot("S07_SH18", sh18,
         lines=[Line("tara", "You can't walk it over. Throw it!", at=0.5),
                Line("rehan", "It's a key, not a ball!", at=2.9),
                Line("tara", "Then bowl it!", at=4.6)], tail=1.0,
         sfx=[bed("wind_gusts", -12, build=0.8)]),
    Shot("S07_SH19", sh19, duration=3.6, sfx=[bed("wind_gusts", -14, build=0.8)]),
    Shot("S07_SH20", sh20, duration=5.4, sfx=[bed("wind_gusts", -10, build=1.0), Sfx("footsteps_soft", 0.2, -12)]),
    Shot("S07_SH21", sh21, duration=7.0, music="bowl_slowmo", music_hits=[6.0],
         sfx=[bed("wind_gusts", -24, build=0.4), Sfx("slowmo_whoosh", 0.1, -4), Sfx("key_click", 6.0, -2)]),
    Shot("S07_SH22", sh22, duration=2.4, sfx=[Sfx("key_click", 0.1, -10)]),
    Shot("S07_SH23", sh23, lines=[Line("tara", "Now. All together.", at=1.2)], duration=6.4, music="three_keys",
         sfx=[bed("wind_gusts", -18, build=0.3), Sfx("key_turn_clack", 3.0, -3), Sfx("key_turn_clack", 3.6, -3),
              Sfx("key_turn_clack", 5.1, -2), Sfx("bhaap_giggle", 4.4, -12)]),
    Shot("S07_SH24", sh24, duration=7.0, music="monsoon_full",
         sfx=[Sfx("trunk_lid_rise", 0.4, -4), Sfx("monsoon_roll", 2.0, -6)]),
    Shot("S07_SH25", sh25, duration=10.0, sfx=[Sfx("monsoon_roll", 0.0, -4), Sfx("thunder", 6.4, -6, params={"dist": 0.5})]),
    Shot("S07_SH26", sh26, duration=7.0, sfx=[Sfx("thunder", 3.0, -8, params={"dist": 0.3}),
                                              Sfx("monsoon_roll", 0.5, -10)]),
    Shot("S07_SH27", sh27, duration=5.5, music="", sfx=[Sfx("first_drop_tin", 2.4, -2)]),
    Shot("S07_SH28", sh28, duration=6.5,
         sfx=[Sfx("first_drop_tin", 0.6, -4), Sfx("raindrops_tin", 1.8, -6, dur=4.7, params={"density": 0.4})]),
]), 7)
