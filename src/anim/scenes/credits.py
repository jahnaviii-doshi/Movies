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


def _roll(cv, c):
    t = c.t
    cv.drawRect(skia.Rect.MakeWH(W, H), K.lin((0, 0), (0, H), ["#0b0d2a", "#14183f", "#06071a"]))
    K.stars(cv, W, H, t, n=220, seed=31, alpha=0.9)
    # the blue wall far below, shimmering
    fx.motes(cv, t, (0, 0, W, H), n=40, color="#ffd36b", a=0.5, seed=8)
    total_h = 0
    sizes = {"title": 92, "head": 34, "name": 54, "small": 30, "pair": 40, "gap": 40}
    for kind, _ in CREDITS:
        total_h += sizes[kind] + 34
    speed = (total_h + H + 100) / max(1, c.dur - 2)
    y = H + 60 - t * speed
    for kind, txt in CREDITS:
        sz = sizes[kind]
        y += sz + 34
        if y < -100 or y > H + 120:
            continue
        a = K.clamp(min((y + 60) / 200, (H + 60 - y) / 200))
        if kind == "title":
            K.text_center(cv, txt, W / 2, y, size=sz, color="#ffe9b8", a=a, italic=True, bold=True)
        elif kind == "head":
            K.text_center(cv, txt, W / 2, y, size=sz, color="#f6b04a", a=a, family="DejaVu Sans", bold=True)
        elif kind == "name":
            K.text_center(cv, txt, W / 2, y, size=sz, color="#fff3d6", a=a, italic=True)
        elif kind == "small":
            K.text_center(cv, txt, W / 2, y, size=sz, color="#d9cdb4", a=a, family="DejaVu Sans")
        elif kind == "pair":
            f1 = K.font(sz, "DejaVu Serif", True, True)
            f2 = K.font(sz * 0.72, "DejaVu Sans")
            w1 = f1.measureText(txt[0])
            cv.drawString(txt[0], W / 2 - 30 - w1, y, f1, fill("#fff3d6", a))
            cv.drawString(txt[1], W / 2 + 30, y, f2, fill("#c9bda4", a))
    # Chutney trotting along the bottom of the credits, then sitting
    x = K.lerp(-200, W * 0.82, K.clamp(t / (c.dur * 0.6)))
    mode = "trot" if t < c.dur * 0.6 else "sit"
    with K.lit(cv, "moon"):
        A.draw_dog(cv, A.DogPose(x=x, y=H - 40, s=0.9, t=t, mode=mode, phase=t * 1.4, tongue=True, ear=0.8))


def _postcredits(cv, c):
    """Chutney sneaks a floating laddoo and drifts up out of frame, legs paddling."""
    t = c.t
    try:
        from ..sets import shop
        shop.draw_shop(cv, t, view="counter")
    except Exception:
        cv.drawRect(skia.Rect.MakeWH(W, H), K.lin((0, 0), (0, H), ["#5a3415", "#2a160a"]))
    try:
        from ..sets import shop as _s
        if hasattr(_s, "draw_counter_front"):
            _s.draw_counter_front(cv, t, "counter")
    except Exception:
        pass
    # timeline: 0-1.2 look left, 1.2-2.4 look right, 2.6 snaffle, 3.2 float up
    look = "l" if t < 1.2 else "r" if t < 2.4 else "f"
    lift = K.ease_in(c.seg(3.2, 8.5))
    y = 1010 - lift * 1300
    flip = look == "l"
    mode = "float" if t > 3.2 else "sit"
    expr = "alert" if t < 2.6 else "proud" if t < 3.4 else "sad"
    head_tilt = math.sin(t * 6) * 4 if t < 2.4 else 0
    A.draw_dog(cv, A.DogPose(x=900, y=y, s=1.7, t=t, mode=mode, flip=flip, expr=expr, head_tilt=head_tilt,
                             ear=1.0 if t > 3.2 else 0.6, mouth=0.3 if 2.6 < t < 3.0 else 0.0))
    if t < 2.6:
        fx.glow_dot(cv, 1200, 760 + math.sin(t * 2) * 6, 40, "gold", 0.8)
        cv.drawCircle(1200, 760 + math.sin(t * 2) * 6, 16, K.rad((1194, 752), 18, ["#ffe08a", "saffron", "#c97a12"]))
    if t > 3.2:
        fx.sparkles(cv, t, 900, y - 120, spread=120, n=14, color="gold", seed=12)


SHOTS = [
    Shot("CR_SH01", _roll, duration=46.0, music="credits", transition="fade_black", trans_dur=1.5,
         sfx=[Sfx("night_bed", 0, -16, dur=46)]),
    Shot("CR_SH02", _postcredits, duration=9.0, music="postcredits", transition="fade_black", trans_dur=1.0,
         sfx=[Sfx("munch", 2.7, -4), Sfx("magic_float", 3.2, -6), Sfx("dog_whine", 5.0, -8)]),
]
