"""Carga y resuelve la configuración de la fábrica (config.yaml)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

# .../factory  (la carpeta que contiene config.yaml, data/ y el paquete factory/)
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = ROOT / "config.yaml"

_DEFAULTS = {
    "project_name": "Podcast de ventas — CORTEXIA 777",
    "plan_path": "../plan.yml",
    "language": "es-neutro-tuteo",
    "hosts": {
        "voice_a": {"name": "Ana", "role": "conductora curiosa"},
        "voice_b": {"name": "Beto", "role": "coach experto"},
    },
    "episode": {"words_per_minute": 150},
    "output": {"data_dir": "data"},
    "brand": {
        "accent": "#f58a2e",
        "grad_1": "#7c5cbf",
        "grad_2": "#4a9eff",
        "grad_3": "#00e87a",
    },
    "audio": {"extensions": [".mp3", ".wav", ".m4a", ".ogg"]},
}


def _merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


@dataclass
class Config:
    raw: dict
    root: Path

    @classmethod
    def load(cls, path: Path | str | None = None) -> "Config":
        path = Path(path) if path else DEFAULT_CONFIG_PATH
        data = {}
        if path.exists():
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return cls(raw=_merge(_DEFAULTS, data), root=ROOT)

    # ── rutas ────────────────────────────────────────────────────────────
    @property
    def plan_path(self) -> Path:
        return (self.root / self.raw["plan_path"]).resolve()

    @property
    def data_dir(self) -> Path:
        return (self.root / self.raw["output"]["data_dir"]).resolve()

    @property
    def scripts_dir(self) -> Path:
        return self.data_dir / "scripts"

    @property
    def briefs_dir(self) -> Path:
        return self.data_dir / "briefs"

    @property
    def audio_dir(self) -> Path:
        return self.data_dir / "audio"

    @property
    def dist_dir(self) -> Path:
        return self.data_dir / "distribution"

    @property
    def state_path(self) -> Path:
        return self.data_dir / "state.json"

    @property
    def sources_path(self) -> Path:
        return self.root / "sources.yaml"

    @property
    def dashboard_path(self) -> Path:
        return self.data_dir / "dashboard.html"

    def ensure_dirs(self) -> None:
        for d in (self.data_dir, self.scripts_dir, self.briefs_dir,
                  self.audio_dir, self.dist_dir):
            d.mkdir(parents=True, exist_ok=True)

    # ── accesos cómodos ──────────────────────────────────────────────────
    @property
    def project_name(self) -> str:
        return self.raw["project_name"]

    @property
    def voice_a(self) -> dict:
        return self.raw["hosts"]["voice_a"]

    @property
    def voice_b(self) -> dict:
        return self.raw["hosts"]["voice_b"]

    @property
    def wpm(self) -> int:
        return int(self.raw["episode"]["words_per_minute"])

    @property
    def audio_exts(self) -> list[str]:
        return [e.lower() for e in self.raw["audio"]["extensions"]]

    @property
    def brand(self) -> dict:
        return self.raw["brand"]
