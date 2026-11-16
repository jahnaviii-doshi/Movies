"""Drawing toolkit on top of skia: colour, paths, gradients, glow, lighting, camera, texture.

Conventions
- Frame is 1920x1080. World units = pixels unless a set says otherwise.
- Rigs draw in local units with origin at the feet, y up = negative.
- All randomness is seeded (deterministic renders; frames can render in any order).
"""
from __future__ import annotations

import math
import random
from contextlib import contextmanager
from functools import lru_cache

import numpy as np
import skia

W, H = 1920, 1080

# ------------------------------------------------------------------ palette (style bible)
PAL = {
    # night
    "night_sky_top": "#0b0d2a", "night_sky_mid": "#1a1f4f", "night_sky_low": "#2b3470",
    "indigo": "#1c2152", "blue_black": "#0a0b1c", "moon": "#f6efd2", "moonglow": "#c9d4ff",
    # sweets glow
    "saffron": "#ffb02e", "rose": "#ff6fa5", "pistachio": "#9bdc6b", "silver": "#eef2ff", "violet": "#b67cff",
    "gold": "#ffd36b", "ghee": "#ffe7a8",
    # day
    "ochre": "#d9a35b", "dust": "#e8c99a", "whitewash": "#f3eadb", "day_sky": "#f4e3c0", "shadow_day": "#9b6b4a",
    # dawn
    "dawn_pink": "#f6a9a0", "dawn_gold": "#ffd8a0", "dawn_blue": "#7d8fc4",
    # architecture
    "wall_blue": "#3d78b8", "wall_blue_dark": "#2a5486", "wood": "#7a4a2a", "wood_dark": "#4e2c18",
    "brick": "#b0603f", "plaster": "#e5d3b3", "plaster_dark": "#bfa27a",
    # characters
    "skin": "#c98a5e", "skin_shadow": "#a96c46", "skin_light": "#dca27a", "blush": "#e37f6a",
    "hair": "#1d1418", "hair_white": "#f2eee8", "line": "#2a1a1c",
    "mustard": "#e3a72f", "mustard_dark": "#b97f1a", "teal": "#2f8f8a", "ribbon": "#d8333d",
    "cap_red": "#d23a35", "tee_blue": "#3a6fd8", "bolt": "#ffd23f", "khaki": "#b59b6a", "sneaker": "#f2f2f2",
    "sari": "#f5f0f7", "sari_border": "#8e6cc9", "bangle": "#d9dde6",
    "shawl": "#f7b8cf", "shawl_light": "#ffe0ec", "amma_spec": "#d8a840",
    "dog_ochre": "#d8994a", "dog_white": "#f6eadb", "dog_dark": "#6a4426",
    "brass": "#d8a837", "brass_light": "#ffe28a", "brass_dark": "#8a5f17",
}


def hexrgb(h: str) -> tuple[float, float, float]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def C(c, a: float = 1.0) -> int:
    """Colour from '#hex', palette key, or (r,g,b) floats -> skia int colour."""
    if isinstance(c, str):
        c = hexrgb(PAL.get(c, c))
    r, g, b = c[:3]
    return skia.Color4f(r, g, b, a).toColor()


def mix(c1, c2, t: float):
    a = hexrgb(PAL.get(c1, c1)) if isinstance(c1, str) else c1
    b = hexrgb(PAL.get(c2, c2)) if isinstance(c2, str) else c2
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def shade(c, k: float):
    """k<0 darker, k>0 lighter."""
    a = hexrgb(PAL.get(c, c)) if isinstance(c, str) else c
    return mix(a, (0, 0, 0), -k) if k < 0 else mix(a, (1, 1, 1), k)


# ------------------------------------------------------------------ math & easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_in_out(t):
    t = clamp(t)
    return 0.5 - 0.5 * math.cos(math.pi * t)


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = clamp(t)
    return t ** 3


def ease_out_back(t, s=1.6):
    t = clamp(t) - 1
    return t * t * ((s + 1) * t + s) + 1


def ease_out_elastic(t):
    t = clamp(t)
    if t in (0, 1):
        return t
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi) / 3) + 1


def seg(t, a, b):
    return 0.0 if t <= a else 1.0 if t >= b else (t - a) / (b - a)


def noise1(x: float, seed: int = 0) -> float:
    """Smooth value noise in [-1,1]."""
    i = math.floor(x)
    f = x - i
    def h(n):
        return random.Random(n * 7919 + seed * 104729).uniform(-1, 1)
    return lerp(h(i), h(i + 1), f * f * (3 - 2 * f))


def wobble(t, speed=1.0, seed=0):
    return noise1(t * speed, seed)


# ------------------------------------------------------------------ paints
def fill(c, a=1.0, aa=True) -> skia.Paint:
    return skia.Paint(Color=C(c, a), AntiAlias=aa, Style=skia.Paint.kFill_Style)


