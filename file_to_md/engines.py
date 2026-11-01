"""Motores de conversión. Cada uno importa sus dependencias solo al usarse."""
from __future__ import annotations

import importlib.util
from abc import ABC, abstractmethod
from pathlib import Path


class EngineError(Exception):
    pass


class Engine(ABC):
    name: str
    #: extensiones (sin punto) que sabe convertir
    formats: frozenset[str]
    #: módulo cuya presencia indica que el motor está instalado
    module: str

    def available(self) -> bool:
        return importlib.util.find_spec(self.module) is not None

    @abstractmethod
    def convert(self, path: Path) -> str: ...


class PyMuPDF(Engine):
    name, module = "pymupdf", "pymupdf4llm"
    formats = frozenset({"pdf"})

    def convert(self, path: Path) -> str:
        import pymupdf4llm

        md = pymupdf4llm.to_markdown(str(path))
        if md.strip():
            return md
        import pymupdf

        with pymupdf.open(str(path)) as doc:
            pages = (p.get_text().strip() for p in doc)
            return "\n\n".join(t for t in pages if t)


class MarkItDownEngine(Engine):
    name, module = "markitdown", "markitdown"
    formats = frozenset({"docx", "pptx", "xlsx", "xls", "html", "htm", "csv", "json", "xml", "txt"})

    def __init__(self) -> None:
        self._md = None

    def convert(self, path: Path) -> str:
        if self._md is None:
            from markitdown import MarkItDown

            self._md = MarkItDown()
        return self._md.convert(str(path)).text_content


class Docling(Engine):
    name, module = "docling", "docling"
    formats = frozenset({"pdf", "docx", "pptx", "xlsx", "html", "htm", "png", "jpg", "jpeg", "tif", "tiff", "bmp", "webp"})

    def __init__(self) -> None:
        self._conv = None

    def convert(self, path: Path) -> str:
        if self._conv is None:
            from docling.document_converter import DocumentConverter

            self._conv = DocumentConverter()
        return self._conv.convert(str(path)).document.export_to_markdown()


class Marker(Engine):
    """Máxima calidad en PDF e imágenes. En CPU el OCR requiere `llama-server`
    (llama.cpp) en el PATH o indicado en LLAMA_CPP_BINARY."""

    name, module = "marker", "marker"
    formats = frozenset({"pdf", "png", "jpg", "jpeg", "tif", "tiff", "bmp", "webp"})

    def __init__(self) -> None:
        self._conv = None

    def convert(self, path: Path) -> str:
        if self._conv is None:
            from marker.converters.pdf import PdfConverter
            from marker.models import create_model_dict

            self._conv = PdfConverter(artifact_dict=create_model_dict())
        from marker.output import text_from_rendered

        return text_from_rendered(self._conv(str(path)))[0]


REGISTRY: dict[str, Engine] = {e.name: e for e in (PyMuPDF(), MarkItDownEngine(), Docling(), Marker())}
