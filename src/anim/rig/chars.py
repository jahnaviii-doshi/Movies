"""The cast. Canonical designs live here and nowhere else.

MEHER (9): small, round face, warm brown skin, two braids with red ribbons, mustard
kurta three sizes too big (sleeves past her wrists), teal pyjama, bare feet, missing front tooth.
KABIR (11): taller, lanky; red cap worn backwards; blue T-shirt with a yellow lightning bolt;
khaki shorts; white sneakers; spiky fringe; cocky grin.
NANI / SHARDA (70s): short and soft; white bun; small oval silver spectacles; white sari with
lavender border, pallu over the left shoulder; silver bangles; slight stoop.
MISHRI AMMA (ancient): tiny; huge cloud-bun of white hair; big round gold spectacles that
magnify her eyes; pink sugar-thread shawl that sparkles; hunched; translucent when fading.
YOUNG SHARDA (9, 80 years ago): plaits with white jasmine, green frock (shown in sepia).
TODDLER: tiny round neighbour toddler with a topknot.
"""
from __future__ import annotations

import math

import skia

from .. import core as K
from ..core import PAL, C, fill, stroke, limb, ellipse, smooth_path, lerp, clamp
from .human import Human, Pose, auto_blink  # noqa: F401


# =============================================================== MEHER
class Meher(Human):
    name = "meher"
    seed = 1
    head_r = 57
    gap_tooth = True
    lash = True

    def body_colors(self):
        return ("mustard", "mustard_dark")

    def sleeve(self):
        return ("mustard", 0.92)   # oversized: sleeves cover nearly to the hand

    def leg_colors(self):
        return ("teal", "skin")

    def body_detail(self, cv, p):
        # kurta placket + embroidered neckline dots
        cv.drawLine(0, self.neck_y + 6, 0, self.neck_y + 46, stroke("mustard_dark", 3))
        for i in range(5):
            cv.drawCircle(0, self.neck_y + 12 + i * 8, 2.2, fill("#fff1c9"))
        # hem band
        cv.drawRect(skia.Rect.MakeLTRB(-120, self.hem_y - 12, 120, self.hem_y + 6), fill("#c98a1f", 0.8))
        for i in range(-6, 7):
            cv.drawCircle(i * 10, self.hem_y - 6, 2, fill("#fff1c9", 0.9))

    def draw_hair_back(self, cv, p):
        r = self.head_r
        ox = self.face_offset(p)
        # two braids hanging behind shoulders, swinging
        sw = math.sin(p.t * 2.0) * 3 + (6 if p.legs == "walk" else 0) * math.sin(p.phase * 6.28)
        if p.legs == "float":
            sw = math.sin(p.t * 1.6) * 10
        for side in (-1, 1):
            bx = side * (r * 0.78) - ox * 0.3
            pts = []
            for i in range(7):
                y = r * 0.2 + i * 17
                pts.append((bx + side * (4 + i * 1.5) + sw * (i / 6), y))
            for i, (x, y) in enumerate(pts):
                seg = ellipse(x, y, 10 - i * 0.6, 10)
                cv.drawPath(seg, fill("hair"))
                cv.drawPath(seg, stroke("line", 2.2))
            x, y = pts[-1]
            # ribbon bow
            for d in (-1, 1):
                bow = K.poly([(x, y + 6), (x + d * 14, y), (x + d * 14, y + 14)])
                cv.drawPath(bow, fill("ribbon"))
                cv.drawPath(bow, stroke("line", 2))
            cv.drawCircle(x, y + 7, 4, fill("ribbon"))
            tail = smooth_path([(x + 2, y + 12), (x + 5 + sw * 0.3, y + 22), (x + 1 + sw * 0.4, y + 30)], close=False)
            cv.drawPath(tail, stroke("ribbon", 3))

    def draw_hair_front(self, cv, p):
        r = self.head_r
        ox = self.face_offset(p)
        part = ox * 0.6 - 4
        cap = smooth_path([(-r * 1.02, r * 0.05), (-r * 1.0, -r * 0.6), (-r * 0.5, -r * 1.02), (part, -r * 1.06),
                           (r * 0.5, -r * 1.02), (r * 1.0, -r * 0.6), (r * 1.02, r * 0.05), (r * 0.88, -r * 0.2),
                           (r * 0.45, -r * 0.55 + 2), (part + 6, -r * 0.62), (part - 6, -r * 0.62),
                           (-r * 0.45, -r * 0.55 + 2), (-r * 0.88, -r * 0.2)], tension=0.5)
        cv.drawPath(cap, K.lin((0, -r), (0, 0), ["#3a2a30", "hair"]))
        cv.drawPath(cap, stroke("line", 3))
        # shine
        cv.drawPath(smooth_path([(-r * 0.6, -r * 0.7), (-r * 0.3, -r * 0.9), (part - 10, -r * 0.92)], close=False),
                    stroke("#6a5560", 3, 0.7))
        cv.drawLine(part, -r * 1.04, part, -r * 0.64, stroke("#4a3a40", 2))


