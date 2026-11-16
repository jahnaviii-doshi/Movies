# Tooling research: AI generation stack (researched 2026-11-16)

Shared by all three films; a copy lives in each film's `bible/tooling.md`.

**How reliable these numbers are:** prices come from vendor pricing pages where I could reach them (Google's Gemini API and Vertex pricing, ElevenLabs' API pricing page) and from reseller and comparison listings everywhere else. Resellers disagree, sometimes by 2×. Rows marked ✅ were confirmed on an official page. Rows marked ⚠️ come from secondary sources and must be confirmed on the vendor page before that phase spends money. `pricing.yaml` carries the same flags, and the estimate prints the unconfirmed ones.

---

## (a) Image generation with reference-image consistency

Used for: character turnarounds, location plates (Phase 2), one keyframe per shot (Phase 4).

| Model | Price | Refs per call | Commercial licence | Notes / restrictions |
|---|---|---|---|---|
| **Gemini 3 Pro Image ("Nano Banana Pro")**, Google | ✅ $0.134/img at 1K–2K, $0.24 at 4K; **Batch API $0.067** | up to 14 | Paid Gemini API tier: output usable commercially; SynthID watermark embedded (invisible) | Strongest multi-reference identity hold in current comparisons. Good at following long structured prompts. No free tier. Safety filters on violence and on realistic minors; stylised child characters are normally fine, but we will confirm this in Phase 2. |
| Seedream 4.5 / 5.0, ByteDance | ⚠️ ~$0.04–0.055/img | up to 10 | Commercial use allowed via API resellers; check reseller terms | Cheap and good. Slightly weaker identity hold on stylised faces. **Budget fallback.** |
| FLUX.2 [pro] / [max], Black Forest Labs | ⚠️ ~$0.04–0.07/img | up to 8–10 | BFL API terms allow commercial output | Excellent painterly textures. Second choice for location plates. |
| GPT Image 2, OpenAI | ⚠️ ~$0.01/img plus input tokens for references | edits | Commercial use allowed | OpenAI's own docs list recurring-character consistency as a limitation, and organisation verification is required. Not recommended as primary. |

**Recommendation:** Nano Banana Pro as primary, with Seedream as a swap-in fallback in `config.yaml`. Bible sheets and keyframe candidates can run through the **Gemini Batch API at half price**. Batch jobs are slower, which is fine because Phases 2 and 4 are not urgent. `generativelanguage.googleapis.com` is already reachable from this environment.

## (b) Image-to-video with first-frame / reference conditioning

Used for: every shot (Phases 5–6), generated **silent**. We do our own sound design, which also halves Veo's price.

| Model | Price (silent, 1080p) | Clip length | Conditioning | Licence / restrictions |
|---|---|---|---|---|
| **Kling 3.0 Pro**, Kuaishou | ⚠️ ~$0.112/s (fal); 4K ~$0.42/s | 3–15 s | start frame + optional end frame; some routes add up to 3 "elements" for identity | Paid output is commercially usable per Kling terms. **Terms differ by access route (direct vs. reseller): confirm for the route we choose.** Strong on stylised 2D/2.5D animation and on expressive faces. |
| **Veo 3.1**, Google | ✅ $0.40/s with audio, ~$0.20/s silent ⚠️; 4K $0.60/s | 4 / 6 / 8 s (extendable) | first + last frame, up to 3 reference images | **Some Veo 3.1 variants are still "Preview" on Vertex, and Google's Pre-GA terms restrict commercial use.** We would use the GA model ID through the Gemini API paid tier and confirm that before Phase 5. Best physics, lighting and camera moves. |
| Veo 3.1 Fast | ✅ $0.10–0.12/s | 4–8 s | same | Good for previz and retakes |
| Veo 3.1 Lite | ✅ $0.05–0.08/s | 4–8 s | same | Cheapest decent option; budget stack only |
| Seedance 2.0 / 2.5, ByteDance | ⚠️ $0.23–0.68/s (quotes vary 3× by reseller) | 5–12 s | first/last frame, multi-ref | Very good motion. Pricing too inconsistent to budget on for now. |
| Runway Gen-4.5 | ⚠️ ~$0.12/s (12 credits/s) | 5–10 s | first frame + references | Commercial use on paid plans |
| Wan 3.0 / Hailuo 3 | ⚠️ $0.04–0.13/s | 5–10 s | first frame (+refs on Hailuo) | Cheaper, lower ceiling |

