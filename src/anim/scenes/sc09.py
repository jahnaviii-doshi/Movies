"""Scene 9: DAWN (~90 s). The thread, the farewell, the fold, the handprint, the walk home."""
from __future__ import annotations

import math

from .. import core as K, fx
from ..rig import chars, animals as A
from ..sets import wall, gali
from ..timeline import Shot, Line, Sfx
from ._util_d import hand_pos, thread_band, thread_strand, amma_wink, long_shadows

FY = wall.FLOOR_Y
CS = wall.CHAR_S


def _cam(cx, cy, z):
    return (cx, cy, z)


def _band_on_meher(cv, t, x, y, s, arms, flip=False, legs="stand", a=1.0):
    (wx, wy), _ = hand_pos("meher", x, y, s, arms, flip, legs, "r", frac=0.72)
    thread_band(cv, wx, wy, s * 0.62, t, a)


# --------------------------------------------------------------------------------------- SH01
def sh01(cv, c):
    """Wide: the shop open in the first rose light. Amma beckons."""
    t = c.t
    z = K.lerp(1.0, 1.06, K.ease_in_out(c.u))
    cam = _cam(960, 560, z)
    wall.draw_wall(cv, t, "dawn", unfold=1.0, fold=0.0, cam=cam)
    beck = c.seg(4.2, 4.6)
    curl = math.sin(max(0, t - 4.2) * 7) * 22 * beck
    with K.camera(cv, *cam):
        with K.lit(cv, "dawn"):
            A.draw_dog(cv, A.DogPose(x=470, y=FY + 18, s=1.1, t=t, mode="sit", tongue=True, ear=0.6, wag=0.6))
            chars.draw(cv, "meher", x=690, y=FY, s=CS, t=t, expr="awe", turn=0.45, look=(0.6, -0.1))
            chars.draw(cv, "amma", brow=0.8, x=1000, y=FY, s=CS, t=t, flip=True, expr="happy", turn=0.4,
                       arms={"r": (70 * beck + 8, 40 + curl)}, hand={"r": "open"})
            chars.draw(cv, "nani", x=1310, y=FY, s=CS, t=t, flip=True, expr="happy", turn=0.3,
                       head_tilt=-4)
    fx.motes(cv, t, (500, 250, 1420, 900), n=30, color="#ffe7a8", a=0.45, seed=91)


# --------------------------------------------------------------------------------------- SH02
def sh02(cv, c):
    """Two-shot: Meher steps closer to Amma."""
    t = c.t
    cam = _cam(K.lerp(860, 880, c.u), 610, 1.6)
    wall.draw_wall(cv, t, "dawn", unfold=1.0, cam=cam)
    step = K.ease_in_out(c.seg(0.6, 2.6))
    mx = K.lerp(690, 790, step)
    curl = math.sin(t * 7) * 22 * (1 - c.seg(2.4, 3.0))
    with K.camera(cv, *cam):
        with K.lit(cv, "dawn"):
            chars.draw(cv, "meher", x=mx, y=FY, s=CS, t=t, expr="shy" if t > 2.6 else "awe",
                       turn=0.5, legs="walk" if 0.6 < t < 2.6 else "stand", phase=t * 1.3,
                       look=(0.7, -0.2), head_tilt=4 * step)
            chars.draw(cv, "amma", brow=0.8, x=1000, y=FY, s=CS, t=t, flip=True, expr="happy", turn=0.45,
                       arms={"r": (78, 40 + curl)}, head_tilt=-5)


