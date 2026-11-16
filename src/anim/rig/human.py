"""Parametric storybook humanoid rig.

Local coords: origin between the feet on the ground, y up is negative. A 9-year-old
is ~300 units tall at scale 1. Every character is drawn by the same code every frame,
so identity is perfectly consistent across the whole film.

Pose fields (all optional):
  x, y, s (scale), flip (face screen-left), turn (0 front .. 1 three-quarter),
  lean (deg), head_tilt (deg), look (dx,dy pupils -1..1), blink (0..1),
  expr: neutral happy grin laugh surprised awe sad worried cry determined smug angry sleepy
        shy wince (+ 'talk' handled by mouth),
  mouth (0..1 openness, from dialogue), brow (extra raise -1..1),
  arms: dict(l=(shoulder_deg, elbow_deg), r=(...)) — 0 = hanging down, + = raised outward/forward
  hand: dict(l='open'|'fist'|'point', r=...), legs: 'stand'|'walk'|'sit'|'float'|'tiptoe'|'kneel',
  phase (walk cycle 0..1), alpha, t (seconds, for idle breathing)
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import skia

from .. import core as K
from ..core import PAL, C, fill, stroke, limb, ellipse, smooth_path, poly, lerp, clamp


@dataclass
class Pose:
    x: float = 960
    y: float = 900
    s: float = 2.0
    flip: bool = False
    turn: float = 0.35
    lean: float = 0.0
    head_tilt: float = 0.0
    look: tuple = (0.0, 0.0)
    blink: float = 0.0
    expr: str = "neutral"
    mouth: float = 0.0
    brow: float = 0.0
    arms: dict = field(default_factory=dict)
    hand: dict = field(default_factory=dict)
    legs: str = "stand"
    phase: float = 0.0
    alpha: float = 1.0
    t: float = 0.0
    breathe: float = 1.0
    hold: str | None = None        # prop in right hand: 'bottle','torch','book','laddoo','toffee','kulfi','jar','lota','slippers','fan','cap'
    hold_l: str | None = None
    extra: dict = field(default_factory=dict)


def auto_blink(t: float, seed: int = 0) -> float:
    """Natural blink every ~3-5 s."""
    period = 3.2 + (seed % 5) * 0.37
    ph = (t + seed * 0.71) % period
    return clamp(1 - abs(ph - 0.08) / 0.08) if ph < 0.16 else 0.0


class Human:
    # proportions (units)
    height = 300
    head_r = 56
    neck_y = -198
    shoulder_w = 30
    hip_y = -112
    hem_y = -72
    hem_w = 58
    body_top_w = 34
    upper_arm = 50
    fore_arm = 46
    leg_w = 15
    thigh = 58
    shin = 50
    skin = "skin"
    line_w = 3.2
    stoop = 0.0          # forward hunch (deg)
    extra_knee_spread = 0
    brow_base = 0.0
    flat = False         # cel/flat-graphic fills (film 2); False keeps film 1 identical
    name = "human"
    seed = 0

    # ------------------------------------------------ public
    def draw(self, cv: skia.Canvas, p: Pose):
        cv.save()
        cv.translate(p.x, p.y)
        cv.scale(-p.s if p.flip else p.s, p.s)
        alpha = p.alpha
        if alpha < 0.999:
            paint = skia.Paint()
            paint.setAlphaf(alpha)
            cv.saveLayer(None, paint)
        breath = math.sin(p.t * 2.1 + self.seed) * 1.4 * p.breathe
        bob = 0.0
        if p.legs == "walk":
            bob = -abs(math.sin(p.phase * 2 * math.pi)) * 6
        if p.legs == "float":
            bob = math.sin(p.t * 1.7) * 4
        if p.legs == "sit":
            cv.translate(0, -self.hip_y - 4)   # (x, y) is the seat contact point when sitting
        cv.translate(0, bob)
        self._shadow(cv, p, bob)
        cv.save()
        cv.rotate(p.lean)
        self.draw_back(cv, p)
        self.draw_arm(cv, p, side="l", back=True)
        self.draw_legs(cv, p)
        self.draw_body(cv, p, breath)
        self.draw_arm(cv, p, side="r", back=False)
        cv.save()
        hx, hy = self.head_anchor(p)
        cv.translate(hx, hy + breath * 0.5)
        cv.rotate(p.head_tilt + self.stoop * 0.4)
        self.draw_head(cv, p)
        cv.restore()
        self.draw_front(cv, p)
        cv.restore()
        if alpha < 0.999:
            cv.restore()
        cv.restore()

    # ------------------------------------------------ hooks for subclasses
    def head_anchor(self, p):
        return (self.stoop * 0.8 + p.turn * 4, self.neck_y - self.head_r * 0.82)

    def draw_back(self, cv, p):
        pass

    def draw_front(self, cv, p):
        pass

    # ------------------------------------------------ body
    def _shadow(self, cv, p, bob):
        if p.legs in ("float", "sit"):
            return
        cv.drawOval(skia.Rect.MakeLTRB(-60, -8 - bob, 60, 8 - bob), fill("#000000", 0.22))

    def body_path(self, p, breath):
        tw, hw = self.body_top_w, self.hem_w
        ny, hy = self.neck_y + 6, self.hem_y
        flare = 6 * math.sin(p.t * 3) if p.legs == "float" else 0
        return smooth_path([
            (-tw * 0.55, ny - 2), (-tw - 4, ny + 14 + breath), (-tw - 2, ny + 50),
            (-hw * 0.8, hy - 40), (-hw - flare, hy), (0, hy + 4), (hw + flare, hy),
            (hw * 0.8, hy - 40), (tw + 2, ny + 50), (tw + 4, ny + 14 + breath), (tw * 0.55, ny - 2), (0, ny + 4),
        ], tension=0.45)

    def body_colors(self):
        return ("mustard", "mustard_dark")

    def draw_body(self, cv, p, breath):
        base, dark = self.body_colors()
        path = self.body_path(p, breath)
        if self.flat:   # cel style: one flat fill + one flat shadow shape
            cv.drawPath(path, fill(base))
        else:
            cv.drawPath(path, K.lin((0, self.neck_y), (0, self.hem_y), [K.shade(base, 0.12), base, dark], [0, 0.4, 1]))
        # side shading for volume
        cv.save()
        cv.clipPath(path, doAntiAlias=True)
        cv.drawRect(skia.Rect.MakeLTRB(self.body_top_w * 0.35, self.neck_y, 120, 0), fill(dark, 0.6 if self.flat else 0.35))
        self.body_detail(cv, p)
        cv.restore()
        cv.drawPath(path, stroke("line", self.line_w))
        # neck
        cv.drawPath(limb(0, self.neck_y + 8, 0, self.neck_y - 12, 18, 18), fill(K.shade(self.skin, -0.12)))

    def body_detail(self, cv, p):
        pass

    def leg_colors(self):
        return ("teal", "skin")   # trouser, foot

    def draw_legs(self, cv, p):
        trouser, foot = self.leg_colors()
        hy = self.hip_y
        lw = self.leg_w
        mode = p.legs
        legs = []
        if mode in ("stand", "tiptoe"):
            legs = [(-12, 0, -14, 0), (12, 0, 14, 0)]
            for sx, _, fx, _ in legs:
                self._leg(cv, sx, hy, fx, -2 if mode == "stand" else -10, trouser, foot, toe=(1 if fx > 0 else -1))
        elif mode == "walk":
            for k, side in ((0, -1), (0.5, 1)):
                ph = (p.phase + k) * 2 * math.pi
                ang = math.sin(ph) * 24
                lift = max(0, math.cos(ph)) * 10
                fx = side * 6 + math.sin(math.radians(ang)) * (self.thigh + self.shin) * 0.9
                self._leg(cv, side * 8, hy, fx, -lift, trouser, foot, toe=1)
        elif mode == "float":
            for side in (-1, 1):
                sw = math.sin(p.t * 2.2 + side) * 6
                self._leg(cv, side * 10, hy, side * 14 + sw, -8, trouser, foot, toe=side, point=True)
        elif mode == "sit":
            # seated, facing camera: short foreshortened thighs, shins hanging, feet toward viewer
            for side in (-1, 1):
                kx = side * (15 + self.extra_knee_spread) + p.turn * 10
                ky = hy + 22
                th = limb(side * 11, hy + 4, kx, ky, lw * 2.3, lw * 2.3)
                cv.drawPath(th, fill(trouser)); cv.drawPath(th, stroke("line", self.line_w))
                swing = math.sin(p.t * 2.0 + side) * 3 * p.extra.get("swing", 0.0)
                fx_, fy_ = kx + swing + p.turn * 4, ky + self.shin * 0.95
                sh = limb(kx, ky, fx_, fy_ - 6, lw * 2.0, lw * 1.7)
                cv.drawPath(sh, fill(trouser)); cv.drawPath(sh, stroke("line", self.line_w))
                fp = ellipse(fx_ + side * 2, fy_ - 2, 11, 8)
                cv.drawPath(fp, fill(foot)); cv.drawPath(fp, stroke("line", self.line_w * 0.9))
        elif mode == "kneel":
            for side in (-1, 1):
                kx = side * 14 + 20
                cv.drawPath(limb(side * 10, hy, kx, -14, lw * 2.2, lw * 2), fill(trouser))
                cv.drawPath(limb(side * 10, hy, kx, -14, lw * 2.2, lw * 2), stroke("line", self.line_w))
                cv.drawPath(limb(kx, -12, kx - 50, -10, lw * 2, lw * 1.6), fill(trouser))
                cv.drawPath(limb(kx, -12, kx - 50, -10, lw * 2, lw * 1.6), stroke("line", self.line_w))

    def _leg(self, cv, hx, hy, fx, fy, trouser, foot, toe=1, point=False, from_knee=False):
        lw = self.leg_w
        path = limb(hx, hy, fx, fy - 8, lw * 2.1, lw * 1.7)
        cv.drawPath(path, fill(trouser))
        cv.drawPath(path, stroke("line", self.line_w))
        # foot
        fp = ellipse(fx + toe * 7, fy - 3 + (4 if point else 0), 14, 7)
        cv.drawPath(fp, fill(foot))
        cv.drawPath(fp, stroke("line", self.line_w * 0.9))

    # ------------------------------------------------ arms
    def sleeve(self):
        return ("mustard", 0.75)   # colour, fraction of arm covered

    def arm_angles(self, p, side):
        default = {"l": (8, 10), "r": (8, 10)}
        a = p.arms.get(side, default[side])
        if p.legs == "walk" and side not in p.arms:
            sw = math.sin((p.phase + (0 if side == "l" else 0.5)) * 2 * math.pi) * 18
            a = (8 + sw, 14)
        if p.legs == "float" and side not in p.arms:
            a = (55 + math.sin(p.t * 2 + (side == "l")) * 8, 20)
        return a

    def draw_arm(self, cv, p, side, back):
        sh_deg, el_deg = self.arm_angles(p, side)
        sgn = -1 if side == "l" else 1
        sx, sy = sgn * (self.shoulder_w + 4), self.neck_y + 16
        # angle from straight down, rotating outward
        a1 = math.radians(sh_deg) * sgn
        ex, ey = sx + math.sin(a1) * self.upper_arm, sy + math.cos(a1) * self.upper_arm
        a2 = a1 - math.radians(el_deg) * sgn
        hx, hy = ex + math.sin(a2) * self.fore_arm, ey + math.cos(a2) * self.fore_arm
        col, frac = self.sleeve()
        skin = self.skin
        if back:
            skin = K.shade(skin, -0.15)
            col = K.shade(col, -0.18) if isinstance(col, (str, tuple)) else col
        # forearm skin
        cv.drawPath(limb(ex, ey, hx, hy, 15, 13), fill(skin))
        cv.drawPath(limb(ex, ey, hx, hy, 15, 13), stroke("line", self.line_w))
        # upper arm (sleeve)
        sx2 = lerp(ex, hx, max(0, frac - 0.5) * 2)
        sy2 = lerp(ey, hy, max(0, frac - 0.5) * 2)
        sl = limb(sx, sy, ex, ey, 26, 24)
        cv.drawPath(sl, fill(col))
        cv.drawPath(sl, stroke("line", self.line_w))
        if frac > 0.5:
            cuff = limb(ex, ey, sx2, sy2, 24, 26)
            cv.drawPath(cuff, fill(col))
            cv.drawPath(cuff, stroke("line", self.line_w))
        # hand
        kind = p.hand.get(side, "open")
        self.draw_hand(cv, hx, hy, a2, kind, skin, side, p)
        prop = p.hold if side == "r" else p.hold_l
        if prop:
            from . import props
            props.held(cv, prop, hx, hy, a2, p)

    def draw_hand(self, cv, x, y, ang, kind, skin, side, p):
        r = 10.5
        hp = ellipse(x, y + 2, r, r * 1.1)
        cv.drawPath(hp, fill(skin))
        cv.drawPath(hp, stroke("line", self.line_w * 0.9))
        if kind == "point":
            d = (math.sin(ang), math.cos(ang))
            f = limb(x, y, x + d[0] * 20, y + d[1] * 20, 7, 6)
            cv.drawPath(f, fill(skin))
            cv.drawPath(f, stroke("line", self.line_w * 0.8))
        elif kind == "open":
            th = limb(x, y, x + (-6 if side == "l" else 6), y - 9, 6, 5)
            cv.drawPath(th, fill(skin))
            cv.drawPath(th, stroke("line", self.line_w * 0.7))
        elif kind == "thumbsup":
            th = limb(x, y - 4, x, y - 20, 7, 6)
            cv.drawPath(th, fill(skin))
            cv.drawPath(th, stroke("line", self.line_w * 0.8))

    # ------------------------------------------------ head
    def face_offset(self, p):
        return p.turn * 13

    def draw_head(self, cv, p):
        r = self.head_r
        self.draw_hair_back(cv, p)
        # ears
        ox = self.face_offset(p)
        for side in (-1, 1):
            ex = side * r * 0.95 - ox * 0.5
            if side == 1 and p.turn > 0.6:
                continue
            ep = ellipse(ex, 4, 9, 12)
            cv.drawPath(ep, fill(self.skin))
            cv.drawPath(ep, stroke("line", self.line_w * 0.9))
        head = self.head_path(p)
        if self.flat:
            cv.drawPath(head, fill(self.skin))
            cv.save()
            cv.clipPath(head, doAntiAlias=True)
            cv.drawPath(ellipse(-r * 0.25 + ox * 0.4, -r * 0.2, r * 1.05, r * 1.12), fill(K.shade(self.skin, -0.16)))
            cv.drawPath(ellipse(-r * 0.32 + ox * 0.4, -r * 0.26, r * 1.02, r * 1.08), fill(self.skin))
            cv.restore()
        else:
            cv.drawPath(head, K.rad((-r * 0.3 + ox * 0.5, -r * 0.35), r * 1.5,
                                    [K.shade(self.skin, 0.12), self.skin, "skin_shadow"], [0, 0.6, 1]))
        cv.drawPath(head, stroke("line", self.line_w))
        self.draw_face(cv, p)
        self.draw_hair_front(cv, p)
        self.draw_head_extra(cv, p)

    def head_path(self, p):
        r = self.head_r
        return smooth_path([(0, -r), (r * 0.92, -r * 0.55), (r * 1.0, r * 0.1), (r * 0.72, r * 0.72),
                            (0, r * 0.95), (-r * 0.72, r * 0.72), (-r * 1.0, r * 0.1), (-r * 0.92, -r * 0.55)],
                           tension=0.55)

    def draw_hair_back(self, cv, p):
        pass

    def draw_hair_front(self, cv, p):
        pass

    def draw_head_extra(self, cv, p):
        pass

    # ------------------------------------------------ face
    eye_y = 2
    eye_dx = 21
    eye_rx = 9.5
    eye_ry = 12.5
    iris = "#2b1810"
    lash = False
    gap_tooth = False

    def draw_face(self, cv, p):
        ox = self.face_offset(p)
        e = p.expr
        blink = max(p.blink, 0.85 if e == "sleepy" else 0.0, 1.0 if e in ("laugh",) else 0.0)
        if e in ("happy",) and p.mouth < 0.2:
            blink = max(blink, 0.0)
        lx, ly = p.look
        # cheeks
        for side in (-1, 1):
            cx = side * 30 + ox
            if side == 1 and p.turn > 0.7:
                continue
            a = 0.5 if e in ("shy", "happy", "laugh", "grin", "awe") else 0.28
            cv.drawCircle(cx, 22, 11, K.rad_a((cx, 22), 12, [("blush", a), ("blush", 0)]))
        # eyes
        for side in (-1, 1):
            far = (side == 1)
            sq = 1 - p.turn * 0.25 if far else 1.0
            ex = side * self.eye_dx * (1 - 0.25 * p.turn if far else 1) + ox
            ey = self.eye_y
            self.draw_eye(cv, ex, ey, sq, blink, lx, ly, e, side)
        # brows
        self.draw_brows(cv, p, ox)
        # nose
        nx = ox + 3 + p.turn * 4
        cv.drawPath(smooth_path([(nx - 3, 12), (nx + 3, 20), (nx - 2, 23)], close=False),
                    stroke(K.shade(self.skin, -0.35), 2.4))
        self.draw_mouth(cv, p, ox)

    def draw_eye(self, cv, x, y, sq, blink, lx, ly, e, side):
        rx, ry = self.eye_rx * sq, self.eye_ry
        if e in ("surprised", "awe"):
            ry *= 1.18
            rx *= 1.1
        if e in ("happy", "laugh") and blink > 0.9:
            # closed happy arcs
            cv.drawPath(smooth_path([(x - rx, y + 2), (x, y - ry * 0.6), (x + rx, y + 2)], close=False),
                        stroke("line", 3.2))
            return
        if blink >= 0.98:
            cv.drawPath(smooth_path([(x - rx, y), (x, y + ry * 0.35), (x + rx, y)], close=False),
                        stroke("line", 3.2))
            return
        # eye white rim (subtle), iris big
        cv.drawOval(skia.Rect.MakeLTRB(x - rx - 2, y - ry - 2, x + rx + 2, y + ry + 2), fill("#fbf6ef"))
        ix, iy = x + lx * rx * 0.25, y + ly * ry * 0.2
        cv.drawOval(skia.Rect.MakeLTRB(ix - rx * 0.95, iy - ry * 0.92, ix + rx * 0.95, iy + ry * 0.92),
                    K.rad((ix, iy + 2), ry, [K.shade(self.iris, 0.25), self.iris, "#0e0807"], [0, 0.55, 1]))
        # highlights
        cv.drawCircle(ix - rx * 0.32, iy - ry * 0.38, rx * 0.34, fill("#ffffff", 0.95))
        cv.drawCircle(ix + rx * 0.35, iy + ry * 0.3, rx * 0.15, fill("#ffffff", 0.8))
        # lid
        lid = max(blink, 0.35 if e in ("sleepy", "smug") else 0.18 if e in ("sad", "worried") else 0.0)
        if lid > 0.02:
            cv.save()
            cv.clipRect(skia.Rect.MakeLTRB(x - rx - 3, y - ry - 3, x + rx + 3, y - ry - 3 + (ry * 2 + 6) * lid))
            cv.drawOval(skia.Rect.MakeLTRB(x - rx - 3, y - ry - 3, x + rx + 3, y + ry + 3), fill(self.skin))
            cv.restore()
            ly2 = y - ry - 3 + (ry * 2 + 6) * lid
            cv.drawLine(x - rx - 2, ly2, x + rx + 2, ly2, stroke("line", 2.6))
        else:
            cv.drawPath(smooth_path([(x - rx - 2, y - ry * 0.6), (x, y - ry - 3), (x + rx + 2, y - ry * 0.6)],
                                    close=False), stroke("line", 2.8))
        if self.lash:
            cv.drawLine(x + side * rx, y - ry * 0.55, x + side * (rx + 5), y - ry * 0.85, stroke("line", 2.2))
        if e == "cry":
            cv.drawPath(ellipse(x + 2, y + ry + 6, 3.5, 6), fill("#bfe3ff", 0.9))

    def draw_brows(self, cv, p, ox):
        e = p.expr
        raise_ = {"surprised": 9, "awe": 8, "worried": 3, "sad": 2, "angry": -4, "determined": -3,
                  "smug": 0, "happy": 3, "laugh": 4, "grin": 2, "cry": 3, "shy": 2, "wince": -2}.get(e, 0)
        raise_ += p.brow * 6 + self.brow_base
        for side in (-1, 1):
            far = side == 1
            bx = side * self.eye_dx * (1 - 0.25 * p.turn if far else 1) + ox
            by = self.eye_y - self.eye_ry - 10 - raise_
            inner = {"worried": -6, "sad": -6, "cry": -7, "angry": 7, "determined": 5}.get(e, 0)
            if e == "smug":
                inner = 4 if side == -1 else -3
                by -= 4 if side == 1 else 0
            x0, x1 = bx - side * 10, bx + side * 10
            y0 = by + inner * 0.5     # inner end
            y1 = by - inner * 0.3
            cv.drawPath(smooth_path([(x0, y0), ((x0 + x1) / 2, min(y0, y1) - 3), (x1, y1)], close=False),
                        stroke("hair", 4.2))

    def draw_mouth(self, cv, p, ox):
        e, m = p.expr, clamp(p.mouth)
        mx, my = ox + 2, 34
        line = stroke("line", 3)
        if m > 0.08:
            # talking: open mouth, shape follows expression slightly
            w = 9 + m * 6 + (4 if e in ("happy", "grin", "laugh") else 0)
            h = 3 + m * 12
            up = 3 if e in ("happy", "grin", "laugh", "awe") else -2 if e in ("sad", "worried", "cry") else 0
            path = smooth_path([(mx - w, my - up), (mx, my - 2), (mx + w, my - up), (mx, my + h)], tension=0.6)
            cv.drawPath(path, fill("#5a1e22"))
            cv.save()
            cv.clipPath(path, doAntiAlias=True)
            cv.drawOval(skia.Rect.MakeLTRB(mx - w * 0.6, my + h * 0.45, mx + w * 0.6, my + h + 6), fill("#d9606a"))
            cv.drawRect(skia.Rect.MakeLTRB(mx - w, my - 6, mx + w, my + 1.5), fill("#fffaf0"))
            if self.gap_tooth:
                cv.drawRect(skia.Rect.MakeLTRB(mx - 2.5, my - 6, mx + 2.5, my + 2), fill("#5a1e22"))
            cv.restore()
            cv.drawPath(path, line)
            return
        if e in ("happy", "grin", "laugh", "awe", "surprised"):
            if e in ("grin", "laugh"):
                path = smooth_path([(mx - 16, my - 4), (mx, my - 1), (mx + 16, my - 4), (mx, my + 12)], tension=0.6)
                cv.drawPath(path, fill("#5a1e22"))
                cv.save(); cv.clipPath(path, doAntiAlias=True)
                cv.drawRect(skia.Rect.MakeLTRB(mx - 18, my - 8, mx + 18, my + 2), fill("#fffaf0"))
                if self.gap_tooth:
                    cv.drawRect(skia.Rect.MakeLTRB(mx - 3, my - 8, mx + 3, my + 3), fill("#5a1e22"))
                cv.drawOval(skia.Rect.MakeLTRB(mx - 9, my + 4, mx + 9, my + 16), fill("#d9606a"))
                cv.restore()
                cv.drawPath(path, line)
            elif e in ("surprised", "awe"):
                o = ellipse(mx, my + 3, 6 if e == "awe" else 7, 8 if e == "awe" else 10)
                cv.drawPath(o, fill("#5a1e22")); cv.drawPath(o, line)
            else:
                cv.drawPath(smooth_path([(mx - 12, my - 3), (mx, my + 6), (mx + 12, my - 3)], close=False), line)
        elif e in ("sad", "cry", "worried"):
            cv.drawPath(smooth_path([(mx - 10, my + 5), (mx, my - 1), (mx + 10, my + 5)], close=False), line)
        elif e == "smug":
            cv.drawPath(smooth_path([(mx - 10, my + 1), (mx + 2, my + 3), (mx + 13, my - 5)], close=False), line)
        elif e in ("angry", "determined", "wince"):
            cv.drawLine(mx - 9, my + 2, mx + 9, my + (0 if e != "wince" else 4), line)
        elif e == "sleepy":
            cv.drawPath(ellipse(mx, my + 2, 4, 3), fill("#5a1e22"))
        elif e == "shy":
            cv.drawPath(smooth_path([(mx - 6, my + 1), (mx, my + 3), (mx + 6, my + 1)], close=False), line)
        else:
            cv.drawPath(smooth_path([(mx - 8, my + 1), (mx, my + 4), (mx + 8, my + 1)], close=False), line)
