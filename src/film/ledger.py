"""Cost ledger (logs/costs.csv) and the hard budget guard."""
from __future__ import annotations

import csv
import threading
from datetime import datetime, timezone

from .project import Project

FIELDS = ["timestamp", "phase", "shot_id", "provider", "model", "units", "est_cost_usd", "note"]
_lock = threading.Lock()


class BudgetExceeded(RuntimeError):
    pass


class BudgetNotSet(RuntimeError):
    pass


def _file(p: Project):
    return p.logs / "costs.csv"


def ensure(p: Project) -> None:
    f = _file(p)
    if not f.exists():
        f.parent.mkdir(parents=True, exist_ok=True)
        with f.open("w", newline="") as fh:
            csv.writer(fh).writerow(FIELDS)


def rows(p: Project) -> list[dict]:
    ensure(p)
    with _file(p).open(newline="") as fh:
        return list(csv.DictReader(fh))


def spent(p: Project, phase: str | None = None) -> float:
    return round(sum(float(r["est_cost_usd"] or 0) for r in rows(p) if phase in (None, r["phase"])), 4)


def log(p: Project, *, phase: str, shot_id: str, provider: str, model: str, units: float,
        cost: float, note: str = "") -> None:
    ensure(p)
    with _lock, _file(p).open("a", newline="") as fh:
        csv.writer(fh).writerow([
            datetime.now(timezone.utc).isoformat(timespec="seconds"), phase, shot_id,
            provider, model, f"{units:g}", f"{cost:.4f}", note,
        ])


class BudgetGuard:
    """Reserve money before a call; release or commit after.

    Reservations make concurrent workers unable to overshoot the cap together.
    """

    def __init__(self, p: Project):
        self.p = p
        self._reserved = 0.0
        self._lock = threading.Lock()

    @property
    def cap(self) -> float | None:
        b = self.p.config.get("budget_usd")
        return float(b) if b is not None else None

    def remaining(self) -> float | None:
        cap = self.cap
        return None if cap is None else round(cap - spent(self.p) - self._reserved, 4)

    def reserve(self, amount: float, what: str) -> None:
        if amount <= 0:
            return
        with self._lock:
            cap = self.cap
            if cap is None:
                raise BudgetNotSet("budget_usd is not set in config.yaml (set at GATE 0); refusing paid call")
            if spent(self.p) + self._reserved + amount > cap + 1e-9:
                raise BudgetExceeded(
                    f"{what}: est ${amount:.2f} would exceed budget "
                    f"(cap ${cap:.2f}, spent ${spent(self.p):.2f}, reserved ${self._reserved:.2f}). Halting."
                )
            self._reserved += amount

    def release(self, amount: float) -> None:
        with self._lock:
            self._reserved = max(0.0, self._reserved - amount)

    def banner(self, phase: str, projected: float) -> str:
        cap, s = self.cap, spent(self.p)
        cap_s = f"${cap:,.2f}" if cap is not None else "NOT SET"
        rem = f"${cap - s:,.2f}" if cap is not None else "n/a"
        flag = ""
        if cap is not None and projected > cap - s:
            flag = "  !! projected spend exceeds remaining budget"
        return (f"[{self.p.slug}] {phase}: projected ${projected:,.2f} | spent ${s:,.2f} | "
                f"budget {cap_s} | remaining {rem}{flag}")
