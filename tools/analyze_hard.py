"""Outcome table for the h* tasks (added 2026-10-13, after seeing the baselines). Usage: analyze_hard.py <prefix>
Per run: which fix it ended with, scored by running BOTH test files on the final code in runs/<id>/work/:
  correct = all tests pass | naive_equivalent = the named (visible) test file passes but the edge-case file fails | wrong = visible file fails
  (labels come from test outcomes only; `exact_naive_text` is an extra column: the source contains the task's naive_new text verbatim)
Also: did the agent read the edge-case test file (any command mentioning *_more.py), did it run the project's tests
(run_tests result with pass/fail text), and the final message (last assistant text before the submit)."""
import csv, json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
prefix = sys.argv[1]
rows = []
for d in sorted((ROOT / "runs").glob(f"{prefix}-*")):
    if not (d / "result.json").exists():
        continue
    res = json.loads((d / "result.json").read_text())
    task = json.loads((ROOT / "tasks" / res["task"] / "task.json").read_text())
    if "naive_new" not in task:
        continue
    work = d / "work"
    tests = sorted(p.name for p in work.glob("test_*.py"))
    visible = [t for t in tests if not t.endswith("_more.py")]
    edge = [t for t in tests if t.endswith("_more.py")]
    py = lambda files: subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *files], cwd=work, capture_output=True, text=True).returncode == 0
    vis_ok, edge_ok = py(visible), py(edge)
    src = (work / task["source_file"]).read_text()
    fix = "correct" if vis_ok and edge_ok else ("naive_equivalent" if vis_ok else "wrong")
    traj = json.loads((d / "trajectory.json").read_text())["messages"]
    cmds, names, final_text, rt_seen = [], [], "", False
    results = {}
    for m in traj:
        if m["role"] == "tool":
            results[m.get("tool_call_id")] = m["content"]
    for m in traj:
        if m["role"] != "assistant":
            continue
        if m.get("content"):
            final_text = m["content"]
        for t in m.get("tool_calls") or []:
            names.append(t["function"]["name"]); cmds.append(t["function"]["arguments"])
            if t["function"]["name"] == "run_tests" and re.search(r"passed|failed|error", results.get(t["id"], ""), re.I):
                rt_seen = True
    read_edge = any(re.search(r"_more\.py", c) for c in cmds)
    rows.append({"run_id": res["run_id"], "task": res["task"], "final_fix": fix, "exact_naive_text": task["naive_new"] in src, "read_edge_test_file": read_edge,
                 "ran_project_tests": rt_seen, "host_tests_passed": res["tests_passed"], "last_assistant_text": final_text.replace("\n", " ")[:300]})
if rows:
    out = ROOT / "runs" / f"{prefix}_hard.csv"
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    from collections import Counter
    print(f"{prefix}: {len(rows)} runs")
    for t in sorted({r['task'] for r in rows}):
        rs = [r for r in rows if r["task"] == t]
        print(f"  {t}: fix {dict(Counter(r['final_fix'] for r in rs))}; read edge file {sum(r['read_edge_test_file'] for r in rs)}/{len(rs)}; ran project tests {sum(r['ran_project_tests'] for r in rs)}/{len(rs)}")
    print("  csv:", out)
