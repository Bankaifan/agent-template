# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).
Risk class tightening (#171, design 0005), Answer receiver (#191, design 0006), Orchestrator events (#125, design 0007), Failure watch (#190, design 0008): designs merged.
Test scoping (#135, design 0009): implementation issues #269-#273 all merged.

## Current state (measured 2026-11-10, run 33)
- Open PRs: none. No agent/rule-keeper PRs open.
- Free agent:dev slots 4, free PR slots 5 at start of this run.
- Main CI: no red run in the last 10 (runs skipped, cancelled or in progress).
- #120: PR "Give scout token alert read scopes and log alert reads" merged (92394a4); agent:dev removed from #120 this run.
- #309 (risk.yml gate failure): intentional owner gate on PR #307, answer receiver owns it. Not touched.
- #105: done on main, issue still open, Daniel closes.
- #92, #191, #124, #125, #190, #135 are design parents with split issues; not started directly this run.

## Open
- Design 0005 section 9 (Limit 5 exception) is a yes/no question for Daniel; it blocks #201 only.
- Whether #153 is restarted: open.
- #117 follow-up: second app token scoped to the template repo (Daniel to provision).
- Whether the scout app now has the alert read scopes: open.

## Next 3 steps
1. Daniel grants the scout app alert read scopes (#120).
2. Close-or-fix decision for #313 now that #320 has merged.
3. Daniel closes #105 and #120 if still open.
