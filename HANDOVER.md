# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).
Risk class tightening (#171, design 0005, merged). Answer receiver (#191, design 0006, merged).

## Current state (measured 2026-11-10)
- Merged: #230 (unblocker verdict write), #232 (#212), #234 (train workflow, #152).
- Open PR #235 (for #129, scout dedup, risk:security, review:1). No other open PRs.
- Started this run: #203 (rule-keeper denied git checkout -b). Slip posted, agent:dev set. Overlap guard exit 0.
- Main CI: last runs success, skipped, cancelled or in progress; no red main.
- #99 (rule keeper overdue): rule-keeper has only workflow_dispatch runs, last success 01:19; no scheduled run seen. Cause open.
- #100 (weekly summary overdue): not looked at, cause open.
- #105: items done on main (comment says so); issue still open, Daniel closes.
- #125 design study: no PR seen (open).
- #92 stays needs-human. #148 not started. #154 is Daniel's.

## Open
- Design 0005 section 9 (Limit 5 exception) is a yes/no question for Daniel; it blocks #201 only.
- Whether #153 is restarted: open.
- #117 follow-up: second app token scoped to the template repo (Daniel to provision).
- How the ruleset file reaches the live ruleset (#154).
- #171 and #191 are parent issues of designs 0005/0006; whether they close once splits land: open.
- #125 design must not duplicate design 0006 (answer receiver).

## Next 3 steps
1. Merge of #235 (#129) and result of #203; remove agent:dev afterwards.
2. #205, #206 (answer receiver), #99/#100 cause.
3. Later #132, #133, #119, #120, #112, #148.
