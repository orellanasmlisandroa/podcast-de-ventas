"""Orquestador de la fábrica: del plan.yml al dashboard, de punta a punta."""
from __future__ import annotations

from .config import Config
from .plan_loader import Plan
from .series import build_series, Episode
from . import (scripts, notebooklm, audio, state as state_mod, dashboard,
               distribution)


def load_episodes(cfg: Config) -> tuple[Plan, list[Episode]]:
    plan = Plan.load(cfg.plan_path)
    return plan, build_series(plan)


def refresh_state(cfg: Config, plan: Plan, episodes: list[Episode],
                  *, write_scripts=True, write_briefs=True) -> dict:
    """Genera artefactos (según flags), escanea audio y reconstruye el estado."""
    cfg.ensure_dirs()
    st = state_mod.load(cfg)
    st["series_title"] = plan.title
    st["project_name"] = cfg.project_name
    st["cta_href"] = plan.cta_href
    eps_state = st.setdefault("episodes", {})

    for ep in episodes:
        rec = eps_state.setdefault(ep.slug, {})
        rec.update(
            number=ep.number,
            slug=ep.slug,
            title=ep.title,
            angle=ep.angle,
            kind=ep.kind,
        )

        if write_scripts:
            rel, words, minutes = scripts.write_script(ep, cfg)
            rec.update(script_file=rel, words=words,
                       est_minutes=round(minutes, 1), script_done=True)
            # Las piezas de distribución se generan a partir del guion.
            rec.update(dist_file=distribution.write_distribution(ep, cfg, plan.cta_href),
                       dist_done=True)
        else:
            rec.setdefault("script_done", (cfg.scripts_dir / f"{ep.stem}.md").exists())
            rec.setdefault("dist_done", (cfg.dist_dir / f"{ep.stem}.dist.md").exists())

        if write_briefs:
            rec.update(brief_file=notebooklm.write_brief(ep, cfg), brief_done=True)
        else:
            rec.setdefault("brief_done", (cfg.briefs_dir / f"{ep.stem}.brief.md").exists())

        rec["audio_expected"] = notebooklm.expected_audio_names(ep, cfg)
        found = audio.find_audio(ep, cfg)
        rec["audio_present"] = found is not None
        rec["audio_file"] = (f"audio/{found.name}" if found else None)

    st["orphan_audio"] = audio.orphan_files(episodes, cfg)
    state_mod.save(cfg, st)
    return st


def build_all(cfg: Config) -> dict:
    """Pipeline completo: guiones + briefs + estado + dashboard."""
    plan, episodes = load_episodes(cfg)
    st = refresh_state(cfg, plan, episodes, write_scripts=True, write_briefs=True)
    dashboard.write_dashboard(cfg, st)
    return st


def refresh_only(cfg: Config) -> dict:
    """Solo re-escanea audio y re-publica dashboard (no regenera guiones)."""
    plan, episodes = load_episodes(cfg)
    st = refresh_state(cfg, plan, episodes, write_scripts=False, write_briefs=False)
    dashboard.write_dashboard(cfg, st)
    return st
