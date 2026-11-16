"""Approval gates. A command whose prerequisite gate is not approved refuses to run.

Approvals are recorded only when the producer gives them (`python -m film gate approve N`).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from .project import Project

GATES = {
    0: "Tooling, stack, estimate, budget, keys",
    1: "Screenplay (story locked)",
    2: "Style bible, character/location sheets, voice auditions",
    3: "Animatic (picture locked)",
    4: "Pilot scene + revised budget",
    5: "Rough cut",
}

# command -> gate that must be approved before it may run
REQUIRES = {
    "script": 0,
    "bible": 1,
    "shots": 2,
    "keyframes": 2,
    "animatic": 2,
    "render": 3,     # pilot scene only until gate 4; full run checks gate 4 itself
    "qc": 3,
    "voice": 2,
    "music": 3,
    "sfx": 3,
    "assemble": 4,
    "export": 5,
}


class GateClosed(RuntimeError):
    pass


def _file(p: Project):
    return p.logs / "gates.json"


def load(p: Project) -> dict:
    f = _file(p)
    data = json.loads(f.read_text()) if f.exists() else {}
    for n in GATES:
        data.setdefault(str(n), {"approved": False})
    return data


def approved(p: Project, n: int) -> bool:
    return bool(load(p)[str(n)].get("approved"))


def require(p: Project, command: str) -> None:
    n = REQUIRES.get(command)
    if n is None:
        return
    missing = [g for g in range(0, n + 1) if not approved(p, g)]
    if missing:
        raise GateClosed(
            f"`{command}` needs GATE {n} ({GATES[n]}) approved; still open: "
            + ", ".join(f"GATE {g}" for g in missing)
        )


def set_gate(p: Project, n: int, ok: bool, notes: str = "") -> None:
    data = load(p)
    data[str(n)] = {
        "approved": ok,
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "notes": notes,
    }
    _file(p).write_text(json.dumps(data, indent=2))
