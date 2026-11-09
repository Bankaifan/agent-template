#!/usr/bin/env python3
"""Check PR form: title is printable ASCII (English), body is not empty.

Reads PR_TITLE and PR_BODY from the environment (pull_request events). On workflow_dispatch it reads
title and body of the open PR for GITHUB_REF_NAME via `gh pr view` (needs GH_TOKEN); no PR means skipped.
Skipped for local runs and pushes to main. Whether the title is really English cannot be verified.
"""
import json
import os
import subprocess
import sys


def dispatch_pr():
    """Title and body of the open PR for the dispatched branch, or None."""
    try:
        out = subprocess.run(["gh", "pr", "view", os.environ["GITHUB_REF_NAME"], "--json", "title,body"],
                             check=True, capture_output=True, text=True).stdout
        pr = json.loads(out)
    except (KeyError, OSError, subprocess.CalledProcessError, ValueError):
        return None
    return pr.get("title") or "", pr.get("body") or ""


def main() -> int:
    event = os.environ.get("GITHUB_EVENT_NAME", "pull_request")
    if event == "workflow_dispatch":
        pr = dispatch_pr()
        title, body = pr if pr else (None, "")
    elif event == "pull_request":
        title, body = os.environ.get("PR_TITLE"), os.environ.get("PR_BODY") or ""
    else:
        title, body = None, ""
    if title is None:
        print("check_pr_form: skipped (no PR title)")
        return 0
    errors = []
    if not title.strip():
        errors.append("title is empty")
    elif not all(32 <= ord(c) < 127 for c in title):
        errors.append("title must be English, printable ASCII only")
    elif len(title) > 100:
        errors.append("title is longer than 100 characters")
    if not body.strip():
        errors.append("body is empty (what and why, link the issue)")
    for e in errors:
        print(f"check_pr_form: {e}")
    if not errors:
        print("check_pr_form: ok")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
