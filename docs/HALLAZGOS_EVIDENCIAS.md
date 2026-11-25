# Hallazgos de Inspección: Capturas de Pantalla y Notificaciones de Mantis
**Consultorio Jurídico - Universidad Icesi**
**Fecha de análisis:** Octubre de 2026
**Autor:** Antigravity AI - Solución MVP

---

## 1. Resumen Ejecutivo de la Inspección

A partir de la inspección exhaustiva de las 7 capturas de pantalla (`imagen_01.png` a `imagen_07.png`) ubicadas en el directorio raíz del proyecto, se ha reconstruido con precisión el ecosistema digital, el formato de las notificaciones, los flujos operativos y la sobrecarga que experimentan los profesores supervisores del Consultorio Jurídico de la Universidad Icesi.

---

## 2. Inventario y Análisis Detallado de Evidencias

### 2.1. `imagen_01.png` y `imagen_02.png`: Bandeja de Correo y Formato de Notificaciones
* **Cliente de Correo:** Webmail/Outlook institucional (cuenta observada: `mrios@example.edu.co` correspondiente a la profesora supervisora *Marcela Andrea Ríos Salazar*).
* **Volumen:** La bandeja de entrada muestra más de 3,764 correos recibidos y decenas de notificaciones con escasos minutos de diferencia.
* **Remitente oficial:** `Consultorio Jurídico <soporte-syri@listas.icesi.edu.co>`.
* **Patrón de Asunto:**
  `[<Área/Proyecto> <ID_CASO_7_DIGITOS>]: <TIPO/RESUMEN>`
  *Ejemplos observados:*
  - `[CJ - Derecho publico 0060228]: CONSULTA`
  - `[CJ - Derecho publico 0061567]: CONSULTA`
  - `[CJ - Derecho publico 0060614]: CONSULTA`
  - `[CJ - Derecho publico 0061601]: CONSULTA`
  - `[CJ - Derecho publico 0050255]: CONSULTA`
  - `[CJ - Derecho publico 0061346]: CONSULTA`
* **Estructura del Cuerpo del Correo:**
  ```text
  Se ha añadido una NOTA a esta solicitud.
  ----------------------------------------------------------------------
  (<ID_NOTA>) <NOMBRE_ESTUDIANTE> (desarrollador) - <YYYY-MM-DD HH:MM>
  https://www.icesi.edu.co/consultorio-juridico-app/view.php?id=<ID_NUMERICO>#c<ID_NOTA>
  <MENSAJE_DEL_ESTUDIANTE>
  [Archivos adjuntos:
  - <NOMBRE_ARCHIVO> (<TAMAÑO> bytes)]
  ----------------------------------------------------------------------
  ```
* **Casos Específicos Evidenciados:**
  - **Caso 0060228 (Imagen 01):** Estudiante *RESTREPO DUQUE VALENTINA (desarrollador)*, nota `(0747353)`. Mensaje: *"Hola profe, por lo anterior, solicito cierre del ID."*
  - **Caso 0061567 (Imagen 02):** Misma estudiante, nota `(0747369)`. Mensaje: *"Hola profe, de momento sin novedades, la usuaria no ha respondido mis mensajes."* Adjunto: `image-17.png (737,118 bytes)` (captura probatoria de intento de contacto).

### 2.2. `imagen_03.png`, `imagen_04.png`, `imagen_05.png`: Expediente y Línea de Actividades en Mantis
* **Instalación de Mantis:** Aplicación web en `/consultorio-juridico-app/view.php?id=60228`.
* **Roles en Mantis:**
  - *supervisor:* Profesor docente (ej. `Marcela Andrea Ríos Salazar`, `Paola Andrea Cifuentes Luna`, `Diana Carolina Mejía Roldán`).
  - *desarrollador:* Rol asignado a los estudiantes practicantes del consultorio (ej. `RESTREPO DUQUE VALENTINA`, `Julián Esteban Cárdenas Pinto`).
