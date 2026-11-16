"""The Weather Keeper of Block C: the cast. Canonical designs live here and nowhere else.

Flat-graphic style: flat fills + one cel shadow shape, dark warm outlines that wobble
(core.STYLE, set by the film package), strong silhouettes.

TARA (10): round black specs, very tight high ponytail, coral/cream striped T-shirt, navy shorts,
    sensible black watch (left wrist), sandals; notebook + pencil (hold='notebook').
ISHAAN (7): small and round-headed, a black mop of hair over his eyes, too-big orange vest,
    khaki shorts, one white sock pulled up (his right leg, screen-left) one sock scrunched down,
    blue sneakers, a jam smudge on his cheek.
REHAN (11): lanky, gap-kneed, teal sports jersey with a white collar stripe, navy track shorts with
    white side stripes, red sweatbands on both wrists, cowlick, white sneakers; tennis ball
    (hand={'r':'ball'}). bowling_pose(u) gives the full run-up -> delivery -> follow-through.
MEGHNATH (80s): tall, thin, stooped; bald crown with a white fringe, long white AWNING eyebrows
    (his main acting tool), big nose, brown buttoned cardigan, grey trousers, chappals, RIGHT arm in
    a white sling (extra={'sling': True}); extra={'cardigan': False} short-sleeved shirt (coda);
    extra={'wet': 1} rain-flattened eyebrows/hair; extra={'brow_lift': -1..1} fine eyebrow control.
BHAAP: a football-sized baby cloud of overlapping puffs, softest white, two dot eyes, no mouth unless
    happy. draw_bhaap(...).
CAPTAIN: an opinionated, heavy-lidded pigeon. draw_pigeon(...), draw_pigeon_flock(...).
DADI: draw_dadi(...) lying on her bed fanning with a newspaper.
VARSHA: draw_varsha_photo(...) framed photo; draw_silhouette(...) for the memory.

API
  draw(cv, who, **pose)        who in tara | ishaan | rehan | meghnath (Pose fields as film 1's rig)
  bowling_pose(u) -> dict      Rehan's pose at u in 0..1 (pass with **, plus x/y/s/t/flip)
  draw_bhaap(cv, x, y, s=1, t=0, mood='happy', mouth=0, rain=0, spark=0, grey=0, squash=0,
             look=(0,0), blink=None, alpha=1)
  draw_pigeon(cv, x, y, s=1, t=0, flip=False, mode='stand', head_bob=0.0)
  draw_pigeon_flock(cv, t, x, y, n=9, spread=300, s=1, color='#3a3f52', seed=1)
  draw_dadi(cv, x, y, s=1, t=0, fan=1.0)
  draw_varsha_photo(cv, x, y, s=1, t=0, glass=1.0)
  draw_silhouette(cv, who, x, y, s, color='#1d1430', **pose)    who='meghnath'|'varsha'
  props: draw_pressure_cooker, draw_stove, draw_key, draw_broom, draw_sack, draw_kite, draw_breeze_jar,
         draw_ball, draw_plate, draw_cooker_lid, draw_newspaper, draw_notebook
  hold= names: notebook, key, broom, sack, kite_spool, jar_breeze, plate, cooker_lid, newspaper, ball,
               torch (film 1), cap...
Light presets added to core.LIGHTS: heat, heat_dusk, workshop, dust, monsoon, monsoon_night.
"""
from __future__ import annotations

import math

import skia

from ... import core as K
from ...core import fill, stroke, limb, ellipse, smooth_path, poly, lerp, clamp
from ...rig import props as _props
from ...rig.human import Human, Pose, auto_blink

# ------------------------------------------------------------------ palette + light presets
WK = {
    "tara_skin": "#c68b5f", "ishaan_skin": "#b97b52", "rehan_skin": "#a46a44", "megh_skin": "#bf8e6a",
    "coral": "#ee6f57", "cream": "#fbecd2", "navy": "#2d3a63", "orange_vest": "#f2932c",
    "jersey": "#1f9e8f", "sweat": "#e0413a", "cardigan": "#8a5a34", "cardigan_dk": "#6a4224",
    "trouser": "#8e8a82", "sling": "#f4f1ea", "shirt_check": "#a9c6e0", "hair_bk": "#1d1418",
    "white_hair": "#f4f1ec", "ball": "#d7e84a",
}
for _k, _v in WK.items():
    K.PAL.setdefault(_k, _v)

K.LIGHTS.update({
    "heat": ((1.06, 1.0, 0.86), (0.09, 0.07, 0.03), 0.72),
    "heat_dusk": ((1.05, 0.80, 0.64), (0.07, 0.03, 0.03), 0.85),
    "workshop": ((0.74, 0.86, 1.02), (0.03, 0.05, 0.10), 0.72),
    "dust": ((1.06, 0.72, 0.44), (0.09, 0.03, 0.0), 0.12),
    "monsoon": ((0.86, 1.0, 0.96), (0.0, 0.03, 0.05), 1.25),
    "monsoon_night": ((0.46, 0.56, 0.76), (0.02, 0.03, 0.07), 0.8),
})


# =============================================================== TARA
class Tara(Human):
    name = "tara"
    seed = 11
    flat = True
    height = 310
    head_r = 55
    neck_y = -206
    hip_y = -114
    hem_y = -110
    hem_w = 40
    body_top_w = 33
    skin = "tara_skin"
    lash = True

    def body_colors(self):
        return ("coral", K.shade("coral", -0.25))

    def sleeve(self):
        return ("coral", 0.32)

    def leg_colors(self):
        return ("tara_skin", "tara_skin")

    def body_path(self, p, breath):
        tw, hw = self.body_top_w, self.hem_w
        ny, hy = self.neck_y + 6, self.hem_y
        return smooth_path([(-tw * 0.5, ny - 2), (-tw - 5, ny + 10 + breath), (-tw - 2, ny + 48), (-hw, hy),
                            (0, hy + 3), (hw, hy), (tw + 2, ny + 48), (tw + 5, ny + 10 + breath),
                            (tw * 0.5, ny - 2), (0, ny + 6)], tension=0.4)

    def body_detail(self, cv, p):
        for i in range(6):
            y = self.neck_y + 18 + i * 15
            cv.drawRect(skia.Rect.MakeLTRB(-90, y, 90, y + 7), fill("cream"))

    def draw_legs(self, cv, p):
        Human.draw_legs(self, cv, p)
        hy = self.hip_y
        if p.legs == "sit":
            sh = smooth_path([(-38, hy - 10), (38, hy - 10), (46, hy + 14), (30, hy + 24), (0, hy + 18),
                              (-30, hy + 24), (-46, hy + 14)], tension=0.25)
        else:
            sh = smooth_path([(-36, hy - 10), (36, hy - 10), (40, hy + 30), (6, hy + 32), (0, hy + 14),
                              (-6, hy + 32), (-40, hy + 30)], tension=0.2)
        cv.drawPath(sh, fill("navy"))
        cv.drawPath(sh, stroke("line", self.line_w))

    def _leg(self, cv, hx, hy, fx, fy, trouser, foot, toe=1, point=False, from_knee=False):
        lw = self.leg_w
        path = limb(hx, hy, fx, fy - 8, lw * 1.8, lw * 1.5)
        cv.drawPath(path, fill(self.skin)); cv.drawPath(path, stroke("line", self.line_w))
        sd = K.rrect(fx - 13 + toe * 5, fy - 10, 28, 10, 4)
        cv.drawPath(sd, fill("#7a4a2a")); cv.drawPath(sd, stroke("line", self.line_w * 0.9))
        cv.drawLine(fx - 6 + toe * 5, fy - 12, fx + 8 + toe * 5, fy - 12, stroke("#7a4a2a", 4))

    def draw_hand(self, cv, x, y, ang, kind, skin, side, p):
        Human.draw_hand(self, cv, x, y, ang, kind, skin, side, p)
        if side == "l":   # sensible watch
            wx, wy = x - math.sin(ang) * 12, y - math.cos(ang) * 12
            cv.save(); cv.translate(wx, wy); cv.rotate(-math.degrees(ang))
            cv.drawRect(skia.Rect.MakeLTRB(-9, -3, 9, 3), fill("#222"))
            cv.drawCircle(0, 0, 5, fill("#f5f1e6")); cv.drawCircle(0, 0, 5, stroke("line", 1.6))
            cv.restore()

    def draw_hair_back(self, cv, p):
        r = self.head_r
        ox = self.face_offset(p)
        sw = math.sin(p.t * 2.4) * 5 + (8 * math.sin(p.phase * 6.28) if p.legs == "walk" else 0)
        bx, by = -ox * 0.6 - r * 0.25, -r * 1.0
        tail = smooth_path([(bx + 6, by + 2), (bx - 10, by - 16), (bx - r * 0.9, by - 8 + sw * 0.2),
                            (bx - r * 1.35 + sw * 0.6, by + r * 0.45), (bx - r * 1.3 + sw, by + r * 1.05),
                            (bx - r * 1.08 + sw * 0.8, by + r * 0.7), (bx - r * 0.9 + sw * 0.4, by + r * 0.3),
                            (bx - r * 0.45, by + 6)], tension=0.45)
        cv.drawPath(tail, fill("hair_bk")); cv.drawPath(tail, stroke("line", 2.8))
        cv.drawPath(smooth_path([(bx - r * 0.5, by - 2), (bx - r * 1.05 + sw * 0.4, by + r * 0.3), (bx - r * 1.15 + sw * 0.8, by + r * 0.85)],
                                close=False), stroke("#4a3a44", 2))

    def draw_hair_front(self, cv, p):
        r = self.head_r
        ox = self.face_offset(p)
        cap = smooth_path([(-r * 1.0, -r * 0.05), (-r * 0.98, -r * 0.62), (-r * 0.5, -r * 1.02), (ox * 0.4, -r * 1.08),
                           (r * 0.5, -r * 1.02), (r * 0.98, -r * 0.62), (r * 1.0, -r * 0.05), (r * 0.86, -r * 0.45),
                           (ox * 0.4, -r * 0.62), (-r * 0.86, -r * 0.45)], tension=0.5)
        cv.drawPath(cap, fill("hair_bk")); cv.drawPath(cap, stroke("line", 3))
        for k in (-0.5, -0.15, 0.2, 0.55):     # tight pulled-back comb lines
            cv.drawPath(smooth_path([(r * k + ox * 0.3, -r * 0.58), (r * k * 0.7 + ox * 0.2, -r * 0.92),
                                     (-r * 0.05, -r * 1.06)], close=False), stroke("#4a3a44", 1.8))
        # hair tie
        bx = -ox * 0.6 - r * 0.25
        cv.drawCircle(bx - 4, -r * 0.98, 7, fill("#f2c94c")); cv.drawCircle(bx - 4, -r * 0.98, 7, stroke("line", 2))

    def draw_head_extra(self, cv, p):
        ox = self.face_offset(p)
        for side in (-1, 1):
            far = side == 1
            ex = side * self.eye_dx * (1 - 0.25 * p.turn if far else 1) + ox
            cv.drawCircle(ex, self.eye_y, 15, fill("#ffffff", 0.14))
            cv.drawCircle(ex, self.eye_y, 15, stroke("#1a1a1a", 3.4))
        cv.drawLine(ox - 6, self.eye_y - 2, ox + 6, self.eye_y - 2, stroke("#1a1a1a", 3))


