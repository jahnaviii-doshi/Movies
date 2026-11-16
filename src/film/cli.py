"""python -m film <command> [--film SLUG | --all]"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys

from . import estimate as est
from . import gates, ledger
from .manifest import Manifest
from .project import ProjectError, list_films, load
from .providers import get as get_provider

# command -> phase in which its implementation lands (built just-in-time, after the previous gate)
PHASE_OF = {"script": 1, "bible": 2, "shots": 3, "keyframes": 4, "animatic": 4, "render": 5,
            "qc": 6, "voice": 4, "music": 5, "sfx": 5, "assemble": 7, "export": 7}
PAID = {"bible", "keyframes", "render", "voice", "music", "sfx", "animatic"}


def _films(args) -> list:
    if getattr(args, "all", False):
        return [load(f) for f in list_films()]
    return [load(args.film)]


# ---------------------------------------------------------------- commands
def cmd_status(args):
    for p in _films(args):
        g = gates.load(p)
        guard = ledger.BudgetGuard(p)
        cap = guard.cap
        print(f"\n=== {p.title} ({p.slug}) ===")
        print("gates:   " + "  ".join(f"G{n}:{'✔' if g[str(n)]['approved'] else '·'}" for n in gates.GATES))
        nxt = next((n for n in gates.GATES if not g[str(n)]["approved"]), None)
        if nxt is not None:
            print(f"next:    GATE {nxt} — {gates.GATES[nxt]}")
        print(f"budget:  {'$%.2f' % cap if cap is not None else 'NOT SET'} | spent ${ledger.spent(p):.2f}")
        shots = json.loads(p.shots_file.read_text()) if p.shots_file.exists() else []
        print(f"script:  {'yes' if p.path('script', 'script.md').exists() else 'not written'} | "
              f"shots: {len(shots) or 'none'}")
        counts = Manifest(p).counts()
        print("assets:  " + (", ".join(f"{k} {v}" for k, v in counts.items()) or "none"))
        ready = []
        for role in p.config["providers"]:
            try:
                ok, why = get_provider(p, role).ready()
            except Exception as e:  # noqa: BLE001
                ok, why = False, str(e)
            ready.append(f"{role}:{'ok' if ok else why}")
        print("keys:    " + " | ".join(ready))


def cmd_estimate(args):
    grand = {s: 0.0 for s in est.SCENARIOS}
    for p in _films(args):
        text, tot = est.report(p)
        print(text)
        for s in est.SCENARIOS:
            grand[s] += tot[s]
        out = p.logs / "estimate.json"
        out.write_text(json.dumps({k: round(v, 2) for k, v in tot.items()}, indent=2))
    if getattr(args, "all", False):
        print("\n=== ALL THREE FILMS ===")
        print("  ".join(f"{s}: ${grand[s]:,.2f}" for s in est.SCENARIOS))


def cmd_doctor(args):
    print(f"python   {sys.version.split()[0]}  {'ok' if sys.version_info >= (3, 11) else 'NEED 3.11+'}")
    ff = shutil.which("ffmpeg")
    conf = subprocess.run([ff, "-hide_banner", "-buildconf"], capture_output=True, text=True).stdout if ff else ""
    for lib in ("libx264", "libass", "libfreetype"):
        print(f"ffmpeg   {lib:<12} {'ok' if f'enable-{lib}' in conf else 'MISSING'}")
    print(f"git      {'ok' if shutil.which('git') else 'MISSING'}")
    for p in _films(args):
        print(f"\n[{p.slug}] keys present: " + ", ".join(
            f"{k}={'yes' if p.has_key(k) else 'no'}"
            for k in ("FAL_KEY", "ELEVENLABS_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY")))


def cmd_gate(args):
    for p in _films(args):
        if args.action == "show":
            g = gates.load(p)
            for n, name in gates.GATES.items():
                rec = g[str(n)]
                print(f"[{p.slug}] GATE {n} {'APPROVED' if rec['approved'] else 'open':<9} {name}"
                      + (f"  ({rec.get('at')}: {rec.get('notes')})" if rec.get("at") else ""))
        else:
            gates.set_gate(p, args.n, args.action == "approve", args.notes or "")
            print(f"[{p.slug}] GATE {args.n} {'approved' if args.action == 'approve' else 're-opened'}")


def cmd_phase(args):
    """Commands for later phases: gate-checked; implementation is written at the start of its phase."""
    for p in _films(args):
        try:
            gates.require(p, args.cmd)
        except gates.GateClosed as e:
            print(f"[{p.slug}] blocked: {e}")
            continue
        print(f"[{p.slug}] `{args.cmd}` is implemented at the start of Phase {PHASE_OF[args.cmd]}.")


# ---------------------------------------------------------------- parser
def build() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="python -m film", description="Manifest-driven animated film pipeline")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, fn, help_):
        sp = sub.add_parser(name, help=help_)
        g = sp.add_mutually_exclusive_group()
        g.add_argument("--film", help="film slug: " + ", ".join(list_films()))
        g.add_argument("--all", action="store_true", help="run for every film")
        sp.set_defaults(fn=fn)
        if name in PAID:
            sp.add_argument("--dry-run", action="store_true", help="show what would be generated and its cost")
            sp.add_argument("--mock", action="store_true", help="offline placeholders, zero spend")
        return sp

    add("status", cmd_status, "gates, budget, spend, assets, key readiness")
    add("estimate", cmd_estimate, "projected cost: low / expected / high")
    add("doctor", cmd_doctor, "check tools and which API keys are present (never prints values)")
    sp = add("gate", cmd_gate, "show / approve / reopen a gate (approval is the producer's call)")
    sp.add_argument("action", choices=["show", "approve", "reopen"])
    sp.add_argument("n", type=int, nargs="?", default=0)
    sp.add_argument("--notes")
    for name in ("script", "bible", "shots", "animatic", "qc", "voice", "music", "sfx", "assemble", "export"):
        add(name, cmd_phase, f"Phase {PHASE_OF[name]}")
    for name in ("keyframes", "render"):
        sp = add(name, cmd_phase, f"Phase {PHASE_OF[name]}")
        sp.add_argument("--scene", type=int)
        if name == "render":
            sp.add_argument("--shot")
    return ap


def main(argv=None):
    args = build().parse_args(argv)
    try:
        args.fn(args)
    except ProjectError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except (ledger.BudgetExceeded, ledger.BudgetNotSet) as e:
        print(f"HALT: {e}", file=sys.stderr)
        return 3
    return 0
