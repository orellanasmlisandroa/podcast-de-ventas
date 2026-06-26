"""Renderiza el dashboard HTML de la fábrica (data/dashboard.html).

Auto-contenido (CSS embebido) y con la paleta oscura de CORTEXIA. Muestra cada
episodio con su estado (guion / brief / audio), enlaces a los archivos y el
avance global de la serie.
"""
from __future__ import annotations

import html
from datetime import datetime

from .config import Config
from . import state as state_mod


def _chip(done: bool, label_done: str, label_pending: str) -> str:
    cls = "ok" if done else "pending"
    txt = label_done if done else label_pending
    return f'<span class="chip {cls}">{html.escape(txt)}</span>'


def _episode_card(rec: dict) -> str:
    title = html.escape(rec.get("title", ""))
    number = html.escape(rec.get("number", ""))
    angle = html.escape(rec.get("angle", "") or "")
    kind = "TRÁILER" if rec.get("kind") == "trailer" else "EPISODIO"
    words = rec.get("words", 0)
    mins = rec.get("est_minutes", 0)

    script_file = rec.get("script_file")
    brief_file = rec.get("brief_file")
    dist_file = rec.get("dist_file")
    audio_file = rec.get("audio_file")
    audio_present = rec.get("audio_present")

    links = []
    if script_file:
        links.append(f'<a href="{html.escape(script_file)}" target="_blank">Guion ↗</a>')
    if brief_file:
        links.append(f'<a href="{html.escape(brief_file)}" target="_blank">Brief NotebookLM ↗</a>')
    if dist_file:
        links.append(f'<a href="{html.escape(dist_file)}" target="_blank">Distribución ↗</a>')
    if audio_present and audio_file:
        links.append(f'<a href="{html.escape(audio_file)}" target="_blank">Audio ↗</a>')
    links_html = " · ".join(links)

    expected = ", ".join(rec.get("audio_expected", [])[:1]) or "—"
    audio_hint = (
        f'<div class="hint">Esperando audio en <code>data/audio/{html.escape(expected)}</code></div>'
        if not audio_present else ""
    )

    return f"""
    <article class="ep {'done' if audio_present else 'wip'}">
      <header>
        <span class="num">{number}</span>
        <span class="kind">{kind}</span>
      </header>
      <h3>{title}</h3>
      <p class="angle">{angle}</p>
      <div class="chips">
        {_chip(rec.get('script_done'), 'Guion ✓', 'Guion …')}
        {_chip(rec.get('brief_done'), 'Brief ✓', 'Brief …')}
        {_chip(audio_present, 'Audio listo ✓', 'Audio pendiente')}
      </div>
      <div class="meta">~{mins} min · ~{words} palabras</div>
      <div class="links">{links_html}</div>
      {audio_hint}
    </article>"""