def stroke(c, w=3.0, a=1.0, cap="round") -> skia.Paint:
    p = skia.Paint(Color=C(c, a), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w)
    p.setStrokeCap({"round": skia.Paint.kRound_Cap, "butt": skia.Paint.kButt_Cap, "square": skia.Paint.kSquare_Cap}[cap])
    p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def lin(p0, p1, colors, pos=None, a=1.0) -> skia.Paint:
    sh = skia.GradientShader.MakeLinear([skia.Point(*p0), skia.Point(*p1)], [C(c, a) for c in colors], pos)
    return skia.Paint(Shader=sh, AntiAlias=True)


def rad(center, r, colors, pos=None, a=1.0) -> skia.Paint:
    sh = skia.GradientShader.MakeRadial(skia.Point(*center), max(r, 0.01), [C(c, a) for c in colors], pos)
    return skia.Paint(Shader=sh, AntiAlias=True)


def rgba_list(colors_alpha):
    """[(colour, alpha), ...] for gradients that fade out."""
    return [C(c, a) for c, a in colors_alpha]


def rad_a(center, r, colors_alpha, pos=None) -> skia.Paint:
    sh = skia.GradientShader.MakeRadial(skia.Point(*center), max(r, 0.01), rgba_list(colors_alpha), pos)
    return skia.Paint(Shader=sh, AntiAlias=True)


def lin_a(p0, p1, colors_alpha, pos=None) -> skia.Paint:
    sh = skia.GradientShader.MakeLinear([skia.Point(*p0), skia.Point(*p1)], rgba_list(colors_alpha), pos)
    return skia.Paint(Shader=sh, AntiAlias=True)


# ------------------------------------------------------------------ paths
def poly(pts, close=True) -> skia.Path:
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    return p


def smooth_path(pts, close=True, tension=0.5) -> skia.Path:
    """Catmull-Rom through points -> cubic beziers."""
    n = len(pts)
    p = skia.Path()
    p.moveTo(*pts[0])
    rng = range(n) if close else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (close or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (close or i + 2 < n) else p2
        k = tension / 3 * 2
        c1 = (p1[0] + (p2[0] - p0[0]) * k / 2, p1[1] + (p2[1] - p0[1]) * k / 2)
        c2 = (p2[0] - (p3[0] - p1[0]) * k / 2, p2[1] - (p3[1] - p1[1]) * k / 2)
        p.cubicTo(*c1, *c2, *p2)
    if close:
        p.close()
    return p


def ellipse(cx, cy, rx, ry) -> skia.Path:
    p = skia.Path()
    p.addOval(skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry))
    return p


def rrect(x, y, w, h, r) -> skia.Path:
    p = skia.Path()
    p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r))
    return p


def limb(x0, y0, x1, y1, w0, w1) -> skia.Path:
    """Tapered capsule from (x0,y0) width w0 to (x1,y1) width w1."""
    ang = math.atan2(y1 - y0, x1 - x0)
    nx, ny = -math.sin(ang), math.cos(ang)
    p = skia.Path()
    p.moveTo(x0 + nx * w0 / 2, y0 + ny * w0 / 2)
    p.lineTo(x1 + nx * w1 / 2, y1 + ny * w1 / 2)
    p.arcTo(skia.Rect.MakeLTRB(x1 - w1 / 2, y1 - w1 / 2, x1 + w1 / 2, y1 + w1 / 2),
            math.degrees(ang) + 90, -180, False)
    p.lineTo(x0 - nx * w0 / 2, y0 - ny * w0 / 2)
    p.arcTo(skia.Rect.MakeLTRB(x0 - w0 / 2, y0 - w0 / 2, x0 + w0 / 2, y0 + w0 / 2),
            math.degrees(ang) - 90, -180, False)
    p.close()
    return p


def draw_shape(cv: skia.Canvas, path: skia.Path, color, line="line", lw=3.0, a=1.0, paint=None):
    cv.drawPath(path, paint or fill(color, a))
    if line and lw > 0:
        cv.drawPath(path, stroke(line, lw, a))


# ------------------------------------------------------------------ layers, glow, lighting
@contextmanager
def layer(cv: skia.Canvas, alpha=1.0, color_filter=None, image_filter=None, blend=None):
    paint = skia.Paint()
    paint.setAlphaf(clamp(alpha))
    if color_filter is not None:
        paint.setColorFilter(color_filter)
    if image_filter is not None:
        paint.setImageFilter(image_filter)
    if blend is not None:
        paint.setBlendMode(blend)
    cv.saveLayer(None, paint)
    try:
        yield cv
    finally:
        cv.restore()


