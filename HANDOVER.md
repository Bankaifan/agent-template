# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).
Risk class tightening (#171, design 0005, merged). Answer receiver (#191, design 0006, merged).

## Current state (measured 2026-11-10)
- Open PR #232 (for #212, risk:infra): CI running.
- Open PR #230 (unblocker verdict write via Edit(verdict.json), risk:security, review:1).
- PR #223 (for #204) is no longer open; whether it merged: open.
- Started this run: #152 (train workflow; train core #151 is closed). Slip posted, model:sonnet + agent:dev. Overlap guard exit 0.
- Main CI: last runs success, skipped or cancelled; no red main.
- #125 design study: no PR seen (open).
- Design 0005 issues #197-#201 exist (prio:1, not approved, no agent:dev).
- #92 stays needs-human. Design 0004: #148 not started. #154 is Daniel's.
- #105 looks superseded by #147 (unblocker.yml exists); not started.
- #99, #100 (overdue scheduled run issues): not started, cause open.

## Open
- Design 0005 section 9 (Limit 5 exception) is a yes/no question for Daniel; it blocks #201 only.
- Whether #153 is restarted: open (#181 closed).
- #117 follow-up: second app token scoped to the template repo (Daniel to provision).
- How the ruleset file reaches the live ruleset (#154).
- #171 and #191 are parent issues of designs 0005/0006; whether they get closed once the splits land: open.
- #125 design must not duplicate design 0006 (answer receiver).

## Next 3 steps
1. Merge of #230 and #232 (#212); remove agent:dev from #212 after merge.
2. Result of #152; then #205, #206.
3. Later #129, #132, #133, #119, #120, #112, #148.