# =============================================================== KABIR
class Kabir(Human):
    name = "kabir"
    seed = 2
    height = 330
    head_r = 55
    neck_y = -222
    hip_y = -122
    hem_y = -112
    hem_w = 38
    body_top_w = 34
    upper_arm = 56
    fore_arm = 52
    thigh = 64
    shin = 60
    leg_w = 12

    def body_colors(self):
        return ("tee_blue", K.shade("tee_blue", -0.3))

    def sleeve(self):
        return ("tee_blue", 0.35)

    def leg_colors(self):
        return ("skin", "sneaker")

    def body_path(self, p, breath):
        tw, hw = self.body_top_w, self.hem_w
        ny, hy = self.neck_y + 6, self.hem_y
        return smooth_path([(-tw * 0.5, ny - 2), (-tw - 6, ny + 10 + breath), (-tw - 2, ny + 50), (-hw, hy),
                            (0, hy + 2), (hw, hy), (tw + 2, ny + 50), (tw + 6, ny + 10 + breath),
                            (tw * 0.5, ny - 2), (0, ny + 6)], tension=0.4)

    def body_detail(self, cv, p):
        y0 = self.neck_y + 30
        bolt = K.poly([(4, y0), (-12, y0 + 30), (-1, y0 + 30), (-8, y0 + 56), (14, y0 + 22), (2, y0 + 22), (10, y0)])
        cv.drawPath(bolt, fill("bolt"))
        cv.drawPath(bolt, stroke("line", 2))

    def draw_legs(self, cv, p):
        # shorts first (khaki), then skinny legs + sneakers via base
        Human.draw_legs(self, cv, p)
        hy = self.hip_y
        if False:
            pass
        else:
            shorts = smooth_path([(-37, hy - 12), (37, hy - 12), (40, hy + 34), (6, hy + 36), (0, hy + 16),
                                  (-6, hy + 36), (-40, hy + 34)], tension=0.2)
        cv.drawPath(shorts, fill("khaki"))
        cv.drawPath(shorts, stroke("line", self.line_w))
        cv.drawRect(skia.Rect.MakeLTRB(-30, hy + 8, -14, hy + 22), fill(K.shade("khaki", -0.15)))

    def _leg(self, cv, hx, hy, fx, fy, trouser, foot, toe=1, point=False, from_knee=False):
        lw = self.leg_w
        path = limb(hx, hy, fx, fy - 8, lw * 1.7, lw * 1.4)
        cv.drawPath(path, fill("skin"))
        cv.drawPath(path, stroke("line", self.line_w))
        # sneaker
        sh = K.rrect(fx - 12 + toe * 4, fy - 16, 30, 16, 7)
        cv.drawPath(sh, fill("sneaker"))
        cv.drawPath(sh, stroke("line", self.line_w * 0.9))
        cv.drawRect(skia.Rect.MakeLTRB(fx - 12 + toe * 4, fy - 4, fx + 18 + toe * 4, fy), fill("#cc4a3a"))

    def draw_hand(self, cv, x, y, ang, kind, skin, side, p):
        """extra: crystal (0..1) turns his RIGHT hand to sugar crystal; glove=True hides it in a wool glove;
        crystal_wrist (0..1) extends the crystal up the forearm."""
        cr = p.extra.get("crystal", 0.0) if side == "r" else 0.0
        if side == "r" and p.extra.get("glove"):
            g = ellipse(x, y + 2, 15, 16)
            cv.drawPath(g, fill("#5b6b8c")); cv.drawPath(g, stroke("line", self.line_w))
            for i in range(3):
                cv.drawLine(x - 10, y - 8 + i * 6, x + 10, y - 8 + i * 6, stroke("#7d8db0", 1.6))
            return
        Human.draw_hand(self, cv, x, y, ang, kind, skin, side, p)
        if cr > 0:
            from .props import crystal_hand
            cv.save(); cv.translate(x, y + 2); cv.scale(1.15, 1.15)
            crystal_hand(cv, p, cr)
            cv.restore()
            wr = p.extra.get("crystal_wrist", 0.0)
            if wr > 0:
                # crystal facets creeping up the forearm toward the elbow
                for i in range(int(6 * wr)):
                    fx = x - math.sin(ang) * (12 + i * 6)
                    fy = y - math.cos(ang) * (12 + i * 6)
                    cv.drawPath(K.poly([(fx, fy - 6), (fx + 6, fy), (fx, fy + 6), (fx - 6, fy)]), fill("#eaf7ff", 0.85))
                    cv.drawPath(K.poly([(fx, fy - 6), (fx + 6, fy), (fx, fy + 6), (fx - 6, fy)]), stroke("#9fc7e8", 1.4))
            t = p.t
            if math.sin(t * 2.7) > 0.6:
                from ..fx import star4
                star4(cv, x + 6, y - 6, 7 * cr, "#ffffff", cr)

    def draw_hair_front(self, cv, p):
        r = self.head_r
        ox = self.face_offset(p)
        # spiky fringe peeking out under backwards cap
        spikes = [(-r * 0.95, -r * 0.2)]
        for i in range(7):
            x = -r * 0.8 + i * r * 0.27 + ox * 0.4
            spikes += [(x, -r * (0.55 if i % 2 else 0.42)), (x + r * 0.13, -r * 0.62)]
        spikes += [(r * 0.95, -r * 0.2), (r * 0.9, -r * 0.75), (-r * 0.9, -r * 0.75)]
        hair = K.poly(spikes)
        cv.drawPath(hair, fill("hair"))
        cv.drawPath(hair, stroke("line", 2.6))
        # backwards cap: dome + brim sticking out behind (to screen-left when facing right)
        dome = smooth_path([(-r * 1.0, -r * 0.55), (-r * 0.75, -r * 1.05), (0, -r * 1.22), (r * 0.75, -r * 1.05),
                            (r * 1.0, -r * 0.55), (0, -r * 0.7)], tension=0.5)
        cv.drawPath(dome, K.lin((0, -r * 1.2), (0, -r * 0.5), [K.shade("cap_red", 0.15), "cap_red"]))
        cv.drawPath(dome, stroke("line", 3))
        cv.drawLine(0, -r * 1.2, 0, -r * 0.7, stroke(K.shade("cap_red", -0.3), 2))
        cv.drawCircle(0, -r * 1.2, 4, fill(K.shade("cap_red", -0.2)))
        bx = -r * 0.9 - ox * 0.3
        brim = smooth_path([(bx + 6, -r * 0.7), (bx - 38, -r * 0.8), (bx - 40, -r * 0.62), (bx + 4, -r * 0.5)], tension=0.4)
        cv.drawPath(brim, fill(K.shade("cap_red", -0.15)))
        cv.drawPath(brim, stroke("line", 3))