# --------------------------------------------------------------------------------------- SH03
def sh03(cv, c):
    """Closer on Amma: she draws a single glowing thread out of her sugar shawl."""
    t = c.t
    cam = _cam(K.lerp(905, 925, c.u), 585, 1.9)
    wall.draw_wall(cv, t, "dawn", unfold=1.0, cam=cam)
    pull = K.ease_in_out(c.seg(1.0, 3.8))
    arms = {"r": (K.lerp(20, 118, pull), K.lerp(95, 25, pull)), "l": (18, 70)}
    ax, ay = 1040, FY
    with K.camera(cv, *cam):
        with K.lit(cv, "dawn"):
            chars.draw(cv, "meher", x=760, y=FY, s=CS, t=t, expr="awe", turn=0.5, look=(0.6, -0.4))
            chars.draw(cv, "amma", brow=0.8, x=ax, y=ay, s=CS, t=t, flip=True, expr="happy", turn=0.4, arms=arms,
                       hand={"r": "fist"}, look=(0.5, 0.2), head_tilt=-3)
        if t > 1.0:
            (hx, hy), _ = hand_pos("amma", ax, ay, CS, arms, flip=True)
            chest = (ax + 8 * CS, ay - 100 * CS)
            a = K.clamp((t - 1.0) / 0.4)
            thread_strand(cv, chest, (hx, hy), t, a=a, sag=K.lerp(4, 40, pull), width=3.4)
            fx.glow_dot(cv, hx, hy, 40, "#ffb3d1", 0.6 * a)
            fx.sparkles(cv, t, (chest[0] + hx) / 2, (chest[1] + hy) / 2, spread=70, n=10, color="#ffd1e4",
                        size=6, seed=93, a=a)


# --------------------------------------------------------------------------------------- SH04
def sh04(cv, c):
    """Two-shot: Amma ties the thread round Meher's wrist."""
    t = c.t
    cam = _cam(905, 600, 1.85)
    wall.draw_wall(cv, t, "dawn", unfold=1.0, cam=cam)
    mx, ax = 780, 1040
    offer = K.ease_out(c.seg(0.2, 1.2))
    m_arms = {"r": (K.lerp(8, 62, offer), K.lerp(10, 18, offer))}
    (wx, wy), _ = hand_pos("meher", mx, FY, CS, m_arms, frac=0.72)
    reach = K.ease_in_out(c.seg(0.5, 1.6))
    a_arms = {"r": (K.lerp(40, 66, reach), K.lerp(40, 12, reach) + math.sin(t * 9) * 8 * c.seg(1.6, 2.2) * (1 - c.seg(3.2, 3.6))),
              "l": (K.lerp(18, 50, reach), 30)}
    tie = c.seg(1.8, 3.4)
    with K.camera(cv, *cam):
        with K.lit(cv, "dawn"):
            chars.draw(cv, "meher", x=mx, y=FY, s=CS, t=t, expr="awe" if t < 3.6 else "happy", turn=0.5,
                       arms=m_arms, hand={"r": "open"}, look=(0.4, 0.6) if t < 3.4 else (0.7, -0.3),
                       mouth=c.mouth("meher"))
            chars.draw(cv, "amma", brow=0.8, x=ax, y=FY, s=CS, t=t, flip=True, expr="happy", turn=0.45, arms=a_arms,
                       hand={"r": "fist"}, mouth=c.mouth("amma"), look=(0.4, 0.5) if t < 3.4 else (0.6, -0.2),
                       head_tilt=-6 if t > 3.4 else -2)
        (hx, hy), _ = hand_pos("amma", ax, FY, CS, a_arms, flip=True)
        if t < 3.4:
            thread_strand(cv, (hx, hy), (wx, wy), t, a=1 - c.seg(3.0, 3.4), sag=10, width=2.0)
        # loops winding round the wrist
        for i in range(3):
            u = K.clamp(tie * 3 - i)
            if u > 0:
                cv.save(); cv.translate(wx, wy); cv.scale(1, 0.5)
                cv.drawCircle(0, 0, 12 * CS * 0.62 + i * 1.5, K.stroke("#ffe3ef", 2.4, u * 0.8))
                cv.restore()
        thread_band(cv, wx, wy, CS * 0.62, t, a=c.seg(3.0, 3.6))
        if 3.2 < t < 4.4:
            fx.sparkles(cv, t, wx, wy, spread=60, n=12, color="#ffd1e4", size=7, seed=95, a=1 - c.seg(3.8, 4.4))


# --------------------------------------------------------------------------------------- SH05
def sh05(cv, c):
    """MCU Meher: 'Will you be here next summer?'"""
    t = c.t
    cam = _cam(800, 470, 2.6)
    wall.draw_wall(cv, t, "dawn", unfold=1.0, cam=cam)
    arms = {"r": (40, 70)}
    look_wrist = t < 0.9
    with K.camera(cv, *cam):
        with K.lit(cv, "dawn"):
            chars.draw(cv, "meher", x=800, y=FY, s=CS, t=t, expr="worried" if not look_wrist else "awe",
                       turn=0.5, arms=arms, look=(0.3, 0.7) if look_wrist else (0.8, -0.3),
                       head_tilt=6 if not look_wrist else -8, mouth=c.mouth("meher"), brow=0.4)
        _band_on_meher(cv, t, 800, FY, CS, arms)


