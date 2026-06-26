"""Editor de distribución: de cada episodio saca las piezas para repartir.

Trabaja SOLO con lo que está en el episodio (los 8 movimientos del guion); no
inventa. Entrega, en orden:
  1. Notas del episodio (resumen + 4–6 puntos con sello de tiempo).
  2. Tres títulos de clip (tres ángulos distintos, cada uno nombra su momento).
  3. Descripción de YouTube (2 líneas fuertes + qué te llevas + una invitación).

Los sellos de tiempo se calculan con el conteo de palabras de cada movimiento y
la velocidad de habla (config.episode.words_per_minute).
"""
from __future__ import annotations

from .config import Config
from .series import Episode
from .scripts import build_movements
from . import text_utils as T


def _ts(seconds: float) -> str:
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"


def _clip(text: str, n: int) -> str:
    words = T.clean(text).split()
    out = " ".join(words[:n])
    return out + ("…" if len(words) > n else "")


def movement_timings(ep: Episode, cfg: Config) -> dict[str, dict]:
    """Mapa nombre_movimiento -> {start (s), words, text, lead}.

    `text` es todo el movimiento (para el cálculo de tiempo). `lead` es el turno
    de la voz que defiende (Voz A) — el contenido sustancial, no la pregunta de
    enganche — y es lo que se usa para los recortes y los puntos.
    """
    A = cfg.voice_a["name"]
    out: dict[str, dict] = {}
    cum = 0
    for m in build_movements(ep, cfg):
        text = " ".join(t for _, t in m.turns)
        lead = next((t for sp, t in m.turns if sp == A),
                    m.turns[-1][1] if m.turns else "")
        words = T.count_words(text)
        out[m.name] = {"start": cum / cfg.wpm * 60 if cfg.wpm else 0, "words": words,
                       "text": text, "lead": lead}
        cum += words
    return out


def _notes(ep: Episode, tim: dict, A: str, B: str) -> str:
    obj = tim.get("OBJECIÓN", {}).get("lead", "")
    ex = tim.get("EJEMPLO", {}).get("lead", "")

    intro = (
        f"{A} defiende «{ep.title.lower()}» y {B} no se lo traga: pregunta, duda "
        f"y saca la objeción que cualquiera tendría antes de pagar. Es para quien "
        f"está evaluando si esto le sirve y quiere oír la pega difícil, no el "
        f"folleto."
    )

    # Puntos con sello de tiempo, solo de los movimientos que existen.
    candidates = [
        ("GANCHO", "El miedo con el que llega casi todo el mundo."),
        ("PROBLEMA", "Lo que de verdad está en juego si te quedas mirando."),
        ("EJEMPLO", f"El caso que lo aterriza: «{_clip(ex, 8)}»" if ex else None),
        ("OBJECIÓN", f"La pega que frena la compra: «{_clip(obj, 14)}»"),
        ("MÉTODO", "La respuesta, paso a paso y sin humo."),
        ("CIERRE", "Por dónde empezar hoy, sin complicarte."),
    ]
    bullets = []
    for name, desc in candidates:
        if desc and name in tim:
            bullets.append(f"- `{_ts(tim[name]['start'])}` — {desc}")

    return "## 1. Notas del episodio\n\n" + intro + "\n\n" + "\n".join(bullets) + "\n"


def _clip_titles(ep: Episode, tim: dict, B: str) -> str:
    obj = tim.get("OBJECIÓN", {}).get("lead", "")
    ex = tim.get("EJEMPLO", {}).get("lead", "")
    titles = []

    # Ángulo 1 — el momento de la objeción
    titles.append(
        f'"Esto lo arma cualquiera con una IA gratis"… ¿seguro? '
        f"[recorte {_ts(tim.get('OBJECIÓN', {}).get('start', 0))}]"
        if "no es" in obj.lower() or "moda" in obj.lower() or "gratis" in obj.lower()
        else f"La objeción que casi entierra la idea — y la respuesta "
             f"[recorte {_ts(tim.get('OBJECIÓN', {}).get('start', 0))}]"
    )

    # Ángulo 2 — el ejemplo/analogía (si lo hay); si no, el gancho
    if ex:
        titles.append(
            f"{_clip(ex, 7).capitalize()} — y qué tiene que ver contigo "
            f"[recorte {_ts(tim['EJEMPLO']['start'])}]"
        )
    else:
        titles.append(
            f"El miedo a llegar tarde, dicho en voz alta por {B} "
            f"[recorte {_ts(tim.get('GANCHO', {}).get('start', 0))}]"
        )

    # Ángulo 3 — el método
    titles.append(
        f"El paso a paso, sin ser técnico, en {ep.title.lower()} "
        f"[recorte {_ts(tim.get('MÉTODO', {}).get('start', 0))}]"
    )

    body = "\n".join(f"{i+1}. {t}" for i, t in enumerate(titles))
    return "## 2. Tres títulos de clip\n\n" + body + "\n"


def _youtube(ep: Episode, cta_href: str) -> str:
    take = T.clean(ep.takeaway) if ep.takeaway else ""
    # Dos primeras líneas: lo más fuerte (se ve sin "ver más").
    line1 = f"{ep.angle or ep.title}"
    line2 = "Aquí no te vendo humo: ponemos la objeción difícil sobre la mesa y la respondemos."
    summary = (
        "En unos 5 minutos: el problema real, un caso que lo aterriza y el paso a "
        "paso para hacerlo tú. Sales con criterio para decidir, no con una promesa."
    )
    if cta_href:
        cta = f"👉 Da el siguiente paso: {cta_href}"
    else:
        cta = "👉 Tu siguiente paso: elige un tema y arma una sola pieza de prueba esta semana."
    tail = f"\n\n— {take}" if take else ""
    return (
        "## 3. Descripción de YouTube\n\n"
        f"{line1}\n{line2}\n\n{summary}\n\n{cta}{tail}\n"
    )


def render_distribution(ep: Episode, cfg: Config, cta_href: str = "") -> str:
    A, B = cfg.voice_a["name"], cfg.voice_b["name"]
    tim = movement_timings(ep, cfg)
    header = (
        f"# Piezas para repartir — {ep.number}: {ep.title}\n\n"
        f"*Generado del guion del episodio (8 movimientos). Solo material del episodio.*\n\n"
        "---\n\n"
    )
    return (
        header
        + _notes(ep, tim, A, B) + "\n"
        + _clip_titles(ep, tim, B) + "\n"
        + _youtube(ep, cta_href)
    )


def write_distribution(ep: Episode, cfg: Config, cta_href: str = "") -> str:
    cfg.dist_dir.mkdir(parents=True, exist_ok=True)
    out = cfg.dist_dir / f"{ep.stem}.dist.md"
    out.write_text(render_distribution(ep, cfg, cta_href), encoding="utf-8")
    return out.relative_to(cfg.data_dir).as_posix()
