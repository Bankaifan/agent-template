# 0009 Test scoping

Issue: #135 (design study, no implementation in this PR).

## 1. Goal

Pull requests run only the tests that can be affected by the changed files; `main` and a nightly run always run the full suite. A change to a shared or core file, or an unmappable change, falls back to the full run. Heavy tests can be marked `slow` and run only nightly when the repo variable `NIGHTLY_HEAVY_TESTS` is `true` (default `false`). A nightly failure opens one `prio:1` issue. The required check `validate` keeps its name and always reports.

## 2. Current state (file references)

- `Makefile:2-4`: `make check` runs `ruff check .` and `pytest --timeout=60 -q` over all of `tests/`, then actionlint, zizmor and the repo checks (`Makefile:5-13`). One target for local runs, pull requests and pushes.
- `.github/workflows/validate.yml:3-8`: triggers `pull_request`, `push` to `main`, `workflow_dispatch`. Job `validate` runs `make check` (`:43`) with `fetch-depth: 0`. `PR_BASE_REF` is already passed (`:39`) and is empty outside pull requests; `make test-evidence` uses it (`Makefile:16-18`).
- `.github/rulesets/main.json:30`: required checks `validate`, `agent-smoke`, `risk`, `security-review`. Job `agent-smoke` already uses a changed-file filter step instead of a workflow-level `paths` filter so the required check always reports (`validate.yml:45-68`). Scoping must keep that property.
- `tests/conftest.py`: one autouse fixture; no markers are registered, there is no pytest config file (no `pyproject.toml`, `pytest.ini`).
- `.github/workflows/setup.yml:39-63`: the "Optional variables" table is the registry of variable defaults (`row NAME DEFAULT VALUE`); `tools/check/check_var_defaults.py` guards the expression form (`vars.X != '0'` needs an empty-string case).
- Scheduled workflows and the liveness guard: `tools/liveness.py` `SCHEDULED` lists the scheduled workflows; a new nightly workflow must be added there or it can silently stop.
- Failure issues from guards are signed (`tools/guard_mark.py`) and trusted by title prefix (`tools/trusted_issues.py`, see design 0008).
- Open: how long the full suite takes today. Nothing in this repo measures it; PR 1 records `pytest --durations=20` in its body before any claim about savings.

## 3. Options with trade-offs

Scoping:
- A. Keep the full suite on every PR. Simple, always correct, cost grows with the suite.
- B. Scope by changed files with a mapping `source path -> test files`. Chosen: cheap and visible. Risk: a wrong or stale mapping hides a failure. Mitigated by the full-run fallback (4.2), by the full suite on `main`, and by a test that fails when a module has no mapping.
- C. Coverage-based test selection (for example `pytest-testmon`). Accurate, but adds a dependency and a cache that can go stale. Rejected for now.

Heavy tests:
- D. A `slow` marker, deselected by default (`-m "not slow"`) in the PR run, selected in the nightly run. Chosen.
- E. Separate directory for heavy tests. Needs a second path convention and does not show up in the test file itself. Rejected.

Switch:
- F. Repo variable `NIGHTLY_HEAVY_TESTS`, default `false`. With `false` the nightly workflow runs nothing heavy and `slow` tests are not run anywhere except where a developer asks for them locally; the nightly run of the normal suite still happens. With `true`, `slow` tests are included in the nightly run. Chosen: the owner can try it without a revert.

Failure reporting of the nightly run:
- G. Let the workflow fail and rely on the failure watch of design 0008. Not available yet and a red scheduled run is easy to miss.
- H. The nightly job opens (or updates) one `prio:1` issue when it fails, with a fixed text and the run URL, no log text. Chosen. It follows the existing guard issue pattern (design 0008, 0004).

## 4. Chosen approach

A + B + D + F + H as one set.