* **Expediente 0060228 - Historial Reconstruido:**
  1. *2026-03-03 15:02 (Julián Esteban Cárdenas Pinto):* Crea enlace a carpeta de SharePoint institucional: `https://icesiedu.sharepoint.com/:f:/r/sites/500/501/Expedientes%20Usuarios/60228...`.
  2. *2026-03-05 15:40 (Paola Andrea Cifuentes Luna - Supervisor):* Nota directiva: *"ESTE CASO ES PARA CONCEPTO + DP"*.
  3. *2026-03-09 21:37 (RESTREPO DUQUE VALENTINA):* Entrega de borradores jurídicos con adjuntos:
     - `DERECHO DE PETICIÓN- ROSALBA.docx (19,659 bytes)`
     - `CONCEPTO JURÍDICO - ROSALBA PEÑARANDA.docx (75,829 bytes)`
  4. *2026-03 en adelante:* Retroalimentación de la profesora Marcela Andrea Ríos Salazar.
  5. *2026-05-13 11:17:* Estudiante reporta seguimiento de entrega de requerimiento sin respuesta de usuaria.
  6. *2026-05-20 15:41:* Estudiante solicita cierre formal por falta de entrega de documentos del usuario.
  7. *2026-05-22 15:04 (Diana Carolina Mejía Roldán - Supervisor):* Comunica que la mensajería devolvió el requerimiento ("motivo se negó a recibir").
  8. *2026-05-27, 2026-06-03, 2026-06-10, 2026-10-02, 2026-10-10, 2026-10-16:* El estudiante insiste reiteradamente: *"Hola profe, por lo anterior, solicito cierre del ID."*
* **Hallazgo Clave de Fricción:** Una solicitud de cierre no atendida por meses genera un bucle de notificaciones semanales repetitivas que inundan la bandeja de entrada de los profesores.

### 2.3. `imagen_06.png`: Dashboard "Mi Vista" de Mantis
* **Sección "Asignadas a mí (pendientes)":** Muestra casos activos que requieren acción del profesor (ej. `0061719`, `0004999`, `0002714`).
* **Sección "No Asignadas":** Existen más de 2,688 solicitudes no asignadas acumuladas en el sistema.
* **Sección "Línea de tiempo" en tiempo real:**
  - `VALENCIA ORTIZ SANTIAGO` realizó comentario en `0062883` y `0062866`.
  - `Camila Andrea Bonilla Soto` adjuntó `2119- Solicitud_comparecencia_a_la_audiencia_de_conciliacion_...` en `0062644`.
  - `Camila Andrea Bonilla Soto` adjuntó `CONSTANCIA DE NO ACUERDO NELLY BARRERA 5903.pdf` en `0062564`.

### 2.4. `imagen_07.png`: Ficha Técnica Completa de un Caso en Mantis
* **Metadatos disponibles:**
  - `Id`: `0060228` (7 dígitos con ceros iniciales, normalizado a 5 o 6 en la URL `id=60228`).
  - `Proyecto`: `CJ - Derecho publico` (otros: `[1. Solicitudes Jurídico]`, `[2. Solicitudes Conciliación]`, `[CJ - Familia]`).
  - `Fecha de envío`: `2026-03-03 14:09`.
  - `Última actualización`: `2026-10-16 16:08`.
  - `Informador`: `Natalia Prieto Camargo`.
  - `Asignada a`: `RESTREPO DUQUE VALENTINA`.
  - `Estado actual`: `aprobado` (otros estados en combos: `resuelto`, `cerrado`).
  - `Datos de Atención al Ciudadano`:
    * Solicitante: `ROSALBA PEÑARANDA OCAMPO`.
    * Cédula de Ciudadanía: `99000101`, expedida en `CALI`.
    * Contacto: Celular/Teléfono `3000000101`, Dirección `CALLE 10 NO 20-30`, Barrio `SAN FERNANDO-CALI`.
    * Turno y Sala: `Semana 5, Martes, Sala 3, Turno 1 [14:00 - 14:30]`.

---

## 3. Tipología de Notificaciones Identificada

