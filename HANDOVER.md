# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).
Risk class tightening (#171, design 0005), Answer receiver (#191, design 0006), Orchestrator events (#125, design 0007): designs merged.

## Current state (measured 2026-11-10)
- No open PRs. Merged: #235 (#129 scout dedup), rule-keeper branch fix (#203, 82da104).
- No open agent:dev issues before this run. Main CI: no red main.
- Started this run: #99 (also covers #100). Slip posted, model:sonnet and agent:dev set, overlap exit 0.
- #99/#100: rule-keeper and weekly-summary crons are weekly (Mon); only workflow_dispatch runs exist. Cause open (liveness.py false positive or schedule not fired).
- #105: done on main, issue still open, Daniel closes.
- Design 0007 split issues #237-#241 exist (open, not on the trusted list, so not started).
- #92 stays needs-human. #148 not started. #154 is Daniel's.

## Open
- Design 0005 section 9 (Limit 5 exception) is a yes/no question for Daniel; it blocks #201 only.
- Whether #153 is restarted: open.
- #117 follow-up: second app token scoped to the template repo (Daniel to provision).
- How the ruleset file reaches the live ruleset (#154).
- #171, #191, #125 are parent issues of designs; whether they close once splits land: open.
- Why #237-#241 are not approved or listed: open.

## Next 3 steps
1. Result of #99/#100; remove agent:dev afterwards.
2. #205, #206 (answer receiver), #132, #133.
3. Later #119, #120, #112, #148.
