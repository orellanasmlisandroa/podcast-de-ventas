# Brief de producción — Tráiler 00: El podcast ya no es un hobby. Es un activo que vende

> Flujo de audio: **manual con NotebookLM (Audio Overview)**.
> La fábrica ya generó el guion; este brief te dice cómo convertirlo en audio.

## 1. Fuentes para cargar en NotebookLM
Crea un cuaderno nuevo en https://notebooklm.google.com y carga **solo fuentes
reales y permitidas** (ese es el diferencial del proyecto):

- [ ] El guion de este episodio: `scripts/ep00_hero.md`
- [ ] El `plan.yml` del proyecto (conocimiento base de la serie)
- [ ] Los videos / documentos de los expertos del tema (los que puedas usar)

## 2. Prompt de personalización (pégalo en "Customize")
```
Eres el guionista de un episodio de podcast de dos voces, en español neutro (tuteo), basado ÚNICAMENTE en las fuentes cargadas. No inventes datos que no estén en las fuentes.
Tema del tráiler: «El podcast ya no es un hobby. Es un activo que vende». Ángulo: El aperitivo de todo lo que armamos esta semana.

PAPELES (no las dejes de acuerdo en todo):
- Voz A (Ana): defiende la solución del negocio; conoce el material a fondo.
- Voz B (Beto): oyente escéptico que evalúa comprar; pregunta, duda, pide pruebas, saca la objeción real del comprador. La tensión A↔B es el motor; resuélvela al final, no antes.

NIVEL: háblale a alguien que está evaluando comprar, no a un experto. Cero jerga; si un término es indispensable, explícalo en una frase.

ESTRUCTURA EN 8 MOVIMIENTOS (sin saltarte ninguno): 1) Gancho: el dolor o pregunta que el oyente ya trae. 2) Problema: qué está en juego si no se resuelve. 3) Experto: A explica el cómo desde el material. 4) Ejemplo: un caso concreto de las fuentes. 5) Objeción: B lanza la duda más fuerte del comprador (UNA sola, bien trabajada). 6) Método: A responde con el paso a paso real. 7) Recapitulación: ambas voces resumen qué quedó claro. 8) Cierre: una sola invitación a dar el siguiente paso, sin sonar a anuncio.

LÍMITES: ~5 minutos hablados; el cierre invita, no presiona. Idea de cierre: «Todos pueden poner un chat. Casi nadie puede poner un coach hecho de fuentes reales.».
```

## 3. Generación
1. Pulsa **Generate** en el panel de Audio Overview.
2. Escucha el resultado; si hace falta, ajusta el prompt y regenera.
3. **Descarga** el audio (botón de los tres puntos → Download).

## 4. Entrega (esto es lo que detecta la fábrica)
Renombra el archivo descargado y déjalo en `data/audio/`:

```
data/audio/ep00_hero.mp3
```

Extensiones aceptadas: .mp3, .wav, .m4a, .ogg.
En cuanto el archivo aparezca ahí, corre `python -m factory build`
(o deja `python -m factory watch` corriendo) y el dashboard pasará este
episodio a **Audio listo**.

---
*Ángulo:* El aperitivo de todo lo que armamos esta semana
*Frase de cierre:* Todos pueden poner un chat. Casi nadie puede poner un coach hecho de fuentes reales.
