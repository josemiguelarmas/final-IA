import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, Base

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield

def test_api_health():
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

def test_api_notifications_list():
    with TestClient(app) as client:
        response = client.get("/api/notifications")
        assert response.status_code == 200
        notifs = response.json()
        assert isinstance(notifs, list)

def test_api_import_and_human_review_cycle():
    with TestClient(app) as client:
        # 1. Importar notificación
        payload = {
            "subject": "[CJ - Derecho publico 0060228]: CONSULTA",
            "body": """Se ha añadido una NOTA a esta solicitud.
----------------------------------------------------------------------
(0747353) RESTREPO DUQUE VALENTINA (desarrollador) - 2026-10-16 16:08
https://www.icesi.edu.co/consultorio-juridico-app/view.php?id=60228#c747353
Hola profe, por lo anterior, solicito cierre del ID.
----------------------------------------------------------------------""",
            "sender": "Consultorio Jurídico <soporte-syri@listas.icesi.edu.co>",
            "recipient": "Marcela Andrea Ríos Salazar <mrios@example.edu.co>"
        }
        create_resp = client.post("/api/notifications/import", json=payload)
        assert create_resp.status_code == 200
        created = create_resp.json()
        assert created["matched_case_id"] == "0060228"
        assert created["category"] == "requiere_actuacion"
        assert created["review_status"] == "pendiente_revision_humana"
        notif_id = created["id"]

        # 2. Consultar detalle
        detail_resp = client.get(f"/api/notifications/{notif_id}")
        assert detail_resp.status_code == 200
        detail = detail_resp.json()
        assert detail["case_summary"] is not None
        assert detail["case_summary"]["citizen_name"] == "ROSALBA PEÑARANDA OCAMPO"
        assert "cierre" in detail["preliminary_recommendation"].lower()

        # 3. Revisión y aprobación humana por parte del docente
        review_payload = {
            "action_type": "aprobado",
            "confirmed_category": "requiere_actuacion",
            "confirmed_case_id": "0060228",
            "edited_draft": "Apreciada Valentina, revisados los antecedentes, se autoriza formalmente el cierre del caso por inactividad. Proceder en Mantis.",
            "teacher_notes": "Verificada devolución de citación por mensajería en SharePoint.",
            "action_status": "completada",
            "reviewer_name": "Prof. Marcela Andrea Ríos Salazar"
        }
        review_resp = client.post(f"/api/notifications/{notif_id}/review", json=review_payload)
        assert review_resp.status_code == 200
        reviewed = review_resp.json()
        assert reviewed["review_status"] == "revisada"
        assert reviewed["human_decision"]["teacher_notes"] == "Verificada devolución de citación por mensajería en SharePoint."
        assert "se autoriza formalmente" in reviewed["response_draft"]

def test_api_stats():
    with TestClient(app) as client:
        resp = client.get("/api/stats")
        assert resp.status_code == 200
        stats = resp.json()
        assert "total_notifications" in stats
        assert stats["total_notifications"] > 0
