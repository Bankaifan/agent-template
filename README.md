# agent-template

Private GitHub template for projects where AI agents write code and humans keep control.

Idea: **rules a script can check live in CI, not in prompts.** The agents get a short
`AGENTS.md`; CI supplies the strictness.

- Orchestrator + developer + reviewer + tester roles (`.agents/roles/`), each at most 15 lines.
- Agents run in GitHub Actions via [`anthropics/claude-code-action@v1`](https://github.com/anthropics/claude-code-action),
  paid by a Claude subscription (OAuth token), no API key.
- Two GitHub Apps: the **author** pushes and opens PRs, the **approver** reviews. Nobody approves their own work.
- A ruleset on `main` (PR, 1 approval, check `validate`, linear history, squash only) plus auto-merge.
- A weekly gap finder that only opens issues proposing new checks.

Quota is scarce: at most 2 agent jobs run at the same time; models are chosen per role
(developer routine: haiku, core work: sonnet, reviewer: sonnet, orchestrator: sonnet).

## Setup

1. **Use this template** (private repo). Enable *Settings > General > Allow auto-merge*, allow *squash merging* only.
2. **Create two GitHub Apps** and install both on the repo.
   - Author: Contents, Pull requests, Issues: read and write.
   - Approver: Pull requests: read and write, Contents and Issues: read.
3. **Add 5 secrets** (*Settings > Secrets and variables > Actions*): `CLAUDE_CODE_OAUTH_TOKEN` (from `claude setup-token`),
   `AUTHOR_APP_ID`, `AUTHOR_APP_KEY`, `APPROVER_APP_ID`, `APPROVER_APP_KEY` (the `.pem` content).
   Optional variables: `RUNNER` (default `ubuntu-latest`, e.g. `self-hosted`), `AUTHOR_BOT` (the author app's bot login, e.g. `my-author[bot]`).
4. **Import the ruleset**: *Settings > Rules > Rulesets > New > Import* with `.github/rulesets/main.json`.
5. **Create the labels**:
   ```bash
   for l in agent:dev agent:review model:sonnet review:1 review:2 needs-human gap-finder; do gh label create "$l" 2>/dev/null; done
   ```
6. **First task**: open an issue with a goal and acceptance criteria, add label `agent:dev` (or comment `/dev`).
   Add `model:sonnet` for core work, otherwise haiku is used. The PR is reviewed, auto-merged after approval and green CI.

Then fill in `AGENTS.md` (one sentence about the project) and replace the placeholders in `HANDOVER.md`.

## Limits

- One agent run per issue or PR at a time (`concurrency` per number, never cancelled). GitHub cannot cap
  jobs across workflows without dropping queued runs, so the orchestrator keeps at most 2 `agent:dev` issues open.
- Review rounds are capped at 2 (labels `review:1`, `review:2`), then the PR gets `needs-human`.
- Use only in private repos: the review workflow accepts bot-authored PRs.
- Not verified end to end yet; see `docs/decisions/0001-agent-setup.md`.

German short version: [README.de.md](README.de.md).
