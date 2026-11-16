# Score: The Weather Keeper of Block C

Everything is synthesized in code: `src/anim/films/weather_keeper/{motifs,cues,sfx,synth_extra}.py`, plus the shared instrument library in `src/anim/audio/synth.py`.

- **Key and scale:** Sa = G, with a tanpura drone on G2.
- **The Keeper and the Monsoon** use a monsoon-raag colour, a Megh-like pentatonic: **G A C D F** (Sa Re ma Pa komal-ni). The scale belongs to the tradition; the melodies are original.
- **Bhaap** is in bright G major.
- **New instruments** (in `synth_extra.py`): sitar (jawari bloom), shehnai, trumpet, trombone, tuba, glockenspiel, pizzicato strings, string section (lines and chords), snare, kick, dhol, cymbal and timpani.

## The three leitmotifs

Notes are written as pitch(beats).

### 1. Keeper's theme
4/4, ♩=56, 16 beats. A slow, lonely solo, usually on sarangi.

```
G4(1) A4(½) C5(1½) D5(1) | C5(½) A4(½) G4(3) | F4(1) G4(½) A4(½) C5(1) A4(1) | G4(4)
```

- **1 voice:** Meghnath alone. Used in `cloud_birth`, `photo_alone`, `go_home` (fragments), `aftermath` and the `keeper_bed` fallback.
- **2 voices:** adds a bansuri counter-line `D4(4) F4(2) D4(2) C4(2) F4(2) D4(4)`, the first kid holding the wire, plus string chords. Used in `recruited` and `workshop_reveal`.
- **3 voices:** adds a pizzicato bass `G2(4) F2(2) C3(2) F2(2) A2(2) G2(4)` and a glockenspiel doubling. Used in `three_keys`, `keeper_laughs`, `notebook_passed` and `credits`.
- **Other appearances:**
  - Heroic, on strings and trombone, in `storm_rescue`.
  - Comic, on tuba, in `stairs_khadoos`.
  - On shehnai, in `block_life`.
- **Chords:** Gsus2 → Fsus2 → Csus2 → G (open fifths).

### 2. Bhaap's theme
2/4, ♩=132, 10 beats. Glockenspiel and pizzicato.

```
D5(¼) E5(¼) D5(½) B4(½) G4(½) | A4(¼) B4(¼) D5(½) G5(1) | E5(¼) D5(¼) B4(½) A4(¼) G4(¼) E4(½) | G4(½) A4(½) B4(½) G4(1) | rest(1½)
```

- **Pizzicato/glock:** glockenspiel melody, pizz doubling an octave down, and a quarter-note pizz bass `G2 D3 C3 D3 E2 B2 C3 D3`. Used in `coda`.
- **Tiny:** a glockenspiel-only version. Used in `cloud_birth` (when he opens his eyes), `smog_sweep`, `notebook`, `bhaap_returns` and `postcredits`.
- **Brass band:** trumpet, tuba oom-pah, trombone stabs, snare and kick. Used in `montage_brass`, `first_rain_dance` and `credits`.
- **Sad:** B→A♯ and E→D♯, played slowly, glock plus a low bansuri, like drizzle. Used in `go_home` and `waiting`.

### 3. Monsoon theme
4/4, ♩=72, 28 beats. Swelling. It arrives in full only at the climax.

```
C5(1) D5(1) F5(1½) D5(½) C5(1) A4(1) G4(2) |
A4(1) C5(1) D5(1) G5(1) F5(1½) D5(½) C5(2) |
D5(1) F5(1) G5(1) A5(1) G5(1½) F5(½) D5(1) C5(1) G5(4)
```

- **Instrumentation:** string line, shehnai joining for the second half, sitar doubling and arpeggios, sus-chord string pads, tabla keherwa, dhol on the downbeats, and cymbals.
- **Hint:** just the first four notes, `C5 D5 F5 D5`, on shehnai over a purple pad. Heard only in Varsha's memory (`varsha_memory`), as the slowmo foreshadow (`bowl_slowmo`), and as the tag of `notebook_passed`.
- **Full:** `monsoon_full`, then the finale of `credits`.
- **Dance:** ♩=112, with a dhol-slap groove. Used in `first_rain_dance`.

