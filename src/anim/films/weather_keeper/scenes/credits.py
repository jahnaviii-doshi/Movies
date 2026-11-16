"""End credits for The Weather Keeper of Block C (rolling, flat-graphic sky), then a post-credits tag:
Captain the pigeon tries to spin his own cloud. It goes about as well as you'd expect."""
from __future__ import annotations

import math

import skia

from .... import core as K, fx
from ....core import W, H, fill, stroke, lerp, clamp
from ....timeline import Shot, Sfx
from ..rig import draw_bhaap, draw_pigeon, draw_pressure_cooker, draw_stove
from ..sets import roof, skyline
from ..sets import weather_fx as WX

CREDITS = [
    ("title", "The Weather Keeper of Block C"),
    ("gap", ""),
    ("head", "Written, directed, designed and animated"),
    ("name", "Claude (Anthropic)"),
    ("small", "Every frame drawn in code: flat-graphic rigs, sets, wind, rain and one small cloud"),
    ("gap", ""),
    ("head", "Starring"),
    ("pair", ("Tara", "who writes everything down")),
    ("pair", ("Ishaan", "who waits")),
    ("pair", ("Rehan", "who bowls")),
    ("pair", ("Meghnath", "Keeper of the weather")),
    ("pair", ("Bhaap", "a cloud")),
    ("pair", ("Captain", "a pigeon with opinions")),
    ("gap", ""),
    ("head", "Voices"),
    ("small", "Kokoro-82M open text-to-speech model (Apache-2.0), run locally"),
    ("gap", ""),
    ("head", "Music & sound"),
    ("small", "Original score and sound effects composed and synthesized in code"),
    ("small", "Sitar, shehnai, sarangi, tabla, bansuri and a small brass band: all built from waveforms"),
    ("gap", ""),
    ("head", "Tools"),
    ("small", "Skia (skia-python) · NumPy · SciPy · FFmpeg · Python"),
    ("gap", ""),
    ("small", "Block C, Sector 9 exists only here. Please water your plants anyway."),
    ("gap", ""),
    ("head", "Somebody has to keep it."),
]

SIZES = {"title": 84, "head": 36, "name": 56, "small": 30, "pair": 42, "gap": 40}
GAP = 34
HOLD = 6.5


def _layout():
    ys, y = [], 0
    for kind, _ in CREDITS:
        y += SIZES[kind] + GAP
        ys.append(y)
    return ys


def _roll(cv, c):
    t = c.t
    # a calm, rain-washed dusk sky over the wet skyline
    cv.drawRect(skia.Rect.MakeWH(W, H), K.lin((0, 0), (0, H), ["#24344c", "#3b5672", "#6d8aa0"]))
    with K.layer(cv, alpha=0.55):
        skyline.draw_skyline(cv, t, "monsoon_night", cam_x=lerp(0, 220, c.u), rain=0.0, pigeons=False,
                             lightning_on=False)
    cv.drawRect(skia.Rect.MakeWH(W, H), K.lin_a((0, 0), (0, H), [("#101827", 0.55), ("#101827", 0.15),
                                                                  ("#101827", 0.6)]))
    ys = _layout()
    start, stop = H + 40, H / 2 + 20 - ys[-1]
    k = clamp(t / max(1.0, c.dur - HOLD))
    off = lerp(start, stop, k)
    bx = lerp(-120, W + 140, (t / 22.0) % 1.0) if t < c.dur - HOLD else lerp(W * 0.5 + 360, W * 0.5 + 330,
                                                                               clamp((t - (c.dur - HOLD)) / 1.5))
    by = 170 + 18 * math.sin(t * 1.4) if t < c.dur - HOLD else H / 2 - 40
    for (kind, txt), yy in zip(CREDITS, ys):
        y = off + yy
        if y < -100 or y > H + 120:
            continue
        a = clamp(min((y + 40) / 220, (H + 40 - y) / 220))
        sz = SIZES[kind]
        if kind == "title":
            K.text_center(cv, txt, W / 2, y, size=sz, color="#e8f4ff", a=a, italic=True, bold=True)
        elif kind == "head":
            last = txt.startswith("Somebody")
            K.text_center(cv, txt, W / 2, y, size=sz + (16 if last else 0), color="#9fd7ff" if not last else "#ffffff",
                          a=a, family="DejaVu Serif" if last else "DejaVu Sans", bold=True, italic=last)
        elif kind == "name":
            K.text_center(cv, txt, W / 2, y, size=sz, color="#ffffff", a=a, italic=True)
        elif kind == "small":
            K.text_center(cv, txt, W / 2, y, size=sz, color="#d4e2ec", a=a, family="DejaVu Sans")
        elif kind == "pair":
            f1 = K.font(sz, "DejaVu Serif", True, True)
            f2 = K.font(sz * 0.72, "DejaVu Sans")
            w1 = f1.measureText(txt[0])
            cv.drawString(txt[0], W / 2 - 30 - w1, y, f1, fill("#ffffff", a))
            cv.drawString(txt[1], W / 2 + 30, y + 2, f2, fill("#b9cfdd", a))
    # Bhaap drifts across the top, drizzling on the names as he goes; at the end he settles by the last line
    settled = t >= c.dur - HOLD
    WX.rain(cv, t, 0.8, wind=0.0, rect=(bx - 60, by + 30, bx + 60, by + 420), seed=7, n=60, speed=650,
            length=20, color="#9fd7ff", splash=False)
    draw_bhaap(cv, bx, by, 1.0, t, mood="happy" if settled else "sleepy", mouth=0.3 if settled else 0.0,
               spark=0.4 if settled and (t % 2) < 0.4 else 0.0)
    # Captain walks along the bottom edge, stops under the last line, stands on one leg
    run = clamp(t / (c.dur - HOLD))
    gx = lerp(-80, W * 0.5 - 380, run)
    draw_pigeon(cv, gx, H - 26, 1.3, t, mode="stand" if run < 1 else "one_leg", head_bob=1.0 if run < 1 else 0.0)


