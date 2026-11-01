"""Configuración por variables de entorno (ver .env.example)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field

ENGINES = ("pymupdf", "markitdown", "docling", "marker")


def _bool(name: str, default: bool) -> bool:
    v = os.environ.get(name)
    return default if v is None else v.strip().lower() in ("1", "true", "yes", "on")


def _int(name: str, default: int) -> int:
    return int(os.environ.get(name, default))


@dataclass
class Settings:
    # auto | quality | balanced | light
    profile: str = "auto"
    # cpu | cuda | auto (los motores con IA lo respetan)
    device: str = "auto"
    enabled: dict[str, bool] = field(default_factory=dict)
    max_upload_mb: int = 50
    max_concurrency: int = 1
    timeout_s: int = 1800
    threads: int = 0  # 0 = sin límite
    # Páginas con menos de N caracteres de texto se consideran escaneadas
    scanned_chars_per_page: int = 40

    @classmethod
    def from_env(cls) -> "Settings":
        s = cls(
            profile=os.environ.get("PROFILE", "auto").lower(),
            device=os.environ.get("DEVICE", "auto").lower(),
            enabled={e: _bool(f"ENGINE_{e.upper()}_ENABLED", True) for e in ENGINES},
            max_upload_mb=_int("MAX_UPLOAD_MB", 50),
            max_concurrency=max(1, _int("MAX_CONCURRENCY", 1)),
            timeout_s=_int("TIMEOUT_S", 1800),
            threads=_int("THREADS", 0),
            scanned_chars_per_page=_int("SCANNED_CHARS_PER_PAGE", 40),
        )
        if s.threads > 0:
            for var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "TORCH_NUM_THREADS"):
                os.environ.setdefault(var, str(s.threads))
        if s.device == "cpu":
            os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
        return s
