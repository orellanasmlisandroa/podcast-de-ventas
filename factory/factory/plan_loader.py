"""Lee el plan.yml del proyecto y expone sus secciones."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Plan:
    raw: dict
    path: Path

    @classmethod
    def load(cls, path: Path | str) -> "Plan":
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"No se encontró el plan: {path}")
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return cls(raw=data, path=path)

    @property
    def title(self) -> str:
        return self.raw.get("display_title") or self.raw.get("title", "")

    @property
    def promise(self) -> str:
        return self.raw.get("promise", "")

    @property
    def earworm(self) -> str:
        return self.raw.get("earworm", "")

    @property
    def language(self) -> str:
        return self.raw.get("language", "es")

    @property
    def cta_href(self) -> str:
        for s in self.sections:
            if s.get("component") == "cta-closing":
                return s.get("slots", {}).get("cta_href", "")
        return ""

    @property
    def sections(self) -> list[dict]:
        return self.raw.get("sections", [])
