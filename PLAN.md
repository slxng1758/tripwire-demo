# Phase 2: fault injection experiment

Question: when a layer of the stack silently misbehaves, does a coding agent notice, or does it report success with a wrong result?

## Setup (decided 2026-10-12)
- Agent: mini-swe-agent 2.4.6 (single `bash` tool via OpenAI-style tool calling; litellm underneath, so it can be pointed at a proxy with `api_base`).
- Model: a small OpenAI model (mini/nano class) called directly with Sarah's OpenAI key via `UPSTREAM_BASE_URL=https://api.openai.com/v1` (model id still to choose; switched from OpenRouter on 2026-10-12 because Sarah has OpenAI credit).
- Proxy: `proxy/` (FastAPI, OpenAI-compatible, non-streaming). Injects ONE fault per run, logs every exchange to JSONL.
- Tasks: 30-50 small Python repos with a failing test; success = the test passes after the agent finishes. (`tasks/`, not written yet.)

## Faults (each grounded in Phase 1 rows)
| Fault | Layer | What the proxy does | Phase 1 evidence |
|---|---|---|---|
| truncate_read | context | cuts the output of a file-read command (cat/nl/head/tail/sed -n) in half, no marker | rows 293, 320, 266 |
| model_swap | routing | sends the request to a different model than requested | rows 586, 630 |
| drop_tool | tools | removes a named tool from the request | rows 180, 448, 629 |
| schema_drift | output | renames/reshapes a tool-call argument key in the response | rows 625, 607, 310 |
| disguised_failure | output | returns 200 + finish_reason "stop" with empty/partial content and no tool call | rows 581, 310 (swallowed/disguised: 11 of 58 confirmed) |

Out of scope: logging/billing/telemetry losses (4 of 58) - real bugs, but they do not change what an agent sees.

## Known design problems (decide before running)
1. **drop_tool is degenerate with mini-swe-agent.** It has exactly one tool (`bash`). Dropping it removes all tool use, so the agent gets a format error immediately - a loud failure, not a silent one. Options: (a) drop it from the plan and run four faults; (b) add a second tool to the agent (e.g. a `read_file` tool) so one can be dropped; (c) switch to an agent with several tools. Recommended: (b), because "silent" needs the agent to keep working with less than it expected.
2. **schema_drift may be loud.** Renaming `command` -> `cmd` makes mini-swe-agent raise a FormatError and ask the model to retry. That is a "detected" outcome by construction. Try subtler drifts (extra keys, wrapped values) and report which are noticed.
3. **disguised_failure** will probably be noticed by mini-swe-agent too (no tool call -> FormatError). It still measures whether the agent *recovers*, so keep it, but say so.
4. Streaming is not supported (mini-swe-agent does not stream). Streaming is a stretch goal.

## Measures (per fault vs a no-fault baseline)
- Task success rate and drop vs baseline.
- Fault fired? (proxy log `injected` flag) - analyze only runs where it fired.
- Detection: did the agent re-read, retry, or flag the problem? LLM judge reads the transcript; Sarah hand-checks a sample.
- Silent-wrong rate: agent submits, the test fails, and nothing in the transcript acknowledged the fault.
- Repeats: run each (task, fault) 3 times so single flukes do not dominate; report intervals, not bare percentages.

## Blockers right now
- No real API calls allowed until Sarah says so. Key is in phase2/.env (git-ignored) as UPSTREAM_API_KEY.
- Docker daemon is not running (only needed for docker-isolated task environments; local environment works for small tasks).

## Status
- [x] proxy + fault functions + 11 passing tests (mock upstream, no network)
- [x] key in phase2/.env (OpenAI, git-ignored); NO real API calls made so far
- [x] 3 starter tasks (tasks/t001_total, t002_slugify, t003_median): bug sits at the bottom of a ~800-char file, so a half-truncated read hides it
- [x] runner.py + scripted fake model (fake_upstream.py): offline end-to-end run works for all five faults; faults fire as expected (fake agent results are NOT meaningful, it only tests wiring)
- [x] first real smoke test (2026-10-12, Sarah approved, local env): t001_total, fault=none, model gpt-5.4-mini, 6 model calls, ~10.5k prompt + 0.6k completion tokens, ~13 s, tests passed. Run saved in runs/real-smoke-1/
- [x] run the agent in Docker: image tripwire-task (docker/Dockerfile: python 3.12-slim + pytest), `--env docker` runs commands in a container with no network, 1 GB / 1 CPU, task folder mounted at /work. Verified offline with the fake model (2026-10-12). Use docker for the real runs.
- [ ] scale tasks to 30-50
- [ ] LLM judge + hand spot-check
- [ ] fix drop_tool design (see above)

## Runner notes
- `python runner.py --task t001_total --fault truncate_read` runs OFFLINE against the fake model. Real calls need `--really-call-api` plus `--env docker` (or `--allow-local`).
- mini-swe-agent needs MSWEA_CONFIGURED=true (set by the runner) to skip its first-run wizard, and Enter on stdin to leave its interactive 'Agent wants to finish' prompt (the runner sends it).
- The real key is given only to the proxy process; the agent gets a dummy key.

## Findings from the smoke test
- The agent read the file with `nl -ba stats.py`, which the truncate_read fault matches, so that fault will fire on real runs.
- Requested model `gpt-5.4-mini`, response model `gpt-5.4-mini-2026-03-17` (a dated snapshot). The Phase 3 "model that answered matches the model requested" check must treat a dated snapshot as a match, or it will false-alarm on every normal run. (Same trap as Phase 1 row 296, dated model snapshots.)
- Safety guards now in place: per-run call cap in the proxy (default 25, returns 429 afterwards) and mini-swe-agent step_limit set to the same number.

