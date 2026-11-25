import uvicorn
import os
import sys

# Asegurar que el directorio backend esté en sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Iniciando Consultorio Jurídico Mantis AI MVP en http://localhost:{port}")
    reload = os.environ.get("DEBUG", "false").lower() == "true"
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=reload)
