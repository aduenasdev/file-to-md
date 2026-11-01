"""CLI: python -m file_to_md convert <archivo>... [-o DIR] [--profile P] [--engine E]
        python -m file_to_md engines
        python -m file_to_md serve [--host H] [--port N]"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import Settings
from .engines import REGISTRY, EngineError
from .router import PROFILES
from .service import convert


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="file-to-md")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("convert", help="Convierte archivos a Markdown")
    c.add_argument("files", nargs="+")
    c.add_argument("-o", "--out", help="Carpeta de salida (por defecto, stdout)")
    c.add_argument("--profile", choices=PROFILES)
    c.add_argument("--engine", choices=sorted(REGISTRY))
    sub.add_parser("engines", help="Lista motores instalados")
    s = sub.add_parser("serve", help="Arranca la API HTTP")
    s.add_argument("--host", default="0.0.0.0")
    s.add_argument("--port", type=int, default=8000)
    a = ap.parse_args(argv)
    settings = Settings.from_env()

    if a.cmd == "engines":
        for n, e in REGISTRY.items():
            print(f"{n:11} instalado={e.available()!s:5} activo={settings.enabled.get(n)!s:5} {','.join(sorted(e.formats))}")
        return 0
    if a.cmd == "serve":
        import uvicorn

        uvicorn.run("file_to_md.api:app", host=a.host, port=a.port)
        return 0

    rc = 0
    out = Path(a.out) if a.out else None
    if out:
        out.mkdir(parents=True, exist_ok=True)
    for f in a.files:
        try:
            r = convert(f, settings, a.profile, a.engine)
        except EngineError as e:
            print(f"ERROR {f}: {e}", file=sys.stderr)
            rc = 1
            continue
        print(f"{f}: motor={r.engine} tipo={r.kind} {r.seconds}s", file=sys.stderr)
        for w in r.warnings:
            print(f"  aviso: {w}", file=sys.stderr)
        if out:
            (out / (Path(f).name + ".md")).write_text(r.markdown, encoding="utf-8")
        else:
            print(r.markdown)
    return rc


if __name__ == "__main__":
    sys.exit(main())