# ------------------------------------------------------------------ post-credits tag
def _frazzle(cv, x, y, s, t, k):
    """Puffed-up singed feathers + a wisp of smoke around a just-zapped pigeon."""
    if k <= 0:
        return
    for i in range(11):
        a = -math.pi * 0.95 + i * math.pi * 0.95 / 10
        r0, r1 = 34 * s, (52 + 8 * (i % 2)) * s
        cv.drawLine(x + math.cos(a) * r0, y - 34 * s + math.sin(a) * r0 * 0.8,
                    x + math.cos(a) * r1, y - 34 * s + math.sin(a) * r1 * 0.8, stroke("#5d6880", 3 * s, k))
    for j in range(3):
        u = (t * 0.6 + j * 0.33) % 1.0
        cv.drawCircle(x + 10 * s + 18 * s * math.sin(u * 6 + j), y - 90 * s - u * 70 * s, (10 + 10 * u) * s,
                      fill("#9aa1ad", 0.5 * k * (1 - u)))


def _tag(cv, c):
    t = c.t
    cam = (860, 720, 2.6)
    T_WHIS, T_SPIN, T_POOF, T_SNEEZE, T_RAIN, T_TURN = 0.4, 2.0, 3.6, 5.2, 6.4, 8.2
    spin = K.smooth(c.seg(T_SPIN, T_POOF))
    roof.draw_roof(cv, t, "heat", "wide", steam_on=1.0 if t < T_POOF else 0.4, spin=spin * 0.6, cam=cam)
    cx, cy = roof.ANCHORS["cooker"]
    with K.camera(cv, *cam):
        with K.lit(cv, "heat", amount=0.6):
            # Captain on the stove rim, flapping one wing in circles like Meghnath's hand
            px, py = cx + 130, cy + 80
            if t < T_SPIN:
                mode = "stand"
            elif t < T_POOF:
                mode = "flap"
            elif t < T_TURN:
                mode = "stand"
            else:
                mode = "turn_away"
            zap = K.smooth(c.seg(T_SNEEZE, T_SNEEZE + 0.15))
            draw_pigeon(cv, px, py, 2.4, t, flip=True, mode=mode, head_bob=1.0 if t < T_SPIN else 0.0,
                        lid=0.9 if t > T_SNEEZE else 0.45)
            _frazzle(cv, px, py, 2.4, t, zap)
        # the tiny lopsided cloud he makes
        if t > T_POOF:
            grow = K.ease_out_back(c.seg(T_POOF, T_POOF + 0.5), 2.2)
            lx, ly = px - 60, py - 210 + 6 * math.sin(t * 2)
            cv.save(); cv.translate(lx, ly); cv.rotate(-14); cv.scale(1.25, 0.8)
            draw_bhaap(cv, 0, 0, 0.62 * grow, t, mood="shy" if t < T_SNEEZE - 0.4 else "excited",
                       spark=1.0 if T_SNEEZE < t < T_SNEEZE + 0.35 else 0.0,
                       rain=1.0 if t > T_RAIN else 0.0, squash=0.6 if T_SNEEZE - 0.3 < t < T_SNEEZE else 0.0,
                       grey=0.25)
            cv.restore()
            if T_SNEEZE < t < T_SNEEZE + 0.3:
                fx.flash(cv, "#fff7c0", 0.25)
                for i in range(3):
                    WX.lightning(cv, t, [(lx - 10 + i * 10, ly + 20), (lx + i * 14 - 5, ly + 60), (px - 10, py - 40)],
                                 a=0.9, seed=i, width=3)
            if t > T_RAIN:
                WX.rain(cv, t, 1.0, wind=0.0, rect=(lx - 40, ly + 10, lx + 40, py), seed=9, n=40, speed=600,
                        length=16, color="#6aa8d8", splash=False)
        if T_POOF - 0.1 < t < T_POOF + 0.6:
            fx.sparkles(cv, t, px - 60, py - 210, spread=50, n=8, color="#ffffff", size=6, seed=4,
                        a=1 - c.seg(T_POOF, T_POOF + 0.6))


SHOTS = [
    Shot("CR_SH01", _roll, duration=46.0, music="credits", transition="fade_black", trans_dur=1.5,
         sfx=[Sfx("night_bed_delhi", 0, -20, dur=46.0), Sfx("raindrops_tin", 0, -24, dur=46.0, params={"density": 0.2})]),
    Shot("CR_SH02", _tag, duration=10.0, music="postcredits", transition="fade_black", trans_dur=1.0,
         sfx=[Sfx("heat_bed", 0, -20, dur=10.0), Sfx("pressure_cooker_whistle", 0.4, -8), Sfx("pigeon_coo", 1.4, -10),
              Sfx("pigeon_flap", 2.1, -8), Sfx("steam_hiss", 2.2, -14), Sfx("cloud_puff", 3.6, -6),
              Sfx("bhaap_sneeze_spark", 5.2, -4), Sfx("bhaap_drizzle", 6.4, -10, dur=3.6), Sfx("pigeon_coo", 8.3, -8)]),
]