# =============================================================== NANI
class Nani(Human):
    name = "nani"
    seed = 3
    height = 290
    head_r = 54
    neck_y = -196
    hip_y = -100
    hem_y = -6
    hem_w = 66
    body_top_w = 44
    shoulder_w = 38
    stoop = 6
    skin = "#b77b55"

    def body_colors(self):
        return ("sari", "#d8d0e6")

    def sleeve(self):
        return ("#d6c8ef", 0.4)

    def leg_colors(self):
        return ("sari", "#b77b55")

    def draw_legs(self, cv, p):
        if p.legs == "sit":
            Human.draw_legs(self, cv, p)
            return
        # feet peeking under sari
        step = math.sin(p.phase * 6.28) * 8 if p.legs == "walk" else 0
        for side in (-1, 1):
            fp = ellipse(side * 16 + step * side, -4, 14, 7)
            cv.drawPath(fp, fill(self.skin))
            cv.drawPath(fp, stroke("line", 2.6))

    def body_path(self, p, breath):
        tw, hw = self.body_top_w, self.hem_w
        ny, hy = self.neck_y + 6, self.hem_y
        if p.legs == "sit":
            hy = self.hip_y + 20
        return smooth_path([(-tw * 0.5, ny - 2), (-tw - 8, ny + 16 + breath), (-tw - 12, ny + 70),
                            (-hw, hy - 30), (-hw + 4, hy), (0, hy + 4), (hw - 4, hy), (hw, hy - 30),
                            (tw + 12, ny + 70), (tw + 8, ny + 16 + breath), (tw * 0.5, ny - 2), (0, ny + 6)],
                           tension=0.45)

    def body_detail(self, cv, p):
        hy = self.hem_y if p.legs != "sit" else self.hip_y + 20
        # lavender border at hem + pallu diagonal over left shoulder
        cv.drawRect(skia.Rect.MakeLTRB(-120, hy - 14, 120, hy + 6), fill("sari_border"))
        cv.drawRect(skia.Rect.MakeLTRB(-120, hy - 18, 120, hy - 14), fill("#c9b4ec"))
        pallu = K.poly([(-self.body_top_w - 10, self.neck_y + 4), (-self.body_top_w + 14, self.neck_y - 2),
                        (self.body_top_w + 20, self.neck_y + 120), (self.body_top_w - 4, self.neck_y + 132)])
        cv.drawPath(pallu, fill("sari_border"))
        cv.drawPath(pallu, stroke("#6b4fa3", 1.5))
        # pleats
        for i in range(-2, 3):
            cv.drawLine(i * 9, hy - 60, i * 11, hy - 16, stroke("#cfc6dd", 2))

    def draw_hand(self, cv, x, y, ang, kind, skin, side, p):
        Human.draw_hand(self, cv, x, y, ang, kind, skin, side, p)
        for k in range(2):
            cv.drawOval(skia.Rect.MakeLTRB(x - 11, y - 14 - k * 5, x + 11, y - 8 - k * 5), stroke("bangle", 2.6))

    def draw_hair_back(self, cv, p):
        r = self.head_r
        ox = self.face_offset(p)
        bun = ellipse(-ox * 0.4 - r * 0.15, -r * 0.92, r * 0.42, r * 0.34)
        cv.drawPath(bun, fill("hair_white"))
        cv.drawPath(bun, stroke("line", 2.6))

    def draw_hair_front(self, cv, p):
        r = self.head_r
        ox = self.face_offset(p)
        part = ox * 0.6 - 2
        hair = smooth_path([(-r * 1.02, r * 0.0), (-r * 0.95, -r * 0.62), (-r * 0.45, -r * 1.0), (part, -r * 1.04),
                            (r * 0.45, -r * 1.0), (r * 0.95, -r * 0.62), (r * 1.02, r * 0.0), (r * 0.82, -r * 0.35),
                            (part + 4, -r * 0.7), (part - 4, -r * 0.7), (-r * 0.82, -r * 0.35)], tension=0.5)
        cv.drawPath(hair, K.lin((0, -r), (0, 0), ["#ffffff", "#ddd8d0"]))
        cv.drawPath(hair, stroke("line", 2.8))
        for k in range(3):
            cv.drawPath(smooth_path([(-r * 0.8 + k * 6, -r * 0.4), (-r * 0.5 + k * 8, -r * 0.82), (part - 6, -r * 0.95)],
                                    close=False), stroke("#c9c2b8", 1.6))
        # bindi
        cv.drawCircle(ox + 1, -r * 0.42, 3.2, fill("#b0252f"))

    def draw_head_extra(self, cv, p):
        # small oval silver spectacles (unless stolen by the monkey)
        if p.extra.get("no_specs"):
            return
        ox = self.face_offset(p)
        for side in (-1, 1):
            far = side == 1
            ex = side * self.eye_dx * (1 - 0.25 * p.turn if far else 1) + ox
            cv.drawOval(skia.Rect.MakeLTRB(ex - 15, self.eye_y - 12, ex + 15, self.eye_y + 12), stroke("#9aa1ad", 2.6))
            cv.drawOval(skia.Rect.MakeLTRB(ex - 14, self.eye_y - 11, ex + 14, self.eye_y + 11), fill("#ffffff", 0.12))
        cv.drawLine(ox - 6, self.eye_y - 2, ox + 6, self.eye_y - 2, stroke("#9aa1ad", 2.4))
        # wrinkles
        cv.drawPath(smooth_path([(ox - 34, 30), (ox - 30, 38), (ox - 24, 42)], close=False), stroke("#8f5b3d", 1.6))
        cv.drawPath(smooth_path([(ox + 34, 30), (ox + 30, 38), (ox + 24, 42)], close=False), stroke("#8f5b3d", 1.6))

    def draw_mouth(self, cv, p, ox):
        Human.draw_mouth(self, cv, p, ox)


