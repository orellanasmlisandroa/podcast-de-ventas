"""Servidor FastAPI para la aplicación web de la Fábrica de Podcasts de Ventas — CORTEXIA 777."""
from __future__ import annotations

import os
import shutil
import yaml
from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.responses import HTMLResponse, PlainTextResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from factory.config import Config, DEFAULT_CONFIG_PATH
from factory import pipeline, state as state_mod

app = FastAPI(title="Fábrica de Podcasts — CORTEXIA 777")
api = app

# Configurar CORS por si se usa en desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolver la carpeta raíz de factory
cfg_init = Config.load()
ROOT_DIR = cfg_init.root

def get_config() -> Config:
    return Config.load()

@app.get("/api/state")
def get_state(cfg: Config = Depends(get_config)):
    try:
        st = state_mod.load(cfg)
        summary = state_mod.summarize(st)
        return {"state": st, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cargar el estado: {str(e)}")

@app.post("/api/build")
def build_all(cfg: Config = Depends(get_config)):
    try:
        st = pipeline.build_all(cfg)
        summary = state_mod.summarize(st)
        return {"state": st, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al construir la serie: {str(e)}")

@app.post("/api/refresh")
def refresh_only(cfg: Config = Depends(get_config)):
    try:
        st = pipeline.refresh_only(cfg)
        summary = state_mod.summarize(st)
        return {"state": st, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al refrescar el estado de audios: {str(e)}")

@app.get("/api/episodes")
def list_episodes(cfg: Config = Depends(get_config)):
    try:
        st = state_mod.load(cfg)
        eps = sorted(st.get("episodes", {}).values(), key=lambda r: r.get("number", "99"))
        return eps
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar episodios: {str(e)}")

@app.get("/api/episodes/{slug}")
def get_episode(slug: str, cfg: Config = Depends(get_config)):
    st = state_mod.load(cfg)
    ep = st.get("episodes", {}).get(slug)
    if not ep:
        raise HTTPException(status_code=404, detail=f"Episodio '{slug}' no encontrado")
    return ep

@app.get("/api/episodes/{slug}/script")
def get_script(slug: str, cfg: Config = Depends(get_config)):
    st = state_mod.load(cfg)
    ep = st.get("episodes", {}).get(slug)
    if not ep or not ep.get("script_file"):
        raise HTTPException(status_code=404, detail="El guión no ha sido generado aún")
    path = cfg.data_dir / ep["script_file"]
    if not path.exists():
         raise HTTPException(status_code=404, detail=f"Archivo de guión no encontrado en {path}")
    return PlainTextResponse(path.read_text(encoding="utf-8"))

@app.get("/api/episodes/{slug}/brief")
def get_brief(slug: str, cfg: Config = Depends(get_config)):
    st = state_mod.load(cfg)
    ep = st.get("episodes", {}).get(slug)
    if not ep or not ep.get("brief_file"):
        raise HTTPException(status_code=404, detail="El brief no ha sido generado aún")
    path = cfg.data_dir / ep["brief_file"]
    if not path.exists():
         raise HTTPException(status_code=404, detail=f"Archivo de brief no encontrado en {path}")
    return PlainTextResponse(path.read_text(encoding="utf-8"))

@app.get("/api/episodes/{slug}/distribution")
def get_distribution(slug: str, cfg: Config = Depends(get_config)):
    st = state_mod.load(cfg)
    ep = st.get("episodes", {}).get(slug)
    if not ep or not ep.get("dist_file"):
        raise HTTPException(status_code=404, detail="Las piezas de distribución no han sido generadas aún")
    path = cfg.data_dir / ep["dist_file"]
    if not path.exists():
         raise HTTPException(status_code=404, detail=f"Archivo de distribución no encontrado en {path}")
    return PlainTextResponse(path.read_text(encoding="utf-8"))

@app.post("/api/episodes/{slug}/audio")
async def upload_audio(slug: str, file: UploadFile = File(...), cfg: Config = Depends(get_config)):
    _, ext = os.path.splitext(file.filename)
    ext = ext.lower()
    if ext not in cfg.audio_exts:
        raise HTTPException(status_code=400, detail=f"Extensión no permitida. Formatos válidos: {cfg.audio_exts}")
    
    plan, episodes = pipeline.load_episodes(cfg)
    ep = next((e for e in episodes if e.slug == slug), None)
    if not ep:
        raise HTTPException(status_code=404, detail=f"Episodio '{slug}' no encontrado en el plan activo")
    
    cfg.ensure_dirs()
    
    # Eliminar cualquier audio previo para este episodio con otras extensiones permitidas
    for allowed_ext in cfg.audio_exts:
        old_file = cfg.audio_dir / f"{ep.stem}{allowed_ext}"
        if old_file.exists():
            try:
                old_file.unlink()
            except Exception:
                pass
                
    # Guardar nuevo archivo
    target_path = cfg.audio_dir / f"{ep.stem}{ext}"
    try:
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar el archivo: {str(e)}")
        
    # Refrescar estado y dashboard
    st = pipeline.refresh_only(cfg)
    summary = state_mod.summarize(st)
    return {"state": st, "summary": summary}

@app.get("/api/config")
def get_raw_config(cfg: Config = Depends(get_config)):
    return cfg.raw

@app.put("/api/config")
def update_config(new_raw: dict):
    path = DEFAULT_CONFIG_PATH
    try:
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(new_raw, f, allow_unicode=True, sort_keys=False)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al escribir config.yaml: {str(e)}")

@app.get("/audio/{filename}")
def serve_audio(filename: str, cfg: Config = Depends(get_config)):
    audio_file = cfg.audio_dir / filename
    if not audio_file.exists() or not audio_file.is_file():
        raise HTTPException(status_code=404, detail="Archivo de audio no encontrado")
    
    ext = Path(filename).suffix.lower()
    media_types = {
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".m4a": "audio/mp4",
        ".ogg": "audio/ogg"
    }
    media_type = media_types.get(ext, "application/octet-stream")
    return FileResponse(audio_file, media_type=media_type)

@app.get("/")
def get_index():
    index_path = ROOT_DIR / "static" / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Frontend index.html no encontrado en static/")
    return HTMLResponse(index_path.read_text(encoding="utf-8"))

# Montar static para otros assets si existiera
static_path = ROOT_DIR / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
