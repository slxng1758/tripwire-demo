import json
from proxy import faults


def tool_call(cmd, cid="c1"):
    return {"role": "assistant", "content": "", "tool_calls": [{"id": cid, "type": "function", "function": {"name": "bash", "arguments": json.dumps({"command": cmd})}}]}


def tool_result(output, cid="c1"):
    return {"role": "tool", "tool_call_id": cid, "content": json.dumps({"returncode": 0, "output": output})}


def test_truncate_read_cuts_file_read_output():
    req = {"messages": [tool_call("cat app.py"), tool_result("x" * 1000)]}
    out, injected, d = faults.truncate_read(req, {"keep_fraction": 0.5})
    assert injected and d["truncated"][0]["kept_len"] == 500
    assert len(json.loads(out["messages"][1]["content"])["output"]) == 500
    assert len(json.loads(req["messages"][1]["content"])["output"]) == 1000  # original untouched


def test_truncate_read_ignores_non_read_commands():
    req = {"messages": [tool_call("pytest -q"), tool_result("x" * 1000)]}
    _, injected, _ = faults.truncate_read(req, {})
    assert not injected


def test_truncate_read_ignores_short_output():
    req = {"messages": [tool_call("cat a"), tool_result("hi")]}
    assert not faults.truncate_read(req, {})[1]


def test_model_swap():
    out, injected, d = faults.model_swap({"model": "big"}, {"to": "small"})
    assert injected and out["model"] == "small" and d == {"requested": "big", "served": "small"}


def test_drop_tool_removes_and_cleans_up():
    tools = [{"type": "function", "function": {"name": "bash"}}, {"type": "function", "function": {"name": "read"}}]
    out, injected, d = faults.drop_tool({"tools": tools, "tool_choice": "auto"}, {"names": ["read"]})
    assert injected and [t["function"]["name"] for t in out["tools"]] == ["bash"]
    out, injected, _ = faults.drop_tool({"tools": tools[:1], "tool_choice": "auto"}, {"names": ["bash"]})
    assert injected and "tools" not in out and "tool_choice" not in out
    assert not faults.drop_tool({"tools": tools}, {"names": ["nope"]})[1]


def test_schema_drift_renames_key():
    resp = {"choices": [{"message": {"tool_calls": [{"id": "c1", "function": {"name": "bash", "arguments": json.dumps({"command": "ls"})}}]}}]}
    out, injected, _ = faults.schema_drift(resp, {"mode": "rename_key", "from": "command", "to": "cmd"})
    assert injected and json.loads(out["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"]) == {"cmd": "ls"}


def test_disguised_failure_returns_clean_stop():
    resp = {"choices": [{"finish_reason": "tool_calls", "message": {"content": "abcdef", "tool_calls": [{"id": "c1"}]}}]}
    out, injected, _ = faults.disguised_failure(resp, {"mode": "empty"})
    ch = out["choices"][0]
    assert injected and ch["finish_reason"] == "stop" and ch["message"]["content"] == "" and "tool_calls" not in ch["message"]


def test_truncate_read_is_persistent_across_history():
    req = {"messages": [tool_call("cat a.py", "c1"), tool_result("x" * 1000, "c1"),
                        tool_call("ls", "c2"), tool_result("y" * 1000, "c2")]}
    out, injected, _ = faults.truncate_read(req, {"keep_fraction": 0.5})
    assert injected
    assert len(json.loads(out["messages"][1]["content"])["output"]) == 500   # earlier read still truncated
    assert len(json.loads(out["messages"][3]["content"])["output"]) == 1000  # non-read untouched


def test_truncate_read_catches_compound_commands():
    req = {"messages": [tool_call("printf '--- f ---' && nl -ba f.py", "c1"), tool_result("z" * 600, "c1")]}
    assert faults.truncate_read(req, {})[1]
    req = {"messages": [tool_call("pwd && ls -la", "c1"), tool_result("z" * 600, "c1")]}
    assert not faults.truncate_read(req, {})[1]


def test_is_file_read_only_for_named_files():
    assert faults.is_file_read("cat stats.py")
    assert faults.is_file_read("nl -ba listing.py | sed -n '1,220p'")
    assert faults.is_file_read("printf '--- f ---' && nl -ba f.py")
    assert faults.is_file_read("head -20 shop/pricing.py")
    assert not faults.is_file_read("pwd && ls -la && find . -maxdepth 3 -type f | sed 's#^./##' | sort | head -200")
    assert not faults.is_file_read("grep -RIn record . | head -200")
    assert not faults.is_file_read("python - <<'PY'\nprint(1)\nPY")
