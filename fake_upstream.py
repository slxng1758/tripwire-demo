"""Scripted fake OpenAI-compatible model server for OFFLINE end-to-end tests. No network, no cost.

Env FAKE_SCRIPT: JSON list of bash commands. The fake issues them one per turn, based on how many
tool results are already in the conversation. If the agent sends a plain user/format-error message
and no new tool result, it repeats the last command (so a disguised-failure fault is survivable).
"""
import json
import os
import time

from fastapi import FastAPI, Request

app = FastAPI()


@app.post("/v1/chat/completions")
async def chat(request: Request):
    req = await request.json()
    script = json.loads(os.environ.get("FAKE_SCRIPT", "[]"))
    done = sum(1 for m in req.get("messages", []) if m.get("role") == "tool")
    cmd = script[min(done, len(script) - 1)] if script else "echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"
    tools = {t["function"]["name"] for t in req.get("tools", [])}
    if "pytest" in cmd and "run_tests" in tools:
        fn = {"name": "run_tests", "arguments": "{}"}
    elif "pytest" in cmd and "run_tests" not in tools and "run_tests" in os.environ.get("FAKE_EXPECT_TOOL", ""):
        fn = {"name": "run_tests", "arguments": "{}"}  # mimics an agent calling a tool that was silently dropped
    else:
        fn = {"name": "bash", "arguments": json.dumps({"command": cmd})}
    msg = {"role": "assistant", "content": f"Step {done + 1}.",
           "tool_calls": [{"id": f"call_{done}_{int(time.time()*1000)%100000}", "type": "function", "function": fn}]}
    return {"id": "fake", "object": "chat.completion", "created": int(time.time()), "model": req.get("model", "fake"),
            "choices": [{"index": 0, "finish_reason": "tool_calls", "message": msg}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}}