# --------------------------------------------------------------------------------------- SH06
def sh06(cv, c):
    """MCU Amma: 'If somebody tells the story right.' ... and a wink."""
    t = c.t
    cam = _cam(1000, 610, 2.7)
    wall.draw_wall(cv, t, "dawn", unfold=1.0, cam=cam)
    line_end = c.shot.lines[0].end if c.shot.lines else 2.5
    tilt = -8 * K.ease_out_back(c.seg(line_end + 0.1, line_end + 0.6))
    wink = 1.0 if line_end + 0.5 < t < line_end + 1.15 else 0.0
    with K.camera(cv, *cam):
        with K.lit(cv, "dawn"):
            chars.draw(cv, "amma", brow=0.8, x=1000, y=FY, s=CS, t=t, flip=True, expr="happy", turn=0.4,
                       head_tilt=tilt, mouth=c.mouth("amma"), look=(0.6, -0.2), arms={"r": (30, 80)},
                       hand={"r": "point"})
            amma_wink(cv, 1000, FY, CS, t, turn=0.4, head_tilt=tilt, flip=True, side=-1, amount=wink)
    if wink:
        with K.camera(cv, *cam):
            fx.star4(cv, 1045, 455, 9, "#ffffff", 1.0)


# --------------------------------------------------------------------------------------- SH07
def sh07(cv, c):
    """Close, tender: 'Don't let the story lose its ending.'"""
    t = c.t
    z = K.lerp(2.15, 2.35, K.ease_in_out(c.u))
    cam = _cam(925, 545, z)
    wall.draw_wall(cv, t, "dawn", unfold=1.0, cam=cam)
    arms_m = {"r": (30, 60)}
    with K.camera(cv, *cam):
        with K.lit(cv, "dawn"):
            chars.draw(cv, "meher", x=815, y=FY, s=CS, t=t, expr="happy", turn=0.5, look=(0.7, -0.4),
                       arms=arms_m, head_tilt=4)
            chars.draw(cv, "amma", brow=0.8, x=1040, y=FY, s=CS, t=t, flip=True, expr="happy", turn=0.45,
                       mouth=c.mouth("amma"), look=(0.6, -0.5), head_tilt=-6 + math.sin(t * 1.3) * 2,
                       arms={"r": (55, 60), "l": (20, 40)})
        _band_on_meher(cv, t, 815, FY, CS, arms_m)
    fx.motes(cv, t, (0, 0, 1920, 1080), n=24, color="#ffe7a8", a=0.35, seed=97)


# --------------------------------------------------------------------------------------- SH08
def sh08(cv, c):
    """Wide: Amma steps back into her shop, waving; the shop begins to fold away."""
    t = c.t
    fold = K.lerp(0.0, 0.42, K.ease_in_out(c.seg(2.4, c.dur)))
    cam = _cam(960, 560, K.lerp(1.08, 1.0, c.u))
    wall.draw_wall(cv, t, "dawn", unfold=1.0, fold=fold, cam=cam)
    back = K.ease_in_out(c.seg(0.4, 3.2))
    amma_a = 1 - K.ease_in(c.seg(2.2, 3.6))
    wave = math.sin(t * 6) * 20
    arms_m = {"r": (30 + 40 * c.seg(1.0, 1.4) * (1 - c.seg(4.2, 4.8)), 40 + wave * 0.7), "l": (8, 10)}
    with K.camera(cv, *cam):
        with K.lit(cv, "dawn"):
            if amma_a > 0.01:
                chars.draw(cv, "amma", brow=0.8, x=K.lerp(1000, 960, back), y=K.lerp(FY, FY - 40, back),
                           s=K.lerp(CS, CS * 0.86, back), t=t, flip=back < 0.5, turn=K.lerp(0.4, 0.1, back),
                           expr="happy", arms={"r": (120, 30 + wave)}, alpha=amma_a)
            chars.draw(cv, "meher", x=650, y=FY, s=CS, t=t, expr="happy", turn=0.45, arms=arms_m,
                       hand={"r": "open"}, look=(0.6, -0.2))
            chars.draw(cv, "nani", x=1330, y=FY, s=CS, t=t, flip=True, expr="happy", turn=0.35,
                       arms={"r": (40, 50)}, head_tilt=-3)
            A.draw_dog(cv, A.DogPose(x=440, y=FY + 18, s=1.1, t=t, mode="sit", ear=0.9, expr="alert"))
        _band_on_meher(cv, t, 650, FY, CS, arms_m)


