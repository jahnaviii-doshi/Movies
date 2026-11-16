"""Procedural sound effects for The Weather Keeper of Block C. REGISTRY[name](dur=None, **params)
-> (N, 2) float32 @ 48 kHz. Spot effects peak around -6 dBFS; beds (`*_bed`, ambiences, rain,
storms, winds) render the full requested `dur` themselves and sit near -30 dBFS RMS.
The pressure-cooker whistle (cloud-making) and FIRST_DROP_TIN (the first raindrop on a tin roof)
are the two signature sounds.
"""
from __future__ import annotations

import numpy as np

from ...audio import synth as S
from ...audio.sfx import (_kid_layers, _rng, bed, coo, creak, crickets_bed, glide_tone, metal, noise_sweep, shimmer,
                          space, spot, st, thump, whoosh, wood)
from . import synth_extra as X

SR = S.SR
ns, t_axis, noise = S.ns, S.t_axis, S.noise


def _sum(*xs):
    """Sum mono signals of different lengths (zero-padded to the longest)."""
    n = max(len(x) for x in xs)
    out = np.zeros(n)
    for x in xs:
        out[: len(x)] += x
    return out


def _len(dur, default):
    return float(dur) if dur else float(default)


def _place(out, t, sig, p=0.0, gain=1.0):
    s = sig if sig.ndim == 2 else st(sig, p)
    i = ns(t) if t > 0 else 0
    if i >= len(out):
        return
    m = min(len(s), len(out) - i)
    out[i: i + m] += gain * s[:m]


# ------------------------------------------------------------------ cloud-making & Bhaap
def pressure_cooker_whistle(dur=None, seed=1):
    """THE sound of cloud-making: two chuffs, then a rising piercing squeal that settles, hiss tail."""
    D = _len(dur, 3.2)
    n = ns(D)
    out = np.zeros((n, 2))
    # chuffs (steam puffs lifting the weight)
    for k, t0 in enumerate((0.0, 0.35)):
        c = S.bp(noise(ns(0.22), seed + k), 600, 4000) * np.exp(-t_axis(ns(0.22)) / 0.06)
        _place(out, t0, c, 0.0, 0.5)
        _place(out, t0, wood(1400, 0.05, seed + k) * 0.25, 0.1)
    # whistle: pitch rises 1.4k -> 2.6k with flutter, plus breathy band
    w0, wl = 0.6, max(0.8, D - 1.2)
    m = ns(wl)
    t = t_axis(m)
    f = 1400 + 1200 * (1 - np.exp(-t / 0.35)) + 40 * np.sin(2 * np.pi * 9 * t)
    tone = np.sin(np.cumsum(2 * np.pi * f / SR)) + 0.25 * np.sin(np.cumsum(2 * np.pi * 2 * f / SR))
    env = np.clip(t / 0.25, 0, 1) * np.clip((wl - t) / 0.4, 0, 1)
    breath = S.bp(noise(m, seed + 7), 1800, 5500) * 0.6
    _place(out, w0, (0.55 * tone + breath) * env, 0.05)
    # hiss tail
    h = S.hp(noise(ns(1.0), seed + 9), 2500) * np.linspace(0.5, 0, ns(1.0)) ** 2
    _place(out, D - 1.0, h, 0.0, 0.4)
    return spot(space(out, 0.12, 1.0), 0.45)


def steam_hiss(dur=None, seed=2):
    D = _len(dur, 2.0)
    n = ns(D)
    x = S.hp(noise(n, seed), 2500) * (0.7 + 0.3 * np.sin(2 * np.pi * 3 * t_axis(n)))
    x *= np.sin(np.pi * np.linspace(0, 1, n)) ** 0.5
    return spot(st(x), 0.25)


def cloud_puff(dur=None, seed=3):
    n = ns(0.6)
    t = t_axis(n)
    x = S.lp(noise(n, seed), 900) * np.exp(-t / 0.12) * (1 - np.exp(-t / 0.01))
    x += 0.4 * np.sin(2 * np.pi * (220 - 80 * t) * t) * np.exp(-t / 0.1)
    return spot(space(x, 0.2, 1.0), 0.35)


def _chirp_voice(notes, vowel="u", shift=1.6, vel=0.8):
    return S.voice(notes, vowel, vel=vel, formant_shift=shift, vib_depth=0.02, breathy=0.2)


def bhaap_giggle(dur=None, seed=4):
    """A tiny, airy, wordless giggle (high 'oo' blips)."""
    g = _rng(seed)
    notes = [(i * 0.09, 0.07, 900 + 120 * g.uniform(-1, 1) + 60 * i, 0.8) for i in range(6)]
    x = _chirp_voice(notes, "u", 1.9)
    return spot(space(x, 0.18, 0.8, 0.6), 0.3)


def bhaap_coo(dur=None, seed=5):
    x = _chirp_voice([(0, 0.25, 700, 0.8), (0.25, 0.35, 880, 0.8)], "u", 1.8)
    return spot(space(x, 0.18, 0.8, 0.6), 0.3)


def spark_tzik(dur=None, seed=6):
    """A tiny lightning zap: electric crackle + bright ping."""
    n = ns(0.35)
    t = t_axis(n)
    g = _rng(seed)
    crack = S.hp(noise(n, seed), 3000) * (g.random(n) < 0.08) * np.exp(-t / 0.05) * 3
    zap = np.sin(np.cumsum(2 * np.pi * (3200 - 2200 * np.clip(t / 0.08, 0, 1)) / SR)) * np.exp(-t / 0.06)
    ping = 0.5 * np.sin(2 * np.pi * 2600 * t) * np.exp(-t / 0.12)
    return spot(space(crack + zap + ping, 0.15, 0.8, 0.8), 0.4)


