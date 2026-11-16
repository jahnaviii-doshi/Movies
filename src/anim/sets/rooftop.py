"""Nani's rooftop, the charpais, sleepers, and Meher's POV down into the gali.

draw_rooftop(cv, t, time='night'|'dawn'|'morning'|'evening'|'night_dim', lantern=1.0, cam=None, beds=True,
             town_lights=0.0, powercut_u=None)
  Fixed 1920x1080 composition looking across the terrace toward the town:
  back parapet (y~600-690) with Chandpur beyond, stair-door hut (mumty) with the black water tank on top
  at back-left, right parapet running toward camera, three empty charpais, lantern on a stool,
  raised tulsi planter, clothesline. `cam` = dict(cx, cy, zoom) applies a camera (core.camera) to
  the terrace layers (the sky/town get a gentler parallax). lantern 0..1 = lamp brightness.
  beds=False omits the charpais (draw them yourself with draw_charpai for custom layering).

ANCHORS (screen coords at cam=None; 's' = suggested character scale for chars.draw):
  charpai_nani:   dict(x, y=floor point, surface=(x,y) bed top centre, sit=(x,y) origin for legs='sit',
                       head=(x,y) pillow head position for a sleeper, s)
  charpai_meher:  same keys
  charpai_kabir:  same keys
  parapet_lean:   (x, y, s)  a kid standing at the right parapet, facing right (flip=False), looking down
  water_tank_top: (x, y, s)  where the monkey sits (draw_monkey origin), s for the monkey
  stair_door:     (x, y, s)  feet position of someone in the mumty doorway
  lantern:        (x, y)     lamp flame centre

draw_charpai(cv, x, y, s=1.0, light=None)  (x,y) = floor under bed centre; returns dict(surface, sit, head).
draw_sleeper(cv, x, y, s, t, who='nani'|'kabir'|'meher'|'kid', face_cover=False, sheet='#e9e4f2', breathe=1.0)
  (x,y) = bed-surface centre (use charpai(...)['surface']); the person lies head-left on a pillow.
draw_lantern(cv, x, y, s, t, on=1.0)  hurricane lantern at floor/stool point (x,y).

draw_parapet_view(cv, t, time='night', dog=None)
  Meher's POV straight down into the narrow gali: parapet coping across the bottom of frame, haveli
  walls + carved balconies receding toward the far dead end (top), wires crossing, the lane floor,
  the blue wall at the end catching moonlight. PARAPET_DOG_ANCHOR = (x, y, s) for a small Chutney in the lane
  (DogPose s); BLUE_WALL_POV = (x, y) centre of the far wall.
"""
from __future__ import annotations

import math
from functools import lru_cache

import skia

from .. import core as K
from ..core import W, H, fill, stroke, smooth_path, poly, ellipse, lerp, clamp
from . import town as T

TOWN_TIME = {"night": "night", "night_dim": "night_dim", "dawn": "dawn", "morning": "morning", "evening": "dusk"}
LINE = "#3a2418"
ROPE = "#e8d3a6"
WOOD = "#8a5530"

BEDS = {"nani": (470, 900), "meher": (930, 960), "kabir": (1390, 905)}
BED_S = {"nani": 1.0, "meher": 1.08, "kabir": 1.0}


