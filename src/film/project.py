"""Locating a film project and loading its config, pricing and secrets."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

STUDIO_ROOT = Path(__file__).resolve().parents[2]
FILMS_DIR = STUDIO_ROOT / "films"
PRICING_FILE = STUDIO_ROOT / "pricing.yaml"


class ProjectError(RuntimeError):
    pass


def list_films() -> list[str]:
    return sorted(p.parent.name for p in FILMS_DIR.glob("*/config.yaml"))


def _load_env(path: Path) -> dict[str, str]:
    """Minimal .env parser. Values are kept in memory only and never printed."""
    env: dict[str, str] = {}
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            v = v.strip().strip('"').strip("'")
            if v:
                env[k.strip()] = v
    # real environment variables win over the file
    for k in list(env) + ["FAL_KEY", "ELEVENLABS_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY"]:
        if os.environ.get(k):
            env[k] = os.environ[k]
    return env


@dataclass
class Project:
    root: Path
    config: dict
    pricing: dict
    env: dict = field(repr=False)

    # ---- paths -------------------------------------------------------
    @property
    def slug(self) -> str:
        return self.config["slug"]

    @property
    def title(self) -> str:
        return self.config["title"]

    def path(self, *parts: str) -> Path:
        return self.root.joinpath(*parts)

    @property
    def logs(self) -> Path:
        return self.root / "logs"

    @property
    def shots_file(self) -> Path:
        return self.root / "shots" / "shots.json"

    # ---- pricing -----------------------------------------------------
    def price(self, ref: str) -> dict:
        """ref like 'video.kling_v3_pro' -> {'unit':..., 'usd':...}"""
        group, name = ref.split(".", 1)
        try:
            return self.pricing[group][name]
        except KeyError as e:
            raise ProjectError(f"pricing.yaml has no entry {ref!r}") from e

    def provider_cfg(self, role: str) -> dict:
        try:
            return self.config["providers"][role]
        except KeyError as e:
            raise ProjectError(f"config.yaml providers has no role {role!r}") from e

    def has_key(self, name: str) -> bool:
        return bool(self.env.get(name))


def load(film: str | None = None) -> Project:
    root: Path | None = None
    if film:
        cand = Path(film)
        root = cand if (cand / "config.yaml").exists() else FILMS_DIR / film
    elif os.environ.get("FILM"):
        root = FILMS_DIR / os.environ["FILM"]
    else:
        cur = Path.cwd().resolve()
        for p in [cur, *cur.parents]:
            if (p / "config.yaml").exists() and (p / "bible").exists():
                root = p
                break
    if root is None or not (root / "config.yaml").exists():
        raise ProjectError(
            "No film selected. Use --film <slug> (one of: " + ", ".join(list_films()) + ") "
            "or run from inside a film directory."
        )
    config = yaml.safe_load((root / "config.yaml").read_text())
    pricing = yaml.safe_load(PRICING_FILE.read_text())
    return Project(root=root.resolve(), config=config, pricing=pricing, env=_load_env(root / ".env"))
