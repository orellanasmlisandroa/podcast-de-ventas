# 🎙️ Fábrica de Podcasts de Ventas — CORTEXIA 777

Pipeline en Python que convierte el **conocimiento real del proyecto**
(`../plan.yml`) en una **serie de podcasts a dos voces**, lista para producir el
audio en **NotebookLM** y publicada en un **dashboard**.

Es la versión funcional de lo que la pieza describe: tomar fuentes reales y
sacar de ellas un coach/serie de podcasts — el mismo molde, automatizado.

```
plan.yml  →  serie  →  guiones  →  briefs NotebookLM  →  (audio manual)  →  estado  →  dashboard
```

## Qué genera

| Artefacto | Carpeta | Qué es |
|-----------|---------|--------|
| **Guiones** | `data/scripts/` | Un episodio por sección del plan, en diálogo Ana (conductora) ↔ Beto (coach), con cold open, puntos, analogía y cierre. |
| **Briefs NotebookLM** | `data/briefs/` | Instrucciones + prompt listo para pegar en NotebookLM y generar el Audio Overview de cada episodio. |
| **Piezas para repartir** | `data/distribution/` | Notas del episodio (con sellos de tiempo), tres títulos de clip y la descripción de YouTube — generadas del guion. |
| **Estado** | `data/state.json` | Registro de cada episodio: guion/brief/audio, duración, palabras. |
| **Dashboard** | `data/dashboard.html` | Tablero visual (paleta CORTEXIA) con el avance de la serie. |
| **Audio** | `data/audio/` | Carpeta donde **tú** dejas los audios generados en NotebookLM. |

## 🚀 Aplicación Web (Recomendado)

Ahora puedes usar la Fábrica de Podcasts con una interfaz visual moderna y premium basada en el diseño de CORTEXIA.

Para arrancar la aplicación web en Windows, ejecuta desde esta carpeta (`factory/`):
```powershell
.\start.ps1
```
Y abre en tu navegador: **[http://localhost:8000](http://localhost:8000)**

Desde la interfaz web podrás:
- **Tablero de Control:** Ver el avance general de audio con KPIs dinámicos y barras de progreso.
- **Acciones en 1-Clic:** Generar todos los guiones, briefs y distribución con el botón "Construir Todo" o sincronizar audios con "Sincronizar Audios".
- **Visor Detallado:** Inspeccionar el guion, el brief de NotebookLM y las notas de distribución por pestañas con renderizado de Markdown a HTML.
- **Copiado Rápido:** Copiar al portapapeles el prompt de personalización para NotebookLM y el contenido completo de cada pestaña con botones de un solo clic.
- **Reproductor de Audio Integrado:** Subir tus archivos de audio (.mp3, .wav, .m4a, .ogg) para cada episodio y escucharlos directamente en la app.
- **Configuración Interactiva:** Editar `config.yaml` interactivamente (nombres de voces, PPM, colores de la paleta y ruta del plan). Puedes cambiar `plan_path` para apuntar a otros planes `.yml` y reusar la fábrica en otros nichos.

## Requisitos


- Python 3.10+ (probado en 3.13)
- `pip install -r requirements.txt`  (PyYAML para la CLI; FastAPI + Uvicorn para la app web)

## Uso rápido

Desde esta carpeta (`factory/`):

```bash
python -m factory build       # genera TODO + dashboard
python -m factory dashboard   # reconstruye y abre el dashboard
python -m factory status      # avance en la terminal
```

O en Windows, con el lanzador:

```powershell
.\run.ps1            # instala deps, build y abre el dashboard
.\run.ps1 watch      # vigila la carpeta de audio
.\run.ps1 status
```

## El flujo de audio (manual con NotebookLM)

1. Corre `python -m factory build`. Ya tienes guiones y briefs.
2. Abre el brief de un episodio (`data/briefs/epNN_*.brief.md`).
3. En [NotebookLM](https://notebooklm.google.com): crea un cuaderno, carga las
   fuentes que indica el brief (el guion + el plan + los videos de los expertos),
   pega el prompt de personalización y genera el **Audio Overview**.
4. Descarga el audio y déjalo en `data/audio/` con el nombre exacto del episodio
   (ver `python -m factory audio`). Ej.: `data/audio/ep01_la-ola.mp3`.
5. Corre `python -m factory refresh` (o deja `watch` corriendo): el dashboard
   pasa ese episodio a **Audio listo ✓**.

## Automatización

```bash
python -m factory watch --interval 10   # detecta audios nuevos y republica el dashboard
python -m factory schedule              # imprime el comando de Task Scheduler (Windows)
```

`schedule` da un `schtasks` que refresca el dashboard cada 15 min sin intervención.

## Comandos

| Comando | Acción |
|---------|--------|
| `build` | Pipeline completo: guiones + briefs + estado + dashboard |
| `scripts` | Solo (re)genera los guiones |
| `briefs` | Solo (re)genera los briefs |
| `distribute` | Genera las piezas para repartir (notas, clips, descripción) |
| `refresh` | Re-escanea el audio y re-publica el dashboard (no toca guiones) |
| `dashboard` | Reconstruye y abre el dashboard en el navegador |
| `status` | Tabla de estado en la terminal |
| `audio` | Lista los nombres de audio esperados por episodio |
| `watch` | Vigila `data/audio/` y actualiza al detectar audio |
| `schedule` | Comando de tarea programada de Windows |
| `init` | Crea las carpetas de datos |

## Configuración — `config.yaml`

Cambia las **voces**, la **velocidad de palabras** (para estimar duración), la
**paleta** o la **fuente de conocimiento** (`plan_path`). Apuntando `plan_path` a
otro `plan.yml` reusas la misma fábrica para **cualquier nicho** (keto, perros,
inmobiliaria…), tal como describe la pieza: un solo molde, distintas fuentes.

## Estructura

```
factory/
├─ config.yaml            # configuración
├─ requirements.txt
├─ run.ps1                # lanzador para Windows
├─ factory/               # paquete Python
│  ├─ cli.py              # interfaz de comandos
│  ├─ config.py           # carga de config y rutas
│  ├─ plan_loader.py      # lee ../plan.yml
│  ├─ series.py           # secciones → episodios
│  ├─ scripts.py          # episodios → guiones a dos voces
│  ├─ notebooklm.py       # episodios → briefs de audio
│  ├─ distribution.py     # episodios → notas, clips y descripción
│  ├─ audio.py            # detección de audios entregados
│  ├─ state.py            # registro data/state.json
│  ├─ dashboard.py        # render del dashboard HTML
│  ├─ pipeline.py         # orquestador
│  ├─ automate.py         # watch + tarea programada
│  └─ text_utils.py       # limpieza de HTML/Markdown
└─ data/                  # se crea al correr (guiones, briefs, audio, dashboard)
```
