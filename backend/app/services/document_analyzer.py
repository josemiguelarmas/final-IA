import io
import re
from typing import Optional, List
from app.schemas import DocumentAnalysisSchema, DocumentFactSchema, AttachmentSchema

class DocumentAnalyzer:
    """
    Analizador de documentos jurídicos y anexos del Consultorio Jurídico.
    Extrae contenido de DOCX, PDF y texto, estructurando pretensiones, hechos,
    normas y elementos faltantes sin generar alucinaciones ni invocar APIs comerciales.
    """

    @classmethod
    def analyze_attachment(
        cls,
        attachment: AttachmentSchema,
        file_bytes: Optional[bytes] = None
    ) -> DocumentAnalysisSchema:
        """
        Analiza un archivo adjunto. Si se proveen bytes reales los extrae;
        si es un dato de muestra, utiliza `sample_content_text` o el resumen.
        """
        if attachment.is_corrupt:
            return DocumentAnalysisSchema(
                document_type=f"Archivo Dañado ({attachment.filename})",
                purpose="No se puede determinar el contenido por daño o formato no legible en el archivo.",
                main_request="Solicitud no determinable debido a corrupción del archivo.",
                status="corrupto",
                incomplete_or_missing_aspects=[
                    "El archivo no pudo ser leído o abierto correctamente.",
                    "Se requiere solicitar al practicante el reenvío del documento en formato DOCX o PDF válido."
                ]
            )

        extracted_text = ""
        filename_lower = (attachment.filename or "").lower()

        # 1. Extracción de bytes si se proporcionan
        if file_bytes:
            extracted_text = cls._extract_text_from_bytes(file_bytes, filename_lower)
        elif attachment.sample_content_text:
            extracted_text = attachment.sample_content_text
        elif attachment.content_summary:
            extracted_text = attachment.content_summary

        if not extracted_text:
            if "png" in filename_lower or "jpg" in filename_lower:
                return DocumentAnalysisSchema(
                    document_type="Captura de Pantalla / Evidencia Gráfica",
                    purpose="Registro probatorio de gestión (ej. conversación de mensajería o radicado).",
                    main_request="Evidencia visual de intento de contacto o soporte del trámite.",
                    status="analizado",
                    complete_aspects=["Archivo de imagen recibido legiblemente."]
                )
            return DocumentAnalysisSchema(
                document_type="Archivo sin contenido textual legible",
                purpose="No fue posible extraer texto del archivo.",
                status="no_soportado",
                incomplete_or_missing_aspects=["El archivo carece de capa de texto extraíble."]
            )

        # 2. Análisis semántico estructurado sobre el texto
        return cls._analyze_text_content(attachment.filename, extracted_text)

    @classmethod
    def _extract_text_from_bytes(cls, data: bytes, filename: str) -> str:
        text = ""
        try:
            if filename.endswith(".docx"):
                import docx
                doc = docx.Document(io.BytesIO(data))
                paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                text = "\n".join(paragraphs)
            elif filename.endswith(".pdf"):
                from pypdf import PdfReader
                reader = PdfReader(io.BytesIO(data))
                pages = [page.extract_text() or "" for page in reader.pages]
                text = "\n".join(pages)
            elif filename.endswith(".txt"):
                text = data.decode("utf-8", errors="ignore")
        except Exception:
            return ""
        return text

    @classmethod
    def _analyze_text_content(cls, filename: str, text: str) -> DocumentAnalysisSchema:
        upper_text = text.upper()
        doc_type = "Documento Jurídico General"
        purpose = ""
        main_request = ""
        petitioner = None
        counterpart = None
        legal_grounds: List[str] = []
        facts: List[DocumentFactSchema] = []
        complete_aspects: List[str] = []
        incomplete_aspects: List[str] = []
        inconsistencies: List[str] = []

        # Tipo de documento y propósito
        if "ACCIÓN DE TUTELA" in upper_text or "ACCIONANTE" in upper_text:
            doc_type = "Borrador de Acción de Tutela"
            purpose = "Protección inmediata de derechos fundamentales (Art. 86 C.P. y Decreto 2591 de 1991) frente a la acción u omisión de una autoridad o particular."
        elif "ACTA DE CONCILIACIÓN" in upper_text:
            doc_type = "Acta de Conciliación con Acuerdo"
            purpose = "Constancia del acuerdo alcanzado por las partes en audiencia de conciliación extrajudicial."
        elif "DERECHO DE PETICIÓN" in upper_text or "PETICIONARIO" in upper_text:
            doc_type = "Borrador de Derecho de Petición"
            purpose = "Ejercicio del derecho fundamental de petición (Art. 23 C.P.) para requerir actuación de entidad pública o prestadora de servicios."
        elif "CONCEPTO JURÍDICO" in upper_text or "PROBLEMA JURÍDICO" in upper_text:
            doc_type = "Concepto Jurídico de Asesoría"
            purpose = "Concepto de viabilidad y fundamentación jurídica emitido por el estudiante practicante."
        elif "CONSTANCIA DE NO ACUERDO" in upper_text or "CENTRO DE CONCILIACIÓN" in upper_text:
            doc_type = "Acta / Constancia de No Acuerdo de Conciliación"
            purpose = "Certificación oficial de agotamiento de audiencia de conciliación extrajudicial sin arreglo entre partes."
        elif "CITACIÓN" in upper_text or "COMPARECENCIA" in upper_text:
            doc_type = "Citación a Audiencia de Conciliación"
            purpose = "Notificación formal a las partes para comparecer a audiencia en fecha y hora determinada."

        # Identificación de Peticionario
        pet_match = re.search(r"(?:PETICIONARIO|ACCIONANTE|USUARIA|CONVOCANTE|SOLICITANTE)[\s:]+([^\n,;]+)", text, re.IGNORECASE)
        if pet_match:
            petitioner = pet_match.group(1).strip()

        # Identificación de Entidad o Contraparte
        ent_match = re.search(r"(?:SEÑORES|DIRIGIDO A|ENTIDAD|ACCIONADA|ACCIONADO|CONVOCADO)[\s:]+([^\n,;]+)", text, re.IGNORECASE)
        if ent_match:
            counterpart = ent_match.group(1).strip()

        # Extracción de Normas Jurídicas
        norm_patterns = [
            r"ART(?:ÍCULO|\.)?\s*\d+\s*(?:DE LA\s*)?C(?:ONSTITUCIÓN|\.P\.)",
            r"LEY\s*\d+\s*(?:DE\s*\d{4})?",
            r"DECRETO\s*\d+\s*(?:DE\s*\d{4})?",
            r"CÓDIGO\s+[A-Z\s]+",
            r"SILENCIO ADMINISTRATIVO\s+[A-Z]+"
        ]
        for pat in norm_patterns:
            for match in re.finditer(pat, text, re.IGNORECASE):
                ground = match.group(0).strip()
                if ground not in legal_grounds:
                    legal_grounds.append(ground)

        # Extracción de Hechos
        lines = text.splitlines()
        for idx, line in enumerate(lines):
            l = line.strip()
            # Hechos numerados
            if re.match(r"^\d+\.\s+", l) and len(l) > 15:
                facts.append(DocumentFactSchema(
                    page_or_section=f"Línea {idx+1}",
                    fact=l,
                    grounding="Texto literal extraído del documento del estudiante."
                ))
            elif "PRETENSIONES" in l.upper() or "PETICIÓN:" in l.upper():
                # Capturar pretensión
                if idx + 1 < len(lines):
                    main_request = lines[idx + 1].strip()

        if not main_request:
            if "cierre" in text.lower():
                main_request = "Solicitud de autorización para cierre del caso por inactividad o cumplimiento."
            elif petitioner and counterpart:
                main_request = f"Reclamación de {petitioner} contra {counterpart}."
            else:
                main_request = "Revisión general de la actuación jurídica presentada."

        # Verificación de completitud y faltantes
        if "DERECHO DE PETICIÓN" in upper_text:
            if "PENDIENTES POR ADJUNTAR" in upper_text or "RECIBOS" in upper_text and "COPIA" not in upper_text:
                incomplete_aspects.append("Se menciona que los recibos o copias de cédula están pendientes por adjuntar antes de la radicación.")
            if not legal_grounds:
                incomplete_aspects.append("No se identificaron citas normativas expresas (ej. Ley 1755 de 2015 o Art. 23 C.P.).")
            else:
                complete_aspects.append("Contiene fundamento normativo constitucional y legal.")
            if facts:
                complete_aspects.append(f"Se estructuran {len(facts)} hechos numerados.")
            else:
                incomplete_aspects.append("Los hechos no están claramente enumerados o redactados cronológicamente.")

        elif "ACCIÓN DE TUTELA" in upper_text or "ACCIONANTE" in upper_text:
            if "JURAMENTO" not in upper_text:
                incomplete_aspects.append("No incluye la manifestación bajo la gravedad del juramento de no haber presentado otra tutela por los mismos hechos (Art. 37 del Decreto 2591 de 1991).")
            else:
                complete_aspects.append("Incluye la manifestación bajo la gravedad del juramento.")
            if "PRUEBAS" not in upper_text:
                incomplete_aspects.append("No relaciona las pruebas que sustentan la solicitud.")
            else:
                complete_aspects.append("Relaciona las pruebas aportadas.")
            if "DERECHOS VULNERADOS" in upper_text or "DERECHOS FUNDAMENTALES" in upper_text:
                complete_aspects.append("Identifica los derechos fundamentales invocados.")
            if facts:
                complete_aspects.append(f"Se estructuran {len(facts)} hechos numerados.")

        elif "ACTA DE CONCILIACIÓN" in upper_text:
            if "LEY 2220 DE 2022" in upper_text:
                complete_aspects.append("Cita la Ley 2220 de 2022 (Estatuto de Conciliación vigente).")
            if petitioner and counterpart:
                complete_aspects.append("Identifica plenamente a las partes convocante y convocada.")
            if "ACUERDO:" in upper_text:
                complete_aspects.append("Consigna las obligaciones acordadas, con monto, plazo y modalidad.")
            else:
                incomplete_aspects.append("No se consignan con claridad las obligaciones acordadas por las partes.")
            if "FIRMAS" in upper_text:
                complete_aspects.append("Incluye el bloque de firmas de las partes y del conciliador.")
            else:
                incomplete_aspects.append("No se evidencia el bloque de firmas de las partes y del conciliador.")

        elif "CONSTANCIA DE NO ACUERDO" in upper_text:
            if "LEY 2220 DE 2022" in upper_text:
                complete_aspects.append("Cita la Ley 2220 de 2022 (Estatuto de Conciliación vigente).")
            if petitioner and counterpart:
                complete_aspects.append("Identifica plenamente a las partes convocante y convocada.")
            complete_aspects.append("Declara expresamente la falta de ánimo conciliatorio.")

        if not complete_aspects:
            complete_aspects.append("Documento estructurado con formato académico estándar.")

        return DocumentAnalysisSchema(
            document_type=doc_type,
            purpose=purpose or "Análisis del contenido documental aportado por el estudiante.",
            petitioner=petitioner,
            counterpart_or_entity=counterpart,
            main_request=main_request,
            relevant_facts=facts[:5],
            legal_grounds=legal_grounds,
            complete_aspects=complete_aspects,
            incomplete_or_missing_aspects=incomplete_aspects,
            inconsistencies=inconsistencies,
            status="analizado"
        )
