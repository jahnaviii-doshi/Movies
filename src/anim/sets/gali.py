"""The gali: the narrow old lane that ends at the peeling blue wall.

draw_gali(cv, t, time='night'|'day'|'dawn'|'sunrise', syrup=0.0, rickshaw=True, wall_glow=0.0, cam=None)
    One-point perspective down the lane, camera at child height (~1.15 m). Havelis on both
    sides (jharokha balconies, arched doors with brass lion knockers, steps, drainpipes,
    tulsi pots, shutters), a tangle of wires overhead, a sleeping cycle-rickshaw on the right.
    syrup 0..1  the lane floods with glossy amber syrup (rising, rippling, a floating slipper)
    wall_glow   the far wall's cracks glow gold (matches wall.py)
    cam         None or (cx, cy, zoom) in screen/world px — wraps the draw in core.camera

draw_gali_side(cv, t, time='night'|'day', scroll=0.0, syrup=0.0)
    Side elevation for lateral tracking shots: seamlessly scrolling house fronts.
    Characters stand on GROUND_Y_SIDE at s≈2.0. scroll in px (any value; wraps).

Anchors / helpers
    gali_ground(d) -> (y, s): d=0 near camera .. 1 at the wall; screen y of the lane-centre
        floor and the rig scale (chars ~300 units tall at s=1). gali_ground(0) ≈ (1103, 2.2).
    gali_x(d, a) -> x: screen x for lateral offset a in metres (-1.7..1.7) at depth d.
    project(X, Y, Z) -> (x, y): world metres -> screen (Y down, floor at Y=1.15).
    WALL_RECT  (l, t, r, b) screen rect of the blue wall at the end of the lane.
    RICKSHAW_POS  dict(x, y, s, matrix) — rickshaw_matrix() gives the perspective matrix that
        maps draw_rickshaw's local coords (drawn at x=0,y=0,s=1) onto its parking spot.
    plane_matrix(X) -> skia.Matrix mapping elevation coords (u = depth cm, v = height cm,
        negative up) on the facade plane x=X metres onto the screen.

Shared helpers used by wall.py / shop.py: bloom(cv, draw_fn, radius, strength, color_filter).
"""
from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
import skia

from .. import core as K
from ..core import C, fill, stroke, lerp, clamp, smooth_path, poly, ellipse

W, H = 1920, 1080
F = 720.0
VPX, VPY = 960.0, 520.0
FLOOR = 1.15            # camera height above floor (m)
HALF = 1.7              # half lane width (m)
ZWALL = 9.0
Z_NEAR_CHAR, Z_FAR_CHAR = 1.42, 8.4


# ------------------------------------------------------------------ projection
def project(X, Y, Z):
    return (VPX + X * F / Z, VPY + Y * F / Z)


def plane_matrix(X: float) -> skia.Matrix:
    """Facade plane x=X. Input (u, v): u = depth Z in cm, v = height in cm (negative up, 0 = floor)."""
    # w = 0.01 u ; x = 9.6u + X F ; y = 5.2u + 7.2v + F*FLOOR
    return skia.Matrix.MakeAll(VPX * 0.01, 0, X * F, VPY * 0.01, F * 0.01, F * FLOOR, 0.01, 0, 0)


def floor_matrix(Y: float = FLOOR) -> skia.Matrix:
    """Horizontal plane at height Y. Input (a, u): a = lateral cm, u = depth cm."""
    return skia.Matrix.MakeAll(F * 0.01, VPX * 0.01, 0, 0, VPY * 0.01, F * Y, 0, 0.01, 0)


def zplane_matrix(Z: float) -> skia.Matrix:
    """Plane at depth Z (parallel to the screen). Input (a, v) in cm: a lateral, v height (neg up)."""
    k = F / Z * 0.01
    return skia.Matrix.MakeAll(k, 0, VPX, 0, k, VPY + FLOOR * F / Z, 0, 0, 1)


def gali_ground(d: float):
    Z = lerp(Z_NEAR_CHAR, Z_FAR_CHAR, clamp(d))
    return (VPY + FLOOR * F / Z, F / Z * 0.00433)


def gali_x(d: float, a: float = 0.0):
    Z = lerp(Z_NEAR_CHAR, Z_FAR_CHAR, clamp(d))
    return VPX + a * F / Z


_wl, _wt = project(-HALF, FLOOR - 3.6, ZWALL)
_wr, _wb = project(HALF, FLOOR, ZWALL)
WALL_RECT = (_wl, _wt, _wr, _wb)

_RX, _RU, _RK = 1.2, 470.0, 0.5


def rickshaw_matrix() -> skia.Matrix:
    m = plane_matrix(_RX)
    m.preConcat(skia.Matrix.MakeAll(_RK, 0, _RU, 0, _RK, 0, 0, 0, 1))
    return m


_rx, _ry = project(_RX, FLOOR, _RU / 100)
RICKSHAW_POS = dict(x=_rx, y=_ry, s=F / (_RU / 100) * 0.005, matrix=rickshaw_matrix)


# ------------------------------------------------------------------ shared helpers
_BLOOM_SURF = {}


def _bsurf(key, w, h):
    sf = _BLOOM_SURF.get(key)
    if sf is None or sf.width() != w or sf.height() != h:
        sf = skia.Surface(w, h)
        _BLOOM_SURF[key] = sf
    return sf


def bloom(cv: skia.Canvas, draw_fn, radius=24.0, strength=1.0, scale=0.25, color_filter=None):
    """Additive soft glow: draw_fn(canvas) is rendered at low res (same transform), blurred,
    upscaled, and added on top (~25 ms at 1080p). Note: upscaling directly with a non-srcover
    blend mode hits a very slow skia path, hence the separate full-res upscale surface."""
    if strength <= 0.001:
        return
    w, h = int(W * scale), int(H * scale)
    s1 = _bsurf("lo", w, h)
    lc = s1.getCanvas()
    lc.clear(skia.ColorTRANSPARENT)
    lc.save()
    lc.scale(scale, scale)
    lc.concat(cv.getTotalMatrix())
    draw_fn(lc)
    lc.restore()
    img = s1.makeImageSnapshot()
    s2 = _bsurf("blur", w, h)
    c2 = s2.getCanvas()
    c2.clear(skia.ColorTRANSPARENT)
    p = skia.Paint()
    r = max(0.5, radius * scale)
    p.setImageFilter(skia.ImageFilters.Blur(r, r))
    if color_filter is not None:
        p.setColorFilter(color_filter)
    c2.drawImage(img, 0, 0, skia.SamplingOptions(), p)
    s3 = _bsurf("full", W, H)
    c3 = s3.getCanvas()
    c3.clear(skia.ColorTRANSPARENT)   # (kSrc blend while scaling hits skia's slow path; clear+srcover is fast)
    c3.drawImageRect(s2.makeImageSnapshot(), skia.Rect.MakeWH(W, H), skia.SamplingOptions(skia.FilterMode.kLinear))
    pp = skia.Paint()
    pp.setBlendMode(skia.BlendMode.kPlus)
    pp.setAlphaf(clamp(strength))
    cv.save()
    cv.resetMatrix()
    cv.drawImage(s3.makeImageSnapshot(), 0, 0, skia.SamplingOptions(), pp)
    cv.restore()