# =============================================================== ISHAAN
class Ishaan(Human):
    name = "ishaan"
    seed = 12
    flat = True
    height = 235
    head_r = 56
    neck_y = -150
    hip_y = -82
    hem_y = -58
    hem_w = 42
    body_top_w = 28
    shoulder_w = 22
    upper_arm = 34
    fore_arm = 32
    leg_w = 11
    thigh = 38
    shin = 34
    eye_dx = 20
    eye_rx = 10.5
    eye_ry = 13
    skin = "ishaan_skin"

    def body_colors(self):
        return ("orange_vest", K.shade("orange_vest", -0.25))

    def sleeve(self):
        return ("ishaan_skin", 0.0)

    def leg_colors(self):
        return ("ishaan_skin", "ishaan_skin")

    def body_path(self, p, breath):
        tw, hw = self.body_top_w, self.hem_w
        ny, hy = self.neck_y + 6, self.hem_y
        return smooth_path([(-tw * 0.4, ny - 2), (-tw - 2, ny + 4), (-tw + 6, ny + 22 + breath), (-tw - 6, ny + 40),
                            (-hw, hy), (0, hy + 3), (hw, hy), (tw + 6, ny + 40), (tw - 6, ny + 22 + breath),
                            (tw + 2, ny + 4), (tw * 0.4, ny - 2), (0, ny + 14)], tension=0.4)

    def body_detail(self, cv, p):
        cv.drawPath(smooth_path([(-16, self.neck_y + 4), (0, self.neck_y + 22), (16, self.neck_y + 4)], close=False),
                    stroke(K.shade("orange_vest", -0.3), 3))
        cv.drawCircle(-12, self.neck_y + 52, 5, fill("#c9302c", 0.6))    # a jam drip

    def draw_legs(self, cv, p):
        Human.draw_legs(self, cv, p)
        hy = self.hip_y
        sh = smooth_path([(-30, hy - 4), (30, hy - 4), (33, hy + 18), (4, hy + 20), (0, hy + 10), (-4, hy + 20),
                          (-33, hy + 18)], tension=0.2)
        if p.legs != "sit":
            cv.drawPath(sh, fill("khaki")); cv.drawPath(sh, stroke("line", self.line_w))

    def _leg(self, cv, hx, hy, fx, fy, trouser, foot, toe=1, point=False, from_knee=False):
        lw = self.leg_w
        path = limb(hx, hy, fx, fy - 8, lw * 1.9, lw * 1.6)
        cv.drawPath(path, fill(self.skin)); cv.drawPath(path, stroke("line", self.line_w))
        up = hx < 0     # screen-left leg: sock pulled up; the other scrunched at the ankle
        if up:
            sk = limb(lerp(hx, fx, 0.45), lerp(hy, fy, 0.45), fx, fy - 10, lw * 1.75, lw * 1.65)
            cv.drawPath(sk, fill("#fbfbf6")); cv.drawPath(sk, stroke("line", self.line_w * 0.9))
            cv.drawLine(lerp(hx, fx, 0.48) - 8, lerp(hy, fy, 0.48) + 4, lerp(hx, fx, 0.48) + 8, lerp(hy, fy, 0.48) + 4,
                        stroke("#e0413a", 2.4))
        else:
            for k in range(3):
                e = ellipse(fx + k * 1.5, fy - 12 - k * 4, 11, 4)
                cv.drawPath(e, fill("#fbfbf6")); cv.drawPath(e, stroke("line", 1.8))
        sh = K.rrect(fx - 11 + toe * 4, fy - 13, 26, 13, 6)
        cv.drawPath(sh, fill("#3b6fd1")); cv.drawPath(sh, stroke("line", self.line_w * 0.9))

    def draw_hair_front(self, cv, p):
        r = self.head_r
        ox = self.face_offset(p)
        sw = math.sin(p.t * 1.7) * 2
        pts = [(-r * 1.04, r * 0.05), (-r * 1.12, -r * 0.4), (-r * 0.85, -r * 0.95), (-r * 0.35, -r * 1.18),
               (r * 0.2, -r * 1.15), (r * 0.75, -r * 1.0), (r * 1.1, -r * 0.5), (r * 1.06, r * 0.02)]
        # fringe lobes falling over the forehead (down to the brows)
        fr = []
        for i in range(6):
            x = r * 0.95 - i * r * 0.38 + ox * 0.5
            fr += [(x, -r * 0.74 + sw), (x - r * 0.19, -r * 0.6 + (i % 2) * 3 + sw)]
        mop = smooth_path(pts + fr, tension=0.45)
        cv.drawPath(mop, fill("hair_bk")); cv.drawPath(mop, stroke("line", 3))
        cv.drawPath(smooth_path([(-r * 0.6, -r * 0.8), (-r * 0.25, -r * 1.0), (r * 0.15, -r * 0.98)], close=False),
                    stroke("#5a4a52", 3))

    brow_base = 3.0

    def draw_head_extra(self, cv, p):
        ox = self.face_offset(p)
        cv.drawPath(ellipse(ox + 30, 28, 7, 4.5), fill("#a3243a", 0.75))     # jam smudge
        Human.draw_brows(self, cv, p, ox)                                      # brows sit on top of the mop


