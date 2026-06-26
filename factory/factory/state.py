"""Registro de estado de la serie: guarda data/state.json."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from .config import Config


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load(cfg: Config) -> dict:
    if cfg.state_path.exists():
        return json.loads(cfg.state_path.read_text(encoding="utf-8"))
    return {"episodes": {}}


def save(cfg: Config, state: dict) -> None:
    cfg.data_dir.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = _now()
    cfg.state_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def summarize(state: dict) -> dict:
    eps = state.get("episodes", {})
    total = len(eps)
    scripts = sum(1 for e in eps.values() if e.get("script_done"))
    briefs = sum(1 for e in eps.values() if e.get("brief_done"))
    audio = sum(1 for e in eps.values() if e.get("audio_present"))
    return {
        "total": total,
        "scripts": scripts,
        "briefs": briefs,
        "audio": audio,
        "pct_audio": round(100 * audio / total) if total else 0,
    }
