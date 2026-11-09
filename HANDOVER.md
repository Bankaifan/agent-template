# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Issue #15: pin gitleaks-action to a commit SHA; fix rounds use the model of the original task.

## Current state
PR for #15 on branch `agent/15-pin-gitleaks-fix-model`. `validate` pins `gitleaks/gitleaks-action@ff98106e…` (v2.3.9).
`agent-fix` picks sonnet if the PR or an issue it closes has `model:sonnet`; a red-CI fix on a PR touching
`.github/` or `tools/` always uses sonnet. README documents the rule. Unverified in CI until the PR runs.

## Open decisions
- The fix-round model selection was not executed end to end; it runs first in the next fix round (open).
- `agent-fix` now reads issues with the approver app token; its Issues permission is assumed, not checked (open).
- Pinned zizmor 1.5.2 and actionlint 1.7.7 were not verified against upstream releases; CI is the truth.

## Next 3 steps
1. Daniel reviews and merges the PR once CI is green.
2. Watch the first fix round after merge (labels `review:1` and a model line in the `prepare` log).
3. #16 was queued behind this PR (overlapping files); start it after the merge.

## Known traps
- The ruleset file is not applied automatically; it must be re-imported when `.github/rulesets/main.json` changes.
- `gh issue view` on a number that is not an issue fails; the model lookup tolerates that.
