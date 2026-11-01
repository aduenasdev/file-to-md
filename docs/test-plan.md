# Plan de pruebas

Candidatas: 1) MarkItDown  2) Docling  3) Marker  4) PyMuPDF4LLM (+Tesseract/RapidOCR)  5) MinerU (opcional)
Corpus: PDF nativo, PDF escaneado, PDF con tablas, DOCX con tablas/imágenes, imágenes (foto/captura).
Métricas: calidad (tablas, orden, títulos), OCR, tiempo/página, RAM/GPU, tamaño de imagen Docker, licencia, facilidad de API.

## Formatos y estrategia (actualizado)
| Formato | Estrategia | Candidatas |
|---|---|---|
| PDF nativo / escaneado | Motores con IA (máxima calidad, CPU) | Marker, Docling, MinerU (+ PyMuPDF4LLM línea base) |
| Imágenes (png/jpg) | OCR/VLM | Docling, Marker/Surya, MinerU |
| DOCX | Librería directa o motor IA | MarkItDown (mammoth), Docling |
| XLSX / XLS | Librería directa (sin IA) | MarkItDown (openpyxl/xlrd+pandas), Docling (xlsx) |
| HTML | Librería directa (sin IA) | html-to-markdown, markdownify, trafilatura, MarkItDown |

Corpus público (data/samples-public/<tipo>/NN_descripcion.ext): pdf 10, docx 4, xlsx 2, xls 4, html 10.
Corpus sintético (data/samples): 5 casos con verdad conocida.

## Diseño de configuración (.env)
Cada motor se activa/desactiva y se parametriza por entorno (ENGINE_<X>_ENABLED, DEVICE=cpu|cuda|auto, límites de hilos/RAM, ENGINE_PRIORITY por tipo de archivo) y la API permite elegir motor por petición entre los habilitados. Solo se mantendrán los 3 mejores según resultados.
