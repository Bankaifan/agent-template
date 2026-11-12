"""Strip tool attribution footers from a PR or issue body and save it (only when it changed).

Usage: strip_attribution.py <number>. Reads the live body with `gh api` (needs GH_TOKEN and GH_REPO). Writes with `gh api -X PATCH` (issues endpoint, also for PRs) only when
`tools/attribution.remove` changed the text, so the `edited` event this triggers finds nothing and stops (no loop).
Never runs PR code: it only handles the text. Exit 0 on success or nothing to do, 1 on a gh error.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import attribution


def gh(args, stdin=None):
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True, input=stdin).stdout


def main(argv=None, environ=None):
    argv = sys.argv[1:] if argv is None else argv
    env = os.environ if environ is None else environ
    if len(argv) != 1 or not argv[0].isdigit():
        print("usage: strip_attribution.py <number>", file=sys.stderr)
        return 2
    number, repo = argv[0], env.get("GH_REPO", "")
    endpoint = f"repos/{repo}/issues/{number}"
    try:
        body = json.loads(gh(["api", endpoint])).get("body") or ""  # live body, never the (possibly stale) event copy
        new = attribution.remove(body)
        if new == body:
            print(f"strip_attribution: #{number} has no footer")
            return 0
        gh(["api", "-X", "PATCH", endpoint, "-F", "body=@-"], stdin=new)
    except (OSError, subprocess.CalledProcessError, ValueError) as e:
        print(f"strip_attribution: #{number}: {e}", file=sys.stderr)
        return 1
    print(f"strip_attribution: #{number} footer removed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
