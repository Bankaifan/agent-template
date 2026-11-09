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
- Finish by overwriting HANDOVER.md (short, max 60 lines).
- Everything on GitHub in English (files, commits, PR titles and bodies, issues). Talking to Daniel: German.

## Commits and PRs
- Author: `git config user.name "Daniel"` and `user.email "476059+Bankaifan@users.noreply.github.com"`.
  No `Co-authored-by` trailer.
- PR title: English, ASCII only. Body: what and why in at most 5 lines, link the issue. Enforced by CI.
- Every user-visible change gets a CHANGELOG entry if the project has a CHANGELOG.md.

## Review rounds
Developer -> CI -> reviewer (only on green CI) -> at most 2 fix rounds (started automatically on `CHANGES_REQUESTED`
or on a red CI). Then the PR gets `needs-human` and waits for the orchestrator or Daniel. Do not start a third round.
Only trusted input drives agents: issues by Daniel or labelled `approved`/`auto-ok` by Daniel; the reviewer never runs PR code.

## Models (subscription quota is scarce)
Routine work haiku; core, security and architecture sonnet; opus only with Daniel's OK.
Max 2 agent jobs at once. Script first, then haiku, then sonnet. Short reports, never repeat the diff.
