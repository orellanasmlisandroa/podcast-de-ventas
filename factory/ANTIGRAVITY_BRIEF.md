# Brief para Antigravity — convertir la Fábrica de Podcasts en una app

> Pega este archivo (o ábrelo en el editor) y dale al agente de Antigravity el
> prompt de arranque que está al final. Este documento es la especificación:
> el agente debe **reutilizar** el código Python existente, no reescribirlo.

---

## 1. Qué ya existe (NO reescribir)

Una fábrica en Python, dentro de la carpeta `factory/`, que ya funciona por
línea de comandos. Toda la lógica está aquí y debe quedar intacta:

```
factory/
├─ config.yaml            # configuración (voces, paleta, rutas)
├─ requirements.txt       # solo PyYAML
├─ factory/               # paquete Python (LA LÓGICA — reutilizar tal cual)
│  ├─ cli.py              # comandos: build, scripts, briefs, distribute, refresh, status, watch
│  ├─ pipeline.py         # build_all(cfg), refresh_only(cfg), load_episodes(cfg)
│  ├─ config.py           # Config.load() y todas las rutas (data_dir, scripts_dir, …)
│  ├─ plan_loader.py      # lee ../plan.yml (la fuente de conocimiento)
│  ├─ series.py           # secciones del plan -> episodios (Episode)
│  ├─ scripts.py          # episodios -> guiones a 2 voces (8 movimientos)
│  ├─ notebooklm.py       # episodios -> briefs de audio (NotebookLM)
│  ├─ distribution.py     # episodios -> notas, clips y descripción de YouTube
│  ├─ audio.py            # detección de audios entregados
│  ├─ state.py            # registro data/state.json (+ summarize)
│  ├─ dashboard.py        # render del dashboard HTML
│  └─ automate.py         # watch de la carpeta de audio
└─ data/                  # salida: scripts/ briefs/ distribution/ audio/ state.json dashboard.html
```

Funciones clave que la app debe envolver (ya existen, firma estable):

- `Config.load()` → objeto con rutas y ajustes.
- `pipeline.build_all(cfg)` → genera guiones + briefs + distribución + estado + dashboard; devuelve `state` (dict).
- `pipeline.refresh_only(cfg)` → re-escanea `data/audio/` y republica; devuelve `state`.
- `pipeline.load_episodes(cfg)` → `(plan, [Episode])`.
- `state.load(cfg)` / `state.summarize(state)` → estado y KPIs (total, scripts, briefs, audio, pct_audio).
- `scripts.render_script(ep, cfg)`, `distribution.render_distribution(ep, cfg, cta)`, `notebooklm.render_brief(ep, cfg)` → markdown de cada pieza.

El flujo de audio es **manual con NotebookLM** (no hay TTS por API): el usuario
sube el archivo de audio y la app lo detecta. Mantener ese flujo.

---

## 2. Objetivo: una app web local

Convertir la CLI en una **app web** que cualquiera pueda usar sin terminal.
Stack recomendado (elige esto salvo que haya una razón fuerte para otra cosa):

- **Backend:** FastAPI + Uvicorn, importando el paquete `factory` existente.
  No dupliques la generación: cada endpoint llama a las funciones de arriba.
- **Frontend:** una SPA sencilla (puede ser HTML + JS vanilla, o React si lo
  prefieres) servida por el mismo backend. Estética oscura de CORTEXIA
  (ver paleta abajo). UI en **español**.
- **Empaquetado:** un único comando para arrancar (`uvicorn app:api --reload`)
  y, opcionalmente, un script `start.ps1` / `start.sh`. Mantener Windows como
  objetivo principal (el usuario está en Windows 11).

> Si el usuario luego quiere app de escritorio, envolver la web con Tauri o
> PyWebview — dejarlo anotado, no implementarlo todavía.

---

## 3. Pantallas y funciones

1. **Panel (home)** — el dashboard de la serie con KPIs y barra de avance
   (reutiliza `state.summarize`). Botón **«Construir todo»** que llama a
   `build_all` y refresca la vista.
2. **Lista de episodios** — tarjetas con número, título, ángulo y estado
   (guion ✓ / brief ✓ / distribución ✓ / audio pendiente|listo).
