from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import json
import os

from app.database import get_db
from app.models import NotificationModel, AuditLogModel
from app.schemas import (
    NotificationResponse,
    NotificationCreateRequest,
    HumanDecisionSchema,
    BatchReviewRequest,
    StatsResponse,
    CaseSummarySchema
)
from app.services.email_parser import EmailParser
from app.services.mantis_adapter import get_mantis_adapter
from app.services.document_analyzer import DocumentAnalyzer
from app.services.ai_engine import AIEngine
from app.services.case_synthesizer import CaseSynthesizer
from app.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "mantis_adapter": settings.MANTIS_ADAPTER_TYPE,
        "ai_engine": "ollama" if not settings.FORCE_RULE_ENGINE else "reglas_locales_expertas"
    }

@router.get("/notifications", response_model=List[NotificationResponse])
def get_notifications(
    category: Optional[str] = None,
    review_status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(NotificationModel)
    if category and category != "todas":
        query = query.filter(NotificationModel.category == category)
    if review_status and review_status != "todos":
        query = query.filter(NotificationModel.review_status == review_status)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (NotificationModel.subject.ilike(search_fmt)) |
            (NotificationModel.body.ilike(search_fmt)) |
            (NotificationModel.matched_case_id.ilike(search_fmt))
        )
    return query.order_by(NotificationModel.received_at.desc()).all()

