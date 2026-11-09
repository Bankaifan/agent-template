# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Issue #12: CI tools for agents, script pre-filters, scripted weekly summary, monthly scout, lean roles.

## Current state
PR for #12 on branch `agent/12-ci-tools-prefilter-lean-roles`. #11 (secure inputs, reliable triggers) is merged.
See `docs/decisions/0005-ci-tools-prefilter-lean-roles.md`.

## Open decisions
- Pinned zizmor 1.5.2 and actionlint 1.7.7 were not verified against upstream releases; CI is the truth.
- gitleaks-action@v2 first run (licence for org repos?) is open.
- Author app permissions and `workflow_run` events from app-created runs (from #11) are still unverified.

## Next 3 steps
1. Daniel merges the PR once CI is green; re-import the ruleset only if `.github/rulesets/main.json` changes.
2. Watch the first orchestrator run with the pre-filter and the first Monday summary.
3. Set `IDEAS_PER_WEEK` as needed (it now means ideas per monthly run).

## Known traps
- The ruleset file is not applied automatically; it must be re-imported.