# =============================================================== REHAN
class Rehan(Human):
    name = "rehan"
    seed = 13
    flat = True
    height = 335
    head_r = 53
    neck_y = -226
    hip_y = -126
    hem_y = -114
    hem_w = 38
    body_top_w = 33
    upper_arm = 57
    fore_arm = 53
    thigh = 66
    shin = 62
    leg_w = 11.5
    skin = "rehan_skin"

    def body_colors(self):
        return ("jersey", K.shade("jersey", -0.28))

    def sleeve(self):
        return ("jersey", 0.36)

    def leg_colors(self):
        return ("rehan_skin", "sneaker")

    def body_path(self, p, breath):
        tw, hw = self.body_top_w, self.hem_w
        ny, hy = self.neck_y + 6, self.hem_y
        return smooth_path([(-tw * 0.5, ny - 2), (-tw - 6, ny + 10 + breath), (-tw - 2, ny + 50), (-hw, hy),
                            (0, hy + 2), (hw, hy), (tw + 2, ny + 50), (tw + 6, ny + 10 + breath), (tw * 0.5, ny - 2),
                            (0, ny + 6)], tension=0.4)

    def body_detail(self, cv, p):
        ny = self.neck_y
        cv.drawPath(smooth_path([(-18, ny + 4), (0, ny + 16), (18, ny + 4)], close=False), stroke("#ffffff", 5))
        cv.drawRect(skia.Rect.MakeLTRB(-90, ny + 24, 90, ny + 30), fill("#ffffff", 0.9))
        cv.drawRect(skia.Rect.MakeLTRB(-90, self.hem_y - 10, 90, self.hem_y - 6), fill("#ffffff", 0.7))

    def draw_legs(self, cv, p):
        Human.draw_legs(self, cv, p)
        hy = self.hip_y
        if p.legs == "sit":
            sh = smooth_path([(-38, hy - 12), (38, hy - 12), (46, hy + 14), (30, hy + 26), (0, hy + 20), (-30, hy + 26),
                              (-46, hy + 14)], tension=0.25)
        else:
            sh = smooth_path([(-36, hy - 12), (36, hy - 12), (40, hy + 32), (6, hy + 34), (0, hy + 14), (-6, hy + 34),
                              (-40, hy + 32)], tension=0.2)
        cv.drawPath(sh, fill("navy")); cv.drawPath(sh, stroke("line", self.line_w))
        for x in (-37, 37):
            cv.drawLine(x, hy - 8, x * 1.06, hy + 30, stroke("#ffffff", 3))

    def _leg(self, cv, hx, hy, fx, fy, trouser, foot, toe=1, point=False, from_knee=False):
        lw = self.leg_w
        path = limb(hx, hy, fx, fy - 8, lw * 1.7, lw * 1.4)
        cv.drawPath(path, fill(self.skin)); cv.drawPath(path, stroke("line", self.line_w))
        kx, ky = lerp(hx, fx, 0.55), lerp(hy, fy, 0.55)                 # knobbly knees
        cv.drawCircle(kx, ky, lw * 0.85, fill(self.skin)); cv.drawCircle(kx, ky, lw * 0.85, stroke("line", 2.0))
        sh = K.rrect(fx - 12 + toe * 4, fy - 16, 31, 16, 7)
        cv.drawPath(sh, fill("sneaker")); cv.drawPath(sh, stroke("line", self.line_w * 0.9))
        cv.drawRect(skia.Rect.MakeLTRB(fx - 12 + toe * 4, fy - 4, fx + 19 + toe * 4, fy), fill("#1f9e8f"))

    def draw_hand(self, cv, x, y, ang, kind, skin, side, p):
        wx, wy = x - math.sin(ang) * 13, y - math.cos(ang) * 13
        cv.drawPath(limb(wx + math.sin(ang) * 4, wy + math.cos(ang) * 4, wx - math.sin(ang) * 4,
                         wy - math.cos(ang) * 4, 21, 21), fill("sweat"))
        cv.drawPath(limb(wx + math.sin(ang) * 4, wy + math.cos(ang) * 4, wx - math.sin(ang) * 4,
                         wy - math.cos(ang) * 4, 21, 21), stroke("line", 2.2))
        Human.draw_hand(self, cv, x, y, ang, "fist" if kind == "ball" else kind, skin, side, p)
        if kind == "ball":
            draw_ball(cv, x + math.sin(ang) * 6, y + math.cos(ang) * 6 + 2, 0.85)

    def draw_hair_front(self, cv, p):
        r = self.head_r
        ox = self.face_offset(p)
        hair = smooth_path([(-r * 1.0, -r * 0.2), (-r * 0.95, -r * 0.7), (-r * 0.45, -r * 1.05), (r * 0.2, -r * 1.08),
                            (r * 0.8, -r * 0.85), (r * 1.0, -r * 0.25), (r * 0.8, -r * 0.55), (r * 0.3 + ox * 0.4, -r * 0.62),
                            (-r * 0.2 + ox * 0.4, -r * 0.5), (-r * 0.8, -r * 0.55)], tension=0.45)
        cv.drawPath(hair, fill("hair_bk")); cv.drawPath(hair, stroke("line", 3))
        lick = smooth_path([(r * 0.05, -r * 1.04), (r * 0.18, -r * 1.36), (r * 0.32, -r * 1.06)], tension=0.4)
        cv.drawPath(lick, fill("hair_bk")); cv.drawPath(lick, stroke("line", 2.6))


def bowling_hop(u: float) -> float:
    """Vertical offset (units, negative = up) for the gather leap; subtract from y * s in scenes."""
    k = (clamp(u) - 0.55) / 0.2
    return -40 * math.sin(math.pi * k) if 0 < k < 1 else 0.0


def bowling_pose(u: float) -> dict:
    """Rehan's bowling action (character faces screen-right with flip=False; use flip=True to bowl left).
    u: 0..0.55 run-up, 0.55..0.70 gather & leap, 0.70..0.84 delivery (arm over the top), 0.84..1 follow-through."""
    u = clamp(u)
    if u < 0.55:
        k = u / 0.55
        ph = k * 4.0
        return dict(legs="walk", phase=ph, lean=8 + 6 * k, expr="determined", turn=0.6,
                    arms={"l": (25 + 30 * math.sin(ph * 6.28), 70), "r": (25 - 30 * math.sin(ph * 6.28), 70)},
                    hand={"r": "ball"})
    if u < 0.70:   # gather: front arm reaches up toward the target, bowling arm swings back
        k = K.ease_out((u - 0.55) / 0.15)
        return dict(legs="walk", phase=0.25, lean=lerp(14, -12, k), expr="determined", turn=0.8,
                    arms={"l": (lerp(30, 172, k), lerp(60, 4, k)), "r": (lerp(30, 250, k), lerp(60, 10, k))},
                    hand={"r": "ball", "l": "point"})
    if u < 0.84:   # delivery: bowling arm from behind, straight up over the top, releasing forward
        k = (u - 0.70) / 0.14
        e = K.ease_in_out(k)
        return dict(legs="walk", phase=0.5, lean=lerp(-12, 20, e), expr="angry", turn=0.8,
                    arms={"l": (lerp(172, 25, e), 30), "r": (lerp(250, 70, e), 4)},
                    hand={"r": "ball" if k < 0.6 else "open", "l": "fist"})
    k = (u - 0.84) / 0.16   # follow-through: arm sweeps down and across, body pitches forward
    return dict(legs="walk", phase=lerp(0.5, 0.75, k), lean=lerp(20, 26, k), expr="surprised", turn=0.8,
                arms={"l": (lerp(25, 15, k), 40), "r": (lerp(70, -20, k), 10)}, hand={"r": "open"})


