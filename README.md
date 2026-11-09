# agent-template

Private GitHub template for projects where AI agents write code and humans keep control.

Idea: **rules a script can check live in CI, not in prompts.** The agents get a short
`AGENTS.md`; CI supplies the strictness.

- Orchestrator + developer + reviewer + tester roles (`.agents/roles/`), each at most 15 lines.
- Agents run in GitHub Actions via [`anthropics/claude-code-action@v1`](https://github.com/anthropics/claude-code-action),
  paid by a Claude subscription (OAuth token), no API key.
- Two GitHub Apps: the **author** pushes and opens PRs, the **approver** reviews. Nobody approves their own work.
- A ruleset on `main` (PR, 1 approval, code owner review, check `validate`, linear history, rebase merge only) plus auto-merge.
  The developer squashes its branch into one commit authored by Daniel, so Daniel is the sole author on `main`.
- Fix rounds start automatically when the reviewer requests changes (max 2, then `needs-human`).
- Dependabot PRs are not reviewed by AI: a model-free workflow approves patch/minor once `validate` is green and
  enables auto-merge; majors get `needs-human`.
- `.github/CODEOWNERS`: `@Bankaifan` owns `AGENTS.md`, `CLAUDE.md`, `.agents/`, `.github/`, `tools/check/`.
- A weekly rule keeper that opens one PR proposing rule removals, new checks and contradiction fixes (Daniel merges).
- A daily `branch-cleanup` that deletes `agent/*` branches with a closed PR, or no PR and no commit for 7 days (dry-run input on manual runs).
- An autonomous `orchestrator` (push to `main`, daily, manual; off unless variable `ORCHESTRATOR_ENABLED=true`) that cuts task slips,
  keeps at most 2 `agent:dev` issues, handles `needs-human` PRs, updates HANDOVER.md via PR and keeps one "Weekly summary" issue.
- A weekly `scout` (haiku) that opens at most `IDEAS_PER_WEEK` (default 3, 0 = off) `idea` issues; small low-risk ones also get
  `auto-ok` and may be started by the orchestrator, the rest wait for Daniel's `approved` label.

Quota is scarce: `ORCHESTRATOR_ENABLED` and `IDEAS_PER_WEEK` control the autonomous load; at most 2 agent jobs run at the same time; models are chosen per role
(developer routine: haiku, core work: sonnet, reviewer: sonnet, orchestrator: sonnet).

## Setup

1. **Use this template** (private repo). Enable *Settings > General > Allow auto-merge*, allow *rebase merging* only.
2. **Create two GitHub Apps** and install both on the repo.
   - Author: Contents, Pull requests, Issues: read and write.
   - Approver: Pull requests: read and write, Contents and Issues: read.
3. **Add 5 secrets in every repo** (*Settings > Secrets and variables > Actions*; they are not inherited from the template): `CLAUDE_CODE_OAUTH_TOKEN` (from `claude setup-token`),
   `AUTHOR_APP_ID`, `AUTHOR_APP_KEY`, `APPROVER_APP_ID`, `APPROVER_APP_KEY` (the `.pem` content).
   Optional variables: `RUNNER` (default `ubuntu-latest`, e.g. `self-hosted`), `AUTHOR_BOT` (the author app's bot login, e.g. `my-author[bot]`).
4. **Import the ruleset**: *Settings > Rules > Rulesets > New > Import* with `.github/rulesets/main.json`.
   Re-import it whenever that file changes (it is not applied automatically); delete the old ruleset first.
5. **Run the `setup` workflow** (*Actions > setup > Run workflow*): it creates all labels (idempotent) and fails with
   the list of missing secrets (names only, values are never printed).
6. **First task**: open an issue with a goal and acceptance criteria, add label `agent:dev` (or comment `/dev`).
   Add `model:sonnet` for core work, otherwise haiku is used. The PR is reviewed, auto-merged after approval and green CI.

Then fill in `AGENTS.md` (one sentence about the project) and replace the placeholders in `HANDOVER.md`.

## Limits

- One agent run per issue or PR at a time (`concurrency` per number, never cancelled). GitHub cannot cap
  jobs across workflows without dropping queued runs, so the orchestrator keeps at most 2 `agent:dev` issues open.
- Review rounds are capped at 2 (labels `review:1`, `review:2`), then the PR gets `needs-human`.
- Dependabot runs get no repo secrets, so `dependabot-automerge.yml` uses `workflow_run` on `validate`. Open: if the
  secrets are still missing there, add the four app secrets under *Secrets > Dependabot* too. Dependabot
  `github-actions` PRs touch `.github/`, so they still need Daniel as code owner.
- Use only in private repos: the review workflow accepts bot-authored PRs.
- Not verified end to end yet; see `docs/decisions/0001-agent-setup.md`.

German short version: [README.de.md](README.de.md).