# --------------------------------------------------------------------------------------- SH09
def sh09(cv, c):
    """Wide, lower: Meher, Kabir and Nani watch the last panels fold in."""
    t = c.t
    fold = K.lerp(0.42, 1.0, K.ease_in_out(c.seg(0.0, c.dur - 1.2)))
    cam = _cam(960, 600, K.lerp(1.0, 1.04, c.u))
    wall.draw_wall(cv, t, "dawn", unfold=1.0, fold=fold, cam=cam)
    flex = c.seg(3.0, 3.6) * (1 - c.seg(5.6, 6.2))
    arms_k = {"r": (K.lerp(8, 70, flex), K.lerp(10, 80, flex))}
    arms_m = {"r": (14, 30)}
    with K.camera(cv, *cam):
        with K.lit(cv, "dawn"):
            A.draw_dog(cv, A.DogPose(x=1760, y=FY + 30, s=1.1, t=t, mode="sit", flip=True, ear=0.4, expr="sad"))
            chars.draw(cv, "meher", x=560, y=FY + 40, s=CS * 1.05, t=t, expr="sad" if fold < 0.9 else "happy",
                       turn=0.55, look=(0.8, -0.2), arms=arms_m)
            chars.draw(cv, "kabir", x=1290, y=FY + 40, s=CS * 1.0, t=t, flip=True, turn=0.5,
                       expr="happy" if flex > 0.5 else "awe", arms=arms_k, hand={"r": "open"},
                       look=(0.2, 0.4) if flex > 0.3 else (0.7, -0.2))
            chars.draw(cv, "nani", x=1560, y=FY + 40, s=CS * 1.0, t=t, flip=True, turn=0.35, expr="happy",
                       arms={"l": (14, 20)})
        _band_on_meher(cv, t, 560, FY + 40, CS * 1.05, arms_m)


# --------------------------------------------------------------------------------------- SH10
def sh10(cv, c):
    """Only a peeling blue wall in the dawn... and, for a moment, a small golden handprint."""
    t = c.t
    cam = _cam(960, 520, K.lerp(1.15, 1.32, K.ease_in_out(c.u)))
    hp = c.seg(1.4, c.dur - 0.6)
    wall.draw_wall(cv, t, "dawn", unfold=0.0, handprint=hp, cam=cam)
    fx.motes(cv, t, (300, 200, 1620, 900), n=26, color="#ffd6a0", a=0.4, seed=99)


# --------------------------------------------------------------------------------------- SH11
def sh11(cv, c):
    """CU Meher looks at the thread on her wrist and smiles."""
    t = c.t
    cam = _cam(780, 470, K.lerp(2.6, 2.8, c.u))
    wall.draw_wall(cv, t, "dawn", unfold=0.0, cam=cam)
    lift = K.ease_out(c.seg(0.2, 1.2))
    arms = {"r": (K.lerp(20, 60, lift), K.lerp(30, 110, lift))}
    with K.camera(cv, *cam):
        with K.lit(cv, "dawn"):
            chars.draw(cv, "meher", x=760, y=FY, s=CS, t=t, expr="grin" if t > 1.8 else "awe", turn=0.35,
                       arms=arms, look=(0.5, 0.8) if t < 2.6 else (0.9, -0.4), head_tilt=-6)
        _band_on_meher(cv, t, 760, FY, CS, arms)
        (wx, wy), _ = hand_pos("meher", 760, FY, CS, arms, frac=0.72)
        fx.sparkles(cv, t, wx, wy, spread=40, n=6, color="#ffd1e4", size=5, seed=101, a=lift)


