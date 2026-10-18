import json
import httpx
from fastapi.testclient import TestClient
from proxy import app as appmod


def make_client(tmp_path, monkeypatch, upstream):
    monkeypatch.setenv("UPSTREAM_BASE_URL", "http://up/v1")
    monkeypatch.setenv("LOG_PATH", str(tmp_path / "log.jsonl"))

    class FakeClient:
        async def post(self, url, json=None, headers=None):
            return upstream(json)
    appmod.app.state.client = FakeClient()
    return TestClient(appmod.app)


def ok(req):
    body = {"id": "x", "model": req["model"], "choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": "hello world"}}]}
    return httpx.Response(200, json=body)


def test_passthrough_and_log(tmp_path, monkeypatch):
    c = make_client(tmp_path, monkeypatch, ok)
    c.post("/_control", json={"fault": "none", "run_id": "r1"})
    r = c.post("/v1/chat/completions", json={"model": "m", "messages": []})
    assert r.json()["choices"][0]["message"]["content"] == "hello world"
    rec = json.loads((tmp_path / "log.jsonl").read_text().splitlines()[0])
    assert rec["run_id"] == "r1" and rec["injected"] is False


def test_model_swap_end_to_end_and_start_after(tmp_path, monkeypatch):
    c = make_client(tmp_path, monkeypatch, ok)
    c.post("/_control", json={"fault": "model_swap", "params": {"to": "cheap"}, "start_after": 1})
    first = c.post("/v1/chat/completions", json={"model": "big", "messages": []}).json()
    second = c.post("/v1/chat/completions", json={"model": "big", "messages": []}).json()
    assert first["model"] == "big" and second["model"] == "cheap"
    assert c.get("/_state").json()["fired"] == 1


def test_disguised_failure_end_to_end(tmp_path, monkeypatch):
    c = make_client(tmp_path, monkeypatch, ok)
    c.post("/_control", json={"fault": "disguised_failure", "params": {"mode": "empty"}})
    out = c.post("/v1/chat/completions", json={"model": "m", "messages": []}).json()
    assert out["choices"][0]["message"]["content"] == ""


def test_unknown_fault_rejected(tmp_path, monkeypatch):
    c = make_client(tmp_path, monkeypatch, ok)
    assert c.post("/_control", json={"fault": "bogus"}).status_code == 400


def test_call_budget_blocks(tmp_path, monkeypatch):
    c = make_client(tmp_path, monkeypatch, ok)
    monkeypatch.setenv("MAX_CALLS", "2")
    c.post("/_control", json={"fault": "none"})
    codes = [c.post("/v1/chat/completions", json={"model": "m", "messages": []}).status_code for _ in range(3)]
    assert codes == [200, 200, 429]


def test_checker_logs_missing_tool(tmp_path, monkeypatch):
    c = make_client(tmp_path, monkeypatch, ok)
    c.post("/_control", json={"fault": "none"})
    sysmsg = "You have two tools: `bash` (shell) and `run_tests` (tests)."
    req = {"model": "m", "messages": [{"role": "system", "content": sysmsg}], "tools": [{"type": "function", "function": {"name": "bash"}}]}
    assert c.post("/v1/chat/completions", json=req).status_code == 200
    rec = json.loads((tmp_path / "log.jsonl").read_text().splitlines()[-1])
    assert [f["check"] for f in rec["checks"]] == ["tool_missing"]