def bhaap_sneeze_spark(dur=None, seed=7):
    n1 = ns(0.25)
    ah = _chirp_voice([(0, 0.18, 820, 0.7), (0.18, 0.05, 1200, 0.5)], "a", 2.0)
    out = np.zeros(ns(0.8))
    out[: len(ah)] += ah[: len(out)] * 0.8
    tz = spark_tzik(seed=seed)[:, 0]
    out[ns(0.22): ns(0.22) + len(tz)] += tz[: len(out) - ns(0.22)]
    return spot(out, 0.4)


def bhaap_drizzle(dur=None, seed=8):
    """Gentle patter of a tiny cloud raining (sad)."""
    D = _len(dur, 3.0)
    n = ns(D)
    out = np.zeros(n)
    g = _rng(seed)
    for _ in range(int(D * 28)):
        i = int(g.integers(0, n - ns(0.05)))
        f = g.uniform(1800, 4200)
        m = ns(0.04)
        out[i: i + m] += np.sin(2 * np.pi * f * t_axis(m)) * np.exp(-t_axis(m) / 0.008) * g.uniform(0.3, 1.0)
    out += 0.15 * S.bp(noise(n, seed + 1), 3000, 8000)
    return spot(space(st(out, 0.0), 0.15, 0.8), 0.18)


# ------------------------------------------------------------------ the block, the heat
def ceiling_fans_stop(dur=None, seed=9):
    """A hundred fans whirring down together: wobbling hum + whoosh falling in pitch."""
    D = _len(dur, 3.5)
    n = ns(D)
    t = t_axis(n)
    rate = 9.0 * np.exp(-t / (D * 0.35))
    amp = np.exp(-t / (D * 0.45))
    blade = (0.5 + 0.5 * np.sin(np.cumsum(2 * np.pi * rate / SR))) ** 2
    air = S.bp(noise(n, seed), 250, 1400) * blade * amp
    hum = 0.3 * np.sin(np.cumsum(2 * np.pi * (100 * np.clip(rate / 9, 0.3, 1)) / SR)) * amp
    return spot(space(np.stack([air + hum, air * 0.9 + hum], 1), 0.25, 1.6), 0.3)


def cooler_hum(dur=None, seed=10):
    D = _len(dur, 8.0)
    n = ns(D)
    t = t_axis(n)
    x = 0.5 * np.sin(2 * np.pi * 50 * t) + 0.25 * np.sin(2 * np.pi * 100 * t) + 0.5 * S.bp(noise(n, seed), 200, 900)
    return bed(st(x), 0.02)


def power_cut_groan(dur=None, seed=11):
    """Off-screen collective 'uhhhh' from every floor at once (layered synthetic voices)."""
    D = _len(dur, 2.6)
    out = np.zeros((ns(D) + ns(1.0), 2))
    g = _rng(seed)
    for k in range(14):
        f0 = g.uniform(110, 260)
        L = g.uniform(1.4, D)
        notes = [(0.0, L * 0.4, f0, 0.8), (L * 0.4, L * 0.6, f0 * 0.82, 0.7)]
        v = S.voice(notes, "o" if k % 3 else "a", vel=0.6, formant_shift=g.uniform(0.85, 1.3), vib_depth=0.012)
        _place(out, g.uniform(0, 0.35), S.lp(v, 1500), g.uniform(-0.9, 0.9), 0.5)
    out = out[: ns(D)]
    return spot(space(out, 0.35, 2.0, 0.3), 0.3)


def bucket_clang(dur=None, seed=12):
    return spot(space(metal(420, 1.0, 1.0, (1.0, 2.1, 3.3, 4.9), 0.6, seed), 0.2, 1.2), 0.45)


def water_tanker(dur=None, seed=13):
    """Diesel grind arriving + buckets clanging + water gush."""
    D = _len(dur, 6.0)
    n = ns(D)
    t = t_axis(n)
    rpm = 28 + 6 * np.sin(2 * np.pi * 0.3 * t)
    eng = np.sin(np.cumsum(2 * np.pi * rpm / SR)) ** 3 + 0.5 * S.lp(noise(n, seed), 300)
    eng = S.lp(eng, 600) * np.clip(t / 1.5, 0, 1)
    out = st(eng * 0.6, -0.2)
    g = _rng(seed)
    for k in range(int(D * 0.8)):
        _place(out, g.uniform(1.5, D - 0.5), metal(g.uniform(350, 520), 0.8, 1.0, (1.0, 2.1, 3.3, 4.9), 0.5, k),
               g.uniform(-0.7, 0.7), 0.35)
    gush = S.bp(noise(n, seed + 3), 300, 3000) * np.clip((t - 2.0) / 0.5, 0, 1) * 0.4
    out += st(gush, 0.3)
    return spot(space(out, 0.2, 1.4), 0.4)


def ball_tok(dur=None, seed=14):
    n = ns(0.18)
    t = t_axis(n)
    x = np.sin(2 * np.pi * 380 * t) * np.exp(-t / 0.02) + 0.5 * S.bp(noise(n, seed), 1000, 4000) * np.exp(-t / 0.006)
    return spot(space(x, 0.25, 1.2), 0.4)


def door_creak(dur=None, seed=15):
    return spot(space(creak(1.2, 210, 90, seed, 250, 1400), 0.2, 1.3), 0.35)