def render(cfg: Config, state: dict) -> str:
    s = state_mod.summarize(state)
    b = cfg.brand
    eps = sorted(state.get("episodes", {}).values(),
                 key=lambda r: r.get("number", "99"))
    cards = "\n".join(_episode_card(r) for r in eps)
    updated = state.get("updated_at", "")
    try:
        updated = datetime.fromisoformat(updated).strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        pass

    orphans = state.get("orphan_audio", [])
    orphan_html = ""
    if orphans:
        items = "".join(f"<li><code>{html.escape(o)}</code></li>" for o in orphans)
        orphan_html = (
            '<div class="warn"><strong>Audios sin episodio asignado:</strong>'
            f'<ul>{items}</ul>'
            "Renómbralos al patrón <code>epNN_slug.ext</code> para que la fábrica los enlace.</div>"
        )

    project = html.escape(state.get("project_name", cfg.project_name))
    if " — " in project:
        head, _, tail = project.partition(" — ")
        title_html = f'{head} — <span class="pop">{tail}</span>'
    else:
        title_html = project
    series_title = html.escape(state.get("series_title", ""))
    cta = state.get("cta_href", "")
    cta_html = (f'<a class="cta" href="{html.escape(cta)}" target="_blank">Abrir el sistema completo ↗</a>'
                if cta else "")

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fábrica de Podcasts · {project}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@600;800&family=DM+Sans:wght@400;500;700&family=DM+Mono&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg:#0d0d0f; --card:#13131a; --border:#1e1e28; --hover:#1a1a24;
    --text:#fff; --muted:#6b6b80; --accent:{b['accent']};
    --g1:{b['grad_1']}; --g2:{b['grad_2']}; --g3:{b['grad_3']};
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:var(--bg); color:var(--text);
    font-family:'DM Sans',system-ui,sans-serif; line-height:1.55; padding:40px 24px 80px; }}
  .wrap {{ max-width:1100px; margin:0 auto; }}
  .eyebrow {{ font-family:'DM Mono',monospace; color:var(--accent);
    letter-spacing:.12em; font-size:12px; text-transform:uppercase; }}
  h1 {{ font-family:'Syne',sans-serif; font-weight:800; font-size:38px;
    line-height:1.1; margin:8px 0 6px; }}
  h1 .pop {{ background:linear-gradient(135deg,var(--g1),var(--g2) 50%,var(--g3));
    -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }}
  .sub {{ color:var(--muted); max-width:680px; }}
  .bar {{ display:flex; gap:16px; flex-wrap:wrap; margin:28px 0; }}
  .kpi {{ background:var(--card); border:1px solid var(--border);
    border-radius:14px; padding:16px 20px; min-width:140px; }}
  .kpi b {{ font-family:'Syne',sans-serif; font-size:28px; display:block; }}
  .kpi span {{ color:var(--muted); font-size:12px; text-transform:uppercase;
    letter-spacing:.08em; }}
  .progress {{ height:10px; background:var(--border); border-radius:100px;
    overflow:hidden; margin:8px 0 28px; }}
  .progress > i {{ display:block; height:100%;
    width:{s['pct_audio']}%; background:linear-gradient(90deg,var(--accent),var(--g3)); }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:16px; }}
  .ep {{ background:var(--card); border:1px solid var(--border); border-radius:16px;
    padding:18px 20px; transition:.2s; }}
  .ep:hover {{ background:var(--hover); border-color:#2a2a38; }}
  .ep.done {{ border-color:rgba(0,232,122,.35); }}
  .ep header {{ display:flex; align-items:center; gap:10px; margin-bottom:6px; }}
  .ep .num {{ font-family:'DM Mono',monospace; color:var(--accent); font-size:13px; }}
  .ep .kind {{ font-size:10px; letter-spacing:.1em; color:var(--muted);
    border:1px solid var(--border); border-radius:100px; padding:2px 8px; }}
  .ep h3 {{ font-family:'Syne',sans-serif; font-size:19px; margin-bottom:4px; }}
  .ep .angle {{ color:var(--muted); font-size:13.5px; margin-bottom:12px; }}
  .chips {{ display:flex; flex-wrap:wrap; gap:6px; margin-bottom:10px; }}
  .chip {{ font-size:11px; padding:4px 9px; border-radius:100px;
    border:1px solid var(--border); }}
  .chip.ok {{ color:#00e87a; border-color:rgba(0,232,122,.4);
    background:rgba(0,232,122,.08); }}
  .chip.pending {{ color:var(--muted); }}
  .meta {{ font-family:'DM Mono',monospace; font-size:12px; color:var(--muted); }}
  .links {{ margin-top:8px; font-size:13px; }}
  .links a {{ color:var(--g2); }}
  .links a:hover {{ text-decoration:underline; }}
  .hint {{ margin-top:8px; font-size:12px; color:var(--muted); }}
  .hint code, .warn code {{ background:#000; padding:1px 6px; border-radius:6px;
    font-family:'DM Mono',monospace; font-size:11.5px; }}
  .warn {{ background:rgba(245,138,46,.08); border:1px solid rgba(245,138,46,.3);
    border-radius:12px; padding:14px 18px; margin:24px 0; font-size:13.5px; }}
  .warn ul {{ margin:8px 0; padding-left:20px; }}
  .foot {{ margin-top:40px; color:var(--muted); font-size:12px;
    display:flex; justify-content:space-between; flex-wrap:wrap; gap:10px; }}
  .cta {{ display:inline-block; margin-top:18px; background:var(--accent);
    color:#000; font-weight:700; padding:10px 20px; border-radius:100px; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="eyebrow">Fábrica de Podcasts de Ventas · CORTEXIA 777</div>
  <h1>{title_html}</h1>
  <p class="sub">{series_title}</p>

  <div class="bar">
    <div class="kpi"><b>{s['total']}</b><span>Episodios</span></div>
    <div class="kpi"><b>{s['scripts']}</b><span>Guiones</span></div>
    <div class="kpi"><b>{s['briefs']}</b><span>Briefs</span></div>
    <div class="kpi"><b>{s['audio']}/{s['total']}</b><span>Audio listo</span></div>
    <div class="kpi"><b>{s['pct_audio']}%</b><span>Serie completa</span></div>
  </div>
  <div class="progress"><i></i></div>

  {orphan_html}

  <div class="grid">
    {cards}
  </div>

  {cta_html}

  <div class="foot">
    <span>Actualizado: {updated}</span>
    <span>Audio: flujo manual NotebookLM (Audio Overview)</span>
  </div>
</div>
</body>
</html>
"""


def write_dashboard(cfg: Config, state: dict) -> str:
    cfg.data_dir.mkdir(parents=True, exist_ok=True)
    cfg.dashboard_path.write_text(render(cfg, state), encoding="utf-8")
    return str(cfg.dashboard_path)