# =============================================================== MEGHNATH
class Meghnath(Human):
    name = "meghnath"
    seed = 14
    flat = True
    height = 365
    head_r = 52
    neck_y = -256
    hip_y = -146
    hem_y = -124
    hem_w = 46
    body_top_w = 35
    shoulder_w = 31
    upper_arm = 60
    fore_arm = 56
    thigh = 74
    shin = 70
    leg_w = 13
    stoop = 11
    skin = "megh_skin"
    eye_rx = 7.5
    eye_ry = 8.5
    eye_dx = 20

    def body_colors(self):
        return ("cardigan", "cardigan_dk")

    def sleeve(self):
        return ("cardigan", 0.94)

    def leg_colors(self):
        return ("trouser", "megh_skin")

    def _cardigan(self, p):
        return p.extra.get("cardigan", True)

    def draw_body(self, cv, p, breath):
        if not self._cardigan(p):
            self.body_colors = lambda: ("shirt_check", K.shade("shirt_check", -0.25))   # noqa: E731
            self.sleeve = lambda: ("shirt_check", 0.35)                                 # noqa: E731
        else:
            self.body_colors = Meghnath.body_colors.__get__(self)
            self.sleeve = Meghnath.sleeve.__get__(self)
        Human.draw_body(self, cv, p, breath)

    def body_detail(self, cv, p):
        ny, hy = self.neck_y, self.hem_y
        if self._cardigan(p):
            cv.drawPath(K.poly([(-14, ny + 4), (0, ny + 40), (14, ny + 4)]), fill("#efe6d6"))   # vest V
            cv.drawLine(0, ny + 40, 0, hy, stroke("cardigan_dk", 3))
            for i in range(5):
                cv.drawCircle(4, ny + 50 + i * 20, 3.5, fill("#d9c49a"))
                cv.drawCircle(4, ny + 50 + i * 20, 3.5, stroke("line", 1.4))
            cv.drawRect(skia.Rect.MakeLTRB(-90, hy - 14, 90, hy + 4), fill("cardigan_dk"))
            for i in range(-9, 10):
                cv.drawLine(i * 6, hy - 13, i * 6, hy + 2, stroke("#5a3820", 1.4))
            cv.drawPath(K.rrect(-34, hy - 50, 22, 18, 3), stroke("cardigan_dk", 2.4))    # pocket
        else:
            for i in range(-6, 7):
                cv.drawLine(i * 12, ny, i * 12, hy, stroke("#7fa2c4", 2))
            for j in range(8):
                cv.drawLine(-90, ny + 12 + j * 16, 90, ny + 12 + j * 16, stroke("#7fa2c4", 1.6))

    def draw_legs(self, cv, p):
        mode = p.legs
        if mode in ("stand", "walk", "tiptoe"):
            Human.draw_legs(self, cv, p)
        else:
            Human.draw_legs(self, cv, p)

    def _leg(self, cv, hx, hy, fx, fy, trouser, foot, toe=1, point=False, from_knee=False):
        lw = self.leg_w
        path = limb(hx, hy, fx, fy - 8, lw * 2.1, lw * 1.8)
        cv.drawPath(path, fill("trouser")); cv.drawPath(path, stroke("line", self.line_w))
        ch = K.rrect(fx - 14 + toe * 5, fy - 9, 32, 9, 4)
        cv.drawPath(ellipse(fx + toe * 5 + 2, fy - 8, 14, 6), fill(self.skin))
        cv.drawPath(ch, fill("#5a3a22")); cv.drawPath(ch, stroke("line", self.line_w * 0.9))

    def draw_arm(self, cv, p, side, back):
        if side == "r" and p.extra.get("sling"):
            self._sling_arm(cv, p)
            return
        Human.draw_arm(self, cv, p, side, back)

    def _sling_arm(self, cv, p):
        sx, sy = self.shoulder_w + 4, self.neck_y + 16
        ex, ey = sx + 6, sy + self.upper_arm * 0.95
        hx, hy = -8, ey - 14
        col = "cardigan" if self._cardigan(p) else "shirt_check"
        cv.drawPath(limb(sx, sy, ex, ey, 26, 24), fill(col)); cv.drawPath(limb(sx, sy, ex, ey, 26, 24), stroke("line", self.line_w))
        cv.drawPath(limb(ex, ey, hx, hy, 23, 20), fill(col)); cv.drawPath(limb(ex, ey, hx, hy, 23, 20), stroke("line", self.line_w))
        hp = ellipse(hx - 6, hy, 11, 10)
        cv.drawPath(hp, fill(self.skin)); cv.drawPath(hp, stroke("line", self.line_w * 0.9))
        # sling cloth: a triangle cradling the forearm, strap to the opposite shoulder
        cloth = smooth_path([(ex + 12, ey - 14), (ex + 8, ey + 18), (hx - 4, hy + 26), (hx - 14, hy + 2), (hx + 4, hy - 4)],
                            tension=0.35)
        cv.drawPath(cloth, fill("sling")); cv.drawPath(cloth, stroke("line", self.line_w))
        cv.drawLine(hx - 12, hy - 2, -self.shoulder_w + 6, self.neck_y + 8, stroke("line", 9))
        cv.drawLine(hx - 12, hy - 2, -self.shoulder_w + 6, self.neck_y + 8, stroke("sling", 6))
        cv.drawLine(ex + 10, ey - 12, self.shoulder_w - 2, self.neck_y + 8, stroke("line", 9))
        cv.drawLine(ex + 10, ey - 12, self.shoulder_w - 2, self.neck_y + 8, stroke("sling", 6))
        for i in range(3):
            cv.drawLine(ex - 6 - i * 12, ey + 6 + i * 3, ex - 2 - i * 12, ey + 14 + i * 3, stroke("#d9d2c4", 1.6))

    def draw_hair_back(self, cv, p):
        pass

    def draw_hair_front(self, cv, p):
        r = self.head_r
        ox = self.face_offset(p)
        wet = clamp(p.extra.get("wet", 0.0))
        # bald crown with a white fringe round the sides and back
        for side in (-1, 1):
            if side == 1 and p.turn > 0.7:
                continue
            x0 = side * r * 0.98 - ox * 0.3
            fr = smooth_path([(x0 - side * 4, -r * 0.62), (x0 + side * 9, -r * 0.48), (x0 + side * 13, -r * 0.18 + wet * 6),
                              (x0 + side * 8, r * 0.12 + wet * 10), (x0 - side * 2, r * 0.2), (x0 - side * 6, -r * 0.2)],
                             tension=0.5)
            cv.drawPath(fr, fill("white_hair")); cv.drawPath(fr, stroke("line", 2.4))
        cv.drawPath(smooth_path([(-r * 0.3 + ox, -r * 0.82), (-r * 0.05 + ox, -r * 0.9)], close=False),
                    stroke("#ffffff", 3, 0.5))      # scalp shine
        for k in range(2):                           # forehead lines
            y = -r * 0.5 + k * 8
            cv.drawPath(smooth_path([(ox - 16, y), (ox, y - 2), (ox + 16, y)], close=False), stroke("#8a5a3e", 1.5))

    def draw_brows(self, cv, p, ox):
        """The awnings: big fluffy white tufts that sweep out past the face and droop or lift with mood."""
        e = p.expr
        wet = clamp(p.extra.get("wet", 0.0))
        lift = {"surprised": 1.0, "awe": 0.9, "laugh": 0.75, "happy": 0.5, "grin": 0.45, "neutral": 0.0,
                "worried": 0.15, "sad": -0.6, "cry": -0.6, "sleepy": -0.8, "angry": -0.35, "determined": -0.2,
                "smug": 0.05, "wince": -0.4}.get(e, 0.0) + p.extra.get("brow_lift", 0.0) + p.brow * 0.5
        lift = clamp(lift, -1, 1)
        frown = {"angry": 1.0, "determined": 0.6, "wince": 0.5}.get(e, 0.0)
        worry = {"worried": 1.0, "sad": 0.8, "cry": 0.9}.get(e, 0.0)
        bounce = math.sin(p.t * 9) * 2.5 if e == "laugh" else 0.0
        for side in (-1, 1):
            far = side == 1
            bx = side * self.eye_dx * (1 - 0.25 * p.turn if far else 1) + ox
            base_y = self.eye_y - 12 - lift * 9 + bounce
            cv.save()
            cv.translate(bx - side * 10, base_y + frown * 5 - worry * 5)
            # rotate the whole awning about its inner root: droop (positive outward-down) .. lift
            ang = side * (18 - 30 * lift + 10 * worry - 8 * frown)
            if wet:
                ang = lerp(ang, side * 4, wet)
            cv.rotate(ang)
            L = 46 * (1 - 0.25 * wet)
            T = 15 * (1 - 0.45 * wet)
            pts = [(0, 4), (side * 4, -T * 0.7), (side * L * 0.45, -T), (side * L * 0.85, -T * 0.55),
                   (side * (L + 6), T * 0.2), (side * L * 0.92, T * 0.9), (side * L * 0.7, T * 0.4),
                   (side * L * 0.5, T * 0.85), (side * L * 0.3, T * 0.45), (side * L * 0.12, T * 0.8)]
            brow = smooth_path(pts, tension=0.45)
            cv.drawPath(brow, fill("white_hair")); cv.drawPath(brow, stroke("line", 2.4))
            for k in range(4):
                y0 = -T * 0.4 + k * T * 0.28
                cv.drawPath(smooth_path([(side * 6, y0), (side * L * 0.5, y0 - 2), (side * L * 0.85, y0 + 3 + k)],
                                        close=False), stroke("#cfc8bc", 1.4))
            cv.restore()

    def draw_head_extra(self, cv, p):
        ox = self.face_offset(p)
        # big nose
        nose = smooth_path([(ox + 1, 2), (ox + 9 + p.turn * 4, 16), (ox + 13 + p.turn * 4, 26), (ox + 4, 31),
                            (ox - 7, 27), (ox - 4, 18)], tension=0.55)
        cv.drawPath(nose, fill(K.shade(self.skin, -0.06))); cv.drawPath(nose, stroke("line", 2.4))
        # cheek / mouth lines
        for side in (-1, 1):
            x = ox + side * 18
            cv.drawPath(smooth_path([(x, 24), (x + side * 4, 34), (x + side * 2, 42)], close=False), stroke("#8a5a3e", 1.6))

    def draw_mouth(self, cv, p, ox):
        # mouth sits lower under the big nose
        cv.save(); cv.translate(0, 6)
        Human.draw_mouth(self, cv, p, ox)
        cv.restore()

    def face_offset(self, p):
        return p.turn * 11


