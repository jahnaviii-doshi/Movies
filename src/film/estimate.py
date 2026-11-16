"""Whole-film cost projection: low / expected / high, plus alternative stacks.

Before shots.json exists the numbers come from config.yaml `plan:`. After Phase 3
the real shot count, durations, dialogue lengths and ON-line count replace them.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

from .project import Project

SCENARIOS = ("low", "expected", "high")
CLIP_HANDLE = 1.15          # generate slightly long so the edit has trim room
SHEETS_PER_CHARACTER = 2    # turnaround (front/3-4/side/back) + expression sheet
ANGLES_PER_LOCATION = 3     # establishing plate + 2 alternates
BIBLE_RETRY = 1.3
VOICE_FINAL_TAKES = 3
AUDITION_CHARS = 300        # per audition clip
AUDITIONS_PER_CHARACTER = 3
LIPSYNC_LINE_S = 3.0


@dataclass
class Line:
    item: str
    units: float
    unit: str
    usd: float


def _plan(p: Project, s: str) -> dict:
    pl = p.config["plan"]
    v = lambda k: pl[k][s] if isinstance(pl[k], dict) else pl[k]  # noqa: E731
    d = {
        "shots": v("shots"),
        "runtime_s": p.config["runtime_target_s"],
        "dialogue_lines": pl["dialogue_lines"],
        "dialogue_chars": pl["dialogue_lines"] * pl["avg_line_chars"],
        "on_fraction": pl["lipsync_on_fraction"],
        "hero": v("hero_shot_fraction"),
        "retake": v("retake_rate"),
        "kf_regen": v("keyframe_regen_rate"),
        "music_min": v("music_minutes_generated"),
        "sfx_min": v("sfx_minutes_generated"),
        "source": "plan (config.yaml)",
    }
    if p.shots_file.exists():  # real shot list overrides the plan
        shots = json.loads(p.shots_file.read_text())
        lines = [ln for sh in shots for ln in sh.get("dialogue", [])]
        d.update(shots=len(shots), runtime_s=sum(sh["duration_s"] for sh in shots),
                 dialogue_lines=len(lines), dialogue_chars=sum(len(ln["line"]) for ln in lines),
                 on_fraction=(sum(ln.get("sync") == "ON" for ln in lines) / len(lines)) if lines else 0,
                 hero=sum(bool(sh.get("hero")) for sh in shots) / max(1, len(shots)),
                 source="shots/shots.json")
    return d


def _usd(p: Project, ref: str, scenario: str) -> float:
    pr = p.price(ref)
    return float(pr.get("high_usd", pr["usd"])) if scenario == "high" else float(pr["usd"])


def project_cost(p: Project, scenario: str, video_ref: str | None = None,
                 hero_ref: str | None = None, image_ref: str | None = None,
                 qc_ref: str | None = None) -> tuple[list[Line], dict]:
    c = p.config
    d = _plan(p, scenario)
    prov = c["providers"]
    video_ref = video_ref or prov["video"]["price"]
    hero_ref = hero_ref or prov["video_hero"]["price"]
    image_ref = image_ref or prov["image"]["price"]
    qc_ref = qc_ref or prov["qc"]["price"]
    lipsync_ref = "lipsync.sync_3" if scenario == "high" else prov["lipsync"]["price"]
    takes = c["takes_per_shot"]
    L: list[Line] = []

    # Phase 2: bible
    n_chars, n_locs, cands = len(c["characters"]), len(c["locations"]), c["bible_candidates"]
    bible_imgs = round((n_chars * SHEETS_PER_CHARACTER + n_locs * ANGLES_PER_LOCATION) * cands * BIBLE_RETRY)
    L.append(Line("Bible: character sheets + location plates", bible_imgs, "image",
                  bible_imgs * _usd(p, image_ref, scenario)))
    aud_k = n_chars * AUDITIONS_PER_CHARACTER * AUDITION_CHARS / 1000
    L.append(Line("Bible: voice auditions (3 per character)", aud_k, "kchar", aud_k * _usd(p, "voice.eleven_v3", scenario)))

    # Phase 4: keyframes + animatic
    kf = round(d["shots"] * c["keyframe_candidates"] * (1 + d["kf_regen"]))
    L.append(Line("Keyframes (2 candidates/shot + animatic regens)", kf, "image", kf * _usd(p, image_ref, scenario)))
    sk = d["dialogue_chars"] / 1000
    L.append(Line("Scratch voices for animatic", sk, "kchar", sk * _usd(p, prov["voice_scratch"]["price"], scenario)))

    # Phases 5-6: video
    gen_s = d["runtime_s"] * CLIP_HANDLE * takes * (1 + d["retake"])
    hero_s, std_s = gen_s * d["hero"], gen_s * (1 - d["hero"])
    L.append(Line(f"Video: {video_ref.split('.')[1]} ({takes} takes, {d['retake']:.0%} retakes)", std_s, "second",
                  std_s * _usd(p, video_ref, scenario)))
    L.append(Line(f"Video: hero shots on {hero_ref.split('.')[1]} (0-30% of shots)", hero_s, "second",
                  hero_s * _usd(p, hero_ref, scenario)))
    ls = d["dialogue_lines"] * d["on_fraction"] * LIPSYNC_LINE_S * takes * (1 + d["retake"])
    L.append(Line(f"Lip-sync ({d['on_fraction']:.0%} ON lines)", ls, "second", ls * _usd(p, lipsync_ref, scenario)))

    # audio
    vk = d["dialogue_chars"] * VOICE_FINAL_TAKES / 1000
    L.append(Line("Final dialogue (3 takes/line)", vk, "kchar", vk * _usd(p, prov["voice"]["price"], scenario)))
    L.append(Line("Music: leitmotifs + scene cues (iterations incl.)", d["music_min"], "minute",
                  d["music_min"] * _usd(p, prov["music"]["price"], scenario)))
    L.append(Line("SFX: ambience beds + spot effects", d["sfx_min"], "minute",
                  d["sfx_min"] * _usd(p, prov["sfx"]["price"], scenario)))

    # QC
    judgments = kf + d["shots"] * takes * (1 + d["retake"])
    L.append(Line(f"QC judging ({qc_ref.split('.')[1]})", judgments, "call", judgments * _usd(p, qc_ref, scenario)))
    return L, d


def total(lines: list[Line]) -> float:
    return sum(l.usd for l in lines)


ALT_STACKS = {
    "budget  (all video on Veo 3.1 Lite, Seedream keyframes)": dict(
        video_ref="video.veo_3_1_lite", hero_ref="video.veo_3_1_lite", image_ref="image.seedream_4_5"),
    "premium (all video on Veo 3.1 standard)": dict(video_ref="video.veo_3_1", hero_ref="video.veo_3_1"),
    "recommended + unattended QC via Claude API": dict(qc_ref="qc.claude_api_judge"),
}


def report(p: Project) -> tuple[str, dict]:
    out = [f"\n=== {p.title} ({p.slug}) — cost projection ==="]
    res = {}
    per = {s: project_cost(p, s) for s in SCENARIOS}
    d0 = per["expected"][1]
    out.append(f"source: {d0['source']} | shots {per['low'][1]['shots']}/{d0['shots']}/{per['high'][1]['shots']} "
               f"| runtime {d0['runtime_s']/60:.1f} min | {p.config['resolution'][0]}x{p.config['resolution'][1]} "
               f"@ {p.config['fps']} fps")
    w = 58
    out.append(f"{'item':<{w}} {'low':>9} {'expected':>9} {'high':>9}")
    out.append("-" * (w + 30))
    for i, ln in enumerate(per["expected"][0]):
        vals = [per[s][0][i].usd for s in SCENARIOS]
        out.append(f"{ln.item[:w]:<{w}} " + " ".join(f"{v:>9,.2f}" for v in vals))
    out.append("-" * (w + 30))
    sub = {s: total(per[s][0]) for s in SCENARIOS}
    cont = p.config.get("contingency_pct", 15) / 100
    out.append(f"{'API subtotal':<{w}} " + " ".join(f"{sub[s]:>9,.2f}" for s in SCENARIOS))
    out.append(f"{f'+ contingency {cont:.0%}':<{w}} " + " ".join(f"{sub[s]*cont:>9,.2f}" for s in SCENARIOS))
    tot = {s: sub[s] * (1 + cont) for s in SCENARIOS}
    out.append(f"{'TOTAL (USD)':<{w}} " + " ".join(f"{tot[s]:>9,.2f}" for s in SCENARIOS))
    out.append(f"per finished minute (expected): ${tot['expected'] / (d0['runtime_s']/60):,.2f}")
    out.append("\nAlternative stacks (expected scenario, incl. contingency):")
    for name, kw in ALT_STACKS.items():
        out.append(f"  {name:<56} ${total(project_cost(p, 'expected', **kw)[0]) * (1 + cont):>9,.2f}")
    out.append("Not included: subscriptions (ElevenLabs plan with commercial licence, $22-99/mo; "
               "Enterprise may be required for music in film — see tooling.md).")
    unverified = sorted({ref for ref in [v['price'] for v in p.config['providers'].values()]
                         if not p.price(ref).get("verified")})
    if unverified:
        out.append("Prices not yet confirmed on vendor pages: " + ", ".join(unverified))
    res = {"low": tot["low"], "expected": tot["expected"], "high": tot["high"]}
    return "\n".join(out), res