_OVER = {}


def overlay(cv, key, draw_fn, alpha=1.0, w=W, h=H):
    """Full-frame overlays (big radial gradients cost ~35 ms live): rendered once, drawn 1:1."""
    if alpha <= 0.003:
        return
    img = _OVER.get((key, w, h))
    if img is None:
        sf = skia.Surface(w, h)
        sf.getCanvas().clear(skia.ColorTRANSPARENT)
        draw_fn(sf.getCanvas())
        img = _OVER[(key, w, h)] = sf.makeImageSnapshot()
    p = skia.Paint(); p.setAlphaf(clamp(alpha))
    cv.drawImage(img, 0, 0, skia.SamplingOptions(), p)


def draw_cached(cv, img: skia.Image, w=W, h=H):
    cv.drawImageRect(img, skia.Rect.MakeWH(w, h), skia.SamplingOptions(skia.FilterMode.kLinear))


@lru_cache(maxsize=32)
def _render(key, scale, w=W, h=H):
    fn, args = key[0], key[1:]
    surf = skia.Surface(int(w * scale), int(h * scale))
    c = surf.getCanvas()
    c.clear(skia.ColorTRANSPARENT)
    c.scale(scale, scale)
    STATIC[fn](c, *args)
    return surf.makeImageSnapshot()


STATIC = {}


def cached(cv, fn_name, *args, cam=None, w=W, h=H):
    zoom = cam[2] if cam else 1.0
    scale = 1.0 if zoom <= 1.08 else (1.5 if zoom <= 1.6 else 2.0)
    draw_cached(cv, _render((fn_name,) + tuple(args), scale, w, h), w, h)


def apply_cam(cv, cam):
    if cam is None:
        cv.save()
        return
    cx, cy, z = cam
    cv.save()
    cv.translate(W / 2, H / 2)
    cv.scale(z, z)
    cv.translate(-cx, -cy)


# ------------------------------------------------------------------ house elevations
HOUSE_COLS = {
    "whitewash": "#efe3cc", "ochre": "#dcae6a", "pink": "#e6b4a3", "mint": "#b8d1ad",
    "bluewash": "#9bbbdc", "sandstone": "#d8b98c", "lilac": "#c9b6d8",
}
LINE_E = 0.9   # outline width in elevation cm


def _door(cv, u, w, h, col, rng):
    """Arched wooden door centred at u (cm), width w, height h (cm)."""
    frame = smooth_path([(u - w / 2 - 14, 0), (u - w / 2 - 14, -h + w / 2), (u - w * 0.3, -h - 12),
                         (u, -h - w * 0.18 - 16), (u + w * 0.3, -h - 12), (u + w / 2 + 14, -h + w / 2),
                         (u + w / 2 + 14, 0)], close=True, tension=0.4)
    cv.drawPath(frame, fill(K.shade(col, -0.18)))
    cv.drawPath(frame, stroke("line", LINE_E))
    door = smooth_path([(u - w / 2, 0), (u - w / 2, -h + w / 2), (u - w * 0.28, -h), (u, -h - w * 0.15),
                        (u + w * 0.28, -h), (u + w / 2, -h + w / 2), (u + w / 2, 0)], close=True, tension=0.4)
    wood = rng.choice(["#6b3e22", "#5a3a2a", "#3f5f6e", "#7a3328"])
    cv.drawPath(door, K.lin((u, -h), (u, 0), [K.shade(wood, 0.12), wood, K.shade(wood, -0.25)]))
    cv.drawLine(u, -h - w * 0.12, u, 0, stroke("#2a1a1c", 1.2))
    for k in range(4):                       # panels
        for sd in (-1, 1):
            r = K.rrect(u + sd * w * 0.27 - w * 0.17, -h * (0.22 + k * 0.19) - h * 0.14, w * 0.34, h * 0.14, 3)
            cv.drawPath(r, stroke(K.shade(wood, -0.35), 1.0))
    for k in range(5):                       # brass studs
        for sd in (-1, 1):
            cv.drawCircle(u + sd * w * 0.42, -h * (0.1 + k * 0.17), 1.8, fill("brass"))
    # lion knockers
    for sd in (-1, 1):
        kx, ky = u + sd * w * 0.18, -h * 0.5
        cv.drawCircle(kx, ky, 5, fill("brass"))
        cv.drawCircle(kx, ky + 6, 6, stroke("brass_dark", 1.6))
    cv.drawPath(door, stroke("line", LINE_E))
    # step
    st = K.rrect(u - w / 2 - 24, -14, w + 48, 16, 2)
    cv.drawPath(st, fill(K.shade("#b9a58a", -0.05)))
    cv.drawPath(st, stroke("line", LINE_E * 0.8))


def _window(cv, u, v, w, h, col, shutter, rng, open_=0.3):
    frame = K.rrect(u - w / 2 - 8, v - h - 8, w + 16, h + 16, 6)
    cv.drawPath(frame, fill(K.shade(col, -0.15)))
    arch = smooth_path([(u - w / 2, v), (u - w / 2, v - h + w / 2), (u, v - h - 4), (u + w / 2, v - h + w / 2),
                        (u + w / 2, v)], tension=0.45)
    cv.drawPath(arch, fill("#1c1622"))
    for i in range(1, 3):                    # grille
        cv.drawLine(u - w / 2 + w * i / 3, v - h + 6, u - w / 2 + w * i / 3, v, stroke("#5a4a3a", 1.2))
    cv.drawPath(arch, stroke("line", LINE_E))
    sw = w / 2 * (1 - open_)
    for sd in (-1, 1):
        x0 = u + sd * w / 2
        sh = K.poly([(x0, v - h + 8), (x0 + sd * sw, v - h + 8), (x0 + sd * sw, v), (x0, v)])
        cv.drawPath(sh, fill(shutter))
        for k in range(5):
            yy = v - h + 14 + k * (h - 16) / 5
            cv.drawLine(x0, yy, x0 + sd * sw, yy, stroke(K.shade(shutter, -0.3), 1.0))
        cv.drawPath(sh, stroke("line", LINE_E))
    # ledge + flower pot sometimes
    cv.drawRect(skia.Rect.MakeLTRB(u - w / 2 - 14, v + 6, u + w / 2 + 14, v + 14), fill(K.shade(col, -0.22)))
    if rng.random() < 0.5:
        cv.drawPath(K.poly([(u - 12, v + 6), (u + 12, v + 6), (u + 9, v - 12), (u - 9, v - 12)]), fill("#b4613f"))
        for k in range(5):
            cv.drawCircle(u - 10 + k * 5, v - 18 - (k % 2) * 5, 5, fill("#4f8a3e"))


