"""Convierte las secciones del plan.yml en una serie de episodios de podcast.

Cada sección con contenido sustancial se vuelve un episodio (un ángulo de la
serie), tal como describe el propio plan: «una serie de podcasts por distintos
ángulos». El hero se convierte en el tráiler (episodio 00).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .plan_loader import Plan
from . import text_utils as T

# Componentes que se convierten en episodio y cómo.
EPISODE_COMPONENTS = {
    "hero-gradient",
    "section-narrative",
    "section-cards",
    "stat-row",
    "section-compare",
    "points-list",
}


@dataclass
class Episode:
    index: int
    number: str          # "00", "01", ...
    slug: str
    kind: str            # "trailer" | "episode"
    component: str
    title: str
    angle: str           # subtítulo / promesa del episodio
    body: str            # narración base (puede ser "")
    beats: list[tuple[str, str]]  # (etiqueta, texto) — los puntos del episodio
    analogy: str
    takeaway: str

    @property
    def stem(self) -> str:
        return f"ep{self.number}_{self.slug}"

    @property
    def label(self) -> str:
        return f"{self.number} · {self.title}"


def _beats_from_section(comp: str, slots: dict) -> tuple[str, list[tuple[str, str]]]:
    """Devuelve (body, beats) según el tipo de componente."""
    body = ""
    beats: list[tuple[str, str]] = []

    if comp == "hero-gradient":
        body = T.clean(slots.get("tagline", ""))
        for pill in slots.get("stat_pills", []):
            beats.append(("Dato", T.clean(pill)))

    elif comp == "section-narrative":
        body = "\n\n".join(T.paragraphs(slots.get("body_md", "")))

    elif comp == "section-cards":
        for c in slots.get("cards", []):
            label = T.clean_inline(c.get("title", "")) or T.clean_inline(str(c.get("num", "")))
            beats.append((label, T.clean(c.get("body", ""))))

    elif comp == "stat-row":
        for s in slots.get("stats", []):
            beats.append((T.clean_inline(s.get("num", "")), T.clean(s.get("label", ""))))

    elif comp == "section-compare":
        left, right = slots.get("left", {}), slots.get("right", {})
        left_body = " ".join(T.paragraphs(left.get("body_md", "")))
        right_body = " ".join(T.paragraphs(right.get("body_md", "")))
        beats.append((f"{T.clean_inline(left.get('tag',''))}: {T.clean_inline(left.get('title',''))}", left_body))
        beats.append((f"{T.clean_inline(right.get('tag',''))}: {T.clean_inline(right.get('title',''))}", right_body))

    elif comp == "points-list":
        for p in slots.get("points", []):
            beats.append((T.clean_inline(str(p.get("num", ""))), "\n\n".join(T.paragraphs(p.get("body_md", "")))))

    return body, beats


def build_series(plan: Plan) -> list[Episode]:
    episodes: list[Episode] = []
    idx = 0
    for sec in plan.sections:
        comp = sec.get("component", "")
        if comp not in EPISODE_COMPONENTS:
            continue
        slots = sec.get("slots", {}) or {}
        slug = sec.get("id", f"sec-{idx}")

        title = T.clean_inline(slots.get("title", "")) or slug.replace("-", " ").title()
        angle = T.clean(slots.get("subtitle", "") or slots.get("super", "") or slots.get("tagline", ""))
        body, beats = _beats_from_section(comp, slots)
        analogy = T.extract_analogy(sec.get("notes", "") or "")
        takeaway = plan.earworm

        kind = "trailer" if comp == "hero-gradient" else "episode"
        number = f"{idx:02d}"

        episodes.append(
            Episode(
                index=idx,
                number=number,
                slug=slug,
                kind=kind,
                component=comp,
                title=title,
                angle=angle,
                body=body,
                beats=beats,
                analogy=analogy,
                takeaway=takeaway,
            )
        )
        idx += 1
    return episodes
