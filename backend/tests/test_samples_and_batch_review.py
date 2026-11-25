import json
import os
from collections import defaultdict

import pytest
from fastapi.testclient import TestClient

from app.main import app

SAMPLES = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "sample_data", "notifications.json")


@pytest.fixture(scope="module")
def seeded():
    """Restaura los casos de muestra sobre la base temporal y devuelve la lista de correos."""
    with TestClient(app) as client:
        assert client.post("/api/reset-samples").status_code == 200
        yield client, client.get("/api/notifications").json()


def test_samples_use_their_own_reception_date(seeded):
    _, notifs = seeded
    with open(SAMPLES, encoding="utf-8") as f:
        expected = {s["subject"] + s["received_at"] for s in json.load(f)}
    got = {n["subject"] + n["received_at"][:19] for n in notifs}
    assert expected == got


def test_sample_classification_matches_expected_category(seeded):
    _, notifs = seeded
    with open(SAMPLES, encoding="utf-8") as f:
        samples = json.load(f)
    by_key = {(n["subject"], n["received_at"][:19]): n for n in notifs}
    wrong = [
        (s["id"], s["expected_category"], by_key[(s["subject"], s["received_at"])]["category"])
        for s in samples
        if by_key[(s["subject"], s["received_at"])]["category"] != s["expected_category"]
    ]
    assert wrong == []


def test_samples_have_multi_message_cases_and_varied_states(seeded):
    _, notifs = seeded
    per_case = defaultdict(list)
    for n in notifs:
        if n["matched_case_id"]:
            per_case[n["matched_case_id"]].append(n)
    assert max(len(v) for v in per_case.values()) >= 4
    assert sum(1 for v in per_case.values() if len(v) > 1) >= 5
    assert {"pendiente_revision_humana", "revisada", "archivada"} <= {n["review_status"] for n in notifs}
    assert {"requiere_actuacion", "informativa", "revision_necesaria"} <= {n["category"] for n in notifs}


def test_attached_documents_are_analyzed(seeded):
    _, notifs = seeded
    tutela = [n for n in notifs if n["document_analysis"] and "Tutela" in n["document_analysis"]["document_type"]]
    assert len(tutela) == 2
    v1, v2 = sorted(tutela, key=lambda n: n["received_at"])
    assert any("juramento" in m for m in v1["document_analysis"]["incomplete_or_missing_aspects"])
    assert v2["document_analysis"]["incomplete_or_missing_aspects"] == []
    assert not any(n["document_analysis"] and n["document_analysis"]["status"] == "no_soportado"
                   and n["extracted_data"]["attachments"] and n["extracted_data"]["attachments"][0]["filename"].endswith(".docx")
                   for n in notifs)


def test_sample_data_has_no_real_people(seeded):
    _, notifs = seeded
    blob = json.dumps(notifs, ensure_ascii=False).lower()
    for real in ("kustner", "miryam", "sastoque", "chacon", "rubiela", "zacipa", "1113631466"):
        assert real not in blob


def test_batch_review_applies_one_decision_to_every_message_of_a_case(seeded):
    client, notifs = seeded
    case_msgs = [n for n in notifs if n["matched_case_id"] == "0060228" and n["review_status"] == "pendiente_revision_humana"]
    assert len(case_msgs) == 4
    resp = client.post("/api/notifications/review-batch", json={
        "notification_ids": [n["id"] for n in case_msgs],
        "decision": {"action_type": "aprobado", "confirmed_category": "requiere_actuacion",
                     "edited_draft": "Se autoriza el cierre del caso.", "teacher_notes": "Una sola aprobación.",
                     "action_status": "completada"},
    })
    assert resp.status_code == 200
    updated = resp.json()
    assert len(updated) == 4
    assert {n["review_status"] for n in updated} == {"revisada"}
    assert {n["response_draft"] for n in updated} == {"Se autoriza el cierre del caso."}
    # Ningún correo de otro caso resulta afectado
    others = [n for n in client.get("/api/notifications").json() if n["matched_case_id"] != "0060228"]
    assert any(n["review_status"] == "pendiente_revision_humana" for n in others)


def test_batch_review_rejects_unknown_ids(seeded):
    client, _ = seeded
    resp = client.post("/api/notifications/review-batch", json={
        "notification_ids": ["notif-inexistente"],
        "decision": {"action_type": "archivado"},
    })
    assert resp.status_code == 404