3. **Detalle de episodio** — pestañas para ver el **guion**, el **brief de
   NotebookLM** (con botón «copiar prompt»), y las **piezas de distribución**
   (notas, 3 títulos de clip, descripción de YouTube, cada uno con botón copiar).
4. **Subir audio** — en el detalle, un input para subir el archivo del Audio
   Overview; se guarda en `data/audio/` con el nombre exacto del episodio
   (`epNN_slug.ext`) y se llama a `refresh_only`. La tarjeta pasa a «Audio listo».
5. **Configuración** — formulario para editar `config.yaml` (nombres de las dos
   voces y sus papeles, palabras por minuto, paleta, `plan_path`). Guardar
   reescribe `config.yaml`.
6. (Opcional) **Cambiar de tema/nicho** — permitir apuntar `plan_path` a otro
   `plan.yml` para reusar la fábrica en otro nicho.

---

## 4. API sugerida (mapea 1:1 a las funciones existentes)

```
GET    /api/state                 -> state.load + summarize
POST   /api/build                 -> pipeline.build_all  (genera todo)
POST   /api/refresh               -> pipeline.refresh_only (re-escanea audio)
GET    /api/episodes              -> lista de episodios con estado
GET    /api/episodes/{slug}       -> metadatos + rutas de sus archivos
GET    /api/episodes/{slug}/script        -> markdown del guion
GET    /api/episodes/{slug}/brief         -> markdown del brief
GET    /api/episodes/{slug}/distribution  -> markdown de distribución
POST   /api/episodes/{slug}/audio         -> subir archivo a data/audio/ + refresh
GET    /api/config                -> config.yaml actual
PUT    /api/config                -> guardar config.yaml
```

Servir los markdown ya renderizados (no reimplementar la generación). Para
mostrar markdown en el frontend, renderizarlo a HTML en el cliente.

---

## 5. No-negociables (criterios de aceptación)

- [ ] La app **importa y reutiliza** el paquete `factory/` — cero lógica de
      generación duplicada. Si algo falta, se añade *dentro* del paquete.
- [ ] «Construir todo» genera los 12 episodios con guiones, briefs y piezas de
      distribución, y el panel muestra los KPIs correctos.
- [ ] Subir un audio para un episodio lo marca como «Audio listo» sin recargar
      a mano (llamar a `refresh_only`).
- [ ] El flujo de audio sigue siendo **manual con NotebookLM** (sin TTS).
- [ ] UI en español, paleta CORTEXIA, sin jerga corporativa.
- [ ] Un solo comando arranca la app en Windows; README con los pasos.
- [ ] `requirements.txt` actualizado (añadir `fastapi`, `uvicorn`,
      `python-multipart` para subir archivos).
- [ ] No romper la CLI existente (`python -m factory build` sigue funcionando).

## 6. Paleta CORTEXIA (para la UI)

```
fondo        #0d0d0f      tarjeta      #13131a      borde     #1e1e28
texto        #ffffff      apagado      #6b6b80      acento    #f58a2e
gradiente: #7c5cbf → #4a9eff → #00e87a   (para títulos destacados)
tipografías: Syne (títulos), DM Sans (texto), DM Mono (datos)
```

## 7. Cómo verificar

```
pip install -r factory/requirements.txt
# arrancar la app (el agente define el comando exacto, p. ej.):
uvicorn app:api --reload
# abrir http://localhost:8000 , pulsar «Construir todo», ver 12 episodios,
# abrir un episodio, copiar el prompt del brief, subir un audio de prueba.
```

---

## PROMPT DE ARRANQUE (pégaselo al agente de Antigravity)

> Lee `factory/ANTIGRAVITY_BRIEF.md`. Construye la app web que describe,
> reutilizando el paquete Python `factory/` existente sin duplicar su lógica de
> generación. Usa FastAPI + Uvicorn para el backend y una interfaz web sencilla
> en español con la paleta CORTEXIA. Implementa las pantallas y la API del
> brief, cumple todos los criterios de aceptación de la sección 5, actualiza
> `requirements.txt` y deja un README con un único comando para arrancar en
> Windows. No rompas la CLI actual. Antes de empezar, muéstrame un plan corto
> de archivos que vas a crear; luego impleméntalo y verifícalo arrancando la app.
