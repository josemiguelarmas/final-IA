# Guía de Despliegue en Servidor Linux
**Sistema de Automatización de Notificaciones Mantis - Consultorio Jurídico**

Esta guía detalla los pasos para instalar, configurar, ejecutar y mantener el MVP en un servidor Linux (Ubuntu 22.04 / 24.04 LTS o Debian 12).

---

## 1. Requisitos Mínimos y Recomendados del Servidor

| Componente | Requisito Mínimo (Motor de Reglas Locales) | Requisito Recomendado (Con Ollama Llama 3.2 3B) | Requisito Óptimo (Modelos 7B / 8B con GPU) |
| :--- | :--- | :--- | :--- |
| **CPU** | 2 núcleos x86_64 | 4 núcleos x86_64 | 8 núcleos |
| **Memoria RAM**| 4 GB | 8 GB a 16 GB | 16 GB a 32 GB |
| **Almacenamiento**| 10 GB SSD | 30 GB SSD | 60 GB NVMe SSD |
| **GPU (Opcional)**| No requerida | No requerida (CPU inferencia 1-3s) | NVIDIA RTX / T4 / A10 (VRAM 8GB+) |
| **Sistema Operativo**| Ubuntu 22.04+ / Debian 12 | Ubuntu 22.04+ / Debian 12 | Ubuntu 22.04+ con NVIDIA Container Toolkit |

---

## 2. Instalación de Docker y Docker Compose en Linux

Si opta por el despliegue con contenedores:

```bash
# 1. Actualizar repositorios e instalar paquetes base
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# 2. Agregar clave GPG oficial de Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 3. Configurar repositorio de Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 4. Instalar Docker Engine y Plugin Compose
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 5. Permitir ejecutar docker sin sudo
sudo usermod -aG docker $USER
newgrp docker
```

---

## 3. Instalación del Motor de IA Local (Ollama)

### Opción A: Instalación Nativa en el Host Linux (Recomendada para rendimiento)
```bash
# Descargar e instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verificar servicio activo
sudo systemctl status ollama

# Descargar el modelo de lenguaje de pesos abiertos seleccionado
# Para servidores con 8-16GB RAM:
ollama pull llama3.2:3b

# O para mayor capacidad de razonamiento jurídico (requiere ~6GB de RAM libres):
# ollama pull mistral:7b
# ollama pull qwen2.5:7b
```

### Opción B: Ejecución dentro de Docker Compose
Si prefiere contenerizar Ollama, use el `docker-compose.yml` provisto en el proyecto:
```bash
docker compose up -d ollama
# Esperar que inicie e invocar la descarga del modelo:
docker exec -it consultorio_mantis_ai_ollama ollama pull llama3.2:3b
```

---

## 4. Configuración de Variables de Entorno

Copie el archivo de ejemplo y defina los valores del servidor:

```bash
cp .env.example .env
nano .env
```

Parámetros clave para producción:
```ini
DEBUG=false
PORT=8000
DATABASE_URL="sqlite:////app/data/consultorio_juridico.db"
OLLAMA_BASE_URL="http://localhost:11434"
OLLAMA_MODEL="llama3.2:3b"
FORCE_RULE_ENGINE=false
MANTIS_ADAPTER_TYPE="mock"
MANTIS_BASE_URL="https://www.icesi.edu.co/consultorio-juridico-app"
```

---

## 5. Inicio de la Aplicación

### Opción A: Con Docker Compose (Recomendado)
```bash
# Construir y levantar en segundo plano
docker compose up -d --build

# Verificar estado de los contenedores
docker compose ps
```

### Opción B: Despliegue Nativo con Python Virtualenv
```bash
# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias backend
pip install -r backend/requirements.txt

# Construir frontend
cd frontend
npm ci
npm run build
cd ..

# Iniciar servidor con Uvicorn
PORT=8000 python backend/run.py
```

---

## 6. Verificación de Funcionamiento (Healthcheck)

Compruebe que todos los endpoints respondan correctamente:

```bash
# 1. Comprobar API y conexión
curl -s http://localhost:8000/api/health | jq .

# 2. Consultar estadísticas iniciales
curl -s http://localhost:8000/api/stats | jq .

# 3. Comprobar inferencia de Ollama en el servidor
curl -s http://localhost:11434/api/tags | jq .
```

---

## 7. Configuración de Seguridad y Reverse Proxy (Nginx + UFW)

**CRÍTICO:** Nunca exponga el puerto `11434` de Ollama a Internet. Debe permanecer vinculado a `127.0.0.1` o dentro de la red interna de Docker.

### Configuración con Nginx como proxy reverso con SSL:
```nginx
# /etc/nginx/sites-available/consultorio-ai.conf
server {
    listen 80;
    server_name consultorio-ai.icesi.edu.co;

    # Redirección forzosa a HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name consultorio-ai.icesi.edu.co;

    ssl_certificate /etc/ssl/certs/consultorio.crt;
    ssl_certificate_key /etc/ssl/private/consultorio.key;

    # Protección de cabeceras HTTP
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Proxy hacia el contenedor de la aplicación
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Configuración del Firewall (`ufw`):
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## 8. Copias de Seguridad y Recuperación (Backups)

Para respaldar la base de datos y auditoría:

```bash
# Script de respaldo diario
BACKUP_DIR="/var/backups/consultorio_ai"
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)

# Respaldo SQLite en caliente
sqlite3 /var/lib/docker/volumes/mvp_app_data/_data/consultorio_juridico.db ".backup '$BACKUP_DIR/db_$DATE.sqlite'"

# Comprimir y retener por 30 días
gzip "$BACKUP_DIR/db_$DATE.sqlite"
find $BACKUP_DIR -name "*.sqlite.gz" -mtime +30 -delete
```

---

## 9. Monitoreo y Solución de Problemas Frecuentes

### Ver registros de la aplicación en vivo:
```bash
docker compose logs -f app
```

### El modelo responde lento en Ollama:
1. Compruebe que el servidor no esté agotando la memoria SWAP: `free -h` y `top`.
2. Reduzca el tamaño del modelo a `llama3.2:1b` o `llama3.2:3b`.
3. Active `FORCE_RULE_ENGINE=true` en `.env` si se requiere respuesta ultra-rápida (menos de 20 milisegundos) sin consumo de GPU.

### La base de datos no inicia:
Compruebe los permisos del volumen de datos: `chmod 755 /app/data`.
