# Multi-stage Dockerfile para Despliegue en Servidores Linux
# Etapa 1: Compilación de Frontend React
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Etapa 2: Backend FastAPI en Python
FROM python:3.11-slim AS runner
WORKDIR /app

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Instalar dependencias del sistema mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del backend
COPY backend/app ./app
COPY backend/run.py ./run.py

# Copiar bundle estático compilado del frontend
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Exponer puerto HTTP
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/api/health || exit 1

# Comando de inicio
CMD ["python", "run.py"]
