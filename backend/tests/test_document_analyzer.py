import pytest
from app.services.document_analyzer import DocumentAnalyzer
from app.schemas import AttachmentSchema

def test_document_analysis_derecho_peticion():
    sample_text = """SEÑORES: EMPRESAS MUNICIPALES DE CALI - EMCALI E.I.C.E. E.S.P.
ASUNTO: DERECHO DE PETICIÓN (Art. 23 C.P. y Ley 1755 de 2015)
PETICIONARIO: ROSALBA PEÑARANDA OCAMPO, identificada con C.C. 99000101 de Cali.
HECHOS:
1. Desde hace 3 meses se viene facturando cobro no autorizado.
PRETENSIONES:
1. Que se revise la tarifa aplicada.
ANEXOS: Recibos pendientes por adjuntar."""

    attachment = AttachmentSchema(
        filename="DERECHO DE PETICIÓN- ROSALBA.docx",
        file_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        size_bytes=19659,
        sample_content_text=sample_text
    )

    analysis = DocumentAnalyzer.analyze_attachment(attachment)
    assert "Derecho de Petición" in analysis.document_type
    assert "ROSALBA PEÑARANDA OCAMPO" in analysis.petitioner
    assert "EMCALI" in analysis.counterpart_or_entity
    assert any("23" in g for g in analysis.legal_grounds)
    assert any("pendientes por adjuntar" in missing for missing in analysis.incomplete_or_missing_aspects)

def test_document_analysis_corrupt_file():
    attachment = AttachmentSchema(
        filename="liquidacion_danada.dat",
        file_type="application/octet-stream",
        size_bytes=12450,
        is_corrupt=True
    )
    analysis = DocumentAnalyzer.analyze_attachment(attachment)
    assert analysis.status == "corrupto"
    assert any("reenvío" in missing for missing in analysis.incomplete_or_missing_aspects)
