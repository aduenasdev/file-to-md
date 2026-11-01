"""Selección de motor según tipo de documento y perfil.

Perfiles:
  quality   máxima calidad, sin importar el coste.
  balanced  buena calidad con coste moderado.
  light     mínimo consumo de recursos.
  auto      calidad máxima solo donde aporta diferencia (documentos escaneados e
            imágenes); en el resto usa el motor ligero, cuya calidad es equivalente.
"""
from __future__ import annotations

from pathlib import Path

from .config import Settings
from .engines import REGISTRY, EngineError

PROFILES = ("auto", "quality", "balanced", "light")
IMAGE_EXT = {"png", "jpg", "jpeg", "tif", "tiff", "bmp", "webp"}

# Orden de preferencia por tipo de documento y perfil (el primero disponible gana;
# el resto actúa como respaldo si falla o devuelve vacío).
CHAINS: dict[str, dict[str, list[str]]] = {
    "pdf_text": {
        "quality": ["marker", "docling", "pymupdf"],
        "balanced": ["docling", "pymupdf"],
        "light": ["pymupdf", "docling"],
        "auto": ["pymupdf", "marker", "docling"],
    },
    "scanned": {
        "quality": ["marker", "docling"],
        "balanced": ["docling", "marker"],
        "light": ["docling", "marker"],
        "auto": ["marker", "docling"],
    },
    "office": {
        "quality": ["docling", "markitdown"],
        "balanced": ["markitdown", "docling"],
        "light": ["markitdown", "docling"],
        "auto": ["markitdown", "docling"],
    },
    "other": {p: ["markitdown", "docling"] for p in PROFILES},
}


def extension(path: Path) -> str:
    return path.suffix.lower().lstrip(".")


def pdf_is_scanned(path: Path, min_chars: int) -> bool:
    """True si el PDF casi no tiene capa de texto. Lanza EngineError si está protegido."""
    import pymupdf

    with pymupdf.open(path) as doc:
        if doc.needs_pass:
            raise EngineError("PDF protegido con contraseña")
        pages = min(len(doc), 5)
        if pages == 0:
            return False
        chars = sum(len(doc[i].get_text().strip()) for i in range(pages))
    return chars / pages < min_chars


def classify(path: Path, settings: Settings) -> str:
    ext = extension(path)
    if ext == "pdf":
        return "scanned" if pdf_is_scanned(path, settings.scanned_chars_per_page) else "pdf_text"
    if ext in IMAGE_EXT:
        return "scanned"
    if ext in {"docx", "pptx", "xlsx"}:
        return "office"
    return "other"


def plan(path: Path, settings: Settings, profile: str | None = None, engine: str | None = None) -> tuple[str, list[str]]:
    """Devuelve (tipo, lista ordenada de motores a intentar)."""
    ext = extension(path)
    kind = classify(path, settings)
    if engine:
        if engine not in REGISTRY:
            raise EngineError(f"Motor desconocido: {engine}")
        names = [engine]
    else:
        profile = (profile or settings.profile).lower()
        if profile not in PROFILES:
            raise EngineError(f"Perfil desconocido: {profile}")
        names = CHAINS[kind][profile]
    usable = [
        n for n in names
        if settings.enabled.get(n, False) and ext in REGISTRY[n].formats and REGISTRY[n].available()
    ]
    if not usable:
        raise EngineError(f"Ningún motor disponible para .{ext} ({kind}). Instala los extras necesarios o revisa ENGINE_*_ENABLED.")
    return kind, usable
