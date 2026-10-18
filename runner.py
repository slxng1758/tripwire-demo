"""Run one (task, fault) trial: proxy + agent + test, and write runs/<run_id>/result.json.

Safety:
  * Real OpenAI calls need --really-call-api. Without it the upstream is the scripted fake (offline, free).
  * mini-swe-agent executes bash on this machine. Real runs therefore need --env docker, or --allow-local.
  * The real key is given only to the proxy process, never to the agent process.
"""
import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import uuid
from pathlib import Path

import httpx

ROOT = Path(__file__).parent
PY = sys.executable


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def load_env(path):
    env = {}
    if path.exists():
        for line in path.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip("\"'")
    return env


def wait_up(url, tries=60):
    for _ in range(tries):
        try:
            httpx.get(url, timeout=1)
            return True
        except Exception:
            time.sleep(0.25)
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    ap.add_argument("--fault", default="none")
    ap.add_argument("--params", default="{}")
    ap.add_argument("--start-after", type=int, default=0)
    ap.add_argument("--model", default="gpt-5-mini", help="model id sent to the upstream (check your OpenAI dashboard)")
    ap.add_argument("--cost-limit", type=float, default=0.5)
    ap.add_argument("--really-call-api", action="store_true")
    ap.add_argument("--env", choices=["local", "docker"], default="local")
    ap.add_argument("--allow-local", action="store_true")
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--max-calls", type=int, default=25, help="hard cap on model calls per run, enforced in the proxy")
    ap.add_argument("--run-id", default=None)
    a = ap.parse_args()

    if a.really_call_api and a.env == "local" and not a.allow_local:
        sys.exit("Refusing: real runs execute the agent's bash on this machine. Use --env docker (preferred) or pass --allow-local.")

    task = json.loads((ROOT / "tasks" / a.task / "task.json").read_text())
    run_id = a.run_id or f"{a.task}-{a.fault}-{uuid.uuid4().hex[:6]}"
    rdir = ROOT / "runs" / run_id
    work = rdir / "work"
    shutil.rmtree(rdir, ignore_errors=True)
    shutil.copytree(ROOT / "tasks" / a.task / "repo", work)
    dotenv = load_env(ROOT / ".env")

    procs = []
    try:
        fport, pport = free_port(), free_port()
        if a.really_call_api:
            upstream, ukey = dotenv.get("UPSTREAM_BASE_URL", "https://api.openai.com/v1"), dotenv.get("UPSTREAM_API_KEY", "")
            if not ukey:
                sys.exit("No UPSTREAM_API_KEY in phase2/.env")
        else:
            fenv = {**os.environ, "FAKE_SCRIPT": json.dumps(task["fake_script"])}
            procs.append(subprocess.Popen([PY, "-m", "uvicorn", "fake_upstream:app", "--port", str(fport), "--log-level", "warning"], cwd=ROOT, env=fenv))
            if not wait_up(f"http://127.0.0.1:{fport}/docs"):
                sys.exit("fake upstream did not start")
            upstream, ukey = f"http://127.0.0.1:{fport}/v1", "fake"
        penv = {**os.environ, "UPSTREAM_BASE_URL": upstream, "UPSTREAM_API_KEY": ukey, "LOG_PATH": str(rdir / "proxy_log.jsonl"), "MAX_CALLS": str(a.max_calls)}
        procs.append(subprocess.Popen([PY, "-m", "uvicorn", "proxy.app:app", "--port", str(pport), "--log-level", "warning"], cwd=ROOT, env=penv))
        if not wait_up(f"http://127.0.0.1:{pport}/_state"):
            sys.exit("proxy did not start")
        httpx.post(f"http://127.0.0.1:{pport}/_control", json={"fault": a.fault, "params": json.loads(a.params), "start_after": a.start_after, "run_id": run_id}).raise_for_status()

        aenv = {**os.environ, "PATH": f"{ROOT/'.venv/bin'}:{os.environ.get('PATH', '')}", "OPENAI_API_KEY": "proxy-only", "MSWEA_COST_TRACKING": "ignore_errors", "MSWEA_SILENT_STARTUP": "1", "MSWEA_CONFIGURED": "true", "PYTHONPATH": str(ROOT), "LITELLM_LOCAL_MODEL_COST_MAP": "True", "LITELLM_LOG": "ERROR"}
        cmd = [str(ROOT / ".venv/bin/mini"), "-t", task["prompt"], "-m", f"openai/{a.model}", "-y", "-l", str(a.cost_limit),
               "-c", "mini.yaml", "-c", f"agent.step_limit={a.max_calls}", "-c", f"model.model_kwargs.api_base=http://127.0.0.1:{pport}/v1",
               "-o", str(rdir / "trajectory.json")]
        if a.env == "docker":
            # container: no network, 1 GB / 1 CPU, task folder mounted at /work; model calls happen on the host
            (rdir / "env.yaml").write_text(
                "model:\n  model_class: tripwire_agent.model.TripwireModel\n"
                "environment:\n  environment_class: tripwire_agent.env.TripwireDockerEnv\n  image: tripwire-task\n  cwd: /work\n"
                f"  run_args: ['--rm', '--network', 'none', '--memory', '1g', '--cpus', '1', '-v', '{work.resolve()}:/work']\n"
                "agent:\n  system_template: |\n"
                "    You are a helpful assistant that can interact with a computer.\n"
                "    You have two tools: `bash` (run shell commands) and `run_tests` (run the project's test suite; no arguments).\n"
                "    pytest is NOT available in bash. Use the `run_tests` tool to run the tests and to check your fix before you submit.\n")
            os.system(f"chmod -R a+rwX '{work}'")  # the container's unprivileged user must be able to edit the mounted files
            cmd += ["-c", str(rdir / "env.yaml")]
        else:
            cmd += ["-c", "environment.environment_class=local"]
        t0 = time.time()
        try:
            p = subprocess.run(cmd, cwd=work, env=aenv, capture_output=True, text=True, timeout=a.timeout, input="\n" * 5)  # Enter quits the interactive 'Agent wants to finish' prompt
            agent_rc, agent_out = p.returncode, (p.stdout + p.stderr)[-4000:]
        except subprocess.TimeoutExpired:
            agent_rc, agent_out = -1, "agent timed out"
        elapsed = time.time() - t0
        state = httpx.get(f"http://127.0.0.1:{pport}/_state").json()
        t = subprocess.run(task["test_cmd"], shell=True, cwd=work, capture_output=True, text=True, timeout=120, env=aenv)
        res = {"run_id": run_id, "task": a.task, "fault": a.fault, "params": json.loads(a.params), "model": a.model,
               "real_api": a.really_call_api, "agent_returncode": agent_rc, "elapsed_s": round(elapsed, 1),
               "proxy_calls": state["calls"], "fault_fired": state["fired"], "tests_passed": t.returncode == 0,
               "test_output_tail": (t.stdout + t.stderr)[-800:], "agent_output_tail": agent_out[-1500:]}
        (rdir / "result.json").write_text(json.dumps(res, indent=1))
        print(json.dumps({k: res[k] for k in ("run_id", "fault", "proxy_calls", "fault_fired", "tests_passed", "agent_returncode")}))
    finally:
        for pr in procs:
            pr.terminate()


if __name__ == "__main__":
    main()