def padlock_rattle(dur=None, seed=16):
    out = np.zeros(ns(0.8))
    g = _rng(seed)
    for k in range(5):
        x = metal(g.uniform(1800, 2600), 0.25, 1.0, (1.0, 2.7, 5.1), 0.3, k)
        i = ns(k * 0.11 + g.uniform(0, 0.03))
        out[i: i + len(x)] += x[: len(out) - i] * g.uniform(0.5, 1)
    return spot(space(out, 0.15, 0.8), 0.35)


def pigeon_coo(dur=None, seed=17):
    x = np.concatenate([coo(seed), np.zeros(ns(0.15)), coo(seed + 1)])
    return spot(space(x, 0.15, 1.0), 0.35)


def pigeon_flap(dur=None, seed=18):
    out = np.zeros(ns(0.9))
    for k in range(6):
        m = ns(0.07)
        b = S.bp(noise(m, seed + k), 300, 2500) * np.sin(np.pi * np.linspace(0, 1, m))
        i = ns(k * 0.12)
        out[i: i + m] += b * (1 - k * 0.1)
    return spot(space(out, 0.15, 1.0), 0.4)


def pigeon_flock(dur=None, seed=19):
    D = _len(dur, 2.5)
    out = np.zeros((ns(D), 2))
    g = _rng(seed)
    for k in range(10):
        f = pigeon_flap(seed=seed + k)
        _place(out, g.uniform(0, D * 0.4), f[:, 0], g.uniform(-0.9, 0.9), 0.5)
    return spot(out, 0.45)


def kite_wind(dur=None, seed=20):
    D = _len(dur, 4.0)
    n = ns(D)
    t = t_axis(n)
    w = noise_sweep(D, 500, 1300, 0.7, seed, env=0.6 + 0.4 * np.sin(2 * np.pi * t / 2.2) ** 2)
    flutter = S.bp(noise(n, seed + 1), 700, 2000) * (0.5 + 0.5 * np.sin(2 * np.pi * 14 * t)) ** 4 * 0.5
    return bed(st(w + flutter), 0.04)


def jar_unscrew(dur=None, seed=21):
    out = np.zeros(ns(0.7))
    for k in range(4):
        x = S.bp(noise(ns(0.08), seed + k), 2000, 6000) * np.exp(-t_axis(ns(0.08)) / 0.02)
        i = ns(k * 0.15)
        out[i: i + len(x)] += x
    pop = np.sin(2 * np.pi * 900 * t_axis(ns(0.06))) * np.exp(-t_axis(ns(0.06)) / 0.01)
    out[ns(0.62): ns(0.62) + len(pop)] += pop[: len(out) - ns(0.62)]
    return spot(out, 0.35)


def jar_breeze(dur=None, seed=22):
    """A breeze swirling down into a jar, then the lid screwed on with a 'tink'."""
    D = _len(dur, 2.2)
    n = ns(D)
    w = noise_sweep(D - 0.4, 2500, 500, 0.8, seed)
    out = np.zeros(n)
    out[: len(w)] += w
    tink = metal(1900, 0.6, 0.7, (1.0, 2.8, 5.0), 0.4, seed)
    i = ns(D - 0.45)
    out[i: i + len(tink)] += tink[: n - i]
    return spot(space(out, 0.2, 1.0), 0.4)


def broom_sweep(dur=None, seed=23):
    D = _len(dur, 1.6)
    out = np.zeros(ns(D))
    k = 0
    while k * 0.5 < D - 0.4:
        m = ns(0.38)
        s = S.bp(noise(m, seed + k), 1500, 7000) * np.sin(np.pi * np.linspace(0, 1, m)) ** 1.5
        i = ns(k * 0.5)
        out[i: i + m] += s[: len(out) - i]
        k += 1
    return spot(st(out), 0.3)


def sack_tie(dur=None, seed=24):
    out = np.zeros(ns(0.7))
    rustle = S.bp(noise(ns(0.4), seed), 800, 5000) * np.sin(np.pi * np.linspace(0, 1, ns(0.4)))
    out[: len(rustle)] += rustle * 0.6
    snap = S.bp(noise(ns(0.05), seed + 1), 1000, 6000) * np.exp(-t_axis(ns(0.05)) / 0.008)
    out[ns(0.5): ns(0.55)] += snap
    return spot(out, 0.35)


def hail_rattle(dur=None, seed=25):
    """A mini hailstorm: marbles in a box + ice on a helmet and stumps."""
    D = _len(dur, 3.0)
    n = ns(D)
    out = np.zeros((n, 2))
    g = _rng(seed)
    for k in range(int(D * 70)):
        f = g.uniform(1500, 5000)
        m = ns(0.05)
        x = np.sin(2 * np.pi * f * t_axis(m)) * np.exp(-t_axis(m) / 0.007) + 0.4 * S.bp(noise(m, k), 2000, 8000) * np.exp(-t_axis(m) / 0.004)
        _place(out, g.uniform(0, D - 0.06), x, g.uniform(-0.9, 0.9), g.uniform(0.2, 0.7))
    for k in range(int(D * 2)):   # helmet / plastic tocks
        _place(out, g.uniform(0, D - 0.2), wood(g.uniform(500, 900), 0.1, k), g.uniform(-0.5, 0.5), 0.6)
    return spot(space(out, 0.12, 1.0), 0.45)