# =============================================================== DADI (head rig only)
class _DadiHead(Human):
    name = "dadi"
    seed = 15
    flat = True
    head_r = 50
    skin = "#b9845d"

    def draw_hair_back(self, cv, p):
        r = self.head_r
        cv.drawPath(ellipse(-r * 0.2, -r * 0.95, r * 0.4, r * 0.3), fill("white_hair"))
        cv.drawPath(ellipse(-r * 0.2, -r * 0.95, r * 0.4, r * 0.3), stroke("line", 2.4))

    def draw_hair_front(self, cv, p):
        r = self.head_r
        h = smooth_path([(-r * 1.02, 0), (-r * 0.9, -r * 0.65), (-r * 0.3, -r * 1.02), (r * 0.3, -r * 1.02), (r * 0.9, -r * 0.65),
                         (r * 1.02, 0), (r * 0.8, -r * 0.4), (0, -r * 0.65), (-r * 0.8, -r * 0.4)], tension=0.5)
        cv.drawPath(h, fill("#e8e4dc")); cv.drawPath(h, stroke("line", 2.6))
        cv.drawCircle(0, -r * 0.42, 3, fill("#b0252f"))


_DADI = _DadiHead()


def draw_dadi(cv, x, y, s=1.0, t=0.0, fan=1.0):
    """Dadi lying on her bed (side view, head screen-left) fanning slowly with a newspaper.
    (x, y) = floor point under the middle of the bed."""
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    # bed
    for lx in (-230, 230):
        cv.drawRect(skia.Rect.MakeLTRB(lx - 8, -110, lx + 8, 0), fill("#6c4a32"))
        cv.drawRect(skia.Rect.MakeLTRB(lx - 8, -110, lx + 8, 0), stroke("line", 2.6))
    cv.drawRect(skia.Rect.MakeLTRB(-250, -150, -232, 0), fill("#6c4a32")); cv.drawRect(skia.Rect.MakeLTRB(-250, -150, -232, 0), stroke("line", 2.6))
    mat = K.rrect(-240, -126, 480, 30, 10)
    cv.drawPath(mat, fill("#e8dcc6")); cv.drawPath(mat, stroke("line", 3))
    pil = K.rrect(-232, -152, 110, 34, 16)
    cv.drawPath(pil, fill("#f6f1e6")); cv.drawPath(pil, stroke("line", 3))
    # body under a thin cotton sheet with slow breathing
    br = math.sin(t * 1.4) * 3
    sheet = smooth_path([(-140, -126), (-120, -170 - br), (0, -178 - br), (120, -168), (210, -150), (232, -126)], tension=0.5)
    cv.drawPath(sheet, fill("#d6e2ea")); cv.drawPath(sheet, stroke("line", 3))
    for i in range(4):
        cv.drawLine(-80 + i * 60, -168 - br, -60 + i * 60, -128, stroke("#b9cbd6", 2))
    # head on pillow (tilted to lie down)
    cv.save(); cv.translate(-178, -170); cv.rotate(-70)
    _DADI.draw_head(cv, Pose(expr="sleepy", blink=0.7, t=t, turn=0.3))
    cv.restore()
    # fanning arm + newspaper
    ang = -20 + math.sin(t * 2.0) * 22 * fan
    cv.save(); cv.translate(-110, -168 - br); cv.rotate(ang)
    cv.drawPath(limb(0, 0, -10, -60, 18, 15), fill("#e9e4dc")); cv.drawPath(limb(0, 0, -10, -60, 18, 15), stroke("line", 2.6))
    cv.drawCircle(-10, -64, 10, fill(_DADI.skin)); cv.drawCircle(-10, -64, 10, stroke("line", 2.4))
    cv.save(); cv.translate(-10, -70)
    draw_newspaper(cv, 0, 0, 1.0, folded=True)
    cv.restore()
    cv.restore()
    cv.restore()


# =============================================================== VARSHA
class _Varsha(Human):
    name = "varsha"
    seed = 16
    flat = True
    head_r = 54
    skin = "#c3906a"
    lash = True

    def draw_hair_back(self, cv, p):
        r = self.head_r
        t = p.t
        w = math.sin(t * 2.5) * 6
        hair = smooth_path([(-r * 0.6, -r * 1.0), (r * 0.6, -r * 1.05), (r * 1.6 + w, -r * 0.9), (r * 2.4 + w * 2, -r * 0.4),
                            (r * 2.1 + w, -r * 0.05), (r * 2.7 + w * 1.5, r * 0.4), (r * 1.6 + w, r * 0.6), (r * 1.0, r * 0.9),
                            (-r * 0.9, r * 0.8), (-r * 1.2, 0)], tension=0.45)
        cv.drawPath(hair, fill("hair_bk")); cv.drawPath(hair, stroke("line", 2.6))
        for k in range(3):
            y = -r * 0.5 + k * r * 0.4
            cv.drawPath(smooth_path([(r * 1.2, y), (r * 1.8 + w, y - 6), (r * 2.4 + w, y + 2)], close=False),
                        stroke("#4a3a44", 2))

    def draw_hair_front(self, cv, p):
        r = self.head_r
        h = smooth_path([(-r * 1.02, -r * 0.1), (-r * 0.9, -r * 0.7), (-r * 0.2, -r * 1.06), (r * 0.6, -r * 0.98),
                         (r * 1.1, -r * 0.5), (r * 0.7, -r * 0.62), (0, -r * 0.55), (-r * 0.7, -r * 0.4)], tension=0.5)
        cv.drawPath(h, fill("hair_bk")); cv.drawPath(h, stroke("line", 2.6))
        cv.drawCircle(4, -r * 0.4, 3.2, fill("#c0262f"))


_VARSHA = _Varsha()


def draw_varsha_photo(cv, x, y, s=1.0, t=0.0, glass=1.0):
    """Framed photograph (centre x,y): Varsha laughing, hair full of wind. ~220x280 at s=1."""
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawPath(K.rrect(-118, -148, 236, 296, 8), fill("#5a3a22")); cv.drawPath(K.rrect(-118, -148, 236, 296, 8), stroke("line", 3))
    cv.drawRect(skia.Rect.MakeLTRB(-104, -134, 104, 134), fill("#efe4cc"))
    inner = skia.Rect.MakeLTRB(-90, -120, 90, 120)
    cv.save(); cv.clipRect(inner)
    cv.drawRect(inner, K.lin((0, -120), (0, 120), ["#8fc3e8", "#d8ecf6"]))
    for k in range(4):   # wind streaks
        yy = -90 + k * 34
        cv.drawLine(-80, yy, -20, yy - 6, stroke("#ffffff", 3, 0.7))
    cv.drawPath(smooth_path([(-90, 130), (-60, 60), (0, 44), (60, 60), (90, 130)]), fill("#c94f6d"))
    cv.drawPath(smooth_path([(-90, 130), (-60, 60), (0, 44), (60, 60), (90, 130)]), stroke("line", 2.6))
    cv.save(); cv.translate(-8, -6); cv.scale(0.95, 0.95); cv.rotate(-8)
    _VARSHA.draw_head(cv, Pose(expr="laugh", blink=1.0, mouth=0.75, t=t, turn=0.25))
    cv.restore()
    cv.restore()
    cv.drawRect(inner, stroke("line", 2))
    if glass:
        cv.drawPath(K.poly([(-80, -120), (-40, -120), (-90, -40), (-90, -80)]), fill("#ffffff", 0.18 * glass))
    cv.restore()


def draw_silhouette(cv, who, x, y, s, color="#1d1430", **pose):
    """A flat dark silhouette of a rig (memory scene). who='meghnath' (young-ish, no sling) or 'varsha'."""
    r, g, b = K.hexrgb(color)
    m = [0, 0, 0, 0, r, 0, 0, 0, 0, g, 0, 0, 0, 0, b, 0, 0, 0, 1, 0]
    with K.layer(cv, color_filter=K.matrix_filter(m)):
        if who == "varsha":
            _WOMAN.draw(cv, Pose(x=x, y=y, s=s, **pose))
        else:
            rig = CAST["meghnath"]
            p = Pose(x=x, y=y, s=s, **pose)
            p.extra = dict(p.extra or {}, sling=False)
            rig.draw(cv, p)


class _Woman(Human):
    """Varsha full-figure (used only as a silhouette): sari silhouette, long wind-blown hair."""
    flat = True
    height = 320
    head_r = 50
    hem_y = -6
    hem_w = 60
    skin = "#c3906a"

    def draw_legs(self, cv, p):
        pass

    def draw_hair_back(self, cv, p):
        _VARSHA.draw_hair_back(cv, p)

    def draw_hair_front(self, cv, p):
        _VARSHA.draw_hair_front(cv, p)


_WOMAN = _Woman()


# =============================================================== BHAAP
_PUFFS = [(0, 0, 1.0), (-0.62, 0.18, 0.62), (0.62, 0.16, 0.64), (-0.35, -0.42, 0.62), (0.36, -0.44, 0.58),
          (0.0, -0.68, 0.5), (-0.95, 0.38, 0.4), (0.96, 0.36, 0.42), (-0.4, 0.52, 0.55), (0.42, 0.52, 0.55)]


