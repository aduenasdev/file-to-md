"""Orquestación: elige motor, convierte y aplica respaldo."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

from .config import Settings
from .engines import REGISTRY, EngineError
from .router import plan


@dataclass
class Result:
    markdown: str
    engine: str
    kind: str
    seconds: float
    warnings: list[str] = field(default_factory=list)


def convert(path: str | Path, settings: Settings | None = None, profile: str | None = None, engine: str | None = None) -> Result:
    settings = settings or Settings.from_env()
    path = Path(path)
    if not path.is_file():
        raise EngineError(f"No existe el archivo: {path}")
    kind, chain = plan(path, settings, profile, engine)
    warnings: list[str] = []
    start = time.perf_counter()
    for name in chain:
        try:
            text = REGISTRY[name].convert(path)
        except Exception as e:  # el motor falló: probamos el siguiente
            warnings.append(f"{name} falló: {type(e).__name__}: {str(e)[:200]}")
            continue
        if text and text.strip():
            return Result(text, name, kind, round(time.perf_counter() - start, 2), warnings)
        warnings.append(f"{name} devolvió contenido vacío")
    raise EngineError("No se pudo extraer contenido. " + " | ".join(warnings))
