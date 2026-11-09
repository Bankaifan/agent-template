#!/usr/bin/env python3
"""Check PR form: title is printable ASCII (English), body is not empty.

Reads PR_TITLE and PR_BODY from the environment. Skipped when PR_TITLE is unset
(local runs) or outside pull_request events (pushes to main set it empty). Whether the title is really English cannot be verified.
"""
import os
import sys


def main() -> int:
    title = os.environ.get("PR_TITLE")
    if title is None or os.environ.get("GITHUB_EVENT_NAME", "pull_request") != "pull_request":
        print("check_pr_form: skipped (PR_TITLE not set)")
        return 0
    body = os.environ.get("PR_BODY") or ""
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
