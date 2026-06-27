# Imagen para desplegar la Fábrica de Podcasts (FastAPI) en Railway.
# Sirve la app de factory/ escuchando en el puerto que Railway inyecta vía $PORT.
FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias primero (mejor cache de capas)
COPY factory/requirements.txt /app/factory/requirements.txt
RUN pip install --no-cache-dir -r /app/factory/requirements.txt

# Copiar el resto del repo (factory/, plan.yml en la raíz, etc.)
COPY . /app

# La app importa "app:app" y el paquete "factory" desde dentro de factory/;
# además resuelve ../plan.yml relativo a esta carpeta.
WORKDIR /app/factory

# Railway define $PORT en runtime; 8000 como fallback local.
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}
