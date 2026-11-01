# Ejemplos

Genera documentos de prueba (PDF con tabla, DOCX, imagen, foto con ruido, PDF escaneado):

```bash
pip install -e ".[light,dev]" pymupdf
python examples/generate_samples.py        # → examples/samples/ (ignorado por git)
```

CLI:

```bash
file-to-md convert examples/samples/<archivo>.pdf
file-to-md convert examples/samples/<archivo>.png --profile quality   # requiere extras marker/docling
```

API:

```bash
file-to-md serve &
curl -F file=@examples/samples/<archivo>.docx http://localhost:8000/convert
```
