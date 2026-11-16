# Scene authoring guide: The Midnight Sweet Shop

Scenes live in `src/anim/scenes/scNN.py`. Each module exports `SHOTS: list[Shot]` (see `src/anim/timeline.py`).

## Runtime targets (20:00 total, credits excluded)

| Scene | Beat | Target | ± |
|---|---|---|---|
| sc01 | Summer night, title, power cut, Nani's half-story | 90 s | 8 |
| sc02 | Midnight, Chutney, stairs, gali, **the shop unfolds**, Amma | 120 s | 8 |
| sc03 | The rules, Tola, memory bubble, floating laddoo, **the flight**, dawn | 150 s | 10 |
| sc04 | Kabir saw; next midnight; fake kindness; boing; storms out | 120 s | 8 |
| sc05 | Montage: day kindnesses, brave toffee vs monkey, kulfi + Chutney's line, the fading | 150 s | 10 |
| sc06 | The theft; wish jalebis chaos (syrup, flying rickshaw, pink buffalo); crystal fingers | 120 s | 8 |
| sc07 | Gloves at dinner; flickering shop; confession; rule 5; "We need Nani"; shop slams shut | 150 s | 10 |
| sc08 | Waking Nani; the stairs; the hum; young Sharda; **BLAZE**; Kabir's heavy kindness | 150 s | 10 |
| sc09 | Dawn; the thread; "Don't let the story lose its ending"; walk home | 90 s | 8 |
| sc10 | "Next summer"; Meher tells it; the wall shimmers | 60 s | 6 |

Check the runtime of one scene with:

```bash
python -c "from anim.timeline import build_film; s=build_film(['sc03'],False); print(sum(x.duration for x in s))"
```

## Shots

- **IDs** use the form `S{scene:02d}_SH{n:02d}`.
- **Length:** usually 3–9 s, about 6.5 s on average.
- **Duration:** leave `duration=None` and the shot ends at its last line plus `tail`; otherwise set it explicitly.
- **What `draw(cv, c)` covers:** it draws the *complete* frame, background included. The renderer adds paper grain and vignette, and handles transitions (`cut`, `dissolve`, `fade_black`, `fade_white`) from `Shot.transition` and `trans_dur`.
- **Timing context:** `c.t` is seconds into the shot, `c.u` is progress from 0 to 1, and `c.seg(a, b)` gives 0..1 progress between two times. Ease motion with `K.ease_in_out`, `ease_out`, `ease_out_back` and `ease_out_elastic`.
- **Overflow frames:** for dissolves, `draw` may be called with `c.t` greater than the duration (the next shot fades in over it). Clamp anything that would break.
- **Camera:** wrap the set and characters in `with K.camera(cv, cx, cy, zoom, t=c.t):`. Almost every shot gets gentle life: a slow push-in (zoom 1.0 → 1.05), a drift, or a pan. Avoid dead-static frames, but keep moves storybook-gentle.

## Characters

- **Drawing:** `chars.draw(cv, 'meher'|'kabir'|'nani'|'amma'|'young_sharda'|'toddler', x=, y=, s=, t=c.t, mouth=c.mouth('meher'), expr=..., ...)`. Passing `mouth=c.mouth(who)` makes lip-sync automatic. Blinks and breathing are automatic too.
- **Poses:** `turn`, `flip`, `look=(dx,dy)`, `head_tilt`, `lean`, `arms={'l':(shoulder,elbow),'r':(...)}`, `hand={'r':'point'|'fist'|'open'|'thumbsup'}`, `legs='stand'|'walk'|'sit'|'float'|'tiptoe'|'kneel'` (walk takes `phase`), `hold='bottle'|'torch'|'book'|'laddoo'|'toffee'|'kulfi'|'lota'|'slippers'|'fan'|'jar'|'specs'`, and `extra={...}`.
  - Kabir's `extra` takes `crystal` (0..1), `crystal_wrist` (0..1) and `glove` (True).
  - Nani's `extra` takes `no_specs` (True).
- **Chutney:** `A.draw_dog(cv, A.DogPose(...))` with modes `stand`, `walk`, `trot`, `sit`, `lie`, `float` and `beg`. Other controls: `ear`, `wag`, `look_up`, `mouth`, `tongue`, and `expr` = `happy`|`sad`|`alert`|`sneeze`|`guilty`|`proud`.
- **Tola:** `A.draw_scale(cv, A.ScalePose(...))` with `tilt` (positive = right pan down), `eyes`, `mouth`, `tarnish`, `shine`, `bubble_on`, `jitter`.
- **Others:** `A.draw_buffalo`, `A.draw_monkey` and `A.draw_rickshaw`.
- **Lighting:** match the characters to the set with `with K.lit(cv, 'night'|'moon'|'shop'|'day'|'dusk'|'dawn'|'memory'|'dim'):`.
  - **Amma fading:** `with K.lit(cv, 'shop', alpha=a, desat=d):`, plus `fx.sparkles` drifting off her.