# =============================================================== MISHRI AMMA
class Amma(Human):
    name = "amma"
    seed = 4
    height = 210
    head_r = 46
    neck_y = -138
    hip_y = -70
    hem_y = -4
    hem_w = 50
    body_top_w = 34
    shoulder_w = 28
    upper_arm = 36
    fore_arm = 34
    stoop = 14
    skin = "#c08a64"
    eye_rx = 8.5
    eye_ry = 10.5

    def body_colors(self):
        return ("shawl", K.shade("shawl", -0.18))

    def sleeve(self):
        return ("shawl", 0.85)

    def leg_colors(self):
        return ("shawl", "#c08a64")

    def draw_legs(self, cv, p):
        for side in (-1, 1):
            fp = ellipse(side * 12, -4, 11, 6)
            cv.drawPath(fp, fill(self.skin))
            cv.drawPath(fp, stroke("line", 2.4))

    def body_path(self, p, breath):
        tw, hw = self.body_top_w, self.hem_w
        ny, hy = self.neck_y + 4, self.hem_y
        return smooth_path([(-tw * 0.5, ny), (-tw - 14, ny + 18 + breath), (-tw - 16, ny + 60), (-hw, hy - 16),
                            (-hw + 6, hy), (0, hy + 3), (hw - 6, hy), (hw, hy - 16), (tw + 16, ny + 60),
                            (tw + 14, ny + 18 + breath), (tw * 0.5, ny), (0, ny + 4)], tension=0.5)

    def body_detail(self, cv, p):
        # sugar-thread texture: fine sparkling crosshatch
        t = p.t
        r = K.rng(44)
        for i in range(70):
            x, y = r.uniform(-70, 70), r.uniform(self.neck_y, 0)
            a = 0.35 + 0.35 * math.sin(t * r.uniform(1, 3) + i)
            cv.drawLine(x, y, x + r.uniform(-8, 8), y + r.uniform(4, 10), stroke("shawl_light", 1.4, a))
        for i in range(24):
            x, y = r.uniform(-60, 60), r.uniform(self.neck_y, 0)
            a = clamp(math.sin(t * r.uniform(1.5, 4) + i * 1.7))
            if a > 0.6:
                cv.drawCircle(x, y, 2.2, fill("#ffffff", a))
        # fringe at hem
        for i in range(-9, 10):
            cv.drawLine(i * 5.5, self.hem_y - 6, i * 5.5 + math.sin(t * 2 + i) * 1.5, self.hem_y + 6,
                        stroke("shawl_light", 1.6))

    def draw_hair_back(self, cv, p):
        r = self.head_r
        ox = self.face_offset(p)
        # the big cloud bun, piled high on the crown like spun sugar
        cx, cy = -ox * 0.3 - 4, -r * 1.28
        puffs = [(-22, 8, 17), (20, 10, 16), (0, -6, 22), (-12, -16, 14), (13, -14, 15), (0, 14, 16)]
        for (dx, dy, rr) in puffs:
            cv.drawCircle(cx + dx, cy + dy, rr + 2.4, fill("line"))
        for (dx, dy, rr) in puffs:
            cv.drawCircle(cx + dx, cy + dy, rr, K.rad((cx + dx - 5, cy + dy - 6), rr * 1.4, ["#ffffff", "hair_white", "#d9d2c8"]))
        cv.drawCircle(cx - 6, cy - 14, 5, fill("#ffffff", 0.95))

    def draw_hair_front(self, cv, p):
        r = self.head_r
        ox = self.face_offset(p)
        hair = smooth_path([(-r * 1.04, -r * 0.05), (-r * 0.9, -r * 0.7), (-r * 0.3, -r * 1.02), (r * 0.3, -r * 1.02),
                            (r * 0.9, -r * 0.7), (r * 1.04, -r * 0.05), (r * 0.7, -r * 0.5), (ox * 0.5, -r * 0.62),
                            (-r * 0.7, -r * 0.5)], tension=0.5)
        cv.drawPath(hair, fill("hair_white"))
        cv.drawPath(hair, stroke("line", 2.6))

    def draw_head_extra(self, cv, p):
        ox = self.face_offset(p)
        r = self.head_r
        # big round gold spectacles
        for side in (-1, 1):
            far = side == 1
            ex = side * self.eye_dx * (1 - 0.25 * p.turn if far else 1) + ox
            cv.drawCircle(ex, self.eye_y, 17, fill("#ffffff", 0.16))
            cv.drawCircle(ex, self.eye_y, 17, stroke("amma_spec", 3.4))
            cv.drawLine(ex - 9, self.eye_y - 10, ex - 3, self.eye_y - 14, stroke("#ffffff", 2, 0.7))
        cv.drawPath(smooth_path([(ox - 4, self.eye_y - 3), (ox, self.eye_y - 6), (ox + 4, self.eye_y - 3)], close=False),
                    stroke("amma_spec", 3))
        # wrinkles + smile lines
        for side in (-1, 1):
            x = ox + side * 30
            cv.drawPath(smooth_path([(x, 20), (x - side * 3, 30), (x - side * 8, 36)], close=False), stroke("#8a5636", 1.5))
        cv.drawLine(ox - 10, -r * 0.48, ox + 10, -r * 0.48, stroke("#8a5636", 1.4))
        cv.drawLine(ox - 7, -r * 0.4, ox + 7, -r * 0.4, stroke("#8a5636", 1.2))

    def draw_front(self, cv, p):
        # shawl drape over the shoulders (in front of arms)
        ny = self.neck_y
        t = p.t
        drape = smooth_path([(-self.body_top_w - 20, ny + 22), (-10, ny + 4), (10, ny + 4),
                             (self.body_top_w + 20, ny + 22), (self.body_top_w + 24, ny + 70),
                             (0, ny + 56 + math.sin(t * 1.5) * 2), (-self.body_top_w - 24, ny + 70)], tension=0.45)
        cv.drawPath(drape, K.lin((0, ny), (0, ny + 70), ["shawl_light", "shawl"]))
        cv.drawPath(drape, stroke("line", 2.6))
        for i in range(-10, 11, 2):
            cv.drawLine(i * 4.5, ny + 60 + abs(i) * 0.6, i * 4.5, ny + 68 + abs(i) * 0.6, stroke("shawl_light", 1.5))