# ------------------------------------------------------------------ props
def draw_charpai(cv, x, y, s=1.0, light=None):
    """Woven rope bed in 3/4 view. (x,y) = floor point under the bed centre."""
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    hw, d, legh = 190, 70, 62
    sk = 26   # perspective skew of the back edge
    fl, fr = (-hw, -legh), (hw, -legh)
    br, bl = (hw - sk, -legh - d), (-hw - sk, -legh - d)
    # back legs
    for (lx, ly) in (bl, br):
        cv.drawPath(K.rrect(lx - 6, ly, 12, legh - 14, 4), fill(K.shade(WOOD, -0.3)))
    # shadow
    cv.drawOval(skia.Rect.MakeLTRB(-hw - 30, -24, hw + 20, 14), fill("#000000", 0.22))
    # rope bed
    top = poly([fl, fr, br, bl])
    cv.drawPath(top, fill(ROPE))
    cv.save(); cv.clipPath(top, doAntiAlias=True)
    for i in range(-30, 30):
        x0 = i * 14
        cv.drawLine(x0, -legh, x0 + 120, -legh - d - 30, stroke("#c9b07a", 2.4))
        cv.drawLine(x0, -legh, x0 - 90, -legh - d - 30, stroke("#d9c08a", 2.0))
    cv.drawRect(skia.Rect.MakeLTRB(-300, -legh - d - 10, 300, -legh), K.lin_a((0, -legh - d), (0, -legh),
                [("#000000", 0.12), ("#000000", 0.0)]))
    cv.restore()
    # frame rails
    for a, b, w in ((bl, br, 8), (fl, fr, 11), (fl, bl, 9), (fr, br, 9)):
        cv.drawLine(*a, *b, stroke(WOOD, w, cap="round"))
        cv.drawLine(*a, *b, stroke(K.shade(WOOD, 0.25), 2.2))
    cv.drawPath(top, stroke(LINE, 2.6))
    # front legs (turned)
    for (lx, ly) in (fl, fr):
        leg = smooth_path([(lx - 7, ly), (lx + 7, ly), (lx + 9, ly + 20), (lx + 6, ly + 40), (lx + 8, 0),
                           (lx - 8, 0), (lx - 6, ly + 40), (lx - 9, ly + 20)], tension=0.4)
        cv.drawPath(leg, K.lin((lx - 9, 0), (lx + 9, 0), [K.shade(WOOD, 0.15), WOOD, K.shade(WOOD, -0.3)]))
        cv.drawPath(leg, stroke(LINE, 2.2))
    cv.restore()
    surf = (x - sk * 0.5 * s, y - (legh + d * 0.5) * s)
    return {"surface": surf, "sit": (surf[0] - 30 * s, surf[1] + 85 * s), "head": (x - (hw - 40) * s, surf[1] - 18 * s)}


def draw_lantern(cv, x, y, s=1.0, t=0.0, on=1.0):
    fl = 1.0 + 0.06 * math.sin(t * 13) + 0.04 * math.sin(t * 7.3 + 1)
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    if on > 0:
        g = on * fl
        cv.drawCircle(0, -40, 160, K.rad_a((0, -40), 160, [("#ffb347", 0.32 * g), ("#ff9a3a", 0.12 * g), ("#ff9a3a", 0)],
                                            [0, 0.4, 1]))
    cv.drawPath(K.rrect(-22, -10, 44, 10, 3), fill("#6a2d22")); cv.drawPath(K.rrect(-22, -10, 44, 10, 3), stroke(LINE, 2))
    glass = smooth_path([(-14, -12), (-20, -36), (-12, -60), (12, -60), (20, -36), (14, -12)], tension=0.5)
    cv.drawPath(glass, fill("#fff1c8" if on > 0 else "#9aa0a8", 0.55 + 0.4 * on))
    if on > 0:
        cv.drawPath(ellipse(0, -34, 5 * fl, 11 * fl), fill("#fff7d0"))
        cv.drawPath(ellipse(0, -30, 8, 14), fill("#ffb347", 0.6 * on))
    cv.drawPath(glass, stroke(LINE, 2))
    for dx in (-18, 18):
        cv.drawLine(dx * 0.8, -12, dx, -60, stroke("#6a2d22", 3))
    cv.drawPath(K.rrect(-16, -70, 32, 10, 4), fill("#6a2d22"))
    cv.drawPath(smooth_path([(-12, -70), (0, -96), (12, -70)], close=False), stroke("#4a4f5c", 2.4))
    cv.restore()