def stumps_fall(dur=None, seed=26):
    out = np.zeros(ns(0.9))
    for k, f in enumerate((650, 720, 590)):
        x = wood(f, 0.15, seed + k)
        i = ns(k * 0.09)
        out[i: i + len(x)] += x
    rattle = S.bp(noise(ns(0.3), seed + 5), 800, 3000) * np.exp(-t_axis(ns(0.3)) / 0.08) * 0.4
    out[ns(0.3): ns(0.6)] += rattle
    return spot(space(out, 0.2, 1.4), 0.4)


def crowd_howl_distant(dur=None, seed=27):
    """Off-screen cricket kids howling, far away across the ground."""
    x = _kid_layers(["Aaaah!", "Hey! Hey!", "Ow ow ow!", "Run! Run!", "Aaaaah!"], seed, 6, 0.5)
    x = S.lp(x, 2200) if x.ndim == 1 else np.stack([S.lp(x[:, 0], 2200), S.lp(x[:, 1], 2200)], 1)
    return spot(space(x, 0.4, 2.4, 0.3), 0.25)


def metal_hatch(dur=None, seed=28):
    out = np.zeros(ns(1.6))
    cr = creak(0.8, 160, 110, seed, 200, 1100)
    out[: len(cr)] += cr * 0.6
    clank = metal(180, 1.0, 1.0, (1.0, 1.7, 2.9, 4.1), 0.7, seed)
    out[ns(0.7): ns(0.7) + len(clank)] += clank[: len(out) - ns(0.7)]
    return spot(space(out, 0.35, 2.0, 0.4), 0.45)


def workshop_ambience(dur=None, seed=29):
    """The tank workshop: cool airy hum, faint swirling jar breezes, distant wind chimes."""
    D = _len(dur, 10.0)
    n = ns(D)
    t = t_axis(n)
    air = S.bp(noise(n, seed), 120, 900) * (0.7 + 0.3 * np.sin(2 * np.pi * t / 6.0))
    hum = 0.2 * np.sin(2 * np.pi * 73 * t) * (0.8 + 0.2 * np.sin(2 * np.pi * t / 4.0))
    out = st(air + hum)
    g = _rng(seed)
    for k in range(int(D / 1.7)):
        f = float(g.choice([1568.0, 1760.0, 2093.0, 2349.0, 2637.0]))
        _place(out, g.uniform(0, D - 2), S.chime(f, 2.0, 0.3), g.uniform(-0.8, 0.8), 0.25)
    for k in range(int(D / 3.0)):
        w = noise_sweep(1.6, g.uniform(400, 900), g.uniform(1200, 2600), 0.8, seed + k) * 0.5
        _place(out, g.uniform(0, D - 1.7), w, g.uniform(-0.8, 0.8), 0.6)
    return bed(space(out, 0.4, 2.6, 0.5), 0.025)


def calendar_flip(dur=None, seed=30):
    out = np.zeros(ns(0.5))
    for k in range(3):
        m = ns(0.08)
        out[ns(k * 0.12): ns(k * 0.12) + m] += S.bp(noise(m, seed + k), 1500, 7000) * np.sin(np.pi * np.linspace(0, 1, m))
    return spot(out, 0.3)


def chains_unwind(dur=None, seed=31):
    D = _len(dur, 1.8)
    out = np.zeros(ns(D))
    g = _rng(seed)
    for k in range(int(D * 14)):
        x = metal(g.uniform(1400, 3200), 0.2, 1.0, (1.0, 2.6, 4.7), 0.25, k)
        i = ns(g.uniform(0, D - 0.21))
        out[i: i + len(x)] += x * g.uniform(0.3, 0.8)
    return spot(space(out, 0.2, 1.2), 0.4)


def tin_lid_creak(dur=None, seed=32):
    return spot(space(creak(0.9, 240, 140, seed, 400, 2400) + 0.3 * creak(0.9, 300, 200, seed + 1, 1500, 4000), 0.2, 1.2), 0.35)


# ------------------------------------------------------------------ the aandhi
def aandhi_roar(dur=None, seed=33):
    """A huge dust storm: roaring wind with gusts, flapping, rattling debris."""
    D = _len(dur, 8.0)
    n = ns(D)
    t = t_axis(n)
    gust = 0.6 + 0.4 * np.sin(2 * np.pi * t / 2.7) * np.sin(2 * np.pi * t / 4.1 + 1)
    low = S.lp(noise(n, seed), 260) * 2.5
    mid = S.bp(noise(n, seed + 1), 300, 2400)
    howl = 0.15 * np.sin(np.cumsum(2 * np.pi * (330 + 90 * np.sin(2 * np.pi * t / 3.3)) / SR))
    a = (low + mid * 0.8 + howl) * gust
    b2 = (S.lp(noise(n, seed + 2), 260) * 2.5 + S.bp(noise(n, seed + 3), 300, 2400) * 0.8 + howl) * gust[::-1]
    out = np.stack([a, b2], 1)
    g = _rng(seed)
    for k in range(int(D * 3)):
        _place(out, g.uniform(0, D - 0.3), S.bp(noise(ns(0.25), k), 1200, 6000) * np.exp(-t_axis(ns(0.25)) / 0.05),
               g.uniform(-0.9, 0.9), 0.5)
    env = np.clip(t / 0.8, 0, 1) * np.clip((D - t) / 0.8, 0, 1)
    return bed(out * env[:, None], 0.09)


def laundry_flap(dur=None, seed=34):
    D = _len(dur, 1.5)
    n = ns(D)
    t = t_axis(n)
    x = S.bp(noise(n, seed), 400, 3000) * (0.5 + 0.5 * np.sin(2 * np.pi * 7 * t)) ** 6
    return spot(space(st(x), 0.15, 1.0), 0.35)


