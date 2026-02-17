# Production Dockerfile für Django
FROM python:3.11-slim

# Umgebungsvariablen setzen
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Arbeitsverzeichnis erstellen
WORKDIR /app

# System-Dependencies installieren
RUN apt-get update && apt-get install -y \
    gcc \
    netcat-traditional \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python Dependencies installieren
COPY requirements.txt requirements-prod.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r requirements-prod.txt

# Projekt-Dateien kopieren
COPY . .

# Static files und Datenverzeichnis erstellen
RUN mkdir -p /app/staticfiles /app/mediafiles /app/data

# Nicht-root User erstellen für Sicherheit
RUN addgroup --system django && \
    adduser --system --ingroup django django && \
    chown -R django:django /app && \
    chmod -R 755 /app/data

# Entrypoint Script ausführbar machen
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh && \
    chown django:django /app/entrypoint.sh

# Zum django User wechseln
USER django

# Port freigeben
EXPOSE 8000

# Entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Standard Command
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "core.wsgi:application"]