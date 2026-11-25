from sqlalchemy import Column, String, Text, Float, DateTime, JSON, ForeignKey, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class NotificationModel(Base):
    __tablename__ = "notifications"

    id = Column(String(50), primary_key=True, index=True)
    message_id = Column(String(150), unique=True, index=True, nullable=True)
    sender = Column(String(200), nullable=False)
    recipient = Column(String(200), nullable=False)
    received_at = Column(DateTime, default=datetime.utcnow)
    subject = Column(String(300), nullable=False)
    body = Column(Text, nullable=False)
    
    # Extracted metadata
    extracted_data = Column(JSON, default=dict)
    
    # AI Classification
    category = Column(String(50), default="revision_necesaria") # requiere_actuacion, informativa, revision_necesaria
    category_confidence = Column(Float, default=0.0)
    category_justification = Column(Text, default="")
    category_evidence = Column(JSON, default=list)
    
    # Case Association
    matched_case_id = Column(String(50), nullable=True, index=True)
    match_certainty = Column(String(50), default="no_identificado") # confirmada, probable, no_identificado
    
    # Mantis Context & Case Synthesis
    case_summary = Column(JSON, default=dict)
    
    # Document Analysis
    document_analysis = Column(JSON, default=dict)
    
    # Preliminary Recommendation & Response Draft
    preliminary_recommendation = Column(Text, default="")
    recommendation_basis = Column(Text, default="")
    response_draft = Column(Text, default="")
    verification_checklist = Column(JSON, default=list)
    uncertainties = Column(JSON, default=list)
    
    # System & Processing Metadata
    processing_time_ms = Column(Float, default=0.0)
    ai_engine_used = Column(String(100), default="reglas_locales_expertas")
    review_status = Column(String(50), default="pendiente_revision_humana") # pendiente_analisis, analizada, pendiente_revision_humana, revisada, archivada
    
    # Teacher Review / Human in the Loop (Audit trail)
    human_decision = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    audit_logs = relationship("AuditLogModel", back_populates="notification", cascade="all, delete-orphan")


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    notification_id = Column(String(50), ForeignKey("notifications.id"), nullable=False)
    action = Column(String(100), nullable=False) # ej: "creacion", "clasificacion_ia", "aprobacion_docente", "edicion_borrador", "cambio_caso"
    performed_by = Column(String(100), default="sistema")
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON, default=dict)
    
    notification = relationship("NotificationModel", back_populates="audit_logs")
