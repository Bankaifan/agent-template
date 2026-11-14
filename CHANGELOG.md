# Changelog

## [Unreleased]
- README (EN and DE) and `docs/decisions/0007-template-sync.md`: six-step setup for the template sync, version gate, reuse by other projects.

## [1.101] - 2026-11-14
- The actions watcher skips with a warning when `GUARD_KEY` is unset instead of failing every scheduled run.

## [1.100] - 2026-11-14
- A downstream project no longer turns the template's own design studies into implementation issues or closes issues through their `Issue: #N` header (`TEMPLATE_DESIGNS` in `tools/design_origin.py`, delivered by template sync).

## [1.99] - 2026-11-14
- AGENTS.md no longer has a per-project placeholder: the project sentence lives in AGENTS.project.md, so a project needs no override of AGENTS.md.

## [1.98] - 2026-11-14
- Docs: `docs/bootstrap.md` describes the first PR of a project that imports the template (title for `managed_guard`, leave `HANDOVER.md` out, install both apps before `agent-smoke`).

## [1.97] - 2026-11-14
- Template tests no longer assert text in the root README: the README-link check is marked `template_only`, and the operator-switch check reads `docs/variables.md`, so a project can replace its README.

## [1.96] - 2026-11-14
- The fresh-downstream e2e test (`test_acceptance_3`) no longer fails in projects with their own `project.mk`: its scratch copy drops the project-owned extension files before `make check`.

## [1.95] - 2026-11-14
- A project can install its own tools with an optional unmanaged `.agents/install.sh`: `tools/ci/install_tools.sh` runs it once, only the version on the base branch (`origin/main`), before `make check`.

## [1.94] - 2026-11-14
- Template tests that check the template's own files (watch list, fresh-downstream e2e, README design rule, real checks.json, validate.yml shape) are marked `template_only` and no longer fail in downstream projects.

## [1.93] - 2026-11-13
- Dispatcher: a multi-step issue is no longer restarted from the slip of a step that already merged; it waits for the next slip instead of producing an empty run and `needs-human`.

## [1.92] - 2026-11-13
- Unblocker: a developer run whose step already landed on main is restarted by script (class 1) instead of being sent to Daniel as an owner decision.

## [1.91] - 2026-11-13
- Dispatcher: a one-line prose slip (`Slip. Goal: ... Files: a.py. Model: haiku.`) is read; before, only a `Files:` line at the start of a line counted, so such issues were never started.

## [1.90] - 2026-11-13
- managed_guard: every part of a split template sync (`Template sync <sha> part 2a`, `part 2b-1`, ...) is exempt like part 1, not only part 1.

## [1.89] - 2026-11-13
- Failure watch: a security review cancelled by a newer run of the same branch (cancel-in-progress) no longer opens a failure issue.

## [1.88] - 2026-11-12
- A settled dev run (merged PR, nothing left) now closes the issue as well as dropping agent:dev, so the dispatcher cannot restart it in a loop.

## [1.87] - 2026-11-12
- A dev run without a PR on an issue that already has a merged PR now drops agent:dev instead of retrying and opening a stuck-run issue.

## [1.86] - 2026-11-12
- The orchestrator changes its body files with Edit instead of a denied sed call.

## [1.85] - 2026-11-12
- A silent developer or fix run retries once by itself (fix: the task restarts from main) and then becomes one signed prio:1 issue for the agents instead of needs-human.

## [1.84] - 2026-11-12
- A PR title over 100 characters is cut at a word boundary by script instead of parking the PR with Daniel; the fix run's silent-run note now knows the author app and can offer a restart.

## [1.83] - 2026-11-12
- Developer and fix runs may pipe into head, tail, grep, sort, wc and jq (read-only filters; both runs already have python3).

## [1.82] - 2026-11-12
- The orchestrator writes long issue and comment bodies to `.agent-out/` (its only writable path) instead of a denied `/tmp` file.

## [1.81] - 2026-11-12
- Pipeline canary: a signed haiku issue after merges to workflows/tools, a 45 min check that names the stage where the chain stopped.

