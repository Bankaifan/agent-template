# 0001 Agent setup

Status: accepted (Daniel, 2026-11-09). Not yet verified end to end.

## Decision
- Payment: Claude subscription only (`CLAUDE_CODE_OAUTH_TOKEN`), no API key, no budget console.
- Agents run in GitHub Actions with `anthropics/claude-code-action@v1`; runner via variable `RUNNER`.
- Quota is scarce: max 2 agent jobs at once (two `concurrency` slots shared by all agent workflows).
- Models per role via `--model`: developer routine haiku, core sonnet, reviewer sonnet, orchestrator sonnet.
- Two GitHub Apps (author pushes and opens PRs, approver reviews); auto-merge squash with the author token.
- Ruleset on `main`: PR, 1 approval, check `validate`, linear history, squash only, no force push or deletion.
- Commits authored as Daniel, no `Co-authored-by` trailer.
- Rules a script can check go into `tools/check/`, not into prompts. The gap finder proposes new checks as issues.

## Consequences
- Review rounds are capped at 2 by labels; a third trigger ends in `needs-human`.
- `concurrency` keeps only one pending job per slot, so a burst can drop queued runs.
- Open: app permissions and the approver counting as a required reviewer need a first real run.
