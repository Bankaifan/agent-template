"""Model-free dispatcher (design 0015, step 3): start ready issues that already carry a slip, no model run.

  python3 tools/dispatch.py start
  python3 tools/dispatch.py after-merge PR_NUMBER

start: candidates come only from the start list of `prefilter.start_state()` (trusted issues from
`tools/trusted_issues.py`, unblocked, within the free slots). Each one with a slip (`slip.py`) is checked with
`overlap.py` (exit 1 or 2: skipped, retried next run), then gets its model label and `agent:dev` last. N free slots and
N ready issues start N issues in one run. after-merge: removes `agent:dev` from the issues a merged same-repo `agent/`
PR names with `Refs #N` / `Closes #N`, then runs start. Writes labels only; issue text is read for numbers and
`Files:` / `Model:` / `Depends on:` lines and never copied into a comment. Needs the gh CLI (GH_TOKEN, GH_REPO).
"""
import json
import subprocess
import sys

import overlap
import prefilter
import slip

LABEL_COLOR = "ededed"


def start(state, gh=prefilter.gh, overlap_main=overlap.main, authors=overlap.DEFAULT_TRUSTED):
    """Start the issues of STATE["start"] that hold a slip; returns the numbers started."""
    started = []
    for n in state["start"]:
        issue = json.loads(gh("issue", "view", str(n), "--json", "labels,body,author,comments"))
        files = slip.slip_files(issue, authors)
        if not files:
            continue  # no slip: the model writes it
        if overlap_main(["--files", ",".join(files), "--issue", str(n)]) != 0:
            print(f"#{n}: overlap or unreadable, deferred")
            continue
        model = f"model:{slip.model_of(issue, authors)}"
        try:
            gh("label", "create", model, "--force", "--color", LABEL_COLOR)
            gh("issue", "edit", str(n), "--add-label", model)
            gh("issue", "edit", str(n), "--add-label", "agent:dev")  # last: this label starts the developer run
        except (subprocess.CalledProcessError, OSError) as e:  # a failed label call must not stop the other issues
            print(f"#{n}: label call failed ({type(e).__name__}), skipped", file=sys.stderr)
            continue
        started.append(n)
        print(f"#{n}: started ({model})")
    return started


def after_merge(pr, gh=prefilter.gh):
    """Remove `agent:dev` from the issues a merged same-repo `agent/` PR names; returns their numbers."""
    p = json.loads(gh("pr", "view", str(pr), "--json", "state,body,headRefName,isCrossRepository"))
    if p.get("state") != "MERGED" or p.get("isCrossRepository") or not p.get("headRefName", "").startswith("agent/"):
        return []
    done = sorted(prefilter.closing_issues(p.get("body")))
    for n in done:
        try:
            gh("issue", "edit", str(n), "--remove-label", "agent:dev")
        except (subprocess.CalledProcessError, OSError) as e:
            print(f"#{n}: cannot remove agent:dev ({type(e).__name__})", file=sys.stderr)
    return done


def main(argv) -> int:
    if not argv or argv[0] not in ("start", "after-merge") or (argv[0] == "after-merge" and len(argv) != 2):
        print(__doc__, file=sys.stderr)
        return 2
    if argv[0] == "after-merge":
        print(f"agent:dev removed from {after_merge(int(argv[1]))}")
    start(prefilter.start_state())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