def draw_sleeper(cv, x, y, s=1.0, t=0.0, who="nani", face_cover=False, sheet="#e9e4f2", breathe=1.0):
    """Person asleep on their back under a light sheet, head on the pillow at the left. (x,y)=bed surface centre."""
    from ..rig import chars
    from ..rig.human import Pose
    rig = chars.CAST.get(who if who != "kid" else "meher")
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    br = math.sin(t * 1.6 + {"nani": 0, "kabir": 2, "meher": 4, "kid": 5}.get(who, 1)) * 2.5 * breathe
    L = {"nani": 300, "kabir": 330, "meher": 280, "kid": 220}.get(who, 280)
    hx = -L / 2 + 20
    # pillow
    pil = smooth_path([(hx - 46, -6), (hx - 40, -40), (hx + 40, -44), (hx + 50, -8), (hx + 10, 2)], tension=0.5)
    cv.drawPath(pil, fill("#f3efe6")); cv.drawPath(pil, stroke(LINE, 2.2))
    # body lump under sheet
    body = smooth_path([(hx + 30, -10), (hx + 60, -46 - br), (hx + 150, -54 - br), (L / 2 - 50, -40), (L / 2 - 6, -34),
                        (L / 2 + 6, -12), (L / 2 - 10, 4), (hx + 30, 6)], tension=0.45)
    cv.drawPath(body, K.lin((0, -60), (0, 6), [K.shade(sheet, 0.08), sheet, K.shade(sheet, -0.18)]))
    cv.save(); cv.clipPath(body, doAntiAlias=True)
    for i in range(5):
        cv.drawPath(smooth_path([(hx + 60 + i * 40, -48), (hx + 80 + i * 40, -20), (hx + 70 + i * 40, 4)], close=False),
                    stroke(K.shade(sheet, -0.15), 2))
    cv.restore()
    cv.drawPath(body, stroke(LINE, 2.4))
    # head (rig head, rotated so the face looks up)
    cv.save(); cv.translate(hx, -34); cv.rotate(-78)
    sc = 0.55 if who != "kid" else 0.45
    cv.scale(sc, sc)
    if rig is not None:
        rig.draw_head(cv, Pose(expr="sleepy", blink=1.0, t=t, turn=0.0, extra={"no_specs": True}))
    cv.restore()
    if face_cover:
        cv.save(); cv.translate(hx + 6, -38); cv.rotate(-70)
        cap = ellipse(0, 0, 30, 22)
        cv.drawPath(cap, K.lin((0, -22), (0, 22), [K.shade("cap_red", 0.15), "cap_red"]))
        cv.drawPath(cap, stroke(LINE, 2.4))
        cv.drawLine(0, -22, 0, 22, stroke(K.shade("cap_red", -0.3), 1.6))
        brim = K.rrect(-34, 14, 42, 10, 5)
        cv.drawPath(brim, fill(K.shade("cap_red", -0.15))); cv.drawPath(brim, stroke(LINE, 2))
        cv.restore()
    # a hand resting on the sheet
    cv.drawPath(ellipse(hx + 120, -50 - br, 9, 7), fill(rig.skin if rig else "skin"))
    cv.drawPath(ellipse(hx + 120, -50 - br, 9, 7), stroke(LINE, 1.8))
    cv.restore()