- **Acting:** every line gets a matching expression and a little body language (head tilt on questions, lean-in, arm gesture). Listeners react. Keep comic timing crisp: anticipation, action, a held reaction.
- **Staging limits:** at most 3 characters in frame, plus Chutney and Tola. No crowds; off-screen voices only.

## Effects (`src/anim/fx.py`)

- **Sparkle and glow:** `sparkles`, `motes`, `glow_dot`, `light_pool`, `light_rays`.
- **Bubbles:** `bubble`, and `memory_bubble(cv, x, y, r, t, draw_inside_fn)`. `draw_inside_fn` draws a full 1920×1080 scene, which is fitted inside the bubble and graded sepia.
- **Hits:** `chime_rings`, `vibe_lines`.
- **Heroic shadow:** `hero_shadow(cv, draw_fn, base_x, base_y, grow)`.
- **Screen effects:** `fade`, `flash`, `sugar_crystals`, and `card(cv, t, text)` for title cards.

## Sound

- **Dialogue:** `Line(char, text, at=seconds_into_shot)`. Characters are `meher`, `kabir`, `nani`, `amma`, `chutney`, `kid1` and `kid2`. Audio is synthesized and cached automatically. Use the script's lines exactly. Ellipses and commas shape the delivery.
- **Music:** set `music="<cue id>"` on the shot where a cue starts; it plays until the next cue (`""` means silence). Use `music_hits=[...]` for accents.
  - Cue ids: `dusk`, `rooftop_story`, `midnight_mystery`, `wonder_unfold`, `shop_warm`, `flight`, `dawn_soft`, `swagger`, `deflate`, `montage`, `brave`, `chutney_tender`, `fading`, `sneak`, `wish_chaos`, `crystal_sting`, `low_point`, `stairs_tender`, `wall_hum`, `memory`, `blaze`, `heavy`, `dawn_farewell`, `walk_home`, `coda`, `credits`, `postcredits`.
- **SFX:** `Sfx(name, at, gain_db, dur)`. Beds such as `night_bed`, `day_bed` and `crickets_bed` loop to `dur`, so give every shot an appropriate bed.
  - Names: `crickets_bed`, `night_bed`, `day_bed`, `heat_cicadas`, `train_horn_distant`, `fans_wind_down`, `town_groan`, `clock_strike` (params `n`), `dog_whine`, `dog_bark`, `dog_sneeze`, `dog_howl`, `dog_pant`, `footsteps_soft`, `stair_creak`, `wind_chime_hello`, `wall_glow`, `shop_unfold`, `lantern_light`, `awning_snap`, `floor_creak`, `tola_tink`, `tola_clank`, `tola_clonk`, `tola_laugh`, `tola_alarm`, `tola_clonng`, `tola_thunk`, `jar_chord`, `bubble_rise`, `bubble_settle`, `bubble_fizzle`, `magic_float`, `whoosh`, `wind_flight`, `boing`, `sparkle`, `monkey_chatter`, `shadow_grow`, `syrup_gush`, `slosh`, `rickshaw_bell`, `rickshaw_zoom`, `sploosh`, `buffalo_moo`, `crystal_tink`, `crystal_spread`, `crystal_melt`, `shop_flicker`, `shop_shut`, `jars_refill`, `page_turn`, `water_pour`, `iron_steam`, `koel_call`, `sparrows_dawn`, `kids_laugh`, `kids_gasp`, `hum_lullaby`, `wall_echo_lullaby`, `sung_lullaby_child`, `pop`, `swallow_gulp`, `munch`.

## Review loop (required)

1. Run `python -m anim.render --stills scNN` and LOOK at the contact sheet with the Read tool.
2. Render key moments full-size and look at them too: use `anim.assemble.frame_png(shots, id, t, path)`, saving to the scratchpad.
3. Fix staging, scale, lighting mismatches and anything ugly or confusing. Kids must be able to follow every beat with the sound off.

## Set notes (learned during set review)

- **Sitting:** with `legs='sit'`, the character's `(x, y)` is the **seat contact point**.
  - On rooftop charpais, use `rooftop.ANCHORS['charpai_X']['surface']`, with y + 10 and `s ≈ anchor['s'] * 1.5`. The anchor's own `sit` key predates this convention: do not use it.
- **Standing scale:** pick `s` by eye so a kid is about 40–55% of frame height in a medium shot, and 20–30% in a wide.
- **Cost of `K.lit()`:** each full-frame `lit()` layer costs about 12 ms, so group all characters under ONE `lit()` per shot where possible.
- **Sleeping figures** on charpais: `rooftop.draw_sleeper(cv, x, y, s, t, who, face_cover)`, with `(x, y)` = the bed surface.
- **Torch-lit stairs:** call `stairwell.draw_torch_light(cv, t, (x, y, ang))` AFTER drawing the characters.
