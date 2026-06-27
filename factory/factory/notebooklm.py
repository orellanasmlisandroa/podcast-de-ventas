"""Genera el brief de producción de audio en NotebookLM para cada episodio.

Flujo de audio MANUAL elegido: la fábrica produce el guion + estas instrucciones;
tú generas el «Audio Overview» en NotebookLM y dejas el archivo en data/audio/
con el nombre indicado. El pipeline lo detecta y actualiza el dashboard.
"""
from __future__ import annotations

from .config import Config
from .series import Episode
from . import sources as sources_mod


def _fuentes_block(ep: Episode, cfg: Config) -> str:
    """Lista de fuentes a cargar en NotebookLM, con las URLs reales del usuario."""
    lines = [f"- [ ] El guion de este episodio: `scripts/{ep.stem}.md`"]
    src = sources_mod.load(cfg)
    if sources_mod.is_configured(src):
        if src.get("niche"):
            lines.append(f"- [ ] *(Nicho: {src['niche']})*")
        for url in src.get("youtube", []):
            lines.append(f"- [ ] YouTube: {url}")
        for url in src.get("website", []):
            lines.append(f"- [ ] Sitio web: {url}")
        for url in src.get("social", []):
            lines.append(f"- [ ] Red social: {url}")
        lines.append("- [ ] (Opcional) El `plan.yml` del proyecto como guía de estructura")
    else:
        lines.append("- [ ] El `plan.yml` del proyecto (conocimiento base de la serie)")
        lines.append("- [ ] Los videos / documentos de los expertos del tema (los que puedas usar)")
        lines.append("\n> Aún no configuraste tus fuentes. Hazlo en la pantalla de inicio de la app "
                     "(nicho + URLs de YouTube, redes y sitio web) y este brief listará tus enlaces.")
    return "\n".join(lines)


def expected_audio_names(ep: Episode, cfg: Config) -> list[str]:
    return [f"{ep.stem}{ext}" for ext in cfg.audio_exts]


def render_brief(ep: Episode, cfg: Config) -> str:
    a, b = cfg.voice_a["name"], cfg.voice_b["name"]
    audio_name = f"{ep.stem}{cfg.audio_exts[0]}"
    kind = "tráiler" if ep.kind == "trailer" else "episodio"
    fuentes = _fuentes_block(ep, cfg)

    # Prompt de personalización que se pega en NotebookLM (campo "Customize").
    # Mismo guion de dirección que usa la fábrica: tensión a dos voces en 8 movimientos.
    custom_prompt = (
        f"Eres el guionista de un episodio de podcast de dos voces, en español "
        f"neutro (tuteo), basado ÚNICAMENTE en las fuentes cargadas. No inventes "
        f"datos que no estén en las fuentes.\n"
        f"Tema del {kind}: «{ep.title}». Ángulo: {ep.angle or ep.title}.\n\n"
        f"PAPELES (no las dejes de acuerdo en todo):\n"
        f"- Voz A ({a}): defiende la solución del negocio; conoce el material a fondo.\n"
        f"- Voz B ({b}): oyente escéptico que evalúa comprar; pregunta, duda, pide "
        f"pruebas, saca la objeción real del comprador. La tensión A↔B es el motor; "
        f"resuélvela al final, no antes.\n\n"
        f"NIVEL: háblale a alguien que está evaluando comprar, no a un experto. Cero "
        f"jerga; si un término es indispensable, explícalo en una frase.\n\n"
        f"ESTRUCTURA EN 8 MOVIMIENTOS (sin saltarte ninguno): 1) Gancho: el dolor o "
        f"pregunta que el oyente ya trae. 2) Problema: qué está en juego si no se "
        f"resuelve. 3) Experto: A explica el cómo desde el material. 4) Ejemplo: un "
        f"caso concreto de las fuentes. 5) Objeción: B lanza la duda más fuerte del "
        f"comprador (UNA sola, bien trabajada). 6) Método: A responde con el paso a "
        f"paso real. 7) Recapitulación: ambas voces resumen qué quedó claro. "
        f"8) Cierre: una sola invitación a dar el siguiente paso, sin sonar a anuncio.\n\n"
        f"LÍMITES: ~5 minutos hablados; el cierre invita, no presiona. "
        f"Idea de cierre: «{ep.takeaway}»."
    )

    return f"""# Brief de producción — {kind.capitalize()} {ep.number}: {ep.title}

> Flujo de audio: **manual con NotebookLM (Audio Overview)**.
> La fábrica ya generó el guion; este brief te dice cómo convertirlo en audio.

## 1. Fuentes para cargar en NotebookLM
Crea un cuaderno nuevo en https://notebooklm.google.com y carga **solo fuentes
reales y permitidas** (ese es el diferencial del proyecto):

{fuentes}

## 2. Prompt de personalización (pégalo en "Customize")
```
{custom_prompt}
```

## 3. Generación
1. Pulsa **Generate** en el panel de Audio Overview.
2. Escucha el resultado; si hace falta, ajusta el prompt y regenera.
3. **Descarga** el audio (botón de los tres puntos → Download).

## 4. Entrega (esto es lo que detecta la fábrica)
Renombra el archivo descargado y déjalo en `data/audio/`:

```
data/audio/{audio_name}
```

Extensiones aceptadas: {", ".join(cfg.audio_exts)}.
En cuanto el archivo aparezca ahí, corre `python -m factory build`
(o deja `python -m factory watch` corriendo) y el dashboard pasará este
episodio a **Audio listo**.

---
*Ángulo:* {ep.angle or '—'}
*Frase de cierre:* {ep.takeaway or '—'}
"""


def write_brief(ep: Episode, cfg: Config) -> str:
    cfg.briefs_dir.mkdir(parents=True, exist_ok=True)
    out = cfg.briefs_dir / f"{ep.stem}.brief.md"
    out.write_text(render_brief(ep, cfg), encoding="utf-8")
    return out.relative_to(cfg.data_dir).as_posix()
