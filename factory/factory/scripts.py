"""Genera el guion a dos voces de cada episodio a partir del contenido del plan.

Formato: episodio de podcast con TENSIÓN entre dos voces (sin llamadas a ninguna
IA; todo sale del material del plan.yml).

  - Voz A: defiende la solución del negocio; conoce el material a fondo.
  - Voz B: oyente escéptico que evalúa comprar; pregunta, duda, pide pruebas.

La tensión A↔B es el motor del episodio y se resuelve al final, no antes.
Estructura fija en 8 movimientos: gancho, problema, experto, ejemplo, objeción,
método, recapitulación y cierre. Largo objetivo: ~5 minutos hablados. Una sola
objeción central, bien trabajada. El cierre invita, no presiona.
"""
from __future__ import annotations

from dataclasses import dataclass

from .config import Config
from .series import Episode
from . import text_utils as T


@dataclass
class Movement:
    """Un movimiento del episodio (uno de los 8), con sus turnos de diálogo."""
    n: int
    name: str
    turns: list[tuple[str, str]]   # (hablante, texto)

# Dolores que el oyente-comprador ya trae (movimiento 1 · gancho).
_PAINS = [
    "Tengo ganas de hacer algo con todo esto de la IA, pero no sé por dónde se "
    "empieza ni si de verdad vale la pena.",
    "Veo que todo el mundo habla de esto y me da miedo quedarme afuera… pero "
    "también que sea puro humo.",
    "Quiero vender algo propio en vez de cambiar horas por dinero, pero no tengo "
    "claro el qué ni el cómo.",
    "Tengo la sensación de que voy tarde y de que esto es solo para gente técnica.",
]

# Una sola objeción central por episodio (movimiento 5). La más fuerte que
# tendría alguien antes de pagar.
_OBJECTIONS = [
    "Frena un segundo. Suena bien, pero hoy cualquiera arma algo parecido con una "
    "IA gratis. ¿Por qué pagaría por lo que yo mismo podría improvisar en una tarde?",
    "Te compro la idea, pero ¿no es otra moda más? ¿Cómo sé que esto no se apaga "
    "en seis meses y me quedo con algo que ya no le importa a nadie?",
    "Vale, pero yo no soy técnico ni tengo equipo. ¿Esto no termina siendo "
    "demasiado complicado para alguien como yo?",
    "Ok, pero ¿de verdad hay gente dispuesta a pagar por esto, o voy a terminar "
    "con un producto bonito que nadie compra?",
    "Suena lindo, pero ya me quemé antes con promesas así. ¿Qué hace que esta vez "
    "sea distinto y no otra pérdida de tiempo y de plata?",
]

_ORDINALS = ["Primero", "Segundo", "Tercero", "Cuarto", "Quinto", "Sexto"]


def _line(speaker: str, text: str) -> str:
    return f"**{speaker.upper()}:** {text.strip()}\n"


def _mv(n: int, label: str) -> str:
    return f"**[{n} · {label}]**\n"


