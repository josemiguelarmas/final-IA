import pytest
from app.services.email_parser import EmailParser

def test_parse_standard_mantis_email():
    subject = "[CJ - Derecho publico 0060228]: CONSULTA"
    body = """Se ha añadido una NOTA a esta solicitud.
----------------------------------------------------------------------
(0747353) RESTREPO DUQUE VALENTINA (desarrollador) - 2026-10-16 16:08
https://www.icesi.edu.co/consultorio-juridico-app/view.php?id=60228#c747353
Hola profe, por lo anterior, solicito cierre del ID.
----------------------------------------------------------------------"""

    extracted = EmailParser.parse_text_notification(subject, body)
    assert extracted.case_id == "0060228"
    assert extracted.numeric_case_id == 60228
    assert extracted.project == "CJ - Derecho publico"
    assert extracted.student_name == "RESTREPO DUQUE VALENTINA"
    assert extracted.student_role == "desarrollador"
    assert extracted.note_id == "0747353"
    assert "solicito cierre del ID" in extracted.student_message

def test_parse_attachments_in_body():
    subject = "[CJ - Derecho publico 0060228]: CONSULTA"
    body = """Se ha añadido una NOTA a esta solicitud.
----------------------------------------------------------------------
(0682173) RESTREPO DUQUE VALENTINA (desarrollador) - 2026-03-09 21:37
https://www.icesi.edu.co/consultorio-juridico-app/view.php?id=60228#c682173
Hola profe, adjunto concepto y dp.
Archivos adjuntos:
- DERECHO DE PETICIÓN- ROSALBA.docx (19,659 bytes)
- CONCEPTO JURÍDICO - ROSALBA PEÑARANDA.docx (75,829 bytes)
----------------------------------------------------------------------"""

    extracted = EmailParser.parse_text_notification(subject, body)
    assert len(extracted.attachments) == 2
    assert extracted.attachments[0].filename == "DERECHO DE PETICIÓN- ROSALBA.docx"
    assert extracted.attachments[0].size_bytes == 19659
    assert extracted.attachments[1].filename == "CONCEPTO JURÍDICO - ROSALBA PEÑARANDA.docx"
    assert extracted.attachments[1].size_bytes == 75829
