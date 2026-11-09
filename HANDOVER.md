# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. Written by the orchestrator at the end of each session. -->

## Goal
Issue #7: automatic fix rounds, dependabot without AI, Daniel as sole author (rebase merge), CODEOWNERS, setup workflow.

## Current state
PR for #7 is open (branch `agent/7-fix-rounds-dependabot-rebase`). Nothing here is verified end to end yet.
See `docs/decisions/0002-fix-rounds-dependabot-rebase.md`.

## Open decisions
- Does `workflow_run` of a dependabot-triggered `validate` see the Actions secrets? If not, add the app secrets as Dependabot secrets.
- Dependabot `github-actions` PRs touch `.github/`, so they need Daniel as code owner.

## Next 3 steps
1. Daniel merges the PR, re-imports `.github/rulesets/main.json`, switches the repo to rebase merge only.
2. Run the `setup` workflow to create labels and check the 5 secrets.
3. First real run: agent PR with `CHANGES_REQUESTED`, and one dependabot PR.

## Known traps
- The ruleset file is not applied automatically; it must be re-imported.
