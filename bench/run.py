"""Uso: python run.py <motor> <archivo>... ; escribe output/<motor>/<archivo>.md y una línea JSON con métricas."""
import sys, time, pathlib, json, subprocess, os
engine, files = sys.argv[1], sys.argv[2:]
out = pathlib.Path("output")/engine; out.mkdir(parents=True, exist_ok=True)

def md_markitdown():
    from markitdown import MarkItDown
    m = MarkItDown()
    return lambda f: m.convert(f).text_content
def md_pymupdf():
    import pymupdf4llm
    return lambda f: pymupdf4llm.to_markdown(f)
def md_docling():
    from docling.document_converter import DocumentConverter
    c = DocumentConverter()
    return lambda f: c.convert(f).document.export_to_markdown()
def md_marker():
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.output import text_from_rendered
    c = PdfConverter(artifact_dict=create_model_dict())
    return lambda f: text_from_rendered(c(f))[0]
def md_mineru():
    def run(f):
        d = out/"_mineru"; subprocess.run([str(pathlib.Path(sys.executable).parent/"mineru"),"-p",f,"-o",str(d),"-b","pipeline"],check=True)
        return next(d.rglob(pathlib.Path(f).stem+".md")).read_text(encoding="utf8")
    return run

t0=time.time(); conv = globals()["md_"+engine](); init=time.time()-t0
for f in files:
    t=time.time()
    try:
        text=conv(f); err=None
        (out/(pathlib.Path(f).name+".md")).write_text(text,encoding="utf8")
    except Exception as e: err=f"{type(e).__name__}: {str(e)[:200]}"
    print(json.dumps({"engine":engine,"file":pathlib.Path(f).name,"s":round(time.time()-t,1),"init_s":round(init,1),"err":err}),flush=True)

