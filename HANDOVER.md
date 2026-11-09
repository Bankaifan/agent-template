# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Issue #19: template sync. This PR is the design study only (`docs/design/0001-template-sync.md`), no implementation.

## Current state
Design on branch `agent/19-template-sync-design`, fix round 1 after review feedback:
- `EXTRA_INSTALL` moved from `.agents/project.env` (read from the PR branch, unsafe) to repo variable `vars.EXTRA_INSTALL`.
- Sync fails loudly when the compare response has 300 or more files (possible truncation).
- Template detection rule: `template` equals `GH_REPO`. `template.json` example moved to the README, not committed here.
- Owner decisions: two (author app on the template repo; widened trust for `Template sync` issues). Needs Daniel.

## Open decisions
- Whether the author app can read a private template repo is not verified (open, owner decision 1).
- The sync flow was not run end to end (open).

## Next 3 steps
1. Daniel decides the two owner decisions in section 9 (PR gets `needs-human`).
2. After approval the orchestrator creates the four implementation issues with a `Design:` line.
3. Work them in order (1 and 2 may run in parallel).
