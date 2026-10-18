"""Pure functions that inject one silent fault into an OpenAI-style chat request/response.

Each fault takes the parsed JSON dict and returns (new_dict, injected: bool, detail: dict).
`injected` is False when the fault did not apply to this particular call (e.g. no file read present),
so the experiment can tell "fault active" apart from "fault actually fired".
"""
import copy
import json
import re

FILE_READ_RE = re.compile(r"^\s*(cat|nl|head|tail|sed\s+-n|less|bat)\b")
FILE_READ_ANY = re.compile(r"(?:^|&&|\|\||;|\|)\s*(cat|nl|head|tail|sed\s+-n|less|bat)\b")

FAULTS = ("none", "truncate_read", "model_swap", "drop_tool", "schema_drift", "disguised_failure")



def _stages(cmd):
    """Split a shell command into pipeline/sequence stages, respecting quotes."""
    out, cur, q, i = [], [], None, 0
    while i < len(cmd):
        c = cmd[i]
        if q:
            cur.append(c)
            if c == q:
                q = None
        elif c in "'\"":
            q = c
            cur.append(c)
        elif c in ";|&":
            out.append("".join(cur))
            cur = []
            while i + 1 < len(cmd) and cmd[i + 1] in ";|&":
                i += 1
        else:
            cur.append(c)
        i += 1
    out.append("".join(cur))
    return [x.strip() for x in out if x.strip()]


FILE_OPERAND = re.compile(r"(?<![\w.])[\w./-]+\.[A-Za-z0-9]{1,6}(?![\w.])")


def is_file_read(cmd):
    """True if some stage is cat/nl/head/tail/less/bat/sed -n applied to a named FILE (not stdin, not a listing)."""
    for st in _stages(cmd):
        if re.match(r"(cat|nl|head|tail|less|bat|sed\s+-n)\b", st):
            body = re.sub(r"'[^']*'|\"[^\"]*\"", "", st)  # drop quoted args such as sed scripts
            if FILE_OPERAND.search(body):
                return True
    return False


def _tool_command(call):
    try:
        return json.loads(call["function"]["arguments"]).get("command", "")
    except Exception:
        return ""


def truncate_read(req, params):
    """Silently cut the output of file-read tool results (Phase 1: context layer).

    Applies to EVERY file-read result in the request history on every call (deterministic), so the model
    keeps seeing the truncated version. A file read is any command that contains cat/nl/head/tail/sed -n
    as a pipeline stage, including compound commands like `printf x && nl -ba f.py`.
    """
    keep = float(params.get("keep_fraction", 0.5))
    min_chars = int(params.get("min_chars", 200))
    req = copy.deepcopy(req)
    msgs = req.get("messages", [])
    cmds = {}
    for m in msgs:
        for c in m.get("tool_calls") or []:
            cmds[c.get("id")] = _tool_command(c)
    changed = []
    for m in msgs:
        if m.get("role") != "tool":
            continue
        cmd = cmds.get(m.get("tool_call_id"), "")
        if not is_file_read(cmd):
            continue
        content = m.get("content")
        text = content if isinstance(content, str) else json.dumps(content)
        try:  # mini-swe-agent wraps output as JSON: {"returncode":..,"output":".."}
            obj = json.loads(text)
            out = obj.get("output", "")
            if len(out) < min_chars:
                continue
            obj["output"] = out[: int(len(out) * keep)]
            m["content"] = json.dumps(obj)
            changed.append({"cmd": cmd[:80], "original_len": len(out), "kept_len": len(obj["output"])})
        except Exception:
            if len(text) < min_chars:
                continue
            m["content"] = text[: int(len(text) * keep)]
            changed.append({"cmd": cmd[:80], "original_len": len(text), "kept_len": len(m["content"])})
    if not changed:
        return req, False, {"reason": "no file-read result long enough"}
    return req, True, {"truncated": changed}


def model_swap(req, params):
    """Serve a different model than the one requested (Phase 1: routing layer)."""
    to = params.get("to")
    if not to:
        return req, False, {"reason": "no target model configured"}
    req = copy.deepcopy(req)
    detail = {"requested": req.get("model"), "served": to}
    req["model"] = to
    return req, True, detail


def drop_tool(req, params):
    """Remove named tools from the request (Phase 1: tools layer)."""
    names = set(params.get("names", []))
    tools = req.get("tools")
    if not tools:
        return req, False, {"reason": "request has no tools"}
    req = copy.deepcopy(req)
    kept = [t for t in tools if t.get("function", {}).get("name") not in names]
    removed = [t["function"]["name"] for t in tools if t not in kept]
    if not removed:
        return req, False, {"reason": "named tool not present"}
    if kept:
        req["tools"] = kept
    else:
        req.pop("tools", None)
        req.pop("tool_choice", None)
    return req, True, {"removed": removed}


def schema_drift(resp, params):
    """Slightly change the shape of tool-call arguments in the response (Phase 1: output layer)."""
    mode = params.get("mode", "rename_key")
    resp = copy.deepcopy(resp)
    changed = []
    for ch in resp.get("choices", []):
        for c in (ch.get("message") or {}).get("tool_calls") or []:
            try:
                args = json.loads(c["function"]["arguments"])
            except Exception:
                continue
            if mode == "rename_key" and params.get("from", "command") in args:
                args[params.get("to", "cmd")] = args.pop(params.get("from", "command"))
            elif mode == "wrap_list" and params.get("key", "command") in args:
                k = params.get("key", "command")
                args[k] = [args[k]]
            elif mode == "stringify_extra":
                args["_meta"] = "x"
            else:
                continue
            c["function"]["arguments"] = json.dumps(args)
            changed.append(c.get("id"))
    return resp, bool(changed), {"mode": mode, "tool_call_ids": changed}


def disguised_failure(resp, params):
    """Return a clean 'stop' with empty/partial content as if the upstream call succeeded (Phase 1: swallowed failure)."""
    resp = copy.deepcopy(resp)
    mode = params.get("mode", "empty")
    for ch in resp.get("choices", []):
        msg = ch.get("message") or {}
        text = msg.get("content") or ""
        if mode == "empty":
            msg["content"] = ""
        else:
            msg["content"] = text[: max(0, len(text) // 2)]
        msg.pop("tool_calls", None)
        ch["message"] = msg
        ch["finish_reason"] = "stop"
    return resp, True, {"mode": mode}


REQUEST_FAULTS = {"truncate_read": truncate_read, "model_swap": model_swap, "drop_tool": drop_tool}
RESPONSE_FAULTS = {"schema_drift": schema_drift, "disguised_failure": disguised_failure}
