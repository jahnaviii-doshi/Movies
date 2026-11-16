# Movies: original animated short films

## 🎬 The Midnight Sweet Shop (finished)

A 20-minute animated family film. On sweltering summer nights in an old Indian town, a shy girl finds a sweet shop that appears only at midnight, where the only currency is one true kindness. **Watch it:** download the video from this repo's **Releases** page (720p share copy, or the 1080p master).

- Script: `films/midnight_sweet_shop/script/script.md`
- Poster, thumbnail and stills: `films/midnight_sweet_shop/edit/final/`
- Subtitles: `films/midnight_sweet_shop/edit/final/The_Midnight_Sweet_Shop_en.srt`

Every frame is drawn by code in this repo: vector character rigs (`src/anim/rig`), painted sets (`src/anim/sets`), effects (`src/anim/fx.py`), and one module per scene (`src/anim/scenes`). The score and sound effects are synthesized in NumPy (`src/anim/audio`). Voices come from the open Kokoro-82M TTS model (Apache-2.0), run locally.

### Rebuild the film

```bash
python3 -m venv .venv && .venv/bin/pip install -e . skia-python numpy scipy soundfile kokoro-onnx
mkdir -p models && cd models
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
cd ..
PYTHONPATH=src .venv/bin/python -m anim.render --jobs 4    # picture: ~35 min on 4 cores
PYTHONPATH=src .venv/bin/python -m anim.audio.mix          # dialogue + score + SFX, -16/-23 LUFS
PYTHONPATH=src .venv/bin/python -m anim.assemble           # final mp4s + subtitles
PYTHONPATH=src .venv/bin/python -m anim.render --stills sc05   # contact sheet for reviewing one scene
```

On Linux, skia needs `libegl1` and `libgl1` installed.

## Coming next

*The Weather Keeper of Block C* and *The Lost Property Office*. Their briefs are in `films/*/bible/story.md`.

---

## Original pipeline notes

| Film | Folder |
|---|---|
| The Midnight Sweet Shop | `films/midnight_sweet_shop/` |
| The Weather Keeper of Block C | `films/weather_keeper/` |
| The Lost Property Office | `films/lost_property_office/` |

One shared pipeline (`src/film/`) drives all three films. Each film folder follows the production layout:
`config.yaml`, `.env`, `bible/`, `script/`, `shots/shots.json`, `assets/`, `edit/` and `logs/`.

## Setup

```bash
python3 -m venv .venv && .venv/bin/pip install -e .
```

## Commands

Run `.venv/bin/python -m film <cmd> --film <slug>`, or use `--all` to run against every film.

| Command | What it does | Spends? |
|---|---|---|
| `status` | Shows gates, budget, spend, asset counts and key readiness | no |
| `estimate` | Projects low/expected/high cost and compares alternative stacks | no |
| `doctor` | Checks the toolchain and which keys are present (never prints values) | no |
| `gate show / approve N / reopen N` | Gate records. Approval is the producer's call | no |
| `script` | Phase 1: screenplay | no |
| `bible` | Phase 2: style bible, reference sheets, voice auditions | yes |
| `shots` | Phase 3: shot list + validation | no |
| `keyframes [--scene N]` | Phase 4: keyframe stills | yes |
| `animatic` | Phase 4: animatic cut with scratch voices | yes (scratch TTS) |
| `render [--scene N] [--shot ID]` | Phases 5–6: image-to-video takes | yes |
| `qc` | Scores takes against the reference sheets | no (session) |
| `voice` / `music` / `sfx` | Final audio | yes |
| `assemble` / `export` | Edit, mix, deliverables | no |

Every paid command takes `--dry-run`, which shows what would run and what it would cost, and `--mock`, which makes offline placeholders at zero spend. A command refuses to run until the gate before it is approved.

## Guarantees

- **Budget hard cap.** Before each call, the pipeline reserves that call's estimated cost against `budget_usd`. If the call would exceed the cap, the pipeline halts. If `budget_usd` is unset, no paid call runs at all.
- **Idempotent.** Each asset key is hashed together with its prompt, model, params and the bytes of its reference files. An approved asset is never regenerated. A cached one is reused, so a crash resumes where it stopped.
- **Traceable.** Every output file `X` gets an `X.json` sidecar with the exact prompt, model, seed, references and cost. Every paid call is a row in `logs/costs.csv`.
- **Swappable vendors.** Each role is one line in `config.yaml` (`adapter`, `model`, `price`). Adapters live in `src/film/providers/`.

## Re-rendering one shot

Coming in Phase 5: un-approve the shot's take in `logs/manifest.json` (or pass `--force`), then run `render --shot S03_SH014`.
