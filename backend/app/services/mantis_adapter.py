from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import json
import os
import httpx
from app.config import settings
from app.schemas import CaseSummarySchema

class MantisAdapter(ABC):
    """
    Contrato de integración con Mantis Bug Tracker.
    Permite desacoplar el origen de datos (Mantis real vs Simulado).
    """

    @abstractmethod
    async def get_case(self, case_id: str) -> Optional[CaseSummarySchema]:
        """Recupera la ficha técnica y síntesis histórica de un expediente."""
        pass

    @abstractmethod
    async def find_cases_by_query(self, query: str) -> List[CaseSummarySchema]:
        """Busca casos por nombres de usuarios o palabras clave cuando el ID no está explícito."""
        pass


class MockMantisAdapter(MantisAdapter):
    """
    Adaptador simulado para pruebas y demostración.
    Utiliza los casos reconstruidos fielmente de las capturas de pantalla de Icesi.
    Etiqueta explícitamente todos los resultados como simulados.
    """

    def __init__(self, sample_data_path: Optional[str] = None):
        if not sample_data_path:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            sample_data_path = os.path.join(base_dir, "sample_data", "mantis_cases.json")
        
        self.cases: Dict[str, Dict[str, Any]] = {}
        if os.path.exists(sample_data_path):
            with open(sample_data_path, "r", encoding="utf-8") as f:
                self.cases = json.load(f)

    async def get_case(self, case_id: str) -> Optional[CaseSummarySchema]:
        normalized_id = case_id.zfill(7)
        case_data = self.cases.get(normalized_id)
        if not case_data:
            # Buscar por ID numérico sin ceros iniciales
            clean_num = str(int(case_id)) if case_id.isdigit() else case_id
            for k, v in self.cases.items():
                if str(v.get("numeric_id")) == clean_num or k == normalized_id:
                    case_data = v
                    break

        if not case_data:
            return None

        activities = case_data.get("activities", [])
        recent_text = activities[-1].get("text") if activities else "Sin actividad previa registrada."

        return CaseSummarySchema(
            case_id=case_data.get("id", normalized_id),
            project=case_data.get("project", "Consultorio Jurídico"),
            citizen_name=case_data.get("citizen", {}).get("nombre"),
            citizen_doc=f"{case_data.get('citizen', {}).get('tipo_documento')} {case_data.get('citizen', {}).get('numero_documento')}",
            citizen_phone=case_data.get("citizen", {}).get("telefono"),
            area=case_data.get("area", "Área General"),
            status=case_data.get("status", "en_tramite"),
            origin_description=case_data.get("description", ""),
            timeline_synthesis=activities,
            recent_activity=recent_text,
            pending_commitments=[
                f"Asignado actualmente a practicante: {case_data.get('assigned_to')}",
                f"Supervisor docente a cargo: {case_data.get('supervisor')}"
            ],
            is_simulated=True
        )

    async def find_cases_by_query(self, query: str) -> List[CaseSummarySchema]:
        q = query.lower().strip()
        results = []
        for cid, data in self.cases.items():
            citizen_name = (data.get("citizen", {}).get("nombre") or "").lower()
            summary = (data.get("summary") or "").lower()
            if q in citizen_name or q in summary or q in cid:
                c = await self.get_case(cid)
                if c:
                    results.append(c)
        return results


class HttpMantisAdapter(MantisAdapter):
    """
    Adaptador HTTP para conexión real con la API REST de Mantis Bug Tracker.
    Requiere URL base institucional y Token de API otorgado por SYRI/Mantis.
    """

    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token

    async def get_case(self, case_id: str) -> Optional[CaseSummarySchema]:
        numeric_id = str(int(case_id)) if case_id.isdigit() else case_id
        url = f"{self.base_url}/api/rest/issues/{numeric_id}"
        headers = {"Authorization": self.api_token}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 404:
                    return None
                resp.raise_for_status()
                data = resp.json().get("issues", [{}])[0]

                # Mapeo de esquema REST de Mantis estándar
                activities = []
                for note in data.get("notes", []):
                    activities.append({
                        "id": str(note.get("id")),
                        "author": note.get("reporter", {}).get("name", "Desconocido"),
                        "role": "desarrollador",
                        "date": note.get("created_at", ""),
                        "text": note.get("text", ""),
                        "attachments": []
                    })

                return CaseSummarySchema(
                    case_id=case_id.zfill(7),
                    project=data.get("project", {}).get("name", "Consultorio Jurídico"),
                    citizen_name=data.get("summary"),
                    status=data.get("status", {}).get("name"),
                    origin_description=data.get("description", ""),
                    timeline_synthesis=activities,
                    recent_activity=activities[-1]["text"] if activities else None,
                    pending_commitments=[],
                    is_simulated=False
                )
        except Exception as e:
            # Fallback seguro reportando la incapacidad de conectar
            return None

    async def find_cases_by_query(self, query: str) -> List[CaseSummarySchema]:
        # Mantis REST search endpoint
        return []


def get_mantis_adapter() -> MantisAdapter:
    """Fábrica de adaptadores según configuración activa"""
    if settings.MANTIS_ADAPTER_TYPE == "http" and settings.MANTIS_API_TOKEN:
        return HttpMantisAdapter(
            base_url=settings.MANTIS_BASE_URL or "https://www.icesi.edu.co/consultorio-juridico-app",
            api_token=settings.MANTIS_API_TOKEN
        )
    return MockMantisAdapter()
