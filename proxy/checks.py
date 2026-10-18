"""Phase 3: proxy-side checks for silent failures. Pure functions, no network.

Each check looks only at what is about to be sent to the model (`sent`) and what came back (`body`), the way a real
checker in front of a model would. It must NOT compare against the fault injector's own pre-fault copy of the request: that
would just detect our own injection (circular). Every check returns a list of findings: {"check", "detail"}.
"""
import ast
import re

NUMBERING = re.compile(r"^\s*\d+\t", re.M)  # `nl -ba` line-number prefix
LS_ROW = re.compile(r"^[-dl][rwxsStT-]{9}\S*\s+\d+\s+\S+\s+\S+\s+(\d+)\s+\w{3}\s+\d+\s+[\d:]+\s+(\S+)\s*$", re.M)
DATE_SUFFIX = re.compile(r"-(\d{4}-\d{2}-\d{2}|\d{8})$")


def _tool_names(sent):
    return {t.get("function", {}).get("name") for t in sent.get("tools") or []}


def _text(m):
    c = m.get("content")
    return c if isinstance(c, str) else str(c or "")


def check_tools_vs_instructions(sent):
    """Tools the system prompt says exist (backticked names in the sentence that lists the tools) but the tools array lacks."""
    sys_text = " ".join(_text(m) for m in sent.get("messages", []) if m.get("role") == "system")
    if not sent.get("tools") or not sys_text:
        return []
    listed = set()
    for sentence in re.split(r"(?<=[.\n])\s", sys_text):
        if re.search(r"\btools?\b", sentence) and ":" in sentence:
            listed |= set(re.findall(r"`(\w+)`", sentence))
    missing = sorted(listed - _tool_names(sent))
    return [{"check": "tool_missing", "detail": f"instructions mention {missing} but the request offers {sorted(_tool_names(sent))}"}] if missing else []


def base_model(name):
    return DATE_SUFFIX.sub("", name or "")


def check_model(requested, body):
    """Returned model differs from the requested one after stripping a date suffix."""
    got = body.get("model") if isinstance(body, dict) else None
    if got and requested and base_model(got) != base_model(requested):
        return [{"check": "model_swap", "detail": f"requested {requested}, got {got}"}]
    return []


def _tool_pairs(messages):
    cmds = {}
    for m in messages:
        for t in m.get("tool_calls") or []:
            try:
                import json
                cmds[t["id"]] = json.loads(t["function"]["arguments"]).get("command", "")
            except Exception:
                cmds[t["id"]] = ""
    for m in messages:
        if m.get("role") == "tool":
            yield cmds.get(m.get("tool_call_id"), ""), m


def _result_text(m):
    import json
    c = _text(m)
    try:
        return str(json.loads(c).get("output", ""))
    except Exception:
        return c


def check_file_reads(sent):
    """A file read looks cut off: (a) a .py file read whole by `cat`/`nl` does not parse, or (b) it is shorter than the size
    shown by an earlier `ls -l` listing. Heuristic: a cut at a function boundary passes (a); (b) needs a prior ls -l."""
    findings, sizes = [], {}
    for cmd, m in _tool_pairs(sent.get("messages", [])):
        out = _result_text(m)
        for size, name in LS_ROW.findall(out):
            sizes[name] = int(size)
        # single-file reads only: `cat f.py`, `nl -ba f.py`, optionally `| sed -n '1,Np'`. Compound commands (`a && b`) concatenate
        # several files, which would not parse and would be false positives; they are skipped (a known blind spot).
        mm = re.fullmatch(r"\s*(?:cat|nl\s+-ba)\s+(\S+\.py)\s*(?:\|\s*sed\s+-n\s+'1,\d+p'\s*)?", cmd)
        if not mm:
            continue
        name = mm.group(1).split("/")[-1]
        body = NUMBERING.sub("", out)
        why = []
        if name in sizes and len(body.encode()) < sizes[name] * 0.9:
            why.append(f"saw {len(body.encode())} bytes of a {sizes[name]}-byte file")
        try:
            ast.parse(body)
        except SyntaxError as e:
            why.append(f"does not parse ({e.msg})")
        if why:
            findings.append({"check": "suspect_file_read", "detail": f"`{cmd[:60]}`: " + "; ".join(why)})
    return findings


def run_all(sent, requested_model=None, body=None):
    f = check_tools_vs_instructions(sent) + check_file_reads(sent)
    if body is not None:
        f += check_model(requested_model, body)
    return f