def shutter_rattle(dur=None, seed=35):
    D = _len(dur, 1.5)
    out = np.zeros(ns(D))
    g = _rng(seed)
    k = 0.0
    while k < D - 0.15:
        x = metal(g.uniform(300, 600), 0.15, 1.0, (1.0, 1.9, 3.3, 5.2), 0.3, int(k * 100))
        i = ns(k)
        out[i: i + len(x)] += x[: len(out) - i]
        k += g.uniform(0.04, 0.09)
    return spot(space(out, 0.15, 1.0), 0.35)


def chair_cartwheel(dur=None, seed=36):
    D = _len(dur, 1.8)
    out = np.zeros(ns(D))
    k = 0
    while k * 0.28 < D - 0.15:
        x = wood(320 + 30 * (k % 3), 0.12, seed + k) * 0.8 + 0.4 * S.bp(noise(ns(0.12), k), 300, 1500) * np.exp(-t_axis(ns(0.12)) / 0.03)
        i = ns(k * 0.28)
        out[i: i + len(x)] += x[: len(out) - i]
        k += 1
    return spot(space(out, 0.2, 1.2), 0.35)


def klang(dur=None, seed=37):
    """The big tin trunk lid slammed shut."""
    x = _sum(metal(140, 2.0, 1.0, (1.0, 1.6, 2.4, 3.3, 4.7), 0.9, seed), thump(70, 0.6, seed) * 0.8)
    return spot(space(x, 0.3, 1.8), 0.5)


def storm_reverse(dur=None, seed=38):
    """Whooshy reverse suck as the storm is spun back down."""
    D = _len(dur, 3.0)
    n = ns(D)
    t = t_axis(n)
    x = noise_sweep(D, 300, 3000, 0.9, seed, env=(t / D) ** 2)
    y = noise_sweep(D, 250, 2500, 0.9, seed + 1, env=(t / D) ** 2.2)
    swirl = 0.3 * np.sin(np.cumsum(2 * np.pi * (100 + 500 * (t / D) ** 2) / SR)) * (t / D) ** 2
    out = np.stack([x + swirl, y + swirl], 1)
    out[-ns(0.05):] *= np.linspace(1, 0, ns(0.05))[:, None]
    return spot(out, 0.45)


# ------------------------------------------------------------------ beds
def heat_bed(dur=None, seed=39):
    D = _len(dur, 10.0)
    n = ns(D)
    t = t_axis(n)
    cic = S.bp(noise(n, seed), 4200, 7600) * (0.6 + 0.4 * np.sin(2 * np.pi * 52 * t) ** 2) * (0.6 + 0.4 * np.sin(2 * np.pi * t / 6.5))
    traffic = S.lp(noise(n, seed + 1), 240) * 4
    buzz = 0.04 * np.sin(2 * np.pi * 100 * t)
    out = np.stack([cic + traffic * 0.3 + buzz, cic[::-1] + traffic * 0.3 + buzz], 1)
    g = _rng(seed)
    for k in range(int(D / 6)):
        _place(out, g.uniform(0, D - 2), S.lp(glide_tone(400, 380, 0.4, (1, .5, .3)) * 0.1, 900), g.uniform(-0.8, 0.8), 0.5)
    return bed(out, 0.025)


def night_bed_delhi(dur=None, seed=40):
    D = _len(dur, 10.0)
    n = ns(D)
    out = crickets_bed(D, 1.0, seed).astype(np.float64)[:n]
    if len(out) < n:
        out = np.vstack([out, np.zeros((n - len(out), 2))])
    out += st(S.lp(noise(n, seed + 1), 200) * 1.5) * 0.4
    g = _rng(seed)
    for k in range(int(D / 9)):   # a far dog
        bark = glide_tone(520, 420, 0.18, (1, .5, .3)) * np.sin(np.pi * np.linspace(0, 1, ns(0.18)))
        _place(out, g.uniform(0, D - 1), S.lp(bark, 1500) * 0.06, g.uniform(-0.9, 0.9))
    return bed(out, 0.022)


def plane_distant(dur=None, seed=41):
    D = _len(dur, 8.0)
    n = ns(D)
    t = t_axis(n)
    x = S.lp(noise(n, seed), 500) * 2 + 0.1 * np.sin(2 * np.pi * 180 * t)
    env = np.sin(np.pi * t / D) ** 2
    return spot(np.stack([x * env * np.linspace(1.2, 0.6, n), x * env * np.linspace(0.6, 1.2, n)], 1), 0.15)


def wind_gusts(dur=None, seed=42, build=1.0):
    """Night wind building in gusts (build 0..1 = how much it grows)."""
    D = _len(dur, 8.0)
    n = ns(D)
    t = t_axis(n)
    grow = 0.4 + 0.6 * build * (t / D)
    gust = (0.5 + 0.5 * np.sin(2 * np.pi * t / 1.9) * np.sin(2 * np.pi * t / 3.1)) ** 2
    a = (S.lp(noise(n, seed), 500) * 2 + S.bp(noise(n, seed + 1), 500, 1800) * gust) * grow
    b2 = (S.lp(noise(n, seed + 2), 500) * 2 + S.bp(noise(n, seed + 3), 500, 1800) * gust[::-1]) * grow
    return bed(np.stack([a, b2], 1), 0.05)


