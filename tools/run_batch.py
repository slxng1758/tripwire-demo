"""Run a batch of (task x condition x repeat) trials via runner.py, resumable. Real API calls, Docker only.
usage: run_batch.py --prefix base --fault none [--params JSON] [--repeats 3] [--tasks t001,t002|all] [--model M]
"""
import argparse, csv, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("--prefix", required=True)
ap.add_argument("--fault", default="none")
ap.add_argument("--params", default="{}")
ap.add_argument("--repeats", type=int, default=3)
ap.add_argument("--tasks", default="all")
ap.add_argument("--model", default="gpt-5.4-mini")
ap.add_argument("--max-calls", type=int, default=25)
a = ap.parse_args()
tasks = sorted(p.name for p in (ROOT / "tasks").glob("t*")) if a.tasks == "all" else a.tasks.split(",")
for r in range(1, a.repeats + 1):
    for t in tasks:
        rid = f"{a.prefix}-{t}-r{r}"
        if (ROOT / "runs" / rid / "result.json").exists():
            continue
        subprocess.run([sys.executable, str(ROOT / "runner.py"), "--task", t, "--fault", a.fault, "--params", a.params, "--env", "docker",
                        "--really-call-api", "--model", a.model, "--max-calls", str(a.max_calls), "--run-id", rid, "--timeout", "420"], cwd=ROOT)
rows = []
for t in tasks:
    for r in range(1, a.repeats + 1):
        f = ROOT / "runs" / f"{a.prefix}-{t}-r{r}" / "result.json"
        if not f.exists():
            continue
        res = json.loads(f.read_text())
        names, claims = [], False
        for l in (ROOT / "runs" / res["run_id"] / "proxy_log.jsonl").read_text().splitlines():
            x = json.loads(l)
            if "upstream_response" not in x:
                continue
            for tc in (x["upstream_response"].get("choices", [{}])[0].get("message", {}).get("tool_calls") or []):
                names.append(tc["function"]["name"])
        rows.append({"run_id": res["run_id"], "task": t, "fault": res["fault"], "tests_passed": res["tests_passed"], "fault_fired": res["fault_fired"],
                     "model_calls": res["proxy_calls"], "run_tests_calls": names.count("run_tests"), "bash_calls": names.count("bash"),
                     "submitted": any(n == "bash" for n in names) and "COMPLETE_TASK" in json.dumps(json.loads(f.read_text()).get("agent_output_tail", ""))})
out = ROOT / "runs" / f"{a.prefix}_summary.csv"
if rows:
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print("summary:", out, len(rows), "runs;", sum(r["tests_passed"] for r in rows), "passed")