@contextmanager
def glow(cv: skia.Canvas, radius=18.0, strength=1.0):
    """Draw contents twice: blurred additive halo + crisp."""
    yield_list = []
    paint = skia.Paint()
    paint.setImageFilter(skia.ImageFilters.Blur(radius, radius))
    paint.setBlendMode(skia.BlendMode.kPlus)
    paint.setAlphaf(clamp(strength))
    rec = skia.PictureRecorder()
    rc = rec.beginRecording(skia.Rect.MakeWH(W * 4, H * 4))
    rc.setMatrix(cv.getTotalMatrix())
    yield rc
    pic = rec.finishRecordingAsPicture()
    cv.save()
    cv.resetMatrix()
    cv.saveLayer(None, paint)
    cv.drawPicture(pic)
    cv.restore()
    cv.drawPicture(pic)
    cv.restore()


def blur_filter(r):
    return skia.ImageFilters.Blur(r, r)


def matrix_filter(m):
    return skia.ColorFilters.Matrix(m)


LIGHTS = {
    # r,g,b multipliers, r,g,b lift, saturation
    "day": ((1.03, 1.0, 0.95), (0.02, 0.01, 0.0), 1.0),
    "dusk": ((1.0, 0.78, 0.62), (0.05, 0.02, 0.03), 1.0),
    "night": ((0.50, 0.56, 0.86), (0.02, 0.03, 0.08), 0.75),
    "moon": ((0.62, 0.68, 0.95), (0.03, 0.04, 0.09), 0.8),
    "shop": ((1.05, 0.92, 0.74), (0.04, 0.02, 0.0), 1.08),
    "dawn": ((1.0, 0.84, 0.82), (0.05, 0.03, 0.05), 0.95),
    "memory": ((1.0, 0.86, 0.66), (0.08, 0.05, 0.02), 0.25),
    "dim": ((0.42, 0.42, 0.55), (0.01, 0.01, 0.03), 0.4),
    "neutral": ((1, 1, 1), (0, 0, 0), 1.0),
}


def light_matrix(name_or_spec, amount=1.0, desat=0.0):
    if isinstance(name_or_spec, str):
        mul, lift, sat = LIGHTS[name_or_spec]
    else:
        mul, lift, sat = name_or_spec
    sat = lerp(1.0, sat, amount) * (1 - desat)
    mul = [lerp(1.0, m, amount) for m in mul]
    lift = [l * amount for l in lift]
    lr, lg, lb = 0.2126, 0.7152, 0.0722
    s = sat
    sm = [
        lr * (1 - s) + s, lg * (1 - s), lb * (1 - s),
        lr * (1 - s), lg * (1 - s) + s, lb * (1 - s),
        lr * (1 - s), lg * (1 - s), lb * (1 - s) + s,
    ]
    m = []
    for row in range(3):
        m += [sm[row * 3 + 0] * mul[row], sm[row * 3 + 1] * mul[row], sm[row * 3 + 2] * mul[row], 0, lift[row]]
    m += [0, 0, 0, 1, 0]
    return m


@contextmanager
def lit(cv, light="neutral", amount=1.0, alpha=1.0, desat=0.0):
    """Draw contents under a lighting grade (and optional translucency/desaturation)."""
    if light == "neutral" and alpha >= 1 and desat == 0:
        yield cv
        return
    with layer(cv, alpha=alpha, color_filter=matrix_filter(light_matrix(light, amount, desat))):
        yield cv


# ------------------------------------------------------------------ camera
@contextmanager
def camera(cv: skia.Canvas, cx=W / 2, cy=H / 2, zoom=1.0, rot=0.0, shake=0.0, t=0.0):
    """View centred on world point (cx,cy) at zoom."""
    cv.save()
    sx = shake * noise1(t * 23, 11) if shake else 0
    sy = shake * noise1(t * 23, 29) if shake else 0
    cv.translate(W / 2 + sx, H / 2 + sy)
    cv.scale(zoom, zoom)
    if rot:
        cv.rotate(rot)
    cv.translate(-cx, -cy)
    try:
        yield cv
    finally:
        cv.restore()


def cam_lerp(t, a: dict, b: dict, ease=ease_in_out):
    e = ease(t)
    return {k: lerp(a[k], b[k], e) for k in a}


# ------------------------------------------------------------------ images
def np_to_image(arr: np.ndarray) -> skia.Image:
    if arr.dtype != np.uint8:
        arr = np.clip(arr * 255, 0, 255).astype(np.uint8)
    if arr.shape[2] == 3:
        arr = np.dstack([arr, np.full(arr.shape[:2], 255, np.uint8)])
    return skia.Image.fromarray(np.ascontiguousarray(arr), colorType=skia.ColorType.kRGBA_8888_ColorType)


def render_to_image(w, h, draw_fn) -> skia.Image:
    surf = skia.Surface(int(w), int(h))
    cv = surf.getCanvas()
    cv.clear(skia.ColorTRANSPARENT)
    draw_fn(cv)
    return surf.makeImageSnapshot()