def _material(ep: Episode) -> tuple[str, str, list[tuple[str, str]]]:
    """Reparte el contenido del episodio en (explicación experta, ejemplo, pasos).

    Todo sale del material; no se inventan datos.
    """
    beats = [(l, T.clean(t)) for (l, t) in ep.beats if T.clean(t)]
    body_paras = T.paragraphs(ep.body)

    # ── EJEMPLO (mov. 4): preferimos la analogía de las notas del docente ──
    example = ep.analogy
    if not example and beats:
        example = beats[0][1]
        beats = beats[1:]
    if not example and body_paras:
        example = body_paras[-1]
        body_paras = body_paras[:-1]

    # ── EXPERTO (mov. 3) y MÉTODO/pasos (mov. 6) ──────────────────────────
    if beats:
        if body_paras:
            expert = " ".join(body_paras)
            steps = beats
        else:
            expert = beats[0][1]
            steps = beats[1:] or beats
    else:
        sents: list[str] = []
        for p in body_paras:
            sents += T.split_sentences(p)
        if not sents:
            sents = [ep.angle] if ep.angle else [ep.title]
        half = max(1, len(sents) // 2)
        expert = " ".join(sents[:half])
        rest = sents[half:]
        steps = [("", s) for s in rest] if rest else [("", expert)]

    return expert, example, steps[:5]  # tope de 5 para no diluir la objeción


def build_movements(ep: Episode, cfg: Config) -> list[Movement]:
    """Construye los 8 movimientos del episodio (fuente única del guion)."""
    A = cfg.voice_a["name"]
    B = cfg.voice_b["name"]
    pain = _PAINS[ep.index % len(_PAINS)]
    objection = _OBJECTIONS[ep.index % len(_OBJECTIONS)]
    expert, example, steps = _material(ep)
    mvs: list[Movement] = []

    # 1 · GANCHO — la voz escéptica trae el dolor del oyente
    mvs.append(Movement(1, "GANCHO", [
        (B, f"Déjame empezar por donde estoy yo. {pain} Y cuando escucho "
            f"«{ep.title.lower()}», mi primera reacción es: ¿esto de verdad es "
            f"para alguien como yo?"),
    ]))

    # 2 · PROBLEMA — la voz A nombra lo que está en juego
    stake = (
        "Esa duda es exactamente el problema, y te entiendo. Pero ojo con lo que "
        "está en juego mientras la piensas: "
        + (ep.angle or "lo fácil de copiar no se paga; lo único, sí.")
        + " Quedarte quieto no es neutral: es dejar que otro ocupe el lugar."
    )
    mvs.append(Movement(2, "PROBLEMA", [(A, stake)]))

    # 3 · EXPERTO — la voz A explica el cómo desde el material
    mvs.append(Movement(3, "EXPERTO", [
        (B, "A ver, explícamelo claro, como si fuera la primera vez."),
        (A, expert),
    ]))

    # 4 · EJEMPLO — un caso concreto que aterriza el cómo
    if example:
        mvs.append(Movement(4, "EJEMPLO", [
            (B, "Dame un caso concreto, que lo abstracto no me sirve."),
            (A, example),
        ]))

    # 5 · OBJECIÓN — la duda más fuerte del comprador (una sola)
    mvs.append(Movement(5, "OBJECIÓN", [(B, objection)]))

    # 6 · MÉTODO — la voz A responde con el paso a paso real
    step_parts = []
    for i, (label, text) in enumerate(steps):
        o = _ORDINALS[i] if i < len(_ORDINALS) else f"Paso {i + 1}"
        if label:
            step_parts.append(f"{o}, {label}: {text}")
        else:
            soft = text[:1].lower() + text[1:] if text else text
            step_parts.append(f"{o}, {soft}")
    method = ("Es la duda justa, y te la respondo con el paso a paso, no con humo. "
              + "  ".join(step_parts))
    mvs.append(Movement(6, "MÉTODO", [(A, method)]))

    # 7 · RECAPITULACIÓN — las dos voces resumen qué quedó claro
    mvs.append(Movement(7, "RECAPITULACIÓN", [
        (B, "Vale. Lo que me queda claro es que esto no es apretar un botón "
            "mágico, sino seguir un método con material real. Bajó bastante mi "
            "sospecha."),
        (A, "Eso es justo. No te pido fe: te muestro el cómo. "
            + (T.clean(ep.takeaway) if ep.takeaway else "")),
    ]))

    # 8 · CIERRE — una sola invitación, sin presión
    mvs.append(Movement(8, "CIERRE", [
        (B, "¿Y por dónde empezarías tú, sin complicarte?"),
        (A, "Por algo chico, hoy mismo: elige un tema y arma una sola pieza de "
            "prueba con tus propias manos. No hace falta que decidas nada más "
            "ahora; solo mira cómo se siente hacerlo una vez. Si te resuena, el "
            "resto viene solo."),
    ]))
    return mvs


def build_dialogue(ep: Episode, cfg: Config) -> list[str]:
    """Aplana los movimientos al markdown del guion (encabezado + turnos)."""
    lines: list[str] = []
    for m in build_movements(ep, cfg):
        lines.append(_mv(m.n, m.name))
        for speaker, text in m.turns:
            lines.append(_line(speaker, text))
    return lines


def render_script(ep: Episode, cfg: Config) -> tuple[str, int, float]:
    """Devuelve (markdown, palabras, minutos_estimados)."""
    A, B = cfg.voice_a["name"], cfg.voice_b["name"]
    dialogue = build_dialogue(ep, cfg)
    spoken = " ".join(
        T.strip_markdown(ln) for ln in dialogue if not ln.strip().startswith("**[")
    )
    words = T.count_words(spoken)
    minutes = words / cfg.wpm if cfg.wpm else 0.0
    kind = "Tráiler de la serie" if ep.kind == "trailer" else "Episodio"

    header = (
        f"# {kind} {ep.number} — {ep.title}\n\n"
        f"*Serie: {cfg.project_name}*  \n"
        f"*Ángulo: {ep.angle or '—'}*  \n"
        f"*Voz A — {A} ({cfg.voice_a['role']}) · Voz B — {B} ({cfg.voice_b['role']})*  \n"
        f"*Estructura: 8 movimientos · objetivo ~5 min · ~{words} palabras*  \n"
        f"*Idioma: {cfg.raw['language']}*\n\n"
        "---\n"
    )
    md = header + "\n" + "\n".join(dialogue) + "\n"
    return md, words, minutes


def write_script(ep: Episode, cfg: Config) -> tuple[str, int, float]:
    cfg.scripts_dir.mkdir(parents=True, exist_ok=True)
    md, words, minutes = render_script(ep, cfg)
    out = cfg.scripts_dir / f"{ep.stem}.md"
    out.write_text(md, encoding="utf-8")
    return out.relative_to(cfg.data_dir).as_posix(), words, minutes