def draw_bhaap(cv, x, y, s=1.0, t=0.0, mood="happy", mouth=0.0, rain=0.0, spark=0.0, grey=0.0, squash=0.0,
               look=(0.0, 0.0), blink=None, alpha=1.0, glow=1.0):
    """Bhaap, the baby cloud (centre x,y). ~90 px wide at s=1. squash: -1 stretch (zoom) .. 1 squash (landing)."""
    R = 40.0
    cv.save(); cv.translate(x, y + math.sin(t * 1.8) * 4 * s); cv.scale(s, s)
    if alpha < 1:
        pt = skia.Paint(); pt.setAlphaf(clamp(alpha)); cv.saveLayer(None, pt)
    sx, sy = 1 + 0.22 * squash, 1 - 0.18 * squash
    if squash < 0:
        sx, sy = 1 + 0.12 * squash, 1 - 0.25 * squash
    cv.scale(sx, sy)
    white = K.mix("#ffffff", "#9aa3ad", grey)
    shade_c = K.mix("#dfe9f4", "#7d8792", grey)
    line = K.mix("#4a5a70", "#3a4048", grey)
    if glow and grey < 0.8:
        cv.drawCircle(0, 0, R * 2.4, K.rad_a((0, 0), R * 2.4, [("#ffffff", 0.32 * glow * (1 - grey)), ("#ffffff", 0)]))
    puffs = []
    for i, (px, py, pr) in enumerate(_PUFFS):
        br = 1 + 0.05 * math.sin(t * 2.2 + i * 1.3)
        puffs.append((px * R, py * R, pr * R * br))
    # outline pass then fill passes (union-of-circles cloud), flat cel shadow underneath
    for (px, py, pr) in puffs:
        cv.drawCircle(px, py, pr + 3.0, fill(line))
    for (px, py, pr) in puffs:
        cv.drawCircle(px, py, pr, fill(shade_c))
    for (px, py, pr) in puffs:
        cv.drawCircle(px, py - pr * 0.16, pr * 0.9, fill(white))
    cv.drawCircle(-R * 0.35, -R * 0.62, R * 0.16, fill("#ffffff", 0.9 * (1 - grey)))
    # face
    lx, ly = look
    if blink is None:
        blink = auto_blink(t, 21)
    ex, ey, er = R * 0.32, -R * 0.02, R * 0.12
    big = 1.25 if mood == "excited" else 1.0
    for side in (-1, 1):
        cx, cy = side * ex + lx * 5, ey + ly * 4
        if mood == "sleepy" or blink > 0.9:
            cv.drawPath(smooth_path([(cx - er, cy), (cx, cy + er * 0.6), (cx + er, cy)], close=False), stroke("#1b1f2a", 3))
            continue
        if mood == "happy" and mouth > 0.5:
            cv.drawPath(smooth_path([(cx - er, cy + 2), (cx, cy - er * 0.9), (cx + er, cy + 2)], close=False),
                        stroke("#1b1f2a", 3.2))
            continue
        cv.drawPath(ellipse(cx, cy, er * 0.85 * big, er * 1.15 * big), fill("#1b1f2a"))
        cv.drawCircle(cx - er * 0.3, cy - er * 0.45, er * 0.32 * big, fill("#ffffff"))
        lid = {"sad": 0.35, "tired": 0.55, "shy": 0.25}.get(mood, 0.0)
        if lid:
            cv.save(); cv.clipRect(skia.Rect.MakeLTRB(cx - er * 1.4, cy - er * 1.6, cx + er * 1.4, cy - er * 1.6 + er * 2.6 * lid))
            cv.drawCircle(cx, cy, er * 1.5, fill(white))
            cv.restore()
            tilt = 1 if mood == "sad" else 0
            ly0 = cy - er * 1.6 + er * 2.6 * lid
            # sad: inner end higher, outer end lower (droopy), never the angry slant
            cv.drawLine(cx - er * 1.1, ly0 - side * tilt * 4, cx + er * 1.1, ly0 + side * tilt * 4,
                        stroke("#1b1f2a", 2.4))
    if mood in ("happy", "excited", "shy"):
        for side in (-1, 1):
            cv.drawPath(ellipse(side * R * 0.55 + lx * 4, R * 0.18, R * 0.12, R * 0.07), fill("#ffb3c4", 0.8 * (1 - grey)))
    if mood in ("happy", "excited") and mouth > 0.02:
        m = clamp(mouth)
        mx, my = lx * 4, R * 0.2 + ly * 3
        if m < 0.35:
            cv.drawPath(smooth_path([(mx - 7, my), (mx, my + 5), (mx + 7, my)], close=False), stroke("#1b1f2a", 2.6))
        else:
            mp = smooth_path([(mx - 8, my - 1), (mx + 8, my - 1), (mx, my + 4 + m * 8)], tension=0.6)
            cv.drawPath(mp, fill("#5a1e2a")); cv.drawPath(mp, stroke("#1b1f2a", 2))
    if alpha < 1:
        cv.restore()
    cv.restore()
    # rain (under the cloud, not squashed)
    if rain > 0.01:
        rng = K.rng(77)
        n = int(6 + 14 * rain)
        for i in range(n):
            rx = x + rng.uniform(-R * 0.9, R * 0.9) * s
            span = (34 + 40 * rain) * s
            top = y + R * 0.85 * s
            ry = top + ((t * (200 + rng.uniform(0, 80)) * s + rng.uniform(0, span)) % span)
            a = clamp(rain) * (1 - (ry - top) / span) * alpha
            cv.drawLine(rx, ry, rx - 2 * s, ry + 12 * s, stroke("#6fa6e0", 2.4 * s, a))
    if spark > 0.01:
        rng = K.rng(91)
        for i in range(7):
            on = math.sin(t * rng.uniform(9, 15) + i * 2.1) > 1 - 1.7 * spark
            if not on:
                continue
            ang = rng.uniform(0, 6.28) + t * 0.5
            dist = R * rng.uniform(1.05, 1.5) * s
            bx, by = x + math.cos(ang) * dist, y + math.sin(ang) * dist * 0.8
            z = [(bx, by), (bx + 6 * s, by + 8 * s), (bx - 2 * s, by + 10 * s), (bx + 6 * s, by + 20 * s)]
            pth = poly(z, close=False)
            cv.drawPath(pth, stroke("#fff3a0", 5 * s, 0.5 * alpha))
            cv.drawPath(pth, stroke("#ffffff", 2 * s, alpha))


# =============================================================== CAPTAIN (pigeon)
def draw_pigeon(cv, x, y, s=1.0, t=0.0, flip=False, mode="stand", head_bob=0.0, lid=0.45, captain=True):
    """Pigeon side view, origin at feet. ~70 px long at s=1. mode: stand | one_leg | flap | fly | bath | turn_away."""
    cv.save(); cv.translate(x, y); cv.scale(-s if flip else s, s)
    body_c, dark, neck_a, neck_b = "#8f9bb0", "#5d6880", "#3f9a7a", "#8b5aa8"
    bob = head_bob * math.sin(t * 8) * 5
    ground = mode not in ("fly", "flap")
    if ground and mode != "bath":
        legs = [(-4, 0)] if mode == "one_leg" else [(-8, 0), (4, 0)]
        for lx, _ in legs:
            cv.drawLine(lx, -14, lx, 0, stroke("#e87a8a", 3))
            cv.drawLine(lx - 5, 0, lx + 6, 0, stroke("#e87a8a", 3))
    by = -26 if mode != "bath" else -10
    if mode == "turn_away":
        cv.scale(-1, 1)
    # tail
    tail = poly([(-26, by - 2), (-48, by - 8), (-46, by + 4)])
    cv.drawPath(tail, fill(dark)); cv.drawPath(tail, stroke("line", 2))
    body = ellipse(-4, by, 28, 15)
    cv.drawPath(body, fill(body_c)); cv.drawPath(body, stroke("line", 2.4))
    # wing
    if mode in ("flap", "fly"):
        w = math.sin(t * (18 if mode == "flap" else 10)) * 40
        cv.save(); cv.translate(-2, by - 6); cv.rotate(-w - 20)
        wing = smooth_path([(0, 0), (-20, -30), (-6, -40), (14, -12)], tension=0.4)
        cv.drawPath(wing, fill(K.shade(body_c, 0.1))); cv.drawPath(wing, stroke("line", 2.2))
        cv.restore()
    else:
        wing = smooth_path([(14, by - 6), (-20, by - 8), (-30, by + 2), (6, by + 6)], tension=0.4)
        cv.drawPath(wing, fill(K.shade(body_c, -0.08))); cv.drawPath(wing, stroke("line", 2))
        for k in range(2):
            cv.drawLine(-8 - k * 8, by - 4, -2 - k * 8, by + 2, stroke("#3a3f52", 2.4))
    if mode == "turn_away":
        cv.drawCircle(18, by - 16 + bob * 0.3, 10, fill(neck_a)); cv.drawCircle(18, by - 16, 10, stroke("line", 2.2))
        cv.restore()
        return
    # neck + head
    hx, hy = 20 + bob, by - 18
    cv.drawPath(limb(10, by - 4, hx - 2, hy + 4, 16, 13), fill(neck_a))
    cv.drawPath(limb(10, by - 4, hx - 2, hy + 4, 16, 13), stroke("line", 2))
    cv.drawPath(ellipse(10, by - 2, 8, 6), fill(neck_b, 0.8))
    cv.drawCircle(hx, hy, 11, fill(body_c)); cv.drawCircle(hx, hy, 11, stroke("line", 2.4))
    cv.drawPath(poly([(hx + 9, hy - 1), (hx + 19, hy + 3), (hx + 9, hy + 4)]), fill("#3a2a2a"))
    cv.drawCircle(hx + 9, hy - 2, 2.6, fill("#f2efe6"))
    # opinionated eye: orange iris, heavy skeptical lid
    cv.drawCircle(hx + 2, hy - 2, 5, fill("#f28a2a")); cv.drawCircle(hx + 2, hy - 2, 2.2, fill("#111"))
    cv.save(); cv.clipRect(skia.Rect.MakeLTRB(hx - 5, hy - 9, hx + 9, hy - 9 + 12 * lid))
    cv.drawCircle(hx + 2, hy - 2, 5.6, fill(body_c))
    cv.restore()
    cv.drawLine(hx - 4, hy - 9 + 12 * lid, hx + 8, hy - 9 + 12 * lid - 1, stroke("line", 1.8))
    if mode == "bath":
        rng = K.rng(5)
        for i in range(8):
            ph = (t * 3 + i / 8) % 1
            ang = rng.uniform(0.3, 2.8)
            dx, dy = math.cos(ang) * 40 * ph, -math.sin(ang) * 30 * ph + 40 * ph * ph
            cv.drawCircle(-4 + dx, by + dy, 3 * (1 - ph), fill("#8fc3e8", 1 - ph))
    cv.restore()


