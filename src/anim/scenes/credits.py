"""End credits (rolling, storybook) + the post-credits Chutney gag is in sc10 ordering:
credits roll first, then the gag (as the last shot of this module)."""
from __future__ import annotations

import math

import skia

from .. import core as K, fx
from ..core import W, H, fill, stroke
from ..rig import animals as A
from ..timeline import Shot, Sfx

CREDITS = [
    ("title", "The Midnight Sweet Shop"),
    ("gap", ""),
    ("head", "Written, directed, designed and animated"),
    ("name", "Claude (Anthropic)"),
    ("small", "Every frame drawn in code: vector rigs, painted sets, light and magic"),
    ("gap", ""),
    ("head", "Starring"),
    ("pair", ("Meher", "a girl who notices things")),
    ("pair", ("Kabir", "her cousin, eventually")),
    ("pair", ("Chutney", "one ear, all heart")),
    ("pair", ("Mishri Amma", "keeper of the shop")),
    ("pair", ("Tola", "the scale (clank)")),
    ("pair", ("Nani", "who remembered")),
    ("gap", ""),
    ("head", "Voices"),
    ("small", "Kokoro-82M open text-to-speech model (Apache-2.0), run locally"),
    ("gap", ""),
    ("head", "Music & sound"),
    ("small", "Original score and sound effects composed and synthesized in code"),
    ("small", "Santoor, bansuri, harmonium, tabla, tanpura, sarangi: all built from waveforms"),
    ("gap", ""),
    ("head", "Tools"),
    ("small", "Skia (skia-python) · NumPy · SciPy · FFmpeg · Python"),
    ("gap", ""),
    ("small", "No real people, places or stories were harmed. Chandpur exists only here."),
    ("gap", ""),
    ("head", "Don't let the story lose its ending."),
]


SIZES = {"title": 92, "head": 36, "name": 56, "small": 32, "pair": 42, "gap": 40}
GAP = 36


def _layout():
    ys, y = [], 0
    for kind, _ in CREDITS:
        y += SIZES[kind] + GAP
        ys.append(y)
    return ys


def _roll(cv, c):
    t = c.t
    cv.drawRect(skia.Rect.MakeWH(W, H), K.lin((0, 0), (0, H), ["#0b0d2a", "#14183f", "#06071a"]))
    K.stars(cv, W, H, t, n=220, seed=31, alpha=0.9)
    fx.motes(cv, t, (0, 0, W, H), n=40, color="#ffd36b", a=0.5, seed=8)
    ys = _layout()
    hold = 6.0
    # scroll so the final line comes to rest at screen centre, then holds
    start = H + 40
    stop = H / 2 + 20 - ys[-1]
    k = K.clamp(t / max(1.0, c.dur - hold))
    off = K.lerp(start, stop, k)
    for (kind, txt), yy in zip(CREDITS, ys):
        y = off + yy
        if y < -100 or y > H + 120:
            continue
        a = K.clamp(min((y + 40) / 220, (H + 40 - y) / 220))
        sz = SIZES[kind]
        if kind == "title":
            K.text_center(cv, txt, W / 2, y, size=sz, color="#ffe9b8", a=a, italic=True, bold=True)
        elif kind == "head":
            last = txt.startswith("Don't")
            K.text_center(cv, txt, W / 2, y, size=sz + (14 if last else 0), color="#f6b04a", a=a,
                          family="DejaVu Serif" if last else "DejaVu Sans", bold=True, italic=last)
        elif kind == "name":
            K.text_center(cv, txt, W / 2, y, size=sz, color="#fff3d6", a=a, italic=True)
        elif kind == "small":
            K.text_center(cv, txt, W / 2, y, size=sz, color="#ddd1b8", a=a, family="DejaVu Sans")
        elif kind == "pair":
            f1 = K.font(sz, "DejaVu Serif", True, True)
            f2 = K.font(sz * 0.72, "DejaVu Sans")
            w1 = f1.measureText(txt[0])
            cv.drawString(txt[0], W / 2 - 30 - w1, y, f1, fill("#fff3d6", a))
            cv.drawString(txt[1], W / 2 + 30, y + 2, f2, fill("#c9bda4", a))
    # Chutney trots along the bottom, then sits proudly under the last line
    run = K.clamp(t / (c.dur - hold))
    x = K.lerp(-160, W * 0.5 + 330, run)
    mode = "trot" if run < 1 else "sit"
    A.draw_dog(cv, A.DogPose(x=x, y=H - 14, s=0.9, t=t, mode=mode, phase=t * 1.4, tongue=True, ear=0.8,
                             expr="proud" if mode == "sit" else "happy"))


LADDOO = (1240, 545)


