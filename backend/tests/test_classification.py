import pytest
from app.services.ai_engine import AIEngine
from app.services.email_parser import EmailParser

@pytest.mark.asyncio
async def test_classification_requiere_actuacion_closure():
    subject = "[CJ - Derecho publico 0060228]: CONSULTA"
    body = "Hola profe, por lo anterior, solicito cierre del ID."
    extracted = EmailParser.parse_text_notification(subject, body)
    
    result = await AIEngine.classify_and_evaluate(subject, body, extracted)
    assert result["category"] == "requiere_actuacion"
    assert result["confidence"] >= 0.80
    assert "solicito cierre del ID" in str(result["evidence"])

@pytest.mark.asyncio
async def test_classification_informativa_no_news():
    subject = "[CJ - Derecho publico 0061567]: CONSULTA"
    body = "Hola profe, de momento sin novedades, la usuaria no ha respondido mis mensajes."
    extracted = EmailParser.parse_text_notification(subject, body)
    
    result = await AIEngine.classify_and_evaluate(subject, body, extracted)
    assert result["category"] == "informativa"
    assert "seguimiento" in result["justification"].lower() or "trámite" in result["justification"].lower()

@pytest.mark.asyncio
async def test_classification_revision_necesaria_ambiguous():
    subject = "[CJ - Derecho publico]: CONSULTA SIN NUMERO"
    body = "Profe me dijeron algo pero no sé si esperar."
    extracted = EmailParser.parse_text_notification(subject, body)
    
    result = await AIEngine.classify_and_evaluate(subject, body, extracted)
    assert result["category"] == "revision_necesaria"
