# agent-template

GitHub template for projects where AI agents write code and humans keep control.

Idea: **rules a script can check live in CI, not in prompts.** The agents get a short
`AGENTS.md`; CI supplies the strictness.

- Orchestrator + developer + reviewer roles (`.agents/roles/`), each at most 15 lines.
- Agents run in GitHub Actions via [`anthropics/claude-code-action@v1`](https://github.com/anthropics/claude-code-action),
  paid by a Claude subscription (OAuth token), no API key.
- Two GitHub Apps: the **author** pushes and opens PRs, the **approver** reviews. Nobody approves their own work.
- A ruleset on `main` (PR, 1 approval, code owner review, check `validate`, linear history, rebase merge only) plus auto-merge.
  The developer squashes its branch into one commit authored by Daniel, so Daniel is the sole author on `main`.
- The reviewer runs only on green CI (`workflow_run` of `validate`) and never runs PR code (it checks out `main`, reads the PR with `gh`).
  Fix rounds start automatically when the reviewer requests changes or CI is red (max 2, then `needs-human`).
  A fix round uses the model of the original task: sonnet if the PR or an issue it closes (`Closes #N`) has `model:sonnet`, else haiku.
  A red-CI fix on a PR that touches `.github/` or `tools/` always uses sonnet.
  After the developer pushes, a script step makes sure `validate` runs on the head SHA (else `gh workflow run validate.yml`).
- An unblocker (`.agents/roles/unblocker.md`, `.github/workflows/unblocker.yml`) looks at each `needs-human` before Daniel does: a wrong assumption gets a correction and one automatic restart (`unblock:1`), an agent infrastructure bug opens a `prio:1` issue, and only a real owner decision stays with Daniel. The model step has no token and no shell and reads masked files; a script validates its verdict and does all actions (`docs/decisions/0010-unblocker.md`). `UNBLOCKER=off` disables it.
- Dependabot PRs are not reviewed by AI: a model-free workflow approves patch/minor once `validate` is green and
  enables auto-merge; majors get `needs-human`. The update type comes from `dependabot/fetch-metadata` (grouped PRs: highest type wins),
  falling back to the title ("Update x requirement from A to B" is parsed too); unknown means major.
- Every `needs-human` on a PR also requests Daniel's review (`gh pr edit --add-reviewer Bankaifan`, skipped if he is the author), so it shows up under "Needs your review".
- Design study before big work: architectural, breaking, release-relevant or multi-PR issues first get a `docs/design/NNNN-<slug>.md` PR
  (see `docs/design/README.md`), reviewed by a design reviewer (`.agents/roles/design-reviewer.md`). Only the section *Owner decisions* needs Daniel;
  if it is empty the design merges without him. Afterwards the orchestrator creates the implementation issues (body line `Design: docs/design/...`;
  `tools/trusted_issues.py` trusts them when `AUTHOR_BOT` wrote them and the file exists on `main`).
- `.github/CODEOWNERS`: `@Bankaifan` owns only the security-relevant files: `AGENTS.md`, CODEOWNERS, `.github/rulesets/`, `tools/trusted_issues.py`, `tools/agent_guard.py`, `tools/ci/risk.py`, `risk.yml`.
- Risk classes (`tools/ci/risk.py`, workflow `risk`): a diff touching `permissions:`, `allowedTools`, `allowed_bots`, secrets/tokens, trust logic,
  rulesets, CODEOWNERS or the AGENTS.md Limits is `security` (label `risk:security`; the required check `risk` fails until Daniel approves the head SHA);
  other agent-infrastructure changes are `infra`. Every `infra`/`security` agent PR also needs the security reviewer
  (`.agents/roles/security-reviewer.md`, workflow `agent-security-review.yml`, required status `security-review`), then it auto-merges.
  Whatever waits for Daniel ends with a plain-German note (what, worst case, recommendation, yes/no question). Add `risk` and `security-review` to the ruleset's required checks.
- A weekly rule keeper that opens one PR proposing rule removals, new checks, contradiction fixes and scripts for recurring agent work steps (Daniel merges).
- A daily `branch-cleanup` that deletes `agent/*` branches with a closed PR, or no PR and no commit for 7 days (dry-run input on manual runs).
- An autonomous `orchestrator` (after a merge to `main` via `workflow_run` of `validate`, daily, manual; off unless variable `ORCHESTRATOR_ENABLED=true`) that cuts task slips,
  keeps at most 2 `agent:dev` issues, handles `needs-human` PRs, updates HANDOVER.md via PR and .
- A monthly `scout` (haiku) that opens at most `IDEAS_PER_WEEK` (default 3 per run, 0 = off) `idea` issues, also from Dependabot/CodeQL alerts; it adds only `idea`.
- `make check` is what CI checks: ruff, pytest, actionlint, zizmor (pinned in `tools/ci/install_tools.sh`) and the repo checks; the developer
  and fix jobs install the same tools. `validate` also runs gitleaks. Orchestrator and scout run `tools/prefilter.py` first and skip the model when there is nothing to do;
  the "Weekly summary" issue is updated on Mondays by `tools/weekly_summary.py`, no model; it also adds a row to `docs/metrics.csv` via PR
  (tiers S/M/L and thresholds: `docs/decisions/0008-tiers.md`).
  Actions minutes are free on public repos; private repos have a monthly quota, so schedules there are slower.
  Only trusted input drives agents: the orchestrator sees only issues authored by Daniel or labelled `approved`/`auto-ok` by Daniel
  (checked from the issue timeline by `tools/trusted_issues.py`, not by the prompt).

Quota is scarce: `ORCHESTRATOR_ENABLED` and `IDEAS_PER_WEEK` control the autonomous load; at most 2 agent jobs run at the same time; models are chosen per role
(developer routine: haiku, core work: sonnet, reviewer: sonnet, orchestrator: sonnet, fix rounds: as the original task, see above).

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
   Optional variable: `RUNNER` (default `ubuntu-latest`, e.g. `self-hosted`).
4. **Import the ruleset**: *Settings > Rules > Rulesets > New > Import* with `.github/rulesets/main.json`.
   Re-import it whenever that file changes (it is not applied automatically); delete the old ruleset first.
5. **Run the `setup` workflow** (*Actions > setup > Run workflow*): it creates all labels (idempotent) and fails with
   the list of missing secrets and variables (names only, values are never printed).
6. **First task**: open an issue with a goal and acceptance criteria, add label `agent:dev` (or comment `/dev`).
   Add `model:sonnet` for core work, otherwise haiku is used. The PR is reviewed, auto-merged after approval and green CI.

Then fill in `AGENTS.md` (one sentence about the project) and replace the placeholders in `HANDOVER.md`.

## Green means the agents work too

On PRs touching `.github/workflows/`, `.github/actions/` or `tools/ci/`, the required check `agent-smoke` creates both
app tokens with the PR's workflow versions, calls `gh api /installation/repositories` with each and checks the Claude
OAuth secret exists (no model call). It is skipped (= success) when no such path changed. Dependabot PRs get no
Actions secrets: set the three secrets also as **Dependabot secrets** (Actions variables are readable in Dependabot runs);
until then `agent-smoke` fails on them with a clear message. `setup` reports whether they exist (best effort).
Re-import the ruleset after this change.

## Keeping projects in sync

Projects created from this template get later template changes through a weekly report, not a blind file copy.
`template-sync.yml` (Mondays, or `workflow_dispatch`; no model) runs `tools/template_sync.py`. It compares the template's
`main` with `synced_sha` from `.agents/template.json` and lists the changed files that match `managed`. It creates the one
open issue `Template sync <short sha>` (labels `agent:dev`, `model:sonnet`), or edits it if one is already open.
Files you list under `overrides` are shown separately with your `why`. The issue ends with `Template-Sync: <40 hex>`; the
orchestrator trusts it only when the author app (`AUTHOR_BOT`) wrote it. The developer ports `clean` files as they are,
ports `overridden` files by hand keeping their intent (agent-dev downloads the template at that SHA into the
untracked `.template/` first, so the developer can read it), sets `synced_sha` to that SHA and opens one PR with
`Closes #<sync issue>`. The PR touches `.github/`, so Daniel must approve as code owner.

Example `.agents/template.json` for a project (add it once by hand; it is not part of the template, so new projects do not
point back at it):

```json
{
  "template": "Bankaifan/agent-template",
  "synced_sha": "<40 hex: the template commit you last matched>",
  "managed": [".github/workflows/", ".github/dependabot.yml", ".github/CODEOWNERS", ".github/rulesets/",
              ".agents/roles/", "tools/", "tests/", "AGENTS.md", "CLAUDE.md", "Makefile", "docs/design/README.md"],
  "overrides": [
    {"path": ".github/workflows/agent-fix.yml", "why": "workflow_run.workflows needs the CI name 'Validate'"},
    {"path": "AGENTS.md", "why": "project sentence and project rules"}
  ]
}
```

- `managed`: path prefixes the template owns (a trailing `/` means a directory). Other paths are never reported.
- `overrides`: exact `path` plus a free-text `why` for the developer.
- A too-old `synced_sha` only makes the first issue larger. No file, or an empty `synced_sha`: the run prints
  `template-sync: no .agents/template.json, skipped` and succeeds. In the template repo itself it is skipped as well.
- If the compare lists 300 or more files it may be cut off. The run then fails with a message and creates or edits no issue.
- Reading a private template needs the author app installed on the template repo.

**Project values.** Prefer repo variables over edited files: `PYTHON_VERSION` (default `3.x`), `EXTRA_INSTALL` (a shell
command that `tools/ci/install_tools.sh` runs after the common tools; it is read only from the repo variable, never from a
file on a PR branch) and `RUNNER`. `TEMPLATE_SYNC=off` turns the sync off. The one value that cannot be a variable is the CI
name in `workflow_run.workflows` (GitHub allows no expressions there). It is `[validate]` in `agent-fix.yml`,
`agent-review.yml`, `dependabot-automerge.yml` and `orchestrator.yml`. A project whose CI workflow has another name
(for example `Validate`) edits those lines and lists the files under `overrides`.

**Scout ideas for the template.** `scout.yml` opens each idea through `tools/idea_route.py` (no model). If every file of an
idea is under `managed` in `.agents/template.json`, the issue goes to the template repo (label `idea`, body ends with
`Found in: <project>#<context>`, no duplicate of an open template idea); otherwise, or without `template.json`, it stays in
the project. The model step only queues template ideas (`create`, project token). A later step without a model mints a second
author-app token limited to the template repo (same owner, `issues: write`) and runs `flush`, so no model ever sees it. The tool
accepts only the labels `prio:2` and `prio:3` (allowlist, so never `approved` or `auto-ok`) and strips `@` mentions.

Rationale: [docs/decisions/0007-template-sync.md](docs/decisions/0007-template-sync.md).

## Limits

- One agent run per issue or PR at a time (`concurrency` per number, never cancelled). GitHub cannot cap
  jobs across workflows without dropping queued runs, so the orchestrator keeps at most 2 `agent:dev` issues open.
- Rounds: labels `review:1`, `review:2` lead to a fix, `review:3` to `needs-human` (2 fix rounds). A red CI counts as a round.
- Dependabot runs get no repo secrets, so `dependabot-automerge.yml` uses `workflow_run` on `validate`. Open: if the
  secrets are still missing there, add the four app secrets under *Secrets > Dependabot* too. Dependabot
  `github-actions` PRs touch `.github/`, so they still need Daniel as code owner.
- Use private repos or keep `AUTHOR_BOT`/`APPROVER_BOT` set: the review workflow accepts bot-authored PRs.
- `allowedTools` is not a security boundary (e.g. `Bash(git:*)` still allows a lot). The boundaries are the token rights of the two apps and the ruleset on `main`.
- Not verified end to end yet; see `docs/decisions/0001-agent-setup.md`.

German short version: [README.de.md](README.de.md).
