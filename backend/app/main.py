from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os
import json

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models import NotificationModel
from app.api.routes import router as api_router, import_notification
from app.schemas import NotificationCreateRequest

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Crear tablas en SQLite/PostgreSQL
    Base.metadata.create_all(bind=engine)
    
    # 2. Precargar datos de muestra si la base de datos está vacía
    db = SessionLocal()
    try:
        count = db.query(NotificationModel).count()
        if count == 0:
            sample_file = os.path.join(os.path.dirname(__file__), "sample_data", "notifications.json")
            if os.path.exists(sample_file):
                with open(sample_file, "r", encoding="utf-8") as f:
                    samples = json.load(f)
                for s in samples:
                    req = NotificationCreateRequest(
                        subject=s["subject"],
                        body=s["body"],
                        sender=s.get("sender"),
                        recipient=s.get("recipient"),
                        message_id=s.get("message_id"),
                        attachments=s.get("attachments", [])
                    )
                    await import_notification(req, db)
    finally:
        db.close()

    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="MVP de Automatización de Notificaciones de Mantis para el Consultorio Jurídico (Universidad Icesi)",
    lifespan=lifespan
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas de la API REST
app.include_router(api_router, prefix="/api")

# Detección y montaje flexible del Frontend compilado (Vite)
candidate_paths = [
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend", "dist"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist"),
    os.path.join(os.getcwd(), "frontend", "dist"),
    os.path.join(os.getcwd(), "dist")
]

frontend_dist = None
for p in candidate_paths:
    if os.path.exists(p) and os.path.isdir(p) and os.path.exists(os.path.join(p, "index.html")):
        frontend_dist = p
        break

if frontend_dist:
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api"):
            return None
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
