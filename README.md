# file-to-md

Convierte PDF, DOCX, PPTX, XLSX/XLS, HTML e imágenes a Markdown. Un **router** elige por documento el motor
adecuado: el más ligero que dé calidad aceptable, y solo escala a motores con OCR/IA cuando hace falta.

- Motores: PyMuPDF4LLM, MarkItDown, Docling, Marker (imports perezosos: solo se cargan si se usan).
- Interfaces: CLI, API REST (FastAPI) y Docker.
- Licencia: [Apache 2.0](LICENSE).

## Cómo decide

Cadena de motores (el primero disponible gana; el resto es respaldo si falla o devuelve vacío):

| Tipo detectado | `auto` (defecto) | `quality` | `balanced` | `light` |
|---|---|---|---|---|
| PDF con texto | pymupdf → marker → docling | marker → docling → pymupdf | docling → pymupdf | pymupdf → docling |
| PDF escaneado / imagen | marker → docling | marker → docling | docling → marker | docling → marker |
| Office | markitdown → docling | docling → markitdown | markitdown → docling | markitdown → docling |
| HTML y otros | markitdown → docling | markitdown → docling | markitdown → docling | markitdown → docling |

Un PDF es "escaneado" si tiene menos de `SCANNED_CHARS_PER_PAGE` caracteres por página. Los PDF protegidos con
contraseña devuelven error (422 en la API).

## Instalación

```bash
pip install -e ".[light]"        # pymupdf4llm + markitdown (CPU, ~0,3 GB RAM)
pip install -e ".[all]"          # + docling + marker (OCR/IA, ~2 GB RAM)
```

Marker usa OCR basado en `llama-server` (llama.cpp): debe estar en el `PATH` o definirse
`LLAMA_CPP_BINARY=/ruta/llama-server`.

## Uso

```bash
file-to-md convert documento.pdf -o salida.md          # perfil auto
file-to-md convert factura.png --profile quality
file-to-md engines                                      # motores disponibles
file-to-md serve --port 8000                            # API
```

```bash
curl -F file=@documento.pdf -F profile=auto http://localhost:8000/convert              # JSON
curl -F file=@documento.pdf -F format=md http://localhost:8000/convert > salida.md      # Markdown
```

Endpoints: `GET /health`, `GET /engines`, `POST /convert` (`file`, `profile`, `engine`, `format=json|md`).

## Docker

```bash
docker compose up --build                     # EXTRAS=light,docling por defecto
docker build --build-arg EXTRAS=all -t file-to-md .
```

## Configuración (variables de entorno, ver `.env.example`)

`PROFILE`, `DEVICE`, `ENGINE_<PYMUPDF|MARKITDOWN|DOCLING|MARKER>_ENABLED`, `MAX_UPLOAD_MB`, `MAX_CONCURRENCY`,
`TIMEOUT_S`, `THREADS`, `SCANNED_CHARS_PER_PAGE`.

## Probar el proyecto

```bash
pip install -e ".[light,dev]"
python examples/generate_samples.py     # crea examples/samples/
pytest
```

Más en [examples/README.md](examples/README.md). Tiempos y recursos estimados: [docs/benchmark.md](docs/benchmark.md).

## Licencia

Apache License 2.0. Ver [LICENSE](LICENSE).