# --------------------------------------------------------------------------------------- gali walk
def _walkers(cv, t, d, phase_t, look_up=0.0, draw=True):
    """Nani in the middle holding both children's hands, walking toward camera at depth d."""
    y, s = gali.gali_ground(d)
    out = []
    specs = [("meher", -0.6, {"r": (32, 6)}, 0.0), ("nani", 0.0, {"l": (34, 6), "r": (34, 6)}, 0.33),
             ("kabir", 0.6, {"l": (32, 6)}, 0.66)]
    for who, a, arms, ph in specs:
        x = gali.gali_x(d, a)
        bob = -abs(math.sin((phase_t * 1.6 + ph) * math.pi)) * 5 * s
        sway = math.sin((phase_t * 1.6 + ph) * math.pi) * 2.5
        expr = "happy"
        look = (0.6 if a < 0 else -0.6 if a > 0 else 0.0, -0.6 * look_up) if who != "nani" else (0, 0)
        kw = dict(x=x, y=y + bob, s=s, t=t, expr=expr, turn=0.0 if who == "nani" else (0.2 if a < 0 else 0.2),
                  flip=a > 0, arms=arms, hand={"l": "open", "r": "open"}, look=look, lean=sway,
                  head_tilt=(6 if a < 0 else -6) * look_up if who != "nani" else 0)
        out.append((who, kw))
    return out, y, s


def _draw_walk(cv, t, d, phase_t, dog_d=None, dog_x=0.0, look_up=0.0, light="dawn"):
    figs, y, s = _walkers(cv, t, d, phase_t, look_up)
    # long shadows toward camera
    sh = [(lambda c_, w=w, kw=kw: chars.draw(c_, w, **kw), kw["x"], y) for w, kw in figs]
    long_shadows(cv, sh, a=0.32, stretch=2.6)
    with K.lit(cv, light):
        if dog_d is not None:
            dy, dsc = gali.gali_ground(dog_d)
            A.draw_dog(cv, A.DogPose(x=gali.gali_x(dog_d, dog_x), y=dy, s=dsc * 0.7, t=t, mode="trot",
                                     phase=t * 1.2, flip=math.sin(t * 0.7) < 0, tongue=True, ear=1.0,
                                     expr="proud", wag=1.6))
        for who, kw in figs:
            chars.draw(cv, who, **kw)
    # joined hands
    hands = []
    for who, kw in figs:
        for side in ("l", "r"):
            if side in kw["arms"]:
                (hx, hy), _ = hand_pos(who, kw["x"], kw["y"], kw["s"], kw["arms"], kw["flip"], "stand", side)
                hands.append((who, side, hx, hy))
    pairs = [(("meher", "r"), ("nani", "l")), (("nani", "r"), ("kabir", "l"))]
    hd = {(w, sd): (hx, hy) for w, sd, hx, hy in hands}
    for p1, p2 in pairs:
        if p1 in hd and p2 in hd:
            (x1, y1), (x2, y2) = hd[p1], hd[p2]
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            with K.lit(cv, light):
                cv.drawPath(K.ellipse(mx, my, 13 * s, 11 * s), K.fill("skin"))
                cv.drawPath(K.ellipse(mx, my, 13 * s, 11 * s), K.stroke("line", 2.6 * s))
    # the thread on Meher's wrist
    mk = dict(figs)["meher"]
    (wx, wy), _ = hand_pos("meher", mk["x"], mk["y"], mk["s"], mk["arms"], mk["flip"], "stand", "r", frac=0.72)
    thread_band(cv, wx, wy, s * 0.62, t, 0.9)
    return y, s


def sh12(cv, c):
    """Gali at sunrise, wide: three long shadows walk home up the lane."""
    t = c.t
    d = K.lerp(0.78, 0.42, K.ease_in_out(c.u))
    gali.draw_gali(cv, t, "sunrise", rickshaw=True)
    _draw_walk(cv, t, d, t, dog_d=max(0.05, d - 0.16), dog_x=math.sin(t * 0.9) * 0.6)
    fx.motes(cv, t, (500, 250, 1420, 900), n=30, color="#ffe2b0", a=0.4, seed=103)


def sh13(cv, c):
    """Closer: Nani between the children, both looking up at her; Chutney trots ahead, proud."""
    t = c.t
    d = K.lerp(0.36, 0.2, c.u)
    y, s = gali.gali_ground(d)
    cam = (960, K.lerp(y - 260 * s, y - 230 * s, c.u), 1.25)
    gali.draw_gali(cv, t, "sunrise", rickshaw=True, cam=cam)
    with K.camera(cv, *cam):
        _draw_walk(cv, t, d, t, dog_d=max(0.04, d - 0.12), dog_x=-0.9 + c.u * 1.6, look_up=1.0)


