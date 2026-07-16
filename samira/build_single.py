#!/usr/bin/env python3
"""Genera un samira.html autocontenido: CSS y JS inline, imagenes como data URIs."""
import base64, io, re, os
from PIL import Image

ROOT = "/home/user/podcast-de-ventas/samira"
OUT  = os.path.join(ROOT, "samira.html")
MAXW = 1400          # ancho maximo (px)
QUALITY = 82

def encode_img(path, maxw=MAXW):
    im = Image.open(path)
    im = im.convert("RGB")
    # Respeta orientacion EXIF
    from PIL import ImageOps
    im = ImageOps.exif_transpose(im)
    if im.width > maxw:
        h = round(im.height * maxw / im.width)
        im = im.resize((maxw, h), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=QUALITY, optimize=True, progressive=True)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return "data:image/jpeg;base64," + b64

# --- Leer las tres fuentes ---
with open(os.path.join(ROOT, "index.html"), encoding="utf-8") as f:
    html = f.read()
with open(os.path.join(ROOT, "styles.css"), encoding="utf-8") as f:
    css = f.read()
with open(os.path.join(ROOT, "script.js"), encoding="utf-8") as f:
    js = f.read()

# --- Mapa de imagenes -> data URI ---
imgdir = os.path.join(ROOT, "img")
datauris = {}
for name in sorted(os.listdir(imgdir)):
    if name.lower().endswith((".jpg", ".jpeg", ".png")):
        key = "img/" + name
        datauris[key] = encode_img(os.path.join(imgdir, name))
        kb = len(datauris[key]) * 3 // 4 // 1024
        print(f"  {name}: ~{kb} KB")

# --- Reemplazar el <link> del CSS por un <style> inline ---
html = html.replace(
    '<link rel="stylesheet" href="styles.css" />',
    "<style>\n" + css + "\n</style>"
)
# CSS: url("img/hero.jpg") dentro de styles
for key, uri in datauris.items():
    css_pat = f'url("{key}")'
    if css_pat in html:
        html = html.replace(css_pat, f'url("{uri}")')

# --- Reemplazar el <script src> por el JS inline ---
# El JS referencia rutas img/... en el array PHOTOS; sustituir por data URIs
js_inline = js
for key, uri in datauris.items():
    js_inline = js_inline.replace(f'"{key}"', f'"{uri}"')
html = html.replace(
    '<script src="script.js"></script>',
    "<script>\n" + js_inline + "\n</script>"
)

# --- Reemplazar cualquier src="img/..." que quede en el HTML (og:image, figuras) ---
for key, uri in datauris.items():
    html = html.replace(f'src="{key}"', f'src="{uri}"')
    html = html.replace(f'content="{key}"', f'content="{uri}"')

# Quitar preconnect a Google Fonts (sin conexion, pero dejamos el <link> de fuentes
# para quien tenga internet; si no, cae a las fuentes del sistema definidas en CSS)

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

size_mb = os.path.getsize(OUT) / 1024 / 1024
print(f"\nGenerado: {OUT}")
print(f"Tamano final: {size_mb:.1f} MB")
# Verificar que no queden rutas locales sin incrustar
leftover = re.findall(r'(?:src|href|content)="img/[^"]+"', html) + re.findall(r'"img/samira[^"]+"', html)
print("Rutas locales restantes:", leftover if leftover else "ninguna")
