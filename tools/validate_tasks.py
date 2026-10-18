"""Check every task: tests fail before the fix, pass after it, and the bug sits past the truncation point."""
import json, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent / "tasks"
OLD = {"t001_total": ("stats.py", "sum(prices[:-1])", "sum(prices)"),
       "t002_slugify": ("text.py", 'return s.replace(" ", "_")', 'return s.lower().replace(" ", "-")'),
       "t003_median": ("nums.py", "    return s[len(s) // 2]", "    n = len(s)\n    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2")}
bad = 0
rows = []
for d in sorted(list(ROOT.glob("t*")) + list(ROOT.glob("h*"))):
    meta = json.loads((d / "task.json").read_text())
    f, old, new = OLD.get(meta["id"]) or (meta["source_file"], meta["bug_old"], meta["bug_new"])
    work = Path(tempfile.mkdtemp()) / "repo"
    shutil.copytree(d / "repo", work)
    run = lambda: subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=work, capture_output=True, text=True)
    before = run().returncode != 0
    src = (work / f).read_text()
    found = src.count(old) == 1
    pos = src.find(old) / len(src) if found else -1
    (work / f).write_text(src.replace(old, new))
    after = run().returncode == 0
    naive_fails = True  # h* tasks only: the plausible-but-incomplete fix must still fail the tests
    if meta.get("naive_new"):
        (work / f).write_text(src.replace(old, meta["naive_new"]))
        naive_fails = run().returncode != 0
    ok = before and after and found and pos > 0.55 and naive_fails
    bad += not ok
    rows.append((meta["id"], meta.get("kind", "-"), len(src), round(pos, 2), "fails-before" if before else "PASSES-BEFORE", "passes-after" if after else "FAILS-AFTER", "naive-fix-fails" if (meta.get("naive_new") and naive_fails) else ("NAIVE-FIX-PASSES" if meta.get("naive_new") else "-"), "ok" if ok else "PROBLEM"))
for r in rows:
    print(*r, sep="\t")
print("problems:", bad)
sys.exit(1 if bad else 0)