### 4.1 Mapping, changed file to tests
New script `tools/ci/select_tests.py` (stdlib only, no model). Input: the changed file list (`git diff --name-only $BASE...$HEAD`); output: either `all` or a list of test files, one per line. Rules in order:
1. A changed file under `tests/` selects itself.
2. `tools/<name>.py` selects `tests/test_<name>.py` (the repo convention), plus the tests found by a grep for `import <name>` / `from tools import <name>` / `tools/<name>.py` in `tests/` (so a test of a caller that exercises the module also runs).
3. `tools/check/check_<x>.py` selects `tests/test_check_<x>.py`. `tools/ci/<x>.py` selects `tests/test_<x>.py`.
4. `.github/workflows/<w>.yml` selects the tests that mention `<w>.yml` (for example `tests/test_train_workflow.py`).
5. Anything not matched by a rule is "unmappable" and selects `all`.
The list is sorted and deduplicated; an empty result (docs-only change) selects nothing, and `make check` then still runs ruff and all non-pytest checks. Pytest with no selected files is skipped explicitly (pytest exits 5 on "no tests collected", which must not fail the run).

### 4.2 Fallback to the full run
`all` is selected when any changed file is one of: `tests/conftest.py`, `Makefile`, `tools/ci/install_tools.sh`, `tools/ci/select_tests.py` itself, `tools/guard_mark.py`, `tools/trusted_issues.py`, `tools/decision.py`, `AGENTS.md`, `.agents/**`, `.github/workflows/validate.yml`, any `pyproject.toml` / `pytest.ini` / `requirements*`, or when the list of changed files cannot be computed (no base SHA, shallow history, error). The list of shared/core files is a constant `FULL_RUN` in the script; it is data, with its own test. A file that is imported by more than five other modules under `tools/` is added to it by a test that computes the import graph, so the list cannot go stale unnoticed.

