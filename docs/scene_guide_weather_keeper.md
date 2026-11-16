# Scene authoring guide: The Weather Keeper of Block C

**Read first:** `docs/scene_guide.md`, film 1's guide. Its shot, camera, acting, review and sound conventions all apply here. The differences for film 2 follow.

## Basics

- **Location:** scenes go in `src/anim/films/weather_keeper/scenes/scNN.py`, plus `credits.py`. Each module exports `SHOTS`. Helpers go in `_util_X.py` in the same folder.
- **Running anything:** always use `cd /home/user/movies && FILM=weather_keeper .venv/bin/python ...`. Without `FILM`, you get film 1.
- **Review:** `FILM=weather_keeper .venv/bin/python -m anim.render --stills sc03` writes a contact sheet to `films/weather_keeper/edit/stills_review/`.
- **Imports, inside a scene module:**
  ```python
  from ..rig import draw, draw_bhaap, draw_pigeon, ...
  from ..sets import roof, workshop, ...
  from ....timeline import Shot, Line, Sfx
  from .... import core as K, fx
  ```
- **APIs:** read the module docstrings in `films/weather_keeper/rig.py` and `sets/*.py`. They hold every anchor.

## Runtime targets (20:00 total, credits excluded)

| Scene | Beat | Target |
|---|---|---|
| sc01 | Heatwave | 120 s |
| sc02 | The roof | 120 s |
| sc03 | Recruited | 180 s |
| sc04 | Apprenticeship montage | 180 s |
| sc05 | Midpoint | 120 s |
| sc06 | The shortcut | 180 s |
| sc07 | Climax | 180 s |
| sc08 | The first rain | 90 s |
| sc09 | Coda | 30 s |
| credits | Roll plus a short tag | ~45 s + ~10 s |

## Style

- **Flat-graphic look:** strong silhouettes. Lines boil gently, which is automatic.
- **Lighting:** match the set's weather with `K.lit(cv, ...)`. Presets: `heat`, `heat_dusk`, `evening`→`heat_dusk`, `night`, `workshop`, `dust`, `monsoon`, `monsoon_night`, `dawn`.
  - Group the characters under ONE `lit()` per shot.
  - Draw **Bhaap OUTSIDE `lit()`**, so he stays the softest, brightest white in frame. In the dust storm, give him only a slight orange tint.
- **Colour arc:** sc01–sc05 are sun-bleached; the workshop is cool blue-silver; the dust storm is brown-orange monochrome; the monsoon (late sc07–sc09) is saturated greens and slates with wet reflections.
- **Staging limits:** at most 3 humans in frame, plus Bhaap and pigeons. No crowds: neighbours and cricket kids are off-screen voices or tiny distant figures.
- **No text in frame,** except the credits.

## Voices

- **Characters:** `tara`, `ishaan`, `rehan`, `meghnath`, plus `neighbor_m`, `neighbor_f`, `kid1` and `kid2` for off-screen voices.
- **Lines:** use the script's lines exactly.
- **Lip-sync:** `draw(cv, who, ..., mouth=c.mouth(who))`. For Bhaap, set `mouth` only when he's happy; he has no lines.

## Music

Cue ids, from `films/weather_keeper/cues.py`:

`heat_open`, `block_life`, `stairs_khadoos`, `roof_sneak`, `cloud_birth`, `caught`, `recruited`, `workshop_reveal`, `montage_brass`, `smog_sweep`, `hailstorm`, `notebook`, `photo_alone`, `overdue`, `trunk_reveal`, `varsha_memory`, `go_home`, `dadi_night`, `shortcut_sneak`, `aandhi`, `storm_rescue`, `aftermath`, `waiting`, `bhaap_returns`, `three_keys`, `bowl_slowmo`, `monsoon_full`, `first_rain_dance`, `keeper_laughs`, `notebook_passed`, `coda`, `credits`, `postcredits`. `""` means silence.

Some cues give their `music_hits` a specific meaning; see `docs/score_weather_keeper.md`:
- `heat_open` hit 0 is the thermometer ping; hit 1 is the power-cut sag.
- `roof_sneak` hit 0 stops the music dead for the cooker whistle.
- `bowl_slowmo` hit 0 is the key's click.

## SFX

Names from the film's `sfx.py`, plus everything in film 1's list:

`pressure_cooker_whistle`, `steam_hiss`, `cloud_puff`, `bhaap_giggle`, `bhaap_coo`, `bhaap_sneeze_spark`, `bhaap_drizzle`, `spark_tzik`, `ceiling_fans_stop`, `cooler_hum`, `power_cut_groan`, `water_tanker`, `bucket_clang`, `ball_tok`, `door_creak`, `padlock_rattle`, `pigeon_coo`, `pigeon_flap`, `pigeon_flock`, `kite_wind`, `jar_unscrew`, `jar_breeze`, `broom_sweep`, `sack_tie`, `hail_rattle`, `stumps_fall`, `crowd_howl_distant`, `metal_hatch`, `workshop_ambience`, `calendar_flip`, `chains_unwind`, `tin_lid_creak`, `aandhi_roar`, `laundry_flap`, `shutter_rattle`, `chair_cartwheel`, `klang`, `storm_reverse`, `heat_bed`, `night_bed_delhi`, `plane_distant`, `key_skitter`, `wind_gusts(build)`, `slowmo_whoosh`, `key_click`, `key_turn_clack`, `trunk_lid_rise`, `monsoon_roll`, `thunder(dist)`, `first_drop_tin`, `raindrops_tin(density)`, `rain_roar`, `rain_puddles`, `steel_plate_drum(bpm)`, `cheers_distant`, `mud_slide`, `creaky_laugh`, `window_open`, `curtain_flutter`, `school_bell`, `footsteps_slipper`, `chilli_watering`.

Every shot needs an ambience bed with `dur` equal to the shot duration: `heat_bed`, `night_bed_delhi`, `workshop_ambience`, `rain_roar`, and so on.