## Baseline (9 runs, 2026-10-12, no fault, gpt-5.4-mini, local env)
- 9 of 9 passed (3 tasks x 3 repeats). Average 5.8 model calls and ~10.9k prompt + ~0.8k completion tokens per run. Runs in runs/base-*/.
- All 9 source-file reads used cat/nl/sed -n style commands, which the truncate_read regex matches. A read done through a Python one-liner would NOT be matched; that run would count as fault_not_fired. Analyze fault results only over runs where result.json has fault_fired > 0.
- With only 3 tasks the baseline is a harness check, not a measurement. Target 20+ tasks (ideally 30) before any fault run.
- Rough budget for 20 tasks x 5 conditions x 3 repeats = 300 runs: about 3.3M prompt tokens. Check the OpenAI usage page for actual spend after the baselines, and set a monthly spending limit in the OpenAI account settings (Sarah to do; the per-run call cap does not bound total spend).

## Decisions from review (2026-10-12)
- The drop_tool fault must remove a tool the tasks depend on (e.g. run_tests or submit), not an unused one. Needs a second tool added to the agent; not built yet.
- Phase 3 model check: compare the base name with the date suffix stripped, but log the full returned name so a swap between two snapshots of one model is still visible.
- The swallowed-failure fault already exists as disguised_failure (clean finish_reason "stop" with empty/partial content).
- Order: baselines (done) -> 20+ tasks + second tool + fault_fired logging (already logged per run) -> rerun baselines on the full set -> faults one at a time.

## Task set (2026-10-12)
- 20 tasks in tasks/ (t001-t003 hand-written, t004-t020 generated by tools/make_tasks.py). Original code written for this study.
- tools/validate_tasks.py checks, for every task: tests fail before the fix, pass after the intended fix, the bug string appears exactly once, and it sits in the last ~45% of its file (positions 0.62-0.98) so a half-truncated read hides it. All 20 pass the check.
- Bug kinds: off-by-one (3), wrong condition (4), math/rounding (4), string handling (2), mutable default, wrong ordering, logic/merge, parsing, data constant, dedupe ordering. Two tasks are multi-file (t015, t020), where the bug is in the second file read.
- t002's test was changed after the first baseline (the old version needed an unrelated accent fix too), so rerun its baseline.
- NOT done yet: the second tool for drop_tool. Every task is scored by `python -m pytest -q`; a `run_tests` tool wrapping that is the natural candidate.
- Sarah: spot-check 3-4 tasks yourself (suggested: t005, t012, t016, t020): read the file, find the bug, run `cd phase2/tasks/<id>/repo && ../../../.venv/bin/python -m pytest -q`.

## Cost so far (reported by Sarah from the OpenAI usage page)
About 7 cents for the 10 real runs so far (1 smoke test + 9 baselines, ~120k tokens). That is roughly 0.7 cents per run, so the 60-run baseline is about 40 cents and the 300-run study about $2, if runs stay similar. Faults may lengthen runs (retries), so recheck after the first fault batch.

## Baseline on 20 tasks, two tools, Docker (2026-10-12, no fault, gpt-5.4-mini)
- 60/60 runs passed (20 tasks x 3 repeats). runs/base20_summary.csv.
- Mean 5.9 model calls per run (4-9); ~11.8k prompt + 0.65k completion tokens per run; ~709k prompt tokens in total.
- The agent called run_tests in 60/60 runs (exactly once each), so dropping it will matter. Only 1 bash command mentioned pytest at all, and pytest is not reachable from bash.
- Ceiling effect: a 100% baseline means any drop is attributable to the fault, but faults that do not change the final test result can only be measured through the detection and claim measures, not through success rate.
- Next: pilot each fault (1 repeat = 20 runs) before running the full 3 repeats; check spend after the first pilot.

## Pilot results (2026-10-13, PRELIMINARY: automatic metrics + regexes; LLM judge and Sarah's hand-check pending)
Both pilots: gpt-5.4-mini, 20 tasks x 1 repeat, Docker, two tools. Baseline: 60/60 pass, run_tests used in 60/60 runs.

**drop_tool (run_tests removed from the tool list, still in the prompt)**: fault fired 20/20. Success 20/20. Submitted 20/20. run_tests called 0/20 (strict-verified 0/20: no project test-suite output). Tried `pytest` in bash 17/20 and hit "no module named pytest". Wrote that pytest/tests were unavailable or mentioned the "test runner" in 19/20 (broad regex, needs the judge). Ran some ad hoc check after the edit (loose-verified) 20/20. No agent said that its run_tests TOOL was missing from its tool list. Pattern: agent notices pytest is not in bash, falls back to manual checks, submits "verified manually". Bug fixed anyway in all 20, so success rate did not drop.

**truncate_read (v3, file reads of a named file cut in half; v0 and v1 invalid, see SCORING.md notes)**: fault fired 20/20. Success 20/20. Agent text says output was truncated / needs the rest in 16/20 (regex; none about directory listings). Used a non-truncated way to view code (python read_text/open, grep -n, awk) in 16/20. Silent-wrong 0/20.

Reading so far: with this agent, model and task difficulty, truncation was noticed and routed around, and a missing test tool did not lower success. The interesting finding is the verification gap in drop_tool (submitting on manual checks), not a success-rate drop. Tasks may be too easy for success-rate effects; the 100% baseline leaves no headroom for faults that only hurt harder tasks.
