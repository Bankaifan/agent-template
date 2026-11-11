# Changelog

## [Unreleased]
- README (EN and DE) and `docs/decisions/0007-template-sync.md`: six-step setup for the template sync, version gate, reuse by other projects.

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
