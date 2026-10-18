# Tripwire

Tripwire studies **silent failures in AI agent infrastructure**: cases where a layer between the user and the model (context handling, routing, tools, output parsing) misbehaves without raising an error, so the agent or user keeps going with a wrong, incomplete, or mis-sourced result.

This repo is the demo of the experimental code: a fault-injection proxy, a small coding-agent harness, a set of bug-fix tasks, and proxy-side checks.

## The question

When one layer of the stack silently misbehaves, does a coding agent **notice**, or does it report success anyway?

## How it works

```
mini-swe-agent  ──►  Tripwire proxy (FastAPI, OpenAI-compatible)  ──►  model API
 (runs in Docker)      injects ONE fault per run, logs every exchange (JSONL)
```

- **Agent:** [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) with two tools, `bash` and `run_tests`, running in a no-network Docker container.
- **Tasks:** small Python repos with a failing test (`tasks/`). Each bug sits in the late part of its file, so a half-truncated read can hide it. After every run the tests are re-run on the host, regardless of what the agent said.
- **Faults** (`proxy/faults.py`), each modeled on real bug reports from open-source agent/LLM libraries:

| Fault | Layer | What the proxy does |
|---|---|---|
| `truncate_read` | context | cuts the output of a file-read command in half, with no marker |
| `drop_tool` | tools | removes a named tool from the request |
| `model_swap` | routing | sends the request to a different model than requested |
| `schema_drift` | output | renames or reshapes a tool-call argument in the response |
| `disguised_failure` | output | returns a clean "stop" with empty or partial content |

- **Checks** (`proxy/checks.py`): cheap proxy-side checks that look only at what is sent and returned (for example, tools the prompt mentions but the request lacks, or a returned model that differs from the requested one) and flag likely silent failures. `tools/eval_checker.py` replays them over logged runs.
- **Scoring** (`SCORING.md`): the definitions of "noticed", "claimed success", "verified" and "silent-wrong" were fixed before the pilot runs. Later changes are dated notes, not edits.

## Preliminary results

Small pilots, one model (gpt-5.4-mini), counts first. The LLM judge and a full manual hand-check are not done, so treat these as preliminary.

- **Baseline** (20 tasks x 3, no fault): 60/60 pass.
- **`drop_tool`** (`run_tests` removed, 20 runs): the fault fired in 20/20 runs and 20/20 still passed, but the agent never ran the project's tests (0/20) and submitted after ad hoc manual checks. None said its test tool was missing.
- **`truncate_read`** (20 runs): 20/20 passed. The agent's text mentioned truncation in about 16/20. The detector took three versions; the two invalid ones are kept and documented in `SCORING.md`.
- **A harder task** (`h001_percentile`, the only one of five hard tasks where the obvious fix is wrong), 10 runs per condition:
  - Without `run_tests`: 9/10 submitted an incomplete fix that passed the named test but failed the edge-case tests, and none said the tests had not been run.
  - With `run_tests`: 9/10 fixed it correctly.

Caveats: one model, small n, one hard task, and the run set is not a random sample of agent failures.

## Layout

| Path | Contents |
|---|---|
| `proxy/` | fault-injecting proxy (`app.py`, `faults.py`) and checks (`checks.py`) |
| `tripwire_agent/` | agent model wrapper and Docker environment |
| `tasks/` | 20 bug-fix tasks (`t001`-`t020`) and 5 harder ones (`h001`-`h005`) |
| `tools/` | task generation/validation, batch runner, analysis scripts |
| `tests/` | unit tests (no network) |
| `docker/` | task image (Python 3.12 + pytest) |
| `runner.py`, `fake_upstream.py` | single-run driver; scripted fake model for free offline runs |
| `PLAN.md`, `SCORING.md`, `judge_prompt.md` | design, scoring rules, judge prompt |

## Running it

Offline, no API key needed:

```bash
python -m venv .venv && .venv/bin/pip install mini-swe-agent fastapi uvicorn httpx pytest
.venv/bin/python -m pytest -q                                        # unit tests
.venv/bin/python tools/validate_tasks.py                             # check every task
docker build -t tripwire-task docker
.venv/bin/python runner.py --task t005_paginate --fault truncate_read --env docker   # fake model
```

Real runs call a paid API: put `UPSTREAM_API_KEY` in a git-ignored `.env`, then use `tools/run_batch.py ... --really-call-api --env docker`. Each run is capped at 25 model calls.
