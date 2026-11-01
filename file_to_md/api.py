"""API HTTP (FastAPI)."""
from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse

from . import __version__
from .config import Settings
from .engines import REGISTRY, EngineError
from .router import PROFILES
from .service import convert

settings = Settings.from_env()
app = FastAPI(title="file-to-md", version=__version__)
_slots = asyncio.Semaphore(settings.max_concurrency)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": __version__}


@app.get("/engines")
def engines() -> dict:
    return {
        "profile": settings.profile,
        "profiles": PROFILES,
        "engines": {
            n: {"enabled": settings.enabled.get(n, False), "installed": e.available(), "formats": sorted(e.formats)}
            for n, e in REGISTRY.items()
        },
    }


@app.post("/convert")
async def convert_file(
    file: UploadFile = File(...),
    profile: str | None = Form(None),
    engine: str | None = Form(None),
    format: str = Form("json"),
):
    suffix = Path(file.filename or "").suffix
    limit = settings.max_upload_mb * 1024 * 1024
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / f"upload{suffix}"
        size = 0
        with dest.open("wb") as fh:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > limit:
                    raise HTTPException(413, f"El archivo supera {settings.max_upload_mb} MB")
                fh.write(chunk)
        async with _slots:
            try:
                res = await asyncio.wait_for(
                    asyncio.to_thread(convert, dest, settings, profile, engine), settings.timeout_s
                )
            except asyncio.TimeoutError:
                raise HTTPException(504, "Tiempo de conversión agotado")
            except EngineError as e:
                raise HTTPException(422, str(e))
    if format == "md":
        return PlainTextResponse(res.markdown, media_type="text/markdown", headers={"X-Engine": res.engine})
    return {"markdown": res.markdown, "engine": res.engine, "kind": res.kind, "seconds": res.seconds, "warnings": res.warnings}
