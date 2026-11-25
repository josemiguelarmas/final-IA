# MVP: Automatización de Notificaciones de Mantis para el Consultorio Jurídico
**Universidad Icesi - Consultorio Jurídico**

Asistente inteligente de supervisión docente diseñado para procesar el alto volumen diario de correos provenientes de **Mantis Bug Tracker**, clasificar la necesidad de actuación, cotejar antecedentes procesales, analizar documentos aportados por practicantes y generar síntesis y borradores de respuesta orientativos bajo estricto control y revisión humana.

---

## 🌟 Características Principales

* 🔒 **100% Libre de APIs Comerciales de Pago:** Sin costes variables ni dependencia de OpenAI, Anthropic o Gemini. Utiliza modelos locales de código abierto (vía Ollama) o el motor experto de reglas jurídicas estructuradas.
* 🛡️ **Seguridad y Privacidad Estricta:** Principio de minimización de datos. Aislamiento contra ataques de *Prompt Injection* y protección de datos sensibles conforme a la Ley 1581 de 2012 (Habeas Data).
* 👨‍🏫 **Human-in-the-Loop Obligatorio:** La IA actúa exclusivamente como asistente consultivo. Toda respuesta permanece en borrador local y ningún correo ni mutación en Mantis se emite automáticamente.
* 📑 **Análisis Documental Integrado:** Extracción y validación de borradores en `.docx`, `.pdf` y `.txt` (Derechos de Petición, Conceptos Jurídicos, Constancias de Conciliación).
* 📊 **Historial y Ficha de Mantis:** Cotejo automático de notas, líneas de tiempo y datos del solicitante reconstruidos de las evidencias reales de la Universidad Icesi.
* 💻 **Multiplataforma:** Desarrollado y probado en Windows 11; preparado y documentado para desplegarse en servidores Linux con Docker.

---

## 🏗️ Arquitectura del Sistema

```
mvp/
├── backend/                  # API REST con FastAPI (Python 3.10+)
│   ├── app/
│   │   ├── api/routes.py     # Endpoints REST (Notificaciones, Revisión, Stats)
│   │   ├── services/
│   │   │   ├── email_parser.py       # Extractor de notas, IDs y adjuntos Mantis
│   │   │   ├── mantis_adapter.py     # Adaptador Mock / Conector HTTP REST Mantis
│   │   │   ├── document_analyzer.py  # Analizador de DOCX, PDF y hechos legales
│   │   │   ├── ai_engine.py          # Motor IA Local (Ollama + Reglas Expertas)
│   │   │   └── case_synthesizer.py   # Síntesis fáctica, recomendaciones y borradores
│   │   ├── sample_data/      # Datos de prueba basados en evidencias reales
│   │   ├── database.py       # Conexión SQLAlchemy y persistencia
│   │   ├── models.py         # Modelos relacionales con SQLite/PostgreSQL
│   │   └── schemas.py        # Validación estricta con Pydantic v2
│   ├── tests/                # Suite de 12 pruebas automatizadas con pytest
│   ├── requirements.txt      # Dependencias de backend
│   └── run.py                # Servidor Uvicorn
├── frontend/                 # Interfaz de Usuario con React 18 + TypeScript
│   ├── src/
│   │   ├── components/       # Listas, Detalle, Línea de Tiempo, Borradores
│   │   ├── types.ts          # Tipado TypeScript
│   │   └── api.ts            # Cliente HTTP Axios/Fetch
│   ├── package.json
│   └── vite.config.ts
├── docs/                     # Documentación técnica y académica
│   ├── HALLAZGOS_EVIDENCIAS.md   # Análisis de las capturas y modelos de correo
│   ├── ARQUITECTURA_Y_FLUJO.md   # Diagramas de secuencia y diseño
│   ├── GUIA_DESPLIEGUE_LINUX.md  # Manual de instalación y seguridad en Linux
│   └── LIMITACIONES_Y_ROADMAP.md # Requisitos institucionales y fase 2
├── docker-compose.yml        # Orquestación para despliegue en Linux
├── Dockerfile                # Imagen multi-stage (Node + Python)
├── pytest.ini                # Configuración de pruebas
├── .env.example              # Plantilla de variables de entorno
└── README.md                 # Este documento
```

---

## 🚀 Inicio Rápido en Entorno Local

### Prerrequisitos
* Python 3.10 o superior (verificado con Python 3.14).
* Node.js v18+ y npm (para el frontend de React).
* *(Opcional)* Ollama instalado si desea inferencia de modelos de pesos abiertos (ej. `llama3.2:3b`). Si no tiene Ollama instalado, el sistema activará automáticamente el motor experto de reglas jurídicas locales sin interrupciones ni fallos.

