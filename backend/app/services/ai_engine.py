import httpx
import json
import re
import time
from typing import Dict, Any, List, Optional, Tuple
from app.config import settings
from app.schemas import ExtractedDataSchema

class AIEngine:
    """
    Motor de Inferencia de Inteligencia Artificial 100% Local y Libre de Costos.
    Permite alternar de forma transparente entre:
      1. Ollama con modelos de código abierto (ej. llama3.2, mistral, qwen).
      2. Motor Experto Local basado en Reglas Jurídicas y Procesamiento Estructurado.
    Totalmente aislado de APIs comerciales de pago (OpenAI, Anthropic, Gemini API comercial).
    """

    ADVERSARIAL_PATTERNS = [
        re.compile(r"ignora\s+(?:todas\s+)?(?:las\s+)?instrucciones", re.IGNORECASE),
        re.compile(r"eres\s+un\s+bot", re.IGNORECASE),
        re.compile(r"drop\s+table", re.IGNORECASE),
        re.compile(r"delete\s+from", re.IGNORECASE),
        re.compile(r"env[ií]a\s+(?:un\s+)?correo\s+a", re.IGNORECASE),
        re.compile(r"system\s*prompt", re.IGNORECASE),
        re.compile(r"hazte\s+pasar\s+por", re.IGNORECASE)
    ]

    @classmethod
    async def classify_and_evaluate(
        cls,
        subject: str,
        body: str,
        extracted: ExtractedDataSchema
    ) -> Dict[str, Any]:
        """
        Clasifica la notificación y genera justificación, evidencias y evaluación de riesgos.
        """
        start_time = time.perf_counter()

        # 1. Filtro estricto de seguridad contra Inyección Adversaria (Prompt Injection)
        injection_detected, matched_term = cls._detect_prompt_injection(body)
        if injection_detected:
            duration_ms = (time.perf_counter() - start_time) * 1000
            return {
                "category": "revision_necesaria",
                "confidence": 0.99,
                "justification": f"ALERTA DE SEGURIDAD: Se detectó un patrón de inyección de instrucciones adversarias en el texto de la notificación ('{matched_term}'). El sistema aisló el mensaje para revisión humana inmediata.",
                "evidence": [f"Patrón detectado en cuerpo: {matched_term}"],
                "ai_engine_used": "filtro_seguridad_adversario_local",
                "processing_time_ms": round(duration_ms, 2),
                "is_injection_alert": True
            }

        # 2. Intento de inferencia con Ollama si está habilitado y no forzado a reglas
        if not settings.FORCE_RULE_ENGINE:
            ollama_result = await cls._try_ollama_inference(subject, body, extracted)
            if ollama_result:
                duration_ms = (time.perf_counter() - start_time) * 1000
                ollama_result["processing_time_ms"] = round(duration_ms, 2)
                return ollama_result

        # 3. Fallback / Motor Experto Local Estructurado
        rule_result = cls._evaluate_expert_rules(subject, body, extracted)
        duration_ms = (time.perf_counter() - start_time) * 1000
        rule_result["processing_time_ms"] = round(duration_ms, 2)
        return rule_result

    @classmethod
    def _detect_prompt_injection(cls, text: str) -> Tuple[bool, str]:
        for pattern in cls.ADVERSARIAL_PATTERNS:
            match = pattern.search(text)
            if match:
                return True, match.group(0)
        return False, ""

    @classmethod
    async def _try_ollama_inference(
        cls,
        subject: str,
        body: str,
        extracted: ExtractedDataSchema
    ) -> Optional[Dict[str, Any]]:
        """
        Intenta invocar el endpoint local de Ollama. Si no responde en el tiempo límite,
        retorna None para permitir fallback limpio sin interrumpir la operación.
        """
        prompt = f"""Eres un asistente de clasificación jurídica para el Consultorio Jurídico de la Universidad Icesi.
Analiza la siguiente notificación de Mantis y clasifícala en una de las tres categorías:
- 'requiere_actuacion': si el profesor debe revisar un documento, autorizar un cierre, responder al estudiante o tomar una decisión.
- 'informativa': si es solo un avance de trámite, una constancia sin novedad o un aviso de audiencia que no requiere respuesta inmediata.
- 'revision_necesaria': si falta información, el caso es ambiguo o el mensaje no es comprensible.

Notificación:
Asunto: {subject}
Estudiante: {extracted.student_name}
Mensaje: {extracted.student_message or body}
Adjuntos: {[a.filename for a in extracted.attachments]}

Responde ÚNICAMENTE en formato JSON con la siguiente estructura:
{{
  "category": "requiere_actuacion|informativa|revision_necesaria",
  "confidence": 0.85,
  "justification": "Explicación clara en español",
  "evidence": ["Frase textual 1", "Frase textual 2"]
}}"""

        try:
            url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate"
            payload = {
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }
            async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT_SECONDS) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    raw_resp = data.get("response", "{}")
                    parsed = json.loads(raw_resp)
                    if "category" in parsed and parsed["category"] in ["requiere_actuacion", "informativa", "revision_necesaria"]:
                        return {
                            "category": parsed["category"],
                            "confidence": float(parsed.get("confidence", 0.85)),
                            "justification": parsed.get("justification", "Clasificado mediante modelo de lenguaje local."),
                            "evidence": parsed.get("evidence", []),
                            "ai_engine_used": f"ollama_{settings.OLLAMA_MODEL}"
                        }
        except Exception:
            # Fallback silencioso y controlado
            pass
        return None

    @classmethod
    def _evaluate_expert_rules(
        cls,
        subject: str,
        body: str,
        extracted: ExtractedDataSchema
    ) -> Dict[str, Any]:
        """
        Motor de Reglas Jurídicas y Procesamiento Heurístico Estructurado.
        Garantiza consistencia pedagógica y legal sin llamadas a APIs comerciales.
        """
        text_lower = (body + " " + subject).lower()
        msg_lower = (extracted.student_message or "").lower()

        evidence: List[str] = []
        category = "revision_necesaria"
        justification = ""
        confidence = 0.80

        # Caso A: Solicitud explícita de cierre de caso
        if "cierre del id" in text_lower or "cierre de la solicitud" in text_lower or "solicito cierre" in text_lower:
            category = "requiere_actuacion"
            confidence = 0.95
            evidence.append("Solicitud explícita: 'solicito cierre del ID'")
            justification = "El estudiante solicita formalmente la autorización y cierre del caso en Mantis. Requiere que el docente supervisor verifique si se cumplen los requisitos procesales o de desistimiento para autorizar el cierre definitivo."

        # Caso E: Citación o aviso de comparecencia informativa (antes que la entrega de documentos: la citación suele venir como PDF adjunto)
        elif "citación a audiencia" in text_lower or "para conocimiento" in text_lower or "comparecencia programada" in text_lower:
            category = "informativa"
            confidence = 0.85
            evidence.append("Aviso de programación de diligencia.")
            justification = "Comunica la fecha y hora fijada para una audiencia o diligencia con fines de control de agenda, sin requerir una actuación docente resolutiva inmediata."

        # Caso B: Entrega de documentos jurídicos (DP, Concepto, Constancia)
        elif any(att.file_type in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"] for att in extracted.attachments) or \
             "adjunto concepto" in text_lower or "adjunto dp" in text_lower or "constancia de no acuerdo" in text_lower or "borrador" in text_lower:
            category = "requiere_actuacion"
            confidence = 0.92
            evidence.append(f"Adjuntos identificados: {', '.join([a.filename for a in extracted.attachments]) or 'Mención de borrador'}")
            justification = "El practicante remite borradores jurídicos (concepto, derecho de petición o constancia) que exigen revisión docente de fondo previa a su radicación o expedición formal."

        # Caso C: Archivo dañado o ilegible
        elif any(att.is_corrupt for att in extracted.attachments):
            category = "requiere_actuacion"
            confidence = 0.90
            evidence.append("Adjunto con archivo dañado detectado.")
            justification = "Uno de los documentos adjuntos se encuentra dañado o en formato no reconocible. Se requiere que el profesor solicite al estudiante el reenvío inmediato del documento."

        # Caso D: Trámite informativo de seguimiento (sin novedad / la usuaria no respondió)
        elif "sin novedades" in text_lower or "no ha respondido" in text_lower or "no recibí respuesta" in text_lower:
            category = "informativa"
            confidence = 0.88
            evidence.append("Frase informativa: 'sin novedades, la usuaria no ha respondido mis mensajes'")
            justification = "Notificación de mero trámite y seguimiento procesal donde el estudiante deja constancia de su gestión de contacto sin solicitar una decisión inmediata ni radicación."

        # Caso F: Ausencia de ID de caso o ambigüedad
        elif not extracted.case_id:
            category = "revision_necesaria"
            confidence = 0.70
            evidence.append("No se detectó un número de solicitud o ID de Mantis en el asunto ni en el cuerpo.")
            justification = "No fue posible identificar inequívocamente el ID del expediente en Mantis. Se requiere revisión humana para cotejar el caso en el sistema."

        # Caso G: Mensajes dudosos o consultas informales
        elif "no sé si" in msg_lower or "me avisaron" in msg_lower or len(msg_lower) < 20:
            category = "revision_necesaria"
            confidence = 0.65
            evidence.append(f"Mensaje ambiguo: '{extracted.student_message or body}'")
            justification = "El mensaje del practicante plantea dudas operativas o carece de información suficiente para determinar si procede una actuación docente o administrativa."

        else:
            category = "revision_necesaria"
            confidence = 0.60
            justification = "El contenido no encaja de forma concluyente en los patrones automatizados habituales. Se recomienda verificación por parte del profesor."

        return {
            "category": category,
            "confidence": confidence,
            "justification": justification,
            "evidence": evidence,
            "ai_engine_used": "reglas_locales_expertas"
        }
