# Resultados de la comparativa (corpus sintético, CPU Intel Core 5 120U, 16 GB, sin GPU)

Fecha: 2026-11-01. Versiones: Docling 2.145, Marker 2.1 (Surya 2.5, vía llama.cpp b12032), MinerU 3.4.5 (backend pipeline), MarkItDown 0.1.8, PyMuPDF4LLM 2.0.
Tiempos medidos con otros procesos compitiendo por CPU (MinerU y Marker a la vez en parte): son pesimistas.

| Archivo | MarkItDown | PyMuPDF4LLM | Docling | Marker | MinerU |
|---|---|---|---|---|---|
| 01 PDF nativo + tabla | texto, tabla sin formato (1 s) | **OK** (1 s) | orden roto: título y tabla al final (95 s) | **OK perfecto** (133 s) | OK, tabla en HTML (190 s) |
| 02 DOCX con tabla | OK | n/d | **OK** (0,2 s) | falla (falta weasyprint) | OK, tabla HTML (70 s) |
| 03 PNG texto | vacío | vacío | OK, párrafo unido (61 s) | **OK perfecto** (41 s) | OK (219 s) |
| 04 foto ruidosa | vacío | vacío | título invertido (106 s) | **OK** (364 s; negritas espurias) | espacios perdidos (139 s) |
| 05 PDF escaneado | vacío | vacío | título invertido, espacios (96 s) | **OK** (271 s) | espacios perdidos (173 s) |

Notas: MarkItDown y PyMuPDF4LLM no hacen OCR (solo línea base). Marker requiere el binario `llama-server` (llama.cpp) para OCR en CPU; MinerU 4.x cambió a CLI de "document center", se usa la 3.4.5.

## Conclusión provisional
1. **Marker** – máxima calidad en PDF nativo e imágenes/escaneados (tablas en Markdown real, espacios y orden correctos). Lento en CPU.
2. **MinerU (pipeline)** – calidad alta con OCR, tablas en HTML, pierde algún espacio en escaneos. Soporta DOCX. Muy pesado.
3. **Docling** – bueno en DOCX/tablas Office y OCR razonable; orden de lectura erróneo en PDF nativo simple.
Rápidos sin IA (para formatos nativos): PyMuPDF4LLM (PDF con texto), MarkItDown (DOCX/XLSX/HTML).

Pendiente: ejecutar el corpus público (30 archivos) para confirmar, sobre todo xls/xlsx/html/pdf complejos.