**Recommendation:** route through **fal.ai**, so one key and one adapter cover every video model and swapping is a config edit:
- **Kling 3.0 Pro** as the workhorse for about 85% of shots: dialogue, character acting, gentle camera moves.
- **Veo 3.1** for about 15% of hero shots: the shop unfolding, the rooftop flight, the monsoon sweep, the luggage-tag train, the Office reveal.
- Every shot is image-to-video from an approved keyframe; text-to-video is never used.
- The Phase 5 pilot measures which model holds *our* characters better, and routing is reset from that result.

## Lip-sync (only for `ON` lines, ≤25%)

| Model | Price | Notes |
|---|---|---|
| **sync lipsync-2 (fal)** | ⚠️ ~$0.05/s | Works on stylised/animated faces. Recommended. |
| sync-3 | ⚠️ ~$0.125/s | Higher quality; used in the "high" scenario |
| Kling lip-sync / PixVerse speech | ⚠️ ~$0.035–0.10/s | Alternatives |

## (c) Expressive multi-voice TTS (English + Hindi)

| Model | Price | Hindi | Licence | Notes |
|---|---|---|---|---|
| **ElevenLabs Eleven v3** | ✅ $0.08 / 1k chars (API) | ✅ in the 70+ language list | Commercial licence on every paid plan (Starter $6/mo and up); none on the free tier | Audio tags for performance (`[whispers]`, `[laughs]`, `[sighs]`), multi-speaker dialogue mode, 5,000 chars per request. A newer v4 exists and will be auditioned at Gate 2. |
| ElevenLabs Flash v2.5 | ✅ $0.04 / 1k chars | ✅ | same | Scratch voices for the animatic |

The whole film's dialogue is roughly 10,000 characters, so voice costs are trivial (<$5 per film). We need one locked voice per character, picked from 3 auditions each at Gate 2. **Children's voices:** use the voice library or Voice Design to make age-appropriate synthetic voices. These are never clones of real people.

## (d) Instrumental music with commercial-use rights

| Model | Price | Licence | Notes |
|---|---|---|---|
| **ElevenLabs Music** | ⚠️ $0.15/min (some pages still say $0.30) | Trained on licensed data; commercial use on paid plans. **One source says film/TV use needs an Enterprise agreement. This must be confirmed with ElevenLabs before Phase 5.** | Section-level "composition plans" let us keep cues musically related |
| Stable Audio 2.5, Stability AI | ⚠️ ~$0.20/generation | Commercial licence on paid plans; Enterprise licence above $1M annual revenue | Audio-to-audio: a motif we write can be re-arranged, which suits leitmotifs |
| Lyria 3.5, Google | ⚠️ $0.04–0.08/song | Preview terms; commercial status unsettled | Not recommended yet |
| Suno v6 / Udio | n/a | Licensing still contested | **Excluded** |

**Recommendation (hybrid, which gives the most musical result and the cleanest rights):**
1. **I write each leitmotif as an original melody** in notation/MIDI. For example, Amma's 6-note lullaby must be *exactly the same tune* every time it is heard. Music models can't reliably repeat a specific melody, so the motifs come from us.
2. The motifs are rendered as a clean melodic layer (MIDI → sampled instruments).
3. **ElevenLabs Music** or **Stable Audio 2.5** (audio-to-audio from the motif) generates the arranged scene cues and beds around them.

That way the score is one coherent piece of music, every melody is provably original, and the generated parts are covered by a commercial licence.

## (e) Sound effects

| Model | Price | Licence |
|---|---|---|
| **ElevenLabs SFX v2** | ⚠️ ~$0.12/min generated | Commercial on paid plans; loopable ambiences up to 30 s |
| Stable Audio 2.5 | ⚠️ per generation | as above |
| Freesound CC0 subset | free | CC0 only (no attribution, commercial OK); good for real ambiences such as crickets, trains and rain on tin |

## QC (automated shot review)

- **Default: in-session review.** I render contact sheets (frames at 0/50/100% next to the reference sheets) and score them here. This costs no API money but needs this session to be running.
- **Optional: unattended judge** via the Claude API (`claude-opus-5-5`, about $0.06 per take). This lets QC run overnight; it adds about $70 per film.

---

## Recommended stack (per film)