# =============================================================== YOUNG SHARDA (memory)
class YoungSharda(Meher):
    name = "young_sharda"
    seed = 5
    gap_tooth = False

    def body_colors(self):
        return ("#5e9a58", "#3f6f3c")

    def sleeve(self):
        return ("#5e9a58", 0.3)

    def leg_colors(self):
        return ("skin", "skin")

    def body_detail(self, cv, p):
        cv.drawRect(skia.Rect.MakeLTRB(-120, self.hem_y - 10, 120, self.hem_y + 6), fill("#e9e2c2"))

    def draw_hair_back(self, cv, p):
        Meher.draw_hair_back(self, cv, p)
        r = self.head_r
        # jasmine in plaits
        for side in (-1, 1):
            for i in range(4):
                cv.drawCircle(side * r * 0.8, r * 0.3 + i * 22, 4.5, fill("#fffdf3"))


# =============================================================== TODDLER
class Toddler(Human):
    name = "toddler"
    seed = 6
    height = 150
    head_r = 44
    neck_y = -96
    hip_y = -52
    hem_y = -40
    hem_w = 34
    body_top_w = 24
    shoulder_w = 20
    upper_arm = 24
    fore_arm = 22
    leg_w = 10
    thigh = 26
    shin = 22
    eye_rx = 8
    eye_ry = 10
    eye_dx = 17

    def body_colors(self):
        return ("#f0d36a", "#cfa93f")

    def sleeve(self):
        return ("#f0d36a", 0.3)

    def leg_colors(self):
        return ("skin", "skin")

    def draw_hair_front(self, cv, p):
        r = self.head_r
        cv.drawPath(ellipse(0, -r * 1.0, 10, 12), fill("hair"))
        cv.drawCircle(0, -r * 0.95, 5, fill("#e2463f"))
        cv.drawPath(smooth_path([(-r * 0.6, -r * 0.75), (0, -r * 0.95), (r * 0.6, -r * 0.75), (0, -r * 0.82)]),
                    fill("hair"))


CAST = {"meher": Meher(), "kabir": Kabir(), "nani": Nani(), "amma": Amma(),
        "young_sharda": YoungSharda(), "toddler": Toddler()}


def draw(cv, who: str, **pose):
    """Convenience: draw(cv, 'meher', x=.., y=.., expr='happy', t=ctx.t, ...)."""
    rig = CAST[who]
    p = Pose(**pose)
    if "blink" not in pose:
        p.blink = auto_blink(p.t, rig.seed)
    rig.draw(cv, p)
    return p
