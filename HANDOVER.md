# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).
Risk class tightening (#171, design 0005), Answer receiver (#191, design 0006), Orchestrator events (#125, design 0007), Failure watch (#190, design 0008): designs merged.

## Current state (measured 2026-11-10)
- No open PRs. Main CI: last status runs green.
- Design 0008 merged (479ce20). Removed agent:dev from #190. Created split issues #251 (allowlist, risk:security), #252 (module), #253 (wiring, risk:security), #254 (weekly summary). Labels prio:2 (prio:3 for #254); not yet on the trusted list, so not started (open: when they appear).
- Started #119 (check_drift.sh tests): slip posted, model:sonnet and agent:dev set.
- #105: done on main, issue still open, Daniel closes.
- #92, #191, #124, #125 are design parents with split issues; not started directly.
- Design 0007 split issues #237-#241 exist (open, not on the trusted list).
- #148 not started. #154 is Daniel's. #244 is not approved.
- #99/#100 may still be open; the failure watch (#252/#253) will close them.

## Open
- Design 0005 section 9 (Limit 5 exception) is a yes/no question for Daniel; it blocks #201 only.
- Whether #153 is restarted: open.
- #117 follow-up: second app token scoped to the template repo (Daniel to provision).
- How the ruleset file reaches the live ruleset (#154).
- #171, #191, #125, #190 are parent issues of designs; whether they close once splits land: open.
- Why #237-#241 and #251-#254 are not listed as approved: open.
- Wiring of check_test_evidence.py into CI needs a follow-up slip (workflow file, risk:security).

## Next 3 steps
1. Merge #119 result; then #251, #252 (disjoint files) once they are on the trusted list.
2. #205, #206 (answer receiver), wiring slip for check_test_evidence.py.
3. Later #120, #112, #148.