# ------------------------------------------------------------------ the keys and the trunk
def key_skitter(dur=None, seed=43):
    D = _len(dur, 1.3)
    out = np.zeros(ns(D))
    g = _rng(seed)
    t0 = 0.0
    k = 0
    while t0 < D - 0.1:
        x = metal(g.uniform(2500, 4000), 0.1, 1.0, (1.0, 2.4, 4.4), 0.2, k)
        i = ns(t0)
        out[i: i + len(x)] += x[: len(out) - i] * (1 - t0 / D)
        t0 += 0.03 + 0.1 * (t0 / D)
        k += 1
    scrape = S.bp(noise(len(out), seed), 2000, 7000) * np.linspace(0.5, 0, len(out)) ** 2 * 0.4
    return spot(space(out + scrape, 0.15, 1.0), 0.4)


def slowmo_whoosh(dur=None, seed=44):
    D = _len(dur, 3.0)
    n = ns(D)
    t = t_axis(n)
    x = noise_sweep(D, 120, 500, 0.9, seed) * 2
    rum = 0.4 * np.sin(np.cumsum(2 * np.pi * (45 + 15 * np.sin(np.pi * t / D)) / SR)) * np.sin(np.pi * t / D)
    spin = 0.3 * S.bp(noise(n, seed + 1), 200, 900) * (0.5 + 0.5 * np.sin(2 * np.pi * 2.0 * t)) ** 4
    return spot(space(st(x + rum + spin), 0.35, 2.4, 0.3), 0.45)


def key_click(dur=None, seed=45):
    out = np.zeros(ns(0.8))
    c = _sum(metal(3200, 0.15, 1.0, (1.0, 2.3), 0.2, seed), wood(1800, 0.05, seed) * 0.6)
    out[: len(c)] += c
    ring = S.chime(1568.0, 0.6, 0.6)
    out[ns(0.05): ns(0.05) + len(ring)] += ring[: len(out) - ns(0.05)] * 0.6
    return spot(space(out, 0.2, 1.2), 0.45)


def key_turn_clack(dur=None, seed=46):
    out = np.zeros(ns(0.6))
    a = metal(900, 0.2, 1.0, (1.0, 2.2, 3.9), 0.3, seed)
    b = _sum(thump(140, 0.3, seed) * 0.7, metal(600, 0.3, 1.0, (1.0, 1.8, 3.1), 0.4, seed + 1))
    out[: len(a)] += a * 0.6
    out[ns(0.12): ns(0.12) + len(b)] += b[: len(out) - ns(0.12)]
    return spot(space(out, 0.25, 1.4), 0.5)


def trunk_lid_rise(dur=None, seed=47):
    """Heavy iron hinge groan + rising magic shimmer as the Monsoon Trunk opens."""
    D = _len(dur, 3.5)
    n = ns(D)
    out = np.zeros((n, 2))
    gr = creak(min(2.0, D * 0.6), 90, 60, seed, 150, 900) * 1.2
    _place(out, 0.0, gr, 0.0)
    _place(out, 0.3, shimmer(D - 0.3, 600, 1800, 18, seed, True), 0.0, 0.9)
    pad = S.pad([196.0, 293.66, 440.0], D, 1.0, 0.5)[:n]
    pad = pad * 6 * np.linspace(0, 1, len(pad))
    _place(out, 0.0, pad, 0.0, 0.6)
    return spot(space(out, 0.35, 2.4), 0.45)


def monsoon_roll(dur=None, seed=48):
    """A deep rolling thunder-swell that keeps coming."""
    D = _len(dur, 8.0)
    n = ns(D)
    t = t_axis(n)
    rumble = S.lp(noise(n, seed), 90) * 6 * (0.6 + 0.4 * _norm(S.lp(noise(n, seed + 1), 1.5)))
    swell = np.clip(t / (D * 0.4), 0, 1) * np.clip((D - t) / 1.5, 0, 1)
    out = np.stack([rumble * swell, S.lp(noise(n, seed + 2), 90) * 6 * swell], 1)
    g = _rng(seed)
    for k in range(int(D / 2.5)):
        _place(out, g.uniform(0.5, D - 2), thunder(dist=g.uniform(0.4, 1.0), seed=seed + k), g.uniform(-0.7, 0.7), 0.5)
    return bed(out, 0.07)


def _norm(x):
    return x / (np.max(np.abs(x)) + 1e-9)


def thunder(dur=None, dist=0.5, seed=49):
    """Thunder: near (dist 0) = sharp crack + rumble; far (1) = soft low roll."""
    D = _len(dur, 4.0)
    n = ns(D)
    t = t_axis(n)
    crack = S.hp(noise(n, seed), 800) * np.exp(-t / 0.08) * (1 - dist) * 1.5
    roll = S.lp(noise(n, seed + 1), 120 + 300 * (1 - dist)) * 5 * np.exp(-t / (1.2 + dist)) * (0.6 + 0.4 * _norm(S.lp(noise(n, seed + 2), 4)))
    x = crack + roll
    return spot(space(st(x), 0.4, 3.0, 0.3), 0.6 - 0.3 * dist)


def FIRST_DROP_TIN(dur=None, seed=50):
    """THE sound: one fat raindrop on a tin roof — a soft 'tunk' with a little metallic ring."""
    n = ns(2.2)
    t = t_axis(n)
    body = np.sin(2 * np.pi * 210 * t) * np.exp(-t / 0.035) * 1.2
    ring = metal(1180, 2.2, 1.0, (1.0, 1.47, 2.09, 2.71, 3.62), 1.4, seed) * 0.5
    splash = S.bp(noise(n, seed), 2500, 9000) * np.exp(-t / 0.012) * 0.25
    x = body + ring + splash
    return spot(space(st(x, 0.05), 0.3, 2.2, 0.55), 0.55)


