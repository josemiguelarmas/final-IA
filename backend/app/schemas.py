from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class AttachmentSchema(BaseModel):
    filename: str
    file_type: Optional[str] = None
    size_bytes: Optional[int] = 0
    content_summary: Optional[str] = None
    sample_content_text: Optional[str] = None
    is_corrupt: Optional[bool] = False

class ExtractedDataSchema(BaseModel):
    case_id: Optional[str] = None
    numeric_case_id: Optional[int] = None
    project: Optional[str] = None
    summary_subject: Optional[str] = None
    student_name: Optional[str] = None
    student_role: Optional[str] = None
    note_id: Optional[str] = None
    mantis_url: Optional[str] = None
    activity_date: Optional[str] = None
    student_message: Optional[str] = None
    attachments: List[AttachmentSchema] = []

class DocumentFactSchema(BaseModel):
    page_or_section: str
    fact: str
    grounding: str

class DocumentAnalysisSchema(BaseModel):
    document_type: str = "Desconocido"
    purpose: str = ""
    petitioner: Optional[str] = None
    counterpart_or_entity: Optional[str] = None
    main_request: str = ""
    relevant_facts: List[DocumentFactSchema] = []
    legal_grounds: List[str] = []
    complete_aspects: List[str] = []
    incomplete_or_missing_aspects: List[str] = []
    inconsistencies: List[str] = []
    status: str = "analizado"  # analizado, corrupto, no_soportado

class CaseSummarySchema(BaseModel):
    case_id: str
    project: str
    citizen_name: Optional[str] = None
    citizen_doc: Optional[str] = None
    citizen_phone: Optional[str] = None
    area: Optional[str] = None
    status: Optional[str] = None
    origin_description: str = ""
    timeline_synthesis: List[Dict[str, Any]] = []
    recent_activity: Optional[str] = None
    pending_commitments: List[str] = []
    is_simulated: bool = True

class HumanDecisionSchema(BaseModel):
    action_type: str = "aprobado"  # aprobado, corregido, descartado, archivado
    confirmed_category: Optional[str] = None
    confirmed_case_id: Optional[str] = None
    edited_draft: Optional[str] = None
    teacher_notes: Optional[str] = None
    action_status: str = "pendiente"  # pendiente, completada, no_requerida
    reviewed_at: Optional[datetime] = None
    reviewer_name: Optional[str] = "Prof. Marcela Andrea Ríos Salazar"

class NotificationCreateRequest(BaseModel):
    subject: str
    body: str
    received_at: Optional[datetime] = None
    sender: Optional[str] = "Consultorio Jurídico <soporte-syri@listas.icesi.edu.co>"
    recipient: Optional[str] = "Marcela Andrea Ríos Salazar <mrios@example.edu.co>"
    message_id: Optional[str] = None
    attachments: Optional[List[AttachmentSchema]] = []

class BatchReviewRequest(BaseModel):
    """Una misma decisión docente aplicada a varios correos (p. ej. todos los de un caso)."""
    notification_ids: List[str] = Field(min_length=1)
    decision: HumanDecisionSchema

class NotificationResponse(BaseModel):
    id: str
    message_id: Optional[str] = None
    sender: str
    recipient: str
    received_at: datetime
    subject: str
    body: str
    extracted_data: ExtractedDataSchema
    category: str
    category_confidence: float
    category_justification: str
    category_evidence: List[str]
    matched_case_id: Optional[str]
    match_certainty: str
    case_summary: Optional[CaseSummarySchema] = None
    document_analysis: Optional[DocumentAnalysisSchema] = None
    preliminary_recommendation: str
    recommendation_basis: str
    response_draft: str
    verification_checklist: List[str]
    uncertainties: List[str]
    processing_time_ms: float
    ai_engine_used: str
    review_status: str
    human_decision: Optional[HumanDecisionSchema] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class StatsResponse(BaseModel):
    total_notifications: int
    requiere_actuacion: int
    informativa: int
    revision_necesaria: int
    pendiente_revision_humana: int
    revisadas: int
    archivadas: int
    avg_processing_time_ms: float
    ai_engines_distribution: Dict[str, int]
