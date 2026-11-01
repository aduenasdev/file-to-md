import pymupdf
from fastapi.testclient import TestClient

from file_to_md.api import app

client = TestClient(app)


def _pdf_bytes() -> bytes:
    doc = pymupdf.open()
    doc.new_page().insert_text((72, 100), "Hola mundo desde la API. " * 8)
    return doc.tobytes()


def test_health_and_engines():
    assert client.get("/health").json()["status"] == "ok"
    assert "pymupdf" in client.get("/engines").json()["engines"]


def test_convert_pdf():
    r = client.post("/convert", files={"file": ("a.pdf", _pdf_bytes())}, data={"profile": "light"})
    assert r.status_code == 200 and "Hola mundo" in r.json()["markdown"]


def test_convert_md_format():
    r = client.post("/convert", files={"file": ("a.pdf", _pdf_bytes())}, data={"engine": "pymupdf", "format": "md"})
    assert r.headers["content-type"].startswith("text/markdown") and r.headers["x-engine"] == "pymupdf"


def test_unsupported_returns_422():
    r = client.post("/convert", files={"file": ("a.xyz", b"data")})
    assert r.status_code == 422