def raindrops_tin(dur=None, density=0.3, seed=51):
    """Drops on tin, sparse -> denser (density 0..1 is the END density; starts sparse)."""
    D = _len(dur, 4.0)
    n = ns(D)
    out = np.zeros((n, 2))
    g = _rng(seed)
    t0 = 0.4
    while t0 < D - 0.3:
        u = t0 / D
        rate = 1.0 + 40 * density * u ** 1.5
        f = g.uniform(900, 1500)
        m = ns(0.6)
        tt = t_axis(m)
        d = np.sin(2 * np.pi * g.uniform(160, 260) * tt) * np.exp(-tt / 0.03) + 0.35 * np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.25)
        _place(out, t0, d, g.uniform(-0.8, 0.8), g.uniform(0.4, 1.0))
        t0 += g.exponential(1.0 / rate)
    return spot(space(out, 0.25, 1.8, 0.5), 0.4)


def rain_roar(dur=None, seed=52):
    """The full downpour on everything: dense hiss, splashes, tin roof drumming, gutters."""
    D = _len(dur, 10.0)
    n = ns(D)
    t = t_axis(n)
    hiss = S.bp(noise(n, seed), 800, 9000) + 0.6 * S.lp(noise(n, seed + 1), 400)
    hiss2 = S.bp(noise(n, seed + 2), 800, 9000) + 0.6 * S.lp(noise(n, seed + 3), 400)
    tin = S.bp(noise(n, seed + 4), 900, 1600) * (0.5 + 0.5 * (_rng(seed).random(n) < 0.02)) * 0.5
    gut = 0.2 * S.bp(noise(n, seed + 5), 150, 500) * (0.7 + 0.3 * np.sin(2 * np.pi * t / 3))
    out = np.stack([hiss + tin + gut, hiss2 + tin * 0.8 + gut], 1)
    env = np.clip(t / 1.0, 0, 1)
    return bed(out * env[:, None], 0.08)


def rain_puddles(dur=None, seed=53):
    D = _len(dur, 6.0)
    n = ns(D)
    out = st(S.bp(noise(n, seed), 1000, 7000) * 0.4)
    g = _rng(seed)
    for k in range(int(D * 12)):
        m = ns(0.08)
        tt = t_axis(m)
        pl = np.sin(np.cumsum(2 * np.pi * (g.uniform(600, 1400) * (1 + 1.5 * tt / 0.08)) / SR)) * np.exp(-tt / 0.02)
        _place(out, g.uniform(0, D - 0.1), pl, g.uniform(-0.8, 0.8), g.uniform(0.2, 0.6))
    return bed(out, 0.035)


def steel_plate_drum(dur=None, seed=54, bpm=120):
    """Someone on a balcony banging a steel plate in rhythm (ta-ta-TAA)."""
    D = _len(dur, 4.0)
    out = np.zeros((ns(D), 2))
    q = 60 / bpm
    pattern = [1, 0, 1, 1, 0, 1, 0, 1]
    t0, i = 0.0, 0
    while t0 < D - 0.3:
        if pattern[i % 8]:
            x = metal(780, 0.5, 1.0, (1.0, 2.31, 3.86, 5.12), 0.5, i % 4) * (1.0 if i % 4 == 0 else 0.7)
            _place(out, t0, x, 0.4)
        t0 += q / 2
        i += 1
    return spot(space(out, 0.3, 1.8), 0.35)


def cheers_distant(dur=None, seed=55):
    x = _kid_layers(["Yaaay!", "Woo hoo!", "It's raining!", "Yay! Yay!", "Hooray!"], seed, 6, 0.5)
    x = np.stack([S.lp(x[:, 0], 3000), S.lp(x[:, 1], 3000)], 1) if x.ndim == 2 else S.lp(x, 3000)
    return spot(space(x, 0.35, 2.4, 0.4), 0.3)


def mud_slide(dur=None, seed=56):
    D = _len(dur, 1.4)
    n = ns(D)
    t = t_axis(n)
    x = S.lp(noise(n, seed), 700) * 3 * np.sin(np.pi * t / D) + 0.3 * S.bp(noise(n, seed + 1), 300, 1500) * (0.5 + 0.5 * np.sin(2 * np.pi * 11 * t))
    sq = 0.3 * np.sin(np.cumsum(2 * np.pi * (300 - 150 * t / D) / SR)) * np.exp(-t / 0.3)
    return spot(space(st(x + sq), 0.15, 1.0), 0.35)


def creaky_laugh(dur=None, seed=57):
    """An old man's big, creaky, surprised laugh (synthesized: 'ha-ha-ha' with vocal fry)."""
    out = np.zeros(ns(2.4))
    syl = [(0.0, 0.32, 150), (0.36, 0.22, 175), (0.62, 0.2, 165), (0.86, 0.2, 155), (1.1, 0.5, 140)]
    for k, (st0, L, f) in enumerate(syl):
        v = S.voice([(0, L, f, 0.9), (L * 0.6, L * 0.4, f * 0.9, 0.7)], "a", vel=0.9, formant_shift=0.92, vib_depth=0.02,
                    breathy=0.3, wobble=0.02)
        fry = 1 + 0.5 * (np.sin(2 * np.pi * 34 * t_axis(len(v))) > 0.6)
        i = ns(st0)
        out[i: i + len(v)] += (v * fry)[: len(out) - i]
    return spot(space(out, 0.15, 1.2), 0.45)


