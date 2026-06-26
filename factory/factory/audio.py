"""Gestiona la carpeta de entrega de audio (flujo manual NotebookLM)."""
from __future__ import annotations

from pathlib import Path

from .config import Config
from .series import Episode


def find_audio(ep: Episode, cfg: Config) -> Path | None:
    """Busca un archivo de audio entregado para el episodio (cualquier extensión)."""
    for ext in cfg.audio_exts:
        candidate = cfg.audio_dir / f"{ep.stem}{ext}"
        if candidate.exists():
            return candidate
    return None


def scan(episodes: list[Episode], cfg: Config) -> dict[str, Path | None]:
    """Mapa slug -> ruta de audio entregado (o None)."""
    return {ep.slug: find_audio(ep, cfg) for ep in episodes}


def orphan_files(episodes: list[Episode], cfg: Config) -> list[str]:
    """Audios sueltos en la carpeta que no corresponden a ningún episodio."""
    if not cfg.audio_dir.exists():
        return []
    expected = {f"{ep.stem}{ext}" for ep in episodes for ext in cfg.audio_exts}
    out = []
    for f in cfg.audio_dir.iterdir():
        if f.is_file() and f.suffix.lower() in cfg.audio_exts and f.name not in expected:
            out.append(f.name)
    return sorted(out)