def draw_pigeon_flock(cv, t, x, y, n=9, spread=300, s=1.0, color="#3a3f52", seed=1, speed=60.0):
    """Distant pigeons as flapping silhouettes drifting right."""
    rng = K.rng(seed)
    for i in range(n):
        px = x + rng.uniform(-spread, spread) + t * speed * rng.uniform(0.7, 1.3)
        py = y + rng.uniform(-spread * 0.35, spread * 0.35) + math.sin(t * 2 + i) * 6
        w = math.sin(t * rng.uniform(10, 14) + i) * 0.8
        sc = s * rng.uniform(0.6, 1.2)
        p = skia.Path()
        p.moveTo(px - 14 * sc, py - 8 * sc * w)
        p.quadTo(px - 6 * sc, py - 2 * sc, px, py)
        p.quadTo(px + 6 * sc, py - 2 * sc, px + 14 * sc, py - 8 * sc * w)
        cv.drawPath(p, stroke(color, 3 * sc))
        cv.drawCircle(px, py + 1 * sc, 2.6 * sc, fill(color))


# =============================================================== PROPS
def draw_ball(cv, x, y, s=1.0):
    cv.drawCircle(x, y, 9 * s, fill("ball")); cv.drawCircle(x, y, 9 * s, stroke("line", 2 * s))
    p = skia.Path(); p.moveTo(x - 8 * s, y - 3 * s); p.quadTo(x, y + 5 * s, x + 8 * s, y - 3 * s)
    cv.drawPath(p, stroke("#ffffff", 1.6 * s))


def draw_notebook(cv, x, y, s=1.0, open_=False):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    if open_:
        for d in (-1, 1):
            pg = K.poly([(0, -18), (d * 34, -22), (d * 34, 22), (0, 24)])
            cv.drawPath(pg, fill("#fffaf0")); cv.drawPath(pg, stroke("line", 2.2))
            for k in range(4):
                cv.drawLine(d * 6, -10 + k * 8, d * 28, -12 + k * 8, stroke("#9db7d6", 1.2))
    else:
        cv.drawPath(K.rrect(-20, -26, 40, 52, 4), fill("#3f6fb5")); cv.drawPath(K.rrect(-20, -26, 40, 52, 4), stroke("line", 2.4))
        cv.drawRect(skia.Rect.MakeLTRB(16, -24, 20, 24), fill("#fffaf0"))
        for k in range(6):
            cv.drawCircle(-20, -20 + k * 8, 3, stroke("#cfd6e3", 1.8))
        cv.drawLine(-22, -30, -30, 18, stroke("#f2c94c", 5)); cv.drawLine(-30, 18, -31, 23, stroke("line", 2.4))
    cv.restore()


def draw_stove(cv, x, y, s=1.0, flame=1.0, t=0.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawPath(K.rrect(-46, -20, 92, 20, 4), fill("#3d3f46")); cv.drawPath(K.rrect(-46, -20, 92, 20, 4), stroke("line", 2.4))
    for i in range(5):
        fh = (10 + 4 * math.sin(t * 20 + i)) * flame
        cv.drawPath(ellipse(-20 + i * 10, -22 - fh / 2, 4, fh / 2), fill("#4f8de8", 0.9))
    cv.restore()


def draw_pressure_cooker(cv, x, y, s=1.0, t=0.0, whistle=0.0, steam=0.0, flip=False):
    """Aluminium pressure cooker standing on (x,y). whistle 0..1 lifts the weight (rattle); steam 0..1 jet."""
    cv.save(); cv.translate(x, y); cv.scale(-s if flip else s, s)
    body = smooth_path([(-46, 0), (-50, -60), (-44, -70), (44, -70), (50, -60), (46, 0)], tension=0.2)
    cv.drawPath(body, fill("#c9ced6")); cv.drawPath(body, stroke("line", 2.8))
    cv.drawRect(skia.Rect.MakeLTRB(14, -66, 34, -4), fill("#e7ebf0"))
    lid = K.rrect(-48, -80, 96, 12, 5)
    cv.drawPath(lid, fill("#b3b9c2")); cv.drawPath(lid, stroke("line", 2.6))
    cv.drawPath(K.rrect(44, -80, 66, 12, 5), fill("#222")); cv.drawPath(K.rrect(44, -80, 66, 12, 5), stroke("line", 2.4))
    cv.drawPath(K.rrect(-82, -78, 36, 9, 4), fill("#222"))
    jig = math.sin(t * 50) * 3 * whistle
    wy = -88 - 6 * whistle
    cv.drawRect(skia.Rect.MakeLTRB(-4, -90, 4, -80), fill("#7a7f88"))
    cv.drawPath(K.rrect(-9 + jig, wy - 12, 18, 14, 4), fill("#4b4f58")); cv.drawPath(K.rrect(-9 + jig, wy - 12, 18, 14, 4), stroke("line", 2.2))
    if steam > 0.01:
        for i in range(7):
            ph = (t * 1.6 + i / 7) % 1
            r_ = 6 + 22 * ph
            cv.drawCircle(math.sin(ph * 5 + i) * 10 * ph, wy - 14 - ph * 140 * steam, r_,
                          fill("#ffffff", 0.75 * (1 - ph) * steam))
    cv.restore()


def draw_cooker_lid(cv, x, y, s=1.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawPath(K.rrect(-36, -8, 72, 12, 5), fill("#b3b9c2")); cv.drawPath(K.rrect(-36, -8, 72, 12, 5), stroke("line", 2.4))
    cv.drawPath(K.rrect(-8, -18, 16, 12, 4), fill("#4b4f58"))
    cv.restore()


def draw_key(cv, x, y, s=1.0, rot=0.0, glow=0.0, t=0.0):
    """A large ornate iron key, centre (x,y), pointing right at rot=0. ~120 px long at s=1."""
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s, s)
    if glow:
        cv.drawCircle(0, 0, 90, K.rad_a((0, 0), 90, [("#bfe3ff", 0.5 * glow), ("#bfe3ff", 0)]))
    iron, hl = "#3a4048", "#7d8792"
    cv.drawCircle(-44, 0, 20, fill(iron)); cv.drawCircle(-44, 0, 20, stroke("line", 2.4))
    for k, (dx, dy, r) in enumerate([(-50, -3, 6), (-40, -4, 7), (-45, 4, 6)]):    # cloud cut-out in the bow
        cv.drawCircle(dx, dy, r, fill("#9fb3c8"))
    cv.drawRect(skia.Rect.MakeLTRB(-26, -5, 54, 5), fill(iron)); cv.drawRect(skia.Rect.MakeLTRB(-26, -5, 54, 5), stroke("line", 2.2))
    cv.drawRect(skia.Rect.MakeLTRB(-22, -9, -16, 9), fill(iron))
    bit = poly([(36, 5), (36, 22), (44, 22), (44, 14), (50, 14), (50, 24), (56, 24), (56, 5)])
    cv.drawPath(bit, fill(iron)); cv.drawPath(bit, stroke("line", 2.2))
    cv.drawLine(-22, -2, 50, -2, stroke(hl, 1.6))
    cv.restore()


def draw_broom(cv, x, y, s=1.0, rot=0.0):
    """Long-handled grass broom; (x,y) = handle top, hangs down."""
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s, s)
    cv.drawLine(0, 0, 0, 160, stroke("#8a5a34", 7))
    cv.drawRect(skia.Rect.MakeLTRB(-8, 150, 8, 166), fill("#d8333d"))
    fan_ = poly([(-8, 160), (8, 160), (40, 240), (-40, 240)])
    cv.drawPath(fan_, fill("#d9b45a")); cv.drawPath(fan_, stroke("line", 2.4))
    for k in range(-4, 5):
        cv.drawLine(k * 1.5, 166, k * 9, 238, stroke("#b08a3a", 1.4))
    cv.restore()