def window_open(dur=None, seed=58):
    out = np.zeros(ns(1.0))
    cr = creak(0.5, 260, 180, seed, 400, 2000) * 0.6
    out[: len(cr)] += cr
    lat = metal(1200, 0.3, 1.0, (1.0, 2.5, 4.2), 0.3, seed)
    out[ns(0.45): ns(0.45) + len(lat)] += lat[: len(out) - ns(0.45)] * 0.6
    return spot(space(out, 0.15, 1.0), 0.35)


def curtain_flutter(dur=None, seed=59):
    D = _len(dur, 2.0)
    n = ns(D)
    t = t_axis(n)
    x = S.bp(noise(n, seed), 300, 2500) * (0.5 + 0.5 * np.sin(2 * np.pi * 4 * t + np.sin(2 * np.pi * 0.7 * t))) ** 3
    return spot(st(x * np.sin(np.pi * t / D)), 0.22)


def school_bell(dur=None, seed=60):
    D = _len(dur, 2.2)
    n = ns(D)
    t = t_axis(n)
    ring = metal(1350, D, 1.0, (1.0, 2.0, 2.76, 3.9), 0.7, seed) * (0.6 + 0.4 * (np.sin(2 * np.pi * 22 * t) > 0))
    return spot(space(st(S.lp(ring, 5000)), 0.35, 2.2, 0.4), 0.25)


def footsteps_slipper(dur=None, seed=61, rate=1.7):
    D = _len(dur, 2.0)
    out = np.zeros(ns(D))
    k = 0
    while k / rate < D - 0.15:
        m = ns(0.09)
        x = _sum(S.bp(noise(m, seed + k), 400, 2500) * np.exp(-t_axis(m) / 0.02), 0.6 * wood(260, 0.06, k))
        m = len(x)
        i = ns(k / rate)
        out[i: i + m] += x[: len(out) - i] * (1.0 if k % 2 else 0.8)
        k += 1
    return spot(st(out), 0.3)


def chilli_watering(dur=None, seed=62):
    D = _len(dur, 2.0)
    n = ns(D)
    t = t_axis(n)
    stream = S.bp(noise(n, seed), 600, 3500) * (0.7 + 0.3 * np.sin(2 * np.pi * 9 * t)) * np.sin(np.pi * t / D) ** 0.5
    soil = S.lp(noise(n, seed + 1), 500) * 0.8 * np.sin(np.pi * t / D)
    return spot(space(st(stream * 0.6 + soil), 0.15, 1.0), 0.25)


REGISTRY = {
    "pressure_cooker_whistle": pressure_cooker_whistle, "steam_hiss": steam_hiss, "cloud_puff": cloud_puff,
    "bhaap_giggle": bhaap_giggle, "bhaap_coo": bhaap_coo, "bhaap_sneeze_spark": bhaap_sneeze_spark,
    "bhaap_drizzle": bhaap_drizzle, "spark_tzik": spark_tzik, "ceiling_fans_stop": ceiling_fans_stop,
    "cooler_hum": cooler_hum, "power_cut_groan": power_cut_groan, "water_tanker": water_tanker,
    "bucket_clang": bucket_clang, "ball_tok": ball_tok, "door_creak": door_creak, "padlock_rattle": padlock_rattle,
    "pigeon_coo": pigeon_coo, "pigeon_flap": pigeon_flap, "pigeon_flock": pigeon_flock, "kite_wind": kite_wind,
    "jar_unscrew": jar_unscrew, "jar_breeze": jar_breeze, "broom_sweep": broom_sweep, "sack_tie": sack_tie,
    "hail_rattle": hail_rattle, "stumps_fall": stumps_fall, "crowd_howl_distant": crowd_howl_distant,
    "metal_hatch": metal_hatch, "workshop_ambience": workshop_ambience, "calendar_flip": calendar_flip,
    "chains_unwind": chains_unwind, "tin_lid_creak": tin_lid_creak, "aandhi_roar": aandhi_roar,
    "laundry_flap": laundry_flap, "shutter_rattle": shutter_rattle, "chair_cartwheel": chair_cartwheel,
    "klang": klang, "storm_reverse": storm_reverse, "heat_bed": heat_bed, "night_bed_delhi": night_bed_delhi,
    "plane_distant": plane_distant, "key_skitter": key_skitter, "wind_gusts": wind_gusts,
    "slowmo_whoosh": slowmo_whoosh, "key_click": key_click, "key_turn_clack": key_turn_clack,
    "trunk_lid_rise": trunk_lid_rise, "monsoon_roll": monsoon_roll, "thunder": thunder,
    "FIRST_DROP_TIN": FIRST_DROP_TIN, "first_drop_tin": FIRST_DROP_TIN, "raindrops_tin": raindrops_tin,
    "rain_roar": rain_roar, "rain_puddles": rain_puddles, "steel_plate_drum": steel_plate_drum,
    "cheers_distant": cheers_distant, "mud_slide": mud_slide, "creaky_laugh": creaky_laugh,
    "window_open": window_open, "curtain_flutter": curtain_flutter, "school_bell": school_bell,
    "footsteps_slipper": footsteps_slipper, "chilli_watering": chilli_watering,
    # convenient aliases for scene authors
    "whoosh_wk": lambda dur=None: whoosh(dur or 0.9, 1.0),
}
