"""Fuentes del podcast: nicho + URLs (YouTube, redes, sitio web).

Se guardan en `sources.yaml`. Estas fuentes se inyectan en los briefs de
NotebookLM (sección «Fuentes para cargar»), que es quien lee los videos/sitios y
genera el audio — la app no descarga nada por su cuenta.
"""
from __future__ import annotations

import yaml

from .config import Config

DEFAULTS = {
    "niche": "",
    "description": "",
    "youtube": [],
    "social": [],
    "website": [],
}
_LIST_KEYS = ("youtube", "social", "website")


def _as_list(v) -> list[str]:
    if not v:
        return []
    if isinstance(v, str):
        v = v.splitlines()
    return [str(x).strip() for x in v if str(x).strip()]


def _normalize(data: dict) -> dict:
    out = dict(DEFAULTS)
    for k in DEFAULTS:
        if k in data and data[k] is not None:
            out[k] = data[k]
    out["niche"] = str(out["niche"]).strip()
    out["description"] = str(out["description"]).strip()
    for k in _LIST_KEYS:
        out[k] = _as_list(out[k])
    return out


def load(cfg: Config) -> dict:
    p = cfg.sources_path
    data = {}
    if p.exists():
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return _normalize(data)


def save(cfg: Config, data: dict) -> dict:
    out = _normalize(data or {})
    cfg.sources_path.write_text(
        yaml.safe_dump(out, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    return out


def is_configured(data: dict) -> bool:
    return bool(data.get("niche") or data.get("youtube")
                or data.get("social") or data.get("website"))


def all_urls(data: dict) -> list[str]:
    urls = []
    for k in _LIST_KEYS:
        urls += data.get(k, [])
    return urls
