"""Uso: python bench/solo.py <motor> <archivo>... ; ejecuta bench/run.py del venv del motor en solitario y mide tiempo total y RAM pico (árbol de procesos). Anexa a results/solo.jsonl"""
import sys, subprocess, time, json, psutil, pathlib
engine, files = sys.argv[1], sys.argv[2:]
venv = {"markitdown":"baseline","pymupdf":"baseline","docling":"docling","marker":"marker","mineru":"mineru"}[engine]
py = str(pathlib.Path("bench")/f".venv-{venv}"/"Scripts"/"python.exe")
t0 = time.time()
p = subprocess.Popen([py, "bench/run.py", engine, *files], stdout=subprocess.PIPE, text=True)
root = psutil.Process(p.pid); peak = 0
while p.poll() is None:
    try:
        rss = sum(c.memory_info().rss for c in [root, *root.children(recursive=True)] if c.is_running())
        peak = max(peak, rss)
    except psutil.Error: pass
    time.sleep(0.5)
rec = {"engine":engine,"files":[pathlib.Path(f).name for f in files],"total_s":round(time.time()-t0,1),"peak_ram_gb":round(peak/2**30,2),
       "per_file":[json.loads(l) for l in p.stdout.read().splitlines() if l.startswith("{")]}
pathlib.Path("results").mkdir(exist_ok=True)
open("results/solo.jsonl","a",encoding="utf8").write(json.dumps(rec,ensure_ascii=False)+"\n"); print(json.dumps(rec,ensure_ascii=False))
