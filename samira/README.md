# Bienvenida, Samira · Reportaje de nacimiento

Sitio web estático (HTML + CSS + JavaScript puro) que celebra el nacimiento de
Samira — **14 de julio de 2026, Plainsboro, New Jersey, US** — como una mezcla
entre anuncio de nacimiento y portfolio fotográfico.

## Estructura

```
samira/
├── index.html      Estructura y contenido de todas las secciones
├── styles.css      Estilos (paleta y tipografías editables arriba del archivo)
├── script.js       Galería, lightbox, navegación y animaciones
├── img/            Fotografías (hero.jpg + samira-01…16.jpg)
└── samira.html     Versión de UN SOLO ARCHIVO (CSS, JS y fotos incrustados)
```

## Versión de un solo archivo (para compartir)

`samira.html` es una copia autocontenida: lleva el CSS, el JavaScript y las
fotos incrustados dentro del propio archivo (~6 MB). No necesita la carpeta
`img/` ni un servidor: se abre con doble clic y se puede enviar por correo o
WhatsApp tal cual. Para regenerarlo tras editar los archivos fuente, usa el
script `build_single.py` (requiere `pip install Pillow`).

## Cómo verlo

No necesita compilación. Abre `index.html` en el navegador, o sirve la carpeta:

```bash
cd samira
python3 -m http.server 8000
# visita http://localhost:8000
```

## Qué editar

- **Datos personales:** busca los textos entre `[corchetes]` en `index.html`
  (nombre del fotógrafo, apellido de Samira, hora, peso y talla).
- **Contacto:** en `index.html`, reemplaza `tucorreo@ejemplo.com` y el número de
  WhatsApp (`wa.me/10000000000`).
- **Fotos y pies de foto:** edita el array `PHOTOS` al inicio de `script.js`.
- **Colores y tipografías:** variables `:root` al inicio de `styles.css`.

## Hospedaje

Al ser 100% estático, funciona en cualquier hosting: GitHub Pages, Netlify,
Vercel, o subiendo la carpeta a cualquier servidor. Es responsive y ligero.