@lru_cache(maxsize=4)
def paper_grain(seed=3) -> skia.Image:
    """Full-resolution grain (built once per seed) so it can be drawn 1:1 (fast path)."""
    rng_ = np.random.default_rng(seed)
    n = rng_.normal(0.5, 0.11, (H // 2, W // 2))
    k = np.ones(5) / 5
    n = 0.6 * n + 0.4 * np.apply_along_axis(lambda r: np.convolve(r, k, "same"), 1, n)
    n = np.clip(n, 0, 1)
    n = np.repeat(np.repeat(n, 2, axis=0), 2, axis=1)       # nearest upscale to full res
    g = (n * 255).astype(np.uint8)
    rgba = np.dstack([g, g, g, np.full(g.shape, 255, np.uint8)])
    return skia.Image.fromarray(np.ascontiguousarray(rgba), colorType=skia.ColorType.kRGBA_8888_ColorType)


@lru_cache(maxsize=8)
def grain_srcover(seed: int, amount: float) -> skia.Image:
    """Grain as a premultiplied white/black alpha layer: approximates an overlay blend with a fast src-over."""
    arr = paper_grain(seed).toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)[:, :, 0].astype(np.float32) / 255
    d = (arr - 0.5) * 2 * amount * 2.2
    a = np.clip(np.abs(d), 0, 1)
    c = np.where(d > 0, a, 0)                     # premultiplied: white -> rgb=a, black -> rgb=0
    rgba = (np.dstack([c, c, c, a]) * 255).astype(np.uint8)
    return skia.Image.fromarray(np.ascontiguousarray(rgba), colorType=skia.ColorType.kRGBA_8888_ColorType,
                                alphaType=skia.AlphaType.kPremul_AlphaType)


@lru_cache(maxsize=8)
def vignette_img(strength: float) -> skia.Image:
    return render_to_image(W, H, lambda c: c.drawRect(skia.Rect.MakeWH(W, H), rad_a(
        (W / 2, H / 2), W * 0.72, [("#000000", 0), ("#000000", 0), ("#05030a", strength)], [0, 0.55, 1])))


def finish(cv: skia.Canvas, t: float, grain=0.10, vignette=0.45):
    """Storybook finishing pass: paper grain (overlay) + soft vignette. Applied by the renderer."""
    cv.save()
    cv.resetMatrix()
    dev = cv.getBaseLayerSize()
    full = dev.width() >= W
    if not full:
        cv.scale(dev.width() / W, dev.height() / H)
    if grain:
        cv.drawImage(grain_srcover(3 + (int(t * 12) % 3), round(grain, 3)), 0, 0)
    if vignette:
        cv.drawImage(vignette_img(round(vignette, 2)), 0, 0)
    cv.restore()


# ------------------------------------------------------------------ text
@lru_cache(maxsize=16)
def font(size: float, family="DejaVu Serif", bold=False, italic=False) -> skia.Font:
    style = skia.FontStyle(skia.FontStyle.kBold_Weight if bold else skia.FontStyle.kNormal_Weight,
                           skia.FontStyle.kNormal_Width,
                           skia.FontStyle.kItalic_Slant if italic else skia.FontStyle.kUpright_Slant)
    tf = skia.Typeface.MakeFromName(family, style)
    f = skia.Font(tf, size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    return f


def text_center(cv, s, x, y, size=72, color="#fff3d6", a=1.0, family="DejaVu Serif", bold=False, italic=False,
                shadow=True):
    f = font(size, family, bold, italic)
    w = f.measureText(s)
    if shadow:
        cv.drawString(s, x - w / 2 + 3, y + 4, f, fill("#000000", 0.45 * a))
    cv.drawString(s, x - w / 2, y, f, fill(color, a))
    return w


# ------------------------------------------------------------------ misc helpers
def rng(seed) -> random.Random:
    return random.Random(seed)


def stars(cv, w, h, t, n=260, seed=7, top=0, bottom=None, alpha=1.0):
    r = rng(seed)
    bottom = bottom if bottom is not None else h * 0.7
    for i in range(n):
        x, y = r.uniform(0, w), r.uniform(top, bottom)
        s = r.choice([0.8, 1.0, 1.2, 1.6, 2.2]) * (1.0 if r.random() < 0.9 else 1.8)
        tw = 0.55 + 0.45 * math.sin(t * r.uniform(0.6, 2.4) + r.uniform(0, 6.28))
        a = alpha * tw * (1 - 0.6 * (y - top) / max(1, bottom - top))
        if s > 2:
            cv.drawCircle(x, y, s * 3, rad_a((x, y), s * 3, [("#cfd8ff", 0.35 * a), ("#cfd8ff", 0)]))
        cv.drawCircle(x, y, s, fill("#f4f1ff", a))