def _laddoo(cv, t, x, y, a=1.0):
    by = y + math.sin(t * 2.2) * 7
    fx.glow_dot(cv, x, by, 70, "gold", 0.8 * a)
    cv.drawCircle(x, by, 27, K.rad((x - 8, by - 9), 30, ["#ffe08a", "saffron", "#c97a12"]))
    cv.drawCircle(x, by, 27, stroke("line", 2.6, a))
    for i in range(7):
        ang = i * 0.9
        cv.drawCircle(x + math.cos(ang) * 14, by + math.sin(ang) * 14, 2.6, fill("#fff2c0", a))
    if math.sin(t * 3) > 0.5:
        fx.star4(cv, x + 14, by - 16, 8, "#ffffff", a)


def _postcredits(cv, c):
    """Chutney peeks over the counter, looks left, looks right, snaffles a floating laddoo...
    and slowly rises out of frame, legs paddling, deeply surprised."""
    from ..sets import shop
    t = c.t
    CAM = (1010, 560, K.lerp(1.75, 1.85, c.u))
    shop.draw_shop(cv, t, view="counter", cam=CAM)
    with K.camera(cv, *CAM):
        st = _gag(cv, c, t, part="dog")
    shop.draw_counter_front(cv, t, "counter", cam=CAM)   # in front of Chutney
    with K.camera(cv, *CAM):
        _gag(cv, c, t, part="front", st=st)


def _gag(cv, c, t, part="dog", st=None):
    # beats
    T_LEFT, T_RIGHT, T_SNAF, T_LIFT = 1.0, 2.2, 3.4, 4.6
    rise = K.ease_in(c.seg(T_LIFT, 10.2))
    peek = K.ease_out_back(c.seg(0.2, 0.9))
    y = K.lerp(960, 745, peek) - rise * 820
    lunge = K.ease_out(c.seg(T_SNAF, T_SNAF + 0.25)) * (1 - K.ease_in_out(c.seg(T_SNAF + 0.4, T_SNAF + 0.9)))
    x = 860 + lunge * 175
    flip = T_LEFT <= t < T_RIGHT
    if t < T_SNAF:
        expr, mouth = "alert", 0.0
    elif t < T_LIFT:
        expr, mouth = "proud", 0.25 * abs(math.sin(t * 14))   # munch munch
    elif t < T_LIFT + 0.8:
        expr, mouth = "alert", 0.0
    else:
        expr, mouth = "sad", 0.7                             # mouth agape: deeply surprised
    mode = "float" if t > T_LIFT + 0.3 else "sit"
    if part == "dog":
        # Chutney is behind the counter: drawn before the counter front
        A.draw_dog(cv, A.DogPose(x=x, y=y, s=1.7, t=t, mode=mode, flip=flip, expr=expr, mouth=mouth,
                                 head_tilt=(math.sin(t * 5) * 5 if t < T_SNAF else 0) + lunge * 18,
                                 ear=1.0 if t > T_LIFT else 0.55, wag=1.4 if t < T_SNAF else 0.6))
        return
    if t < T_SNAF + 0.12:
        _laddoo(cv, t, *LADDOO)
    if T_SNAF < t < T_SNAF + 0.5:
        fx.sparkles(cv, t, LADDOO[0], LADDOO[1], spread=40, n=8, color="gold", seed=13,
                    a=1 - c.seg(T_SNAF, T_SNAF + 0.5))
    if t > T_LIFT:
        dy = y - 140
        fx.sparkles(cv, t, x, dy, spread=110, n=14, color="gold", seed=12, a=K.clamp(1 - rise * 0.6))
    # eye-darting "?" moments: tiny shake lines when he checks each way
    if T_LEFT - 0.1 < t < T_LEFT + 0.25 or T_RIGHT - 0.1 < t < T_RIGHT + 0.25:
        fx.vibe_lines(cv, x + (-60 if flip else 60), y - 150, 40, t, color="line", a=0.7, n=2)


SHOTS = [
    Shot("CR_SH01", _roll, duration=46.0, music="credits", transition="fade_black", trans_dur=1.5,
         sfx=[Sfx("night_bed", 0, -16, dur=46)]),
    Shot("CR_SH02", _postcredits, duration=11.0, music="postcredits", transition="fade_black", trans_dur=1.0,
         sfx=[Sfx("crickets_bed", 0, -26, dur=11.0),
              Sfx("floor_creak", 0.3, -14), Sfx("tola_tink", 1.0, -18), Sfx("tola_tink", 2.2, -18),
              Sfx("pop", 3.4, -10), Sfx("munch", 3.5, -4), Sfx("swallow_gulp", 4.3, -8),
              Sfx("magic_float", 4.7, -6), Sfx("dog_whine", 6.2, -8), Sfx("pop", 9.8, -14)]),
]
