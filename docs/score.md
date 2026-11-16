# The Midnight Sweet Shop: score and sound

Everything is synthesized from scratch in `src/anim/audio/` with numpy and scipy. There are no samples, no external services, and no existing melodies. The output is 48 kHz stereo.

## Key and palette
**Key:** Sa = D. Melodies are mostly Bhupali-flavoured pentatonic (D E F# A B). The harmony underneath uses I, vi, IV and V.

**Instruments (`synth.py`):**

| Instrument | How it's made |
|---|---|
| Santoor | Modal synthesis, double course, hammer tick |
| Bansuri | Breath noise, late vibrato, portamento |
| Harmonium | Two detuned reeds, bellows tremolo |
| Tabla | Dayan rings with a pitch dip, gliding bayan boom; bols na, tin, tun, ke, ge, dha, dhin |
| Tanpura drone | Pa–Sa'–Sa'–Sa cycle with a jawari brightness bloom |
| Sarangi | Saw through vowel formants, slow slides |
| Strings pad | Detuned saws |
| Music box, bells, chimes | Modal |
| Wordless voice | Glottal source + formants: hum "m", "ah", "oo", and "la" onsets |
| Reverb | Synthetic stereo impulse response |

## Leitmotifs (`motifs.py`)

### 1. Amma's Lullaby: six notes, 3/4, ♩ = 66
```
A4 (1)   B4 (½)   F#4 (1½)  |  A4 (1)   F#4 (1)   E4 (3) ...
Pa       Dha      Ga           Pa       Ga        Re
```
- It ends on **Re (E), unresolved**: the story without its ending.
- Harmony: D, then Bm, then an E/A suspension.
- **The ending.** When the story's ending is remembered, the last E is held and a seventh note resolves it: **E4 (2) → D4 (4)**, Re to Sa, over A then D. This is `LULLABY_ENDED`. It is heard only from the climax onward (`blaze`, `dawn_farewell`, `coda`, `credits`).

**Where it appears:**

| Scene | How |
|---|---|
| sc1 | Nani hums it an octave down (`hum_lullaby` SFX, elderly wobble); music box fragments in `rooftop_story` |
| sc2 | The first three notes on a high music box (`midnight_mystery`) |
| sc3 | Santoor and harmonium variations (`shop_warm`) |
| sc5 | Slow bansuri for Chutney's line (`chutney_tender`); a music box that winds down as Amma fades (`fading`) |
| sc7 | Sarangi over minor harmony, Bm–Em–G (`low_point`) |
| sc8 | The wall echoes it as far chimes (`wall_echo_lullaby`). Young Sharda sings "la-la" (`sung_lullaby_child`) over a music-box `memory` bed. Then the full orchestration *with its ending* (`blaze`): "ah" voice, santoor, pads and ostinato |
| sc9–10 | Bansuri and santoor with the ending (`dawn_farewell`, `coda`) |
| Credits | Section C |

### 2. Wonder theme: 4/4, ♩ = 96
```
A4 B4 | F#5 ———— E5 | F#5 A5 | B5 ———— A5 | F#5  E5 D5 | E5 —— | D5 E5 F#5 A5 | D6 ——
```
- It opens with the lullaby's first interval (A–B), then leaps up a sixth: the same seed as the lullaby, but taking flight.
- Under it: a santoor ostinato in eighths (`D4 A4 D5 E5 F#5 E5 D5 A4`) and a D–Bm–G–A pad.
- Appears in: `wonder_unfold`, `flight`, `montage` (♩ = 112, bouncing), `brave` (augmented low on sarangi with bayan booms), `walk_home` (♩ = 84), `blaze`, and credits section A.

### 3. Kabir's swagger: 4/4, ♩ = 108, swung
```
D4 F#4 A4 | B4 A4 | C5 —. B4 | A4 F#4 || A4 | D5 —— | C5 B4 A4 | F#4 | D4 ——
```
- The flat-seventh **C natural** gives it its cocky, bluesy strut. Harmonium carries the tune over a plucked bass and a swung keherwa.
- **Tender version** (`stairs_tender`, ♩ = 60, straight time): the C is sweetened to **C#**, so the brag becomes a promise.
- **Triumphant-tender** (`heavy`, ♩ = 76): the tender version on harmonium with bansuri an octave up, ending with a THUNK boom and a swell.
- Also: `swagger`, `wish_chaos` (♩ = 132), credits section B, and `postcredits` (music box).

## Cues (`cues.py`)

`render_cue(cue_id, duration, hits)` returns an (N, 2) float32 array at 48 kHz.
- Phrases loop to fill any duration.
- Each cue fades in over 0.3 s and out over 1.5 s.
- Every cue is normalised to its own intended level: soft cues are quieter.
- `hits` (seconds into the cue) add swells, sparkles or booms.
- The `dusk` cue's first hit is the power cut: the music drains away, leaving only the drone.
- An unknown cue id gives a warning and a soft generic lullaby bed.

**All cue ids:** dusk, rooftop_story, midnight_mystery, wonder_unfold, shop_warm, flight, dawn_soft, swagger, deflate, montage, brave, chutney_tender, fading, sneak, wish_chaos, crystal_sting, low_point, stairs_tender, wall_hum, memory, blaze, heavy, dawn_farewell, walk_home, coda, credits, postcredits.

## SFX (`sfx.py`)

`sfx(name, dur=None, **params)`
- Spot effects peak at about −6 dBFS.
- Beds (`crickets_bed`, `night_bed`, `day_bed`, `heat_cicadas`, `wind_flight`, `sparrows_dawn`) sit around −30 dBFS RMS and loop with crossfades to `dur`.
- Parameters: `clock_strike(n=12, interval=1.7)`, `whoosh(intensity=1.0)`, `dog_bark(n=2)`, `koel_call(n_calls=3)`, `footsteps_soft(rate=2.2)`.
- `kids_laugh` and `kids_gasp` layer short Kokoro TTS kid voices (`kid1`, `kid2`) with small pitch offsets. If TTS fails, they fall back to synthesized voices.

## Mix (`mix.py`)

Run `python -m anim.audio.mix`. It reads `films/midnight_sweet_shop/edit/timeline.json` and writes to `edit/audio/`:
- Stems: `dialogue.wav`, `music.wav`, `sfx.wav`
- `mix_raw.wav`
- `mix_16lufs.wav`: −16 LUFS, TP ≤ −1.5 dBTP
- `mix_23lufs.wav`: −23 LUFS, TP ≤ −2 dBTP
- `mix_report.json`

How it mixes:
- **Levels:** dialogue −3 dB, music −5 dB, SFX −2 dB, plus each SFX event's own `gain_db`.
- **Ducking:** music ducks 9 dB and SFX 3 dB under dialogue (150 ms attack, 500 ms release).
- **Loudness:** two-pass ffmpeg loudnorm in linear mode. If linear gain would breach the true-peak ceiling, a transparent lookahead limiter runs first so the result stays linear.
- **Speed:** stems are memory-mapped. Cues and SFX are cached by inputs plus an engine-source hash, so a re-mix after timeline changes only re-renders what changed.
