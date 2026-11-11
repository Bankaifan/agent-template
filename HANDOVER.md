# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).
Risk class tightening (#171, design 0005), Answer receiver (#191, design 0006), Orchestrator events (#125, design 0007), Failure watch (#190, design 0008): designs merged.
Test scoping (#135, design 0009): implementation issues #269-#273 all merged.
Automatic template sync with a two-part version (#386): design study started.

## Current state (measured 2026-11-11, manual run)
- Open PRs: none. No agent/rule-keeper PRs open.
- Free agent:dev slots 4, free PR slots 5 at start of this run.
- Main CI at d3b39a6: no red run in the last 10 (success, skipped, cancelled; the manual orchestrator run was in progress).
- Trusted list: only #386 (owner, approved, prio:1).
- Started #386 as a design task: slip written, overlap check exit 0, labels model:sonnet then agent:dev set. Output: docs/design/0011-automatic-template-sync.md (version x.y scheme, trigger options, setup docs, split).
- #338 is no longer on the trusted list (presumably done).

## Open
- Design 0005 section 9 (Limit 5 exception) is a yes/no question for Daniel; it blocks #201 only.
- Whether #153 is restarted: open.
- #117 follow-up: second app token scoped to the template repo (Daniel to provision).
- Whether the scout app has the alert read scopes (#120) and the next scout run shows 0 denied calls: open.
- Owner decisions of design 0011: open until the PR exists.

## Next 3 steps
1. Review the design 0011 PR when it arrives; if it merged, create the implementation issues from its split (each with a `Design:` line).
2. Daniel closes #327, #105 and #120 if still open.
3. Close-or-fix decision for #313 now that #320 has merged.