| Tipo de Notificación | Patrón Observado en Correo / Mantis | Impacto Operativo | Necesidad de Actuación |
| :--- | :--- | :--- | :--- |
| **1. Solicitud de Cierre de Caso** | *"Hola profe, por lo anterior, solicito cierre del ID."* | Muy alto. Se repite semanalmente si el profesor no valida el cierre. | **Requiere actuación del profesor** (verificar si procede desistimiento o cierre definitivo y cambiar estado a resuelto/cerrado). |
| **2. Entrega de Documentos Jurídicos** | *"Hola profe, adjunto concepto y dp"* + adjuntos `.docx` / `.pdf` | Crítico. Requiere revisión de fondo del texto jurídico antes de radicar. | **Requiere actuación del profesor** (revisar coherencia fáctica, normativa, citas, ortografía y aprobar o solicitar corrección). |
| **3. Informe de Trámite / Sin Novedad** | *"Hola profe, de momento sin novedades, la usuaria no ha respondido..."* + captura WhatsApp | Informativo / Seguimiento. Registra cumplimiento del practicante. | **Informativo / Mero trámite** (no exige acción inmediata a menos que haya vencimiento de términos). |
| **4. Notificación de Audiencia / Conciliación** | Adjuntos como `CONSTANCIA DE NO ACUERDO...pdf`, `Solicitud de comparecencia...` | Legalmente sensible. Plazos perentorios y constancias de ley. | **Requiere actuación / verificación** (firmar constancia o avalar resultado de audiencia). |
| **5. Notas Administrativas o de Supervisores** | *"ESTE CASO ES PARA CONCEPTO + DP"*, *"El requerimiento fue devuelto..."* | Coordinación interna entre profesores y coordinadores. | **Revisión necesaria / Contexto** (condiciona la siguiente asignación). |

---

## 4. Matriz de Asistencia IA vs. Decisiones Humanas Reservadas

### Asistidas por IA (Automatizables en el MVP)
1. **Extracción y Normalización:** Identificar automáticamente el ID del caso (`0060228`), nombre del estudiante, proyecto/área y fecha a partir del asunto o cuerpo.
2. **Clasificación Semántica:** Distinguir si el mensaje es una petición de cierre, entrega de documento, aviso informativo o trámite procesal.
3. **Cruce con Historial:** Extraer antecedentes previos de Mantis para saber qué ocurrió antes (ej. "La usuaria no respondió desde hace 5 meses, la mensajería devolvió la citación").
4. **Análisis de Documentos (.docx / .pdf):** Evaluar si el borrador adjunto contiene hechos, pretensiones, fundamento de derecho y anexos requeridos.
5. **Síntesis Ejecutiva:** Redactar un resumen condensado en 4 líneas con fuentes trazables.
6. **Borrador de Retroalimentación:** Generar una propuesta de respuesta pedagógica o resolutiva para el estudiante (ej. "Autorizo el cierre del ID por desistimiento tácito conforme al protocolo...").

### Exclusivamente Humanas (Profesor Docente)
1. **Juicio Jurídico de Fondo:** Decidir si el concepto jurídico es correcto y aplicable al ordenamiento colombiano.
2. **Aprobación de Cierre o Desistimiento:** Ningún caso se cierra automáticamente en Mantis sin la venia del docente.
3. **Firma y Emisión:** Envío formal de correos al estudiante o usuario.
4. **Modificación de Estados en Mantis:** El sistema de IA es de solo lectura y genera recomendaciones, no ejecuta mutaciones directas.

---

## 5. Incógnitas e Integraciones Pendientes

1. **API de Mantis:** La versión institucional de Mantis observada (`/consultorio-juridico-app/`) podría tener la API REST (`/api/rest/issues`) o SOAP (`mantisconnect.php`) habilitada o bloqueada por el firewall de la universidad (SYRI). El MVP debe usar un adaptador desacoplado (`MantisAdapter`) con datos fidedignos simulados y conector HTTP configurable.
2. **Acceso a SharePoint:** Los expedientes enlazan a SharePoint (`icesiedu.sharepoint.com`). En esta fase se analizan los adjuntos del correo y las notas de Mantis, dejando una interfaz abierta para Microsoft Graph en fases posteriores.
3. **Autenticación Institucional:** Se contempla acceso local protegido para la demostración, con guía de migración a OAuth2/OIDC institucional.
