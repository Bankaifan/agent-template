# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).
Risk class tightening (#171, design 0005, merged). Answer receiver (#191, design 0006, merged).

## Current state (measured 2026-11-10)
- Open PRs: #213 (for #182, approved, risk:security, review:1). Main CI green (status runs success).
- #182: PR #213 touches agent-fix.yml, automerge.yml, status.yml, tools/approval.py, tools/status.py.
- Started this run: #195 (slip written, model:sonnet, agent:dev). Problem 1 (install CI tools) already landed in 27b2795; only Problem 2 (managed-file guard) remains. Slip forbids touching files of #213.
- Created earlier from design 0006: #204 (hold, prio:1), #205-#208 (prio:3). No agent:dev yet; not approved.
- Design 0005 issues #197-#201 exist (prio:1, not approved/trusted yet, no agent:dev).
- #92 stays needs-human. Design 0004: #148 not started. Design 0003: #150, #152 not started; #154 is Daniel's.
- #105 (Unblocker 4/5) looks superseded by #147 (unblocker.yml exists); not started.
- #99, #100 (overdue scheduled run issues): not dev work, not started.

## Open
- Design 0005 section 9 (Limit 5 exception) is a yes/no question for Daniel; it blocks #201 only.
- Whether #153 is restarted: open (#181 closed).
- #117 follow-up: second app token scoped to the template repo (Daniel to provision).
- How the ruleset file reaches the live ruleset (#154).
- Exact cause of the #184 re-label: open, #204 reproduces it first.
- #171 and #191 are parent issues of designs 0005/0006; whether they get closed once the splits land: open.

## Next 3 steps
1. Merge of #213 (#182); then start #204 (owner label hold) and #205 once approved.
2. Start #197 and #198 once they are on the trusted list, then #199, #200.
3. Later #150, #152, #125 (design first), #119, #120, #112, #148.