---

### Paso 1: Clonar o Situarse en el Directorio
```bash
cd mvp
```

### Paso 2: Configurar y Ejecutar el Backend (Python)
```bash
# Crear entorno virtual
python -m venv backend/.venv

# Activar entorno virtual:
# En Windows (PowerShell):
backend\.venv\Scripts\Activate.ps1
# En Linux/macOS:
# source backend/.venv/bin/activate

# Instalar dependencias
pip install -r backend/requirements.txt

# Ejecutar el servidor backend
python backend/run.py
```
> El servidor backend iniciará en **http://localhost:8000**.
> La documentación interactiva OpenAPI (Swagger) estará disponible en **http://localhost:8000/docs**.

---

### Paso 3: Configurar y Ejecutar el Frontend (React)
En una nueva terminal:
```bash
cd frontend
npm install
npm run dev
```
> La interfaz web estará disponible en **http://localhost:3000** (con proxy automático al backend en el puerto 8000).

*Alternativa de producción integrada:* Si compila el frontend con `npm run build`, el backend de FastAPI servirá automáticamente toda la aplicación web en **http://localhost:8000** sin necesidad de levantar Vite por separado.

---

## 🧪 Ejecución de Pruebas Automatizadas

El proyecto cuenta con un conjunto integral de **12 pruebas automatizadas** que validan la ingesta de correos, clasificación, análisis documental, resiliencia ante inyecciones adversarias y el ciclo completo de revisión humana.

Para ejecutar la suite de pruebas:
```bash
# Con el entorno virtual activo:
pytest -v
```

### Escenarios Verificados en las Pruebas:
1. `test_parse_standard_mantis_email`: Extracción precisa de ID `0060228`, estudiante, rol, nota y URL de Mantis.
2. `test_parse_attachments_in_body`: Extracción de adjuntos `.docx` y `.pdf` con tamaños en bytes.
3. `test_classification_requiere_actuacion_closure`: Detección de petición formal de cierre de caso.
4. `test_classification_informativa_no_news`: Detección de reporte de mero trámite y seguimiento sin novedad.
5. `test_classification_revision_necesaria_ambiguous`: Aislamiento a revisión humana ante consultas ambiguas.
6. `test_document_analysis_derecho_peticion`: Análisis semántico de hechos, normas y anexos faltantes.
7. `test_document_analysis_corrupt_file`: Detección controlada de archivos dañados sin rotura del sistema.
8. `test_prompt_injection_detection_and_isolation`: Bloqueo y neutralización de intentos de inyección adversaria.
9. `test_api_flow`: Ciclo completo de vida (ingestión, consulta, aprobación docente y actualización de auditoría).

---

## 🐳 Despliegue con Docker en Servidores Linux

El repositorio incluye un `Dockerfile` optimizado y un `docker-compose.yml`:

```bash
# 1. Copiar y ajustar variables de entorno
cp .env.example .env

# 2. Levantar los servicios (App + Ollama)
docker compose up -d --build

# 3. Descargar el modelo de IA local en el contenedor Ollama
docker exec -it consultorio_mantis_ai_ollama ollama pull llama3.2:3b
```
Para instrucciones detalladas de configuración de proxy Nginx, certificados SSL, políticas de firewall (UFW) y respaldos automáticos, consulte [docs/GUIA_DESPLIEGUE_LINUX.md](docs/GUIA_DESPLIEGUE_LINUX.md).

---

## 📖 Documentación Complementaria

* [Hallazgos de Inspección y Análisis de Evidencias](docs/HALLAZGOS_EVIDENCIAS.md): Reconstrucción del caso real `0060228` y modelos de correo de Icesi.
* [Arquitectura y Flujo Técnico](docs/ARQUITECTURA_Y_FLUJO.md): Diagramas de secuencia y diseño de componentes.
* [Guía de Despliegue en Linux](docs/GUIA_DESPLIEGUE_LINUX.md): Requisitos de servidor, seguridad y mantenimiento.
* [Limitaciones y Roadmap Institucional](docs/LIMITACIONES_Y_ROADMAP.md): Requisitos para conectar Mantis REST y Microsoft Graph en producción.

---

## ⚖️ Licencia y Uso Académico
Desarrollado para el Consultorio Jurídico de la Universidad Icesi como proyecto de innovación tecnológica e inteligencia artificial aplicada al derecho procesal y administrativo.
