# Changelog

## [Unreleased]
- README (EN and DE) and `docs/decisions/0007-template-sync.md`: six-step setup for the template sync, version gate, reuse by other projects.

## [1.16] - 2026-11-11
- `orchestrator.yml` prompt and role: `gh variable` and `gh secret` are named as not allowed, and the DISPATCH value is given in the prompt. A read of a repo variable was denied and ended a run without action as silent (run 43120189065, #313).

## [1.15] - 2026-11-11
- `risk.yml`: `cancel-in-progress: false`. The `pull_request_target` and `pull_request_review` runs for one PR share a concurrency group and cancelled each other within a second (#441, #459).

## [1.14] - 2026-11-11
- `tools/train.py`: a DIRTY approved PR whose only conflicts are `VERSION` and `CHANGELOG.md` is re-bumped with `tools/rebump.py`, rebased onto main and force-pushed with lease, with no agent-fix run; any other conflict keeps the agent-fix path (design 0013 step 2, #450, closes #406).

## [1.13] - 2026-11-11
- `tools/rebump.py`: for a PR whose only conflicts with main are `VERSION` and `CHANGELOG.md`, re-bumps `VERSION` on top of main (x or y step) and moves the PR's changelog lines under the new heading; any other conflicting file is refused (design 0013 step 1, #449).

## [1.12] - 2026-11-11
- `orchestrator.yml`: comments by the author app no longer start an orchestrator run (they displaced pending runs, which ended `cancelled`; #440).

## [1.11] - 2026-11-11
- `.github/workflows/dispatch.yml` runs `tools/dispatch.py` on issue, comment, merge and hourly events when repo variable `DISPATCH` is `on` (default off). With it the orchestrator model only gets issues without a slip (`needs_slip`) and a due handover (`handover_due`), and a merged PR no longer wakes it (design 0015 step 4, #415).

## [1.10] - 2026-11-11
- `tools/slip.py` and `tools/dispatch.py`: model-free start of trusted, unblocked issues that already carry a `Files:` slip, and `agent:dev` removal after a merge; `prefilter.start_state()` is the shared slot and start-list computation (design 0015 steps 1 to 3, #415). Not wired into a workflow yet.

## [1.9] - 2026-11-11
- `tools/trusted_issues.py`: the signed `Unstarted run: ` issue family is trusted like the other guard issues (design 0012 step 4, #427).

## [1.8] - 2026-11-11
- `tools/failure_watch.py`: cancelled runs and startup failures are watched too (a cancelled job that never started is class `cancelled`); expected cancels (agent-review, validate.yml with a newer run of the branch) open no issue; the caller passes its own workflow file, `tools/status.py` passes `status.yml` (design 0012 step 1, #426).

## [1.7] - 2026-11-11
- Orchestrator starts every unblocked issue that fits the free slots in one run (`start` output of `tools/prefilter.py`); parked (`needs-human`) and done `agent:dev` issues no longer hold a slot. Default caps `MAX_DEV` 4 and `MAX_PRS` 5 for every repo.
- Design split issues run in parallel; a body line `Depends on: #N` (`tools/deps.py`) holds an issue back until #N is closed.
- Orchestrator: issue edits by the author app (status issue updates) no longer start a run; each one replaced a pending label or dispatch run, which GitHub then cancelled.

## [1.6] - 2026-11-11
- `tools/status.py` and `tools/train.py`: a PR's CI state (red, running) counts only the checks that `main.json` requires; a red or running non-required check no longer holds the train, and the status issue lists it as "red but not required" (#405).

## [1.5] - 2026-11-11
- `tools/check/check_budget.py` and `docs/budgets.json`: size caps for `AGENTS.md` and `.agents/roles/*.md`; growth past a cap fails `make check`, shrinking never does (#407).

## [1.4] - 2026-11-11
- Reviewer: from round 2 it reads only the delta since the last reviewed head (`tools/review_delta.py`, `.review/delta.diff`) plus its earlier findings; round 1, a rebase or a compare error keep the full diff (#404).

## [1.3] - 2026-11-11
- `tools/orchestrator_gate.py`: skipped runs no longer debounce the `approved` label trigger (#402).

## [1.2] - 2026-11-11
- `tools/design_parents.py`: a hand-written split issue titled `Design NNNN` now links to its design study, so the study closes when its split issues are done (#400).

## [1.1] - 2026-11-11
- `template-sync.yml` polls daily, gated by the template `x` version; `force` input and `TEMPLATE_SYNC_MODE=all` skip the gate.

## [1.0] - 2026-11-11
- First template version: `VERSION`, bump check for managed paths (`.agents/managed.json`), `x.y` accepted by `check_version.py`.
Sync: first versioned template; downstream repos record `synced_version` from here on.
