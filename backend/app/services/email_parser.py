import re
import email
from email import policy
from typing import Dict, Any, List, Optional
from app.schemas import ExtractedDataSchema, AttachmentSchema

class EmailParser:
    """
    Parser especializado en el formato de notificaciones de Mantis Bug Tracker
    utilizado en el Consultorio Jurídico de la Universidad Icesi.
    """

    SUBJECT_REGEX = re.compile(
        r"\[(?P<project>[^\]]*?)(?P<case_id>\d{5,7})\]:\s*(?P<summary>.*)",
        re.IGNORECASE
    )
    
    NOTE_HEADER_REGEX = re.compile(
        r"\((?P<note_id>\d{5,8})\)\s+(?P<author>[^(]+?)\s+\((?P<role>[^)]+)\)\s*-\s*(?P<date>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})",
        re.MULTILINE
    )

    MANTIS_URL_REGEX = re.compile(
        r"https?://[^\s]+/view\.php\?id=(?P<id>\d+)(?:#c(?P<note_id>\d+))?",
        re.IGNORECASE
    )

    ATTACHMENT_REGEX = re.compile(
        r"^-\s*(?P<filename>[^\n\r]+?)\s*\((?P<size>[\d,.]+)\s*bytes\)",
        re.MULTILINE
    )

    @classmethod
    def parse_text_notification(cls, subject: str, body: str) -> ExtractedDataSchema:
        """
        Extrae datos estructurados de un correo a partir de su asunto y cuerpo.
        """
        extracted = ExtractedDataSchema()

        # 1. Analizar asunto
        subj_match = cls.SUBJECT_REGEX.search(subject or "")
        if subj_match:
            raw_id = subj_match.group("case_id").strip()
            # Normalizar a 7 dígitos con ceros iniciales como se observa en Mantis
            extracted.case_id = raw_id.zfill(7)
            extracted.numeric_case_id = int(raw_id)
            extracted.project = subj_match.group("project").strip()
            extracted.summary_subject = subj_match.group("summary").strip()
        else:
            # Búsqueda secundaria de ID en el asunto
            id_match = re.search(r"\b(\d{5,7})\b", subject or "")
            if id_match:
                extracted.case_id = id_match.group(1).zfill(7)
                extracted.numeric_case_id = int(id_match.group(1))

        # 2. Analizar URL de Mantis en el cuerpo si no se halló en el asunto
        url_match = cls.MANTIS_URL_REGEX.search(body or "")
        if url_match:
            extracted.mantis_url = url_match.group(0)
            if not extracted.case_id:
                raw_id = url_match.group("id")
                extracted.case_id = raw_id.zfill(7)
                extracted.numeric_case_id = int(raw_id)
            if url_match.group("note_id"):
                extracted.note_id = url_match.group("note_id")

        # 3. Analizar encabezado de nota de Mantis
        note_match = cls.NOTE_HEADER_REGEX.search(body or "")
        if note_match:
            extracted.note_id = note_match.group("note_id")
            extracted.student_name = note_match.group("author").strip()
            extracted.student_role = note_match.group("role").strip()
            extracted.activity_date = note_match.group("date").strip()

        # 4. Extraer mensaje del estudiante (limpiando separadores y enlaces)
        student_msg = cls._extract_student_message(body or "")
        extracted.student_message = student_msg

        # 5. Extraer menciones de archivos adjuntos en el cuerpo
        attachments: List[AttachmentSchema] = []
        for att_match in cls.ATTACHMENT_REGEX.finditer(body or ""):
            filename = att_match.group("filename").strip()
            raw_size = att_match.group("size").replace(",", "").replace(".", "").strip()
            try:
                size_bytes = int(raw_size)
            except ValueError:
                size_bytes = 0
            
            ext = filename.split(".")[-1].lower() if "." in filename else ""
            file_type = "unknown"
            if ext in ["pdf"]:
                file_type = "application/pdf"
            elif ext in ["docx", "doc"]:
                file_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif ext in ["png", "jpg", "jpeg"]:
                file_type = f"image/{ext}"
            elif ext in ["txt"]:
                file_type = "text/plain"

            attachments.append(AttachmentSchema(
                filename=filename,
                file_type=file_type,
                size_bytes=size_bytes
            ))

        extracted.attachments = attachments
        return extracted

    @classmethod
    def _extract_student_message(cls, body: str) -> str:
        """
        Aísla el texto redactado por el estudiante dentro de la nota de Mantis.
        """
        lines = body.splitlines()
        filtered = []
        capture = False

        for line in lines:
            stripped = line.strip()
            # Iniciar tras los delimitadores de guiones o tras la URL de Mantis
            if "view.php?id=" in stripped:
                capture = True
                continue
            if stripped.startswith("-----") and not capture:
                capture = True
                continue
            elif stripped.startswith("-----") and capture:
                break
            
            if capture:
                if stripped.startswith("Archivos adjuntos:"):
                    break
                if stripped:
                    filtered.append(stripped)

        if filtered:
            return " ".join(filtered)
        
        # Si no hubo marcadores estándar, devolver texto limpio
        return body.strip()

    @classmethod
    def parse_eml_bytes(cls, eml_bytes: bytes) -> Dict[str, Any]:
        """
        Parsea un archivo binario .eml estándar de correo electrónico.
        """
        msg = email.message_from_bytes(eml_bytes, policy=policy.default)
        subject = msg.get("Subject", "")
        sender = msg.get("From", "")
        recipient = msg.get("To", "")
        date = msg.get("Date", "")
        message_id = msg.get("Message-ID", "")

        body = ""
        attachments_data: List[AttachmentSchema] = []

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                filename = part.get_filename()
                if filename:
                    payload = part.get_payload(decode=True)
                    attachments_data.append(AttachmentSchema(
                        filename=filename,
                        file_type=content_type,
                        size_bytes=len(payload) if payload else 0
                    ))
                elif content_type == "text/plain" and not body:
                    body = part.get_content()
        else:
            body = msg.get_content()

        extracted = cls.parse_text_notification(subject, body)
        if attachments_data:
            extracted.attachments.extend(attachments_data)

        return {
            "subject": subject,
            "sender": sender,
            "recipient": recipient,
            "date": date,
            "message_id": message_id,
            "body": body,
            "extracted": extracted
        }