def _jharokha(cv, u, v, w, h, wood):
    """Balcony front panel drawn on the facade-parallel plane in front of the wall."""
    # brackets
    for k in range(3):
        bx = u - w / 2 + 10 + k * (w - 20) / 2
        cv.drawPath(K.poly([(bx - 8, v), (bx + 8, v), (bx + 2, v + 34), (bx - 2, v + 34)]), fill(K.shade(wood, -0.2)))
    body = K.rrect(u - w / 2, v - h, w, h, 4)
    cv.drawPath(body, K.lin((u, v - h), (u, v), [K.shade(wood, 0.1), wood]))
    # arched openings
    n = 3
    for k in range(n):
        ox = u - w / 2 + (k + 0.5) * w / n
        ow = w / n * 0.62
        op = smooth_path([(ox - ow / 2, v - 18), (ox - ow / 2, v - h * 0.62), (ox, v - h * 0.82),
                          (ox + ow / 2, v - h * 0.62), (ox + ow / 2, v - 18)], tension=0.45)
        cv.drawPath(op, fill("#1c1622"))
        # jali dots
        for j in range(4):
            cv.drawCircle(ox, v - 26 - j * 9, 1.5, fill(K.shade(wood, 0.3), 0.7))
        cv.drawPath(op, stroke(K.shade(wood, -0.4), 1.0))
    # carved rail
    cv.drawRect(skia.Rect.MakeLTRB(u - w / 2, v - 16, u + w / 2, v), fill(K.shade(wood, -0.15)))
    for k in range(int(w // 9)):
        cv.drawCircle(u - w / 2 + 5 + k * 9, v - 8, 2.2, fill(K.shade(wood, 0.25)))
    cv.drawPath(body, stroke("line", LINE_E))
    # chhajja roof + mini dome
    roof = K.poly([(u - w / 2 - 14, v - h), (u + w / 2 + 14, v - h), (u + w / 2 - 4, v - h - 18), (u - w / 2 + 4, v - h - 18)])
    cv.drawPath(roof, fill(K.shade(wood, -0.1)))
    cv.drawPath(roof, stroke("line", LINE_E))
    dome = smooth_path([(u - w * 0.28, v - h - 18), (u - w * 0.2, v - h - 40), (u, v - h - 52), (u + w * 0.2, v - h - 40),
                        (u + w * 0.28, v - h - 18)], tension=0.5)
    cv.drawPath(dome, fill(K.shade(wood, 0.05)))
    cv.drawPath(dome, stroke("line", LINE_E))
    cv.drawLine(u, v - h - 52, u, v - h - 64, stroke("brass", 2))


def _house(cv, u0, u1, top, colname, rng, side):
    col = HOUSE_COLS[colname]
    body = K.rrect(u0, top, u1 - u0, -top, 0)
    cv.drawPath(body, K.lin((0, top), (0, 0), [K.shade(col, 0.06), col, K.shade(col, -0.12)]))
    # weathering: stains + flaking patches
    for _ in range(int((u1 - u0) / 18)):
        x, y = rng.uniform(u0, u1), rng.uniform(top + 10, -40)
        rx, ry = rng.uniform(6, 26), rng.uniform(4, 16)
        cv.drawPath(ellipse(x, y, rx, ry), fill(K.shade(col, rng.uniform(-0.18, 0.08)), 0.35))
    for _ in range(int((u1 - u0) / 60)):
        x = rng.uniform(u0 + 10, u1 - 10)
        cv.drawPath(K.rrect(x - 6, top + 10, 12, 150, 6),
                    K.lin_a((x, top + 20), (x, top + 160), [("#5a4636", 0.22), ("#5a4636", 0)]))
    # plinth band and floor-line band
    cv.drawRect(skia.Rect.MakeLTRB(u0, -34, u1, 0), fill(K.shade(col, -0.25)))
    cv.drawRect(skia.Rect.MakeLTRB(u0, -268, u1, -256), fill(K.shade(col, -0.18)))
    # parapet cornice
    cv.drawRect(skia.Rect.MakeLTRB(u0, top, u1, top + 16), fill(K.shade(col, -0.2)))
    for k in range(int((u1 - u0) / 22)):
        cv.drawRect(skia.Rect.MakeLTRB(u0 + 6 + k * 22, top + 16, u0 + 14 + k * 22, top + 24), fill(K.shade(col, -0.28)))
    span = u1 - u0
    # ground floor: door + maybe a window
    du = u0 + span * rng.uniform(0.35, 0.6)
    if u0 < 100:
        du = u1 - 75
    _door(cv, du, rng.choice([96, 106, 116]), rng.choice([205, 220]), col, rng)
    if span > 180:
        wu = u0 + 40 if du - u0 > span / 2 else u1 - 40
        _window(cv, wu, -110, 46, 70, col, rng.choice(["#3f7d6a", "#2f6aa0", "#7a3328"]), rng, 0.25)
    # upper floor: windows + jharokha (drawn later on a forward plane)
    jh = None
    if rng.random() < 0.8 and span > 150:
        jh = (u0 + span * rng.uniform(0.35, 0.65), -300)
        for wu in (u0 + 34, u1 - 34):
            if abs(wu - jh[0]) > 75:
                _window(cv, wu, -320, 42, 74, col, rng.choice(["#3f7d6a", "#2f6aa0", "#8a5a2a"]), rng, 0.5)
    else:
        for wu in np.linspace(u0 + 45, u1 - 45, max(1, int(span // 95))):
            _window(cv, float(wu), -320, 46, 80, col, rng.choice(["#3f7d6a", "#2f6aa0", "#8a5a2a"]), rng, 0.4)
    if top < -500:
        for wu in np.linspace(u0 + 50, u1 - 50, max(1, int(span // 110))):
            _window(cv, float(wu), -480, 40, 60, col, "#2f6aa0", rng, 0.6)
    # drainpipe at the house edge
    cv.drawRect(skia.Rect.MakeLTRB(u1 - 9, top + 18, u1 - 3, -4), fill("#6b6a6e"))
    cv.drawRect(skia.Rect.MakeLTRB(u1 - 11, -10, u1 + 6, -2), fill("#6b6a6e"))
    for k in range(int(-top // 120)):
        cv.drawRect(skia.Rect.MakeLTRB(u1 - 11, top + 60 + k * 120, u1 - 1, top + 64 + k * 120), fill("#4b4a4e"))
    # rooftop things above parapet: water tank / chhatri / antenna
    r = rng.random()
    mid = (u0 + u1) / 2 + rng.uniform(-40, 40)
    if r < 0.4:
        tank = K.rrect(mid - 28, top - 62, 56, 62, 10)
        cv.drawPath(tank, fill("#2a2a30")); cv.drawPath(tank, stroke("line", LINE_E))
        cv.drawLine(mid - 22, top - 44, mid + 22, top - 44, stroke("#3b3b44", 2))
    elif r < 0.7:
        cv.drawLine(mid, top, mid, top - 110, stroke("#3a3a40", 2.4))
        for k in range(4):
            cv.drawLine(mid - 30 + k * 4, top - 70 - k * 10, mid + 30 - k * 4, top - 70 - k * 10, stroke("#3a3a40", 1.8))
    else:
        dome = smooth_path([(mid - 34, top), (mid - 34, top - 30), (mid, top - 70), (mid + 34, top - 30), (mid + 34, top)], tension=0.5)
        cv.drawPath(dome, fill(K.shade(col, -0.05))); cv.drawPath(dome, stroke("line", LINE_E))
    cv.drawPath(body, stroke("line", LINE_E))
    # tulsi pot on the step sometimes
    if rng.random() < 0.6:
        tu = du + rng.choice([-1, 1]) * 90
        if u0 + 30 < tu < u1 - 30:
            pot = K.poly([(tu - 22, 0), (tu + 22, 0), (tu + 18, -46), (tu - 18, -46)])
            cv.drawPath(pot, fill("#c26a3c")); cv.drawPath(pot, stroke("line", LINE_E))
            cv.drawRect(skia.Rect.MakeLTRB(tu - 22, -50, tu + 22, -42), fill("#d98a4f"))
            for k in range(9):
                a = -math.pi / 2 + (k - 4) * 0.28
                cv.drawCircle(tu + math.cos(a) * 18, -60 + math.sin(a) * 18 - 10, 7, fill("#3f7f3a"))
            cv.drawCircle(tu, -84, 6, fill("#4f9a46"))
    return jh


LEFT_HOUSES = [(40, 250, "whitewash", -560), (250, 470, "ochre", -620), (470, 690, "pink", -520), (690, ZWALL * 100, "mint", -600)]
RIGHT_HOUSES = [(40, 200, "bluewash", -600), (200, 420, "sandstone", -540), (420, 640, "whitewash", -660), (640, ZWALL * 100, "lilac", -580)]


def _facades(cv, side):
    X = -HALF if side < 0 else HALF
    houses = LEFT_HOUSES if side < 0 else RIGHT_HOUSES
    rng = K.rng(11 if side < 0 else 23)
    jhs = []
    for (u0, u1, col, top) in houses:
        cv.save()
        cv.concat(plane_matrix(X))
        jh = _house(cv, u0, u1, top, col, rng, side)
        cv.restore()
        if jh:
            jhs.append((jh, col))
    # jharokhas on forward plane (project out 45 cm), far -> near
    for (u, v), col in sorted(jhs, key=lambda j: -j[0][0]):
        Xf = X - side * 0.45
        w, h = 120, 110
        wood = "#7a4a2a" if col not in ("bluewash",) else "#3f5f6e"
        # side cheek (plane Z = u+-w/2) — the near one is visible
        zc = (u - w / 2) / 100
        cv.save(); cv.concat(zplane_matrix(zc))
        a0, a1 = X * 100, Xf * 100
        cheek = K.poly([(a0, v - h), (a1, v - h), (a1, v), (a0, v)])
        cv.drawPath(cheek, fill(K.shade(wood, -0.3))); cv.drawPath(cheek, stroke("line", 0.6))
        cv.restore()
        # underside
        cv.save(); cv.concat(floor_matrix(FLOOR + v / 100))
        und = K.poly([(a0, u - w / 2), (a1, u - w / 2), (a1, u + w / 2), (a0, u + w / 2)])
        cv.drawPath(und, fill(K.shade(wood, -0.45)))
        cv.restore()
        cv.save(); cv.concat(plane_matrix(Xf))
        _jharokha(cv, u, v, w, h, wood)
        cv.restore()


def _floor(cv, col="#b9a58a"):
    cv.save()
    cv.concat(floor_matrix())
    lane = K.poly([(-HALF * 100, 40), (HALF * 100, 40), (HALF * 100, ZWALL * 100), (-HALF * 100, ZWALL * 100)])
    cv.drawPath(lane, K.lin((0, 40), (0, 900), [K.shade(col, -0.05), col, K.shade(col, 0.05)]))
    rng = K.rng(5)
    # worn flagstones
    row = 0
    u = 40
    while u < ZWALL * 100:
        dh = 42 + rng.uniform(-6, 8)
        off = (row % 2) * 30
        a = -HALF * 100 - off
        while a < HALF * 100:
            wd = rng.uniform(48, 70)
            r = K.rrect(a + 2, u + 2, wd - 4, dh - 4, 6)
            cv.drawPath(r, fill(K.shade(col, rng.uniform(-0.1, 0.08))))
            a += wd
        cv.drawLine(-HALF * 100, u, HALF * 100, u, stroke(K.shade(col, -0.35), 1.6, 0.7))
        u += dh
        row += 1
    # gutter along the left side
    cv.drawRect(skia.Rect.MakeLTRB(-HALF * 100, 40, -HALF * 100 + 22, ZWALL * 100), fill("#6e604f"))
    cv.drawLine(-HALF * 100 + 22, 40, -HALF * 100 + 22, ZWALL * 100, stroke("#4a3e33", 1.4))
    # dust/ruts in the middle
    cv.drawPath(K.rrect(-60, 40, 120, 860, 50), K.lin_a((0, 40), (0, 900), [("#e7d6b6", 0.25), ("#e7d6b6", 0.05)]))
    cv.restore()


WALL_TOP_CM = -360


def peeling_wall(cv, a0, a1, top, seed=77, line_w=0.8, flakes=1.0):
    """Peeling blue paint wall in elevation coords (cm; v negative up, 0 = floor). Shared with wall.py."""
    wall = K.rrect(a0, top, a1 - a0, -top, 0)
    cv.drawPath(wall, K.lin((0, top), (0, 0), ["#4a86c4", "wall_blue", "wall_blue_dark"]))
    rng = K.rng(seed)
    w = a1 - a0
    # big exposed patches: plaster with brick showing through
    for _ in range(int(4 * flakes)):
        x, y = rng.uniform(a0 + 0.12 * w, a1 - 0.12 * w), rng.uniform(top * 0.8, top * 0.15)
        rx, ry = rng.uniform(0.09, 0.16) * w, rng.uniform(0.05, 0.09) * w
        pts = [(x + math.cos(a) * rx * rng.uniform(0.6, 1.1), y + math.sin(a) * ry * rng.uniform(0.6, 1.1))
               for a in np.linspace(0, 6.28, 10)[:-1]]
        patch = smooth_path(pts, tension=0.4)
        cv.drawPath(patch, fill("#c7b897", 0.92))
        cv.save(); cv.clipPath(patch, doAntiAlias=True)
        bh = max(4.0, w * 0.018)
        for row in range(-20, 20):
            yy = y + row * bh
            off = (row % 2) * bh
            for col in range(-20, 20):
                xx = x + col * bh * 2.2 + off
                d = math.hypot((xx - x) / rx, (yy - y) / ry)
                if d < 0.62 and rng.random() < 0.8:
                    cv.drawPath(K.rrect(xx, yy, bh * 2.0, bh * 0.85, bh * 0.2),
                                fill(K.mix("brick", "#d9c4a0", 0.25 + rng.uniform(0, 0.25))))
        cv.restore()
        cv.drawPath(patch, stroke("#24476f", line_w * 1.2))
        # curled paint lip highlight
        cv.drawPath(patch, stroke("#7fb0e0", line_w * 0.8, 0.35))
    # small flakes and hairline cracks
    for _ in range(int(26 * flakes)):
        x, y = rng.uniform(a0 + 4, a1 - 4), rng.uniform(top + 6, -6)
        r = rng.uniform(0.004, 0.012) * w
        pts = [(x + math.cos(a) * r * rng.uniform(0.5, 1.2), y + math.sin(a) * r * rng.uniform(0.5, 1.0))
               for a in np.linspace(0, 6.28, 6)[:-1]]
        cv.drawPath(poly(pts), fill("#c9b48f", 0.9))
    for _ in range(int(9 * flakes)):
        x, y = rng.uniform(a0 + 10, a1 - 10), rng.uniform(top + 10, -20)
        pts = [(x, y)]
        for k in range(5):
            x += rng.uniform(-0.03, 0.03) * w; y += rng.uniform(0.01, 0.04) * w
            pts.append((x, y))
        cv.drawPath(poly(pts, close=False), stroke("#22406a", line_w * 0.9, 0.7))
    # grime at the bottom, moss line
    cv.drawRect(skia.Rect.MakeLTRB(a0, top * 0.12, a1, 0), K.lin_a((0, top * 0.12), (0, 0), [("#1c3150", 0.0), ("#1c3150", 0.55)]))
    cv.drawRect(skia.Rect.MakeLTRB(a0, top, a1, top + max(6, -top * 0.04)), fill("#2a4f7e"))
    cv.drawPath(wall, stroke("line", line_w))


def _far_wall(cv, time="night"):
    # distant rooftops beyond the wall (next street), plane Z=13
    cv.save(); cv.concat(zplane_matrix(13.0))
    rng = K.rng(42)
    col = {"night": "#2a2f5c", "day": "#cdb894", "dawn": "#9a7fa0", "sunrise": "#c99a8f"}[time]
    x = -420.0
    while x < 420:
        w = rng.uniform(50, 120); h = rng.uniform(300, 620)
        if rng.random() < 0.3:
            x += w * 0.6
            continue
        cv.drawRect(skia.Rect.MakeLTRB(x, -h, x + w, 0), fill(col))
        for wy in range(int(-h + 40), -40, 70):
            if rng.random() < 0.4:
                cv.drawRect(skia.Rect.MakeLTRB(x + w * 0.3, wy, x + w * 0.45, wy + 22), fill(K.shade(col, -0.25)))
        if rng.random() < 0.35:
            cv.drawPath(smooth_path([(x + 8, -h), (x + w / 2, -h - 70), (x + w - 8, -h)], tension=0.5), fill(col))
        elif rng.random() < 0.5:
            cv.drawPath(K.rrect(x + w * 0.3, -h - 46, 36, 46, 8), fill(K.shade(col, -0.2)))
        x += w
    # a tree crown
    for (dx, dy, r) in ((-150, -560, 70), (-100, -600, 60), (-60, -560, 55)):
        cv.drawCircle(dx, dy, r, fill(K.shade(col, -0.15) if time != "day" else "#8aa86a"))
    cv.restore()
    cv.save()
    cv.concat(zplane_matrix(ZWALL))
    peeling_wall(cv, -HALF * 100, HALF * 100, WALL_TOP_CM)
    cv.restore()


def _wires(cv, t=0.0, near_alpha=1.0):
    rng = K.rng(31)
    for i in range(14):
        z0 = rng.uniform(1.6, 8.6)
        z1 = z0 + rng.uniform(-1.4, 1.6)
        y0 = FLOOR - rng.uniform(3.6, 5.2)
        y1 = FLOOR - rng.uniform(3.6, 5.2)
        sag = rng.uniform(0.3, 0.9)
        A = (-HALF, y0, z0); B = (HALF, y1, max(1.5, z1))
        pts = []
        for s in np.linspace(0, 1, 24):
            X = lerp(A[0], B[0], s); Y = lerp(A[1], B[1], s) + sag * 4 * s * (1 - s); Z = lerp(A[2], B[2], s)
            pts.append(project(X, Y, Z))
        zm = (A[2] + B[2]) / 2
        cv.drawPath(poly(pts, close=False), stroke("#141018", clamp(5.0 / zm, 0.8, 3.2), 0.95 * near_alpha))
    # long wires running down the lane
    for i in range(5):
        x = rng.uniform(-1.4, 1.4); y = FLOOR - rng.uniform(3.9, 4.8)
        pts = []
        for s in np.linspace(0, 1, 30):
            Z = lerp(1.25, ZWALL, s)
            pts.append(project(x, y + 0.25 * math.sin(s * 9 + i), Z))
        cv.drawPath(poly(pts, close=False), stroke("#141018", 1.6, 0.9))
    # a lost kite caught on a wire + a bundle knot
    kx, ky = project(0.5, FLOOR - 4.3, 5.2)
    kite = poly([(kx, ky - 16), (kx + 13, ky), (kx, ky + 18), (kx - 13, ky)])
    cv.drawPath(kite, fill("#e2463f")); cv.drawPath(kite, stroke("line", 1.4))
    cv.drawLine(kx, ky - 16, kx, ky + 18, stroke("#ffd23f", 1.2))
    cv.drawPath(smooth_path([(kx, ky + 18), (kx + 6, ky + 34), (kx - 4, ky + 52), (kx + 3, ky + 66)], close=False),
                stroke("#ffd23f", 1.2))


# ------------------------------------------------------------------ sky
def _sky(cv, time, w=W):
    if time == "night":
        cv.drawRect(skia.Rect.MakeWH(w, H), K.lin((0, 0), (0, 600), ["night_sky_top", "night_sky_mid", "night_sky_low"]))
        K.stars(cv, w, 500, 2.0, n=int(160 * w / W), seed=9)
        mx, my = 1180, 70
        cv.drawCircle(mx, my, 160, K.rad_a((mx, my), 160, [("moonglow", 0.35), ("moonglow", 0)]))
        cv.drawCircle(mx, my, 34, fill("moon"))
        cv.drawCircle(mx - 9, my - 6, 7, fill("#e6dcb8"))
        cv.drawCircle(mx + 10, my + 9, 5, fill("#e6dcb8"))
    elif time == "day":
        cv.drawRect(skia.Rect.MakeWH(w, H), K.lin((0, 0), (0, 600), ["#f7f1e0", "#f4e3c0", "#efd2a0"]))
        cv.drawCircle(760, 40, 300, K.rad_a((760, 40), 300, [("#ffffff", 0.9), ("#fff3d0", 0.3), ("#fff3d0", 0)]))
    else:  # dawn / sunrise
        sun = time == "sunrise"
        cv.drawRect(skia.Rect.MakeWH(w, H), K.lin((0, 0), (0, 620),
                    ["#6f7fb8", "#d99aa6", "#ffc98f"] if not sun else ["#8fa2d0", "#f3b0a0", "#ffdca0"]))
        cv.drawCircle(960, 300, 420, K.rad_a((960, 300), 420, [("#fff1c8", 0.55 if sun else 0.3), ("#ffd8a0", 0)]))


# ------------------------------------------------------------------ lighting per time
def _night_light(cv):
    # right facade (moon from upper left) in deeper shade; moon catches upper left facades
    pts_r = [project(HALF, FLOOR - 7, 1.0), project(HALF, FLOOR - 7, ZWALL), project(HALF, FLOOR, ZWALL), project(HALF, FLOOR, 1.0)]
    cv.drawPath(poly(pts_r), fill("#05061a", 0.45))
    # moonlight on the upper left facades, fading softly downward
    for k in range(10):
        y0 = FLOOR - 7 + k * 0.5
        y1 = y0 + 0.5
        a = 0.30 * (1 - k / 10) ** 1.5
        pts = [project(-HALF, y0, 1.1), project(-HALF, y0, ZWALL), project(-HALF, y1, ZWALL), project(-HALF, y1, 1.1)]
        p = fill("#b9ccff", a); p.setBlendMode(skia.BlendMode.kScreen)
        cv.drawPath(poly(pts), p)
    # moon stripe across the floor in the middle distance
    stripe = [project(-HALF, FLOOR, 5.0), project(HALF, FLOOR, 4.3), project(HALF, FLOOR, 5.6), project(-HALF, FLOOR, 6.4)]
    p2 = fill("#9fb6ff", 0.16); p2.setBlendMode(skia.BlendMode.kScreen)
    cv.drawPath(poly(stripe), p2)
    # darkness pooling low and near
    cv.drawRect(skia.Rect.MakeWH(W, H), K.lin_a((0, 540), (0, H), [("#04030e", 0.0), ("#04030e", 0.6)]))
    # moonlight kissing the far wall: it is the brightest thing in the lane
    l, tp, r, b = WALL_RECT
    wp = skia.Paint(Shader=skia.GradientShader.MakeRadial(skia.Point((l + r) / 2, tp + 30), (r - l) * 1.1,
                    [C("#c9d8ff", 0.35), C("#c9d8ff", 0.0)]), AntiAlias=True)
    wp.setBlendMode(skia.BlendMode.kScreen)
    cv.drawRect(skia.Rect.MakeLTRB(l - 80, tp - 120, r + 80, b + 40), wp)


def _day_light(cv):
    # sun high from the left: left facades in shadow low down, right facades blazing; floor shadow diagonal
    pts_l = [project(-HALF, FLOOR - 7, 1.0), project(-HALF, FLOOR - 7, ZWALL), project(-HALF, FLOOR, ZWALL), project(-HALF, FLOOR, 1.0)]
    sh = fill("#7b4f3a", 0.30); sh.setBlendMode(skia.BlendMode.kMultiply)
    cv.drawPath(poly(pts_l), sh)
    # cast shadow of the left houses onto the floor and up the lower right wall
    shadow = [project(-HALF, FLOOR, 1.0), project(-HALF, FLOOR, ZWALL), project(0.2, FLOOR, ZWALL), project(0.6, FLOOR, 1.0)]
    sh2 = fill("#7b4f3a", 0.35); sh2.setBlendMode(skia.BlendMode.kMultiply)
    cv.drawPath(poly(shadow), sh2)
    glare = fill("#fff6dc", 0.18); glare.setBlendMode(skia.BlendMode.kScreen)
    pts_r = [project(HALF, FLOOR - 7, 1.0), project(HALF, FLOOR - 7, ZWALL), project(HALF, FLOOR - 1.0, ZWALL), project(HALF, FLOOR - 0.6, 1.0)]
    cv.drawPath(poly(pts_r), glare)
    cv.drawRect(skia.Rect.MakeWH(W, H), K.lin_a((0, 0), (0, 500), [("#fff2c8", 0.18), ("#fff2c8", 0.0)]))


def _dawn_light(cv, sun=False):
    a = 0.55 if sun else 0.4
    # soft pink-gold raking light on upper facades, long cool shadows below
    for side in (-1, 1):
        X = side * HALF
        pts = [project(X, FLOOR - 7, 1.0), project(X, FLOOR - 7, ZWALL), project(X, FLOOR - 3.6, ZWALL), project(X, FLOOR - 2.4, 1.0)]
        p = fill("#ffc58a", a * (0.9 if side < 0 else 0.6)); p.setBlendMode(skia.BlendMode.kScreen)
        cv.drawPath(poly(pts), p)
    sh = K.lin_a((0, 420), (0, H), [("#5a4a8a", 0.0), ("#5a4a8a", 0.4)]); sh.setBlendMode(skia.BlendMode.kMultiply)
    cv.drawRect(skia.Rect.MakeLTRB(0, 420, W, H), sh)
    # sunlight streaming down the lane from the far end
    streak = [project(-0.5, FLOOR, ZWALL), project(0.5, FLOOR, ZWALL), project(1.2, FLOOR, 1.3), project(-1.2, FLOOR, 1.3)]
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, 600), skia.Point(0, H)],
                   [C("#ffd9a0", 0.45 if sun else 0.3), C("#ffd9a0", 0.0)]), AntiAlias=True)
    p.setBlendMode(skia.BlendMode.kScreen)
    cv.drawPath(poly(streak), p)


GRADE = {"night": ("night", 1.0), "day": ("day", 1.0), "dawn": ("dawn", 1.0), "sunrise": ("dawn", 0.6)}


def _static_gali(c: skia.Canvas, time: str, rickshaw: bool):
    _sky(c, time)
    light, amt = GRADE[time]
    with K.lit(c, light, amt):
        _far_wall(c, time)
        _floor(c)
        _facades(c, -1)
        _facades(c, 1)
        if rickshaw:
            c.save(); c.concat(rickshaw_matrix())
            from ..rig.animals import draw_rickshaw
            draw_rickshaw(c, 0, 0, 1.0)
            c.restore()
    {"night": _night_light, "day": _day_light, "dawn": lambda cc: _dawn_light(cc, False),
     "sunrise": lambda cc: _dawn_light(cc, True)}[time](c)
    with K.lit(c, light, amt * 0.6):
        _wires(c)


STATIC["gali"] = _static_gali


# ------------------------------------------------------------------ dynamic
def _wall_cracks(cv, amount, t):
    """Gold cracks on the far wall (subset of the wall.py doorway outline)."""
    l, tp, r, b = WALL_RECT
    w, h = r - l, b - tp
    cx = (l + r) / 2
    pts = [(cx - w * 0.22, b), (cx - w * 0.24, b - h * 0.45), (cx - w * 0.17, b - h * 0.68), (cx, b - h * 0.78),
           (cx + w * 0.17, b - h * 0.68), (cx + w * 0.24, b - h * 0.45), (cx + w * 0.22, b)]
    n = len(pts) - 1
    shown = amount * n
    def draw(c):
        for i in range(n):
            f = clamp(shown - i)
            if f <= 0:
                break
            a, bb = pts[i], pts[i + 1]
            c.drawLine(a[0], a[1], lerp(a[0], bb[0], f), lerp(a[1], bb[1], f), stroke("gold", 2.4))
    draw(cv)
    bloom(cv, draw, radius=20, strength=1.0)
    cv.drawCircle(cx, b - h * 0.4, w * 0.9, K.rad_a((cx, b - h * 0.4), w * 0.9, [("saffron", 0.25 * amount), ("saffron", 0)]))


def _syrup_layer(cv, t, level, side_mode=False, ground_y=None):
    if level <= 0.001:
        return
    lv = clamp(level)
    if not side_mode:
        Ysurf = FLOOR - 0.3 * lv
        # surface polygon of the flooded lane
        near_z = 1.05
        pts = [project(-HALF, Ysurf, near_z), project(-HALF, Ysurf, ZWALL), project(HALF, Ysurf, ZWALL), project(HALF, Ysurf, near_z)]
        bot = [project(HALF, FLOOR, near_z), project(-HALF, FLOOR, near_z)]
        surf = poly(pts + bot)
        cv.drawPath(surf, K.lin((0, VPY + 40), (0, H), [("#c97a12"), ("#e59a2a"), ("#ffb444")]))
        cv.drawPath(surf, fill("#ffcf6e", 0.18 + 0.1 * math.sin(t)))
        # wall line: syrup climbing the facades
        for X in (-HALF, HALF):
            band = [project(X, Ysurf, 1.0), project(X, Ysurf, ZWALL), project(X, FLOOR, ZWALL), project(X, FLOOR, 1.0)]
            cv.drawPath(poly(band), fill("#d0821a", 0.92))
            cv.drawPath(poly([project(X, Ysurf, 1.0), project(X, Ysurf, ZWALL)], close=False), stroke("#ffe2a0", 2.5, 0.8))
        # glossy ripples (rows receding)
        rng = K.rng(3)
        for i in range(36):
            z = 1.2 + (i * 0.23 + t * 0.35) % 7.8
            a = rng.uniform(-1.4, 1.4) + 0.2 * math.sin(t * 0.7 + i)
            wd = rng.uniform(0.25, 0.6)
            p0 = project(a - wd, Ysurf, z); p1 = project(a + wd, Ysurf, z)
            al = 0.55 * (1 - abs(((i * 0.23 + t * 0.35) % 7.8) / 7.8 - 0.5) * 1.6)
            cv.drawPath(smooth_path([p0, ((p0[0] + p1[0]) / 2, p0[1] - 2), p1], close=False),
                        stroke("#fff1c2", clamp(5 / z, 0.8, 4), clamp(al)))
        # sun/moon highlight streak
        hl = [project(-0.3, Ysurf, 2.0), project(0.3, Ysurf, 2.0), project(0.1, Ysurf, 8.5), project(-0.1, Ysurf, 8.5)]
        hp = fill("#fff6d8", 0.25); hp.setBlendMode(skia.BlendMode.kScreen)
        cv.drawPath(poly(hl), hp)
        # floating slipper drifting toward camera
        z = 7.5 - (t * 0.45) % 6.0
        sx, sy = project(0.4 + 0.2 * math.sin(t * 0.8), Ysurf, z)
        sc = 3.5 / z
        cv.save(); cv.translate(sx, sy); cv.scale(sc, sc * 0.55); cv.rotate(20 * math.sin(t * 0.9))
        sl = K.rrect(-26, -10, 52, 20, 10)
        cv.drawPath(sl, fill("#3a74c8")); cv.drawPath(sl, stroke("line", 2))
        cv.drawPath(K.rrect(-4, -11, 8, 22, 3), fill("#ffd23f"))
        cv.restore()
        # drips/gushes from drainpipes
        for (X, Z) in ((-HALF + 0.03, 2.5), (-HALF + 0.03, 4.7), (HALF - 0.03, 4.2), (HALF - 0.03, 6.4)):
            x0, y0 = project(X, FLOOR - 0.15, Z)
            x1, y1 = project(X, Ysurf, Z)
            wv = 1.5 * math.sin(t * 6 + Z)
            cv.drawPath(K.rrect(x0 - 6 / Z * 3 + wv, y0 - 60 / Z, 12 / Z * 3, max(2, y1 - y0 + 60 / Z), 4), fill("#f0a838", 0.85 * lv))
    else:
        gy = ground_y
        top = gy - 160 * lv
        cv.drawRect(skia.Rect.MakeLTRB(0, top, W, H), K.lin((0, top), (0, H), ["#ffc256", "#e8952a", "#b86a10"]))
        for i in range(30):
            x = (i * 97 + t * 40) % (W + 200) - 100
            y = top + 6 + (i % 5) * 26
            cv.drawPath(smooth_path([(x, y), (x + 40, y - 3), (x + 80, y)], close=False), stroke("#fff1c2", 2.4, 0.6))
        cv.drawLine(0, top, W, top, stroke("#fff1c2", 3, 0.8))


def _motes(cv, t, time, n=40, seed=8):
    rng = K.rng(seed)
    col = {"night": "#c8d4ff", "day": "#fff3d0", "dawn": "#ffe0b0", "sunrise": "#ffe0b0"}[time]
    for i in range(n):
        x0, y0 = rng.uniform(0, W), rng.uniform(0, H)
        sp = rng.uniform(4, 16)
        x = (x0 + math.sin(t * 0.3 + i) * 40 + t * sp) % W
        y = (y0 - t * sp * 0.6) % H
        a = 0.25 + 0.25 * math.sin(t * 1.3 + i)
        cv.drawCircle(x, y, rng.uniform(1.0, 2.6), fill(col, a))


def _heat_haze(cv, t):
    # shimmering bands near the far end (cheap: translucent warped strokes)
    for i in range(10):
        y = 470 + i * 14
        pts = [(x, y + 3 * math.sin(x * 0.03 + t * 3 + i)) for x in range(700, 1240, 30)]
        cv.drawPath(poly(pts, close=False), stroke("#fff6e0", 3, 0.06))


def draw_gali(cv, t, time="night", syrup=0.0, rickshaw=True, wall_glow=0.0, cam=None):
    apply_cam(cv, cam)
    cached(cv, "gali", time, bool(rickshaw), cam=cam)
    if wall_glow > 0:
        _wall_cracks(cv, wall_glow, t)
    _syrup_layer(cv, t, syrup)
    if time == "day":
        _heat_haze(cv, t)
    _motes(cv, t, time, n=30)
    cv.restore()


# ------------------------------------------------------------------ side elevation (lateral tracking)
GROUND_Y_SIDE = 930
TILE_W = 2400


def _static_side(c: skia.Canvas, time: str):
    for k in range(2):
        c.save(); c.translate(k * TILE_W, 0)
        c.clipRect(skia.Rect.MakeWH(TILE_W, H))
        _sky(c, "night" if time == "night" else "day", TILE_W)
        c.restore()
    light, amt = GRADE[time]
    with K.lit(c, light, amt):
        # far background: rooftops of the next street, soft
        rng = K.rng(66)
        x = -40
        while x < TILE_W * 2:
            w = rng.uniform(160, 300); h = rng.uniform(180, 320)
            c.drawRect(skia.Rect.MakeLTRB(x, 300 - h + 200, x + w, 600), fill(K.shade("#b9a58a", -0.25)))
            x += w
        # house row: two identical tiles so scrolling wraps seamlessly
        for k in range(2):
            c.save(); c.translate(k * TILE_W, GROUND_Y_SIDE); c.scale(1.12, 1.12)
            rng = K.rng(101)
            u = 0
            cols = ["whitewash", "ochre", "pink", "bluewash", "sandstone", "mint", "lilac", "ochre"]
            i = 0
            while u < TILE_W / 1.12 - 10:
                w = min(rng.uniform(250, 360), TILE_W / 1.12 - u)
                jh = _house(c, u, u + w, -rng.uniform(560, 700), cols[i % len(cols)], rng, 1)
                if jh:
                    _jharokha(c, jh[0], jh[1], 120, 110, "#7a4a2a")
                u += w; i += 1
            c.restore()
        # pavement / lane strip
        c.drawRect(skia.Rect.MakeLTRB(0, GROUND_Y_SIDE, TILE_W * 2, H), K.lin((0, GROUND_Y_SIDE), (0, H), ["#a8957a", "#c7b393"]))
        for k in range(0, TILE_W * 2, 60):
            c.drawLine(k, GROUND_Y_SIDE + 6, k + 30, H, stroke("#8c7a62", 1.4, 0.6))
        # wires along the street
        for j in range(4):
            pts = []
            for x in range(0, TILE_W * 2 + 1, 40):
                ph = (x % 600) / 600
                pts.append((x, 180 + j * 26 + 40 * math.sin(ph * math.pi)))
            c.drawPath(poly(pts, close=False), stroke("#141018", 2.2, 0.9))
    if time == "night":
        c.drawRect(skia.Rect.MakeWH(TILE_W * 2, H), K.lin_a((0, 400), (0, H), [("#04030e", 0.0), ("#04030e", 0.4)]))
        p = fill("#a9bfff", 0.12); p.setBlendMode(skia.BlendMode.kScreen)
        c.drawRect(skia.Rect.MakeLTRB(0, 0, TILE_W * 2, 420), p)
    else:
        sh = fill("#7b4f3a", 0.25); sh.setBlendMode(skia.BlendMode.kMultiply)
        c.drawRect(skia.Rect.MakeLTRB(0, GROUND_Y_SIDE - 140, TILE_W * 2, GROUND_Y_SIDE + 40), sh)


STATIC["side"] = _static_side


@lru_cache(maxsize=4)
def _side_img(time):
    surf = skia.Surface(TILE_W * 2, H)
    c = surf.getCanvas()
    _static_side(c, time)
    return surf.makeImageSnapshot()


def draw_gali_side(cv, t, time="night", scroll=0.0, syrup=0.0):
    img = _side_img(time)
    off = scroll % TILE_W
    cv.drawImageRect(img, skia.Rect.MakeXYWH(off, 0, W, H), skia.Rect.MakeWH(W, H),
                     skia.SamplingOptions(skia.FilterMode.kLinear), None)
    _syrup_layer(cv, t, syrup, side_mode=True, ground_y=GROUND_Y_SIDE)
    _motes(cv, t, time, n=24, seed=4)
