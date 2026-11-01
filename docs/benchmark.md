# Recursos y tiempos estimados

Medidas de cada motor **ejecutado en solitario**, en CPU sin GPU (Intel Core 5 120U, 16 GB RAM, con ~3,7 GB
libres durante las pruebas, así que los valores son algo pesimistas). Son órdenes de magnitud para dimensionar;
repítelos en tu hardware con `bench/solo.py`.

## Por motor

| Motor | RAM pico | Arranque en frío | Texto nativo | Escaneado / imagen (OCR) |
|---|---|---|---|---|
| MarkItDown | ~0,15 GB | ~30 s (primer uso) | DOCX/XLSX/HTML: < 2 s por archivo | no (imagen → vacío) |
| PyMuPDF4LLM | ~0,3 GB | ~12 s | ~1 s/página (p. ej. 18 págs ≈ 23 s) | no |
| Marker | ~2 GB | ~30 s | ~8 s/pág (modelos calientes); 1.ª pág ~40 s | ~40 s por imagen limpia; 3–5 min por página escaneada o foto ruidosa |
| Docling | ~1,8 GB | ~70 s | 1–4 min/pág en CPU (muy variable) | ~1,5–2,5 min por imagen/página |
| MinerU (descartado) | ~1,7 GB | CLI: ~100 s por archivo | ~100 s/pág | ~140 s/pág |

## Estimación de tiempo por documento (perfil `auto`, CPU)

| Documento | Motor elegido | Tiempo estimado |
|---|---|---|
| DOCX / XLSX / HTML | markitdown | 1–3 s |
| PDF con texto, N páginas | pymupdf | ~1 s × N (+12 s la primera vez) |
| Imagen con texto | marker | ~40 s – 6 min según ruido |
| PDF escaneado, N páginas | marker | ~1–4 min × N |

Con GPU (`DEVICE=cuda`) Marker y Docling bajan en uno o dos órdenes de magnitud. Los tiempos de arranque se pagan
una vez por proceso (en la API, al primer uso de cada motor).

## Calidad observada y razón de la cadena

- **PDF con texto**: PyMuPDF4LLM da calidad aceptable con ~1 % del coste de los motores IA → primera opción.
- **Escaneados e imágenes**: Marker fue el mejor (orden, espacios y tablas correctos); Docling de respaldo.
- **Office/HTML**: MarkItDown es suficiente y casi instantáneo; Docling mejora tablas complejas (`quality`).
- MinerU tuvo calidad alta pero coste y arranque (CLI por archivo) poco prácticos para un servicio.

## Dimensionado

- Solo `light`: 1 vCPU y 512 MB.
- `auto` con Marker/Docling: ≥ 4 GB RAM por proceso y `MAX_CONCURRENCY=1` por cada 2–3 GB.
- Para volumen de escaneados, usar GPU o colas con varios contenedores.

## Reproducir

```bash
python bench/solo.py <motor> <archivo>...   # usa bench/.venv-<motor>; resultados en results/solo.jsonl
```