## [1.80] - 2026-11-12
- The developer model is chosen by script from the slip: haiku by default, sonnet for workflows, CI, trust or guard tools, CODEOWNERS and design docs, or after a failed round; a `Model:` line is only a hint.

## [1.79] - 2026-11-12
- Failure watch: a red validate run on a PR branch no longer opens or reopens a failing-workflow issue; only main does.

## [1.78] - 2026-11-12
- Automerge also runs when agent-security-review completes, so a security-review success that arrives after the approval no longer leaves the PR waiting.

## [1.77] - 2026-11-12
- The downstream e2e tests run their inner make check without the PR_*, GH_* and GITHUB_* variables of the outer CI run.

## [1.76] - 2026-11-12
- workflow-apply finds the security-approved agent PRs itself; the review run's branch name is always the default branch.

## [1.75] - 2026-11-12
- Validate checks an agent PR with its pending workflow patch applied, so the security review can start.

## [1.74] - 2026-11-12
- Decision record 0016 on the safety boundary (design 0017 step 7) and README entries for `agent-refs.json` and `DEV_SHELL`.

## [1.73] - 2026-11-12
- Repo variable `DEV_SHELL=free` gives developer and fix runs a free shell (bare `Bash`) with the deny settings kept; unset keeps the command list (design 0017 step 6).

## [1.72] - 2026-11-12
- The orchestrator model step is comment-only: no Edit, Write, git or make, and its app token has no contents scope. HANDOVER.md is committed and pushed by a script step.

## [1.71] - 2026-11-12
- The security reviewer is told which Bash forms it may use, so it no longer stops without a verdict after a denied piped command.

## [1.70] - 2026-11-12
- Background scripts (status, failure watch, orchestrator gate, dispatch) skip a tick while the GitHub API budget is low, a rate-limited run no longer becomes a failure issue, and agent runs read failed run logs through `tools/run_log.py`.

## [1.69] - 2026-11-12
- `tools/outside_intake.py`: script core of the outside intake (owed state per thread, author-app markers, cursor, daily run caps); no workflow or model step yet.

## [1.68] - 2026-11-12
- The answer receiver accepts a multi-line evidence quote when the owner comment uses CRLF line breaks; evidence is still checked as an exact, case-sensitive quote.

