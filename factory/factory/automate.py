"""Automatización: vigila la carpeta de audio y re-publica el dashboard."""
from __future__ import annotations

import time

from .config import Config
from . import pipeline, state as state_mod


def _audio_signature(cfg: Config) -> dict[str, float]:
    """Huella de la carpeta de audio (nombre -> mtime) para detectar cambios."""
    sig: dict[str, float] = {}
    if cfg.audio_dir.exists():
        for f in cfg.audio_dir.iterdir():
            if f.is_file() and f.suffix.lower() in cfg.audio_exts:
                sig[f.name] = f.stat().st_mtime
    return sig


def watch(cfg: Config, interval: int = 10) -> None:
    """Bucle: cada `interval` s revisa data/audio/ y, si cambió, reconstruye estado."""
    cfg.ensure_dirs()
    print(f"👀 Vigilando {cfg.audio_dir} cada {interval}s. Ctrl+C para salir.")
    last = None
    try:
        while True:
            sig = _audio_signature(cfg)
            if sig != last:
                st = pipeline.refresh_only(cfg)
                s = state_mod.summarize(st)
                print(f"   ↻ actualizado · audio {s['audio']}/{s['total']} "
                      f"({s['pct_audio']}%) · dashboard: {cfg.dashboard_path}")
                last = sig
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n✋ Vigilancia detenida.")


def schedule_snippet(cfg: Config) -> str:
    """Devuelve un comando de Task Scheduler (Windows) para refrescar cada 15 min."""
    py = "python"
    cmd = f'{py} -m factory refresh'
    return (
        "# Tarea programada de Windows (refresca el dashboard cada 15 min):\n"
        f'schtasks /Create /SC MINUTE /MO 15 /TN "CortexiaPodcastFactory" '
        f'/TR "cmd /c cd /d \\"{cfg.root}\\" && {cmd}" /F\n\n'
        "# Para borrarla:\n"
        'schtasks /Delete /TN "CortexiaPodcastFactory" /F\n'
    )