@router.get("/notifications/{notification_id}", response_model=NotificationResponse)
def get_notification(notification_id: str, db: Session = Depends(get_db)):
    notif = db.query(NotificationModel).filter(NotificationModel.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    return notif

@router.post("/notifications/import", response_model=NotificationResponse)
async def import_notification(
    payload: NotificationCreateRequest,
    db: Session = Depends(get_db)
):
    # Detección de duplicados si existe message_id
    if payload.message_id:
        existing = db.query(NotificationModel).filter(NotificationModel.message_id == payload.message_id).first()
        if existing:
            return existing

    # 1. Parsear correo y extraer entidades
    extracted = EmailParser.parse_text_notification(payload.subject, payload.body)
    if payload.attachments:
        # Los adjuntos declarados en el cuerpo se complementan con los aportados (que traen el contenido)
        provided = {a.filename: a for a in payload.attachments}
        extracted.attachments = [provided.pop(a.filename, a) for a in extracted.attachments]
        extracted.attachments.extend(provided.values())

    # 2. Consultar historial de Mantis
    mantis_adapter = get_mantis_adapter()
    case_summary = None
    match_certainty = "no_identificado"
    matched_case_id = extracted.case_id

    if extracted.case_id:
        case_summary = await mantis_adapter.get_case(extracted.case_id)
        if case_summary:
            match_certainty = "confirmada"
        else:
            match_certainty = "probable_no_encontrado"
    else:
        # Búsqueda contextual por nombres en el cuerpo si no hay ID
        words = payload.body.split()
        for i in range(len(words) - 1):
            two_words = f"{words[i]} {words[i+1]}"
            potential_cases = await mantis_adapter.find_cases_by_query(two_words)
            if potential_cases:
                case_summary = potential_cases[0]
                matched_case_id = case_summary.case_id
                match_certainty = "probable"
                break

    # 3. Analizar documentos adjuntos si los hay
    doc_analysis = None
    if extracted.attachments:
        analyzable = next(
            (a for a in extracted.attachments if a.sample_content_text or a.is_corrupt),
            extracted.attachments[0],
        )
        doc_analysis = DocumentAnalyzer.analyze_attachment(analyzable)

    # 4. Clasificación mediante IA Local
    classification = await AIEngine.classify_and_evaluate(payload.subject, payload.body, extracted)

    # 5. Generar Síntesis, Recomendación y Borrador
    synthesis = CaseSynthesizer.synthesize_case(
        extracted=extracted,
        classification=classification,
        case_summary=case_summary,
        doc_analysis=doc_analysis
    )

    # 6. Persistir en Base de Datos
    notif_id = f"notif-{uuid.uuid4().hex[:8]}"
    msg_id = payload.message_id or f"<{notif_id}@icesi.edu.co>"

    new_notif = NotificationModel(
        id=notif_id,
        message_id=msg_id,
        sender=payload.sender or "Consultorio Jurídico <soporte-syri@listas.icesi.edu.co>",
        recipient=payload.recipient or settings.DEFAULT_SUPERVISOR_EMAIL,
        received_at=payload.received_at or datetime.utcnow(),
        subject=payload.subject,
        body=payload.body,
        extracted_data=extracted.model_dump(),
        category=classification["category"],
        category_confidence=classification["confidence"],
        category_justification=classification["justification"],
        category_evidence=classification.get("evidence", []),
        matched_case_id=matched_case_id,
        match_certainty=match_certainty,
        case_summary=case_summary.model_dump() if case_summary else None,
        document_analysis=doc_analysis.model_dump() if doc_analysis else None,
        preliminary_recommendation=synthesis["preliminary_recommendation"],
        recommendation_basis=synthesis["recommendation_basis"],
        response_draft=synthesis["response_draft"],
        verification_checklist=synthesis["verification_checklist"],
        uncertainties=synthesis["uncertainties"],
        processing_time_ms=classification.get("processing_time_ms", 15.0),
        ai_engine_used=classification.get("ai_engine_used", "reglas_locales_expertas"),
        review_status="pendiente_revision_humana",
        human_decision={}
    )
    db.add(new_notif)

    # Auditoría
    audit = AuditLogModel(
        notification_id=notif_id,
        action="ingestion_y_analisis_ia",
        performed_by="sistema_ia",
        details={
            "motor": classification.get("ai_engine_used"),
            "categoria": classification["category"],
            "caso": matched_case_id
        }
    )
    db.add(audit)
    db.commit()
    db.refresh(new_notif)

    return new_notif

@router.post("/notifications/upload-eml", response_model=NotificationResponse)
async def upload_eml_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    content = await file.read()
    parsed_eml = EmailParser.parse_eml_bytes(content)
    
    payload = NotificationCreateRequest(
        subject=parsed_eml["subject"] or f"Notificación importada ({file.filename})",
        body=parsed_eml["body"],
        sender=parsed_eml["sender"] or "Consultorio Jurídico <soporte-syri@listas.icesi.edu.co>",
        recipient=parsed_eml["recipient"] or settings.DEFAULT_SUPERVISOR_EMAIL,
        message_id=parsed_eml["message_id"],
        attachments=parsed_eml["extracted"].attachments
    )
    return await import_notification(payload, db)

def _apply_review(notif: NotificationModel, review: HumanDecisionSchema, db: Session) -> None:
    """Aplica la decisión docente a una notificación y deja rastro de auditoría (sin confirmar la transacción)."""
    review_data = review.model_dump()
    review_data["reviewed_at"] = datetime.utcnow().isoformat()
    notif.human_decision = review_data

    # Si el profesor corrigió categoría o caso
    if review.confirmed_category:
        notif.category = review.confirmed_category
    if review.confirmed_case_id:
        notif.matched_case_id = review.confirmed_case_id
        notif.match_certainty = "confirmada_por_docente"
    if review.edited_draft:
        notif.response_draft = review.edited_draft

    # Actualizar estado de ciclo de vida
    if review.action_type in ("archivado", "descartado"):
        notif.review_status = "archivada"
    elif review.action_type in ("aprobado", "corregido"):
        notif.review_status = "revisada"

    notif.updated_at = datetime.utcnow()

    db.add(AuditLogModel(
        notification_id=notif.id,
        action="revision_humana_docente",
        performed_by=review.reviewer_name or "Docente Supervisor",
        details={
            "tipo_decision": review.action_type,
            "categoria_confirmada": notif.category,
            "borrador_editado": bool(review.edited_draft)
        }
    ))


@router.post("/notifications/{notification_id}/review", response_model=NotificationResponse)
def submit_human_review(
    notification_id: str,
    review: HumanDecisionSchema,
    db: Session = Depends(get_db)
):
    notif = db.query(NotificationModel).filter(NotificationModel.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")

    _apply_review(notif, review, db)
    db.commit()
    db.refresh(notif)
    return notif


@router.post("/notifications/review-batch", response_model=List[NotificationResponse])
def submit_human_review_batch(payload: BatchReviewRequest, db: Session = Depends(get_db)):
    """Aprueba o archiva de una sola vez varios correos (todos los de un mismo caso)."""
    ids = list(dict.fromkeys(payload.notification_ids))
    notifs = db.query(NotificationModel).filter(NotificationModel.id.in_(ids)).all()
    missing = set(ids) - {n.id for n in notifs}
    if missing:
        raise HTTPException(status_code=404, detail=f"Notificaciones no encontradas: {', '.join(sorted(missing))}")

    for notif in notifs:
        _apply_review(notif, payload.decision, db)
    db.commit()
    for notif in notifs:
        db.refresh(notif)
    return sorted(notifs, key=lambda n: n.received_at, reverse=True)

@router.get("/cases/{case_id}", response_model=Optional[CaseSummarySchema])
async def get_case_details(case_id: str):
    mantis_adapter = get_mantis_adapter()
    case = await mantis_adapter.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Expediente Mantis {case_id} no encontrado")
    return case

@router.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    total = db.query(NotificationModel).count()
    req_act = db.query(NotificationModel).filter(NotificationModel.category == "requiere_actuacion").count()
    info = db.query(NotificationModel).filter(NotificationModel.category == "informativa").count()
    rev_nec = db.query(NotificationModel).filter(NotificationModel.category == "revision_necesaria").count()
    pend_rev = db.query(NotificationModel).filter(NotificationModel.review_status == "pendiente_revision_humana").count()
    revisadas = db.query(NotificationModel).filter(NotificationModel.review_status == "revisada").count()
    archivadas = db.query(NotificationModel).filter(NotificationModel.review_status == "archivada").count()

    # Tiempos promedio
    all_notifs = db.query(NotificationModel.processing_time_ms, NotificationModel.ai_engine_used).all()
    avg_time = sum(n[0] for n in all_notifs) / len(all_notifs) if all_notifs else 0.0

    distribution = {}
    for n in all_notifs:
        eng = n[1] or "desconocido"
        distribution[eng] = distribution.get(eng, 0) + 1

    return StatsResponse(
        total_notifications=total,
        requiere_actuacion=req_act,
        informativa=info,
        revision_necesaria=rev_nec,
        pendiente_revision_humana=pend_rev,
        revisadas=revisadas,
        archivadas=archivadas,
        avg_processing_time_ms=round(avg_time, 2),
        ai_engines_distribution=distribution
    )

@router.post("/reset-samples")
async def reset_sample_data(db: Session = Depends(get_db)):
    """Carga o restaura las notificaciones de prueba representativas observadas en las capturas"""
    db.query(AuditLogModel).delete()
    db.query(NotificationModel).delete()
    db.commit()

    sample_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_data", "notifications.json")
    if not os.path.exists(sample_file):
        raise HTTPException(status_code=404, detail="Archivo de datos de muestra no encontrado")

    with open(sample_file, "r", encoding="utf-8") as f:
        samples = json.load(f)

    imported_count = 0
    for s in samples:
        req = NotificationCreateRequest(
            subject=s["subject"],
            body=s["body"],
            received_at=datetime.fromisoformat(s["received_at"]) if s.get("received_at") else None,
            sender=s.get("sender"),
            recipient=s.get("recipient"),
            message_id=s.get("message_id"),
            attachments=s.get("attachments", [])
        )
        created = await import_notification(req, db)
        imported_count += 1
        # Algunos correos de muestra ya vienen revisados, para mostrar los distintos estados
        if s.get("preset_review"):
            _apply_review(created, HumanDecisionSchema(**s["preset_review"], action_status="completada"), db)
            db.commit()

    return {"status": "ok", "imported": imported_count}