def sh14(cv, c):
    """They walk on, past us; the lane and the wall remain, gold in the morning."""
    t = c.t
    d = K.lerp(0.22, -0.02, K.ease_in(c.seg(0, 4.2)))
    gali.draw_gali(cv, t, "sunrise", rickshaw=True, wall_glow=0.25 * math.sin(c.seg(3.5, c.dur) * math.pi))
    if d > 0.0:
        _draw_walk(cv, t, d, t, dog_d=None)
    fx.motes(cv, t, (600, 300, 1320, 900), n=24, color="#ffe2b0", a=0.4, seed=105)


SHOTS = [
    Shot("S09_SH01", sh01, duration=7.0, music="dawn_farewell", transition="dissolve", trans_dur=1.2,
         sfx=[Sfx("sparrows_dawn", 0, -14, dur=7.0), Sfx("koel_call", 2.5, -12)]),
    Shot("S09_SH02", sh02, duration=5.0,
         sfx=[Sfx("sparrows_dawn", 0, -16, dur=5.0), Sfx("footsteps_soft", 0.6, -12)]),
    Shot("S09_SH03", sh03, duration=6.0,
         sfx=[Sfx("sparrows_dawn", 0, -17, dur=6.0), Sfx("sparkle", 1.0, -6), Sfx("magic_float", 1.4, -12)]),
    Shot("S09_SH04", sh04, lines=[Line("amma", "The job of remembering. It's yours now.", at=3.9)], tail=1.2,
         sfx=[Sfx("sparrows_dawn", 0, -17, dur=8.5), Sfx("sparkle", 3.1, -6)]),
    Shot("S09_SH05", sh05, lines=[Line("meher", "Will you be here next summer?", at=1.0)], tail=0.9,
         sfx=[Sfx("sparrows_dawn", 0, -17, dur=5.0)]),
    Shot("S09_SH06", sh06, lines=[Line("amma", "If somebody tells the story right.", at=0.5)], tail=1.8,
         sfx=[Sfx("sparrows_dawn", 0, -17, dur=6.0), Sfx("sparkle", 3.2, -12)]),
    Shot("S09_SH07", sh07, lines=[Line("amma", "Don't let the story lose its ending.", at=1.0)], tail=2.0,
         sfx=[Sfx("sparrows_dawn", 0, -17, dur=6.5)]),
    Shot("S09_SH08", sh08, duration=8.0,
         sfx=[Sfx("sparrows_dawn", 0, -16, dur=8.0), Sfx("wind_chime_hello", 0.6, -10),
              Sfx("whoosh", 3.0, -14, params={"intensity": 0.4}), Sfx("lantern_light", 5.0, -16)]),
    Shot("S09_SH09", sh09, duration=8.5,
         sfx=[Sfx("sparrows_dawn", 0, -16, dur=8.5), Sfx("whoosh", 1.0, -14, params={"intensity": 0.5}),
              Sfx("floor_creak", 4.0, -14), Sfx("whoosh", 6.4, -12, params={"intensity": 0.6})]),
    Shot("S09_SH10", sh10, duration=6.5,
         sfx=[Sfx("sparrows_dawn", 0, -15, dur=6.5), Sfx("wall_glow", 1.4, -14), Sfx("sparkle", 3.0, -10)]),
    Shot("S09_SH11", sh11, duration=4.5, sfx=[Sfx("sparrows_dawn", 0, -15, dur=4.5), Sfx("sparkle", 0.8, -14)]),
    Shot("S09_SH12", sh12, duration=9.5, music="walk_home", transition="dissolve", trans_dur=1.0,
         sfx=[Sfx("sparrows_dawn", 0, -12, dur=9.5), Sfx("koel_call", 1.5, -10, params={"n_calls": 3}),
              Sfx("footsteps_soft", 0.0, -16, dur=9.5)]),
    Shot("S09_SH13", sh13, duration=7.5,
         sfx=[Sfx("sparrows_dawn", 0, -13, dur=7.5), Sfx("footsteps_soft", 0.0, -14, dur=7.5),
              Sfx("dog_pant", 1.0, -14)]),
    Shot("S09_SH14", sh14, duration=9.0,
         sfx=[Sfx("sparrows_dawn", 0, -12, dur=9.0), Sfx("koel_call", 3.0, -12, params={"n_calls": 2})]),
]
