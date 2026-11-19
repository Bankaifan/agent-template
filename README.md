# agent-template

GitHub template for projects where AI agents write code and humans keep control.

Idea: **rules a script can check live in CI, not in prompts.** The agents get a short
`AGENTS.md`; CI supplies the strictness. Decision: `docs/decisions/0017-hpo-flow.md`.

## What the owner does

- **The release PR.** The merge train (`tools/train.py`) folds the changelog fragments on `main` into one PR
  `Release <version>` from `release/next`: one version step per release, body in `OWNER_LANG` (default German) with the
  user-facing lines and one line naming what is parked. It is the only review request the owner gets; `VERSION`
  changes only when he merges it.
- **PRs that change a CODEOWNERS path** (GitHub requires the code owner's review). `.github/CODEOWNERS` covers only the
  outsider boundary and the gate: CODEOWNERS, `.github/rulesets/`, `tools/trusted_issues.py`, `tools/agent_guard.py`,
  `tools/guard_mark.py`, `tools/exec_log.py`, `tools/ci/risk.py`, `risk.yml`, `.agents/checks.json`. In a project a
  template sync PR that carries such files counts too.
- **Setup, once:** secrets, the two apps, the ruleset (below).

Nobody is asked, mentioned or assigned for anything else, and a person never sets a label.

## How the agents work

- Roles in `.agents/roles/`. Agents run in GitHub Actions via [`anthropics/claude-code-action@v1`](https://github.com/anthropics/claude-code-action),
  paid by a Claude subscription (OAuth token), no API key.
- Two GitHub Apps: the **author** pushes and opens PRs, the **approver** reviews. Nobody approves their own work.
- A ruleset on `main` (PR, 1 approval, code owner review, check `validate`, linear history, rebase merge only) plus auto-merge.
- Names: every piece of work has one NAME. Issues and PRs are titled `V<major>-<NAME>: <summary>`, every commit
  `V<version>-<NAME>: <what it does>` (`tools/task_ids.py`, checked by CI). Many small commits, no squash.
- The reviewer runs only on green CI (`workflow_run` of `validate`) and never runs PR code (it checks out `main`, reads the PR with `gh`).
  Fix rounds start automatically when the reviewer requests changes or CI is red (max 2), then the task restarts once.
- The merge train (`tools/train.py`) lands approved PRs. `main` requires an up-to-date branch, so two or more ready
  PRs with disjoint files land as one PR `Batch: #a, #b` on `agent/batch`: a script builds it, `tools/reapprove.py`
  approves it only when every file is exactly what the approver approved in a member PR, and no model is involved.
  A batch that fails is closed and its PRs land one by one (`docs/decisions/0018-batch-train.md`, `TRAIN_BATCH=off` disables it).
- Stuck work is `parked` by script: no note, no mention. An unblocker (`.agents/roles/unblocker.md`, `unblocker.yml`,
  `docs/decisions/0010-unblocker.md`; `UNBLOCKER=off` disables it) looks at it first: a wrong assumption gets a correction
  and a restart, an infrastructure bug a `prio:1` issue. `tools/status.py` un-parks every parked item after a cool-down
  (24 h, doubled per park, at most 7 days) with a fresh start.
- Intake (`intake.yml`, `tools/outside_intake.py`; `INTAKE=off` disables it): an issue by anyone but the owner, and every
  scout idea, is read as masked data by a model without token or shell. A script validates its verdict and answers,
  declines or opens a slip issue (`Intake: #N`). Only that slip is trusted, and its PR must be risk `none`.
- Only trusted input drives agents (`tools/trusted_issues.py`, not the prompt): issues by the owner, intake slips,
  design-derived and template sync issues of the author app, guard issues signed with `GUARD_KEY`.
- Token boundary (`docs/decisions/0016-safety-boundary.md`, design 0017): the dev and fix model tokens have no `workflows` or `actions` write; a workflow change travels as a patch that `workflow-apply` applies after the security review. Repo variable `DEV_SHELL=free` gives dev and fix runs a free shell (unset: the command list); the deny rules for `Read` stay in both cases. `.github/rulesets/agent-refs.json` confines the app token to `agent/**` branches once imported.
- Untrusted text: all model steps get a deny list for reads outside the workspace. The unblocker and intake read masked
  files and write one validated verdict that a script applies; the other steps are not migrated yet (`docs/decisions/0013-untrusted-text-boundary.md`).
- Dependabot PRs are not reviewed by AI: a model-free workflow approves them once `validate` is green and enables auto-merge.
- Design study only if a change touches who or what is trusted, token or app permissions, CODEOWNERS paths, or what leaves the repo: such an issue first gets a `docs/design/NNNN-<slug>.md` PR
  (see `docs/design/README.md`). The design reviewer (`.agents/roles/design-reviewer.md`) approves it and decides its
  *Owner decisions*; a script then creates the implementation issues (body line `Design: docs/design/...`).
- Risk classes (`tools/ci/risk.py`, workflow `risk`): a diff touching `permissions:`, `allowedTools`, `allowed_bots`, secrets/tokens, trust logic,
  rulesets, CODEOWNERS or the AGENTS.md Limits is `security`, other agent-infrastructure changes are `infra`. Every such
  agent PR also needs the security reviewer (`.agents/roles/security-reviewer.md`, `agent-security-review.yml`, required
  status `security-review`), then it auto-merges. Add `risk` and `security-review` to the ruleset's required checks.
- Weekly: a cleaner (`cleaner.yml`, `.agents/roles/cleaner.md`; `CLEANER=off` disables it) removes what nobody needs, one
  commit per removal with proof, one PR; a rule keeper opens one PR with rule proposals. Daily: `branch-cleanup` deletes
  `agent/*` branches with a closed PR, or no PR and no commit for 7 days.
- An autonomous `orchestrator` (after a merge to `main`, daily, manual; off unless variable `ORCHESTRATOR_ENABLED=true`) cuts task slips,
  keeps at most `MAX_DEV` (default 4) active `agent:dev` issues, starts every unblocked issue that fits and updates HANDOVER.md via PR.
  With `ORCHESTRATOR_EVENTS=on` it also wakes on issues, comments, PRs and reviews of the owner and the agent apps
  (`docs/decisions/0012-orchestrator-events.md`).
- A monthly `scout` (haiku) opens at most `IDEAS_PER_WEEK` (default 3 per run, 0 = off) `idea` issues, also from Dependabot/CodeQL alerts.
- `make check` is what CI checks: ruff, pytest, actionlint, zizmor (pinned in `tools/ci/install_tools.sh`) and the repo checks.
  `validate` also runs gitleaks. Orchestrator and scout run `tools/prefilter.py` first and skip the model when there is nothing to do.
  The "Weekly summary" issue is updated on Mondays by `tools/weekly_summary.py`, no model.
  Actions minutes are free on public repos; private repos have a monthly quota, so schedules there are slower.

## Setup

1. **Use this template** (private repo). Enable *Settings > General > Allow auto-merge*, allow *rebase merging* only.
2. **Create two GitHub Apps** and install both on the repo.
   - Author: Contents, Pull requests, Issues, Actions and Workflows: read and write (Workflows to push `.github/workflows`;
     Actions to read run logs and dispatch `validate`).
   - Approver: Pull requests: read and write, Contents and Issues: read.
3. **Add 4 secrets in every repo** (*Settings > Secrets and variables > Actions*; they are not inherited from the template): `CLAUDE_CODE_OAUTH_TOKEN` (from `claude setup-token`),
   `AUTHOR_APP_KEY`, `APPROVER_APP_KEY` (the `.pem` content), `GUARD_KEY` (any long random string; signs issues the guard scripts write, so the orchestrator trusts them; without it they stay untrusted).
   Four required **variables** (same page, *Variables* tab): `AUTHOR_CLIENT_ID` and `APPROVER_CLIENT_ID` (the apps' client IDs, not secret;
   `app-id` is deprecated in `actions/create-github-app-token`), and `AUTHOR_BOT` and `APPROVER_BOT`, the apps' bot logins (e.g. `my-author[bot]`,
   `my-approver[bot]`; the forms `x`, `app/x` and `x[bot]` are treated alike). They replace any `allowed_bots: '*'`; `agent-fix` also needs the review to come from `APPROVER_BOT`.
   Optional: `OWNER` (default: the repository owner), `OWNER_LANG` (default `German`), `RUNNER` (default `ubuntu-latest`).
4. **Import the ruleset**: *Settings > Rules > Rulesets > New > Import* with `.github/rulesets/main.json`.
   Re-import it whenever that file changes (it is not applied automatically); delete the old ruleset first.
   The optional `.github/rulesets/agent-refs.json` (agent branches only) is imported the same way.
5. **Run the `setup` workflow** (*Actions > setup > Run workflow*): it creates all labels (idempotent) and fails with
   the list of missing secrets and variables (names only, values are never printed).
6. **First task**: open an issue with a goal and acceptance criteria and comment `/dev` (or set `ORCHESTRATOR_ENABLED=true`).
   The PR is reviewed and auto-merged after approval and green CI; the change reaches you in the next release PR.

Then fill in `AGENTS.project.md` (one sentence about the project) and replace the placeholders in `HANDOVER.md`.

## Green means the agents work too

On PRs touching `.github/workflows/`, `.github/actions/` or `tools/ci/`, the required check `agent-smoke` creates both
app tokens with the PR's workflow versions, calls `gh api /installation/repositories` with each and checks the Claude
OAuth secret exists (no model call). It is skipped (= success) when no such path changed. Dependabot PRs get no
Actions secrets: set the three secrets also as **Dependabot secrets** (Actions variables are readable in Dependabot runs);
until then `agent-smoke` fails on them with a clear message. `setup` reports whether they exist (best effort).
Re-import the ruleset after this change.

## Project files (no overrides)

A project adds its own content in four files that the template never manages. A project with these files and no
overrides takes every template sync as a clean copy (`docs/decisions/0008-extension-points.md`,
`docs/design/0016-extension-points.md`).

- `project.mk`: recipes for `project-check::`, which `make check` runs last. The Makefile includes the file when it exists.
- `AGENTS.project.md`: project rules, imported by `CLAUDE.md` after `AGENTS.md`. The Limits in `AGENTS.md` win.
- `.agents/checks.json`: `{"required": ["name", ...]}`, extra required checks. `tools/ruleset.py build` adds them to the
  template ruleset; a name that repeats a template check or is malformed is refused. Re-import the built ruleset in
  *Settings > Rules* after a change; a name counts as required only once GitHub enforces it. The file is owner-guarded (CODEOWNERS).
- `.agents/tool-pins.env`: `RUFF`, `ZIZMOR` or `ACTIONLINT` pins as `NAME=version` lines. Any other line or name fails
  `tools/ci/install_tools.sh`.

Template tests live in `tests/agent/`, so `tests/` stays free for the project's own tests.

## Keeping projects in sync

Projects created from this template get later template changes as one sync PR per template release, not a blind file copy
(`docs/decisions/0007-template-sync.md`, `docs/design/0011-automatic-template-sync.md`).
`template-sync.yml` polls daily (no model) and runs `tools/template_sync.py`. When the template's `VERSION` is higher than
`synced_version` in `.agents/template.json`, a script copies the changed files that match `managed` (clean files as they
are, overridden files merged with `git merge-file`) and opens one PR `Template sync <version>` that also sets `synced_sha`
and `synced_version`. A clean sync needs no model. A file whose merge conflicts stays out of that PR: the PR is titled
`Template sync <short sha> part 1`, and the issue `Template sync <short sha>` (label `agent:dev`) lists only the conflicted
files and ends with `Template-Sync: <40 hex>`. The orchestrator trusts the issue only when the author app (`AUTHOR_BOT`)
wrote it. The developer merges each conflicted file by hand, keeping its intent (agent-dev writes the three versions into
the untracked `.template/` first), sets `synced_sha` and `synced_version`, and opens one PR with `Closes #<sync issue>`.
A sync PR that carries CODEOWNERS paths needs the owner's review as code owner.

Setup for a project (six steps):

1. **Author app.** Install the author app (Setup, step 2) on the project and, if the template is private, on the template repo too.
   The scripted sync needs `contents` and `pull-requests` write on the project, and `workflows` write for a sync that changes
   `.github/workflows/`. Without them the sync falls back to the issue.
2. **Sync files.** Projects created with *Use this template* already have `.github/workflows/template-sync.yml`,
   `tools/template_sync.py` and `tools/template_apply.py`. Older projects copy all three from the template once; later changes
   arrive through the sync.
3. **Create `.agents/template.json`** (example below): `template`, `synced_sha` (the 40-hex template commit you last matched;
   empty means the run is a no-op), `synced_version` (the template version you last matched; missing counts as `0.0`), `managed` and `overrides`.
4. **Optional variables.** `TEMPLATE_SYNC=off` turns the poll off. `TEMPLATE_SYNC_MODE` is `version` by default (one sync
   PR per template release); `all` syncs every template commit. `TEMPLATE_SYNC_APPLY=off` returns to the issue-only
   report (no PR is opened by the script).
5. **Check.** Run *Actions > template-sync > Run workflow* with `force` set: it skips the gate. A clean template gives one
   `Template sync` PR; a conflict gives the part 1 PR and the issue. A second run updates the open PR or issue instead of
   opening another.
6. **When the last sync PR merges** (the script's PR, or the developer's PR after a conflict), `synced_sha` and `synced_version`
   move to the template commit and version it matched; the next sync waits for the next template release.

Another project reuses this template the same way: create it with *Use this template*, then follow steps 1 to 6. Its
`template` field names this repo (`Bankaifan/agent-template`); nothing in the template points back at the project.

Example `.agents/template.json` for a project (add it once by hand; it is not part of the template, so new projects do not
point back at it):

```json
{
  "template": "Bankaifan/agent-template",
  "synced_sha": "<40 hex: the template commit you last matched>",
  "synced_version": "1.1",
  "managed": [".github/workflows/", ".github/claude-judge-settings.json", ".github/dependabot.yml", ".github/CODEOWNERS", ".github/rulesets/",
              ".agents/roles/", "tools/", "tests/agent/", "AGENTS.md", "CLAUDE.md", "Makefile", "docs/design/README.md"],
  "overrides": [
    {"path": ".github/workflows/agent-fix.yml", "why": "workflow_run.workflows needs the CI name 'Validate'"}
  ]
}
```

- `synced_version`: the template version you last matched (set by the sync PR).
- `managed`: path prefixes the template owns (a trailing `/` means a directory). Other paths are never reported.
- `overrides`: exact `path` plus a free-text `why` for the developer. Put project content in the four project files
  (see *Project files*) first; an override is a whole-file copy that a sync cannot update.
- A too-old `synced_sha` only makes the first issue larger. No file, or an empty `synced_sha`: the run prints
  `template-sync: no .agents/template.json, skipped` and succeeds. In the template repo itself it is skipped as well.
- If the compare lists 300 or more files it may be cut off. The run then fails with a message and creates or edits no issue.
- Reading a private template needs the author app installed on the template repo.

**Project values.** Prefer repo variables over edited files: `PYTHON_VERSION` (default `3.x`), `EXTRA_INSTALL` (a shell
command that `tools/ci/install_tools.sh` runs after the common tools; it is read only from the repo variable, never from a
file on a PR branch) and `RUNNER`. `TEMPLATE_SYNC=off` turns the sync off. `NIGHTLY_HEAVY_TESTS` (default `false`): with `true`, tests marked `@pytest.mark.slow` leave PRs and `main` and run in the nightly `nightly.yml` run, which opens one `prio:1` issue when they fail. Mark a test `slow` when it takes over about 5 s or needs a network or service (one `@pytest.mark.slow` line above the test; the marker is registered in `tests/conftest.py`, design in `docs/design/0009-test-scoping.md`). The one value that cannot be a variable is the CI
name in `workflow_run.workflows` (GitHub allows no expressions there). It is `[validate]` in `agent-fix.yml`,
`agent-review.yml`, `dependabot-automerge.yml` and `orchestrator.yml`. A project whose CI workflow has another name
(for example `Validate`) edits those lines and lists the files under `overrides`.

**Scout ideas for the template.** `scout.yml` opens each idea through `tools/idea_route.py` (no model). If every file of an
idea is under `managed` in `.agents/template.json`, the issue goes to the template repo (label `idea`, body ends with
`Found in: <project>#<context>`, no duplicate of an open template idea); otherwise, or without `template.json`, it stays in
the project. The model step only queues template ideas (`create`, project token). A later step without a model mints a second
author-app token limited to the template repo (same owner, `issues: write`) and runs `flush`, so no model ever sees it. The tool
accepts only the labels `prio:2` and `prio:3` and strips `@` mentions.

Rationale: [docs/decisions/0007-template-sync.md](docs/decisions/0007-template-sync.md).

## Limits

- One agent run per issue or PR at a time (`concurrency` per number, never cancelled). GitHub cannot cap
  jobs across workflows without dropping queued runs, so the orchestrator keeps at most `MAX_DEV` (default 4) active `agent:dev` issues.
- Rounds: labels `review:1`, `review:2` lead to a fix, `review:3` to one restart, then `parked` (2 fix rounds). A red CI counts as a round.
- Dependabot runs get no repo secrets, so `dependabot-automerge.yml` uses `workflow_run` on `validate`.
- Use private repos or keep `AUTHOR_BOT`/`APPROVER_BOT` set: the review workflow accepts bot-authored PRs.
- `allowedTools` is not a security boundary (e.g. `Bash(git:*)` still allows a lot). The boundaries are the token rights of the two apps and the rulesets on `main` and, once imported, on agent branches (`agent-refs.json`).
- Not verified end to end yet; see `docs/decisions/0001-agent-setup.md`.

All repo variables with defaults, readers, effects and allowed values: [docs/variables.md](docs/variables.md).

German short version: [README.de.md](README.de.md).