### 4.3 Wiring into CI and `make check`
- `Makefile`: the pytest line becomes a target `test` that reads `PYTEST_ARGS` (default empty = all of `tests/`, today's behaviour). `make check` calls it; local runs stay full.
- `validate.yml`: a step before `make check` runs `python3 tools/ci/select_tests.py` on pull requests only and exports `PYTEST_ARGS` through `$GITHUB_ENV`; on `push` to `main` and `workflow_dispatch` nothing is exported, so the full suite runs. The run also always passes `-m "not slow"`.
- Job name `validate` and the required checks in `.github/rulesets/main.json` stay as they are. No `paths:` filter on the workflow, because a filtered-out required check never reports. The job always runs; only the pytest argument changes. The ruleset needs no re-import.
- The selection result (`all` or the file list) is printed to the job log and the step summary, so a reviewer sees what ran.

### 4.4 Full suite on `main`
`push` to `main` always runs `make check` without `PYTEST_ARGS`. A scoped PR that hides a failure is therefore caught on `main` after the merge (`validate` runs there, see `validate.yml:5-6`). That failure goes red on `main`; the merge train and the failure watch handle it like any red `main`. The scoping is only safe because of this plus 4.2; it is documented in the PR template text of the scoping issue.

### 4.5 The `slow` marker
Register the marker (`markers = slow: ...`) in a new `pytest.ini`, and `--strict-markers`, so a typo fails. `make check` and the PR run pass `-m "not slow"`. Nothing is marked `slow` in the first PR; the marker exists so that tests identified as heavy by `--durations` can be moved. Open: which tests are heavy (see section 2).

### 4.6 Variable `NIGHTLY_HEAVY_TESTS`
- Default `false`, registered in `.github/workflows/setup.yml` in the "Optional variables" table (`row NIGHTLY_HEAVY_TESTS false "$NIGHTLY_HEAVY_TESTS"`), the place where defaults are registered.
- In expressions the compare is `(vars.NIGHTLY_HEAVY_TESTS || 'false') == 'true'`. That form is an equality, so `tools/check/check_var_defaults.py` (which only matches `!=`) is not triggered, and an unset variable can never switch the job off.
- With `false`, PR behaviour differs from today only by the scoping of 4.1 to 4.3.

### 4.7 Nightly workflow
New `.github/workflows/nightly.yml`: `schedule` (daily, off-peak) and `workflow_dispatch`; `permissions: contents: read` at workflow level, `issues: write` only for the issue step through the author app token as in the other guard workflows; checkout without persisted credentials; `make check` without `PYTEST_ARGS`, plus `-m "slow or not slow"` when the variable is `true`. On failure a script step opens one issue `Nightly failed` with label `prio:1` (dedup by title: when one is open, add a comment with the run URL instead), body fixed text and run URL, no log text, signed with `guard_mark.sign` (`GUARD_KEY` only in script steps). It is added to `liveness.SCHEDULED` so a missed nightly raises an overdue issue. `Nightly failed` is added to the `GUARD_TITLES` allowlist (design 0008, 4.6). The workflow touches `.github/`, so the issue is `risk:security` and Daniel approves (CODEOWNERS).

## 5. Migration and compatibility

Additive and off by default for the heavy part. PRs get scoping immediately after PR 1+3 merge; if the mapping is wrong, the fallback is a revert of the `validate.yml` step (Rollback). No required check changes name, no ruleset re-import. Local `make check` is unchanged (full). Open PRs pick the new behaviour up when they next run `validate`.

## 6. Test and verification plan

All of these fail on today's code (no `tools/ci/select_tests.py`, no marker, no variable row):
- `tests/test_select_tests.py`: each mapping rule with a fixture file list; unmappable file -> `all`; each `FULL_RUN` file -> `all`; empty diff -> nothing selected; git failure / missing base -> `all`; docs-only change -> nothing; output is sorted and deduplicated; every module under `tools/` maps to an existing test or is listed as "no test" (fails when someone adds a module without a test or mapping); the `FULL_RUN` constant contains every module imported by more than five other modules.
- `tests/test_validate_workflow.py` (new or extended pattern like `tests/test_train_workflow.py`): job name is still `validate`; no `paths:` filter; `PYTEST_ARGS` is exported only for `pull_request`; the ruleset still lists `validate`.
- `tests/test_nightly_workflow.py`: schedule and dispatch only, `permissions` minimal, `GUARD_KEY` only in script steps, the variable compare uses `|| 'false'`, the workflow is in `liveness.SCHEDULED`.
- `tests/test_pytest_markers.py`: `slow` is registered and `--strict-markers` is on; `make check` selects `-m "not slow"`.
- `tests/test_setup_workflow.py` pattern: the variable table has the `NIGHTLY_HEAVY_TESTS false` row.
- Measurement (recorded in the PR body of PR 3): the same PR once with scoping (selected list printed) and the full run time from `pytest --durations`; one PR touching `tools/guard_mark.py` must show `all`; one docs-only PR must show no pytest tests and `validate` still green.
- `make check` on every PR.

## 7. Rollback

Remove the scoping step from `validate.yml` (one PR; `PYTEST_ARGS` empty means the full suite as today). `NIGHTLY_HEAVY_TESTS=false` (default) turns the heavy part off without a revert; removing `nightly.yml` and its `SCHEDULED` entry removes the nightly run. A stray `Nightly failed` issue is an ordinary issue: close it by hand.

## 8. Split into PR-sized implementation issues

Each under about 400 changed lines, disjoint files:
1. **Scoping script and tests**: `tools/ci/select_tests.py`, `tests/test_select_tests.py`. No wiring; nothing calls it. First.
2. **`slow` marker**: `pytest.ini`, `Makefile` (`test` target with `PYTEST_ARGS` and `-m "not slow"`), `tests/test_pytest_markers.py`. Independent of 1.
3. **Wire scoping into validate** (`risk:security`, workflow change): `.github/workflows/validate.yml`, `tests/test_validate_workflow.py`, the measurement run. Needs 1 and 2.
4. **Nightly workflow and variable** (`risk:security`, workflow, trust allowlist): `.github/workflows/nightly.yml`, `.github/workflows/setup.yml` (variable row), `tools/liveness.py` (`SCHEDULED`), `tools/trusted_issues.py` (`GUARD_TITLES`, if design 0008 PR 1 is merged; otherwise it is left to that PR and noted), `tests/test_nightly_workflow.py`, `tests/test_setup_workflow.py`. Needs 2.
5. **Docs**: `README.md` (variable `NIGHTLY_HEAVY_TESTS`, how scoping works, how to force a full run), `CHANGELOG.md` if present. Last.

Order: 1 and 2 (disjoint, may run in parallel under the 2-job cap), then 3 and 4 in either order, then 5.

## 9. Owner decisions

none
