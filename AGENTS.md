# Working rules
Project: <one sentence>. Current state: HANDOVER.md. Decisions: docs/decisions/. Roles: .agents/roles/.

## Limits (not negotiable)
1. No secrets in code, logs, issues or PRs. Credentials only from environment variables / GitHub Secrets.
2. Nothing irreversible without Daniel's explicit OK: deleting repos or branches holding other people's work,
   database or production changes, releases, payments, permission changes.
3. Never push to `main`, no tags by hand. Always branch + PR. Rebase and force-push are allowed on your own
   agent branches, never on `main`.
4. Read-only checks against real systems are allowed. Anything that writes to production systems or real
   devices needs Daniel's OK.
5. No changes to CI protection, rulesets, permissions, workflows or this file without OK.

## How to work (a proposal, not a cage)
- Small PRs, branched from current `main`, rebase-merged, no stacked PRs, no `git merge main` into a branch.
  If a branch falls behind, rebase it (own branch) or cherry-pick onto a fresh one.
- Before asking for review, squash the branch into ONE commit authored by Daniel (rebase merge keeps the author,
  so Daniel is the sole author on `main`). Force-push to your own branch is allowed.
- Before the PR: `make check` and the tests are green. CI is the truth, not your estimate.
- Claim only what you measured (command + output). Unsure? Ask in the issue, do not guess.
  Missing facts are marked "open".
- Keep context small: read only the files named in the task slip.
- HANDOVER.md (max 60 lines) is rewritten by the orchestrator only; developer and fix runs put notes in the PR body.
- Everything on GitHub in English (files, commits, PR titles and bodies, issues). Talking to Daniel: German.

## Commits and PRs
- Author: `git config user.name "Daniel"` and `user.email "476059+Bankaifan@users.noreply.github.com"`.
  No `Co-authored-by` trailer.
- PR title: English, ASCII only. Body: what and why in at most 5 lines, link the issue. Enforced by CI.
- Every user-visible change gets a CHANGELOG entry if the project has a CHANGELOG.md.

## Review rounds
Developer -> CI -> reviewer (only on green CI) -> at most 2 fix rounds (started automatically on `CHANGES_REQUESTED`
or on a red CI). Then the PR gets `needs-human` plus a review request to Daniel (a label alone is not in his inbox) and waits for the orchestrator or Daniel. Do not start a third round.
Big work (architectural, breaking, release-relevant, multi-PR) starts with a design study in `docs/design/` (see its README); only its *Owner decisions* go to Daniel.
Only trusted input drives agents: issues by Daniel or labelled `approved`/`auto-ok` by Daniel; the reviewer never runs PR code.

## Waiting for Daniel
Daniel approves only what needs him: PRs with risk class `security` (check `risk`, label `risk:security`, see `tools/ci/risk.py`),
`needs-human`, design owner decisions, dependabot majors, product decisions. Whoever parks something with him leaves, as the
LAST comment, a short plain-German note: what changes, the worst case, what the reviewers recommend, one exact yes/no question;
technical terms explained in a few words. PRs get a review request to Bankaifan; only issues that wait for him mention
`@Bankaifan` once in that note. No other comment mentions him. Every infra/security PR also needs the security reviewer
(`.agents/roles/security-reviewer.md`, status `security-review`) besides the normal review, agent-smoke and zizmor.

## Models (subscription quota is scarce)
Routine work haiku; core, security and architecture sonnet; opus only with Daniel's OK.
Max 2 agent jobs at once. Script first, then haiku, then sonnet. Short reports, never repeat the diff.
