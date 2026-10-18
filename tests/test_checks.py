import json
from proxy import checks

SYS = "You have two tools: `bash` (run shell commands) and `run_tests` (run tests).\nOther text."


def req(tools, msgs=()):
    return {"model": "m", "messages": [{"role": "system", "content": SYS}, *msgs], "tools": [{"type": "function", "function": {"name": n}} for n in tools]}


def call(cid, cmd):
    return {"role": "assistant", "tool_calls": [{"id": cid, "function": {"name": "bash", "arguments": json.dumps({"command": cmd})}}]}


def result(cid, out):
    return {"role": "tool", "tool_call_id": cid, "content": json.dumps({"returncode": 0, "output": out})}


def test_tool_missing_flagged_and_clean_passes():
    assert checks.check_tools_vs_instructions(req(["bash", "run_tests"])) == []
    f = checks.check_tools_vs_instructions(req(["bash"]))
    assert f and f[0]["check"] == "tool_missing" and "run_tests" in f[0]["detail"]


def test_model_base_name_ignores_date_suffix():
    assert checks.check_model("gpt-5.4-mini", {"model": "gpt-5.4-mini-2026-03-17"}) == []
    assert checks.check_model("gpt-5.4-mini", {"model": "gpt-4o-mini-2024-07-18"})[0]["check"] == "model_swap"


def test_truncated_read_by_parse_and_by_size():
    full = "def f():\n    return 1\n"
    ok = req(["bash"], [call("a", "cat m.py"), result("a", full)])
    assert checks.check_file_reads(ok) == []
    cut = req(["bash"], [call("a", "cat m.py"), result("a", full[:9])])
    assert checks.check_file_reads(cut)[0]["check"] == "suspect_file_read"
    ls = "-rw-r--r--  1 agent agent  900 Oct 13 00:55 m.py\n"
    short = req(["bash"], [call("l", "ls -l"), result("l", ls), call("a", "cat m.py"), result("a", full)])
    assert "900-byte" in checks.check_file_reads(short)[0]["detail"]


def test_nl_numbering_is_stripped():
    numbered = "     1\tdef f():\n     2\t    return 1\n"
    assert checks.check_file_reads(req(["bash"], [call("a", "nl -ba m.py | sed -n '1,220p'"), result("a", numbered)])) == []