def draw_sack(cv, x, y, s=1.0, fullness=1.0, smog=True, t=0.0):
    """Gunny sack standing at (x,y), tied at the top; smog=True leaks a grey wisp."""
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    w = 46 + 10 * fullness
    sk = smooth_path([(-w, 0), (-w - 4, -60 * fullness - 20), (-14, -96 * fullness - 24), (14, -96 * fullness - 24),
                      (w + 4, -60 * fullness - 20), (w, 0)], tension=0.35)
    cv.drawPath(sk, fill("#b89662")); cv.drawPath(sk, stroke("line", 2.8))
    for k in range(-3, 4):
        cv.drawLine(k * 12, -8, k * 10, -80 * fullness, stroke("#9c7c4c", 1.3))
    ty = -96 * fullness - 24
    cv.drawLine(-16, ty + 10, 16, ty + 10, stroke("#7a4a2a", 5))
    cv.drawPath(ellipse(0, ty - 4, 16, 12), fill("#b89662")); cv.drawPath(ellipse(0, ty - 4, 16, 12), stroke("line", 2.4))
    if smog:
        for i in range(3):
            ph = (t * 0.6 + i / 3) % 1
            cv.drawCircle(4 + ph * 20, ty - 14 - ph * 50, 6 + 10 * ph, fill("#8e9196", 0.5 * (1 - ph)))
    cv.restore()


def draw_kite(cv, x, y, s=1.0, rot=0.0, color="#e0413a", t=0.0, string_to=None, tail=True):
    """Diamond kite centred at (x,y); string_to=(sx,sy) draws a sagging string to the hand."""
    if string_to:
        sx, sy = string_to
        p = skia.Path(); p.moveTo(x, y + 30 * s)
        p.quadTo((x + sx) / 2, max(y, sy) + 40, sx, sy)
        cv.drawPath(p, stroke("#f4efe6", 1.6))
    cv.save(); cv.translate(x, y); cv.rotate(rot + math.sin(t * 3) * 6); cv.scale(s, s)
    k = poly([(0, -40), (30, 0), (0, 40), (-30, 0)])
    cv.drawPath(k, fill(color)); cv.drawPath(k, stroke("line", 2.4))
    cv.drawPath(poly([(0, -40), (30, 0), (0, 0)]), fill(K.shade(color, 0.25)))
    cv.drawLine(0, -40, 0, 40, stroke("line", 1.6)); cv.drawLine(-30, 0, 30, 0, stroke("line", 1.6))
    if tail:
        p = skia.Path(); p.moveTo(0, 40)
        for i in range(1, 6):
            p.lineTo(math.sin(t * 5 + i) * 8, 40 + i * 14)
        cv.drawPath(p, stroke("#f2c94c", 2))
        for i in range(1, 6, 2):
            cv.drawPath(poly([(math.sin(t * 5 + i) * 8 - 5, 40 + i * 14), (math.sin(t * 5 + i) * 8 + 5, 40 + i * 14 - 4),
                              (math.sin(t * 5 + i) * 8 + 5, 40 + i * 14 + 4)]), fill("#f2c94c"))
    cv.restore()


def draw_breeze_jar(cv, x, y, s=1.0, t=0.0, color="#9fd0f0", lid=True, swirl=1.0, rattle=0.0):
    """Glass jar standing at (x,y) with a little breeze swirling inside."""
    jx = math.sin(t * 40) * 2 * rattle
    cv.save(); cv.translate(x + jx, y); cv.scale(s, s)
    jar = K.rrect(-26, -74, 52, 74, 12)
    cv.drawPath(jar, fill("#eaf6ff", 0.35))
    cv.save(); cv.clipPath(jar, doAntiAlias=True)
    for k in range(3):
        a0 = t * (2.5 + k) * swirl + k * 2
        p = skia.Path()
        for j in range(30):
            a = a0 + j * 0.35
            rr = 4 + j * 0.65
            px, py = math.cos(a) * rr, -37 + math.sin(a) * rr * 0.7 + (k - 1) * 10
            p.moveTo(px, py) if j == 0 else p.lineTo(px, py)
        cv.drawPath(p, stroke(color, 3.2, 0.85))
    cv.restore()
    cv.drawPath(jar, stroke("line", 2.4))
    cv.drawLine(-16, -64, -16, -18, stroke("#ffffff", 3, 0.6))
    if lid:
        cv.drawPath(K.rrect(-28, -84, 56, 12, 4), fill("#b9a27a")); cv.drawPath(K.rrect(-28, -84, 56, 12, 4), stroke("line", 2.2))
    cv.restore()


def draw_plate(cv, x, y, s=1.0, rot=0.0):
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s, s)
    cv.drawPath(ellipse(0, 0, 30, 30), fill("#d6dbe2")); cv.drawPath(ellipse(0, 0, 30, 30), stroke("line", 2.4))
    cv.drawPath(ellipse(0, 0, 20, 20), stroke("#aeb5bf", 2))
    cv.drawLine(-14, -18, -4, -22, stroke("#ffffff", 3, 0.8))
    cv.restore()


def draw_newspaper(cv, x, y, s=1.0, folded=True):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    pg = poly([(-26, -34), (26, -30), (24, 30), (-28, 26)])
    cv.drawPath(pg, fill("#efeadf")); cv.drawPath(pg, stroke("line", 2.2))
    for k in range(5):
        cv.drawLine(-20, -22 + k * 10, 18, -20 + k * 10, stroke("#a9a49a", 2))
    cv.drawRect(skia.Rect.MakeLTRB(-20, -30, 0, -24), fill("#5a5650"))
    cv.restore()


# hold= registrations (runtime only; film 1's prop table file is untouched)
def _h_notebook(cv, p):
    draw_notebook(cv, 0, -8, 0.8)


def _h_key(cv, p):
    draw_key(cv, 6, -4, 0.55, rot=-60, glow=p.extra.get("key_glow", 0.0))


def _h_broom(cv, p):
    draw_broom(cv, 0, -60, 0.8, rot=10)


def _h_sack(cv, p):
    draw_sack(cv, 0, 70, 0.55, t=p.t)


def _h_spool(cv, p):
    cv.drawPath(K.rrect(-14, -10, 28, 22, 4), fill("#c9302c")); cv.drawPath(K.rrect(-14, -10, 28, 22, 4), stroke("line", 2))
    cv.drawRect(skia.Rect.MakeLTRB(-12, -4, 12, 6), fill("#f4efe6"))


def _h_jar(cv, p):
    draw_breeze_jar(cv, 0, 30, 0.6, t=p.t, color=p.extra.get("jar_color", "#9fd0f0"))


def _h_plate(cv, p):
    draw_plate(cv, 0, -4, 0.7, rot=p.t * 40)


def _h_lid(cv, p):
    draw_cooker_lid(cv, 0, 0, 0.8)


def _h_news(cv, p):
    draw_newspaper(cv, 0, -20, 0.8)


def _h_ball(cv, p):
    draw_ball(cv, 0, 0, 0.9)


_props.PROPS.update({"notebook": _h_notebook, "key": _h_key, "broom": _h_broom, "sack": _h_sack,
                     "kite_spool": _h_spool, "jar_breeze": _h_jar, "plate": _h_plate, "cooker_lid": _h_lid,
                     "newspaper": _h_news, "ball": _h_ball})


# =============================================================== registry
CAST = {"tara": Tara(), "ishaan": Ishaan(), "rehan": Rehan(), "meghnath": Meghnath()}


def draw(cv, who: str, **pose):
    """draw(cv, 'tara', x=.., y=.., s=.., t=ctx.t, mouth=ctx.mouth('tara'), expr=..., ...)"""
    rig = CAST[who]
    p = Pose(**pose)
    if "blink" not in pose:
        p.blink = auto_blink(p.t, rig.seed)
    rig.draw(cv, p)
    return p
