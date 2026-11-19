# Bootstrap: the first PR of a project that imports the template

The first PR of a new project (created with *Use this template*) hits two guards that were written for later changes.
Three points get it through. Do them in the same PR, after the setup in the README (*Setup*, steps 1 to 5).

1. **Title and config.** Title the PR `Template sync <version>: ...` and include `.agents/template.json` in the same PR.
   `managed_guard` (`tools/managed_guard.py check`) exempts a PR whose title starts with `Template sync` and that changes
   `.agents/template.json`. Without this exemption it fails every managed file the project has.
2. **Leave `HANDOVER.md` out.** `check_pr_form` fails any PR that touches `HANDOVER.md` unless its branch is
   `agent/orchestrator-handover-*`. The orchestrator creates and rewrites that file; put your notes in the PR body.
   Open: the issue does not say whether a project created from the template already contains a `HANDOVER.md` that
   this PR would change. Do not change it in this PR.
3. **Install both apps first.** `agent-smoke` creates both app tokens and calls `gh api /installation/repositories` with
   each. It fails until the author and approver apps are installed on the new repo (README, *Setup* step 2), and it runs
   on any PR that touches `.github/workflows/`, `.github/actions/` or `tools/ci/`.

`check_pr_form` also requires an English printable ASCII title and a non-empty body.

## Dependabot and project-only workflows

`managed_guard` fails in a project for two cases that are not real changes to protected files:

- **Dependabot bumps template workflows.** Its `github-actions` updates change the pins of template-managed workflows,
  and the guard fails the PR. Remove the `github-actions` entry from the project's own (overridden)
  `.github/dependabot.yml`. The template's workflow pins arrive with the template sync; the template's own Dependabot keeps them current.
- **A project-only workflow under a managed prefix**, such as `.github/workflows/release.yml`, is not in the template and
  fails the guard. Give it a one-line override entry in `.agents/template.json` and state the reason there.

Open: with this setup, project-only workflows get no automatic pin bumps; their actions are updated by hand.
`tools/managed_guard.py` is not relaxed for this.
