"""Utilidades de texto: limpiar HTML/Markdown y partir en frases."""
from __future__ import annotations

import html
import re

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"[ \t ]+")
_ARROW_RE = re.compile(r"\s*(?:→|->)\s*$")


def strip_html(text: str) -> str:
    """Quita etiquetas HTML y desescapa entidades, dejando texto legible."""
    if not text:
        return ""
    # Los bloques de los-gigantes traen <a ...>...</a> con imagen embebida.
    # Nos quedamos solo con el texto visible.
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)
    text = _WS_RE.sub(" ", text)
    return text.strip()


def strip_markdown(text: str) -> str:
    """Quita marcas de Markdown (negritas, encabezados, viñetas) dejando texto plano."""
    if not text:
        return ""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)   # **negrita**
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)\*", r"\1", text)  # *itálica*
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)  # # encabezados
    text = re.sub(r"^\s*[-*]\s+", "", text, flags=re.MULTILINE)  # viñetas
    return text.strip()


def clean(text: str) -> str:
    """Limpieza completa: HTML + Markdown + espacios."""
    return _WS_RE.sub(" ", strip_markdown(strip_html(text))).strip()


def clean_inline(text: str) -> str:
    """Como clean(), pero colapsa saltos de línea a espacios (para títulos)."""
    return re.sub(r"\s+", " ", clean(text)).strip()


def split_sentences(text: str) -> list[str]:
    """Parte un párrafo en frases razonables."""
    text = clean(text)
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def paragraphs(text: str) -> list[str]:
    """Devuelve los párrafos no vacíos de un bloque (Markdown)."""
    if not text:
        return []
    out = []
    for block in re.split(r"\n\s*\n", text):
        c = clean(block)
        if c:
            out.append(c)
    return out


def count_words(text: str) -> int:
    return len([w for w in re.split(r"\s+", text.strip()) if w])


def extract_analogy(notes: str) -> str:
    """Saca el primer párrafo de analogía de las notas del docente."""
    if not notes:
        return ""
    # Las notas usan '#### Analogía — ...' seguido del párrafo.
    blocks = re.split(r"^####\s+", notes, flags=re.MULTILINE)
    for block in blocks:
        head, _, rest = block.partition("\n")
        if "analog" in head.lower():
            para = paragraphs(rest)
            if para:
                return para[0]
    # Sin analogía explícita: devuelve el primer párrafo "rico" de las notas.
    paras = [p for p in paragraphs(notes) if not p.lower().startswith("cómo")]
    return paras[0] if paras else ""
