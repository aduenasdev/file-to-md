from pathlib import Path

import pymupdf
import pytest

from file_to_md.config import Settings
from file_to_md.engines import EngineError
from file_to_md.router import plan
from file_to_md.service import convert


@pytest.fixture
def settings():
    return Settings.from_env()


@pytest.fixture
def text_pdf(tmp_path: Path) -> Path:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 100), "Informe de prueba. " * 10)
    p = tmp_path / "a.pdf"
    doc.save(p)
    return p


@pytest.fixture
def scanned_pdf(tmp_path: Path) -> Path:
    doc = pymupdf.open()
    doc.new_page()
    p = tmp_path / "b.pdf"
    doc.save(p)
    return p


def test_text_pdf_auto_prefers_light_engine(text_pdf, settings):
    kind, chain = plan(text_pdf, settings, "auto")
    assert kind == "pdf_text" and chain[0] == "pymupdf"


def test_scanned_pdf_auto_prefers_quality_engine(scanned_pdf, settings):
    settings.enabled = {"marker": True, "docling": True, "pymupdf": True, "markitdown": True}
    from file_to_md import router

    router.REGISTRY["marker"].available = lambda: True
    kind, chain = plan(scanned_pdf, settings, "auto")
    assert kind == "scanned" and chain[0] == "marker"


def test_disabled_engine_is_skipped(text_pdf, settings):
    settings.enabled["pymupdf"] = False
    try:
        _, chain = plan(text_pdf, settings, "light")
    except EngineError:
        return
    assert "pymupdf" not in chain


def test_unknown_profile_and_engine(text_pdf, settings):
    with pytest.raises(EngineError):
        plan(text_pdf, settings, "x")
    with pytest.raises(EngineError):
        plan(text_pdf, settings, engine="nope")


def test_convert_text_pdf(text_pdf, settings):
    r = convert(text_pdf, settings, "light")
    assert "Informe de prueba" in r.markdown and r.engine == "pymupdf"


def test_missing_file(settings):
    with pytest.raises(EngineError):
        convert("no-existe.pdf", settings)