| Role | Model | Route |
|---|---|---|
| image | Gemini 3 Pro Image (Nano Banana Pro) | fal, or Gemini API direct with Batch for half price |
| video | Kling 3.0 Pro i2v, silent | fal |
| video_hero | Veo 3.1 i2v, silent | fal (or Gemini API direct) |
| lipsync | sync lipsync-2 | fal |
| voice | ElevenLabs Eleven v3 (v4 auditioned) | ElevenLabs |
| voice_scratch | ElevenLabs Flash v2.5 | ElevenLabs |
| music | authored motifs + ElevenLabs Music / Stable Audio 2.5 | ElevenLabs |
| sfx | ElevenLabs SFX v2 + Freesound CC0 | ElevenLabs |
| qc | in-session (optional Claude API judge) | — |

**Keys needed:** `FAL_KEY`, `ELEVENLABS_API_KEY` (paid plan with commercial licence), and optionally `GEMINI_API_KEY` for the cheaper direct/batch image route.

**Network:** this cloud environment currently blocks `queue.fal.run`, `fal.media` and `api.elevenlabs.io`; Google's API is reachable. Entering the keys through the secure credential form also allows those API hosts. fal's download CDN (`fal.media` / `v3.fal.media`) needs to be allowlisted separately.

## Known risks

1. **Character drift across ~200 shots.** This is the biggest quality risk for any AI film today. Mitigations: canonical text blocks, locked references passed on every call, image-to-video from approved keyframes only, and short 3–8 s shots. The Gate 4 pilot measures how well these work.
2. **"Feature-film" polish.** These models produce beautiful frames and good short motion. They are weaker at sustained character *acting* (subtle performances, hands, multi-character interaction) than hand-keyed feature animation. We design shots to their strengths and keep complex action off-screen or in wide shots.
3. **Licence caveats to clear before Phase 5:** Veo's GA-vs-Preview terms, Kling's terms for the access route we use, and whether ElevenLabs Music needs an Enterprise agreement for film.
4. **Safety filters** may refuse some prompts (child characters in peril, a fall, a collapse). The pipeline logs refusals and moves on. Peril beats are written gently anyway.

## Sources

- Gemini API pricing (Veo 3.1, Gemini 3 Pro Image): https://ai.google.dev/gemini-api/docs/pricing
- Vertex AI pricing: https://cloud.google.com/vertex-ai/generative-ai/pricing
- Veo 3.1 model page (Preview status): https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/veo/3-1-generate
- Google Generative AI Preview terms: https://cloud.google.com/terms/genai-preview-products
- ElevenLabs API pricing: https://elevenlabs.io/pricing/api
- ElevenLabs models (v3 languages, SFX model): https://elevenlabs.io/docs/overview/models
- ElevenLabs Music API: https://elevenlabs.io/eleven-music-api
- AI music licensing comparison: https://invideo.io/blog/ai-music-copyright-comparison/
- Kling 3.0 on fal: https://fal.ai/models/fal-ai/kling-video/v3/standard/image-to-video/llms.txt
- Kling 3.0 Pro (Atlas Cloud): https://www.atlascloud.ai/models/kwaivgi/kling-v3.0-pro/image-to-video
- Kling 3.0 API guide (Krea): https://www.krea.ai/blog/kling-3-0-api-access-guide-pricing-code-examples-for-multi-shot-ai-video
- Kling commercial-use discussion: https://wavespeed.ai/blog/video-model-access/can-i-use-kling-ai-api-for-commercial-projects/
- Video model price comparisons: https://www.teamday.ai/blog/best-ai-video-models-2026 · https://fal.ai/learn/tools/best-image-to-video-apis-2026 · https://openrouter.ai/blog/insights/image-to-video-models-compared/ · https://www.atlascloud.ai/blog/tips/cheapest-ai-video-generation-api-2026
- Image model comparisons: https://openrouter.ai/blog/insights/image-generation-models-compared/ · https://www.recraft.ai/blog/best-ai-image-generation-api · https://higgsfield.ai/blog/tools-for-consistent-ai-characters
- Lip-sync pricing: https://aireiter.com/blog/best-lip-sync-api-2026 · https://www.veed.io/learn/best-lipsync-api
- Music API comparisons: https://www.teamday.ai/blog/best-ai-music-models-2026 · https://musicapi.ai/blog/best-ai-music-api-2026