def draw_tulsi(cv, x, y, s=1.0, t=0.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    base = poly([(-46, 0), (46, 0), (40, -90), (-40, -90)])
    cv.drawPath(base, K.lin((-46, 0), (46, 0), ["#f0e2c6", "#e2cfa8", "#bfa27a"]))
    cv.drawPath(base, stroke(LINE, 2.4))
    cv.drawRect(skia.Rect.MakeLTRB(-52, -104, 52, -88), fill("#e9d8b6")); cv.drawRect(skia.Rect.MakeLTRB(-52, -104, 52, -88), stroke(LINE, 2.2))
    cv.drawPath(ellipse(0, -40, 14, 18), fill("#c9563a", 0.9))   # painted niche
    cv.drawCircle(0, -48, 4, fill("#ffd23f"))
    r = K.rng(9)
    for i in range(26):
        a = -math.pi / 2 + r.uniform(-1.3, 1.3)
        L = r.uniform(30, 70)
        sw = math.sin(t * 1.2 + i) * 2
        x1, y1 = math.cos(a) * L * 0.5 + sw, -104 + math.sin(a) * L
        cv.drawLine(0, -100, x1, y1, stroke("#3f6b35", 2))
        cv.drawPath(ellipse(x1, y1, 7, 4.5), fill(r.choice(["#4f8a43", "#5f9a4f", "#3f7a3a"])))
    cv.restore()


def draw_stool(cv, x, y, s=1.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    for dx in (-24, 24):
        cv.drawLine(dx, 0, dx * 0.8, -46, stroke(WOOD, 7))
    top = K.rrect(-34, -56, 68, 12, 4)
    cv.drawPath(top, fill(K.shade(WOOD, 0.1))); cv.drawPath(top, stroke(LINE, 2.2))
    cv.restore()


# ------------------------------------------------------------------ static terrace
def _terrace(cv, time):
    rng = K.rng(31)
    # back parapet (top face + front face)
    cv.drawRect(skia.Rect.MakeLTRB(-20, 600, W + 20, 616), fill("#efe2c8"))
    wall = skia.Rect.MakeLTRB(-20, 616, W + 20, 700)
    cv.drawRect(wall, K.lin((0, 616), (0, 700), ["#d9c3a0", "#c4a983"]))
    for i in range(24):
        px, py = rng.uniform(0, W), rng.uniform(625, 690)
        cv.drawOval(skia.Rect.MakeXYWH(px, py, rng.uniform(20, 60), rng.uniform(6, 14)), fill("#b8996f", 0.4))
    for i in range(5):  # brick peeks
        px, py = rng.uniform(100, W - 100), rng.uniform(630, 680)
        cv.save(); cv.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(px, py, 40, 22), 8, 8), doAntiAlias=True)
        for r_ in range(4):
            for c_ in range(5):
                cv.drawRect(skia.Rect.MakeXYWH(px + c_ * 11 - (r_ % 2) * 5, py + r_ * 6, 9, 4), fill("brick", 0.75))
        cv.restore()
    cv.drawLine(-20, 600, W + 20, 600, stroke(LINE, 2.4))
    cv.drawLine(-20, 616, W + 20, 616, stroke(LINE, 1.6))
    # floor with perspective tiles
    floor = skia.Rect.MakeLTRB(-20, 700, W + 20, H + 20)
    cv.drawRect(floor, K.lin((0, 700), (0, H), ["#cdb995", "#d8c4a0", "#c9b089"]))
    vx, vy = 960, 300
    for i in range(-16, 17):
        bx = 960 + i * 150
        x0 = lerp(vx, bx, (700 - vy) / (H - vy))
        cv.drawLine(x0, 700, bx, H, stroke("#b39a74", 1.4, 0.7))
    yy = 700
    step = 20
    while yy < H:
        cv.drawLine(-20, yy, W + 20, yy, stroke("#b39a74", 1.4, 0.6))
        step *= 1.32
        yy += step
    for i in range(30):   # stains / wear
        px, py = rng.uniform(0, W), rng.uniform(720, H)
        cv.drawOval(skia.Rect.MakeXYWH(px, py, rng.uniform(40, 140), rng.uniform(8, 26)), fill("#a88d66", 0.18))
    # shadow under back parapet
    cv.drawRect(skia.Rect.MakeLTRB(-20, 700, W + 20, 740), K.lin_a((0, 700), (0, 740), [("#000000", 0.18), ("#000000", 0)]))

    # right parapet running toward camera
    rp_top = poly([(1640, 600), (1690, 600), (1990, H + 40), (1890, H + 40)])
    rp_face = poly([(1600, 616), (1640, 600), (1890, H + 40), (1760, H + 40)])
    cv.drawPath(rp_face, K.lin((1600, 0), (1890, 0), ["#cdb48d", "#bfa27a"]))
    cv.drawPath(rp_top, fill("#efe2c8"))
    cv.drawPath(rp_face, stroke(LINE, 2.2)); cv.drawPath(rp_top, stroke(LINE, 2.2))
    cv.drawPath(poly([(1690, 600), (W + 20, 600), (W + 20, H + 40), (1990, H + 40)]), fill("#c6b08e"))

    # mumty (stair-door hut) back-left
    hut = skia.Rect.MakeLTRB(90, 330, 470, 700)
    cv.drawRect(hut, K.lin((90, 0), (470, 0), ["#e2cca6", "#d8bf96", "#bea078"]))
    cv.drawRect(skia.Rect.MakeLTRB(80, 316, 480, 334), fill("#ecdcbc"))
    cv.drawRect(skia.Rect.MakeLTRB(80, 316, 480, 334), stroke(LINE, 2.2))
    for i in range(3):
        px, py = rng.uniform(110, 430), rng.uniform(350, 640)
        cv.drawOval(skia.Rect.MakeXYWH(px, py, rng.uniform(30, 60), rng.uniform(10, 20)), fill("#b8996f", 0.35))
    cv.drawRect(hut, stroke(LINE, 2.6))
    door = T.window_path(200, 430, 130, 270)
    cv.drawPath(door, fill("#5a3a2a"))
    cv.save(); cv.clipPath(door, doAntiAlias=True)
    cv.drawRect(skia.Rect.MakeLTRB(200, 430, 265, 700), fill("#7a4a2a"))
    cv.drawRect(skia.Rect.MakeLTRB(265, 430, 330, 700), fill("#6e4226"))
    for yy in range(470, 700, 40):
        cv.drawLine(200, yy, 330, yy, stroke("#4e2c18", 2))
    for k in range(4):
        cv.drawCircle(225 + (k % 2) * 80, 520 + (k // 2) * 100, 4, fill("brass"))
    cv.restore()
    cv.drawPath(door, stroke(LINE, 2.6))
    cv.drawRect(skia.Rect.MakeLTRB(190, 700 - 6, 340, 704), fill("#bfa27a"))
    # small window on the hut
    T.arched_window(cv, 390, 400, 40, 70, frame="#5a3a2a", lw=2)
    # water tank on top of the hut
    T.water_tank(cv, 370, 316, r=62, h=96, lw=2.4, line=LINE)
    cv.drawRect(skia.Rect.MakeLTRB(300, 300, 440, 318), fill("#5a5a66"))
    # pipe
    cv.drawLine(430, 300, 430, 316, stroke("#5a5a66", 6)); cv.drawLine(452, 260, 452, 700, stroke("#6a6a76", 5))
    # clothesline from hut to a pole
    cv.drawRect(skia.Rect.MakeLTRB(1504, 360, 1514, 640), fill("#5a4a40"))
    cv.drawRect(skia.Rect.MakeLTRB(1504, 360, 1514, 640), stroke(LINE, 1.6))


@lru_cache(maxsize=8)
def _static(time):
    light = T.TIME_LIGHT[TOWN_TIME[time]]

    def paint(cv):
        with K.lit(cv, light):
            _terrace(cv, time)
        grade = {"night": ("#070a24", 0.18, 0.5), "night_dim": ("#04061a", 0.3, 0.62), "evening": ("#3a1c30", 0.05, 0.3),
                 "dawn": ("#4a3060", 0.05, 0.22)}.get(time)
        if grade:
            gc, a0, a1 = grade
            pnt = K.lin_a((0, 300), (0, H), [(gc, a0), (gc, a1)])
            pnt.setBlendMode(skia.BlendMode.kSrcATop)
            cv.drawRect(skia.Rect.MakeWH(W, H), pnt)
        if time in ("night", "night_dim", "evening"):
            # moonlight rim on parapet tops
            cv.drawRect(skia.Rect.MakeLTRB(0, 598, W, 606), fill("#bcc8ff", 0.25))
    return K.render_to_image(W, H, paint)


@lru_cache(maxsize=8)
def _beds(time):
    light = T.TIME_LIGHT[TOWN_TIME[time]]

    def paint(cv):
        with K.lit(cv, light):
            for k in ("nani", "kabir", "meher"):
                draw_charpai(cv, *BEDS[k], s=BED_S[k])
            draw_stool(cv, 735, 805, 0.9)
            draw_tulsi(cv, 1530, 770, 0.95, t=0.0)
    return K.render_to_image(W, H, paint)


def _anchors():
    out = {}
    for k in ("nani", "meher", "kabir"):
        x, y = BEDS[k]
        s = BED_S[k]
        hw, d, legh, sk = 190, 70, 62, 26
        surf = (x - sk * 0.5 * s, y - (legh + d * 0.5) * s)
        out[f"charpai_{k}"] = {"x": x, "y": y, "surface": surf, "sit": (surf[0] - 30 * s, surf[1] + 85 * s),
                               "head": (x - (hw - 40) * s, surf[1] - 18 * s), "s": 1.05 * s}
    out["parapet_lean"] = (1625, 800, 1.1)
    out["water_tank_top"] = (370, 200, 1.1)
    out["stair_door"] = (265, 700, 0.95)
    out["lantern"] = (735, 805 - 50 * 0.9 - 34)
    return out


ANCHORS = _anchors()


from contextlib import contextmanager


@contextmanager
def _lit_rect(cv, light, rect, amount=1.0):
    """Lighting grade in a bounded layer (much cheaper than a full-frame layer)."""
    paint = skia.Paint()
    paint.setColorFilter(K.matrix_filter(K.light_matrix(light, amount)))
    cv.saveLayer(rect, paint)
    try:
        yield cv
    finally:
        cv.restore()


@lru_cache(maxsize=12)
def _town_layers(tt, town_lights):
    return K.render_to_image(W, H, lambda c: T.draw_town(c, 0.0, time=tt, lights=town_lights, skip_near=True,
                                                          y_offset=-60, cam_x=300, sky=False))


def draw_rooftop(cv, t, time="night", lantern=1.0, cam=None, beds=True, town_lights=0.0, powercut_u=None):
    tt = TOWN_TIME[time]
    # sky + town beyond the parapet (gentle parallax with the camera)
    cv.save()
    if cam:
        z = 1 + (cam.get("zoom", 1) - 1) * 0.35
        cv.translate(W / 2, H / 2); cv.scale(z, z)
        cv.translate(-W / 2 - (cam.get("cx", W / 2) - W / 2) * 0.3, -H / 2 - (cam.get("cy", H / 2) - H / 2) * 0.3)
    if powercut_u is None:
        cv.drawImage(T._sky(tt), 0, 0)
        if tt in ("night", "night_dim"):
            K.stars(cv, W, H, t, n=240, seed=7, bottom=620, alpha=1.0 if tt == "night" else 0.7)
        elif tt == "dawn":
            K.stars(cv, W, H, t, n=60, seed=7, bottom=300, alpha=0.35)
        cv.drawImage(_town_layers(tt, round(town_lights, 2)), 0, 0)
    else:
        T.draw_town(cv, t, time=tt, lights=town_lights, powercut_u=powercut_u, skip_near=True, y_offset=-60,
                    cam_x=300)
    cv.restore()
    cv.save()
    if cam:
        cv.translate(W / 2, H / 2); cv.scale(cam.get("zoom", 1), cam.get("zoom", 1))
        cv.translate(-cam.get("cx", W / 2), -cam.get("cy", H / 2))
    cv.drawImage(_static(time), 0, 0)
    light = T.TIME_LIGHT[tt]
    # clothesline with swaying clothes (live)
    with _lit_rect(cv, light, skia.Rect.MakeLTRB(440, 340, 1560, 520)):
        T.laundry(cv, 470, 380, 1508, 372, K.rng(77), t=t, sag=26, lw=2.0, line=LINE, n=7)
    if beds:
        cv.drawImage(_beds(time), 0, 0)
    lx, ly = 735, 805 - 50 * 0.9
    on = lantern if time in ("night", "night_dim", "evening", "dawn") else 0.0
    if time == "dawn":
        on *= 0.4
    with _lit_rect(cv, light, skia.Rect.MakeLTRB(lx - 160, ly - 200, lx + 160, ly + 20), amount=0.35 if on > 0 else 1.0):
        draw_lantern(cv, lx, ly, 0.9, t, on=on)
    if on > 0:
        fl = 1.0 + 0.05 * math.sin(t * 11) + 0.03 * math.sin(t * 5.3)
        R_ = 620 * fl
        p = K.rad_a((lx, ly - 30), R_, [("#ffb347", 0.28 * on), ("#ff9a3a", 0.10 * on), ("#ff9a3a", 0)], [0, 0.4, 1])
        p.setBlendMode(skia.BlendMode.kPlus)
        cv.drawRect(skia.Rect.MakeLTRB(lx - R_, ly - 30 - R_, lx + R_, ly - 30 + R_), p)
    cv.restore()


# ------------------------------------------------------------------ parapet POV
VP = (960, 150)
PARAPET_DOG_ANCHOR = (930, 700, 0.42)
BLUE_WALL_POV = (960, 190)


def _lane_x(side, y):
    """Lane edge x at screen y (side -1 left, +1 right). Lane bottom edge at y=960."""
    u = (y - VP[1]) / (960 - VP[1])
    return VP[0] + side * lerp(52, 170, u)


def _roof_x(side, y):
    u = (y - VP[1]) / (960 - VP[1])
    return VP[0] + side * lerp(150, 1100, u)


@lru_cache(maxsize=4)
def _pov_static(time):
    light = "moon"
    rng = K.rng(404)

    def paint(cv):
        cv.drawRect(skia.Rect.MakeWH(W, H), fill("#0b0d26"))
        with K.lit(cv, light):
            # lane floor
            lane = poly([(_lane_x(-1, VP[1] + 40), VP[1] + 40), (_lane_x(1, VP[1] + 40), VP[1] + 40),
                         (_lane_x(1, 1000), 1000), (_lane_x(-1, 1000), 1000)])
            cv.drawPath(lane, K.lin((0, VP[1]), (0, 1000), ["#cdb995", "#d8c4a0", "#b39a74"]))
            cv.save(); cv.clipPath(lane, doAntiAlias=True)
            for i in range(40):
                y = VP[1] + 40 + (i / 40) ** 1.6 * 900
                cv.drawLine(0, y, W, y, stroke("#9a8060", 1.2, 0.5))
            cv.drawLine(960, VP[1], 960, 1000, stroke("#7d6a52", 3, 0.6))   # drain
            cv.restore()
            # blue wall at the dead end
            bw = skia.Rect.MakeLTRB(_lane_x(-1, VP[1] + 40) - 10, VP[1] - 30, _lane_x(1, VP[1] + 40) + 10, VP[1] + 42)
            cv.drawRect(bw, K.lin((0, bw.top()), (0, bw.bottom()), ["#5c93cf", "wall_blue", "wall_blue_dark"]))
            for k in range(6):
                cv.drawOval(skia.Rect.MakeXYWH(bw.left() + rng.uniform(0, 90), bw.top() + rng.uniform(0, 50), 18, 8),
                            fill("#d9cdb0", 0.6))
            cv.drawRect(bw, stroke(LINE, 1.6))
            # side walls: moonlit at the roof edge (near us), falling into deep shadow toward the lane
            for side in (-1, 1):
                wall = poly([(_roof_x(side, VP[1] - 40), VP[1] - 40), (_lane_x(side, VP[1] - 40), VP[1] - 40),
                             (_lane_x(side, 1100), 1100), (_roof_x(side, 1100), 1100)])
                lit_c = "#d8c6a4" if side < 0 else "#cdb592"
                cv.drawPath(wall, K.lin((_roof_x(side, 640), 640), (_lane_x(side, 640), 640),
                                        [lit_c, K.mix(lit_c, "#1a1c3a", 0.55), "#0c0d22"], [0, 0.45, 1]))
                cv.save(); cv.clipPath(wall, doAntiAlias=True)
                for f in range(10):
                    u0 = f / 10
                    yb = VP[1] + (u0 ** 1.25) * 900
                    cv.drawLine(_roof_x(side, yb), yb, _lane_x(side, yb), yb, stroke("#1a1626", 2.2, 0.7))
                    for k in range(4):
                        uu = 0.12 + k * 0.22
                        fx = lerp(_roof_x(side, yb), _lane_x(side, yb), uu)
                        fy = yb + 14 + 30 * u0
                        sz = 8 + 42 * u0
                        if (f + k) % 3 == 0 and f > 1:
                            # carved balcony projecting toward the lane, roof seen from above
                            bx1 = lerp(_roof_x(side, fy), _lane_x(side, fy), min(0.97, uu + 0.12))
                            box = poly([(fx, fy), (bx1, fy + sz * 0.1), (bx1, fy + sz * 0.9), (fx, fy + sz)])
                            cv.drawPath(box, fill("#6a3e26")); cv.drawPath(box, stroke("#1a0f0a", 1.6))
                            cv.drawPath(poly([(bx1, fy + sz * 0.1), (bx1 + side * -sz * 0.18, fy + sz * 0.14),
                                              (bx1 + side * -sz * 0.18, fy + sz * 0.86), (bx1, fy + sz * 0.9)]),
                                        fill("#a8774a"))
                            if f % 2:
                                cv.drawCircle(fx + (bx1 - fx) * 0.5, fy + sz * 0.5, sz * 0.18, fill("#4f7d43"))
                        elif k < 3:
                            wp = T.window_path(fx - sz * 0.25, fy, sz * 0.5, sz * 0.9)
                            cv.drawPath(wp, fill("#1a1220")); cv.drawPath(wp, stroke("#120c10", 1.2))
                # roof-edge parapet coping (near, crisp, moonlit)
                cv.restore()
                cv.drawPath(wall, stroke(LINE, 2))
                edge = poly([(_roof_x(side, VP[1] - 40), VP[1] - 40), (_roof_x(side, VP[1] - 40) + side * 26, VP[1] - 40),
                             (_roof_x(side, 1100) + side * 120, 1100), (_roof_x(side, 1100), 1100)])
                cv.drawPath(edge, fill("#b9b6c8")); cv.drawPath(edge, stroke(LINE, 2))
            # laundry strung across the gulf
            for i, y0 in enumerate((330, 560)):
                xl, xr = _roof_x(-1, y0) + 40, _roof_x(1, y0) - 40
                T.laundry(cv, xl, y0, xr, y0 + 10, K.rng(500 + i), sag=30 + i * 20, lw=1.6, line="#120c10", n=6)
            # wires crossing the gulf
            for i in range(9):
                y0 = 260 + i * 70 + rng.uniform(-20, 20)
                T.wire(cv, -10, y0, W + 10, y0 + rng.uniform(-60, 60), sag=rng.uniform(20, 60), col="#0e0c14", w=2.2)
            # parapet coping across the bottom (we're leaning over it)
            cv.drawPath(poly([(-20, 980), (W + 20, 960), (W + 20, H + 20), (-20, H + 20)]), fill("#e2cfac"))
            cv.drawPath(poly([(-20, 980), (W + 20, 960), (W + 20, 990), (-20, 1010)]), fill("#f0e2c6"))
            cv.drawLine(-20, 980, W + 20, 960, stroke(LINE, 2.6))
            cv.drawLine(-20, 1010, W + 20, 990, stroke(LINE, 1.6))
        # moonlight: cool shaft down the lane, blue wall catches it
        p = K.lin_a((0, 0), (0, H), [("#c9d4ff", 0.20), ("#c9d4ff", 0.0)])
        p.setBlendMode(skia.BlendMode.kPlus)
        cv.drawPath(poly([(760, 0), (1160, 0), (_lane_x(1, 900), 900), (_lane_x(-1, 900), 900)]), p)
        cv.drawRect(bw.makeOutset(30, 30), K.rad_a((bw.centerX(), bw.centerY()), 140, [("#9fc0ff", 0.35), ("#9fc0ff", 0)]))
    return K.render_to_image(W, H, paint)


def draw_parapet_view(cv, t, time="night", dog=None):
    cv.drawImage(_pov_static(time), 0, 0)
    # faint glints in the blue wall's cracks (slow pulse; the magic is stirring)
    bx, by = BLUE_WALL_POV
    a = 0.12 + 0.08 * math.sin(t * 1.3)
    cv.drawCircle(bx, by, 60, K.rad_a((bx, by), 60, [("#ffd36b", a * 0.5), ("#ffd36b", 0)]))
