"""OpenAI-compatible fault-injection proxy.

Sits between a coding agent and an upstream model. Forwards /v1/chat/completions (non-streaming) and
injects ONE configured fault, then logs every exchange to a JSONL file so runs can be judged later.

Env:
  UPSTREAM_BASE_URL   e.g. https://openrouter.ai/api/v1
  UPSTREAM_API_KEY    key for the upstream
  LOG_PATH            JSONL log file (default runs/proxy_log.jsonl)
Runtime control: POST /_control {"fault": "...", "params": {...}, "start_after": N, "run_id": "..."}
"""
import json
import os
import time

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from . import checks
from .faults import FAULTS, REQUEST_FAULTS, RESPONSE_FAULTS

app = FastAPI()
state = {"fault": "none", "params": {}, "start_after": 0, "calls": 0, "fired": 0, "run_id": "unset"}
app.state.client = None


def _log(rec):
    path = os.environ.get("LOG_PATH", "runs/proxy_log.jsonl")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(rec) + "\n")


def _client():
    if app.state.client is None:
        app.state.client = httpx.AsyncClient(timeout=300)
    return app.state.client


@app.post("/_control")
async def control(request: Request):
    cfg = await request.json()
    fault = cfg.get("fault", "none")
    if fault not in FAULTS:
        return JSONResponse({"error": f"unknown fault {fault}"}, status_code=400)
    state.update(fault=fault, params=cfg.get("params", {}), start_after=int(cfg.get("start_after", 0)),
                 calls=0, fired=0, run_id=cfg.get("run_id", "unset"))
    return {"ok": True, **state}


@app.get("/_state")
async def get_state():
    return state


@app.post("/v1/chat/completions")
async def chat(request: Request):
    req = await request.json()
    state["calls"] += 1
    n = state["calls"]
    cap = int(os.environ.get("MAX_CALLS", "0"))
    if cap and n > cap:  # hard spend guard: refuse once the per-run call budget is used up
        _log({"t": time.time(), "run_id": state["run_id"], "call": n, "blocked": "MAX_CALLS", "cap": cap})
        return JSONResponse({"error": {"message": f"proxy call budget ({cap}) exhausted", "type": "budget_exhausted"}}, status_code=429)
    fault, params = state["fault"], state["params"]
    active = fault != "none" and n > state["start_after"]
    sent, injected, detail = req, False, {}
    if active and fault in REQUEST_FAULTS:
        sent, injected, detail = REQUEST_FAULTS[fault](req, params)
    base = os.environ.get("UPSTREAM_BASE_URL", "").rstrip("/")
    headers = {"Authorization": f"Bearer {os.environ.get('UPSTREAM_API_KEY', '')}", "Content-Type": "application/json"}
    t0 = time.time()
    up = await _client().post(f"{base}/chat/completions", json=sent, headers=headers)
    latency = time.time() - t0
    try:
        body = up.json()
    except Exception:
        body = {"error": up.text[:500]}
    out = body
    if up.status_code == 200 and active and fault in RESPONSE_FAULTS:
        out, injected, detail = RESPONSE_FAULTS[fault](body, params)
    if injected:
        state["fired"] += 1
    try:  # Phase 3 checker, LOG ONLY: judged on what is sent to / returned by the model; must never break proxying
        found = checks.run_all(sent, req.get("model"), body if isinstance(body, dict) else None)
    except Exception as e:
        found = [{"check": "checker_error", "detail": repr(e)[:200]}]
    _log({"t": time.time(), "run_id": state["run_id"], "call": n, "fault": fault, "active": active,
          "injected": injected, "detail": detail, "requested_model": req.get("model"),
          "served_model": sent.get("model"), "response_model": body.get("model") if isinstance(body, dict) else None,
          "status": up.status_code, "latency_s": round(latency, 3),
          "checks": found, "request": req, "sent": sent if sent is not req else None, "upstream_response": body, "returned": out if out is not body else None})
    return JSONResponse(out, status_code=up.status_code)
