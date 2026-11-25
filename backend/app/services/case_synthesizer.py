from typing import Dict, Any, List, Optional
from app.schemas import (
    ExtractedDataSchema,
    CaseSummarySchema,
    DocumentAnalysisSchema
)

class CaseSynthesizer:
    """
    Sintetizador de Expedientes, Recomendador de Actuaciones y Redactor de Borradores.
    Genera resúmenes ejecutivos, listas de chequeo y borradores de respuesta editables
    para la supervisión docente del Consultorio Jurídico.
    """

    @classmethod
    def synthesize_case(
        cls,
        extracted: ExtractedDataSchema,
        classification: Dict[str, Any],
        case_summary: Optional[CaseSummarySchema],
        doc_analysis: Optional[DocumentAnalysisSchema]
    ) -> Dict[str, Any]:
        """
        Produce la síntesis ejecutiva, recomendación preliminar y borrador de respuesta.
        """
        category = classification.get("category", "revision_necesaria")
        student_msg = extracted.student_message or ""
        student_name = extracted.student_name or "Estudiante Practicante"
        case_id = extracted.case_id or (case_summary.case_id if case_summary else "No Identificado")
        citizen_name = case_summary.citizen_name if case_summary else "Usuario no confirmado"

        uncertainties: List[str] = []
        verification_checklist: List[str] = []
        preliminary_rec = ""
        rec_basis = ""
        draft = ""

        # Control de incertidumbres
        if not case_summary:
            uncertainties.append("No se pudo vincular la notificación con un expediente registrado en Mantis.")
        elif case_summary.is_simulated:
            uncertainties.append("Los datos del expediente provienen del adaptador simulado de demostración (Mantis Mock).")

        if doc_analysis and doc_analysis.status == "corrupto":
            uncertainties.append("El documento aportado no pudo ser procesado por presentar errores de lectura o corrupción de datos.")

        # Escenario 1: Solicitud de Cierre de Caso
        if "cierre del id" in student_msg.lower() or "solicito cierre" in student_msg.lower():
            # Evaluar antecedentes
            had_returned_mail = False
            user_unresponsive_months = False
            if case_summary and case_summary.timeline_synthesis:
                for act in case_summary.timeline_synthesis:
                    text_act = (act.get("text") or "").lower()
                    if "devolvió" in text_act or "negó a recibir" in text_act:
                        had_returned_mail = True
                    if "no recibí ninguna respuesta" in text_act or "no ha respondido" in text_act:
                        user_unresponsive_months = True

            preliminary_rec = "Autorizar cierre del caso por inactividad/desistimiento del usuario o solicitar último requerimiento formal."
            rec_basis = (
                f"El caso {case_id} ({citizen_name}) registra múltiples insistencias de cierre por parte del practicante {student_name}. "
                + ("Se evidencia devolución de correspondencia con anotación 'se negó a recibir' en el historial. " if had_returned_mail else "")
                + "Cumplidos los términos reglamentarios de inactividad de la parte interesada, procede el cierre de la solicitud en Mantis."
            )
            verification_checklist = [
                "Verificar que se hayan cumplido los 30 días de inactividad del usuario conforme al reglamento del Consultorio Jurídico.",
                "Confirmar que obre constancia de la citación o devolución por mensajería en el expediente de SharePoint.",
                "Validar que el estado en Mantis se cambie formalmente a 'resuelto' o 'cerrado'."
            ]
            draft = (
                f"Apreciado(a) {student_name},\n\n"
                f"Revisados los antecedentes del caso {case_id} correspondiente a {citizen_name}, y constatando las gestiones "
                f"de contacto infructuosas y la devolución del requerimiento por mensajería, se autoriza el cierre de la solicitud.\n\n"
                f"Por favor proceda a consolidar la constancia de cierre en la carpeta de SharePoint y actualice el estado del caso en Mantis a 'Resuelto'.\n\n"
                f"Cordialmente,\nProf. Supervisora - Consultorio Jurídico Universidad Icesi"
            )

        # Escenario 2: Entrega de documentos para revisión docente
        elif (
            doc_analysis
            and doc_analysis.status == "analizado"
            and doc_analysis.document_type != "Captura de Pantalla / Evidencia Gráfica"
            and category != "informativa"
        ):
            doc_type = doc_analysis.document_type
            petitioner = doc_analysis.petitioner or citizen_name
            counterpart = doc_analysis.counterpart_or_entity or "la entidad competente"
            
            has_missing = bool(doc_analysis.incomplete_or_missing_aspects)
            if has_missing:
                preliminary_rec = f"Devolver borrador de {doc_type} con observaciones de completitud antes de autorizar radicación."
                rec_basis = f"Se identificaron elementos pendientes: {'; '.join(doc_analysis.incomplete_or_missing_aspects)}."
                verification_checklist = [
                    "Comprobar que se anexe la documentación de soporte exigida (copia de documento de identidad y soportes probatorios).",
                    "Verificar que la entidad receptora corresponda al ente competente territorialmente.",
                    "Revisar el estilo de redacción y la debida fundamentación constitucional y legal."
                ]
                missing_str = "\n- ".join(doc_analysis.incomplete_or_missing_aspects)
                draft = (
                    f"Apreciado(a) {student_name},\n\n"
                    f"He revisado el borrador de {doc_type} para el caso {case_id} ({petitioner}).\n\n"
                    f"El documento cuenta con una buena estructura inicial; no obstante, antes de proceder con la radicación formal "
                    f"es indispensable atender los siguientes ajustes:\n- {missing_str}\n\n"
                    f"Una vez incorporadas las correcciones, por favor cargue la versión definitiva para aprobación final.\n\n"
                    f"Cordialmente,\nProf. Supervisora - Consultorio Jurídico Universidad Icesi"
                )
            else:
                preliminary_rec = f"Aprobar borrador de {doc_type} y autorizar suscripción y radicación formal."
                rec_basis = f"El documento cumple con los requisitos formales, identificación de partes ({petitioner} vs {counterpart}), hechos claros y citas normativas pertinentes."
                verification_checklist = [
                    "Validar firmas del usuario y del estudiante conciliador/apoderado.",
                    "Verificar que la fecha de radicación quede registrada en la bitácora de Mantis."
                ]
                draft = (
                    f"Apreciado(a) {student_name},\n\n"
                    f"Revisado el proyecto de {doc_type} correspondiente al caso {case_id} ({petitioner}), encuentro que cumple "
                    f"a cabalidad con los estándares jurídicos y formales requeridos.\n\n"
                    f"Se autoriza proceder con la firma y respectivo trámite/radicación ante {counterpart}.\n\n"
                    f"Cordialmente,\nProf. Supervisora - Consultorio Jurídico Universidad Icesi"
                )

        # Escenario 3: Documento dañado
        elif doc_analysis and doc_analysis.status == "corrupto":
            preliminary_rec = "Requerir al estudiante el reenvío inmediato del archivo en formato DOCX o PDF válido."
            rec_basis = "El archivo adjunto no pudo ser procesado debido a inconsistencias o daño de formato."
            verification_checklist = ["Comprobar que el estudiante remita un archivo íntegro y legible."]
            draft = (
                f"Apreciado(a) {student_name},\n\n"
                f"El archivo remitido en la última nota del caso {case_id} presenta un error de lectura y no se puede visualizar. "
                f"Por favor vuelva a adjuntarlo a la solicitud en formato Word (.docx) o PDF a la mayor brevedad.\n\n"
                f"Cordialmente,\nProf. Supervisora - Consultorio Jurídico Universidad Icesi"
            )

        # Escenario 3b: Adjunto sin texto extraíble (p. ej. hoja de cálculo)
        elif doc_analysis and doc_analysis.status == "no_soportado" and category != "informativa":
            preliminary_rec = "Revisar manualmente el adjunto: el sistema no pudo extraer su contenido."
            rec_basis = "El archivo adjunto no tiene una capa de texto legible por el sistema (p. ej. hoja de cálculo), por lo que no se emite una evaluación documental."
            verification_checklist = [
                "Abrir el adjunto directamente en el expediente de SharePoint.",
                "Cotejar los valores y cálculos con el resto de documentos entregados en la nota.",
            ]
            draft = (
                f"Apreciado(a) {student_name},\n\n"
                f"Recibí los documentos de la última nota del caso {case_id}. Los revisaré directamente en el expediente "
                f"y le comunicaré las observaciones.\n\n"
                f"Cordialmente,\nProf. Supervisora - Consultorio Jurídico Universidad Icesi"
            )

        # Escenario 4: Novedad o Seguimiento Informativo
        elif category == "informativa":
            preliminary_rec = "Tomar nota del avance procesal. No se requiere actuación inmediata del docente."
            rec_basis = "La notificación corresponde a un reporte de trámite, citación de agenda o seguimiento de contacto sin solicitud pendiente."
            verification_checklist = [
                "Verificar la fecha de la diligencia en la agenda docente si se trata de una audiencia de conciliación.",
                "Hacer seguimiento pasivo al plazo de espera de respuesta del usuario."
            ]
            draft = (
                f"Apreciado(a) {student_name},\n\n"
                f"Enterada del reporte sobre el caso {case_id}. Se toma nota del avance para el seguimiento respectivo.\n\n"
                f"Cordialmente,\nProf. Supervisora - Consultorio Jurídico Universidad Icesi"
            )

        # Escenario 5: Revisión Necesaria / Ambigüedad
        else:
            preliminary_rec = "Revisión manual requerida: solicitar aclaración al practicante o verificar expediente en Mantis."
            rec_basis = "El contenido de la notificación o los identificadores del expediente presentan ambigüedad que impide emitir una recomendación concluyente."
            verification_checklist = [
                "Revisar el expediente directamente en Mantis con el número de caso asignado.",
                "Pedir al practicante precisión sobre la actuación o solicitud que somete a consideración."
            ]
            draft = (
                f"Apreciado(a) {student_name},\n\n"
                f"En relación con su mensaje sobre el caso {case_id}, le agradezco precisar con mayor claridad cuál es la solicitud "
                f"o actuación que requiere revisión por parte de la docente supervisora.\n\n"
                f"Cordialmente,\nProf. Supervisora - Consultorio Jurídico Universidad Icesi"
            )

        return {
            "preliminary_recommendation": preliminary_rec,
            "recommendation_basis": rec_basis,
            "response_draft": draft,
            "verification_checklist": verification_checklist,
            "uncertainties": uncertainties
        }