## [1.67] - 2026-11-12
- The orchestrator parks items with Daniel through `agent_guard.py park`, which refuses a note without a valid decision marker (#416).

## [1.66] - 2026-11-12
- Developer and fix runs are told that workflow changes are allowed and travel as a patch, so they no longer stop on old refusal comments.

## [1.65] - 2026-11-12
- The dispatcher restarts an agent:dev issue parked with `Waiting for #N` once #N is closed (no run in progress); while #N is open it holds no dev slot.

## [1.64] - 2026-11-12
- Agent workflow changes no longer stall: they travel as a patch file and are applied by script after the security review.

## [1.63] - 2026-11-12
- The version bump check test no longer fails on the release PR, where CI sets PR_HEAD_REF to release/next.

## [1.62] - 2026-11-12
- The merge train releases through a `release/next` pull request instead of pushing the release commit to main.

## [1.61] - 2026-11-12
- `tools/failure_watch.py`, `tools/actions_watch.py`: a failed `agent-dev` or `agent-fix` run that stopped at its `--max-turns` cap after a successful result (log: `reported a successful result after N turns, exceeding the configured maximum of M`) opens no failure issue and is not restarted; the run report prints the turn count (#562, Refs #439).

## [1.60] - 2026-11-12
- The dispatcher starts the first issues with a slip from the whole startable list, so slip-less issues ahead no longer take the free slots (#552).

## [1.59] - 2026-11-12
- Read-only gh calls in the liveness, unblocker, orchestrator gate and status tools retry transient failures twice and report stderr on the final error (#548).

## [1.58] - 2026-11-12
- The design split writes `Depends on:` with the final steps into the source issue, so a merged design no longer restarts its source issue (#544).

## [1.57] - 2026-11-12
- Judging model steps (review, security review, scout, unblocker, answer-receiver) are pinned read-only by `tests/test_judge_boundary.py` (design 0017, step 4).

## [1.56] - 2026-11-12
- `.github/workflows/agent-dev.yml`, `.github/workflows/agent-fix.yml`: the model step's token no longer has `workflows` or `actions` write, so a dev or fix push that changes `.github/workflows/` is refused and the run reports it on the issue or PR for Daniel; the CI trigger and the failed-log fetch use their own short-lived `actions` token (#539, Refs #421).

## [1.55] - 2026-11-12
- `.github/rulesets/agent-refs.json` confines branch creation, update and deletion to `agent/**` (plus the default branch), and `agent-tags.json` blocks tag creation for the app token (design 0017 step 2, #538).

## [1.54] - 2026-11-12
- `tools/run_stats.py denied [DAYS] [DIR]`: permission denials per workflow summed from saved execution files (design 0017 step 1, #537).

## [1.53] - 2026-11-12
- Projects add a make hook, rules, required checks and tool pins in four unmanaged files (`project.mk`, `AGENTS.project.md`, `.agents/checks.json`, `.agents/tool-pins.env`) instead of overriding managed files (design 0016).

## [1.52] - 2026-11-12
- Template tests moved to `tests/agent/` with their conftest; the managed prefix is `tests/agent/`, so `tests/` is free for project tests.

## [1.51] - 2026-11-12
- Required checks: `tools/ruleset.py build` writes the template ruleset plus the project's checks from `.agents/checks.json`; `status` reads the same set. `.agents/checks.json` is owned by Daniel (CODEOWNERS).

## [1.50] - 2026-11-12
- Tests pin the job names (`validate`, `changes`, `agent-smoke`) and triggers of `validate.yml`, which the required checks report under.

## [1.49] - 2026-11-12
- Test scoping accepts `tests/agent/` (template tests) and a project `tests/` tree side by side.

## [1.48] - 2026-11-12
- Projects can pin RUFF, ZIZMOR and ACTIONLINT in an optional `.agents/tool-pins.env` (`NAME=version` lines); any other line or name fails `install_tools.sh`.

## [1.47] - 2026-11-12
- CLAUDE.md imports `AGENTS.project.md` after `AGENTS.md`; projects put their rules there (new, unmanaged, empty by default) instead of overriding AGENTS.md (design 0016 step 2).

## [1.46] - 2026-11-12
- Makefile: `make check` runs `project-check` last; projects add its recipes in an optional `project.mk` instead of overriding the Makefile (design 0016).

## [1.45] - 2026-11-12
- The overlap guard no longer defers slips because of a `risk:security` PR that waits only for the owner (`needs-human` or approved head), nor because of that PR's own slip (#521).

## [1.44] - 2026-11-12
- `tools/actions_watch.py`: the sweep parks a restarted agent issue (`stalled:1`, then `needs-human`) only when the newest failed agent run was created after the `stalled:1` label (issue timeline). An older failed run, or a missing label event, waits for the restart's own run (design 0012 step 3, #508).

## [1.43] - 2026-11-12
- Task issues and their PR titles carry a short upper-case task ID (`NAMES: summary`); a PR whose linked issue has an ID must start its title with it (`check_pr_form`).

## [1.42] - 2026-11-12
- A denied tool call that the allow list does not cover opens one signed issue in the template repo (fixed text, capped per workflow, bumped by the next run); the source issue waits with `Depends on:` instead of needs-human, and a denied protected path still gets the note (#416, #489).

## [1.41] - 2026-11-12
- A denial note offers a retrigger ("ja") only after the allow list, the role file or the slip changed; a denied protected file (CODEOWNERS, judge settings) never gets one; the same call denied twice sets restart:1 and unblock:1; an owner answer to a question without a decision marker goes to the orchestrator (label owner-answer) instead of being guessed (#416, #488).

## [1.40] - 2026-11-12
- GUARD_KEY is no longer in any step that runs git in the agent checkout: the guard tools are fetched in a key-free step, and only the script step that runs `agent_guard.py` or `run_report.py` gets the key (#487).

## [1.39] - 2026-11-12
- The failure watch also closes open `<workflow> / - / -` issues when the last run was a cancelled run without any job and a newer run exists (#484).

## [1.38] - 2026-11-12
- Template sync docs: the developer role merges only the conflicted files of a sync; README, README.de and decision 0007 describe the scripted sync (design 0014, #414).

## [1.37] - 2026-11-12
- Template sync: an end-to-end test on a real template and downstream git repo: apply and materialize with conflicts, a sync without conflicts, a judge-settings sync with no model, and a fresh downstream `make check`.

## [1.36] - 2026-11-12
- Developer run for a template sync issue also writes the three versions of each conflicted file (`tools/template_sync.py materialize`) into `.template/`: `<path>.ours`, `<path>.base`, `<path>.theirs`.

## [1.35] - 2026-11-12
- Template sync: the daily poll applies managed template changes by script in one PR (`TEMPLATE_SYNC_APPLY`, default on). The build job holds read access only, the publish job pushes; conflicts still go to the developer as a part 1 PR and issue.

## [1.34] - 2026-11-12
- Template sync: `tools/template_sync.py apply` ports clean template files and three-way merges overridden ones on a checkout, in one commit; `materialize` writes the three versions of a conflicted file for the developer. Conflicts make a `part 1` PR that leaves `synced_sha` unchanged.

## [1.33] - 2026-11-12
- Template-only tests (`template_only` marker, `tests/conftest.py`) and `tools/check/check_version_bump.py` are skipped in downstream projects (`.agents/template.json` present); `managed_guard.py check` stays active (#476).

## [1.32] - 2026-11-12
- `TEMPLATE_SYNC_MODE` now defaults to `all`: every template version produces a sync PR; set `version` to keep the version gate.

## [1.31] - 2026-11-12
- A design study is required only when a change touches who or what is trusted, token or app permissions, CODEOWNERS paths, or what leaves the repo; other big or multi-PR work starts directly with a split in the issue.

## [1.30] - 2026-11-12
- Review rounds count only findings (owner decision 2026-11-12, #469): an approved head gives its round back (`agent_guard.py refund`), a red CI from PR form or `VERSION`/`CHANGELOG.md` counts no round and gets one fix run per PR (`form-failure`, label `formfix`; a second one counts a round), a conflict with main gets one uncounted fix run per head (`conflict:<sha7>`), a silent fix run on a green, approved PR is only logged, and `status.py` removes `needs-human` from a green, approved PR without CODEOWNERS paths. AGENTS.md (Review rounds) says so. Security follow-up: `release_settled` reads the paginated `pulls/N/files` with renamed-from paths and keeps `needs-human` when the list may be cut off; a `risk:security` PR gives its round back only after the security approve of the head.

## [1.29] - 2026-11-12
- `tools/release_fragments.py`, `tools/train.py`, `tools/check/check_version_bump.py`, `changelog.d/`: a PR no longer edits `VERSION` or a version heading; it adds `changelog.d/<issue>.md` (optional `step: x|y`). After the merge the train, as the one writer, assigns the next version per fragment, writes the `CHANGELOG.md` section and pushes one commit to main. `tools/rebump.py` and its train call are removed (#468).

## [1.28] - 2026-11-12
- The version check fails a PR whose new version already has a tag or is not above the highest tag (pre-releases sort before the final version).
- `tools/check/check_version.py --next minor|patch|major` prints the next version after the highest tag; roles take versions from it, not from memory.

## [1.27] - 2026-11-12
- The unblocker workflow also accepts runs started by the approver app, so a `needs-human` label set by that app gets a verdict again (#457).

## [1.26] - 2026-11-12
- `tools/liveness.py`: `watch.yml` is a scheduled workflow (60 min), so the status run raises the signed `Overdue scheduled run: actions watcher` issue when the watcher is dead; the watcher already watches `status` (mutual watch, design 0012 step 5, #430).

## [1.25] - 2026-11-12
- `tools/actions_watch.py`, `watch.yml`: the sweep self-heals. Fallback `agent:dev` on signed watch issues only while the orchestrator is unhealthy and `MAX_DEV` has room; one restart of failed agent work (`stalled:1`, then `needs-human` with the German note); `Kicked: n` counter in the signed `Unstarted run: orchestrator` issue, `needs-human` at 2. Unsigned or foreign-author issues are never touched (design 0012 step 3, #429).

## [1.24] - 2026-11-12
- The status issue shows a "Flow, last 24 h" block (lead time, slowest stage, model runs per merged PR, share needing the owner) from `tools/flow.py`; one CSV row per merged PR is uploaded as the `flow-metrics` artifact (#420).

## [1.23] - 2026-11-12
- Design split issues are created by `tools/design_split.py` (workflow `design-split`) when a design merges; section 8 of a design has a fixed format that `make check` parses; orchestrator prompt step 1b is removed (#417).

## [1.22] - 2026-11-12
- The release PR title is shortened to a version range when the version list would exceed the 100 character title limit.

## [1.21] - 2026-11-12
- agent-fix no longer fails when the PR is merged and its branch deleted between the prepare and fix jobs: the fix job re-checks that the PR is open and skips checkout and agent otherwise (#311).

## [1.20] - 2026-11-12
- `tools/failure_watch.py`, `tools/actions_watch.py`: a cancelled run whose job never started (no job, or no step ran) is expected when a newer run of the same workflow exists: no issue, no rerun. Open `<workflow> / <job> / cancelled` issues whose last run is expected are closed (#482, Refs #440).

## [1.19] - 2026-11-12
- `tools/template_apply.py`: step 1 of the template sync by script (design 0014): plan, path guard (relative managed paths only), three-way merge through `git merge-file` (a conflict leaves the file untouched), write and delete for clean files. Not wired into a workflow yet (#475, #414).

## [1.18] - 2026-11-12
- `strip-attribution.yml`, `tools/strip_attribution.py`, `tools/attribution.py`: tool attribution footers are removed from PR and issue bodies by a script (saved only when changed); `check_pr_form.py` shares the pattern list, keeps the rule for commit messages and judges the live body; the reviewer no longer reports a body footer (#471).

## [1.17] - 2026-11-12
- `.github/workflows/watch.yml` and `tools/actions_watch.py`: a failed, timed-out, cancelled or startup-failed run of any other workflow is rerun once (attempt 1, startup failure or never-started job) or opens/updates the signed `Failing workflow:` issue; a 30 min sweep catches undelivered events; `DRY_RUN` writes nothing (design 0012 step 2, #428).

## [1.16] - 2026-11-11
- `orchestrator.yml` prompt and role: `gh variable` and `gh secret` are named as not allowed, and the DISPATCH value is given in the prompt. A read of a repo variable was denied and ended a run without action as silent (run 43120189065, #313).

## [1.17] - 2026-11-11
- `tools/idea_route.py`: general router. `issue --number N` moves a project issue whose `Files:` line (or guard title: `Failing workflow:`, `Denied command in`, `Overdue scheduled run:`) touches only managed paths (minus overrides) to the template with a back link and a comment; mixed slips are asked to split; `check --number N` exits 3 when `agent:dev` must not be set. Skips with a log line without `TEMPLATE_GH_TOKEN` (#418; token and workflow wiring open, #117).

## [1.15] - 2026-11-11
- `risk.yml`: `cancel-in-progress: false`. The `pull_request_target` and `pull_request_review` runs for one PR share a concurrency group and cancelled each other within a second (#441, #459).

## [1.16] - 2026-11-11
- `tools/failure_watch.py`: an `orchestrator.yml` run cancelled while a newer run exists (pending run displaced in the concurrency group, with or without steps) is an expected cancel, no failure issue (#440).

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
