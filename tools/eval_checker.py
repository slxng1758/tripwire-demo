"""Replay proxy/checks.py over logged runs (offline, free). Per run: was anything flagged on ANY call, and which check.
Truth = the run's fault (result.json) and whether it fired. Clean runs (fault none) give the false-positive rate.
Usage: eval_checker.py <prefix> [<prefix> ...]"""
import json, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from proxy import checks

for prefix in sys.argv[1:]:
    rows = []
    for d in sorted((ROOT / "runs").glob(f"{prefix}-*")):
        if not (d / "result.json").exists():
            continue
        res = json.loads((d / "result.json").read_text())
        flags, first = Counter(), None
        for l in (d / "proxy_log.jsonl").read_text().splitlines():
            x = json.loads(l)
            if "upstream_response" not in x:
                continue
            sent = x.get("sent") or x["request"]  # what actually went to the model
            f = checks.run_all(sent, x.get("requested_model"), x["upstream_response"])
            for c in {g["check"] for g in f}:
                flags[c] += 1
                first = first or x["call"]
        rows.append((res["task"], res["fault"], res["fault_fired"] > 0, dict(flags), first))
    n = len(rows)
    fired = [r for r in rows if r[2]]
    fault = rows[0][1] if rows else "?"
    print(f"{prefix} (fault={fault}): {n} runs, fault fired in {len(fired)}")
    if fault == "none":
        print(f"  false positives: {sum(1 for r in rows if r[3])}/{n} runs flagged", {k for r in rows for k in r[3]} or "")
    else:
        print(f"  caught (any flag) in fired runs: {sum(1 for r in fired if r[3])}/{len(fired)}; by check: {dict(Counter(k for r in fired for k in r[3]))}")
        miss = [r[0] for r in fired if not r[3]]
        print("  missed:", ", ".join(miss) or "none")
