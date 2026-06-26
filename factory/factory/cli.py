"""Interfaz de línea de comandos de la Fábrica de Podcasts.

Uso:  python -m factory <comando>

  build       Pipeline completo: guiones + briefs + estado + dashboard
  scripts     Genera solo los guiones
  briefs      Genera solo los briefs de NotebookLM
  distribute  Genera las piezas para repartir (notas, clips, descripción)
  refresh     Re-escanea el audio y re-publica el dashboard (no regenera guiones)
  dashboard   Reconstruye y abre el dashboard
  status      Muestra el estado de la serie en la terminal
  audio       Lista los nombres de audio esperados por episodio
  watch       Vigila data/audio/ y actualiza el dashboard al detectar audio
  schedule    Imprime el comando de Task Scheduler para automatizar el refresco
  init        Crea las carpetas de datos
"""
from __future__ import annotations

import argparse
import sys
import webbrowser

from .config import Config
from . import pipeline, state as state_mod, automate

# La consola de Windows suele venir en cp1252 y no puede imprimir ✓ · ↻, etc.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def _open(path) -> None:
    try:
        webbrowser.open(path.as_uri())
    except Exception:
        print(f"Abre manualmente: {path}")


def _print_status(cfg: Config) -> None:
    st = state_mod.load(cfg)
    eps = sorted(st.get("episodes", {}).values(), key=lambda r: r.get("number", "99"))
    if not eps:
        print("No hay estado todavía. Corre:  python -m factory build")
        return
    s = state_mod.summarize(st)
    print(f"\n  {st.get('project_name','')}")
    print(f"  {'='*60}")
    print(f"  {'EP':<4}{'TÍTULO':<34}{'GUION':<7}{'BRIEF':<7}{'AUDIO'}")
    print(f"  {'-'*60}")
    for r in eps:
        title = (r.get("title", "")[:31] + "…") if len(r.get("title", "")) > 32 else r.get("title", "")
        g = "✓" if r.get("script_done") else "·"
        b = "✓" if r.get("brief_done") else "·"
        a = "✓" if r.get("audio_present") else "pend."
        print(f"  {r.get('number',''):<4}{title:<34}{g:<7}{b:<7}{a}")
    print(f"  {'-'*60}")
    print(f"  Total {s['total']} · guiones {s['scripts']} · briefs {s['briefs']} "
          f"· audio {s['audio']}/{s['total']} ({s['pct_audio']}%)\n")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="factory",
                                     description="Fábrica de Podcasts de Ventas — CORTEXIA 777")
    parser.add_argument("-c", "--config", help="Ruta a config.yaml")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("build", "scripts", "briefs", "distribute", "refresh",
                 "dashboard", "status", "audio", "schedule", "init"):
        sub.add_parser(name)
    w = sub.add_parser("watch")
    w.add_argument("--interval", type=int, default=10, help="Segundos entre revisiones")

    args = parser.parse_args(argv)
    cfg = Config.load(args.config)

    if args.cmd == "init":
        cfg.ensure_dirs()
        print(f"✓ Carpetas listas en {cfg.data_dir}")
        return 0

    if args.cmd == "build":
        st = pipeline.build_all(cfg)
        s = state_mod.summarize(st)
        print(f"✓ Serie construida: {s['total']} episodios · {s['scripts']} guiones "
              f"· {s['briefs']} briefs · audio {s['audio']}/{s['total']}")
        print(f"  Dashboard: {cfg.dashboard_path}")
        return 0

    if args.cmd in ("scripts", "briefs"):
        plan, episodes = pipeline.load_episodes(cfg)
        st = pipeline.refresh_state(
            cfg, plan, episodes,
            write_scripts=(args.cmd == "scripts"),
            write_briefs=(args.cmd == "briefs"),
        )
        from . import dashboard
        dashboard.write_dashboard(cfg, st)
        print(f"✓ {args.cmd} generados para {len(episodes)} episodios.")
        return 0

    if args.cmd == "distribute":
        plan, episodes = pipeline.load_episodes(cfg)
        from . import distribution
        cfg.dist_dir.mkdir(parents=True, exist_ok=True)
        for ep in episodes:
            distribution.write_distribution(ep, cfg, plan.cta_href)
        st = pipeline.refresh_only(cfg)
        print(f"✓ Piezas de distribución generadas para {len(episodes)} episodios.")
        print(f"  Carpeta: {cfg.dist_dir}")
        return 0

    if args.cmd == "refresh":
        st = pipeline.refresh_only(cfg)
        s = state_mod.summarize(st)
        print(f"✓ Refrescado · audio {s['audio']}/{s['total']} ({s['pct_audio']}%)")
        return 0

    if args.cmd == "dashboard":
        st = pipeline.refresh_only(cfg)
        print(f"✓ Dashboard: {cfg.dashboard_path}")
        _open(cfg.dashboard_path)
        return 0

    if args.cmd == "status":
        _print_status(cfg)
        return 0

    if args.cmd == "audio":
        plan, episodes = pipeline.load_episodes(cfg)
        print(f"\n  Deja cada audio en {cfg.audio_dir} con uno de estos nombres:\n")
        for ep in episodes:
            print(f"  {ep.number}  {ep.stem}{cfg.audio_exts[0]}   ({ep.title})")
        print()
        return 0

    if args.cmd == "watch":
        automate.watch(cfg, interval=args.interval)
        return 0

    if args.cmd == "schedule":
        print(automate.schedule_snippet(cfg))
        return 0

    return 1