## Cues
Each cue plays until the next one starts; `""` is silence. Hits are seconds into the cue.

| Cue | Use | Hits |
|---|---|---|
| `heat_open` | heat-haze sitar drips, drone, Keeper fragment | [0] thermometer *ping*, [1] power cut (music sags to the drone, trombone droop) |
| `block_life` | bustling courtyard: pizz walk, harmonium, tabla, shehnai Keeper | comic trombone stings |
| `stairs_khadoos` | grumpy tuba Keeper and tiptoe pizz | low tuba plus timpani stinger |
| `roof_sneak` | sneaky pizz, glock taps | [0] cooker whistle: music stops dead |
| `cloud_birth` | Keeper's theme, 1 voice | [0] Bhaap opens his eyes: sparkle, then Bhaap tiny |
| `caught` | comic freeze, tremolo strings | timpani and tuba thumps |
| `recruited` | Keeper, 2 voices | — |
| `workshop_reveal` | silver-blue cathedral: glock arpeggios, Keeper on strings, 2 voices | [0] string swell and cymbal |
| `montage_brass` | Bhaap brass band (alternates keys, pizz bars) | cymbal accents |
| `smog_sweep` | brushed snare, pizz bass, Bhaap tiny | — |
| `hailstorm` | comic chaos: pizz and glock rattles, falling tuba | crashes |
| `notebook` | Bhaap tiny, slow, harmonium-ish pads | — |
| `photo_alone` | Keeper solo, very soft | — |
| `overdue` | ticking pizz, low strings, Keeper fragments | — |
| `trunk_reveal` | low strings, sitar shimmer | [0] dhol and timpani boom, then more booms |
| `varsha_memory` | Monsoon hint | [0] where the hint starts |
| `go_home` | Keeper fragment, then sad Bhaap | — |
| `dadi_night` | bansuri Keeper over minor pads | — |
| `shortcut_sneak` | sneaky low pizz, tension rising | [0] lid lifts: cut |
| `aandhi` | dust storm: driving dhol, tremolo strings, sitar swirls | brass blasts |
| `storm_rescue` | heroic Keeper on strings and trombone over drums | [0] storm pulled down: swell, then deflate |
| `aftermath` | sparse pizz, Keeper tail | — |
| `waiting` | sad Bhaap, slow, long silences | — |
| `bhaap_returns` | Bhaap tiny, tender, with strings | sparkles |
| `three_keys` | Keeper, 3 voices | sparkles |
| `bowl_slowmo` | heartbeat kick, timpani riser, Monsoon hint | [0] the key CLICKS: swell and sparkle |
| `monsoon_full` | the Monsoon theme in full | [0] lid lifts: swell |
| `first_rain_dance` | Monsoon dance plus Bhaap brass | — |
| `keeper_laughs` | Keeper, 3 voices, on strings | — |
| `notebook_passed` | Keeper, 3 voices, then Monsoon hint | — |
| `coda` | Bhaap pizz/glock, sunny; Keeper tag | — |
| `credits` | Bhaap brass, then Keeper 3 voices, then Monsoon full | — |
| `postcredits` | Bhaap tiny, fast, with a sparkle | — |
| `keeper_bed` | soft Keeper bed; also the fallback for any unknown cue id | — |

## Sound effects
The registry is in `sfx.py`. Beds render the full `dur` you ask for.

- **Signature sounds:**
  - `pressure_cooker_whistle`: two chuffs, then a rising squeal and a hiss tail. This is the sound of cloud-making.
  - `FIRST_DROP_TIN` (alias `first_drop_tin`): one fat raindrop on tin, a "tunk" with a long metallic ring.
- **Rain:** `raindrops_tin` with a `density` param (0–1); it starts sparse and grows denser toward that end value.
- **Thunder:** `thunder` with `dist`, from 0 (near crack) to 1 (far roll).
- **Wind:** `wind_gusts` with `build`, from 0 to 1.
- **Plate drum:** `steel_plate_drum` with `bpm`.
- **Synthesized voices:** `crowd_howl_distant` and `cheers_distant` layer the shared kid voices (Kokoro TTS). `power_cut_groan` and `creaky_laugh` are fully synthesized.
