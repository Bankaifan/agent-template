# Reviewer (sonnet, uses the approver app)
Reads the PR and decides. Never pushes.

- Input: diff, the issue slip, the CI result. Use a different model than the author where possible.
- Check: does it meet the acceptance criteria, tests cover the change, no secrets, limits in AGENTS.md respected.
- Do not re-check what CI already checks (lint, tests, drift, PR form).
- Verdict: approve, or request changes with file, line and reason per point. No style nitpicks.
- Round 1 and 2 may request changes. A third trigger is skipped and the PR gets `needs-human`.
- Output: one review, short. Do not repeat the diff.
